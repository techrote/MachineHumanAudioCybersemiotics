"""Mergedown #607: independent literal four-survivor enumeration, synthetic only.
Requires Python 3.10+ and NumPy; no network, no upstream imports or human data.
"""
import itertools as it
import json
import numpy as np

GRAMMAR = '0fe95f804a20a8f3a6e59a2f8089d8b83f438204'
MEASUREMENT = 'ed648880b0588b2852a0b691a8f603a2a0a49a13'
KINDS = ('ack', 'terminal', 'quote', 'certificate')
EXPECTED = np.array([[5361100,583915,506745,5024795],
                     [583915,5361100,503530,5020455],
                     [506745,503530,3814360,5955700],
                     [5024795,5020455,5955700,99421870]], dtype=np.int64)
EXPECTED_BOUND = [254990,254990,250330,9992230]


def expressions(n):
    if n == 1:
        yield from ((x,) for x in (0,1,2,3,14))
    elif n > 1:
        for x, tail in it.product(range(4,11), expressions(n-1)):
            yield (x,) + tail
        for left in range(1,n-1):
            for x,a,b in it.product((11,12), expressions(left), expressions(n-1-left)):
                yield (x,) + a + b


def catalogue():
    radix = 17 ** np.arange(3,-1,-1)
    occupied = {int(np.dot(e+(13,)*(4-n),radix))
                for n in range(1,5) for e in expressions(n)}
    assert len(occupied) == 3100
    free = np.array([k for k in range(4913,13*4913) if k not in occupied])
    assert len(free) == 55858
    ids = np.concatenate((np.arange(3840),14*4913+np.arange(3840),
                          free[36480:40320],free[:36480]))
    kinds = np.repeat(np.arange(4),[3840,3840,3840,36480])
    addresses = np.concatenate([np.repeat(np.arange(192),n) for n in (20,20,20,190)])
    # Enumerate all degree <=3 polynomial coefficients instead of interpolating.
    coeff = np.array(list(it.product(range(17),repeat=4)))
    values = coeff @ (np.arange(8)[None,:] ** np.arange(4)[:,None]) % 17
    systematic = values[:,[0,1,4,5]] @ radix
    assert len(np.unique(systematic)) == 17**4
    words = values[np.argsort(systematic)[ids]]
    h = g = 0
    for v in words.ravel().tolist():
        h = (h*31+v+1)%1000000007
        g = (g*37+v+1)%1000000009
    assert (h,g) == (95787044,408117442)
    return words,kinds,addresses,radix


def main():
    words,kinds,addresses,radix = catalogue()
    matrix = np.zeros((4,4),dtype=np.int64)
    bound = matrix.copy()
    per_mask = []
    attempts = 0
    for positions in it.combinations(range(8),4):
        obs = words[:,positions]
        keys = obs @ radix
        assert len(np.unique(keys)) == len(words)
        lookup = np.full(17**4,-1,dtype=np.int32)
        lookup[keys] = np.arange(len(words))
        cell = matrix.copy()*0
        local_bound = cell.copy()
        # For each surviving symbol, explicitly replace it by all 16 alternatives.
        for j in range(4):
            for delta in range(1,17):
                damaged = keys + ((obs[:,j]+delta)%17-obs[:,j])*radix[j]
                got = lookup[damaged]
                good = got >= 0
                src = np.flatnonzero(good)
                dst = got[good]
                assert np.all(src != dst)
                cell += np.bincount(kinds[src]*4+kinds[dst],minlength=16).reshape(4,4)
                same = addresses[src] == addresses[dst]
                local_bound += np.bincount(kinds[src[same]]*4+kinds[dst[same]],minlength=16).reshape(4,4)
                attempts += len(words)
        matrix += cell
        bound += local_bound
        per_mask.append({'survivors':positions,'wrong':int(cell.sum()),'same_address':int(local_bound.sum())})
    assert attempts == 215040000
    assert np.array_equal(matrix,EXPECTED)
    assert bound.diagonal().tolist() == EXPECTED_BOUND
    assert np.array_equal(matrix,matrix.T)
    # Exact published witness: first certificate becomes ACK index 21.
    assert words[11520].tolist() == [1,0,15,10,0,0,8,5]
    assert words[21,:4].tolist() == [0,0,15,10]
    data = {'grammar':GRAMMAR,'measurement':MEASUREMENT,'numpy':np.__version__,
            'attempts':attempts,'kinds':KINDS,'matrix':matrix.tolist(),
            'same_address_matrix':bound.tolist(),'accepted':int(matrix.sum()),
            'cross_kind':int(matrix.sum()-matrix.trace()),'rejected':attempts-int(matrix.sum()),
            'per_mask':per_mask,'scope':'literal finite symbol faults; no channel probability, PCM or human evidence'}
    print(json.dumps(data,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
