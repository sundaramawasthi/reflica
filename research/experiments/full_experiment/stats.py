"""Statistics for the confirmatory experiment (PROTOCOL.md §6). Stdlib only.

Resampling unit is always the scenario: callers pass one value (or one
numerator/denominator pair) per scenario, already aggregated over repeats, so
repeated calls on one scenario are never treated as independent samples.
"""
from __future__ import annotations

import math
import random
from typing import Callable, Sequence

B_RESAMPLES = 10_000
SEED = 20261009
ALPHA = 0.05


def percentile_ci(stats: Sequence[float], alpha: float = ALPHA) -> tuple[float, float]:
    """Two-sided percentile interval; the (alpha/2, 1 - alpha/2) order statistics."""
    s = sorted(stats)
    n = len(s)
    lo = s[max(0, math.floor(alpha / 2 * n))]
    hi = s[min(n - 1, math.ceil((1 - alpha / 2) * n) - 1)]
    return lo, hi


def two_sided_p(stats: Sequence[float], null: float = 0.0) -> float:
    """Bootstrap p-value by CI inversion: 2·min(P*(T ≤ null), P*(T ≥ null)), capped at 1.
    A degenerate distribution exactly at the null gives p = 1."""
    n = len(stats)
    le = sum(t <= null for t in stats) / n
    ge = sum(t >= null for t in stats) / n
    return min(1.0, 2 * min(le, ge))


def bootstrap(n_units: int, statistic: Callable[[list[int]], float | None],
              b: int = B_RESAMPLES, seed: int = SEED) -> tuple[list[float], int]:
    """Resample unit indices with replacement. Resamples where the statistic is
    undefined (returns None, e.g. a zero denominator) are skipped and counted."""
    rng = random.Random(seed)
    out: list[float] = []
    skipped = 0
    for _ in range(b):
        idx = [rng.randrange(n_units) for _ in range(n_units)]
        v = statistic(idx)
        if v is None:
            skipped += 1
        else:
            out.append(v)
    return out, skipped


def paired_mean_difference(diffs: Sequence[float], b: int = B_RESAMPLES, seed: int = SEED) -> dict:
    """Paired scenario-level bootstrap of mean(method − comparator)."""
    n = len(diffs)
    if n < 2:
        return {"n": n, "estimate": None, "ci": None, "p": None, "note": "fewer than 2 paired scenarios"}
    stats, _ = bootstrap(n, lambda idx: sum(diffs[i] for i in idx) / n, b, seed)
    return {"n": n, "estimate": sum(diffs) / n, "ci": percentile_ci(stats), "p": two_sided_p(stats),
            "degenerate": len(set(diffs)) == 1}


def pooled_rate(num: Sequence[float], den: Sequence[float], b: int = B_RESAMPLES, seed: int = SEED) -> dict:
    """Pooled rate Σnum/Σden with a scenario-cluster bootstrap CI."""
    n = len(num)
    if n < 2 or sum(den) == 0:
        return {"n": n, "estimate": None, "ci": None, "note": "insufficient data"}

    def stat(idx):
        d = sum(den[i] for i in idx)
        return None if d == 0 else sum(num[i] for i in idx) / d
    stats, skipped = bootstrap(n, stat, b, seed)
    return {"n": n, "estimate": sum(num) / sum(den), "ci": percentile_ci(stats), "skipped_resamples": skipped}


def pooled_rate_difference(num_a, den_a, num_b, den_b, b: int = B_RESAMPLES, seed: int = SEED) -> dict:
    """Paired cluster bootstrap of pooled_rate(a) − pooled_rate(b) over the same scenarios."""
    n = len(num_a)
    if n < 2 or sum(den_a) == 0 or sum(den_b) == 0:
        return {"n": n, "estimate": None, "ci": None, "p": None, "note": "insufficient data"}

    def stat(idx):
        da, db = sum(den_a[i] for i in idx), sum(den_b[i] for i in idx)
        if da == 0 or db == 0:
            return None
        return sum(num_a[i] for i in idx) / da - sum(num_b[i] for i in idx) / db
    stats, skipped = bootstrap(n, stat, b, seed)
    est = sum(num_a) / sum(den_a) - sum(num_b) / sum(den_b)
    return {"n": n, "estimate": est, "ci": percentile_ci(stats), "p": two_sided_p(stats),
            "skipped_resamples": skipped}


def holm(pvalues: dict[str, float | None], alpha: float = ALPHA) -> dict[str, dict]:
    """Holm step-down. Missing p-values are treated as 1 (cannot reject).
    Returns adjusted p and the reject decision per test."""
    items = sorted(pvalues.items(), key=lambda kv: (1.0 if kv[1] is None else kv[1]))
    m = len(items)
    out: dict[str, dict] = {}
    running = 0.0
    stop = False
    for k, (name, p) in enumerate(items):
        p = 1.0 if p is None else p
        adj = min(1.0, max(running, (m - k) * p))
        running = adj
        reject = not stop and p <= alpha / (m - k)
        if not reject:
            stop = True
        out[name] = {"p": p, "p_holm": adj, "reject": reject}
    return out
