"""Exact shared-input integer carry banks; no hardware or perceptual claims."""
from math import gcd
from functools import reduce


def phases(M, n):
    if type(M) is not int or type(n) is not int or M < 2 or n < 1:
        raise ValueError('need integer M >= 2 and n >= 1')
    return tuple(j*M//n for j in range(n))


def run(M, initial, inputs):
    """Return successive tuples of individual carries; initial phases not mutated."""
    s = list(initial)
    if type(M) is not int or M < 2 or not s or any(type(x) is not int or not 0 <= x < M for x in s):
        raise ValueError('invalid phases')
    for a in inputs:
        if type(a) is not int or not 0 <= a <= M:
            raise ValueError('invalid input increment')
        qr = [divmod(x+a, M) for x in s]
        yield tuple(q for q, _ in qr)
        s = [r for _, r in qr]


def erasure_bounds(M, n, a, e):
    """Sharp universal min/max survivor carries for residue a (not full turns)."""
    phases(M, n)
    if type(a) is not int or not 0 <= a < M or type(e) is not int or not 0 <= e < n:
        raise ValueError('invalid residue or erasure count')
    return max(0, n*a//M-e), min(n-e, (n*a+M-1)//M)


def exact_contract(M, increments):
    """Minimum bank size giving exact aggregate counts for all listed increments/rotations."""
    if type(M) is not int or M < 2:
        raise ValueError('invalid modulus')
    A = tuple(increments)
    if any(type(a) is not int or not 0 <= a <= M for a in A):
        raise ValueError('invalid increment')
    g = reduce(gcd, A, M)
    return M//g
