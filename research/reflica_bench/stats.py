"""Pre-specified statistics for the full-experiment protocol (§5–§7).

Standard library only, so results do not depend on a numerical package's
version. Every function is deterministic for a given input and seed.

    sign_flip_test        paired randomisation test on Σ differences (confirmatory test)
    wilcoxon_signed_rank  exact conditional signed-rank test (ties allowed; sensitivity)
    bootstrap_ci          stratified percentile bootstrap (type-7 quantiles)
    holm                  Holm–Bonferroni adjusted p-values
    verdict_*             the protocol's verdict rules (strict inequalities)
    analysis_set          common-repeat eligibility and missingness
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

SEED = 20261010
N_BOOT = 10_000
ALPHA = 0.05
_ROUND = 12  # differences are rounded before ranking so float noise cannot create ties or break them

SUPPORTED, CONTRADICTED, INCONCLUSIVE = "Supported", "Contradicted", "Inconclusive"


# ---------------------------------------------------------------------------
# Wilcoxon signed-rank, exact
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WilcoxonResult:
    n_nonzero: int
    w_plus: float
    w_minus: float
    p_two_sided: float
    rank_biserial: float  # (W+ − W−) / (W+ + W−); 0 when there is no non-zero difference


def _ranks(values: Sequence[float]) -> list[float]:
    """Average ranks (1-based) of `values`."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def wilcoxon_signed_rank(diffs: Sequence[float]) -> WilcoxonResult:
    """Two-sided Wilcoxon signed-rank test, zero differences dropped
    (Wilcoxon's method), average ranks for tied |d|.

    The p-value is exact: the null distribution of W+ is enumerated over all
    2^n sign assignments of the observed ranks (by dynamic programming on
    doubled ranks, which are integers), so it stays exact with ties.
    p = min(1, 2 · min(P(W+ ≤ w), P(W+ ≥ w))).
    """
    d = [round(x, _ROUND) for x in diffs]
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return WilcoxonResult(0, 0.0, 0.0, 1.0, 0.0)
    r = _ranks([abs(x) for x in d])
    r2 = [int(round(2 * x)) for x in r]
    w_plus2 = sum(k for k, x in zip(r2, d) if x > 0)
    total2 = sum(r2)
    counts = [0] * (total2 + 1)
    counts[0] = 1
    for k in r2:
        for s in range(total2, k - 1, -1):
            counts[s] += counts[s - k]
    denom = 2 ** n
    lower = sum(counts[: w_plus2 + 1]) / denom
    upper = sum(counts[w_plus2:]) / denom
    p = min(1.0, 2 * min(lower, upper))
    w_plus, w_minus = w_plus2 / 2, (total2 - w_plus2) / 2
    return WilcoxonResult(n, w_plus, w_minus, p, (w_plus - w_minus) / (w_plus + w_minus))


# ---------------------------------------------------------------------------
# Paired sign-flip test on the sum of differences
# ---------------------------------------------------------------------------

EXACT_MAX_SUMS = 2_000_000
N_SIGN_FLIP = 200_000


@dataclass(frozen=True)
class SignFlipResult:
    n_nonzero: int
    statistic: float      # Σ d_s: the estimand's numerator (its denominator is fixed)
    p_two_sided: float
    exact: bool


def sign_flip_test(diffs: Sequence[float], *, seed: int = SEED, n_flip: int = N_SIGN_FLIP) -> SignFlipResult:
    """Two-sided paired sign-flip (randomisation) test of H0: each per-scenario
    difference is symmetric about 0. Statistic = Σ d_s, so the test is about
    the same quantity as a mean difference (Σ d / n) or a pooled-rate
    difference (Σ d / Σ amb) — the denominator does not change under sign flips.

    p = P(|S*| ≥ |S_obs|), computed exactly over all 2^k sign vectors
    (k = #non-zero) by dynamic programming on differences scaled to integers
    at 1e-9; sums equal within the rounding error count as ties. The DP stays
    exact for any k while the number of distinct partial sums is ≤ 2,000,000
    (always true for binary d, where it equals k + 1); otherwise Monte Carlo
    with `n_flip` vectors from `random.Random(seed)`,
    p = (1 + #{|S*| ≥ |S_obs|}) / (1 + n_flip).

    For binary per-scenario outcomes (d ∈ {−1, 0, 1}) this is exactly the
    two-sided exact McNemar test.
    """
    d = [round(x, _ROUND) for x in diffs]
    d = [x for x in d if x != 0]
    k = len(d)
    if k == 0:
        return SignFlipResult(0, 0.0, 1.0, True)
    scaled = [int(round(abs(x) * 1e9)) for x in d]
    obs = abs(sum(int(round(x * 1e9)) for x in d))
    tol = k  # each term carries ≤ 0.5 unit of rounding, so equal sums differ by < k units
    dist: dict[int, int] | None = {0: 1}
    for v in scaled:
        nxt: dict[int, int] = {}
        for s, c in dist.items():
            nxt[s + v] = nxt.get(s + v, 0) + c
            nxt[s - v] = nxt.get(s - v, 0) + c
        dist = nxt
        if len(dist) > EXACT_MAX_SUMS:
            dist = None
            break
    if dist is not None:
        hits = sum(c for s, c in dist.items() if abs(s) >= obs - tol)
        return SignFlipResult(k, sum(d), min(1.0, hits / 2 ** k), True)
    rng = random.Random(seed)
    hits = sum(abs(sum(v if rng.random() < 0.5 else -v for v in scaled)) >= obs - tol for _ in range(n_flip))
    return SignFlipResult(k, sum(d), (1 + hits) / (1 + n_flip), False)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def quantile(sorted_values: Sequence[float], q: float) -> float:
    """Type-7 (linear interpolation) quantile of already-sorted values."""
    h = (len(sorted_values) - 1) * q
    lo = math.floor(h)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (h - lo) * (sorted_values[hi] - sorted_values[lo])


def bootstrap_ci(
    units: Sequence[object],
    strata: Sequence[object],
    statistic: Callable[[Sequence[object]], float],
    *,
    n_boot: int = N_BOOT,
    seed: int = SEED,
    level: float = 0.95,
) -> tuple[float, float]:
    """Stratified percentile bootstrap CI.

    Units (scenarios) are resampled with replacement within each stratum
    (category), keeping each stratum's size. A fresh `random.Random(seed)`
    is used for every call, so each CI is reproducible on its own.
    """
    if len(units) != len(strata) or not units:
        raise ValueError("units and strata must be non-empty and the same length")
    groups: dict[object, list[object]] = {}
    for u, s in zip(units, strata):
        groups.setdefault(s, []).append(u)
    keys = sorted(groups, key=str)
    rng = random.Random(seed)
    stats = []
    for _ in range(n_boot):
        sample: list[object] = []
        for k in keys:
            g = groups[k]
            sample.extend(g[rng.randrange(len(g))] for _ in range(len(g)))
        stats.append(statistic(sample))
    stats.sort()
    a = (1 - level) / 2
    return quantile(stats, a), quantile(stats, 1 - a)


# ---------------------------------------------------------------------------
# Multiplicity
# ---------------------------------------------------------------------------

def holm(pvalues: Mapping[str, float]) -> dict[str, float]:
    """Holm–Bonferroni adjusted p-values (step-down, monotone, capped at 1)."""
    items = sorted(pvalues.items(), key=lambda kv: (kv[1], kv[0]))
    m = len(items)
    out: dict[str, float] = {}
    running = 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


# ---------------------------------------------------------------------------
# Verdict rules (protocol §6). All inequalities are strict.
# ---------------------------------------------------------------------------

def verdict_superiority(p_holm: float, ci: tuple[float, float], test_sign: float, predicted: int) -> dict:
    """`predicted` = +1 if the hypothesis predicts a positive difference, −1 if negative.
    `test_sign` = sign of the test statistic (Σ d for the sign-flip test).

    Supported:    p_holm < α, CI entirely on the predicted side of 0, test points the predicted way.
    Contradicted: p_holm < α, CI entirely on the opposite side, test points the opposite way.
    Otherwise Inconclusive; `discordant` marks a test/CI disagreement.
    """
    lo, hi = ci
    ci_side = 1 if lo > 0 else -1 if hi < 0 else 0
    t_side = 1 if test_sign > 0 else -1 if test_sign < 0 else 0
    sig = p_holm < ALPHA
    if sig and ci_side == predicted and t_side == predicted:
        v = SUPPORTED
    elif sig and ci_side == -predicted and t_side == -predicted:
        v = CONTRADICTED
    else:
        v = INCONCLUSIVE
    discordant = (sig != (ci_side != 0)) or (sig and ci_side != 0 and ci_side != t_side)
    return {"verdict": v, "discordant": discordant}


def verdict_noninferiority(ci: tuple[float, float], margin: float) -> str:
    """Supported iff CI lower bound > −margin; Contradicted iff CI upper bound < −margin."""
    lo, hi = ci
    if lo > -margin:
        return SUPPORTED
    if hi < -margin:
        return CONTRADICTED
    return INCONCLUSIVE


def verdict_below_threshold(ci: tuple[float, float], limit: float) -> str:
    """Supported iff CI upper bound < limit; Contradicted iff CI lower bound > limit."""
    lo, hi = ci
    if hi < limit:
        return SUPPORTED
    if lo > limit:
        return CONTRADICTED
    return INCONCLUSIVE


def verdict_all(parts: Sequence[str]) -> str:
    """Composite: Supported iff every part is Supported; Contradicted iff any part is
    Contradicted; otherwise Inconclusive."""
    if parts and all(p == SUPPORTED for p in parts):
        return SUPPORTED
    if any(p == CONTRADICTED for p in parts):
        return CONTRADICTED
    return INCONCLUSIVE


# ---------------------------------------------------------------------------
# Eligibility and missingness (protocol §7)
# ---------------------------------------------------------------------------

OK, MODEL_FAILURE, INFRA_MISSING = "ok", "model_failure", "infra_missing"


def analysis_set(
    status: Mapping[tuple[str, str, int], str],
    scenarios: Sequence[str],
    call_types: Sequence[str],
    repeats: int,
    categories: Mapping[str, object] | None = None,
) -> dict:
    """`status[(scenario, call_type, repeat)]` ∈ {ok, model_failure, infra_missing};
    an absent key is infra_missing. A repeat is *common* to a scenario when no
    call type is infra_missing in it (model failures are scored, not missing).
    The analysis set is every scenario with ≥ 1 common repeat; every
    comparison uses exactly this set and these repeats.
    """
    common: dict[str, list[int]] = {}
    for s in scenarios:
        reps = [r for r in range(repeats)
                if all(status.get((s, c, r), INFRA_MISSING) != INFRA_MISSING for c in call_types)]
        if reps:
            common[s] = reps
    planned = len(scenarios) * len(call_types) * repeats
    by_type = {
        c: {k: sum(status.get((s, c, r), INFRA_MISSING) == k for s in scenarios for r in range(repeats))
            for k in (OK, MODEL_FAILURE, INFRA_MISSING)}
        for c in call_types
    }
    infra = sum(v[INFRA_MISSING] for v in by_type.values())
    by_cat: dict[str, dict] = {}
    if categories is not None:
        for c in call_types:
            for s in scenarios:
                cell = by_cat.setdefault(f"{c}|cat{categories[s]}", {OK: 0, MODEL_FAILURE: 0, INFRA_MISSING: 0,
                                                                     "repeats_used": 0, "excluded": []})
                for r in range(repeats):
                    cell[status.get((s, c, r), INFRA_MISSING)] += 1
                cell["repeats_used"] += len(common.get(s, []))
                if s not in common:
                    cell["excluded"].append(s)
    return {
        "common_repeats": common,
        "excluded_scenarios": [s for s in scenarios if s not in common],
        "calls_planned": planned,
        "calls_infra_missing": infra,
        "infra_missing_fraction": infra / planned if planned else 0.0,
        "stop_rule_triggered": planned > 0 and infra / planned > 0.05,
        "by_call_type": by_type,
        "by_call_type_and_category": by_cat,
    }


# ---------------------------------------------------------------------------
# Exact and score methods for binary per-scenario endpoints (protocol v0.4)
# ---------------------------------------------------------------------------

def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X ≤ k) for X ~ Binomial(n, p), exact summation."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact two-sided Clopper–Pearson interval for a binomial proportion,
    found by bisection on the exact binomial CDF (no special functions)."""
    if not 0 <= k <= n or n == 0:
        raise ValueError("need 0 ≤ k ≤ n, n > 0")
    a = (1 - level) / 2

    def solve(f, target):  # f increasing in p on [0, 1]
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < target else (lo, mid)
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p), a)
    upper = 1.0 if k == n else solve(lambda p: 1 - binom_cdf(k, n, p), 1 - a)
    return lower, upper


def wilson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    z = _z(level)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def _z(level: float) -> float:
    """Standard-normal quantile for a two-sided level (bisection on erf)."""
    target = 1 - (1 - level) / 2
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < target else (lo, mid)
    return (lo + hi) / 2


@dataclass(frozen=True)
class PairedBinary:
    both: int        # a: both methods 1
    only_first: int  # b: first 1, second 0
    only_second: int  # c: first 0, second 1
    neither: int     # d

    @property
    def n(self) -> int:
        return self.both + self.only_first + self.only_second + self.neither

    @property
    def difference(self) -> float:
        """p_first − p_second = (b − c) / n."""
        return (self.only_first - self.only_second) / self.n


def paired_binary(first: Sequence[int], second: Sequence[int]) -> PairedBinary:
    if len(first) != len(second):
        raise ValueError("paired sequences differ in length")
    a = sum(1 for x, y in zip(first, second) if x and y)
    b = sum(1 for x, y in zip(first, second) if x and not y)
    c = sum(1 for x, y in zip(first, second) if not x and y)
    return PairedBinary(a, b, c, len(first) - a - b - c)


def newcombe_paired_ci(t: PairedBinary, level: float = 0.95) -> tuple[float, float]:
    """Newcombe (1998, paired) method 10: square-and-add of Wilson score limits for
    the two marginal proportions, p_first − p_second, with Newcombe's corrected
    correlation term (as in contingencytables::Newcombe_square_and_add_CI_paired_2x2):
        A = ad − bc;  ψ = (A − N/2)/√P if A > N/2;  0 if 0 ≤ A ≤ N/2;  A/√P if A < 0;
        ψ = 0 if any margin is 0;  P = (a+b)(c+d)(a+c)(b+d).
    v0.4 used the uncorrected ψ = A/√P, which was narrower than the published
    method for positively correlated pairs (found by the R comparison)."""
    a, b, c, d, n = t.both, t.only_first, t.only_second, t.neither, t.n
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, level)
    l2, u2 = wilson(a + c, n, level)
    if a + b in (0, n) or a + c in (0, n):
        psi = 0.0
    else:
        prod = (a + b) * (c + d) * (a + c) * (b + d)
        big_a = a * d - b * c
        psi = (big_a - n / 2) / math.sqrt(prod) if big_a > n / 2 else 0.0 if big_a >= 0 else big_a / math.sqrt(prod)
    diff = p1 - p2
    lower = diff - math.sqrt(max(0.0, (p1 - l1) ** 2 + (u2 - p2) ** 2 - 2 * psi * (p1 - l1) * (u2 - p2)))
    upper = diff + math.sqrt(max(0.0, (p2 - l2) ** 2 + (u1 - p1) ** 2 - 2 * psi * (p2 - l2) * (u1 - p1)))
    return lower, upper


def tango_paired_ci(t: PairedBinary, level: float = 0.95) -> tuple[float, float]:
    """Tango (1998) asymptotic score interval for p_first − p_second, paired
    (as contingencytables::Tango_asymptotic_score_CI_paired_2x2): the set of Δ
    with |T(Δ)| ≤ z, T(Δ) = (b − c − NΔ) / √(N(2q̃ + Δ(1 − Δ))), q̃ the
    constrained ML estimate of P(second only). Limits by bisection."""
    b, c, n = t.only_first, t.only_second, t.n
    z = _z(level)
    est = (b - c) / n

    def stat(delta):
        bb = -b - c + (2 * n - b + c) * delta
        cc = -c * delta * (1 - delta)
        q = (math.sqrt(max(0.0, bb * bb - 8 * n * cc)) - bb) / (4 * n)
        var = n * (2 * q + delta * (1 - delta))
        return (b - c - n * delta) / math.sqrt(var) if var > 0 else 0.0

    def root(target, lo, hi):  # stat decreasing in delta; find stat == target (80 halvings < 1e-18)
        for _ in range(80):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if stat(mid) > target else (lo, mid)
        return (lo + hi) / 2

    tol = 1e-7
    lower = -1.0 if est == -1 else root(z, -1 + tol, 1 - tol)
    upper = 1.0 if est == 1 else root(-z, -1 + tol, 1 - tol)
    return lower, upper


def agresti_min_ci(t: PairedBinary, level: float = 0.95) -> tuple[float, float]:
    """Wald interval with Agresti–Min adjustment (0.5 added to every cell)."""
    z = _z(level)
    a, b, c, d = (x + 0.5 for x in (t.both, t.only_first, t.only_second, t.neither))
    n = a + b + c + d
    se = math.sqrt((b + c) - (b - c) ** 2 / n) / n
    return max(-1.0, (b - c) / n - z * se), min(1.0, (b - c) / n + z * se)


def bonett_price_ci(t: PairedBinary, level: float = 0.95) -> tuple[float, float]:
    """Wald interval with Bonett–Price adjustment ((n12 + 1)/(N + 2), (n21 + 1)/(N + 2))."""
    z = _z(level)
    p12, p21 = (t.only_first + 1) / (t.n + 2), (t.only_second + 1) / (t.n + 2)
    se = math.sqrt((p12 + p21 - (p12 - p21) ** 2) / (t.n + 2))
    return max(-1.0, p12 - p21 - z * se), min(1.0, p12 - p21 + z * se)


def mcnemar_midp(t: PairedBinary) -> float:
    """Two-sided McNemar mid-p (as contingencytables::McNemar_midP_test_paired_2x2)."""
    b, c = t.only_first, t.only_second
    k = b + c
    pmf = math.comb(k, b) / 2 ** k
    if b == c:
        return 1 - 0.5 * pmf
    return min(1.0, 2 * binom_cdf(min(b, c), k, 0.5)) - pmf


def mcnemar_exact(t: PairedBinary) -> SignFlipResult:
    """Two-sided exact McNemar test (conditional binomial on discordant pairs)."""
    return sign_flip_test([1] * t.only_first + [-1] * t.only_second)


# ---------------------------------------------------------------------------
# Descriptive intervals (protocol v0.6, S1 = D)
# ---------------------------------------------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    tail = 0.5 * _betainc(df / 2, 0.5, x)
    return 1 - tail if t > 0 else tail


def t_ppf(q: float, df: float) -> float:
    """Student-t quantile by bisection on the exact CDF."""
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return (lo + hi) / 2


def mean_t_interval(values: Sequence[float], level: float = 0.95) -> tuple[float, float, float]:
    """(mean, lower, upper): one-sample t-interval over scenarios. Descriptive use only:
    simulated coverage 0.934–0.959 at n = 63 (protocol Appendix C, DECISION_REPORT_S1_S4)."""
    n = len(values)
    m = sum(values) / n
    if n < 2:
        return m, float("nan"), float("nan")
    sd = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    half = t_ppf(1 - (1 - level) / 2, n - 1) * sd / math.sqrt(n)
    return m, m - half, m + half
