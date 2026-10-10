"""Randomised property tests for describe@1 against an exact reference.

The reference uses exact rational arithmetic (fractions.Fraction) on the same
float inputs, so it is independent of the implementation's floating-point
strategy. Inputs mix extreme magnitudes, large offsets, near-constant and
constant columns, outliers, missing values and big integers.
"""
from __future__ import annotations

import json
import math
import random
from fractions import Fraction

import pytest

from reflica_service.analyses.describe import describe
from reflica_service.csv_adapter import parse_csv

OFFSETS = [0.0, 1.0, 1e6, -3e9, 1e12, 1e100, -1e300, 1e-300]
SPREADS = [1.0, 1e-3, 1e-9, 1e3, 0.0]


def _column(rnd: random.Random, n: int) -> list[float | None]:
    kind = rnd.random()
    if kind < 0.1:  # extremes of the float range
        vals = [rnd.choice([1.7e308, -1.7e308, 1e308, 5e-324, -1e-300, 0.0]) for _ in range(n)]
    else:
        off, spread = rnd.choice(OFFSETS), rnd.choice(SPREADS)
        scale = abs(off) if off else 1.0
        vals = [off + rnd.gauss(0, 1) * spread * scale for _ in range(n)]
        if rnd.random() < 0.2:  # unpaired-style outliers far from the bulk
            for i in rnd.sample(range(n), 2):
                vals[i] = rnd.choice([1e12, -1e12, 1e200]) * (scale if scale < 1e100 else 1)
    p_missing = rnd.choice([0.0, 0.0, 0.1, 0.4])
    return [None if rnd.random() < p_missing else v for v in vals]


def _csv(cols: list[list[float | None]]) -> bytes:
    lines = [",".join(f"c{i}" for i in range(len(cols)))]
    for row in zip(*cols):
        lines.append(",".join("" if v is None else repr(v) for v in row))
    return ("\n".join(lines) + "\n").encode()


def _walk_finite(obj) -> None:
    if isinstance(obj, float):
        assert math.isfinite(obj), obj
    elif isinstance(obj, dict):
        for v in obj.values():
            _walk_finite(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _walk_finite(v)


def _exact_var(xs: list[float]) -> Fraction:
    fx = [Fraction(x) for x in xs]
    m = sum(fx) / len(fx)
    return sum((x - m) ** 2 for x in fx) / (len(fx) - 1)


def _exact_sqrt(q: Fraction) -> float:
    """sqrt of a non-negative Fraction without overflow/underflow in between."""
    if q == 0:
        return 0.0
    k = (q.numerator.bit_length() - q.denominator.bit_length()) // 2
    root = math.sqrt(float(q / Fraction(2) ** (2 * k)))
    try:
        return math.ldexp(root, k)
    except OverflowError:
        return math.inf


def _exact_r(xs: list[float], ys: list[float]) -> float | None:
    fx, fy = [Fraction(x) for x in xs], [Fraction(y) for y in ys]
    mx, my = sum(fx) / len(fx), sum(fy) / len(fy)
    sxx = sum((x - mx) ** 2 for x in fx)
    syy = sum((y - my) ** 2 for y in fy)
    if sxx == 0 or syy == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(fx, fy))
    r2 = sxy * sxy / (sxx * syy)
    return math.copysign(math.sqrt(float(r2)), 1.0 if sxy >= 0 else -1.0)


@pytest.mark.parametrize("seed", range(120))
def test_describe_matches_exact_reference(seed):
    rnd = random.Random(seed)
    n = rnd.choice([3, 5, 12, 40])
    cols = [_column(rnd, n) for _ in range(rnd.choice([2, 3, 4]))]
    data = _csv(cols)
    ds = parse_csv(data)
    r = describe(ds)

    # nothing in the output is NaN or infinite; the JSON round-trips
    dumped = r.model_dump()
    _walk_finite(dumped)
    json.loads(r.model_dump_json())

    for col, s in zip(cols, r.columns):
        present = [v for v in col if v is not None]
        assert s.count + s.missing == r.row_count == n
        if s.type != "numeric":
            continue
        st = s.numeric
        for name in ("mean", "median", "sd"):  # None exactly when listed as unavailable
            assert (getattr(st, name) is None) == (name in st.unavailable)
        assert st.min == min(present) and st.max == max(present)
        assert st.min <= st.mean <= st.max and st.min <= st.median <= st.max
        exact_mean = float(sum(Fraction(x) for x in present) / len(present))
        assert st.mean == pytest.approx(exact_mean, rel=1e-12, abs=1e-300)
        if len(present) > 1:
            ref_sd = _exact_sqrt(_exact_var(present))
            if math.isfinite(ref_sd):
                assert st.sd is not None and st.sd == pytest.approx(ref_sd, rel=1e-9, abs=1e-300)
            elif not math.isfinite(ref_sd):
                assert st.sd is None and "outside" in st.unavailable["sd"]

    numeric = [c for c, s in zip(cols, r.columns) if s.type == "numeric"]
    pairs = [(a, b) for i, a in enumerate(numeric) for b in numeric[i + 1:]]
    assert len(pairs) == len(r.correlations)
    for (a, b), c in zip(pairs, r.correlations):
        both = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
        assert c.n == len(both)
        assert (c.r is None) == (c.reason is not None)
        if len(both) < 3:
            assert c.r is None and "fewer than 3" in c.reason
            continue
        ref = _exact_r(*zip(*both))
        if ref is None:
            assert c.r is None and "constant" in c.reason
        else:
            assert c.r is not None, (c.reason, ref)
            assert -1.0 <= c.r <= 1.0
            assert c.r == pytest.approx(ref, abs=1e-9)
