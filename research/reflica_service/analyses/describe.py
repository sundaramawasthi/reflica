"""describe@1 — descriptive statistics, data-quality issues and correlations.

Standard library only. Deterministic: the same dataset and configuration
always give the same result (column order is preserved; correlation pairs
follow column order).

Methods (also returned in `notes`):
- Missing cells are excluded per column; `missing_fraction` = missing / rows.
- Numeric stats use non-missing values: min, max, mean, median and sample
  standard deviation (n - 1, corrected two-pass). Values are rescaled by an
  exact power of two before centring, which is lossless and prevents both
  overflow and subnormal precision loss. The mean is kept within [min, max]. A
  statistic whose true value is outside the floating-point range is reported
  as unavailable with a reason, never as inf or a crash.
- Distinct counts are exact: integer columns are compared as Python ints,
  text columns as strings. Integers beyond 2**53 cannot be represented
  exactly as floats; the float-based statistics for such columns are flagged
  with `precision_loss`.
- Pearson r is computed per numeric pair on rows where both values are
  present (pairwise deletion). r is None when n < 3 or either side is
  constant on those rows. The first numeric columns, in column order, are
  correlated up to `max_correlation_columns` and up to a total work of
  `max_correlation_work` (pairs x rows); any others are listed in
  `correlations_skipped` with the limit that applied. Correlations are associations, never causal claims.
- Warnings (`issues`, correlation `warnings`) mark valid results that need
  care, e.g. small samples. Unavailable results (`unavailable`, `reason`)
  mark values that could not be computed.

This function has no time limit of its own; run it through
`reflica_service.execution.run_describe` to enforce the analysis timeout.
"""
from __future__ import annotations

import math
import operator
from itertools import compress, repeat

from .. import __version__
from ..csv_adapter import is_number
from ..models import (Column, ColumnSummary, Correlation, CorrelationSkip, Dataset,
                      DescribeResult, Issue, NumericStats, ServiceConfig)

HIGH_MISSING = 0.2
MIN_ID_ROWS = 5
SMALL_SAMPLE = 10
EXACT_FLOAT_INT = 2 ** 53
OUT_OF_RANGE = "true value is outside the floating-point range"

NOTES = (
    "Correlations are Pearson coefficients and describe associations only; they do not show cause and effect.",
    "Missing cells (empty, NA, N/A, NaN, null, None) are excluded per column; correlations use rows where both values are present.",
    "Standard deviation is the sample SD (n - 1).",
    "A column is numeric only if every non-missing value is a finite plain or scientific-notation number; integers with leading zeros are treated as text codes.",
    f"Results based on fewer than {SMALL_SAMPLE} values are valid but flagged as small samples.",
    "Issues and warnings are heuristics for review, not errors.",
)

_sumprod = getattr(math, "sumprod", None) or (lambda a, b: sum(map(operator.mul, a, b)))


def describe(ds: Dataset, config: ServiceConfig | None = None) -> DescribeResult:
    config = config or ServiceConfig()
    numbers = {c.name: c.numbers for c in ds.columns if c.type == "numeric"}
    columns: list[ColumnSummary] = []
    issues: list[Issue] = []
    if ds.numeric_header:
        issues.append(Issue(code="numeric_header",
                            message="Every column name is a number; check that the first row is a header, not data."))
    for c in ds.columns:
        s = _summary(c, numbers.get(c.name, ()), ds.row_count)
        columns.append(s)
        issues.extend(_issues(c, s, ds.row_count))
    if ds.duplicate_rows:
        issues.append(Issue(code="duplicate_rows",
                            message=f"{ds.duplicate_rows} row(s) repeat an earlier row exactly."))

    numeric = [c.name for c in ds.columns if c.type == "numeric"]
    k, reason = _correlation_columns(len(numeric), ds.row_count, config)
    used, skipped = numeric[:k], numeric[k:]
    budget = _Budget(config.correlation_refine_budget_rows)
    correlations = _correlations(used, numbers, budget)
    if budget.exhausted:
        issues.append(Issue(code="correlations_unrefined",
                            message=f"{budget.exhausted} correlation(s) were not computed: they needed exact "
                                    "recomputation and the recomputation budget was used up."))
    skip = None
    if skipped:
        total = len(numeric) * (len(numeric) - 1) // 2
        skip = CorrelationSkip(reason=reason, limit=k, computed_columns=tuple(used),
                               skipped_columns=tuple(skipped),
                               skipped_pairs=total - len(correlations))
    return DescribeResult(service_version=__version__, dataset_sha256=ds.sha256,
                          row_count=ds.row_count, column_count=len(ds.columns),
                          columns=tuple(columns), correlations=correlations,
                          correlations_skipped=skip, issues=tuple(issues), notes=NOTES)


def _correlation_columns(numeric: int, rows: int, config: ServiceConfig) -> tuple[int, str]:
    """How many numeric columns to correlate, and which limit applies.

    Work grows with pairs x rows, so the column count is the largest k with
    k(k-1)/2 * rows <= max_correlation_work, capped at max_correlation_columns.
    """
    k_work = 1
    while k_work < numeric and (k_work + 1) * k_work // 2 * rows <= config.max_correlation_work:
        k_work += 1
    k = min(k_work, config.max_correlation_columns, numeric)
    # the reason is only reported when columns are skipped; when both limits
    # bind, the configured column cap is reported
    binding_cap = k in (numeric, config.max_correlation_columns)
    return k, "column_limit" if binding_cap else "work_limit"


# ---------------------------------------------------------------------------
# Per-column statistics
# ---------------------------------------------------------------------------

def _summary(c: Column, nums: tuple[float | None, ...], rows: int) -> ColumnSummary:
    present = [v for v in c.values if v is not None]
    missing = rows - len(present)
    if c.integer:
        unique = len({int(v) for v in present})
    elif c.type == "numeric":
        unique = len({x for x in nums if x is not None})
    else:
        unique = len(set(present))
    stats = _numeric_stats([x for x in nums if x is not None]) if c.type == "numeric" else None
    return ColumnSummary(name=c.name, type=c.type, integer=c.integer, count=len(present),
                         missing=missing, missing_fraction=missing / rows,
                         unique=unique, numeric=stats)


def _centre(xs: list[float]) -> tuple[list[float], float, int]:
    """Deviations from the mean, the mean, and the binary exponent of the unit.

    Values are first rescaled by an exact power of two so the largest has
    magnitude in [0.5, 1). Power-of-two scaling is lossless, so this keeps
    full precision while preventing overflow near the float limit and loss
    of precision among subnormal values. The true deviation is
    `ldexp(d, exp)`.
    """
    n = len(xs)
    lo, hi = min(xs), max(xs)
    if lo == hi:  # constant: exact zero deviations, exact mean
        return [0.0] * n, lo, 0
    exp = _exponent(max(-lo, hi))
    ys = list(map(math.ldexp, xs, repeat(-exp)))  # |y| < 1: sums cannot overflow
    mean_s = math.fsum(ys) / n
    mean = math.ldexp(mean_s, exp)
    return list(map(operator.sub, ys, repeat(mean_s))), min(max(mean, lo), hi), exp


def _exponent(big: float) -> int:
    """Binary exponent e with big in [2**(e-1), 2**e); 0 for big == 0."""
    return math.frexp(big)[1] if big else 0


def _numeric_stats(xs: list[float]) -> NumericStats:
    n = len(xs)
    unavailable: dict[str, str] = {}
    devs, mean, exp = _centre(xs)
    sd: float | None = None
    if n < 2:
        unavailable["sd"] = "needs at least 2 values"
    else:
        s = max(abs(d) for d in devs)
        if s == 0:
            sd = 0.0
        else:  # rescale deviations so squaring cannot overflow
            ds = [d / s for d in devs]
            # corrected two-pass: subtracting (sum d)^2 / n cancels the rounding error of the mean
            ss = math.fsum(d * d for d in ds) - math.fsum(ds) ** 2 / n
            sd = _scaled(math.sqrt(max(ss, 0.0) / (n - 1)) * s, exp)
            if sd is None:
                unavailable["sd"] = OUT_OF_RANGE
    return NumericStats(min=min(xs), max=max(xs), mean=mean, median=_median(xs), sd=sd,
                        unavailable=unavailable)


def _scaled(v: float, exp: int) -> float | None:
    """ldexp(v, exp), or None if the result is outside the float range."""
    try:
        out = math.ldexp(v, exp)
    except OverflowError:
        return None
    return out if math.isfinite(out) else None


def _median(xs: list[float]) -> float:
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    lo, hi = s[mid - 1], s[mid]
    total = lo + hi
    return total / 2 if math.isfinite(total) else lo / 2 + hi / 2


# ---------------------------------------------------------------------------
# Issues (warnings for review)
# ---------------------------------------------------------------------------

def _issues(c: Column, s: ColumnSummary, rows: int) -> list[Issue]:
    if s.count == 0:
        return [Issue(code="all_missing", column=c.name, message="Every value is missing.")]
    out: list[Issue] = []
    if s.unique == 1:
        out.append(Issue(code="constant_column", column=c.name,
                         message="Only one distinct value; it cannot explain variation."))
    if s.missing_fraction > HIGH_MISSING:
        out.append(Issue(code="high_missing", column=c.name,
                         message=f"{s.missing_fraction:.0%} of values are missing."))
    if c.type == "mixed":
        bad = sum(1 for v in c.values if v is not None and not is_number(v))
        out.append(Issue(code="non_numeric_in_numeric", column=c.name,
                         message=f"Mostly numeric, but {bad} value(s) are not numbers."))
    if c.leading_zeros:
        out.append(Issue(code="leading_zeros", column=c.name,
                         message="Integer-like values with leading zeros (e.g. 007); treated as text codes, not numbers."))
    if c.integer and any(abs(int(v)) > EXACT_FLOAT_INT for v in c.values if v is not None):
        out.append(Issue(code="precision_loss", column=c.name,
                         message="Some integers exceed 2^53; distinct counts are exact, but mean, median and SD are approximate."))
    if c.type == "numeric" and s.count < SMALL_SAMPLE:
        out.append(Issue(code="small_sample", column=c.name,
                         message=f"Only {s.count} value(s); statistics may be unreliable."))
    if (s.missing == 0 and s.unique == rows and rows >= MIN_ID_ROWS
            and (c.type == "text" or c.integer)):
        out.append(Issue(code="possible_id_column", column=c.name,
                         message="Every value is distinct; this may be an identifier, not a measurement."))
    return out


# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------

class _Prepared:
    """A numeric column prepared for correlation.

    Values are centred on the column *median* and rescaled to |z| <= 1 by
    an exact power of two. The median is robust to outliers, and because
    |mean - median| <= SD the complete-column formula can lose at most one
    bit to cancellation. Missing cells become 0 with a 0/1 mask, so every
    per-pair sum is a single C-level sumprod call (extended precision).
    """

    __slots__ = ("filled", "z", "_z2", "mask", "complete", "ss", "sz")

    def __init__(self, nums: tuple[float | None, ...], ones: list[float]):
        present = [x for x in nums if x is not None]
        self.complete = len(present) == len(nums)
        # original values with 0.0 for missing, for the exact per-pair path
        self.filled = list(present) if self.complete else [0.0 if x is None else x for x in nums]
        exp = _exponent(max(map(abs, present)))
        med = math.ldexp(_median(present), -exp)  # overflow-safe median
        ys = map(math.ldexp, self.filled, repeat(-exp))
        self.mask = ones if self.complete else [0.0 if x is None else 1.0 for x in nums]
        z = list(map(operator.mul, map(operator.sub, ys, repeat(med)), self.mask))
        e2 = _exponent(max(map(abs, z)))
        self.z = list(map(math.ldexp, z, repeat(-e2)))  # exact rescale to |z| < 1
        self._z2: list[float] | None = None
        n = len(self.z)
        self.sz = math.fsum(self.z)
        self.ss = _sumprod(self.z, self.z) - self.sz * self.sz / n

    @property
    def z2(self) -> list[float]:
        if self._z2 is None:
            self._z2 = list(map(operator.mul, self.z, self.z))
        return self._z2


class _Budget:
    """Rows the exact per-pair path may still process in this analysis."""

    __slots__ = ("rows", "exhausted")

    def __init__(self, rows: int):
        self.rows = rows
        self.exhausted = 0  # pairs left unrefined because the budget ran out


def _correlations(names: list[str], numbers: dict[str, tuple[float | None, ...]],
                  budget: _Budget) -> tuple[Correlation, ...]:
    ones = [1.0] * len(next(iter(numbers.values()), ()))
    prepared = {n: _Prepared(numbers[n], ones) for n in names}
    return tuple(_pearson(a, b, prepared[a], prepared[b], budget)
                 for i, a in enumerate(names) for b in names[i + 1:])


# If a pair's centred sum of squares is below this fraction of its raw sum of
# squares, the fast one-pass formula may have lost too many digits to
# cancellation (or underflowed); the pair is then recomputed exactly.
REFINE_TOL = 1e-6
UNREFINED = "not computed: the pair is numerically ill-conditioned and the exact-recomputation budget was used up"


def _pearson(xname: str, yname: str, a: _Prepared, b: _Prepared, budget: _Budget) -> Correlation:
    if a.complete and b.complete:
        n = len(a.z)
        if n < 3:
            return Correlation(x=xname, y=yname, n=n, r=None, reason="fewer than 3 paired values")
        sxx, syy = a.ss, b.ss
        sxy = _sumprod(a.z, b.z) - a.sz * b.sz / n
        if sxx <= 0 or syy <= 0:
            return _constant(xname, yname, n)
    else:
        n = round(_sumprod(a.mask, b.mask))
        if n < 3:
            return Correlation(x=xname, y=yname, n=n, r=None, reason="fewer than 3 paired values")
        sx, sy = _sumprod(a.z, b.mask), _sumprod(b.z, a.mask)
        rawx, rawy = _sumprod(a.z2, b.mask), _sumprod(b.z2, a.mask)
        sxx, syy = rawx - sx * sx / n, rawy - sy * sy / n
        sxy = _sumprod(a.z, b.z) - sx * sy / n  # zero-filled: only paired rows contribute
        if sxx <= REFINE_TOL * rawx or syy <= REFINE_TOL * rawy:
            if budget.rows < n:
                budget.exhausted += 1
                return Correlation(x=xname, y=yname, n=n, r=None, reason=UNREFINED)
            budget.rows -= n
            return _pearson_exact(xname, yname, a, b)
    return _result(xname, yname, n, sxy / (math.sqrt(sxx) * math.sqrt(syy)))


def _pearson_exact(xname: str, yname: str, a: _Prepared, b: _Prepared) -> Correlation:
    """Two-pass Pearson on the paired rows only, from the original values,
    each side centred on its own paired mean and rescaled by a power of two,
    so neither cancellation nor underflow can occur. C-level iteration only."""
    sel = list(map(operator.mul, a.mask, b.mask))
    xs, ys = list(compress(a.filled, sel)), list(compress(b.filled, sel))
    n = len(xs)
    dx, dy = _unit_devs(xs), _unit_devs(ys)
    if dx is None or dy is None:
        return _constant(xname, yname, n)
    sx, sy = math.fsum(dx), math.fsum(dy)
    sxx = _sumprod(dx, dx) - sx * sx / n
    syy = _sumprod(dy, dy) - sy * sy / n
    sxy = _sumprod(dx, dy) - sx * sy / n
    if sxx <= 0 or syy <= 0:
        return _constant(xname, yname, n)
    return _result(xname, yname, n, sxy / (math.sqrt(sxx) * math.sqrt(syy)))


def _unit_devs(xs: list[float]) -> list[float] | None:
    """Deviations from the mean rescaled (power of two) to max |d| < 1; None if all equal."""
    devs = _centre(xs)[0]
    e = _exponent(max(map(abs, devs)))
    return None if e == 0 and not any(devs) else list(map(math.ldexp, devs, repeat(-e)))


def _constant(xname: str, yname: str, n: int) -> Correlation:
    return Correlation(x=xname, y=yname, n=n, r=None, reason="a column is constant on the paired rows")


def _result(xname: str, yname: str, n: int, r: float) -> Correlation:
    if not math.isfinite(r):  # safety net: never clamp NaN/inf into a plausible r
        return Correlation(x=xname, y=yname, n=n, r=None, reason="numerical failure: result was not finite")
    r = max(-1.0, min(1.0, r))
    warnings = (f"only {n} paired values; r may be unreliable",) if n < SMALL_SAMPLE else ()
    return Correlation(x=xname, y=yname, n=n, r=r, warnings=warnings)
