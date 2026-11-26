"""Original synthetic retention-mask oracle and listening score. Python 3.11+."""
from collections import Counter
from hashlib import sha256
from math import comb, sin, pi
from pathlib import Path
import json
import random
import struct
import sys
import wave


def audit():
    total = 0
    for n in range(3, 17):
        hist = Counter()
        for mask in range(1, (1 << n) - 1):
            a = [(mask >> i) & 1 for i in range(n)]
            m = sum(a)
            edges = list(zip(a, a[1:] + a[:1]))
            r = edges.count((0, 1))
            both = sum(x and y for x, y in edges)
            touch = sum(x or y for x, y in edges)
            assert 1 <= r <= min(m, n-m)
            assert (both, touch) == (m-r, m+r)
            assert edges.count((1, 0)) == r
            hist[m, r] += 1
            total += 1
        for m in range(1, n):
            assert sum(hist[m, r] for r in range(1, min(m,n-m)+1)) == comb(n,m)
            for r in range(1, min(m,n-m)+1):
                assert r*hist[m,r] == n*comb(m-1,r-1)*comb(n-m-1,r-1)
    assert total == sum(2**n-2 for n in range(3,17))
    # Every fixed query has the same success count under all labelled rotations.
    masks = ('111111000000', '110011001100', '101010101010')
    for s in masks:
        rs = [s[i:]+s[:i] for i in range(12)]
        both = [sum(t[j] == t[(j+1)%12] == '1' for t in rs) for j in range(12)]
        touch = [sum('1' in (t[j],t[(j+1)%12]) for t in rs) for j in range(12)]
        assert len(set(both)) == len(set(touch)) == 1
        r = sum(s[i]=='0' and s[(i+1)%12]=='1' for i in range(12))
        assert (both[0], touch[0]) == (6-r,6+r)
    return total


RATE, CELL = 16000, 8000


def tiles():
    rng = random.Random(696)
    result = []
    for i in range(12):
        buf = []
        for j in range(CELL):
            u = j/CELL
            t = (i*CELL+j)/RATE
            env = min(1, j/160, (CELL-1-j)/160)
            # Invented machinery, whistle, and texture; no microphone input.
            hum = .12*sin(2*pi*73*t) + .07*sin(2*pi*146*t)
            whistle = .13*sin(2*pi*(180+23*i)*j/RATE)*sin(pi*u)**2
            tick = .10*sin(2*pi*(600+70*(i%3))*j/RATE)*max(0, 1-12*abs(u-.35))
            grain = .035*(2*rng.random()-1)*(0.3+0.7*sin(pi*u)**2)
            buf.append(round(32767*env*(hum+whistle+tick+grain)))
        result.append(struct.pack('<'+'h'*CELL,*buf))
    return result


def render(out):
    out.mkdir(parents=True,exist_ok=True)
    source = tiles()
    assert source == tiles() and len(set(source)) == 12
    masks = {'source':'1'*12, 'contiguous':'111111000000',
             'three-islands':'110011001100','alternating':'101010101010'}
    silence = bytes(2*CELL)
    files = {}
    for name,mask in masks.items():
        payload = b''.join(t if bit=='1' else silence for t,bit in zip(source,mask))
        assert max(abs(x[0]) for x in struct.iter_unpack('<h',payload)) < 32767
        path = out/(name+'.wav')
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,RATE,0,'NONE','not compressed'))
            w.writeframes(payload)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,RATE,12*CELL)
            assert w.readframes(12*CELL) == payload
        for i,b in enumerate(mask):
            assert payload[i*CELL*2:(i+1)*CELL*2] == (source[i] if b=='1' else silence)
        files[name] = {'mask':mask,'sha256':sha256(path.read_bytes()).hexdigest(),
                       'retained_frames':mask.count('1')*CELL}
    assert len({x['sha256'] for x in files.values()}) == 4
    return files


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio')
    receipt = {'synthetic':True,'python':sys.version.split()[0],
               'masks_examined':audit(),'audio':render(out),'result':'PASS'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
