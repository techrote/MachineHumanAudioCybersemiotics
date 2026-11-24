"""Original synthetic real-coefficient phase witness, Python 3.11+."""
import hashlib
import itertools
import json
import pathlib
import struct
import sys
import wave


def powers(x, edges):
    return tuple(v*v for v in x) + tuple((x[i]+x[j])**2 for i, j in edges)


def census():
    graphs = cases = 0
    for n in range(2, 5):
        edges = list(itertools.combinations(range(n), 2))
        for bits in itertools.product((0, 1), repeat=len(edges)):
            selected = [e for e, b in zip(edges, bits) if b]
            graphs += 1
            for mask in itertools.product((0, 1), repeat=n):
                support = [i for i, b in enumerate(mask) if b]
                if len(support) < 2:
                    continue
                remaining = set(support)
                c = 0
                while remaining:
                    group = {remaining.pop()}
                    while True:
                        new = {v for v in remaining if any(tuple(sorted((u, v))) in selected for u in group)}
                        if not new:
                            break
                        group.update(new)
                        remaining.difference_update(new)
                    c += 1
                counts = {}
                for signs in itertools.product((-1, 1), repeat=len(support)-1):
                    x = [0]*n
                    for i, s in zip(support, (1,)+signs):
                        x[i] = s
                    key = powers(x, selected)
                    counts[key] = counts.get(key, 0)+1
                assert set(counts.values()) == {2**(c-1)}
                cases += 1
    return dict(graphs=graphs, support_cases=cases)


def render(path, values):
    # One 100 ms slot per value; 250 Hz square wave, energy-coded amplitude.
    # Values are powers, not physical mix waveforms; no normalization per file.
    samples = [1200*p*(1 if i % 32 < 16 else -1) for p in values for i in range(800)]
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(samples), *samples))
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), powers=values)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    chain = [(0, 1), (1, 2)]
    x, y = (1, 0, 1), (1, 0, -1)
    recordings = {}
    for label, edges in [('chain', chain), ('bridge', chain+[(0, 2)])]:
        for name, v in [('a', x), ('b', y)]:
            key = label+'-'+name
            recordings[key] = render(out/(key+'.wav'), powers(v, edges))
    assert recordings['chain-a']['sha256'] == recordings['chain-b']['sha256']
    assert recordings['bridge-a']['sha256'] != recordings['bridge-b']['sha256']
    receipt = dict(status='pass', census=census(), recordings=recordings)
    (out/'witness.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main(pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('build/mhac-372'))
