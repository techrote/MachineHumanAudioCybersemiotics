"""Synthetic graph walks; no human observations. Python standard library only."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import math
import struct
import wave

RATE = 16000
TILE = RATE // 4


def check():
    cases = 0
    for k in range(2, 17):
        for den in range(1, 17):
            for num in range(1, den + 1):
                q = F(num, den)
                p = [q / (1 + q)] + [1 / (k * (1 + q))] * k
                # Independent explicit transition matrix, row = source.
                P = [[F(0) for _ in p] for _ in p]
                for j in range(1, k + 1):
                    P[0][j] = F(1, k)
                    P[j][0], P[j][j] = q, 1 - q
                assert all(sum(row) == 1 for row in P)
                assert sum(p) == 1
                assert [sum(p[i]*P[i][j] for i in range(k+1))
                        for j in range(k+1)] == p
                flow = sum(p[i]*P[i][j] for i in range(k+1)
                           for j in range(k+1) if i != j)
                assert flow == 2*q/(1+q)
                assert p[0]/flow == F(1, 2)
                assert (len(set(p)) == 1) == (q == F(1,k))
                cases += 1
    return cases


def score(k=5):
    transit = [v for j in range(1,k+1) for v in (0,j)]
    dwelling = [v for j in range(1,k+1) for v in [0]+[j]*k]
    collapsed = [v for i,v in enumerate(dwelling)
                 if i == 0 or v != dwelling[i-1]]
    assert transit == collapsed
    assert Counter(dwelling) == {i:k for i in range(k+1)}
    assert Counter(transit)[0] == k
    assert all(Counter(transit)[i] == 1 for i in range(1,k+1))
    return transit, dwelling, collapsed


def pcm(seq):
    freqs = [110, 165, 220, 277, 330, 415]
    frames = []
    for v in seq:
        for i in range(TILE):
            t = i / RATE
            env = math.sin(math.pi*i/(TILE-1))**2
            x = math.sin(2*math.pi*freqs[v]*t)
            x += 0.24*math.sin(2*math.pi*freqs[v]*3*t)
            frames.append(round(9000*env*x))
    assert max(map(abs, frames)) < 32768
    return struct.pack('<'+'h'*len(frames), *frames)


def main():
    root = Path(__file__).parent / 'audio'
    root.mkdir(exist_ok=True)
    transit, dwelling, collapsed = score()
    receipt = {'matrix_cases': check(), 'sample_rate': RATE, 'files': {}}
    for name, seq in [('transit',transit), ('dwelling',dwelling),
                      ('collapsed',collapsed)]:
        payload = pcm(seq)
        assert payload == pcm(seq)
        path = root / (name+'.wav')
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,RATE,0,'NONE','not compressed'))
            w.writeframes(payload)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate()) == (1,2,RATE)
            assert w.getnframes() == len(seq)*TILE
            assert w.readframes(w.getnframes()) == payload
        receipt['files'][name] = {'ticks':len(seq), 'frames':len(seq)*TILE,
                                   'occupancy':dict(sorted(Counter(seq).items())),
                                   'sha256':sha256(path.read_bytes()).hexdigest()}
    assert receipt['files']['transit']['sha256'] == receipt['files']['collapsed']['sha256']
    assert receipt['files']['dwelling']['sha256'] != receipt['files']['transit']['sha256']
    (root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
