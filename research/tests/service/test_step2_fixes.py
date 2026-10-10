"""Regression tests for the Step 2 review findings (problems 1–8 and small samples).

Each test reproduces an input that previously crashed, gave a wrong answer
or could tie up the service.
"""
from __future__ import annotations

import math
import statistics
import time

import pytest

from reflica_service.analyses.describe import (OUT_OF_RANGE, UNREFINED, _correlation_columns,
                                               describe)
from reflica_service.csv_adapter import CSVValidationError, parse_csv
from reflica_service.execution import (AnalysisFailed, AnalysisTimeout, run_describe,
                                       run_with_timeout)
from reflica_service.models import ServiceConfig
from tests.service import _slow


def run(data: bytes, config: ServiceConfig | None = None):
    return describe(parse_csv(data, config), config)


def codes(result, column=None):
    return {i.code for i in result.issues if i.column == column}


# --- Problem 1: numerical overflow -----------------------------------------

def test_huge_equal_values_no_longer_crash():
    s = run(b"x,y\n1e308,1\n1e308,2\n1e308,3\n").columns[0].numeric
    assert (s.mean, s.median, s.min, s.max, s.sd) == (1e308, 1e308, 1e308, 1e308, 0.0)
    assert s.unavailable == {}


def test_huge_spread_values_no_longer_crash():
    xs = [1e200, -1e200, 3e200]
    s = run(("x\n" + "\n".join(map(str, xs)) + "\n").encode()).columns[0].numeric
    assert s.mean == pytest.approx(1e200)
    assert s.sd == pytest.approx(2e200)  # sample SD of (1, -1, 3) × 1e200
    assert math.isfinite(s.median)


def test_sd_beyond_float_range_is_unavailable_not_inf():
    s = run(b"x\n1.7e308\n-1.7e308\n").columns[0].numeric
    assert s.sd is None and s.unavailable == {"sd": OUT_OF_RANGE}
    assert s.mean == 0.0 and math.isfinite(s.median)


def test_median_of_two_huge_values_does_not_overflow():
    assert run(b"x\n1.6e308\n1.7e308\n").columns[0].numeric.median == pytest.approx(1.65e308)


def test_single_value_sd_reason():
    assert run(b"x\n7\n").columns[0].numeric.unavailable == {"sd": "needs at least 2 values"}


def test_tiny_values_keep_precision():
    xs = [1e-300, 2e-300, 3e-300]
    s = run(("x\n" + "\n".join(map(str, xs)) + "\n").encode()).columns[0].numeric
    assert s.mean == pytest.approx(2e-300) and s.sd == pytest.approx(1e-300)


def test_huge_values_correlate():
    (c,) = run(b"x,y\n1e308,1\n-1e308,2\n1.5e308,3\n").correlations
    assert c.r == pytest.approx(statistics.correlation([1, -1, 1.5], [1, 2, 3]))


def test_stats_still_match_reference_on_ordinary_data():
    xs = [3.0, 1.5, 4.0, 1.0, 5.5, 2.25]
    s = run(("x\n" + "\n".join(map(str, xs)) + "\n").encode()).columns[0].numeric
    assert s.mean == pytest.approx(statistics.fmean(xs), rel=1e-15)
    assert s.sd == pytest.approx(statistics.stdev(xs), rel=1e-15)
    assert s.median == statistics.median(xs)


# --- Problem 2: integer precision ------------------------------------------

BIG = b"id\n" + b"".join(b"1234567890123456789%d\n" % i for i in range(5))


def test_big_integers_counted_exactly():
    r = run(BIG)
    assert r.columns[0].unique == 5
    assert "constant_column" not in codes(r, "id")
    assert "possible_id_column" in codes(r, "id")


def test_big_integers_flag_precision_loss():
    assert "precision_loss" in codes(run(BIG), "id")


def test_precision_boundary():
    assert "precision_loss" not in codes(run(b"n\n9007199254740992\n1\n"), "n")  # exactly 2**53
    assert "precision_loss" in codes(run(b"n\n9007199254740993\n1\n"), "n")


# --- Problem 3: rows of empty cells ----------------------------------------

def test_row_of_empty_cells_counts_as_data():
    ds = parse_csv(b"a,b\n1,2\n,\n3,4\n")
    assert ds.row_count == 3
    assert ds.columns[0].values == ("1", None, "3")
    s = describe(ds).columns[0]
    assert (s.count, s.missing) == (2, 1)


def test_missing_token_rows_count_as_data():
    assert parse_csv(b"a,b\nNA,NA\n1,2\n").row_count == 2


def test_truly_blank_lines_still_skipped():
    assert parse_csv(b"a,b\n\n1,2\n   \n\n3,4\n\n").row_count == 2


def test_single_column_blank_rules():
    ds = parse_csv(b'a\n1\n\n""\n2\n')  # empty line skipped; "" is a missing value
    assert ds.row_count == 3 and ds.columns[0].values == ("1", None, "2")


# --- Problem 4: bounded correlation work and enforced timeout ---------------

def wide_csv(cols: int, rows: int) -> bytes:
    header = ",".join(f"c{i}" for i in range(cols))
    body = "\n".join(",".join(str((r * 7 + c * 13) % 97 + c) for c in range(cols)) for r in range(rows))
    return f"{header}\n{body}\n".encode()


def test_correlation_columns_capped_and_skips_reported():
    cfg = ServiceConfig(max_correlation_columns=3)
    r = run(wide_csv(5, 12), cfg)
    assert len(r.correlations) == 3  # pairs among c0..c2
    skip = r.correlations_skipped
    assert skip.computed_columns == ("c0", "c1", "c2")
    assert skip.skipped_columns == ("c3", "c4")
    assert skip.skipped_pairs == 10 - 3


def test_no_skip_record_under_the_cap():
    assert run(wide_csv(4, 12)).correlations_skipped is None


def test_run_describe_matches_in_process_result():
    data = wide_csv(6, 40)
    assert run_describe(data).model_dump() == run(data).model_dump()


def test_run_describe_propagates_validation_errors():
    with pytest.raises(CSVValidationError) as e:
        run_describe(b"a,b\n1,2,3\n")
    assert e.value.code == "malformed_row" and e.value.detail["line"] == 2


def test_run_describe_rejects_oversized_before_spawning():
    with pytest.raises(CSVValidationError) as e:
        run_describe(b"a\n" + b"1\n" * 100, ServiceConfig(max_upload_bytes=50))
    assert e.value.code == "too_large"


def test_timeout_stops_sleeping_worker():
    t = time.monotonic()
    with pytest.raises(AnalysisTimeout) as e:
        run_with_timeout(_slow.sleep_forever, (), 1.0)
    assert time.monotonic() - t < 6
    assert e.value.code == "timeout"


def test_timeout_stops_busy_pure_python_worker():
    t = time.monotonic()
    with pytest.raises(AnalysisTimeout):
        run_with_timeout(_slow.busy_forever, (), 1.0)
    assert time.monotonic() - t < 6


def test_timeout_applies_to_real_describe():
    with pytest.raises(AnalysisTimeout):
        run_describe(wide_csv(50, 3000), ServiceConfig(analysis_timeout_s=0.01))


def test_worker_result_and_errors():
    assert run_with_timeout(_slow.add, (2, 3), 30) == 5
    with pytest.raises(AnalysisFailed, match="planted failure"):
        run_with_timeout(_slow.boom, (), 30)


# --- Problems 5–8 and small samples ----------------------------------------

def test_leading_zero_codes_are_text():
    r = run(b"zip,v\n007,1\n010,2\n123,3\n")
    assert r.columns[0].type == "text" and r.columns[0].numeric is None
    assert "leading_zeros" in codes(r, "zip")


def test_zero_and_decimals_are_not_leading_zero_codes():
    ds = parse_csv(b"v\n0\n0.5\n-0.25\n10\n")
    assert ds.columns[0].type == "numeric" and not ds.columns[0].leading_zeros


def test_numeric_header_accepted_and_flagged():
    r = run(b"2020,2021\n1,2\n3,4\n")
    assert [c.name for c in r.columns] == ["2020", "2021"]
    assert "numeric_header" in codes(r, None)
    assert "numeric_header" not in codes(run(b"year,2021\n1,2\n"), None)


def test_column_limit_checked_before_reading_rows():
    cfg = ServiceConfig(max_columns=2)
    with pytest.raises(CSVValidationError) as e:
        parse_csv(b"a,b,c\n1,2\n" + b"bad,\"row\n", cfg)  # would otherwise be a row/quote error
    assert e.value.code == "too_many_columns"


def test_small_sample_warning_vs_invalid_result():
    r = run(b"x,y\n1,2\n2,4\n3,7\n4,8\n")
    assert "small_sample" in codes(r, "x")
    (c,) = r.correlations
    assert c.r is not None and c.reason is None and c.warnings  # valid, with a warning
    few = run(b"x,y\n1,2\n2,4\n").correlations[0]
    assert few.r is None and few.reason and not few.warnings  # invalid, with a reason


def test_no_small_sample_warning_at_threshold():
    r = run(("x,y\n" + "\n".join(f"{i},{i * i}" for i in range(10)) + "\n").encode())
    assert "small_sample" not in codes(r, "x")
    assert r.correlations[0].warnings == ()


def test_deterministic_with_skips():
    cfg = ServiceConfig(max_correlation_columns=4)
    data = wide_csv(8, 30)
    assert run(data, cfg).model_dump_json() == run(data, cfg).model_dump_json()


# --- Masked pairwise-correlation path: accuracy against a reference ---------

@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("offset", [0.0, 1e6, -3e9])
def test_pairwise_correlation_matches_reference(seed, offset):
    import random
    rnd = random.Random(seed)
    xs = [offset + rnd.gauss(0, 1) for _ in range(60)]
    ys = [0.5 * (x - offset) + rnd.gauss(0, 1) + offset / 2 for x in xs]
    cells = [(None if rnd.random() < 0.15 else x, None if rnd.random() < 0.15 else y) for x, y in zip(xs, ys)]
    body = "\n".join(f"{'' if x is None else repr(x)},{'' if y is None else repr(y)}" for x, y in cells)
    (c,) = run(f"x,y\n{body}\n".encode()).correlations
    paired = [(x, y) for x, y in cells if x is not None and y is not None]
    assert c.n == len(paired)
    assert c.r == pytest.approx(statistics.correlation(*zip(*paired)), abs=1e-9)


def test_constant_on_paired_rows_detected_in_masked_path():
    # y varies overall, but is constant on the rows where x is present
    (c,) = run(b"x,y\n1,5\n2,5\n3,5\n,9\n,1\n").correlations
    assert c.r is None and "constant" in c.reason and c.n == 3


@pytest.mark.parametrize("offset", [0.0, 1e6, -3e9, 1e12])
def test_sd_with_large_offset_matches_reference(offset):
    import random
    rnd = random.Random(11)
    xs = [offset + rnd.gauss(0, 1) for _ in range(200)]
    s = run(("x\n" + "\n".join(map(repr, xs)) + "\n").encode()).columns[0].numeric
    assert s.sd == pytest.approx(statistics.stdev(xs), rel=1e-12)
    assert s.mean == pytest.approx(statistics.fmean(xs), rel=1e-15)


# --- Final-review findings ---------------------------------------------------

def _csv2(xs, ys) -> bytes:
    cell = lambda v: "" if v is None else repr(v)
    return ("x,y\n" + "\n".join(f"{cell(x)},{cell(y)}" for x, y in zip(xs, ys)) + "\n").encode()


def test_review_L_paired_rows_far_from_column_mean():
    # unpaired outliers pull the column mean far from the paired rows; the
    # one-pass formula previously lost ~5 digits silently (r off by 2e-5)
    import random
    rnd = random.Random(1)
    xs = [1e7 + rnd.gauss(0, 1) for _ in range(50)]
    ys = [x - 1e7 + rnd.gauss(0, 0.5) for x in xs]
    (c,) = run(_csv2(xs + [-1e12, 1e12], ys + [None, None])).correlations
    assert c.r == pytest.approx(statistics.correlation(xs, ys), abs=1e-12)


def test_review_O_tiny_paired_values_not_called_constant():
    xs = [1e-170 * i for i in range(1, 8)]
    ys = [2e-170 * i + 1e-171 * (i % 2) for i in range(1, 8)]
    (c,) = run(_csv2(xs + [1e170, None], ys + [None, 1e170])).correlations
    ref = statistics.correlation([x * 1e170 for x in xs], [y * 1e170 for y in ys])
    assert c.reason is None and c.r == pytest.approx(ref, abs=1e-12)


def test_review_R_duplicate_key_cannot_collide():
    assert parse_csv('a,b\n"p\x1fq",r\np,"q\x1fr"\n'.encode()).duplicate_rows == 0


def test_review_constant_huge_column_is_constant_in_correlation():
    r = run(b"x,y\n-1.7e308,1\n-1.7e308,5\n-1.7e308,2\n")
    assert r.correlations[0].r is None and "constant" in r.correlations[0].reason
    assert r.columns[0].numeric.sd == 0.0 and r.columns[0].numeric.mean == -1.7e308


def test_review_mean_of_identical_values_is_exact():
    for v in ("1e-300", "-1e300", "0.1", "5e-324"):
        s = run(f"x\n{v}\n{v}\n{v}\n".encode()).columns[0].numeric
        assert s.mean == s.min == s.max == float(v)


def test_review_subnormal_values_correlate_correctly():
    from fractions import Fraction
    xs, ys = [1.0000000000472005, 1.0000000010307661, 0.999999999616032], [5e-324, 0.0, 5e-324]
    (c,) = run(_csv2(xs, ys)).correlations
    fx, fy = [Fraction(v) for v in xs], [Fraction(v) for v in ys]
    mx, my = sum(fx) / 3, sum(fy) / 3
    sxy = sum((a - mx) * (b - my) for a, b in zip(fx, fy))
    r2 = sxy * sxy / (sum((a - mx) ** 2 for a in fx) * sum((b - my) ** 2 for b in fy))
    assert c.r == pytest.approx(math.copysign(math.sqrt(float(r2)), float(sxy)), abs=1e-12)


def test_review_sd_near_float_limit_is_computed_when_representable():
    s = run(b"x\n-1.7e308\n0\n1e308\n5e-324\n").columns[0].numeric
    assert s.sd is not None and math.isfinite(s.sd) and s.unavailable == {}


# --- Adversarial-timeout closure --------------------------------------------

def _outlier_grid(cols: int, rows: int) -> bytes:
    """Each column's huge outlier sits on a row where only that column is present."""
    import random
    rnd = random.Random(5)
    grid = [[str(rnd.randint(0, 9)) for _ in range(cols)] for _ in range(rows)]
    for i in range(cols):
        grid[i] = [""] * cols
        grid[i][i] = "1e12"
    return (",".join(f"c{i}" for i in range(cols)) + "\n" + "\n".join(",".join(r) for r in grid) + "\n").encode()


def _cluster_grid(cols: int, rows: int) -> bytes:
    """Shared minority 'high' rows plus column-specific bulk rows: every pair is
    ill-conditioned under any single per-column centre."""
    import random
    rnd = random.Random(6)
    h = rows // (cols + 2)
    grid = [[f"{1e12 + rnd.random():.4f}" for _ in range(cols)] for _ in range(h)]
    for i in range(cols):
        for _ in range((rows - h) // cols):
            r = [""] * cols
            r[i] = f"{rnd.random():.3f}"
            grid.append(r)
    return (",".join(f"c{i}" for i in range(cols)) + "\n" + "\n".join(",".join(r) for r in grid) + "\n").encode()


def test_outlier_pattern_needs_no_exact_recomputation():
    # median centring: with a zero refinement budget every r is still computed
    r = run(_outlier_grid(6, 300), ServiceConfig(correlation_refine_budget_rows=0))
    assert all(c.r is not None for c in r.correlations)
    assert "correlations_unrefined" not in codes(r, None)


def test_outlier_pattern_matches_reference():
    data = _outlier_grid(4, 200)
    ds = parse_csv(data)
    for c in describe(ds).correlations:
        xs = dict(zip([col.name for col in ds.columns], [col.numbers for col in ds.columns]))
        both = [(x, y) for x, y in zip(xs[c.x], xs[c.y]) if x is not None and y is not None]
        assert c.r == pytest.approx(statistics.correlation(*zip(*both)), abs=1e-12)


def test_cluster_pattern_is_refined_exactly():
    # exact rational reference: statistics.correlation itself is off by ~1e-7 here
    from tests.service.test_numerics_property import _exact_r
    ds = parse_csv(_cluster_grid(4, 600))
    cols = {col.name: col.numbers for col in ds.columns}
    for c in describe(ds).correlations:
        both = [(x, y) for x, y in zip(cols[c.x], cols[c.y]) if x is not None and y is not None]
        assert c.r == pytest.approx(_exact_r(*zip(*both)), abs=1e-15)


def test_refinement_budget_exhaustion_is_explicit():
    r = run(_cluster_grid(4, 600), ServiceConfig(correlation_refine_budget_rows=0))
    assert all(c.r is None and c.reason == UNREFINED for c in r.correlations)
    assert "correlations_unrefined" in codes(r, None)


def test_refinement_budget_is_spent_in_order():
    rows_per_pair = parse_csv(_cluster_grid(4, 600)).row_count // 6  # shared high rows
    r = run(_cluster_grid(4, 600), ServiceConfig(correlation_refine_budget_rows=rows_per_pair * 2 + 5))
    done = [c.r is not None for c in r.correlations]
    assert done == [True, True] + [False] * (len(done) - 2)


@pytest.mark.parametrize("numeric,rows,work,cap,expected", [
    (10, 100, 10**9, 50, (10, "column_limit")),   # nothing binds: all columns
    (80, 100, 10**9, 50, (50, "column_limit")),   # column cap binds
    (50, 100_000, 50_000_000, 50, (32, "work_limit")),  # 32*31/2*1e5 = 4.96e7
    (50, 26_579, 50_000_000, 50, (50, "column_limit")),  # both bind exactly at the cap
    (5, 10**7, 50_000_000, 50, (3, "work_limit")),
])
def test_correlation_column_selection(numeric, rows, work, cap, expected):
    cfg = ServiceConfig(max_correlation_work=work, max_correlation_columns=cap)
    assert _correlation_columns(numeric, rows, cfg) == expected


def test_work_limit_reported_in_output():
    r = run(wide_csv(6, 100), ServiceConfig(max_correlation_work=300))  # 3 cols: 3 pairs x 100
    skip = r.correlations_skipped
    assert (skip.reason, skip.limit, len(r.correlations)) == ("work_limit", 3, 3)
    assert skip.skipped_columns == ("c3", "c4", "c5") and skip.skipped_pairs == 15 - 3


def test_median_centring_survives_values_at_float_limit():
    # statistics.median overflowed here and the NaN was clamped to r = 1.0
    r = run(b"x,y\n1.7e308,1\n1.7e308,5\n-1.7e308,2\n1e308,9\n,4\n")
    assert all(c.r is None or -1 <= c.r <= 1 for c in r.correlations)
    xs, ys = [1.7e308, 1.7e308, -1.7e308, 1e308], [1, 5, 2, 9]
    ref = statistics.correlation([x / 1e308 for x in xs], ys)
    assert r.correlations[0].r == pytest.approx(ref, abs=1e-12)
