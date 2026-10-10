"""Pre-specified statistics: exactness, reproducibility and verdict boundaries."""

from __future__ import annotations

import itertools
import random
import statistics

import pytest

from reflica_bench import stats as S


def _brute_force_p(diffs):
    d = [round(x, 12) for x in diffs if round(x, 12) != 0]
    r = S._ranks([abs(x) for x in d])
    w = sum(k for k, x in zip(r, d) if x > 0)
    sums = [sum(k for k, s in zip(r, signs) if s) for signs in itertools.product((0, 1), repeat=len(d))]
    lo = sum(s <= w + 1e-9 for s in sums) / len(sums)
    hi = sum(s >= w - 1e-9 for s in sums) / len(sums)
    return min(1.0, 2 * min(lo, hi))


def test_wilcoxon_matches_brute_force_with_ties_and_zeros():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(1, 10)
        diffs = [rng.choice([-2, -1, -0.5, 0, 0.5, 1, 1, 2, 1 / 3]) for _ in range(n)]
        assert S.wilcoxon_signed_rank(diffs).p_two_sided == pytest.approx(_brute_force_p(diffs))


def test_wilcoxon_matches_scipy_exact_without_ties():
    scipy_stats = pytest.importorskip("scipy.stats")
    rng = random.Random(2)
    for _ in range(50):
        diffs = [rng.uniform(-1, 1.2) for _ in range(rng.randint(5, 25))]
        ours = S.wilcoxon_signed_rank(diffs)
        ref = scipy_stats.wilcoxon(diffs, method="exact")
        assert ours.p_two_sided == pytest.approx(ref.pvalue, rel=1e-9)
        assert min(ours.w_plus, ours.w_minus) == pytest.approx(ref.statistic)


def test_wilcoxon_edge_cases():
    assert S.wilcoxon_signed_rank([0, 0, 0]).p_two_sided == 1.0
    r = S.wilcoxon_signed_rank([0.1] * 8)
    assert r.p_two_sided == pytest.approx(2 / 2 ** 8) and r.rank_biserial == 1.0
    assert S.wilcoxon_signed_rank([1e-15, -1e-15, 0.2]).n_nonzero == 1  # float noise is not a difference


def test_minimum_attainable_p_values_documented_in_protocol():
    """Holm with 5 tests needs p < 0.01 for the smallest; 8 one-sided non-zero
    differences reach it, 7 do not (protocol §5, H5a power note)."""
    assert S.wilcoxon_signed_rank([1] * 8).p_two_sided < 0.01
    assert S.wilcoxon_signed_rank([1] * 7).p_two_sided > 0.01


def test_quantile_is_type_7():
    rng = random.Random(3)
    xs = sorted(rng.random() for _ in range(37))
    for q, ref in zip((0.25, 0.5, 0.75), statistics.quantiles(xs, n=4, method="inclusive")):
        assert S.quantile(xs, q) == pytest.approx(ref)


def test_bootstrap_is_reproducible_and_stratified():
    units = list(range(20))
    strata = ["a"] * 5 + ["b"] * 15
    seen = []

    def stat(sample):
        seen.append(sum(u < 5 for u in sample))
        return sum(sample) / len(sample)

    ci1 = S.bootstrap_ci(units, strata, stat, n_boot=500)
    assert all(k == 5 for k in seen)  # every resample keeps stratum sizes
    assert S.bootstrap_ci(units, strata, stat, n_boot=500) == ci1
    assert S.bootstrap_ci(units, strata, stat, n_boot=500, seed=7) != ci1
    assert S.bootstrap_ci([0.3] * 6, ["x"] * 6, lambda s: sum(s) / len(s), n_boot=200) == pytest.approx((0.3, 0.3))


def test_holm():
    adj = S.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06})
    assert S.holm({"a": 0.6, "b": 0.7}) == pytest.approx({"a": 1.0, "b": 1.0})


def test_superiority_verdicts_and_discordance():
    v = S.verdict_superiority
    assert v(0.01, (0.02, 0.3), 0.8, +1) == {"verdict": S.SUPPORTED, "discordant": False}
    assert v(0.01, (-0.3, -0.02), -0.8, +1) == {"verdict": S.CONTRADICTED, "discordant": False}
    assert v(0.01, (-0.01, 0.3), 0.8, +1) == {"verdict": S.INCONCLUSIVE, "discordant": True}
    assert v(0.20, (0.02, 0.3), 0.8, +1) == {"verdict": S.INCONCLUSIVE, "discordant": True}
    assert v(0.20, (-0.1, 0.3), 0.8, +1) == {"verdict": S.INCONCLUSIVE, "discordant": False}
    assert v(0.05, (0.02, 0.3), 0.8, +1)["verdict"] == S.INCONCLUSIVE  # p must be strictly below α
    assert v(0.01, (0.0, 0.3), 0.8, +1)["verdict"] == S.INCONCLUSIVE   # CI touching 0 does not exclude it
    assert v(0.01, (-0.3, -0.02), -0.8, -1)["verdict"] == S.SUPPORTED  # predicted decrease (H5a)


def test_strict_boundaries_for_h4_and_h5b():
    assert S.verdict_noninferiority((-0.05, 0.1), 0.05) == S.INCONCLUSIVE
    assert S.verdict_noninferiority((-0.0499, 0.1), 0.05) == S.SUPPORTED
    assert S.verdict_noninferiority((-0.3, -0.06), 0.05) == S.CONTRADICTED
    assert S.verdict_below_threshold((0.02, 0.15), 0.15) == S.INCONCLUSIVE
    assert S.verdict_below_threshold((0.02, 0.1499), 0.15) == S.SUPPORTED
    assert S.verdict_below_threshold((0.16, 0.3), 0.15) == S.CONTRADICTED


def test_composite_verdict():
    assert S.verdict_all([S.SUPPORTED] * 3) == S.SUPPORTED
    assert S.verdict_all([S.SUPPORTED, S.INCONCLUSIVE]) == S.INCONCLUSIVE
    assert S.verdict_all([S.SUPPORTED, S.CONTRADICTED]) == S.CONTRADICTED
    assert S.verdict_all([]) == S.INCONCLUSIVE


def test_analysis_set_common_repeats_and_missingness():
    types = ("B1", "B2", "EXTRACT")
    st = {(s, c, r): S.OK for s in ("s1", "s2", "s3") for c in types for r in range(3)}
    st[("s1", "B2", 1)] = S.INFRA_MISSING         # repeat 1 of s1 no longer common
    st[("s2", "EXTRACT", 0)] = S.MODEL_FAILURE    # scored, not missing
    for r in range(3):
        del st[("s3", "B1", r)]                   # never ran -> excluded
    a = S.analysis_set(st, ["s1", "s2", "s3"], types, 3)
    assert a["common_repeats"] == {"s1": [0, 2], "s2": [0, 1, 2]}
    assert a["excluded_scenarios"] == ["s3"]
    assert a["calls_infra_missing"] == 4 and a["calls_planned"] == 27
    assert a["by_call_type"]["EXTRACT"][S.MODEL_FAILURE] == 1
    assert a["stop_rule_triggered"]  # 4/27 > 5%


def _brute_sign_flip(diffs):
    d = [round(x, 12) for x in diffs if round(x, 12) != 0]
    obs = abs(sum(d))
    sums = [abs(sum(x if s else -x for x, s in zip(d, signs))) for signs in itertools.product((0, 1), repeat=len(d))]
    return sum(v >= obs - 1e-9 for v in sums) / len(sums)


def test_sign_flip_matches_brute_force():
    rng = random.Random(4)
    for _ in range(200):
        diffs = [rng.choice([-2, -1, -1 / 3, 0, 1 / 3, 0.5, 1, 2, 3]) for _ in range(rng.randint(1, 11))]
        r = S.sign_flip_test(diffs)
        assert r.exact and r.p_two_sided == pytest.approx(_brute_sign_flip(diffs))


def test_sign_flip_monte_carlo_agrees_with_exact_and_is_reproducible():
    rng = random.Random(5)
    diffs = [rng.uniform(-1, 1.5) for _ in range(18)]
    exact = S.sign_flip_test(diffs).p_two_sided
    S_max = S.EXACT_MAX_SUMS
    try:
        S.EXACT_MAX_SUMS = 5
        mc1 = S.sign_flip_test(diffs, n_flip=40_000)
        mc2 = S.sign_flip_test(diffs, n_flip=40_000)
    finally:
        S.EXACT_MAX_SUMS = S_max
    assert not mc1.exact and mc1 == mc2
    assert mc1.p_two_sided == pytest.approx(exact, abs=0.01)


def test_sign_flip_statistic_is_the_estimand_numerator():
    """H5a: pooled-rate difference = Σ d_s / Σ amb_s with Σ amb_s fixed by gold,
    so the test statistic and the CI's point estimate have the same sign and
    the test's p-value does not depend on the denominator."""
    fc_b5 = [0, 0, 1, 0, 0, 0, 1 / 3, 0, 0, 1, 0]
    fc_x = [1, 1, 1, 1, 0, 1, 2, 1, 2, 3, 3]
    amb = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    d = [a - b for a, b in zip(fc_b5, fc_x)]
    r = S.sign_flip_test(d)
    assert r.statistic / sum(amb) == pytest.approx((sum(fc_b5) - sum(fc_x)) / sum(amb))
    assert S.sign_flip_test([x * 7 for x in d]).p_two_sided == pytest.approx(r.p_two_sided)


def test_sign_flip_minimum_p_values():
    assert S.sign_flip_test([1] * 8).p_two_sided == pytest.approx(2 / 2 ** 8)
    assert S.sign_flip_test([1] * 7).p_two_sided == pytest.approx(2 / 2 ** 7)
    assert S.sign_flip_test([0, 0]).p_two_sided == 1.0


def test_missingness_by_call_type_and_category():
    types = ("B1", "EXTRACT")
    st = {(s, c, r): S.OK for s in ("a", "b") for c in types for r in range(2)}
    st[("b", "EXTRACT", 0)] = S.INFRA_MISSING
    st[("b", "EXTRACT", 1)] = S.INFRA_MISSING
    a = S.analysis_set(st, ["a", "b"], types, 2, categories={"a": 7, "b": 7})
    cell = a["by_call_type_and_category"]["EXTRACT|cat7"]
    assert (cell[S.OK], cell[S.INFRA_MISSING], cell["repeats_used"], cell["excluded"]) == (2, 2, 2, ["b"])
    assert a["by_call_type_and_category"]["B1|cat7"]["excluded"] == ["b"]   # excluded for every method


# --- binary-endpoint methods (protocol v0.4, S1) ------------------------------

def test_wilson_and_clopper_pearson_closed_forms():
    lo, hi = S.wilson(0, 10)
    z = 1.959963984540054
    assert lo == pytest.approx(0, abs=1e-12) and hi == pytest.approx(z * z / (10 + z * z), rel=1e-9)
    assert S.clopper_pearson(0, 63) == pytest.approx((0.0, 1 - 0.025 ** (1 / 63)), abs=1e-9)
    assert S.clopper_pearson(63, 63) == pytest.approx((0.025 ** (1 / 63), 1.0), abs=1e-9)
    for k in (1, 3, 10, 31):
        lo, hi = S.clopper_pearson(k, 63)
        assert S.binom_cdf(k, 63, hi) == pytest.approx(0.025, abs=1e-9)       # defining equations
        assert 1 - S.binom_cdf(k - 1, 63, lo) == pytest.approx(0.025, abs=1e-9)
        assert S.clopper_pearson(63 - k, 63) == pytest.approx((1 - hi, 1 - lo), abs=1e-9)


def test_h5b_rule_supports_at_most_three_of_63():
    assert [k for k in range(64) if S.clopper_pearson(k, 63)[1] < 0.15] == [0, 1, 2, 3]


def test_mcnemar_is_the_exact_binomial_test_on_discordant_pairs():
    import math
    t = S.paired_binary([1] * 9 + [0] * 2 + [1] * 30, [0] * 9 + [1] * 2 + [1] * 30)
    assert (t.only_first, t.only_second, t.both) == (9, 2, 30)
    tail = sum(math.comb(11, i) for i in range(3)) / 2 ** 11
    assert S.mcnemar_exact(t).p_two_sided == pytest.approx(2 * tail)
    assert S.mcnemar_exact(S.paired_binary([1, 0], [1, 0])).p_two_sided == 1.0


def test_newcombe_interval_properties_and_coverage():
    t = S.paired_binary([1] * 50 + [0] * 13, [1] * 45 + [0] * 18)
    lo, hi = S.newcombe_paired_ci(t)
    assert lo < t.difference < hi and -1 <= lo and hi <= 1
    same = S.paired_binary([1] * 40 + [0] * 23, [1] * 40 + [0] * 23)
    lo, hi = S.newcombe_paired_ci(same)
    assert lo < 0 < hi
    rng = random.Random(9)
    cover = 0
    for _ in range(600):
        f, g = [], []
        for _ in range(63):
            u = rng.random()
            f.append(int(u < .9))
            g.append(int(u < .8) if rng.random() < .5 else int(rng.random() < .8))
        lo, hi = S.newcombe_paired_ci(S.paired_binary(f, g))
        cover += lo <= 0.1 <= hi
    assert cover / 600 >= 0.93


def test_sign_flip_is_exact_for_long_binary_sequences():
    r = S.sign_flip_test([1] * 40 + [-1] * 20)
    assert r.exact and r.n_nonzero == 60


def test_newcombe_uses_the_pairing_correlation():
    """Positive within-pair correlation must narrow the interval relative to
    ignoring it (phi = 0); negative correlation must widen it."""
    import math

    def width_phi0(t):
        a, b, c, d, n = t.both, t.only_first, t.only_second, t.neither, t.n
        p1, p2 = (a + b) / n, (a + c) / n
        l1, u1 = S.wilson(a + b, n)
        l2, u2 = S.wilson(a + c, n)
        return math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)

    pos = S.PairedBinary(both=20, only_first=12, only_second=2, neither=16)   # Armitage & Berry layout
    lo, hi = S.newcombe_paired_ci(pos)
    assert hi - lo < width_phi0(pos) - 0.01
    neg = S.PairedBinary(both=2, only_first=20, only_second=18, neither=10)
    lo, hi = S.newcombe_paired_ci(neg)
    assert hi - lo > width_phi0(neg) + 0.001


def test_mean_t_interval():
    m, lo, hi = S.mean_t_interval([0.1, 0.2, 0.3, 0.4])
    assert m == pytest.approx(0.25)
    half = S.t_ppf(0.975, 3) * (sum((x - 0.25) ** 2 for x in (0.1, 0.2, 0.3, 0.4)) / 3) ** 0.5 / 2
    assert (lo, hi) == pytest.approx((0.25 - half, 0.25 + half))
    assert S.t_cdf(0.0, 7) == pytest.approx(0.5) and S.t_cdf(S.t_ppf(0.9, 7), 7) == pytest.approx(0.9)
