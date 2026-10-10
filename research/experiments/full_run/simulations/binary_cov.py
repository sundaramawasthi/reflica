"""Coverage / error rates of the proposed binary-endpoint methods at the protocol's sizes."""
import random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from reflica_bench import stats as S
N = int(sys.argv[1])
print("Newcombe paired CI coverage (n=63), structures: (p_first, p_second, correlation via shared shock)")
for p1, p2, shock in ((.95, .95, .0), (.95, .90, .5), (.80, .60, .3), (.98, .93, .8), (.5, .5, .0), (1.0, .9, .0)):
    rng = random.Random(1); cov = 0; below = above = 0
    for _ in range(N):
        f, s_ = [], []
        for _ in range(63):
            if rng.random() < shock:  # shared outcome
                u = rng.random(); f.append(int(u < p1)); s_.append(int(u < p2))
            else:
                f.append(int(rng.random() < p1)); s_.append(int(rng.random() < p2))
        lo, hi = S.newcombe_paired_ci(S.paired_binary(f, s_))
        t = p1 - p2; cov += lo <= t <= hi; below += hi < t; above += lo > t
    print(f"  p1={p1} p2={p2} shock={shock}: coverage {cov/N:.3f}; true above upper {below/N:.3f}, below lower {above/N:.3f}")
print("H4 non-inferiority false support at the margin (true diff = -0.05, rule: lower > -0.05):")
for p2, shock in ((.95, .3), (.90, .5), (.80, .0)):
    p1 = p2 - .05; rng = random.Random(2); fs = 0
    for _ in range(N):
        f, s_ = [], []
        for _ in range(63):
            if rng.random() < shock:
                u = rng.random(); f.append(int(u < p1)); s_.append(int(u < p2))
            else:
                f.append(int(rng.random() < p1)); s_.append(int(rng.random() < p2))
        fs += S.verdict_noninferiority(S.newcombe_paired_ci(S.paired_binary(f, s_)), .05) == S.SUPPORTED
    print(f"  p_B5={p1:.2f} p_B4b={p2}: false support {fs/N:.4f} (nominal ≤ 0.025)")
print("H5b Clopper-Pearson: false support when true scenario-level rate = 0.15 (rule: upper < 0.15), n=63")
rng = random.Random(3); fs = 0
for _ in range(N):
    k = sum(rng.random() < .15 for _ in range(63)); fs += S.clopper_pearson(k, 63)[1] < .15
print(f"  {fs/N:.4f} (nominal ≤ 0.025); max k giving support: {max(k for k in range(64) if S.clopper_pearson(k, 63)[1] < .15)} of 63")
