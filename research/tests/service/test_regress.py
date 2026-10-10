"""regress@1: known answers from R, validation, approval flow, uncertainty and diagnostics.

Reference values in data/regress_reference/ were produced by make_reference.R
(R 4.3.3, base R only); R is not needed to run these tests.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import time
from pathlib import Path

import pytest
from pydantic import ValidationError

np = pytest.importorskip("numpy")

from reflica_service.analyses import _distributions as dist  # noqa: E402
from reflica_service.analyses import regress  # noqa: E402
from reflica_service.csv_adapter import parse_csv  # noqa: E402
from reflica_service.execution import AnalysisTimeout, prepare_regress, run_regress  # noqa: E402
from reflica_service.models import (AnalysisInputError, Approval, RegressSpec,  # noqa: E402
                                    ServiceConfig)

REF = Path(__file__).parent / "data" / "regress_reference"
CASES = ["longley", "mtcars", "cars_no_intercept", "airquality"]


def _csv(rows: list[list], header: list[str]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode()


def _arrays_csv(**cols) -> bytes:
    names = list(cols)
    n = len(cols[names[0]])
    return _csv([[("" if cols[c][i] is None else repr(float(cols[c][i]))) for c in names]
                 for i in range(n)], names)


def _approve(plan, who="researcher@lab"):
    return Approval(plan_sha256=plan.plan_sha256, approved_by=who)


def _fit(data: bytes, config=None, **spec):
    ds = parse_csv(data)
    plan = regress.prepare(ds, RegressSpec(**spec), config)
    return plan, regress.run(ds, plan, _approve(plan), config)


def _err(data: bytes, code: str, config=None, **spec) -> AnalysisInputError:
    with pytest.raises(AnalysisInputError) as e:
        regress.prepare(parse_csv(data), RegressSpec(**spec), config)
    assert e.value.code == code, e.value.message
    return e.value


def _close(actual, expected, rtol, atol=0.0):
    a = np.array([np.nan if v is None else v for v in actual], dtype=float)
    b = np.array([np.nan if v is None else v for v in expected], dtype=float)
    assert a.shape == b.shape
    np.testing.assert_allclose(a, b, rtol=rtol, atol=atol, equal_nan=True)


# ---------------------------------------------------------------------------
# distributions
# ---------------------------------------------------------------------------

def _dist_rows():
    with open(REF / "distributions.csv") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("row", _dist_rows(), ids=lambda r: f"{r['kind']}-{r['x']}-{r['df1']}-{r['df2']}")
def test_distributions_match_r(row):
    x, df1, want = float(row["x"]), float(row["df1"]), float(row["value"])
    if row["kind"] == "t2":
        got = dist.t_sf2(x, df1)
    elif row["kind"] == "f":
        got = dist.f_sf(x, df1, float(row["df2"]))
    elif row["kind"] == "chi2":
        got = dist.chi2_sf(x, df1)
    else:
        got = dist.t_ppf_upper((1 - x) / 2, df1)
    rtol = 1e-9 if df1 > 1000 or (row["df2"] and float(row["df2"]) > 1000) else 1e-11
    assert got == pytest.approx(want, rel=rtol, abs=1e-300)


def test_distribution_edges():
    assert dist.t_sf2(0.0, 5) == 1.0
    assert dist.t_sf2(math.inf, 5) == 0.0
    assert dist.f_sf(0.0, 2, 3) == 1.0 and dist.chi2_sf(0.0, 2) == 1.0
    assert dist.t_ppf_upper(0.5, 9) == 0.0
    assert dist.chi2_sf(10.0, 2) == pytest.approx(math.exp(-5.0), rel=1e-14)
    with pytest.raises(ValueError):
        dist.t_sf2(1.0, 0)


# ---------------------------------------------------------------------------
# known answers (R lm)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", params=CASES)
def case(request):
    ref = json.loads((REF / f"{request.param}.json").read_text())
    plan, res = _fit((REF / f"{request.param}.csv").read_bytes(), target=ref["target"],
                     predictors=tuple(ref["predictors"]), intercept=ref["intercept"],
                     confidence_level=ref["confidence_level"])
    return ref, plan, res


def test_known_answer_coefficients(case):
    ref, plan, res = case
    co = res.measured.coefficients
    assert [c.term for c in co] == ref["terms"]
    # longley is ill-conditioned (NIST StRD "higher difficulty"); it still agrees to ~1e-13
    _close([c.estimate for c in co], ref["estimate"], 1e-11)
    _close([c.std_error for c in co], ref["std_error"], 1e-11)
    _close([c.t for c in co], ref["t"], 1e-11)
    _close([c.p for c in co], ref["p"], 1e-10)
    _close([c.ci_low for c in co], ref["ci_low"], 1e-11)
    _close([c.ci_high for c in co], ref["ci_high"], 1e-11)
    _close([v for row in res.measured.covariance for v in row], ref["vcov"], 1e-11)


def test_known_answer_fit_statistics(case):
    ref, plan, res = case
    f = res.measured.fit
    assert (f.n, f.df_resid, f.f_df1, f.f_df2) == (ref["n"], ref["df_resid"], ref["f_df1"], ref["f_df2"])
    assert plan.rows_total == ref["n_rows"] and plan.rows_used == ref["n"]
    _close([f.sigma, f.r_squared, f.adj_r_squared, f.f_statistic, f.f_p,
            f.log_likelihood, f.aic, f.bic],
           [ref[k] for k in ("sigma", "r_squared", "adj_r_squared", "f_statistic", "f_p",
                             "log_likelihood", "aic", "bic")], 1e-11)
    assert f.r_squared_definition == ("centred" if ref["intercept"] else "uncentred")


def test_known_answer_rows(case):
    ref, _, res = case
    r = res.measured.rows
    assert list(r.rows) == ref["used_rows"]
    _close(r.fitted, ref["fitted"], 1e-12)
    # residuals near zero: compare on the scale of the residual SE
    _close(r.residual, ref["residuals"], 0, atol=1e-11 * ref["sigma"])
    _close(r.leverage, ref["leverage"], 1e-11)
    _close(r.cooks_distance, ref["cooks_distance"], 1e-9, atol=1e-14)
    _close(r.standardized_residual, ref["standardized_residuals"], 0, atol=1e-10)
    _close(r.studentized_residual, ref["studentized_residuals"], 0, atol=1e-10)


def test_known_answer_diagnostics(case):
    ref, _, res = case
    d = res.measured.diagnostics
    rs = d.residuals
    _close([rs.min, rs.q1, rs.median, rs.q3, rs.max], ref["residual_quantiles"], 0,
           atol=1e-11 * ref["sigma"])
    tests = {t.name: t for t in d.tests}
    _close([d.durbin_watson, tests["jarque_bera"].statistic, tests["jarque_bera"].p],
           [ref["durbin_watson"], ref["jarque_bera"], ref["jarque_bera_p"]], 1e-10)
    _close([tests["reset"].statistic, tests["reset"].p], [ref["reset_f"], ref["reset_p"]], 1e-9)
    assert tests["reset"].df == (ref["reset_df1"], ref["reset_df2"])
    if ref["intercept"]:
        bp = tests["breusch_pagan"]
        _close([bp.statistic, bp.p], [ref["breusch_pagan"], ref["breusch_pagan_p"]], 1e-10)
        assert bp.df == (ref["breusch_pagan_df"],)
        _close([c.vif for c in res.measured.coefficients[1:]], ref["vif"], 1e-10)
        _close([c.standardized for c in res.measured.coefficients[1:]],
               ref["standardized_coefficients"], 1e-11)
        assert d.condition_number == pytest.approx(ref["condition_number"], rel=1e-10)
    else:
        assert tests["breusch_pagan"].statistic is None
        assert "breusch_pagan" in res.unavailable and "vif" in res.unavailable


def test_known_answer_flags_agree_with_reference_values(case):
    ref, _, res = case
    n, p = ref["n"], len(ref["terms"])
    d = res.measured.diagnostics
    rows = ref["used_rows"]
    assert set(d.high_leverage_rows) == {r for r, h in zip(rows, ref["leverage"]) if h > 2 * p / n}
    assert set(d.influential_rows) == {r for r, c in zip(rows, ref["cooks_distance"]) if c > 4 / n}
    assert set(d.outlier_rows) == {r for r, t in zip(rows, ref["studentized_residuals"]) if abs(t) > 3}
    cooks = dict(zip(rows, ref["cooks_distance"]))
    assert [cooks[r] for r in d.influential_rows] == sorted((cooks[r] for r in d.influential_rows),
                                                            reverse=True)


def test_airquality_missing_rows_are_listwise_deleted():
    ref = json.loads((REF / "airquality.json").read_text())
    plan, res = _fit((REF / "airquality.csv").read_bytes(), target="Ozone",
                     predictors=("Solar.R", "Wind", "Temp"), confidence_level=0.9)
    assert plan.rows_total == 153 and plan.rows_used == 111 and plan.rows_dropped == 42
    assert {m.column: m.missing for m in plan.missing_by_column} == {
        "Ozone": 37, "Solar.R": 7, "Wind": 0, "Temp": 0}
    codes = {w.code for w in plan.warnings}
    assert {"rows_dropped", "high_dropped_fraction"} <= codes
    assert list(res.measured.rows.rows) == ref["used_rows"]
    miss = {a.name: a for a in res.assumptions}["missing_data_ignorable"]
    assert miss.check == "not_checkable" and "42 rows dropped" in miss.evidence


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

GOOD = _arrays_csv(y=[1, 3, 2, 5, 4, 6, 8, 7], x1=[1, 2, 3, 4, 5, 6, 7, 8],
                   x2=[2, 1, 4, 3, 6, 5, 8, 9])


def test_spec_structure_is_validated():
    with pytest.raises(ValidationError):
        RegressSpec(target="y", predictors=())
    with pytest.raises(ValidationError):
        RegressSpec(target="y", predictors=("x",), confidence_level=1.0)
    with pytest.raises(ValidationError):
        RegressSpec(target="y", predictors=("x",), extra=1)


def test_unknown_column():
    e = _err(GOOD, "unknown_column", target="y", predictors=("x1", "X2"))
    assert e.detail["columns"] == ["X2"]


def test_target_in_predictors_and_duplicates():
    _err(GOOD, "target_in_predictors", target="y", predictors=("x1", "y"))
    _err(GOOD, "duplicate_predictor", target="y", predictors=("x1", "x1"))


def test_too_many_predictors():
    _err(GOOD, "too_many_predictors", ServiceConfig(max_regress_predictors=1),
         target="y", predictors=("x1", "x2"))
    assert ServiceConfig().max_regress_predictors == 20


def test_non_numeric_and_empty_columns():
    data = _csv([[1, "a", ""], [2, "3", ""], [3, "4", ""], [4, "5", ""]], ["y", "mixed", "empty"])
    e = _err(data, "non_numeric_column", target="y", predictors=("mixed",))
    assert e.detail == {"column": "mixed", "non_numeric_count": 1, "examples": ["a"]}
    _err(data, "all_missing", target="y", predictors=("empty",))


def test_insufficient_observations():
    data = _arrays_csv(y=[1, 2, None, 4], x=[1, None, 3, 5])
    e = _err(data, "insufficient_observations", target="y", predictors=("x",))
    assert e.detail == {"complete_rows": 2, "parameters": 2}
    _err(_arrays_csv(y=[None, None, 1], x=[1, 2, None]), "insufficient_observations",
         target="y", predictors=("x",))


def test_constant_target_and_predictor():
    _err(_arrays_csv(y=[2, 2, 2, 2], x=[1, 2, 3, 4]), "constant_target", target="y", predictors=("x",))
    e = _err(_arrays_csv(y=[1, 2, 3, 5], x=[1, 2, 3, 4], c=[7, 7, 7, 7]), "constant_predictor",
             target="y", predictors=("x", "c"))
    assert e.detail["column"] == "c"
    # without an intercept a constant column is allowed (it plays the intercept's role)
    plan, res = _fit(_arrays_csv(y=[1, 2, 3, 5], x=[1, 2, 3, 4], c=[1, 1, 1, 1]),
                     target="y", predictors=("c", "x"), intercept=False)
    assert res.measured.coefficients[0].estimate == pytest.approx(-0.5)
    _err(_arrays_csv(y=[1, 2, 3, 5], x=[0, 0, 0, 0]), "constant_predictor",
         target="y", predictors=("x",), intercept=False)
    _err(_arrays_csv(y=[0, 0, 0, 0], x=[1, 2, 3, 4]), "constant_target",
         target="y", predictors=("x",), intercept=False)


def test_constant_only_after_listwise_deletion():
    e = _err(_arrays_csv(y=[1, 2, 4, 3, None], x=[1, 2, 3, 4, 5], c=[4, 4, 4, 4, 9]),
             "constant_predictor", target="y", predictors=("x", "c"))
    assert e.detail["column"] == "c"


def test_perfect_collinearity_names_the_columns():
    x1 = [1, 2, 3, 4, 5, 6, 7]
    x2 = [3, 1, 4, 1, 5, 9, 2]
    e = _err(_arrays_csv(y=[2, 4, 1, 5, 7, 3, 6], a=x1, b=x2, z=[1, 1, 2, 3, 5, 8, 13],
                         s=[a + 2 * b for a, b in zip(x1, x2)]),
             "perfect_collinearity", target="y", predictors=("a", "b", "z", "s"))
    assert set(e.detail["columns"]) == {"a", "b", "s"}
    # a column that is an affine function of another is collinear with the intercept
    _err(_arrays_csv(y=[1, 3, 2, 5], a=[1, 2, 3, 4], b=[10, 20, 30, 40]),
         "perfect_collinearity", target="y", predictors=("a", "b"))
    _err(_arrays_csv(y=[1, 3, 2, 5], a=[1, 2, 3, 4], b=[2, 4, 6, 8]),
         "perfect_collinearity", target="y", predictors=("a", "b"), intercept=False)


def test_numerically_exact_collinearity_is_refused():
    rng = np.random.default_rng(0)
    a = rng.normal(size=50)
    b = rng.normal(size=50)
    c = a - b + rng.normal(scale=1e-13, size=50)  # differs from a - b only by rounding
    _err(_arrays_csv(y=rng.normal(size=50), a=a, b=b, c=c), "perfect_collinearity",
         target="y", predictors=("a", "b", "c"))


# ---------------------------------------------------------------------------
# human approval and reproducibility
# ---------------------------------------------------------------------------

MTCARS = (REF / "mtcars.csv").read_bytes()
MT_SPEC = RegressSpec(target="mpg", predictors=("wt", "hp"),
                      question="How is fuel economy associated with weight and power?")


def test_prepare_does_not_fit_and_plan_describes_the_run():
    plan = regress.prepare(parse_csv(MTCARS), MT_SPEC)
    assert plan.formula == "mpg ~ 1 + wt + hp"
    assert plan.rows_used == 32 and plan.parameters == 3 and plan.df_resid == 29
    assert "b1·wt" in plan.summary and "associations" in plan.summary
    assert re.fullmatch(r"[0-9a-f]{64}", plan.plan_sha256)
    assert regress.plan_hash(plan) == plan.plan_sha256
    assert not hasattr(plan, "measured")


def test_plan_hash_depends_on_everything_that_matters():
    ds = parse_csv(MTCARS)
    h = regress.prepare(ds, MT_SPEC).plan_sha256
    assert regress.prepare(ds, MT_SPEC).plan_sha256 == h
    for change in ({"question": "Other question"}, {"confidence_level": 0.9},
                   {"intercept": False}, {"predictors": ("hp", "wt")},
                   {"row_order_meaningful": True}):
        assert regress.prepare(ds, MT_SPEC.model_copy(update=change)).plan_sha256 != h
    other = MTCARS.replace(b"21,2.62,110", b"21.5,2.62,110", 1)
    assert other != MTCARS
    assert regress.prepare(parse_csv(other), MT_SPEC).plan_sha256 != h


def test_run_requires_approval_of_this_plan():
    ds = parse_csv(MTCARS)
    plan = regress.prepare(ds, MT_SPEC)
    other = regress.prepare(ds, MT_SPEC.model_copy(update={"confidence_level": 0.9}))
    with pytest.raises(AnalysisInputError) as e:
        regress.run(ds, plan, _approve(other))
    assert e.value.code == "approval_mismatch"


def test_run_refuses_a_modified_plan():
    ds = parse_csv(MTCARS)
    plan = regress.prepare(ds, MT_SPEC)
    tampered = plan.model_copy(update={"spec": MT_SPEC.model_copy(update={"predictors": ("wt",)})})
    with pytest.raises(AnalysisInputError) as e:
        regress.run(ds, tampered, _approve(tampered))
    assert e.value.code == "plan_modified"


def test_run_refuses_different_data():
    plan = regress.prepare(parse_csv(MTCARS), MT_SPEC)
    other = parse_csv(MTCARS.replace(b"21,2.62,110", b"21.5,2.62,110", 1))
    with pytest.raises(AnalysisInputError) as e:
        regress.run(other, plan, _approve(plan))
    assert e.value.code == "plan_mismatch"
    assert e.value.detail["plan_dataset_sha256"] != e.value.detail["dataset_sha256"]


def test_approval_needs_a_named_approver():
    plan = regress.prepare(parse_csv(MTCARS), MT_SPEC)
    for who in ("", "   "):
        with pytest.raises(ValidationError):
            Approval(plan_sha256=plan.plan_sha256, approved_by=who)
    with pytest.raises(ValidationError):
        Approval(plan_sha256="not-a-hash", approved_by="me")


def test_run_record_is_complete():
    ds = parse_csv(MTCARS)
    plan = regress.prepare(ds, MT_SPEC)
    res = regress.run(ds, plan, Approval(plan_sha256=plan.plan_sha256, approved_by=" Dr A ",
                                         note="as discussed"))
    r = res.run
    assert (r.dataset_sha256, r.plan_sha256, r.spec) == (ds.sha256, plan.plan_sha256, MT_SPEC)
    assert (r.approved_by, r.approval_note, r.analysis) == ("Dr A", "as discussed", "regress@1")
    assert r.numpy_version == np.__version__ and r.python_version and "svd" in r.solver
    assert r.spec.question == MT_SPEC.question


def test_deterministic_output():
    ds = parse_csv(MTCARS)
    plan = regress.prepare(ds, MT_SPEC)
    a = regress.run(ds, plan, _approve(plan)).model_dump_json()
    b = regress.run(parse_csv(MTCARS), plan, _approve(plan)).model_dump_json()
    assert a == b


def test_row_order_does_not_change_estimates():
    lines = MTCARS.decode().splitlines()
    shuffled = "\n".join([lines[0]] + lines[:0:-1]).encode()
    _, a = _fit(MTCARS, target="mpg", predictors=("wt", "hp"))
    _, b = _fit(shuffled, target="mpg", predictors=("wt", "hp"))
    for ca, cb in zip(a.measured.coefficients, b.measured.coefficients):
        assert ca.estimate == pytest.approx(cb.estimate, rel=1e-12)
        assert ca.std_error == pytest.approx(cb.std_error, rel=1e-12)


# ---------------------------------------------------------------------------
# measured / assumptions / interpretation
# ---------------------------------------------------------------------------

CAUSAL = re.compile(r"\b(caus\w*|effects?|impacts?|drives?|driv\w+|leads? to|because|proves?|"
                    r"significan\w*|determin\w*|results? in|influenc\w*)\b", re.I)


@pytest.mark.parametrize("name", CASES)
def test_no_causal_or_significance_language(name):
    ref = json.loads((REF / f"{name}.json").read_text())
    _, res = _fit((REF / f"{name}.csv").read_bytes(), target=ref["target"],
                  predictors=tuple(ref["predictors"]), intercept=ref["intercept"])
    texts = [*res.interpretation.statements, *res.interpretation.next_steps,
             res.interpretation.basis, *(w.message for w in res.warnings),
             *(a.statement for a in res.assumptions), *(a.evidence for a in res.assumptions)]
    bad = [t for t in texts if CAUSAL.search(t)]
    assert not bad, bad
    # the limitations name the one thing regression cannot establish
    assert any("does not establish cause and effect" in t for t in res.limitations)
    assert any("changing a predictor" in s for s in res.interpretation.next_steps)


def test_interpretation_reports_association_with_interval():
    _, res = _fit(MTCARS, target="mpg", predictors=("wt", "hp"))
    wt = next(s for s in res.interpretation.statements if s.startswith("wt:"))
    assert "lower by 3.878 on average" in wt and "95% CI -5.172 to -2.584" in wt
    assert "association; it does not show that changing wt would change mpg" in wt
    assert "held fixed in the model" in wt


def test_interpretation_when_interval_includes_zero():
    rng = np.random.default_rng(3)
    x = rng.normal(size=30)
    _, res = _fit(_arrays_csv(y=rng.normal(size=30), x=x), target="y", predictors=("x",))
    c = res.measured.coefficients[1]
    assert c.ci_low < 0 < c.ci_high
    st = res.interpretation.statements[1]
    assert "compatible with no linear association" in st and "does not show that there is no" in st


def test_assumptions_are_stated_with_their_check_status():
    _, res = _fit(MTCARS, target="mpg", predictors=("wt", "hp"))
    a = {x.name: x for x in res.assumptions}
    assert len(a) == 8
    assert a["linearity"].check == "contradicted"            # RESET p = 7e-4 in R
    assert a["constant_variance"].check == "not_contradicted"
    assert "does not show the assumption holds" in a["constant_variance"].evidence
    assert a["independence"].check == "not_checkable"
    for name in ("predictors_without_error", "relevant_variables_included"):
        assert a[name].check == "not_checkable"
    assert a["missing_data_ignorable"].check == "not_contradicted"


def test_perfect_fit_reports_unavailable_uncertainty():
    x = [1, 2, 3, 4, 5, 6]
    plan, res = _fit(_arrays_csv(y=[3 + 2 * v for v in x], x=x), target="y", predictors=("x",))
    m = res.measured
    assert [c.estimate for c in m.coefficients] == pytest.approx([3, 2], abs=1e-12)
    assert all(c.std_error is None and c.p is None and c.ci_low is None for c in m.coefficients)
    assert m.fit.f_statistic is None and m.covariance is None
    assert m.fit.r_squared == pytest.approx(1.0)
    assert "perfect_fit" in {w.code for w in res.warnings}
    assert {"std_error", "confidence_interval", "f_statistic"} <= set(res.unavailable)
    assert {a.name: a.check for a in res.assumptions}["linearity"] == "unavailable"
    json.loads(res.model_dump_json())  # no inf / nan anywhere


def test_minimal_residual_df():
    _, res = _fit(_arrays_csv(y=[1, 3, 2], x=[1, 2, 3]), target="y", predictors=("x",))
    assert res.measured.fit.df_resid == 1
    assert "studentized_residuals" in res.unavailable and "reset" in res.unavailable
    assert all(v is None for v in res.measured.rows.studentized_residual)
    assert "small_residual_df" in {w.code for w in res.warnings}
    json.loads(res.model_dump_json())


def test_leverage_one_rows_have_undefined_influence():
    # the last row is the only one with b = 1, so it is fitted exactly (leverage 1)
    data = _arrays_csv(y=[1, 2, 2, 4, 9], a=[1, 2, 3, 4, 5], b=[0, 0, 0, 0, 1])
    _, res = _fit(data, target="y", predictors=("a", "b"))
    r = res.measured.rows
    assert r.leverage[-1] == pytest.approx(1.0)
    assert r.cooks_distance[-1] is None and r.studentized_residual[-1] is None
    assert r.cooks_distance[0] is not None


# ---------------------------------------------------------------------------
# uncertainty and diagnostics behave as designed
# ---------------------------------------------------------------------------

def test_confidence_interval_coverage_by_simulation():
    """95% intervals should contain the true slope in about 95% of datasets."""
    rng = np.random.default_rng(20261010)
    hits, reps = 0, 300
    x1 = rng.uniform(0, 10, size=25)
    x2 = rng.normal(size=25)
    for _ in range(reps):
        y = 1.0 + 0.5 * x1 - 2.0 * x2 + rng.normal(scale=3.0, size=25)
        _, res = _fit(_arrays_csv(y=y, x1=x1, x2=x2), target="y", predictors=("x1", "x2"))
        c = res.measured.coefficients[1]
        hits += c.ci_low <= 0.5 <= c.ci_high
    # binomial(300, 0.95): 99.9% of outcomes lie in [272, 294]
    assert 272 <= hits <= 294, hits


def test_heteroscedasticity_and_nonlinearity_are_flagged():
    rng = np.random.default_rng(5)
    x = rng.uniform(1, 10, size=200)
    _, het = _fit(_arrays_csv(y=2 * x + rng.normal(size=200) * x, x=x), target="y",
                  predictors=("x",))
    assert "heteroscedasticity" in {w.code for w in het.warnings}
    assert {a.name: a.check for a in het.assumptions}["constant_variance"] == "contradicted"
    _, curved = _fit(_arrays_csv(y=x ** 2 + rng.normal(size=200), x=x), target="y",
                     predictors=("x",))
    assert "nonlinearity" in {w.code for w in curved.warnings}
    assert any("curved term" in s for s in curved.interpretation.next_steps)


def test_autocorrelation_only_checked_when_row_order_is_meaningful():
    rng = np.random.default_rng(7)
    e = np.cumsum(rng.normal(size=100)) * 0.5   # random walk errors
    x = np.arange(100.0)
    data = _arrays_csv(y=x + e, x=x)
    _, unordered = _fit(data, target="y", predictors=("x",))
    assert "autocorrelation" not in {w.code for w in unordered.warnings}
    assert {a.name: a.check for a in unordered.assumptions}["independence"] == "not_checkable"
    _, ordered = _fit(data, target="y", predictors=("x",), row_order_meaningful=True)
    assert "autocorrelation" in {w.code for w in ordered.warnings}
    assert {a.name: a.check for a in ordered.assumptions}["independence"] == "contradicted"


def test_collinearity_and_binary_target_warnings():
    rng = np.random.default_rng(11)
    a = rng.normal(size=60)
    b = a + rng.normal(scale=0.05, size=60)
    y = (a + rng.normal(size=60) > 0).astype(float)
    plan, res = _fit(_arrays_csv(y=y, a=a, b=b), target="y", predictors=("a", "b"))
    codes = {w.code: w for w in res.warnings}
    assert set(codes["high_collinearity"].columns) == {"a", "b"}
    assert "binary_target" in {w.code for w in plan.warnings}


def test_scale_invariance_across_extreme_magnitudes():
    rng = np.random.default_rng(13)
    x = rng.uniform(1, 2, size=40)
    y = 3 * x + rng.normal(size=40)
    _, base = _fit(_arrays_csv(y=y, x=x), target="y", predictors=("x",))
    for sx, sy in ((1e150, 1.0), (1e-150, 1e150), (1.0, 1e-200), (2.0 ** 60, 2.0 ** -60)):
        _, res = _fit(_arrays_csv(y=y * sy, x=x * sx), target="y", predictors=("x",))
        b0, b = base.measured.coefficients[1], res.measured.coefficients[1]
        assert b.estimate == pytest.approx(b0.estimate * sy / sx, rel=1e-12)
        assert b.t == pytest.approx(b0.t, rel=1e-10)
        assert res.measured.fit.r_squared == pytest.approx(base.measured.fit.r_squared, rel=1e-12)
        # a slope's variance can leave the float range while its standard error does not
        assert (res.measured.covariance is None) == ("covariance" in res.unavailable)
        json.loads(res.model_dump_json())
    _, extreme = _fit(_arrays_csv(y=y * 1e150, x=x * 1e-150), target="y", predictors=("x",))
    assert extreme.measured.covariance is None and extreme.measured.coefficients[1].std_error > 1e290


def test_precision_loss_warning_for_huge_integers():
    data = _csv([[1, 2 ** 53 + 1], [3, 2 ** 53 + 5], [2, 2 ** 53 + 9], [5, 2 ** 53 + 20]], ["y", "x"])
    plan = regress.prepare(parse_csv(data), RegressSpec(target="y", predictors=("x",)))
    assert {w.code: w.columns for w in plan.warnings}["precision_loss"] == ("x",)


def test_large_offsets_do_not_lose_precision():
    # x near 1e9 with unit spacing: naive normal equations lose most digits here
    x = 1e9 + np.arange(20.0)
    y = 5.0 + 0.25 * np.arange(20.0) + np.sin(np.arange(20.0))
    _, res = _fit(_arrays_csv(y=y, x=x), target="y", predictors=("x",))
    xc = np.arange(20.0)
    slope = np.cov(xc, y, bias=True)[0, 1] / xc.var()
    assert res.measured.coefficients[1].estimate == pytest.approx(slope, rel=1e-9)


# ---------------------------------------------------------------------------
# execution: separate process, time limit, scale
# ---------------------------------------------------------------------------

def test_execution_round_trip_matches_in_process():
    plan = prepare_regress(MTCARS, MT_SPEC)
    assert plan == regress.prepare(parse_csv(MTCARS), MT_SPEC)
    res = run_regress(MTCARS, plan, _approve(plan))
    ds = parse_csv(MTCARS)
    assert res == regress.run(ds, plan, _approve(plan))


def test_execution_errors_are_forwarded():
    with pytest.raises(AnalysisInputError) as e:
        prepare_regress(MTCARS, RegressSpec(target="mpg", predictors=("weight",)))
    assert e.value.code == "unknown_column" and e.value.detail["columns"] == ["weight"]


def test_execution_checks_approval_before_starting_a_process(monkeypatch):
    import reflica_service.execution as ex
    plan = regress.prepare(parse_csv(MTCARS), MT_SPEC)
    monkeypatch.setattr(ex, "run_with_timeout", lambda *a, **k: pytest.fail("process started"))
    bad = Approval(plan_sha256="0" * 64, approved_by="me")
    with pytest.raises(AnalysisInputError) as e:
        run_regress(MTCARS, plan, bad)
    assert e.value.code == "approval_mismatch"


def test_execution_time_limit():
    plan = regress.prepare(parse_csv(MTCARS), MT_SPEC)
    with pytest.raises(AnalysisTimeout):
        run_regress(MTCARS, plan, _approve(plan), ServiceConfig(analysis_timeout_s=0.001))


def test_scale_100k_rows_20_predictors():
    rng = np.random.default_rng(17)
    n, k = 100_000, 20
    X = rng.integers(0, 100, size=(n, k))
    y = X @ rng.integers(-3, 4, size=k) + rng.integers(0, 50, size=n)
    buf = io.StringIO()
    buf.write(",".join(["y"] + [f"x{j}" for j in range(k)]) + "\n")
    for i in range(n):
        buf.write(f"{y[i]}," + ",".join(map(str, X[i])) + "\n")
    data = buf.getvalue().encode()
    assert len(data) <= ServiceConfig().max_upload_bytes
    spec = RegressSpec(target="y", predictors=tuple(f"x{j}" for j in range(k)))
    t0 = time.monotonic()
    plan = prepare_regress(data, spec)
    res = run_regress(data, plan, _approve(plan))
    elapsed = time.monotonic() - t0
    assert res.measured.fit.n == n and len(res.measured.rows.fitted) == n
    assert elapsed < 2 * ServiceConfig().analysis_timeout_s
