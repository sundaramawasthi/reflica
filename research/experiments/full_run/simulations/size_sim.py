"""P1 assumption check: type-I error of the H5a sign-flip test (and Wilcoxon) under
null scenarios matching H5a's structure: 11 scenarios, ambiguous nodes
[1,1,1,1,1,1,2,2,2,3,4], 3 repeats averaged. Offline simulation, no data."""
import random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from reflica_bench.stats import sign_flip_test, wilcoxon_signed_rank
AMB = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
R = 3

def binom_mean(rng, n, p):  # mean over repeats of falsely-confident counts, nodes independent
    return sum(sum(rng.random() < p for _ in range(n)) for _ in range(R)) / R

def all_or_nothing(rng, n, q_fail, p_node):  # extraction fails -> all FC, else nodes independent
    tot = 0
    for _ in range(R):
        tot += n if rng.random() < q_fail else sum(rng.random() < p_node for _ in range(n))
    return tot / R

def scenario(name, rng):
    if name == "N1 exchangeable (same process, p=0.4)":
        return [binom_mean(rng, a, .4) - binom_mean(rng, a, .4) for a in AMB]
    if name == "N2 equal means, B5 all-or-nothing vs X independent (0.3)":
        return [all_or_nothing(rng, a, .3, 0) - binom_mean(rng, a, .3) for a in AMB]
    if name == "N3 equal means, B5 deterministic per scenario vs X (0.3)":
        # B5 identical across repeats (deterministic given scenario): FC all repeats w.p. 0.3
        return [(a if rng.random() < .3 else 0) - binom_mean(rng, a, .3) for a in AMB]
    if name == "N4 heterogeneous difficulty, equal per-scenario means":
        out = []
        for a in AMB:
            p = rng.choice([.05, .3, .7, .95])
            out.append(all_or_nothing(rng, a, p, 0) - binom_mean(rng, a, p))
        return out
    if name == "N5 low rate, strongly skewed (0.08)":
        return [all_or_nothing(rng, a, .08, 0) - binom_mean(rng, a, .08) for a in AMB]
    if name == "ALT power: B5 0.1 vs X 0.6":
        return [binom_mean(rng, a, .1) - binom_mean(rng, a, .6) for a in AMB]
    if name == "ALT power: B5 0.3 vs X 0.6":
        return [binom_mean(rng, a, .3) - binom_mean(rng, a, .6) for a in AMB]
    raise KeyError(name)

NAMES = ["N1 exchangeable (same process, p=0.4)", "N2 equal means, B5 all-or-nothing vs X independent (0.3)",
         "N3 equal means, B5 deterministic per scenario vs X (0.3)", "N4 heterogeneous difficulty, equal per-scenario means",
         "N5 low rate, strongly skewed (0.08)", "ALT power: B5 0.1 vs X 0.6", "ALT power: B5 0.3 vs X 0.6"]
if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    print(f"{N} simulations each; rejection rate (one-sided in the direction B5 < X is not required: two-sided tests)")
    print(f"{'scenario':60s} {'SF a=.05':>9s} {'SF a=.01':>9s} {'W a=.05':>9s} {'W a=.01':>9s} {'MC se(.05)':>10s}")
    for name in NAMES:
        rng = random.Random(20261010)
        sf5 = sf1 = w5 = w1 = 0
        for _ in range(N):
            d = scenario(name, rng)
            p = sign_flip_test(d).p_two_sided; q = wilcoxon_signed_rank(d).p_two_sided
            sf5 += p < .05; sf1 += p < .01; w5 += q < .05; w1 += q < .01
        se = (0.05 * 0.95 / N) ** .5
        print(f"{name:60s} {sf5/N:9.4f} {sf1/N:9.4f} {w5/N:9.4f} {w1/N:9.4f} {se:10.4f}")
