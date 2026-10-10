"""describe@1: statistics, issues, correlations and determinism."""
from __future__ import annotations

import math
import statistics

import pytest

import reflica_service

from reflica_service.analyses.describe import describe
from reflica_service.csv_adapter import parse_csv


def run(data: bytes):
    return describe(parse_csv(data))


def codes(result, column=None):
    return {i.code for i in result.issues if i.column == column}


def test_numeric_stats_match_reference():
    xs = [3.0, 1.5, 4.0, 1.0, 5.5]
    r = run(("x\n" + "\n".join(map(str, xs)) + "\n").encode())
    s = r.columns[0].numeric
    assert s.min == 1.0 and s.max == 5.5
    assert s.mean == pytest.approx(statistics.fmean(xs))
    assert s.median == statistics.median(xs)
    assert s.sd == pytest.approx(statistics.stdev(xs))


def test_single_value_has_no_sd():
    assert run(b"x\n7\n").columns[0].numeric.sd is None


def test_missing_counts_and_fraction():
    r = run(b"a,b\n1,x\n,y\n3,\nNA,z\n5,w\n")
    a = r.columns[0]
    assert (a.count, a.missing, a.missing_fraction) == (3, 2, 0.4)
    assert a.numeric.mean == 3.0
    assert "high_missing" in codes(r, "a")
    assert "high_missing" not in codes(r, "b")  # 1/5 = 20% is not above the threshold


def test_constant_and_all_missing_columns():
    r = run(b"c,e,v\n1,,1\n1,NA,2\n1,,3\n")
    assert "constant_column" in codes(r, "c")
    assert codes(r, "e") == {"all_missing"}
    assert codes(r, "v") == {"small_sample"}


def test_possible_id_column():
    rows = "\n".join(f"{i},S{i},{i * 1.5},{i % 2}" for i in range(1, 7))
    r = run(f"id,code,measure,group\n{rows}\n".encode())
    assert "possible_id_column" in codes(r, "id")
    assert "possible_id_column" in codes(r, "code")
    assert "possible_id_column" not in codes(r, "measure")  # non-integer numeric
    assert "possible_id_column" not in codes(r, "group")


def test_id_heuristic_needs_enough_rows():
    assert "possible_id_column" not in codes(run(b"id\n1\n2\n3\n"), "id")


def test_mixed_column_issue():
    r = run(b"m\n1\n2\nx\n4\n")
    assert r.columns[0].type == "mixed" and r.columns[0].numeric is None
    assert "non_numeric_in_numeric" in codes(r, "m")
    assert "1 value(s)" in next(i.message for i in r.issues if i.column == "m")


def test_duplicate_rows_issue():
    r = run(b"a,b\n1,2\n1,2\n3,4\n")
    assert "duplicate_rows" in codes(r, None)


def test_pearson_matches_reference_and_is_association():
    xs, ys = [1, 2, 3, 4, 5], [2.1, 3.9, 6.2, 8.1, 9.8]
    r = run(("x,y\n" + "\n".join(f"{x},{y}" for x, y in zip(xs, ys)) + "\n").encode())
    (c,) = r.correlations
    assert (c.x, c.y, c.n, c.relationship) == ("x", "y", 5, "association")
    assert c.r == pytest.approx(statistics.correlation(xs, ys))


def test_perfect_negative_correlation():
    (c,) = run(b"x,y\n1,10\n2,8\n3,6\n").correlations
    assert c.r == pytest.approx(-1.0)


def test_correlation_pairwise_deletion_and_none_cases():
    r = run(b"x,y,k\n1,2,5\n2,,5\n3,6,5\n4,8,5\n")
    by = {(c.x, c.y): c for c in r.correlations}
    assert by[("x", "y")].n == 3 and by[("x", "y")].r == pytest.approx(1.0)
    assert by[("x", "k")].r is None and "constant" in by[("x", "k")].reason
    few = run(b"x,y\n1,2\n2,\n3,\n").correlations[0]
    assert few.r is None and few.n == 1


def test_only_numeric_columns_are_correlated():
    r = run(b"a,t,b,m\n1,x,2,1\n2,y,3,q\n3,z,5,3\n")
    assert [(c.x, c.y) for c in r.correlations] == [("a", "b")]


def test_notes_state_association_not_causation():
    assert any("associations only" in n and "cause" in n for n in run(b"x\n1\n").notes)


def test_no_causal_wording_in_output():
    text = run(b"x,y\n1,2\n2,4\n3,7\n").model_dump_json().lower()
    for word in ("causes", "caused by", "effect of", "leads to"):
        assert word not in text


def test_deterministic_output():
    data = b"a,b,c\n1,2.5,x\n2,,y\n3,7.25,x\n4,9,z\n"
    assert run(data).model_dump_json() == run(data).model_dump_json()


def test_result_metadata():
    data = b"a,b\n1,2\n3,4\n"
    r = run(data)
    assert (r.operation, r.version, r.row_count, r.column_count) == ("describe", "1", 2, 2)
    assert r.dataset_sha256 == parse_csv(data).sha256
    assert r.service_version == reflica_service.__version__
    for c in r.columns:
        stats = c.numeric.model_dump()
        assert all(math.isfinite(v) for k, v in stats.items() if k != "unavailable" and v is not None)
