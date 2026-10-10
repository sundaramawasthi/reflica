"""S1 decision study (offline simulation; no data, no API). Run from research/:

    .venv/bin/python experiments/full_run/simulations/s1_study.py [scale]

scale = 1 (default) uses the simulation counts reported in protocol Appendix C;
smaller values give a quick smoke run. Seeds are fixed per configuration.

A  H4 binary non-inferiority: false pass at the margin (both tails), power, 5 CI methods
B  H1/H2/H5a binary superiority tests: size and power (exact, mid-p, asymptotic McNemar)
C  H5b binary threshold: Clopper–Pearson vs Wilson upper bound
D  original node-level estimands: CI procedures under clustering (percentile bootstrap,
   bootstrap-t, t-interval, empirical Bernstein)
E  estimand divergence: equal node-level accuracy, different error clustering
"""
from __future__ import annotations

import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from reflica_bench import rn, stats as S  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402
from reflica_bench.schema import Determinability  # noqa: E402

SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
_SC = [load_scenario(p) for p in rn.canonical_files()]
NODES = [len(s.ground_truth.nodes) for s in _SC]
DET = [sum(g.determinability != Determinability.AMBIGUOUS for g in s.ground_truth.nodes.values()) for s in _SC]
CATS = [s.category for s in _SC]
N63 = len(NODES)
Z = S._z(0.95)
CI = {"Newcombe": S.newcombe_paired_ci, "Tango": S.tango_paired_ci, "AgrestiMin": S.agresti_min_ci,
      "BonettPrice": S.bonett_price_ci}


def _old_newcombe(t):  # v0.4 implementation (uncorrected psi), kept to explain the 2.6%
    a, b, c, d, n = t.both, t.only_first, t.only_second, t.neither, t.n
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = S.wilson(a + b, n)
    l2, u2 = S.wilson(a + c, n)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    phi = (a * d - b * c) / math.sqrt(den) if den > 0 else 0.0
    return (p1 - p2 - math.sqrt(max(0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2)),
            p1 - p2 + math.sqrt(max(0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2)))


CI_DIAG = dict(CI, Newcombe_v04_uncorrected=_old_newcombe)


def pair(rng, p1, p2, rho):
    """One paired binary observation with marginals p1, p2. With probability rho
    the pair shares one uniform (maximal positive dependence), else independent."""
    if rng.random() < rho:
        u = rng.random()
        return int(u < p1), int(u < p2)
    return int(rng.random() < p1), int(rng.random() < p2)


def scen_probs(rng, p2, delta, hetero):
    """Per-scenario marginals (q1, q2) with average q1 − q2 exactly delta.
    'mixed': half the scenarios have q2 lowered by h and half raised by h,
    h = min(0.3, p2 − 0.1, 1 − p2), so no clamping changes the average."""
    q2 = p2
    if hetero == "mixed":
        h = max(0.0, min(0.3, p2 - 0.1, 1 - p2))
        q2 = p2 - h if rng.random() < 0.5 else p2 + h
    return q2 + delta, q2


# --------------------------------------------------------------------------- A
def job_a(cfg):
    p2, rho, hetero, delta, n_sim, seed = cfg
    rng = random.Random(seed)
    res = {m: [0, 0] for m in CI_DIAG}  # [supported (lower > -δ), contradicted (upper < -δ)]
    for _ in range(n_sim):
        f, g = [], []
        for _ in range(N63):
            q1, q2 = scen_probs(rng, p2, delta, hetero)
            x, y = pair(rng, q1, q2, rho)
            f.append(x)
            g.append(y)
        t = S.paired_binary(f, g)
        for m, fn in CI_DIAG.items():
            lo, hi = fn(t)
            res[m][0] += lo > -0.05
            res[m][1] += hi < -0.05
    return cfg, {m: (v[0] / n_sim, v[1] / n_sim) for m, v in res.items()}


# --------------------------------------------------------------------------- B
def _asym_p(t):
    b, c = t.only_first, t.only_second
    if b + c == 0:
        return 1.0
    z = abs(b - c) / math.sqrt(b + c)
    return math.erfc(z / math.sqrt(2))


def job_b(cfg):
    n, disc, structure, effect, n_sim, seed = cfg
    rng = random.Random(seed)
    out = {m: [0, 0, 0, 0] for m in ("exact", "midp", "asymptotic")}  # better@.05, worse@.05, better@.01, worse@.01
    for _ in range(n_sim):
        b = c = 0
        for _ in range(n):
            dd = disc if structure != "hetero" else rng.choice([disc / 4, disc * 1.75])
            r = 0.5 + effect if structure != "weaknull" else rng.choice([0.2, 0.8]) + effect
            r = min(1, max(0, r))
            if rng.random() < dd:
                if rng.random() < r:
                    b += 1
                else:
                    c += 1
        t = S.PairedBinary(0, b, c, n - b - c)
        ps = {"exact": S.mcnemar_exact(t).p_two_sided, "midp": S.mcnemar_midp(t), "asymptotic": _asym_p(t)}
        for m, p in ps.items():
            for j, al in enumerate((0.05, 0.01)):
                if p < al:
                    out[m][2 * j + (0 if b > c else 1)] += 1
    return cfg, {m: tuple(x / n_sim for x in v) for m, v in out.items()}


# --------------------------------------------------------------------------- C
def job_c(cfg):
    true, n_sim, seed = cfg
    rng = random.Random(seed)
    cp = w = 0
    for _ in range(n_sim):
        k = sum(rng.random() < true for _ in range(N63))
        cp += S.clopper_pearson(k, N63)[1] < 0.15
        w += S.wilson(k, N63)[1] < 0.15
    return cfg, (cp / n_sim, w / n_sim)


# --------------------------------------------------------------------------- D
def node_draw(rng, n_nodes, acc, pattern):
    """Fraction of a scenario's nodes correct, one repeat."""
    if pattern == "independent" or (pattern == "mixed" and rng.random() < 0.5):
        return sum(rng.random() < acc for _ in range(n_nodes)) / n_nodes
    return 1.0 if rng.random() < acc else 0.0


def _boot_t(d, strata, rng, B):
    n = len(d)
    m = sum(d) / n
    se = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1) / n) or 1e-12
    groups = {}
    for x, s in zip(d, strata):
        groups.setdefault(s, []).append(x)
    ts, ms = [], []
    for _ in range(B):
        smp = [g[rng.randrange(len(g))] for g in groups.values() for _ in g]
        mm = sum(smp) / n
        ss = math.sqrt(sum((x - mm) ** 2 for x in smp) / (n - 1) / n) or 1e-12
        ts.append((mm - m) / ss)
        ms.append(mm)
    ts.sort()
    ms.sort()
    return ((m - S.quantile(ts, 0.975) * se, m - S.quantile(ts, 0.025) * se),
            (S.quantile(ms, 0.025), S.quantile(ms, 0.975)))


def _t_interval(d):
    n = len(d)
    m = sum(d) / n
    se = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1) / n)
    tq = 1.999  # t_{0.975, 62}
    return m - tq * se, m + tq * se


def _emp_bernstein(d):
    """Maurer & Pontil (2009) empirical-Bernstein two-sided 95% bound for the mean of
    independent variables in [−1, 1] (rescaled to [0, 1]); conservative, finite-sample."""
    n = len(d)
    x = [(v + 1) / 2 for v in d]
    m = sum(x) / n
    var = sum((v - m) ** 2 for v in x) / (n - 1)
    lg = math.log(4 / 0.05)  # two-sided, union of two one-sided bounds at 0.025 each
    half = math.sqrt(2 * var * lg / n) + 7 * lg / (3 * (n - 1))
    return 2 * (m - half) - 1, 2 * (m + half) - 1


def job_d(cfg):
    acc, pattern_b5, pattern_x, delta, n_sim, B, seed = cfg
    rng = random.Random(seed)
    res = {k: [0, 0] for k in ("percentile", "bootstrap_t", "t_interval", "emp_bernstein")}
    for _ in range(n_sim):
        d = []
        for n in NODES:
            b5 = sum(node_draw(rng, n, acc + delta, pattern_b5) for _ in range(3)) / 3
            x = sum(node_draw(rng, n, acc, pattern_x) for _ in range(3)) / 3
            d.append(b5 - x)
        (bt, pc) = _boot_t(d, CATS, rng, B)
        for k, (lo, hi) in (("percentile", pc), ("bootstrap_t", bt), ("t_interval", _t_interval(d)),
                            ("emp_bernstein", _emp_bernstein(d))):
            res[k][0] += lo > -0.05     # H4 rule under the original node-level estimand
            res[k][1] += lo <= delta <= hi
    return cfg, {k: (v[0] / n_sim, v[1] / n_sim) for k, v in res.items()}


# --------------------------------------------------------------------------- E
def job_e(cfg):
    acc, n_sim, seed = cfg
    rng = random.Random(seed)
    sup = diff_sum = 0
    for _ in range(n_sim):
        f, g = [], []
        for n in NODES:
            fb = sum(rng.random() < acc for _ in range(1)) == 1  # B5: all-or-nothing per scenario
            f.append(int(fb))
            g.append(int(all(rng.random() < acc for _ in range(n))))  # X: independent node errors
        t = S.paired_binary(f, g)
        diff_sum += t.difference
        lo, hi = S.newcombe_paired_ci(t)
        sup += S.mcnemar_exact(t).p_two_sided < 0.05 and lo > 0
    return cfg, (diff_sum / n_sim, sup / n_sim)


def main():
    k = lambda n: max(50, int(n * SCALE))  # noqa: E731
    with Pool(4) as pool:
        print("A. H4 binary non-inferiority, n = 63, true difference = −0.05 (the margin).")
        print("   Rule: Supported iff lower > −0.05 (false pass); Contradicted iff upper < −0.05. Nominal ≤ 0.025 each.")
        cfgs = [(p2, rho, h, -0.05, k(10000), 1000 + i) for i, (p2, rho, h) in enumerate(
            (p2, rho, h) for p2 in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.0) for rho in (0.0, 0.3, 0.6, 0.9)
            for h in ("none", "mixed"))]
        worst = {m: (0, None) for m in CI_DIAG}
        rows = pool.map(job_a, cfgs)
        print(f"   {'p_B4b':>5} {'rho':>4} {'hetero':>6} | " + " | ".join(f"{m[:14]:>14}" for m in CI_DIAG))
        for cfg, r in rows:
            for m, (fp, _) in r.items():
                if fp > worst[m][0]:
                    worst[m] = (fp, cfg[:3])
            print(f"   {cfg[0]:5.2f} {cfg[1]:4.1f} {cfg[2]:>6} | " + " | ".join(f"{r[m][0]:6.4f}/{r[m][1]:6.4f}" for m in CI_DIAG))
        print("   worst false pass per method:", {m: (round(v, 4), c) for m, (v, c) in worst.items()},
              f"(MC s.e. at 0.025 ≈ {math.sqrt(0.025 * 0.975 / k(10000)):.4f})")

        print("\nA2. H4 power and both directions, p_B4b = 0.9, rho = 0.6 (P(Supported) / P(Contradicted))")
        cfgs = [(0.9, 0.6, h, dl, k(10000), 2000 + i) for i, (h, dl) in enumerate(
            (h, dl) for h in ("none", "mixed") for dl in (-0.15, -0.10, -0.05, 0.0, 0.05))]
        for cfg, r in pool.map(job_a, cfgs):
            print(f"   hetero={cfg[2]:>5} true Δ={cfg[3]:+.2f}: " + "  ".join(f"{m[:11]} {r[m][0]:.3f}/{r[m][1]:.3f}" for m in CI))

        print("\nB. Superiority tests: two-sided rejection split by direction (B5 better / B5 worse)")
        cfgs = [(n, disc, st, ef, k(20000), 3000 + i) for i, (n, disc, st, ef) in enumerate(
            (n, disc, st, ef) for n in (63, 11) for disc in (0.05, 0.2, 0.5) for st in ("homog", "hetero", "weaknull")
            for ef in (0.0, 0.3, -0.3))]
        for cfg, r in pool.map(job_b, cfgs):
            tag = "NULL" if cfg[3] == 0 else ("B5 better" if cfg[3] > 0 else "B5 worse")
            print(f"   n={cfg[0]:2d} P(disc)={cfg[1]:.2f} {cfg[2]:>8} {tag:>9}: " +
                  "  ".join(f"{m} .05:{v[0]:.4f}/{v[1]:.4f} .01:{v[2]:.4f}/{v[3]:.4f}" for m, v in r.items()))

        print("\nC. H5b (scenario-level): P(upper < 0.15)")
        for cfg, (cp, w) in pool.map(job_c, [(p, k(20000), 4000 + i) for i, p in enumerate((0.0, 0.02, 0.05, 0.10, 0.15, 0.20))]):
            print(f"   true rate {cfg[0]:.2f}: Clopper–Pearson {cp:.4f}   Wilson {w:.4f}" + ("   <- false pass" if cfg[0] >= 0.15 else "   <- power"))

        print("\nD. Original node-level H4 (mean node-correctness difference), 63 real scenarios, 3 repeats.")
        print("   P(lower > −0.05) / coverage of the true Δ")
        cfgs = [(acc, pb, px, dl, k(1000), 300, 5000 + i) for i, (acc, pb, px, dl) in enumerate(
            (acc, pb, px, dl) for acc in (0.8, 0.95) for (pb, px) in (("independent", "independent"),
                                                                       ("all_or_nothing", "independent"),
                                                                       ("all_or_nothing", "all_or_nothing"),
                                                                       ("mixed", "independent"))
            for dl in (-0.05, 0.0))]
        for cfg, r in pool.map(job_d, cfgs):
            print(f"   acc={cfg[0]:.2f} B5 {cfg[1]:>14} vs X {cfg[2]:>14} true Δ={cfg[3]:+.2f}: " +
                  "  ".join(f"{m} {v[0]:.3f}/{v[1]:.3f}" for m, v in r.items()))

        print("\nE. Equal node-level accuracy; B5 errors all-or-nothing per scenario, comparator independent per node.")
        for cfg, (dm, sup) in pool.map(job_e, [(a, k(4000), 6000 + i) for i, a in enumerate((0.8, 0.9, 0.95, 0.99))]):
            print(f"   node accuracy {cfg[0]:.2f} for both: mean binary 'fully correct' difference {dm:+.3f}; "
                  f"P(H1-type Supported at α .05) {sup:.3f}")


if __name__ == "__main__":
    main()
