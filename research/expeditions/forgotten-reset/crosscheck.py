"""Independent set-based search; compare labelled census against reset.mjs."""
from collections import deque, Counter
from itertools import product
import json


def shortest(maps, k):
    q = frozenset(range(len(maps[0])))
    start = (q,) * (k + 1)
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        sets, d = queue.popleft()
        if len(sets[-1]) == 1:
            return d
        for f in maps:
            child = tuple(frozenset(f[x] for x in s) | (sets[i-1] if i else frozenset())
                          for i, s in enumerate(sets))
            if child not in seen:
                seen.add(child)
                queue.append((child, d+1))
    return None


def census(n):
    maps = list(product(range(n), repeat=n))
    hist = Counter()
    for pair in product(maps, repeat=2):
        a = shortest(pair, 0)
        if a is not None:
            b = shortest(pair, 1)
            hist[f'{a}:{b if b is not None else "impossible"}'] += 1
    return dict(hist)


if __name__ == '__main__':
    print(json.dumps({n: census(n) for n in (2, 3, 4)}, sort_keys=True, indent=2))
