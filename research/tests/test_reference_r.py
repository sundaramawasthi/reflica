"""Our interval and test implementations against an independent reference:
R 4.3.3, contingencytables 3.1.0 (Fagerland, Lydersen & Laake) and base R
binom.test / prop.test / qt. The reference values were produced by
experiments/full_run/reference/refgrid.R (958 tables: every table with
N = 1, 2, 3, 5, 12; 400 random N = 63 tables; 13 edge cases) and are stored
as CSV, so this test needs no R."""
from __future__ import annotations

import csv

import pytest

from reflica_bench import protocol_lock as pl
from reflica_bench import stats as S

REF = pl.FULL_RUN / "reference"
METHODS = {"nc": (S.newcombe_paired_ci, 1e-12), "ta": (S.tango_paired_ci, 1e-6),
           "am": (S.agresti_min_ci, 1e-12), "bp": (S.bonett_price_ci, 1e-12)}


def _rows():
    return list(csv.DictReader((REF / "refgrid.csv").open()))


def test_reference_grid_is_complete():
    assert len(_rows()) == 958


@pytest.mark.parametrize("key", sorted(METHODS))
def test_paired_difference_intervals_match_r(key):
    f, tol = METHODS[key]
    for r in _rows():
        t = S.PairedBinary(*(int(float(r[x])) for x in "abcd"))
        lo, hi = f(t)
        assert lo == pytest.approx(float(r[f"{key}_lo"]), abs=tol), (key, t)
        assert hi == pytest.approx(float(r[f"{key}_hi"]), abs=tol), (key, t)


def test_mcnemar_exact_and_midp_match_r():
    for r in _rows():
        t = S.PairedBinary(*(int(float(r[x])) for x in "abcd"))
        assert S.mcnemar_exact(t).p_two_sided == pytest.approx(float(r["p_exact"]), abs=1e-12)
        assert S.mcnemar_midp(t) == pytest.approx(float(r["p_midp"]), abs=1e-12)


def test_clopper_pearson_and_wilson_match_r():
    for r in csv.DictReader((REF / "refcp.csv").open()):
        k = int(float(r["k"]))
        assert S.clopper_pearson(k, 63) == pytest.approx((float(r["cp_lo"]), float(r["cp_hi"])), abs=1e-12)
        assert S.wilson(k, 63) == pytest.approx((float(r["w_lo"]), float(r["w_hi"])), abs=1e-12)


def test_student_t_quantile_matches_r_qt():
    """refqt.csv: R 4.3.3 qt(0.975, df) for df = 1..100 (used by the descriptive t-intervals)."""
    for r in csv.DictReader((REF / "refqt.csv").open()):
        assert S.t_ppf(0.975, int(r["df"])) == pytest.approx(float(r["q975"]), abs=1e-10)
