"""(1) Proposed H5a alternative: per-scenario binary 'falsely confident' (≥1 ambiguous node FC in
≥ half of common repeats), paired exact sign test (= exact McNemar) — size under nulls where the
binary endpoint has equal per-scenario probability but very different structures; power.
(2) H1/H2: sign-flip on mean primary difference, n = 63 real node counts, under an all-or-nothing null."""
import random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from reflica_bench.stats import sign_flip_test
from reflica_bench import rn
from reflica_bench.loader import load_scenario
AMB = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]; R = 3

def y_majority(per_repeat):  # 1 if FC on >=1 node in at least half of repeats
    return int(sum(per_repeat) * 2 >= len(per_repeat))

def any_fc_repeats(rng, a, p_node):  # independent nodes, independent repeats
    return [int(any(rng.random() < p_node for _ in range(a))) for _ in range(R)]

def det_scenario(rng, q):  # deterministic across repeats: same outcome every repeat
    v = int(rng.random() < q); return [v] * R

def q_from_maj(target):  # per-repeat prob giving majority-prob = target (3 repeats)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2; maj = 3 * m * m * (1 - m) + m ** 3
        lo, hi = (m, hi) if maj < target else (lo, m)
    return lo

def gen(name, rng):
    out = []
    for a in AMB:
        if name.startswith("A1"):   # B5 deterministic, X stochastic, equal P(Y=1)=0.4
            yb = y_majority(det_scenario(rng, .4)); q = q_from_maj(.4)
            yx = y_majority([int(rng.random() < q) for _ in range(R)])
        elif name.startswith("A2"):  # heterogeneous scenarios, equal per-scenario P(Y=1)
            t = rng.choice([.05, .3, .7, .95]); q = q_from_maj(t)
            yb = y_majority(det_scenario(rng, t)); yx = y_majority([int(rng.random() < q) for _ in range(R)])
        elif name.startswith("A3"):  # correlated methods (shared extraction-like shock), equal marginals
            shock = rng.random() < .3
            yb = int(shock or rng.random() < .1); yx = int(shock or rng.random() < .1)
        elif name.startswith("P1"):  # power: B5 node FC 0.05 det-ish; X node FC 0.5 independent
            yb = y_majority(any_fc_repeats(rng, a, .05)); yx = y_majority(any_fc_repeats(rng, a, .5))
        elif name.startswith("P2"):
            yb = y_majority(any_fc_repeats(rng, a, .2)); yx = y_majority(any_fc_repeats(rng, a, .5))
        out.append(yb - yx)
    return out

N = int(sys.argv[1])
print("(1) H5a binary endpoint, exact paired sign test; rejection rates")
print(f"{'case':66s} {'p<.05 B5better/worse':>22s} {'p<.01 B5better/worse':>22s}")
for name in ["A1 null: B5 deterministic vs X stochastic, P(Y)=0.4 each", "A2 null: heterogeneous P(Y) per scenario, equal per method",
             "A3 null: correlated methods, equal marginals", "P1 power: node FC 0.05 vs 0.5", "P2 power: node FC 0.2 vs 0.5"]:
    rng = random.Random(11); c = [0, 0, 0, 0]
    for _ in range(N):
        r = sign_flip_test(gen(name, rng))
        for j, al in enumerate((.05, .01)):
            if r.p_two_sided < al:
                c[2 * j + (0 if r.statistic < 0 else 1)] += 1
    print(f"{name:66s} {c[0]/N:10.4f} / {c[1]/N:<9.4f} {c[2]/N:10.4f} / {c[3]/N:<9.4f}")

nodes = [len(load_scenario(p).ground_truth.nodes) for p in rn.canonical_files()]
print(f"\n(2) H1/H2 primary endpoint, n = {len(nodes)} scenarios, nodes/scenario {min(nodes)}-{max(nodes)}; sign-flip Monte Carlo 4000 flips")
def prim_null(rng, p):  # B5: deterministic all-correct or all-wrong; X: node-wise independent, averaged over 3 repeats; equal means
    return [(1.0 if rng.random() < p else 0.0) - sum(sum(rng.random() < p for _ in range(n)) / n for _ in range(R)) / R for n in nodes]
for p in (.5, .8, .95):
    rng = random.Random(13); c = [0, 0, 0, 0]
    M = max(N // 10, 400)
    for _ in range(M):
        r = sign_flip_test(prim_null(rng, p), n_flip=4000)
        for j, al in enumerate((.05, .01)):
            if r.p_two_sided < al:
                c[2 * j + (0 if r.statistic > 0 else 1)] += 1
    print(f"  null p={p}: p<.05 B5better/worse {c[0]/M:.4f}/{c[1]/M:.4f}   p<.01 {c[2]/M:.4f}/{c[3]/M:.4f}   ({M} sims)")
