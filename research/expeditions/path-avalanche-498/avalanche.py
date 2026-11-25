"""Exact one-grain receipts for a path with two absorbing ends (synthetic)."""
from math import gcd


_UNSET = object()


def validate(n, i, h=_UNSET):
    if type(n) is not int or not 1 <= n <= 4096:
        raise ValueError('path length must be 1..4096')
    if type(i) is not int or not 1 <= i <= n:
        raise ValueError('injection site must be 1..n')
    if h is not _UNSET and (type(h) is not int or not 0 <= h <= n):
        raise ValueError('hole must be 0..n')


def receipt(n, i, h):
    """h=0 denotes all ones; otherwise h is the only empty site."""
    validate(n, i, h)
    m = n + 1
    if h == i:
        u = [0] * n
    else:
        left, right = (0, m) if h == 0 else ((0, h) if i < h else (h, m))
        u = [max(0, min(j-left, right-j, i-left, right-i))
             for j in range(1, m)]
    return {'next': (h-i) % m, 'odometer': u, 'count': sum(u),
            'left': u[0], 'right': u[-1]}


def count(n, i, h):
    validate(n, i, h)
    return (n+1-i)*(i-h) if h < i else i*(h-i)


def candidates(n, i, total, left=None, right=None, second=None, second_site=None):
    """Return all initial holes consistent with exact optional receipts."""
    validate(n, i)
    if type(total) is not int or total < 0:
        raise ValueError('invalid count')
    if any(v is not None and (type(v) is not int or v not in (0, 1))
           for v in (left, right)):
        raise ValueError('invalid end loss')
    if second is not None and (type(second) is not int or second < 0):
        raise ValueError('invalid second count')
    if second_site is not None:
        validate(n, second_site)
        if second is None:
            raise ValueError('second site requires second count')
    j = i if second_site is None else second_site
    m = n+1
    hs = set()
    if total % (m-i) == 0:
        hs.add(i-total//(m-i))
    if total % i == 0:
        hs.add(i+total//i)
    result = []
    for h in sorted(hs):
        if not 0 <= h <= n or count(n, i, h) != total:
            continue
        l, r = int(h == 0 or h > i), int(h < i)
        if left is not None and l != left or right is not None and r != right:
            continue
        if second is not None and count(n, j, (h-i) % m) != second:
            continue
        result.append(h)
    return result


def collision_pairs(n, i):
    validate(n, i)
    m = n+1
    g = gcd(m, i)
    return [(i-i*k//g, i+(m-i)*k//g) for k in range(1, g)]


def plan(n, i, total):
    """Minimum further count-only probes, assuming an exact first count.

    A noncentral repeated probe is enough. At the centre use site 1.
    Empty candidate sets are inconsistent, not requests for further probes.
    """
    hs = candidates(n, i, total)
    return {'candidates': hs, 'status': 'inconsistent' if not hs else
            'unique' if len(hs) == 1 else 'ambiguous',
            'next_site': (1 if 2*i == n+1 else i) if len(hs) == 2 else None}
