"""Tail probabilities and quantiles for the t, F and chi-squared distributions.

Standard library only, so the service needs no SciPy. Built on the regularized
incomplete beta and gamma functions (continued fractions, modified Lentz;
Numerical Recipes 3rd ed., §6.2 and §6.4). Accuracy is checked against R in
`tests/service/test_distributions.py`. Relative error in tail probabilities
was about 1e-12 for df <= 200, 5e-12 for df <= 1000 and 5e-10 near df = 1e5
(differences of large `lgamma` values lose digits); every reported p-value is
therefore accurate to far more digits than are meaningful.
"""
from __future__ import annotations

import math

_EPS = 1e-16
_TINY = 1e-300
_MAX_ITER = 100_000


def _betacf(a: float, b: float, x: float) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > _TINY else _TINY)
    h = d
    for m in range(1, _MAX_ITER):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = 1.0 + aa / c
        c = c if abs(c) > _TINY else _TINY
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = 1.0 + aa / c
        c = c if abs(c) > _TINY else _TINY
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def betainc(a: float, b: float, x: float, y: float | None = None) -> float:
    """Regularized incomplete beta I_x(a, b) for a, b > 0 and 0 <= x <= 1.

    `y` = 1 - x may be passed when it is known more accurately than 1 - x.
    The continued fraction is evaluated where it converges fast, and the
    result is never formed by subtracting from 1 when it is small.
    """
    if y is None:
        y = 1.0 - x
    if not (a > 0 and b > 0 and 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        raise ValueError("betainc needs a, b > 0 and 0 <= x <= 1")
    if x == 0.0 or y == 0.0:
        return 0.0 if x == 0.0 else 1.0
    log_front = (a * math.log(x) + b * math.log(y)
                 - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(log_front) * _betacf(a, b, x) / a
    return 1.0 - math.exp(log_front) * _betacf(b, a, y) / b


def gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x) for a > 0, x >= 0."""
    if not (a > 0 and x >= 0):
        raise ValueError("gammaincc needs a > 0 and x >= 0")
    if x == 0.0:
        return 1.0
    log_front = -x + a * math.log(x) - math.lgamma(a)
    if x < a + 1.0:  # series for P, then Q = 1 - P (Q is not small here)
        ap, s = a, 1.0 / a
        term = s
        for _ in range(_MAX_ITER):
            ap += 1.0
            term *= x / ap
            s += term
            if abs(term) < abs(s) * _EPS:
                return 1.0 - s * math.exp(log_front)
        raise ArithmeticError("incomplete gamma series did not converge")
    b = x + 1.0 - a
    c, d = 1.0 / _TINY, 1.0 / b
    h = d
    for i in range(1, _MAX_ITER):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = b + an / c
        c = c if abs(c) > _TINY else _TINY
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            return math.exp(log_front) * h
    raise ArithmeticError("incomplete gamma continued fraction did not converge")


def t_sf2(t: float, df: float) -> float:
    """Two-sided p-value P(|T| >= |t|) for Student's t with df degrees of freedom."""
    if not df > 0:
        raise ValueError("df must be positive")
    t2 = t * t
    if math.isinf(t2):
        return 0.0
    # p = I_x(df/2, 1/2) with x = df/(df+t^2); 1 - p = I_(1-x)(1/2, df/2).
    # Evaluate whichever is the smaller tail so it is never formed as 1 - (almost 1).
    x, y = df / (df + t2), t2 / (df + t2)
    a, b = df / 2.0, 0.5
    if x < (a + 1.0) / (a + b + 2.0):
        return min(1.0, betainc(a, b, x, y))
    return min(1.0, 1.0 - betainc(b, a, y, x))


def f_sf(f: float, df1: float, df2: float) -> float:
    """Upper-tail probability P(F >= f) for the F(df1, df2) distribution."""
    if not (df1 > 0 and df2 > 0):
        raise ValueError("degrees of freedom must be positive")
    if f <= 0:
        return 1.0
    if math.isinf(f):
        return 0.0
    denom = df2 + df1 * f
    x, y = df2 / denom, df1 * f / denom
    a, b = df2 / 2.0, df1 / 2.0
    if x < (a + 1.0) / (a + b + 2.0):
        return betainc(a, b, x, y)
    return 1.0 - betainc(b, a, y, x)


def chi2_sf(x: float, df: float) -> float:
    """Upper-tail probability P(X >= x) for chi-squared with df degrees of freedom."""
    if not df > 0:
        raise ValueError("df must be positive")
    if x <= 0:
        return 1.0
    if math.isinf(x):
        return 0.0
    return gammaincc(df / 2.0, x / 2.0)


def t_ppf_upper(alpha: float, df: float) -> float:
    """t such that P(T >= t) = alpha, for 0 < alpha <= 0.5 (so t >= 0).

    Bisection on the tail probability to the limit of floating-point resolution:
    slow-ish (~60 tail evaluations) but monotone and robust for every df.
    """
    if not (0.0 < alpha <= 0.5) or not df > 0:
        raise ValueError("t_ppf_upper needs 0 < alpha <= 0.5 and df > 0")
    if alpha == 0.5:
        return 0.0
    target = 2.0 * alpha  # two-sided
    lo, hi = 0.0, 1.0
    while t_sf2(hi, df) > target:
        lo, hi = hi, hi * 2.0
        if hi > 1e300:
            raise ArithmeticError("t quantile out of range")
    for _ in range(2000):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if t_sf2(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
