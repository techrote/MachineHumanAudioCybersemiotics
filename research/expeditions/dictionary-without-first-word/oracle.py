"""Exact fictional graph-alignment model; Python 3.11+, standard library."""
from collections import Counter
from itertools import combinations, permutations
from functools import lru_cache
import argparse
import json
import struct
import wave
from pathlib import Path


@lru_cache(None)
def geometry(n):
    if type(n) is not int or not 1 <= n <= 6:
        raise ValueError('n must be 1..6')
    edges = tuple(combinations(range(n), 2))
    idx = {e: i for i, e in enumerate(edges)}
    return edges, tuple((p, tuple(idx[tuple(sorted((p[a], p[b])))]
                                   for a, b in edges)) for p in permutations(range(n)))


def images(n, mask):
    edges, maps = geometry(n)
    if type(mask) is not int or not 0 <= mask < 1 << len(edges):
        raise ValueError('invalid edge mask')
    bits = [i for i in range(len(edges)) if mask >> i & 1]
    return [(p, sum(1 << remap[i] for i in bits)) for p, remap in maps]


def automorphisms(n, mask):
    return [p for p, m in images(n, mask) if m == mask]


def candidates(n, abstract, physical, anchors=()):
    edges, _ = geometry(n)
    if type(physical) is not int or not 0 <= physical < 1 << len(edges):
        raise ValueError('invalid physical edge mask')
    anchors = tuple(anchors)
    if any(type(a) is not int or type(b) is not int or not (0 <= a < n and 0 <= b < n)
           for a, b in anchors):
        raise ValueError('invalid anchor')
    return [p for p, m in images(n, abstract) if m == physical
            and all(p[a] == b for a, b in anchors)]


def determining(n, autos):
    # Exact by hitting the moved support of every nonidentity automorphism.
    supports = {sum(1 << i for i in range(n) if p[i] != i) for p in autos} - {0}
    for k in range(n + 1):
        found = [s for s in combinations(range(n), k)
                 if all(sum(1 << i for i in s) & t for t in supports)]
        if found:
            return found
    raise AssertionError('full vertex set must work')


def mask_of(n, edges):
    all_edges, _ = geometry(n)
    return sum(1 << all_edges.index(e) for e in {tuple(sorted(e)) for e in edges})


def census(n):
    edges, _ = geometry(n)
    unseen = set(range(1 << len(edges)))
    labeled, classes, twinless = Counter(), Counter(), Counter()
    rigid = 0
    while unseen:
        m = min(unseen)
        im = images(n, m)
        orbit = {v for _, v in im}
        autos = [p for p, v in im if v == m]
        assert len(orbit) * len(autos) == len(im)
        assert orbit <= unseen
        unseen.difference_update(orbit)
        bases = determining(n, autos)
        k = len(bases[0])
        labeled[k] += len(orbit)
        classes[k] += 1
        # A transposition automorphism swaps a pair of twins.
        if not any(sum(a != b for a, b in enumerate(p)) == 2 for p in autos):
            twinless[k] += len(orbit)
        if len(autos) == 1:
            rigid += len(orbit)
    assert sum(labeled.values()) == 1 << len(edges)
    assert rigid == labeled[0]
    return {'n': n, 'labeled': dict(sorted(labeled.items())),
            'classes': dict(sorted(classes.items())), 'twinless_labeled': dict(sorted(twinless.items()))}


def action_values(maps, symbol, action=lambda x: x):
    return {action(p[symbol]) for p in maps}


def pcm(notes):
    # Integer square-wave motifs, 8 kHz mono, 0.1 sec per note.
    return b''.join(struct.pack('<h', 5000 if (t * (220 + 55 * note) // 4000) % 2 == 0 else -5000)
                    for note in notes for t in range(800))


def sonic_witness(out=None):
    n = 5
    edges, _ = geometry(n)
    m = mask_of(n, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])
    maps = candidates(n, m, m, [(0, 0)])
    assert len(maps) == 2
    a, b = maps
    abstract_notes = [v for i, e in enumerate(edges) if m >> i & 1 for v in e]
    relational = [pcm(abstract_notes) for _ in maps]
    anchored = [pcm([p[1]]) for p in maps]
    assert relational[0] == relational[1] and anchored[0] != anchored[1]
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        for name, raw in [('relations-a', relational[0]), ('relations-b', relational[1]),
                          ('target-a', anchored[0]), ('target-b', anchored[1])]:
            with wave.open(str(out / (name + '.wav')), 'wb') as w:
                w.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
                w.writeframes(raw)
    return {'remaining_maps': [list(a), list(b)], 'relation_pcm_equal': True,
            'target_pcm_equal': False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--wav-dir', type=Path)
    args = p.parse_args()
    print(json.dumps({'census': [census(n) for n in range(1, 7)],
                      'sonic_witness': sonic_witness(args.wav_dir)}, sort_keys=True))


if __name__ == '__main__':
    main()
