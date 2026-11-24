"""Exact set-valued credit inspector for partial pair audits."""
from itertools import product
from lab import PAIRS, credit


def inspect(bits):
    """Six entries in AB AC AD BC BD CD order; None = unqueried."""
    if len(bits) != 6 or any(x is not None and (type(x) is not int or x not in (0, 1)) for x in bits):
        raise ValueError('expected six values in {0,1,None}')
    # Use integer twelfths, preserving the joint set instead of just intervals.
    possible = lambda x: (0, 1) if x is None else (x,)
    diffs = [sorted({a-b for a in possible(bits[i]) for b in possible(bits[5-i])})
             for i in range(3)]
    vectors = sorted((3+x+y+z, 3+x-y-z, 3-x+y-z, 3-x-y+z)
                     for x,y,z in product(*diffs))
    k = bits.count(None)
    return {'candidate_graphs': 2**k, 'credit_vectors_twelfths': vectors,
            'coordinate_intervals_twelfths': [(min(v[i] for v in vectors), max(v[i] for v in vectors))
                                              for i in range(4)]}


def verify():
    count = 0
    all_vectors = [tuple(int(c*12) for c in credit(g)) for g in range(64)]
    for bits in product((0,1,None), repeat=6):
        r = inspect(bits)
        graphs = [g for g in range(64) if all(b is None or b == ((g >> j) & 1) for j,b in enumerate(bits))]
        vectors = sorted(set(all_vectors[g] for g in graphs))
        assert r['candidate_graphs'] == len(graphs)
        assert r['credit_vectors_twelfths'] == vectors
        assert all(hi-lo == bits.count(None) for lo,hi in r['coordinate_intervals_twelfths'])
        assert (len(vectors) == 1) == (None not in bits)
        count += 4
    for bad in ([None]*5, [None]*7, [2]*6, [True]*6, ['?']*6):
        try:
            inspect(bad)
        except ValueError:
            count += 1
        else:
            raise AssertionError('invalid audit accepted')
    return count


if __name__ == '__main__':
    print('partial audit assertions:', verify())
    print(inspect((1,None,1,None,0,None)))
