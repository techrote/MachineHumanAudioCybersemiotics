"""Synthetic C3 cross-check and original stereo score; Python standard library."""
from collections import deque
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
import struct
import wave

A = {'a': (1, 2, 0), 'b': (0, 1, 0)}
Q = frozenset(range(3))
PAIRS = frozenset(combinations(Q, 2))


def image(word):
    states = Q
    for c in word:
        states = frozenset(A[c][s] for s in states)
    return states


def successors(state, c):
    S, P = state
    f = A[c]
    s = tuple(frozenset(f[x] for x in level) | (S[j-1] if j else frozenset())
              for j, level in enumerate(S))
    p = tuple(frozenset(tuple(sorted((f[x], f[y]))) for x, y in level if f[x] != f[y])
              | (P[j-1] if j else frozenset()) for j, level in enumerate(P))
    return s, p


def frontier(d):
    start = ((Q,) * (d+1), (PAIRS,) * (d+1))
    queue = deque([(start, '')])
    seen = {start}
    out = {}
    while queue:
        state, w = queue.popleft()
        s, p = state
        if not p[-1]:
            for cap in range(len(s[-1]), 4):
                out.setdefault(str(cap), {'length': len(w), 'word': w})
        for c in A:
            t = successors(state, c)
            if t not in seen:
                seen.add(t)
                queue.append((t, w+c))
    return {'budget': d, 'frontier': out, 'closed_states': len(seen)}


def render(path, left, right):
    # Two copies begin on distinct pitches; each slot shows current state.
    rate, slot = 8000, 800
    data = bytearray()
    for l, r in zip(left, right):
        for i in range(slot):
            env = min(1, i/64, (slot-1-i)/64)
            data.extend(struct.pack('<hh', *(round(9000*env*math.sin(2*math.pi*(220+110*s)*i/rate)) for s in (l,r))))
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
        f.writeframes(data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(word, deleted, initial):
    t = [initial]
    for i, c in enumerate(word):
        t.append(t[-1] if i in deleted else A[c][t[-1]])
    return t


def main():
    out = Path(__file__).resolve().parent
    rows = [frontier(d) for d in range(11)]
    checks = 0
    for n in range(11):
        for w0 in product(A, repeat=n):
            w = ''.join(w0)
            state = ((Q,)*3, (PAIRS,)*3)
            for c in w:
                state = successors(state, c)
            for d in range(3):
                results = [image(''.join(c for i,c in enumerate(w) if i not in cut))
                           for k in range(min(n,d)+1) for cut in combinations(range(n),k)]
                assert state[0][d] == frozenset().union(*results)
                assert (not state[1][d]) == all(len(s)==1 for s in results)
                checks += 1
    for d,row in enumerate(rows):
        assert row['frontier']['3']['length'] == 4*(d+1)
        if d >= 2:
            assert '1' not in row['frontier']
            assert row['frontier']['2']['length'] == 5*d+4
    # The two tracks have different initial states. Shared or independent
    # omissions are represented by holding the state for an omitted slot.
    w = 'baab'*3
    left = trace(w, set(), 0)
    right_shared = trace(w, set(), 2)
    right_independent = trace(w, {len(w)-2}, 2)
    assert left[-1] == right_shared[-1] == 0
    assert right_independent[-1] == 1
    receipt = {'joint_frontier':rows, 'direct_deletion_checks':checks,
               'score_word':w, 'traces':{'left':left,'shared':right_shared,'independent':right_independent},
               'audio_sha256':{}}
    for name, right in [('shared',right_shared),('independent',right_independent)]:
        receipt['audio_sha256'][name+'.wav'] = render(out/(name+'.wav'),left,right)
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
