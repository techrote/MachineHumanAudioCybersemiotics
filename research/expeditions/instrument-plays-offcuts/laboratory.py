"""Original synthetic offcut composition; standard-library Python 3."""
from collections import Counter
from hashlib import sha256
from itertools import product
from math import pi, sin
from pathlib import Path
import json
import struct
import wave


def clip(x, t):
    return max(-t, min(t, x))


def census():
    t = 4
    observed = Counter()
    for x in product(range(-2*t, 2*t+1), repeat=4):
        y = tuple(clip(v, t) for v in x)
        e = tuple(a-b for a, b in zip(x, y))
        assert tuple(b+c for b, c in zip(y, e)) == x
        assert all(c == 0 or (abs(b) == t and b*c > 0)
                   for b, c in zip(y, e))
        observed[y] += 1
    assert len(observed) == (2*t+1)**4
    for y, count in observed.items():
        assert count == (t+1)**sum(abs(v)==t for v in y)
    return {"inputs": sum(observed.values()), "outputs": len(observed),
            "largest_fiber": max(observed.values())}


def pcm(values):
    assert all(-32768 <= v <= 32767 for v in values)
    return struct.pack('<' + 'h'*len(values), *values)


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    sr, t = 16000, 8000
    notes = [110, 146.83, 130.81, 164.81, 110, 174.61, 130.81, 98]
    base = []
    for f in notes:
        for j in range(sr//2):
            env = min(1, j/160, (sr//2-1-j)/160)
            base.append(clip(round(12000*env*sin(2*pi*f*j/sr)), t))
    result = {}
    primary_hashes = []
    for name, mod in [('slow', 3), ('fast', 37)]:
        excess = [round((1 if b>0 else -1)*t*(.5+.5*sin(2*pi*mod*i/sr)))
                  if abs(b)==t else 0 for i,b in enumerate(base)]
        dry = [b+e for b,e in zip(base,excess)]
        primary = [clip(x,t) for x in dry]
        offcut = [x-y for x,y in zip(dry,primary)]
        assert primary == base and offcut == excess
        assert all(x == y+e for x,y,e in zip(dry,primary,offcut))
        assert max(map(abs,dry)) <= 2*t
        for role, samples in [('input',dry),('primary',primary),('offcut',offcut)]:
            payload = pcm(samples)
            filename = f'{name}-{role}.wav'
            with wave.open(str(out/filename),'wb') as w:
                w.setparams((1,2,sr,0,'NONE','not compressed'))
                w.writeframes(payload)
            with wave.open(str(out/filename),'rb') as w:
                assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,sr,len(samples))
                assert w.readframes(len(samples)) == payload
            digest = sha256((out/filename).read_bytes()).hexdigest()
            result[filename] = {"sha256":digest,"frames":len(samples),"peak":max(map(abs,samples))}
            if role=='primary':
                primary_hashes.append(digest)
    assert len(set(primary_hashes))==1
    assert result['slow-offcut.wav']['sha256'] != result['fast-offcut.wav']['sha256']
    return result


if __name__ == '__main__':
    output = Path(__file__).parent / 'audio'
    report = {'census':census(), 'audio':render(output)}
    report['repeat_identical'] = render(output)==report['audio']
    assert report['repeat_identical']
    (output.parent/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
