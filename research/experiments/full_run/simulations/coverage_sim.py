"""Coverage of the pre-specified stratified percentile bootstrap CI (H4: mean primary difference;
H5b: pooled false-abstention rate) under skewed, all-or-nothing structures; Wilcoxon size for H1."""
import random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from reflica_bench.stats import bootstrap_ci, wilcoxon_signed_rank
from reflica_bench import rn
from reflica_bench.loader import load_scenario
from reflica_bench.schema import Determinability as D
scs = [load_scenario(p) for p in rn.canonical_files()]
nodes = [len(s.ground_truth.nodes) for s in scs]
det = [sum(g.determinability != D.AMBIGUOUS for g in s.ground_truth.nodes.values()) for s in scs]
cats = [s.category for s in scs]
R = 3; units = list(range(len(scs)))
N, B = int(sys.argv[1]), int(sys.argv[2])

def h4_diff(rng, pb, px):  # B5 all-or-nothing per scenario (deterministic), B4b all-or-nothing per repeat
    return [(1.0 if rng.random() < pb else 0.0) - sum(1.0 if rng.random() < px else 0.0 for _ in range(R)) / R for n in nodes]
for pb, px, label in ((.95, .95, "equal means, p=.95"), (.9, .95, "B5 0.05 worse")):
    rng = random.Random(3); cover = 0; true = pb - px
    for i in range(N):
        d = h4_diff(rng, pb, px)
        lo, hi = bootstrap_ci(units, cats, lambda s: sum(d[j] for j in s) / len(s), n_boot=B, seed=i)
        cover += lo <= true <= hi
    print(f"H4 mean-difference CI coverage ({label}): {cover/N:.3f}  (target 0.95)")

for q, label in ((.02, "rare, all-or-nothing per scenario"), (.10, "10%, all-or-nothing per scenario")):
    rng = random.Random(4); cover = 0; low_ok = 0
    for i in range(N):
        fa = [k if rng.random() < q else 0 for k in det]  # deterministic method abstains on all determinable nodes of a scenario
        lo, hi = bootstrap_ci(units, cats, lambda s: sum(fa[j] for j in s) / sum(det[j] for j in s), n_boot=B, seed=i)
        cover += lo <= q <= hi; low_ok += hi < q
    print(f"H5b pooled-rate CI coverage ({label}): {cover/N:.3f}; upper bound below truth {low_ok/N:.3f} (target <= 0.025)")

rng = random.Random(13); c = [0, 0]
for _ in range(N):
    d = [(1.0 if rng.random() < .95 else 0.0) - sum(sum(rng.random() < .95 for _ in range(n)) / n for _ in range(R)) / R for n in nodes]
    r = wilcoxon_signed_rank(d)
    if r.p_two_sided < .05:
        c[0 if r.rank_biserial > 0 else 1] += 1
print(f"Wilcoxon H1 null p=.95: p<.05 B5better/worse {c[0]/N:.4f}/{c[1]/N:.4f}")
