"""Exact finite-vector summation-tree laboratory; synthetic, not a production mixer."""
from collections import Counter
from itertools import combinations


class BudgetExceeded(RuntimeError):
    """Search incomplete; never an infeasibility certificate."""


def validate(vectors, limit=14):
    v = tuple(tuple(row) for row in vectors)
    if not 1 <= len(v) <= limit or not v[0] or any(len(r) != len(v[0]) for r in v):
        raise ValueError('nonempty rectangular matrix within leaf limit required')
    if any(type(x) is not int for r in v for x in r):
        raise ValueError('integer coordinates required')
    if (1 << len(v)) * len(v[0]) > 4_000_000:
        raise BudgetExceeded('subset coordinate budget')
    return v


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def norm(a):
    return max(map(abs, a))


def splits(mask):
    """Unordered nonempty bipartitions, once each, anchored at low bit."""
    anchor = mask & -mask
    rest = mask ^ anchor
    s = rest
    while s:
        yield mask ^ s, s
        s = (s - 1) & rest


def subset_sums(v):
    sums = [(0,) * len(v[0])]
    for mask in range(1, 1 << len(v)):
        bit = mask & -mask
        sums.append(add(sums[mask ^ bit], v[bit.bit_length() - 1]))
    return sums


def optimal(vectors, sequential=False):
    """Minimize peak infinity norm of *exact* sums at all tree nodes.

    sequential=True restricts to a left-deep tree, allowing arbitrary order.
    Returns exact optimal peak and one labelled witness tree (int or pair).
    """
    v = validate(vectors)
    sums = subset_sums(v)
    cost, tree = [0] * len(sums), [None] * len(sums)
    for mask in range(1, len(sums)):
        if mask & (mask - 1) == 0:
            cost[mask], tree[mask] = norm(sums[mask]), mask.bit_length() - 1
            continue
        if sequential:
            pairs = ((mask ^ (1 << j), 1 << j) for j in range(len(v)) if mask & (1 << j))
        else:
            pairs = splits(mask)
        best = min((max(cost[a], cost[b]), a, b) for a, b in pairs)
        c, a, b = best
        cost[mask] = max(norm(sums[mask]), c)
        tree[mask] = (tree[a], tree[b])
    return cost[-1], tree[-1]


def evaluate(vectors, tree, cap=None):
    """Replay a tree; cap None is exact, otherwise symmetric saturation.

    Returns output, peak before saturation and number of clipping nodes.
    Rejects missing/duplicate leaves and out-of-range input under a cap.
    """
    v = validate(vectors)
    if cap is not None and (type(cap) is not int or cap < 0 or any(norm(r) > cap for r in v)):
        raise ValueError('nonnegative integer cap must contain every leaf')
    seen = []
    def visit(t):
        if type(t) is int:
            if not 0 <= t < len(v):
                raise ValueError('invalid leaf')
            seen.append(t)
            return v[t], norm(v[t]), 0
        if not isinstance(t, (tuple, list)) or len(t) != 2:
            raise ValueError('binary tree required')
        a, p, c = visit(t[0]); b, q, d = visit(t[1])
        z = add(a, b); peak = norm(z)
        if cap is not None:
            z = tuple(max(-cap, min(cap, x)) for x in z)
        return z, max(p, q, peak), c + d + int(cap is not None and peak > cap)
    out = visit(tree)
    if sorted(seen) != list(range(len(v))):
        raise ValueError('tree must use every labelled leaf once')
    return out


def endpoints(vectors, cap, pair_budget=2_000_000, state_budget=200_000):
    """Count final vectors over all labelled unordered binary trees.

    Distinct tree topologies are counted, not sampled. Counts are not probabilities.
    Raises BudgetExceeded rather than returning an incomplete histogram.
    """
    v = validate(vectors, limit=10)
    if type(cap) is not int or cap < 0 or any(norm(r) > cap for r in v):
        raise ValueError('nonnegative integer cap must contain every leaf')
    if any(type(x) is not int or x < 1 for x in (pair_budget, state_budget)):
        raise ValueError('positive integer budgets required')
    dp = [None] * (1 << len(v)); pairs = states = 0
    for mask in range(1, len(dp)):
        h = Counter()
        if mask & (mask - 1) == 0:
            h[v[mask.bit_length() - 1]] = 1
        else:
            for a, b in splits(mask):
                for x, cx in dp[a].items():
                    for y, cy in dp[b].items():
                        pairs += 1
                        if pairs > pair_budget:
                            raise BudgetExceeded('endpoint pair budget')
                        z = tuple(max(-cap, min(cap, u+w)) for u, w in zip(x, y))
                        h[z] += cx * cy
                        if len(h) + states > state_budget:
                            raise BudgetExceeded('endpoint state budget')
        states += len(h)
        if states > state_budget:
            raise BudgetExceeded('endpoint state budget')
        dp[mask] = h
    return dp[-1]


def balanced_family(n):
    """One coordinate for every balanced sign column modulo sign reversal."""
    if type(n) is not int or n < 2 or n % 2 or n > 14:
        raise ValueError('even n in 2..14 required')
    cols = [{0, *s} for s in combinations(range(1, n), n//2-1)]
    return tuple(tuple(1 if i in c else -1 for c in cols) for i in range(n))
