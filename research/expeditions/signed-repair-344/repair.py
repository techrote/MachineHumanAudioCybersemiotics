"""Exact signed circular two-tap repair. Standard library, synthetic only."""
from fractions import Fraction as F


def conv(a, b):
    if len(a) != len(b) or not a:
        raise ValueError('equal nonempty circular grids required')
    n = len(a)
    return tuple(sum(a[j] * b[(i-j) % n] for j in range(n)) for i in range(n))


def norm(a):
    return sum(map(abs, a))


def delta(n):
    return (F(1),) + (F(0),) * (n-1)


def plan(n, q, budget):
    """q in [0,1/2], budget >= 0; return exact witness and certificate."""
    q, budget = F(q), F(budget)
    if type(n) is not int or n < 2 or not 0 <= q <= F(1,2) or budget < 0:
        raise ValueError('invalid grid, blur or budget')
    d = delta(n)
    h = (1-q, q) + (F(0),) * (n-2)
    if q == 0 or (q == F(1,2) and n % 2 == 0):
        return dict(h=h, g=d, inverse=d if q == 0 else None,
                    required=F(0) if q == 0 else None, residual=2*q, dual=None)
    p = 1-q
    r = q/p
    b = tuple((-r)**k/(p*(1-(-r)**n)) for k in range(n))
    L = norm(b)
    required = (L-1)/2
    lam = min(F(1), budget/required)
    g = tuple((1-lam)*x+lam*y for x,y in zip(d,b))
    # t[j] = <sign(b), shift_j(b)>; certificate on sum-zero residuals.
    t = tuple(sum((-1)**i * b[(i-j)%n] for i in range(n)) for j in range(n))
    return dict(h=h, g=g, inverse=b, required=required,
                residual=2*q*(1-lam), dual=t)
