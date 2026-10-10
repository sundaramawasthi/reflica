"""regress@1 — ordinary least-squares linear regression with diagnostics.

Two steps keep the researcher in control:

1. `prepare(dataset, spec)` validates the requested target and predictors and
   returns a `RegressPlan` (what would be fitted, on which rows, with which
   warnings) identified by `plan_sha256`. Nothing is fitted.
2. `run(dataset, plan, approval)` fits only if the approval names that plan
   and the plan re-derived from the same data and specification is identical.

Method (also returned in `limitations` and the assumption list):
- Rows with a missing value in any selected column are dropped (listwise).
- Each column is first rescaled by an exact power of two (lossless). With an
  intercept the predictors and target are centred (two-pass mean); predictor
  columns are then scaled to unit length and the least-squares problem is
  solved by a singular value decomposition (NumPy). Fitted values, residuals,
  leverage, coefficient covariance, VIF and the collinearity check all come
  from the same decomposition.
- Exact or numerically indistinguishable collinearity (singular-value ratio
  below 1e-10) is refused, not silently resolved by dropping a column.
- Standard errors assume independent, constant-variance errors; t and F
  p-values and confidence intervals also assume normal errors (or a large
  sample). No robust or adjusted alternatives are provided in version 1.
- Diagnostics follow textbook definitions pinned against R in the tests:
  Durbin-Watson; Jarque-Bera (chi-squared, 2 df); Breusch-Pagan (Koenker's
  studentized form, n R^2 of squared residuals on the predictors, k df, as in
  lmtest::bptest); RESET (F test adding fitted^2, as lmtest::resettest with
  power 2); VIF = diag(inverse correlation matrix); Cook's distance,
  leverage, and internally and externally studentized residuals as in R.

Everything returned is an association within the supplied data. Nothing here
supports a claim that changing a predictor would change the target.

NumPy is imported inside functions (optional `service` extra). Run this
through `reflica_service.execution` to enforce the analysis time limit.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform

from .. import __version__
from ..csv_adapter import is_number
from ..models import (AnalysisInputError, Approval, Assumption, Coefficient, Column,
                      ColumnMissing, DiagnosticTest, Diagnostics, Dataset, FitStatistics,
                      Interpretation, Measured, PredictorRange, RegressPlan, RegressResult,
                      RegressSpec, RegressWarning, ResidualSummary, RowDiagnostics, RunRecord,
                      ServiceConfig)
from . import _distributions as dist

INTERCEPT = "(Intercept)"
COLLINEAR_RATIO = 1e-10      # singular-value ratio treated as exact collinearity
PRECISION_RATIO = 1e-7       # below this, warn that several digits may be lost
PERFECT_FIT = 1e-12          # residual norm relative to total norm
EXACT_FLOAT_INT = 2 ** 53
ALPHA = 0.05                 # diagnostic-test flag level (not a decision rule)
VIF_HIGH = 10.0
DROPPED_HIGH = 0.2
OBS_PER_PREDICTOR = 10
SMALL_DF = 10
OUTLIER_T = 3.0
MAX_LISTED_ROWS = 20
SOLVER = ("numpy.linalg.svd on the power-of-two-scaled, centred (with intercept), "
          "unit-length predictor matrix")

DIAGNOSTICS_PLANNED = (
    "residual summary", "leverage", "Cook's distance", "studentized residuals",
    "Durbin-Watson", "Jarque-Bera", "Breusch-Pagan (with intercept)", "RESET",
    "VIF (with intercept, 2+ predictors)", "condition number")

LIMITATIONS = (
    "Ordinary least squares describes linear associations in these rows. It does not establish "
    "cause and effect: a coefficient can reflect confounding, selection, reverse dependence or "
    "chance, whether the data are observational or experimental.",
    "Coefficients are conditional on the predictors included; adding or removing predictors can "
    "change them, including their sign.",
    "Standard errors, confidence intervals and p-values assume independent errors with constant "
    "variance (and normal errors in small samples). Version 1 provides no robust or clustered "
    "standard errors.",
    "p-values are per coefficient and not adjusted for testing several coefficients or for "
    "choosing the model after looking at the data.",
    "Rows with any missing selected value were dropped; results apply to the complete rows only.",
    "Diagnostic tests have little power in small samples and flag unimportant departures in "
    "large ones; a test that does not flag a problem does not show the assumption holds.",
    "Predictions outside the observed predictor ranges (see predictor_ranges) are extrapolation "
    "and are not supported by this analysis.",
)

INTERPRETATION_BASIS = (
    "Generated from fixed templates from the measured values above. Statements describe "
    "associations in these data; next steps are suggestions for the researcher to evaluate.")


def _np():
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - environment without the service extra
        raise RuntimeError("regress requires NumPy; install the 'service' extra") from None
    return np


# ---------------------------------------------------------------------------
# preparation and validation
# ---------------------------------------------------------------------------

class _Data:
    """Complete-case arrays for one specification (all in original units)."""

    def __init__(self, ds: Dataset, spec: RegressSpec, config: ServiceConfig):
        np = _np()
        cols = {c.name: c for c in ds.columns}
        names = (spec.target, *spec.predictors)
        unknown = [n for n in names if n not in cols]
        if unknown:
            raise AnalysisInputError("unknown_column", "Column not found in the dataset: "
                                     + ", ".join(unknown) + ".",
                                     {"columns": unknown, "available": [c.name for c in ds.columns]})
        if spec.target in spec.predictors:
            raise AnalysisInputError("target_in_predictors",
                                     "The target cannot also be a predictor.", {"column": spec.target})
        dupes = sorted({p for p in spec.predictors if spec.predictors.count(p) > 1})
        if dupes:
            raise AnalysisInputError("duplicate_predictor", "A predictor is listed more than once.",
                                     {"columns": dupes})
        if len(spec.predictors) > config.max_regress_predictors:
            raise AnalysisInputError("too_many_predictors",
                                     f"At most {config.max_regress_predictors} predictors are allowed.",
                                     {"predictors": len(spec.predictors),
                                      "limit": config.max_regress_predictors})
        for n in names:
            _check_numeric(cols[n])

        self.rows_total = ds.row_count
        nan = math.nan
        # float() on the validated numeric cells, exactly as describe@1 converts them
        arrays = [np.array([nan if v is None else float(v) for v in cols[n].values], dtype=float)
                  for n in names]
        self.missing = tuple(ColumnMissing(column=n, missing=int(np.isnan(a).sum()))
                             for n, a in zip(names, arrays))
        keep = np.ones(ds.row_count, dtype=bool)
        for a in arrays:
            keep &= ~np.isnan(a)
        self.rows = np.flatnonzero(keep) + 1
        self.y = arrays[0][keep]
        self.X = np.column_stack([a[keep] for a in arrays[1:]])
        self.n = int(keep.sum())
        self.k = len(spec.predictors)
        self.p = self.k + int(spec.intercept)
        self.precision_loss = tuple(n for n, a in zip(names, arrays) if cols[n].integer
                                    and bool((np.abs(a) >= EXACT_FLOAT_INT).any()))

        if self.n - self.p < 1:
            raise AnalysisInputError(
                "insufficient_observations",
                f"{self.n} complete rows cannot estimate {self.p} coefficients with any residual "
                "degrees of freedom; at least {0} complete rows are needed.".format(self.p + 1),
                {"complete_rows": self.n, "parameters": self.p})
        if spec.intercept and self.y.min() == self.y.max():
            raise AnalysisInputError("constant_target", "The target has the same value in every "
                                     "complete row, so there is nothing to explain.",
                                     {"column": spec.target, "value": float(self.y[0])})
        if not spec.intercept and not self.y.any():
            raise AnalysisInputError("constant_target", "The target is zero in every complete row.",
                                     {"column": spec.target})
        for j, name in enumerate(spec.predictors):
            x = self.X[:, j]
            if (spec.intercept and x.min() == x.max()) or not x.any():
                raise AnalysisInputError(
                    "constant_predictor",
                    f"Predictor '{name}' has the same value in every complete row; its coefficient "
                    "cannot be estimated" + (" separately from the intercept." if spec.intercept
                                             else "."),
                    {"column": name, "value": float(x[0])})


def _check_numeric(c: Column) -> None:
    if c.type == "empty":
        raise AnalysisInputError("all_missing", f"Column '{c.name}' has no values.",
                                 {"column": c.name})
    if c.type != "numeric":
        bad = [v for v in c.values if v is not None and not is_number(v)]
        raise AnalysisInputError("non_numeric_column",
                                 f"Column '{c.name}' is not numeric ({len(bad)} non-numeric "
                                 "values); regression needs numbers.",
                                 {"column": c.name, "non_numeric_count": len(bad),
                                  "examples": bad[:3]})


def _formula(spec: RegressSpec) -> str:
    return f"{spec.target} ~ {'1' if spec.intercept else '0'} + " + " + ".join(spec.predictors)


def _hash(plan_fields: dict) -> str:
    blob = json.dumps(plan_fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def plan_hash(plan: RegressPlan) -> str:
    """The hash `plan.plan_sha256` must equal for an unmodified plan."""
    return _hash(plan.model_dump(mode="json", exclude={"plan_sha256"}))


def prepare(ds: Dataset, spec: RegressSpec, config: ServiceConfig | None = None) -> RegressPlan:
    """Validate `spec` against `ds` and describe the fit without running it."""
    return _prepare(ds, spec, config or ServiceConfig())[0]


def _prepare(ds: Dataset, spec: RegressSpec, config: ServiceConfig
             ) -> tuple[RegressPlan, _Data, _Fit]:
    d = _Data(ds, spec, config)
    f = _Fit(d, spec)  # refuses exact collinearity now, before anything is approved
    dropped = d.rows_total - d.n
    warnings = _plan_warnings(d, spec, dropped)
    terms = (["b0"] if spec.intercept else []) + [f"b{i + 1}·{p}" for i, p in
                                                   enumerate(spec.predictors)]
    summary = (f"Fit {spec.target} = {' + '.join(terms)} + error by ordinary least squares on "
               f"{d.n} complete rows of {d.rows_total}"
               + (f" ({dropped} dropped for missing values)" if dropped else "")
               + f", reporting {round(spec.confidence_level * 100, 1):g}% confidence intervals "
               "and diagnostics. Results will describe associations in these rows.")
    fields = dict(service_version=__version__, dataset_sha256=ds.sha256, spec=spec,
                  formula=_formula(spec), summary=summary, rows_total=d.rows_total,
                  rows_used=d.n, rows_dropped=dropped, missing_by_column=d.missing,
                  parameters=d.p, df_resid=d.n - d.p, diagnostics_planned=DIAGNOSTICS_PLANNED,
                  warnings=tuple(warnings))
    draft = RegressPlan(**fields, plan_sha256="0" * 64)
    return draft.model_copy(update={"plan_sha256": plan_hash(draft)}), d, f


def _plan_warnings(d: _Data, spec: RegressSpec, dropped: int) -> list[RegressWarning]:
    w = []
    if dropped:
        cols = tuple(m.column for m in d.missing if m.missing)
        w.append(RegressWarning(code="rows_dropped", columns=cols, message=(
            f"{dropped} of {d.rows_total} rows were dropped: each has a missing value in a selected "
            "column. "
            "Results describe the complete rows only.")))
        if dropped / d.rows_total > DROPPED_HIGH:
            w.append(RegressWarning(code="high_dropped_fraction", columns=cols, message=(
                f"{dropped / d.rows_total:.0%} of rows were dropped. If missingness is related "
                "to the values, the complete rows may not represent the dataset.")))
    if d.n < OBS_PER_PREDICTOR * d.k:
        w.append(RegressWarning(code="few_observations_per_predictor", message=(
            f"{d.n} rows for {d.k} predictors (fewer than {OBS_PER_PREDICTOR} per predictor): "
            "estimates will be imprecise and unstable.")))
    if d.n - d.p < SMALL_DF:
        w.append(RegressWarning(code="small_residual_df", message=(
            f"Only {d.n - d.p} residual degrees of freedom: uncertainty estimates and diagnostic "
            "tests rely heavily on the normal-error assumption and have little power.")))
    if len(set(d.y.tolist())) == 2:
        w.append(RegressWarning(code="binary_target", columns=(spec.target,), message=(
            "The target takes only two values. A linear model of a binary outcome (linear "
            "probability model) can give fitted values outside the observed range and has "
            "non-constant variance by construction.")))
    if d.precision_loss:
        w.append(RegressWarning(code="precision_loss", columns=d.precision_loss, message=(
            "Integers at or beyond 2**53 cannot be represented exactly as floating-point "
            "numbers; their values were rounded.")))
    return w


# ---------------------------------------------------------------------------
# fitting
# ---------------------------------------------------------------------------

def _pow2(np, a):
    """Exact power-of-two scale making max|a| lie in [0.5, 1)."""
    m = float(np.max(np.abs(a)))
    return 1.0 if m == 0 else math.ldexp(1.0, -math.frexp(m)[1])


def _mean(np, a):
    m = a.mean(axis=0)
    return m + (a - m).mean(axis=0)  # second pass removes the first pass's rounding error


class _Fit:
    """Least-squares fit in scaled units; see the module docstring for the method."""

    def __init__(self, d: _Data, spec: RegressSpec):
        np = _np()
        self.np = np
        self.d, self.spec = d, spec
        n, k = d.n, d.k
        self.cx = np.array([_pow2(np, d.X[:, j]) for j in range(k)])
        self.cy = _pow2(np, d.y)
        X = d.X * self.cx
        y = d.y * self.cy
        if spec.intercept:
            self.mx, self.my = _mean(np, X), float(_mean(np, y))
            Xc, yc = X - self.mx, y - self.my
        else:
            self.mx, self.my = np.zeros(k), 0.0
            Xc, yc = X, y
        self.s = np.sqrt((Xc * Xc).sum(axis=0))
        U, S, Vt = np.linalg.svd(Xc / self.s, full_matrices=False)
        self.ratio = float(S[-1] / S[0])
        if self.ratio < COLLINEAR_RATIO:
            v = np.abs(Vt[-1])
            involved = [spec.predictors[j] for j in range(k) if v[j] > 1e-3 * v.max()]
            raise AnalysisInputError(
                "perfect_collinearity",
                "Some predictors are exact (or numerically exact) linear combinations of others"
                + (" and the intercept" if spec.intercept else "")
                + ", so their separate coefficients cannot be estimated: " + ", ".join(involved)
                + ". Remove or combine one of them.",
                {"columns": involved, "singular_value_ratio": self.ratio})
        self.U, self.S, self.V = U, S, Vt.T
        uty = U.T @ yc
        self.b = (self.V @ (uty / S)) / self.s                 # slopes, scaled units
        resid = yc - U @ uty
        resid = resid - U @ (U.T @ resid)                      # one refinement step
        self.resid = resid
        self.fitted = y - resid
        self.rss = float(resid @ resid)
        self.tss = float(yc @ yc)
        self.df = n - d.p
        self.perfect = math.sqrt(self.rss) <= PERFECT_FIT * math.sqrt(self.tss)
        self.sigma2 = self.rss / self.df
        self.lev = (U * U).sum(axis=1) + (1.0 / n if spec.intercept else 0.0)
        # slope covariance / sigma^2 in scaled units: D V diag(1/S^2) V^T D
        W = self.V / S
        self.slope_cov = (W @ W.T) / np.outer(self.s, self.s)

    # -- quantities in original units --------------------------------------

    def coefficients(self):
        """Estimates, standard errors and covariance in original units.

        Everything is formed in scaled units first; only the final scale
        factors (exact powers of two) are applied. A standard error can be
        representable while its square is not, so standard errors are scaled
        separately and the covariance is None if it overflows or underflows.
        """
        np, sp = self.np, self.spec
        unit = np.concatenate(([1.0], self.cx)) if sp.intercept else self.cx  # per term
        est = self.b
        cov = self.slope_cov
        if sp.intercept:
            est = np.concatenate(([self.my - float(self.mx @ self.b)], self.b))
            c_ab = -(cov @ self.mx)
            full = np.empty((self.d.p, self.d.p))
            full[0, 0] = 1.0 / self.d.n + float(self.mx @ cov @ self.mx)
            full[0, 1:], full[1:, 0], full[1:, 1:] = c_ab, c_ab, cov
            cov = full
        cov = self.sigma2 * cov                 # scaled units
        se = np.sqrt(np.diag(cov))
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            orig = cov * np.outer(unit, unit) / self.cy / self.cy
        ok = bool(np.isfinite(orig).all()) and not bool(((orig == 0) & (cov != 0)).any())
        return est * unit / self.cy, se * unit / self.cy, est, se, (orig if ok else None)


def _measure(d: _Data, f: _Fit, spec: RegressSpec
             ) -> tuple[Measured, list[RegressWarning], dict[str, str]]:
    np = f.np
    n, k, p, df = d.n, d.k, d.p, f.df
    unavailable: dict[str, str] = {}
    warnings: list[RegressWarning] = []
    est, se, est_s, se_s, cov = f.coefficients()
    terms = ([INTERCEPT] if spec.intercept else []) + list(spec.predictors)

    # coefficients ---------------------------------------------------------
    alpha = (1.0 - spec.confidence_level) / 2.0
    tq = dist.t_ppf_upper(alpha, df)
    vif = _vif(f, spec)
    std = (f.b * f.s / math.sqrt(f.tss)) if spec.intercept else None
    coefs = []
    for i, term in enumerate(terms):
        j = i - int(spec.intercept)  # predictor index, -1 for the intercept
        if f.perfect:
            s_, t_, p_, lo, hi = None, None, None, None, None
        else:
            s_ = _fin(se[i])
            t_ = float(est_s[i] / se_s[i]) if se_s[i] > 0 else None  # scale-free
            p_ = dist.t_sf2(t_, df) if t_ is not None else None
            lo, hi = float(est[i] - tq * s_), float(est[i] + tq * s_)
        coefs.append(Coefficient(term=term, estimate=_fin(est[i]), std_error=s_, t=t_, p=p_,
                                 ci_low=lo, ci_high=hi,
                                 standardized=None if j < 0 or std is None else float(std[j]),
                                 vif=None if j < 0 or vif is None else float(vif[j])))
    if f.perfect:
        reason = "the model fits the data exactly (residuals are zero to rounding), so uncertainty is undefined"
        for key in ("std_error", "t", "p", "confidence_interval", "f_statistic",
                    "log_likelihood", "studentized_residuals", "cooks_distance",
                    "breusch_pagan", "jarque_bera", "reset", "durbin_watson"):
            unavailable[key] = reason
        warnings.append(RegressWarning(code="perfect_fit", message=(
            "The predictors reproduce the target exactly. Check whether the target was computed "
            "from the predictors; a perfect fit on measured data is unusual.")))

    # fit statistics -------------------------------------------------------
    r2 = 1.0 - f.rss / f.tss
    df1 = k if spec.intercept else p
    adj = 1.0 - (1.0 - r2) * (n - int(spec.intercept)) / df
    fstat = fp = ll = aic = bic = None
    if not f.perfect:
        fstat = ((f.tss - f.rss) / df1) / f.sigma2
        fp = dist.f_sf(fstat, df1, df)
        log_rss = math.log(f.rss) - 2.0 * math.log(f.cy)   # rss in original units, as a log
        ll = -n / 2.0 * (math.log(2 * math.pi) + log_rss - math.log(n) + 1.0)
        aic, bic = -2 * ll + 2 * (p + 1), -2 * ll + math.log(n) * (p + 1)
    sigma = math.sqrt(f.sigma2) / f.cy
    fit_stats = FitStatistics(n=n, parameters=p, df_model=df1, df_resid=df, r_squared=r2,
                              r_squared_definition="centred" if spec.intercept else "uncentred",
                              adj_r_squared=adj, sigma=sigma, f_statistic=fstat, f_df1=df1,
                              f_df2=df, f_p=fp, log_likelihood=ll, aic=aic, bic=bic)

    # rows ------------------------------------------------------------------
    e = f.resid / f.cy
    h = f.lev
    rows = d.rows.tolist()
    std_r = stud = cook = [None] * n
    if not f.perfect:
        with np.errstate(divide="ignore", invalid="ignore"):
            r = f.resid / (math.sqrt(f.sigma2) * np.sqrt(1.0 - h))
            std_r = _opt(r, h)
            cook = _opt(r * r * h / (p * (1.0 - h)), h)
            if df > 1:
                stud = _opt(r * np.sqrt((df - 1) / np.maximum(df - r * r, 0.0)), h)
            else:
                unavailable["studentized_residuals"] = "needs at least 2 residual degrees of freedom"
    row_diag = RowDiagnostics(rows=tuple(rows), fitted=tuple((f.fitted / f.cy).tolist()),
                              residual=tuple(e.tolist()), leverage=tuple(h.tolist()),
                              standardized_residual=tuple(std_r),
                              studentized_residual=tuple(stud), cooks_distance=tuple(cook))

    # diagnostics -----------------------------------------------------------
    q = np.quantile(e, [0, 0.25, 0.5, 0.75, 1])  # R type 7
    tests, dw = [], None
    if not f.perfect:
        dw = float((np.diff(f.resid) ** 2).sum() / f.rss)
        tests = [_breusch_pagan(f, spec, unavailable), _jarque_bera(f),
                 _reset(f, spec, unavailable)]
    high_lev = [rows[i] for i in np.flatnonzero(h > 2.0 * p / n)]
    infl = sorted(((c, rows[i]) for i, c in enumerate(cook) if c is not None and c > 4.0 / n),
                  key=lambda t: (-t[0], t[1]))
    outl = [rows[i] for i, t in enumerate(stud) if t is not None and abs(t) > OUTLIER_T]
    cond = float(f.S[0] / f.S[-1])
    diags = Diagnostics(residuals=ResidualSummary(min=q[0], q1=q[1], median=q[2], q3=q[3], max=q[4]),
                        durbin_watson=dw, tests=tuple(tests), condition_number=cond,
                        high_leverage_rows=tuple(high_lev),
                        influential_rows=tuple(r_ for _, r_ in infl),
                        outlier_rows=tuple(outl))
    if vif is None:
        unavailable["vif"] = "defined only for models with an intercept"
    ranges = tuple(PredictorRange(name=nm, min=float(d.X[:, j].min()), max=float(d.X[:, j].max()),
                                  mean=float(_mean(np, d.X[:, j] * f.cx[j]) / f.cx[j]))
                   for j, nm in enumerate(spec.predictors))
    if cov is None and not f.perfect:
        unavailable["covariance"] = "outside the floating-point range for these data's magnitudes"
    cov_t = None if f.perfect or cov is None else tuple(tuple(float(v) for v in row) for row in cov)
    measured = Measured(fit=fit_stats, coefficients=tuple(coefs), covariance=cov_t,
                        diagnostics=diags, predictor_ranges=ranges, rows=row_diag)
    warnings += _fit_warnings(measured, spec, f, vif)
    return measured, warnings, unavailable


def _fin(x) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise AnalysisInputError("numerical_failure", "The fit produced a non-finite value; the "
                                 "data may span too wide a range of magnitudes to fit reliably.")
    return x


def _opt(a, h) -> list:
    """Per-row values; None where the row has leverage 1 (value undefined)."""
    return [None if hi >= 1.0 - 1e-12 or not math.isfinite(v) else float(v)
            for v, hi in zip(a.tolist(), h.tolist())]


def _vif(f: _Fit, spec: RegressSpec):
    if not spec.intercept:
        return None
    # (Q^T Q)^-1 for unit-length centred columns is the inverse correlation matrix
    return (f.V ** 2 / f.S ** 2).sum(axis=1)


def _breusch_pagan(f: _Fit, spec: RegressSpec, unavailable: dict) -> DiagnosticTest:
    checks = "constant error variance (small p: variance changes with the predictors)"
    if not spec.intercept:
        unavailable["breusch_pagan"] = "computed only for models with an intercept"
        return DiagnosticTest(name="breusch_pagan", checks=checks, statistic=None, df=(f.d.k,),
                              p=None, reason=unavailable["breusch_pagan"])
    z = f.resid ** 2
    z = z / z.mean()
    zc = z - z.mean()
    tot = float(zc @ zc)
    if tot <= 0.0:
        unavailable["breusch_pagan"] = "all squared residuals are equal"
        return DiagnosticTest(name="breusch_pagan", checks=checks, statistic=None, df=(f.d.k,),
                              p=None, reason=unavailable["breusch_pagan"])
    proj = f.U.T @ zc
    lm = f.d.n * float(proj @ proj) / tot
    return DiagnosticTest(name="breusch_pagan", checks=checks, statistic=lm, df=(f.d.k,),
                          p=dist.chi2_sf(lm, f.d.k))


def _jarque_bera(f: _Fit) -> DiagnosticTest:
    np = f.np
    e = f.resid - f.resid.mean()
    m2 = float((e ** 2).mean())
    skew = float((e ** 3).mean()) / m2 ** 1.5
    kurt = float((e ** 4).mean()) / m2 ** 2
    jb = f.d.n / 6.0 * (skew ** 2 + (kurt - 3.0) ** 2 / 4.0)
    return DiagnosticTest(name="jarque_bera", statistic=jb, df=(2,), p=dist.chi2_sf(jb, 2),
                          checks="normal errors (small p: residual skewness or kurtosis "
                                 "differs from a normal distribution)")


def _reset(f: _Fit, spec: RegressSpec, unavailable: dict) -> DiagnosticTest:
    np = f.np
    checks = "linearity (small p: a curved relationship fits better than the linear model)"
    df2 = f.df - 1
    reason = None
    if df2 < 1:
        reason = "needs at least 2 residual degrees of freedom"
    else:
        w = f.fitted ** 2
        if spec.intercept:
            w = w - _mean(np, w)
        norm0 = math.sqrt(float(w @ w))
        for _ in range(2):  # orthogonalise twice for accuracy
            w = w - f.U @ (f.U.T @ w)
        norm = math.sqrt(float(w @ w))
        if norm0 == 0.0 or norm <= COLLINEAR_RATIO * norm0 * 1e3:
            reason = "fitted^2 is collinear with the predictors (e.g. a single binary predictor)"
    if reason:
        unavailable["reset"] = reason
        return DiagnosticTest(name="reset", checks=checks, statistic=None, df=(1, max(df2, 0)),
                              p=None, reason=reason)
    gain = float(f.resid @ w) ** 2 / float(w @ w)
    rss2 = f.rss - gain
    if rss2 <= 0.0:
        unavailable["reset"] = "adding fitted^2 fits the data exactly"
        return DiagnosticTest(name="reset", checks=checks, statistic=None, df=(1, df2), p=None,
                              reason=unavailable["reset"])
    F = gain / (rss2 / df2)
    return DiagnosticTest(name="reset", checks=checks, statistic=F, df=(1, df2),
                          p=dist.f_sf(F, 1, df2))


def _fit_warnings(m: Measured, spec: RegressSpec, f: _Fit, vif) -> list[RegressWarning]:
    w = []
    dg, n = m.diagnostics, m.fit.n
    if vif is not None:
        high = tuple(c.term for c in m.coefficients if c.vif is not None and c.vif > VIF_HIGH)
        if high:
            w.append(RegressWarning(code="high_collinearity", columns=high, message=(
                f"VIF above {VIF_HIGH:g}: these predictors are strongly related to the other "
                "predictors, so their separate coefficients are imprecise and sensitive to "
                "which predictors are included.")))
    if f.ratio < PRECISION_RATIO:
        w.append(RegressWarning(code="numerical_precision", message=(
            f"The predictor matrix is close to singular (condition number {1 / f.ratio:.3g}); "
            f"about {math.log10(1 / f.ratio):.0f} of the ~16 significant digits may be lost.")))
    for code, rows, text in (
            ("influential_rows", dg.influential_rows,
             f"have Cook's distance above 4/n = {4 / n:.3g}: removing any one of them would "
             "change the coefficients noticeably."),
            ("high_leverage_rows", dg.high_leverage_rows,
             f"have leverage above 2p/n = {2 * m.fit.parameters / n:.3g} (unusual predictor "
             "values)."),
            ("outlier_rows", dg.outlier_rows,
             f"have |studentized residual| above {OUTLIER_T:g}.")):
        if rows:
            shown = ", ".join(map(str, rows[:MAX_LISTED_ROWS]))
            more = f" and {len(rows) - MAX_LISTED_ROWS} more" if len(rows) > MAX_LISTED_ROWS else ""
            w.append(RegressWarning(code=code, message=f"Rows {shown}{more} {text}"))
    for t in dg.tests:
        if t.p is None or t.p >= ALPHA:
            continue
        code, text = {
            "breusch_pagan": ("heteroscedasticity", "residual variance appears to change with "
                              "the predictors; standard errors and p-values may be wrong."),
            "jarque_bera": ("non_normal_residuals", "residuals do not look normally distributed; "
                            "in small samples intervals and p-values may be inaccurate."),
            "reset": ("nonlinearity", "a curved relationship fits better; the linear model may "
                      "be misspecified."),
        }[t.name]
        w.append(RegressWarning(code=code, message=f"{t.name} p = {t.p:.3g} < {ALPHA}: {text}"))
    if spec.row_order_meaningful and dg.durbin_watson is not None \
            and not 1.5 <= dg.durbin_watson <= 2.5:
        w.append(RegressWarning(code="autocorrelation", message=(
            f"Durbin-Watson = {dg.durbin_watson:.3g} (far from 2): neighbouring residuals are "
            "correlated, so errors may not be independent and standard errors may be too small.")))
    return w


# ---------------------------------------------------------------------------
# assumptions and interpretation (templates; association language only)
# ---------------------------------------------------------------------------

def _g(v: float | None) -> str:
    return "n/a" if v is None else f"{v:.4g}"


def _assumptions(m: Measured, spec: RegressSpec, plan: RegressPlan) -> tuple[Assumption, ...]:
    tests = {t.name: t for t in m.diagnostics.tests}

    def from_test(name, test_name, statement):
        t = tests.get(test_name)
        if t is None or t.p is None:
            return Assumption(name=name, statement=statement, check="unavailable",
                              evidence=t.reason if t is not None and t.reason else
                              "the check could not be computed for this fit")
        bad = t.p < ALPHA
        return Assumption(name=name, statement=statement,
                          check="contradicted" if bad else "not_contradicted",
                          evidence=f"{test_name} p = {t.p:.3g}" + (
                              "" if bad else "; this does not show the assumption holds, "
                              "only that this test did not detect a departure"))

    dw = m.diagnostics.durbin_watson
    if not spec.row_order_meaningful:
        indep = Assumption(name="independence", check="not_checkable",
                           statement="Errors are independent across rows.",
                           evidence="Depends on how the data were collected (e.g. repeated "
                           "measurements of the same unit, batches, time order); rows were not "
                           "declared to be in a meaningful order, so it was not tested.")
    elif dw is None:
        indep = Assumption(name="independence", statement="Errors are independent across rows.",
                           check="unavailable", evidence="Durbin-Watson could not be computed")
    else:
        bad = not 1.5 <= dw <= 2.5
        indep = Assumption(name="independence", statement="Errors are independent across rows.",
                           check="contradicted" if bad else "not_contradicted",
                           evidence=f"Durbin-Watson = {dw:.3g} (about 2 when neighbouring "
                           "residuals are uncorrelated); checks only neighbouring rows")
    cond = m.diagnostics.condition_number
    return (
        from_test("linearity", "reset",
                  "The target's mean is a linear function of the predictors as entered."),
        indep,
        from_test("constant_variance", "breusch_pagan",
                  "Errors have the same variance for all predictor values."),
        from_test("normal_errors", "jarque_bera",
                  "Errors are normally distributed (matters mostly in small samples)."),
        Assumption(name="no_perfect_collinearity", check="not_contradicted",
                   statement="No predictor is an exact linear combination of the others.",
                   evidence=f"checked before fitting; condition number {_g(cond)}"),
        Assumption(name="predictors_without_error", check="not_checkable",
                   statement="Predictors are measured without substantial error.",
                   evidence="Cannot be checked from the data; measurement error in a predictor "
                   "typically shrinks its coefficient towards zero."),
        Assumption(name="relevant_variables_included", check="not_checkable",
                   statement="No omitted variable is related to both the target and the "
                   "included predictors.",
                   evidence="Cannot be checked from the data; an omitted variable of this kind "
                   "biases the coefficients."),
        Assumption(name="missing_data_ignorable",
                   check="not_checkable" if plan.rows_dropped else "not_contradicted",
                   statement="Rows dropped for missing values do not differ systematically from "
                   "the complete rows.",
                   evidence=(f"{plan.rows_dropped} rows dropped; cannot be checked from the "
                             "complete rows alone" if plan.rows_dropped else "no rows dropped")),
    )


def _interpretation(m: Measured, spec: RegressSpec, warnings: list[RegressWarning]
                    ) -> Interpretation:
    y, lvl = spec.target, f"{round(spec.confidence_level * 100, 1):g}%"
    fs = m.fit
    st = []
    if spec.intercept:
        st.append(f"The included predictors account for {fs.r_squared:.1%} of the variation in "
                  f"{y} across these {fs.n} rows (R² = {fs.r_squared:.4g}; adjusted "
                  f"{_g(fs.adj_r_squared)}). R² describes fit to these rows, not accuracy on new "
                  "data.")
    else:
        st.append(f"Without an intercept, R² = {fs.r_squared:.4g} is measured relative to zero and "
                  "is not comparable with the R² of a model with an intercept.")
    others = " with the other included predictors held fixed in the model" if len(
        spec.predictors) > 1 else ""
    for c in m.coefficients:
        if c.term == INTERCEPT:
            continue
        if c.ci_low is None:
            st.append(f"{c.term}: estimated slope {_g(c.estimate)}; its uncertainty is "
                      "unavailable (see `unavailable`).")
        elif c.ci_low > 0 or c.ci_high < 0:
            direction = "higher" if c.estimate > 0 else "lower"
            st.append(f"{c.term}: in these data, rows where {c.term} is one unit higher have "
                      f"{y} {direction} by {abs(c.estimate):.4g} on average{others} ({lvl} CI "
                      f"{_g(c.ci_low)} to {_g(c.ci_high)}). This is an association; it does not "
                      f"show that changing {c.term} would change {y}.")
        else:
            st.append(f"{c.term}: the data are compatible with no linear association with {y}"
                      f"{others} ({lvl} CI {_g(c.ci_low)} to {_g(c.ci_high)}, which includes "
                      "zero). This does not show that there is no association; the interval "
                      "gives the range of slopes the data are compatible with.")
    codes = {w.code: w for w in warnings}
    nxt = []
    if "influential_rows" in codes or "outlier_rows" in codes:
        nxt.append("Check the flagged rows for recording or measurement errors, and compare the "
                   "fit with and without them, before deciding whether any should be excluded.")
    if "nonlinearity" in codes:
        nxt.append("Plot residuals against fitted values and each predictor; consider whether a "
                   "transformation or a curved term is scientifically justified.")
    if "heteroscedasticity" in codes:
        nxt.append("Treat standard errors with caution; consider a variance-stabilising "
                   "transformation or robust standard errors (not available in regress@1).")
    if "high_collinearity" in codes:
        nxt.append("Decide whether the strongly related predictors measure overlapping things; "
                   "a model with fewer of them may answer the question more clearly.")
    if "few_observations_per_predictor" in codes or "small_residual_df" in codes:
        nxt.append("Estimates are imprecise; more observations, or fewer predictors chosen in "
                   "advance, would narrow the intervals.")
    if "rows_dropped" in codes:
        nxt.append("Compare rows with and without missing values to judge whether dropping them "
                   "could have changed the result.")
    nxt.append("To learn whether changing a predictor changes the target, a study in which the "
               "researcher sets that predictor (ideally randomised, with other conditions "
               "controlled) is needed; this regression alone cannot show it.")
    return Interpretation(statements=tuple(st), next_steps=tuple(nxt), basis=INTERPRETATION_BASIS)


# ---------------------------------------------------------------------------
# entry point for an approved plan
# ---------------------------------------------------------------------------

def run(ds: Dataset, plan: RegressPlan, approval: Approval,
        config: ServiceConfig | None = None) -> RegressResult:
    """Fit the approved plan. Refuses unless approval, plan and data all agree."""
    config = config or ServiceConfig()
    check_approval(plan, approval)
    fresh, d, f = _prepare(ds, plan.spec, config)
    if fresh.plan_sha256 != plan.plan_sha256:
        raise AnalysisInputError(
            "plan_mismatch",
            "The data or the service version differ from those the plan was prepared for; "
            "prepare and approve a new plan.",
            {"approved_plan": plan.plan_sha256, "current_plan": fresh.plan_sha256,
             "dataset_sha256": ds.sha256, "plan_dataset_sha256": plan.dataset_sha256})
    measured, fit_warnings, unavailable = _measure(d, f, plan.spec)
    warnings = list(fresh.warnings) + fit_warnings
    record = RunRecord(dataset_sha256=ds.sha256, plan_sha256=plan.plan_sha256, spec=plan.spec,
                       approved_by=approval.approved_by, approval_note=approval.note,
                       service_version=__version__, solver=SOLVER,
                       python_version=platform.python_version(), numpy_version=f.np.__version__)
    return RegressResult(run=record, measured=measured,
                         assumptions=_assumptions(measured, plan.spec, fresh),
                         interpretation=_interpretation(measured, plan.spec, warnings),
                         warnings=tuple(warnings), unavailable=unavailable,
                         limitations=LIMITATIONS)


def check_approval(plan: RegressPlan, approval: Approval) -> None:
    """Raise unless `approval` names this plan and the plan is unmodified."""
    if plan_hash(plan) != plan.plan_sha256:
        raise AnalysisInputError("plan_modified", "The plan's contents do not match its "
                                 "plan_sha256; it was changed after preparation.",
                                 {"plan_sha256": plan.plan_sha256})
    if approval.plan_sha256 != plan.plan_sha256:
        raise AnalysisInputError("approval_mismatch", "The approval is for a different plan.",
                                 {"approved": approval.plan_sha256, "plan": plan.plan_sha256})
