"""Synthetic anonymous two-message adder channel. Standard library only."""
from itertools import combinations, combinations_with_replacement
from collections import defaultdict
import argparse, hashlib, json, math, struct, wave
from pathlib import Path

def parity(x):
    return x.bit_count() & 1


def receipt(a, b, rows):
    return tuple(parity(a & r) + parity(b & r) for r in rows)


def partitions(m):
    return [(u, v) for u in range(1, 1 << m) for v in range(u + 1, 1 << m) if not u & v]


def distance(rows, u, v):
    return sum(parity(r & u) * parity(r & v) for r in rows)


def exact_cover(m):
    cuts = partitions(m)
    candidates = [r for r in range(1, 1 << m) if r.bit_count() >= 2]
    covers = [sum(1 << i for i, (u, v) in enumerate(cuts) if distance([r], u, v)) for r in candidates]
    target = (1 << len(cuts)) - 1
    suffix = [0] * (len(covers) + 1)
    for i in range(len(covers) - 1, -1, -1):
        suffix[i] = suffix[i + 1] | covers[i]
    visited = 0
    def search(start, budget, mask):
        nonlocal visited
        visited += 1
        if mask == target:
            return []
        if budget == 0 or len(covers) - start < budget or (mask | suffix[start]) != target:
            return None
        for j in range(start, len(covers) - budget + 1):
            new = mask | covers[j]
            if new == mask:
                continue
            tail = search(j + 1, budget - 1, new)
            if tail is not None:
                return [candidates[j]] + tail
        return None
    for k in range(1, len(candidates) + 1):
        witness = search(0, k, 0)
        if witness is not None:
            return dict(m=m, cuts=len(cuts), candidates=len(candidates), optimum=k,
                        witness=witness, search_nodes=visited)
    raise AssertionError('complete graph should work')


def graph_one_error(s):
    # Cycle (parallel edges for s=2) plus antipodal chords covering every vertex.
    return [(1 << i) | (1 << ((i + 1) % s)) for i in range(s)] + [
        (1 << i) | (1 << ((i + s // 2) % s)) for i in range((s + 1) // 2)]


def hamming_rows(k):
    r = 1
    while (1 << r) < k + r + 1:
        r += 1
    checks = [x for x in range(1, 1 << r) if x.bit_count() >= 2][:k]
    rows = [1 << i for i in range(k)]
    rows += [sum(1 << i for i, c in enumerate(checks) if c & (1 << j)) for j in range(r)]
    # Map bit i to relative orientation between anchor 0 and coordinate i+1.
    return [(q << 1) | parity(q) for q in rows]


def qualify():
    out = dict(optima=[], raw_fibres=0, literal_pair_distances=0, graph_cuts=0,
               hamming_cuts=0, three_field_fault_profiles=0, collision_rows=0)
    for m in range(2, 6):
        result = exact_cover(m)
        out['optima'].append(result)
        rows = result['witness']
        groups = defaultdict(list)
        for a, b in combinations_with_replacement(range(1 << m), 2):
            raw = tuple(((a >> j) & 1) + ((b >> j) & 1) for j in range(m))
            groups[raw].append((a, b))
        for raw, pairs in groups.items():
            s = raw.count(1)
            assert len(pairs) == 1 << max(0, s - 1)
            out['raw_fibres'] += 1
            received = [receipt(a, b, rows) for a, b in pairs]
            assert len(set(received)) == len(pairs)
            for (a, b), (c, d) in combinations(pairs, 2):
                u, v = a ^ c, a ^ d
                assert u and v and not u & v
                actual = sum(x != y for x, y in zip(receipt(a, b, rows), receipt(c, d, rows)))
                assert actual == distance(rows, u, v) >= 1
                out['literal_pair_distances'] += 1
        # Every row subset, including nonidentifying dictionaries, at m<=4.
        if m <= 4:
            avail = [r for r in range(1, 1 << m) if r.bit_count() >= 2]
            for mask in range(1 << len(avail)):
                trial = [r for j, r in enumerate(avail) if mask & (1 << j)]
                predicted = all(distance(trial, u, v) for u, v in partitions(m))
                observed = all(len({receipt(a, b, trial) for a, b in pairs}) == len(pairs) for pairs in groups.values())
                assert predicted == observed
                out['collision_rows'] += 1
    for s in range(2, 13):
        full = (1 << s) - 1
        graph = graph_one_error(s)
        ham = hamming_rows(s - 1)
        assert len(graph) == math.ceil(3 * s / 2)
        for u in range(1, full):
            v = full ^ u
            assert distance(graph, u, v) >= 3
            assert distance(ham, u, v) >= 3
            out['graph_cuts'] += 1
            out['hamming_cuts'] += 1
    for q in range(1, 13):
        optimum = 2 * q + (q % 2)
        # Lower-bound proof plus bounded exhaustive independent integer check.
        feasible = []
        for x in range(optimum + 1):
            for y in range(optimum + 1 - x):
                for z in range(optimum + 1 - x - y):
                    for w in range(optimum + 1 - x - y - z):
                        if min(x+w, y+w, z+w, x+y, x+z, y+z) >= q:
                            feasible.append(x+y+z+w)
                        out['three_field_fault_profiles'] += 1
        assert min(feasible) == optimum
    return out


def render(path, a, b, rows, stereo=False):
    # Each 0/1 value produces a phase-aligned integer pulse at one of two pitches.
    # Integer summation means swapped source assignments cannot affect the mono bytes.
    rate, length, active = 8000, 1600, 1200
    tones = []
    for bit in (0, 1):
        freq = 250 + 250 * bit
        tones.append([round(7000 * math.sin(2 * math.pi * freq * i / rate) *
                            min(1, i/80, (active-1-i)/80)) if i < active else 0 for i in range(length)])
    pcm = []
    for r in rows:
        x, y = tones[parity(a&r)], tones[parity(b&r)]
        if stereo:
            pcm.extend(v for pair in zip(x, y) for v in pair)
        else:
            pcm.extend(i+j for i,j in zip(x,y))
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((2 if stereo else 1, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(struct.pack('<'+'h'*len(pcm), *pcm))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio-dir', type=Path)
    args = parser.parse_args()
    out = qualify()
    if args.audio_dir:
        p = args.audio_dir
        p.mkdir(parents=True, exist_ok=True)
        raw = [1,2,4,8]
        extra = [3,5,10,12,15]
        # Two anonymous source pairs, both with raw sum 1111.
        a,b,c,d = 0,15,5,10
        hashes = {}
        for name,x,y in [('a',a,b),('b',c,d)]:
            hashes['raw-'+name] = render(p/('raw-'+name+'.wav'),x,y,raw)
            hashes['bound-'+name] = render(p/('bound-'+name+'.wav'),x,y,raw+extra)
            hashes['stereo-'+name] = render(p/('stereo-'+name+'.wav'),x,y,raw,True)
        assert hashes['raw-a'] == hashes['raw-b']
        assert hashes['bound-a'] != hashes['bound-b']
        assert hashes['stereo-a'] != hashes['stereo-b']
        out['audio_sha256'] = hashes
        out['audio_receipts'] = {'a':receipt(a,b,extra),'b':receipt(c,d,extra)}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
