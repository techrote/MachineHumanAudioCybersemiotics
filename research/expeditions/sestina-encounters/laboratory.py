"""Original synthetic score/oracle; no human or physical measurements."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import array, hashlib, json, math, sys, wave


def rows(p):
    n = len(p)
    out = [tuple(range(n))]
    for _ in range(n - 1):
        out.append(tuple(out[-1][j] for j in p))
    return out


def measure(p):
    r = rows(p)
    n = len(p)
    latin = all(len(set(c)) == n for c in zip(*r))
    edges = Counter((a, b) for row in r for a, b in zip(row, row[1:]))
    seams = sum(a[-1] == b[0] for a, b in zip(r, r[1:]))
    return latin, len(edges), seams, edges


def audit():
    result = {}
    for n in range(2, 9):
        hist = Counter()
        visited = 0
        for p in permutations(range(n)):
            visited += 1
            latin, distinct, seams, edges = measure(p)
            if not latin:
                continue
            # Independent oracle: orbit coordinates, differences of consecutive positions.
            phase = {}
            pos = 0
            for k in range(n):
                phase[pos] = k
                pos = p[pos]
            assert len(phase) == n and pos == 0
            offsets = {(phase[j + 1] - phase[j]) % n for j in range(n - 1)}
            assert distinct == n * len(offsets)
            assert seams == (n - 1 if p[0] == n - 1 else 0)
            if distinct == n * (n - 1):
                assert n % 2 == 0 and all(v == 1 for v in edges.values())
                assert n == 2 or seams == 0
            hist[distinct, seams] += 1
        assert sum(hist.values()) == math.factorial(n - 1)
        result[str(n)] = {'visited': visited, 'latin': sum(hist.values()),
                          'histogram': {f'{d}/{s}': v for (d, s), v in sorted(hist.items())}}
    assert result['6']['histogram'] == {'6/0':1,'6/5':1,'12/0':13,'12/5':5,
        '18/0':52,'18/5':8,'24/0':26,'24/5':10,'30/0':4}
    return result


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    fs, samples = 16000, 4000
    tiles = []
    for f in (220, 247, 294, 330, 370, 440):
        a = array.array('h', (round(9000 * math.sin(math.pi*i/(samples-1))**2 *
            (0.8*math.sin(2*math.pi*f*i/fs)+0.2*math.sin(2*math.pi*2*f*i/fs)))
            for i in range(samples)))
        if sys.byteorder != 'little':
            a.byteswap()
        tiles.append(a.tobytes())
    receipt = {}
    for name, p in {'spiral':(5,0,4,1,3,2), 'encounter':(1,3,0,5,2,4),
                    'rotation':(1,2,3,4,5,0)}.items():
        r = rows(p)
        assert measure(p)[0]
        seq = [v for row in r for v in row]
        pcm = b''.join(tiles[v] for v in seq)
        assert Counter(seq) == Counter({i:6 for i in range(6)})
        path = out / (name + '.wav')
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,fs,0,'NONE','not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,fs,144000)
            assert w.readframes(144000) == pcm
        assert max(abs(v[0]) for v in __import__('struct').iter_unpack('<h',pcm)) <= 9000
        receipt[name] = {'rows': r, 'distinct_internal_pairs': measure(p)[1],
            'repeated_seams': measure(p)[2], 'frames':144000,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    assert len({v['sha256'] for v in receipt.values()}) == 3
    return receipt


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('output')
    data = {'python':sys.version.split()[0], 'audit':audit(), 'audio':render(root)}
    assert data['audio'] == render(root)
    (root/'receipt.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
