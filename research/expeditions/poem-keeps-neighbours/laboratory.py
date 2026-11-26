"""Synthetic transition-anagram score; standard-library Python only."""
from collections import Counter
from itertools import combinations
from math import comb, pi, sin
from pathlib import Path
import hashlib, json, struct, sys, wave


def counts(s, k):
    return Counter(s[i:i+k] for i in range(len(s)-k+1))


def score(w):
    return 'A' + ''.join(x+'A' for x in w)


def switches(w):
    return sum(a != b for a, b in zip(w, w[1:]))


def compositions(n, r):
    return comb(n-1, r-1) if 1 <= r <= n else 0


def predicted(b, c, t):
    runs = t+1
    lo, hi = runs//2, (runs+1)//2
    return (compositions(b, hi)*compositions(c, lo)
            + compositions(b, lo)*compositions(c, hi))


def enumerate_family(b, c):
    histogram = Counter()
    target = score('B'*b+'C'*c)
    for pos in combinations(range(b+c), b):
        chosen = set(pos)
        w = ''.join('B' if i in chosen else 'C' for i in range(b+c))
        s = score(w)
        assert counts(s, 1) == counts(target, 1)
        assert counts(s, 2) == counts(target, 2)
        assert counts(s, 3)['BAC'] + counts(s, 3)['CAB'] == switches(w)
        histogram[switches(w)] += 1
    assert sum(histogram.values()) == comb(b+c, b)
    assert all(histogram[t] == predicted(b, c, t) for t in range(b+c))
    return histogram


def pentagon(directed):
    edges = ([(a, (a+d)%5) for a in range(5) for d in (1, 2)] if directed
             else list(combinations(range(5), 2)))
    def walk(path, remaining):
        if not remaining:
            if path[-1] == path[0]:
                yield tuple(path)
            return
        for i in remaining:
            a, b = edges[i]
            if path[-1] == a or (not directed and path[-1] == b):
                yield from walk(path+[b if path[-1] == a else a], remaining-{i})
    paths = list(walk([0], set(range(len(edges)))))
    assert len(paths) == len(set(paths))
    for p in paths:
        got = Counter((a,b) if directed else tuple(sorted((a,b))) for a,b in zip(p,p[1:]))
        assert got == Counter(edges)
    return paths


RATE, SLOT = 16000, 3200

def render(s):
    data = []
    for x in s:
        f = {'A': 196, 'B': 293.6648, 'C': 392}[x]
        for i in range(SLOT):
            u = i/(SLOT-1)
            env = min(1, u*20, (1-u)*10)
            v = .24*env*(sin(2*pi*f*i/RATE)+.25*sin(4*pi*f*i/RATE))
            data.append(round(32767*v))
    assert max(map(abs,data)) < 32767
    return struct.pack('<'+'h'*len(data), *data)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    families = {(b,c): enumerate_family(b,c) for b in range(1,9) for c in range(1,9)}
    h = families[8,8]
    undirected, directed = pentagon(False), pentagon(True)
    assert len({counts_tuple(p, 2) for p in directed}) == 1
    words = {'blocks': 'BBBBBBBBCCCCCCCC', 'pairs': 'BBCC'*4, 'alternation': 'BC'*8}
    assert len({counts_tuple(score(w), 3) for w in words.values()}) == 3
    assert counts(score('B'*7+'C'*9),2) != counts(score(words['blocks']),2)
    results = {}
    for name,w in words.items():
        s = score(w)
        pcm = render(s)
        assert pcm == render(s)
        path = out/(name+'.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,RATE,0,'NONE','not compressed'))
            f.writeframes(pcm)
        with wave.open(str(path),'rb') as f:
            assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes()) == (1,2,RATE,len(s)*SLOT)
            assert f.readframes(f.getnframes()) == pcm
        results[name] = {'score':s,'switches':switches(w),'frames':len(s)*SLOT,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    assert len({v['sha256'] for v in results.values()}) == 3
    receipt = {'python':sys.version.split()[0], 'families':len(families), 'words_checked':sum(sum(v.values()) for v in families.values()), 'balanced_histogram':dict(sorted(h.items())), 'pentagon_undirected_rooted':len(undirected), 'pentagon_directed_rooted':len(directed), 'directed_examples':[list(directed[0]),list(directed[-1])], 'recordings':results, 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


def counts_tuple(s,k):
    return tuple(sorted(counts(s,k).items()))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))
