"""False 'Supported' / 'Contradicted' rate of the full H5a verdict rule
(sign-flip p < α AND bootstrap CI excludes 0, same direction) under null scenarios."""
import random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from size_sim import AMB, scenario, binom_mean, all_or_nothing
from reflica_bench.stats import sign_flip_test, bootstrap_ci

def n3_reverse(rng):  # X deterministic all-or-nothing, B5 independent (opposite skew)
    return [binom_mean(rng, a, .3) - (a if rng.random() < .3 else 0) for a in AMB]

def n3_p(p):
    return lambda rng: [(a if rng.random() < p else 0) - binom_mean(rng, a, p) for a in AMB]

CASES = {"N3 B5 deterministic, p=0.3": n3_p(.3), "N3 p=0.1": n3_p(.1), "N3 p=0.5": n3_p(.5),
         "N3 reversed (X deterministic), p=0.3": n3_reverse,
         "N1 exchangeable": lambda rng: scenario("N1 exchangeable (same process, p=0.4)", rng)}
N, B = int(sys.argv[1]), int(sys.argv[2])
units = list(range(len(AMB)))
print(f"{N} sims, {B} bootstrap resamples; alpha = Holm first step 0.01 and last step 0.05")
print(f"{'case':42s} {'sign-flip p<.01: B5 better / worse':>36s} {'full rule α=.01: Sup / Contra':>30s} {'full rule α=.05: Sup / Contra':>30s}")
for name, gen in CASES.items():
    rng = random.Random(7)
    t_b = t_w = s1 = c1 = s5 = c5 = 0
    for i in range(N):
        d = gen(rng)
        r = sign_flip_test(d)
        tot = sum(AMB)
        lo, hi = bootstrap_ci(units, ["c7"] * len(units), lambda smp: sum(d[j] for j in smp) / sum(AMB[j] for j in smp), n_boot=B, seed=i)
        neg, pos = hi < 0, lo > 0
        if r.p_two_sided < .01:
            t_b += r.statistic < 0; t_w += r.statistic > 0
        s1 += r.p_two_sided < .01 and neg and r.statistic < 0; c1 += r.p_two_sided < .01 and pos and r.statistic > 0
        s5 += r.p_two_sided < .05 and neg and r.statistic < 0; c5 += r.p_two_sided < .05 and pos and r.statistic > 0
    print(f"{name:42s} {t_b/N:17.4f} / {t_w/N:<16.4f} {s1/N:14.4f} / {c1/N:<13.4f} {s5/N:14.4f} / {c5/N:<13.4f}")
