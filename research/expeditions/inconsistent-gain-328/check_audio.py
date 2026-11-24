"""Independent small-case census and synthetic relative-level audio demonstration."""
from itertools import product
from fractions import Fraction as F
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import struct
import wave


def census():
    hist = Counter()
    gap = bad = 0
    for a,b,c,d,e,f in product(range(3), repeat=6):
        pts = [(0,x,y) for x,y in product(range(-2,3), repeat=2)
               if -a <= x <= b and -c <= y <= d and -e <= y-x <= f]
        # No graph closure: compute exact extrema from feasible integer vertices.
        m = [[max(v[j]-v[i] for v in pts) for j in range(3)] for i in range(3)]
        diameter = max(m[i][j]+m[j][i] for i in range(3) for j in range(3))
        radius = max(F(diameter,2), F(m[0][1]+m[1][2]+m[2][0],3),
                     F(m[0][2]+m[2][1]+m[1][0],3))
        hist[str(radius.numerator)+'/'+str(radius.denominator)] += 1
        gap += 2*radius > diameter
        bad += m[0][1]-m[1][0]+m[1][2]-m[2][1] != m[0][2]-m[2][0]
    return dict(population=sum(hist.values()),strictRadiusGap=gap,
                inconsistentPairMidpoints=bad,radiusHistogram=dict(hist))


def render(path):
    # Three admissible gain states of the monotone three-coordinate simplex.
    # Remove common gain from each error vector, leaving only relative error.
    sr, length, edge = 16000, 9600, 160
    true = [(0,0,0),(0,0,12),(0,12,12)]
    centers = [(0,6,6),(0,4,8)]
    frames, spans = bytearray(), []
    for x in true:
        errs = [[a-b for a,b in zip(x,c)] for c in centers]
        spans.append([max(e)-min(e) for e in errs])
        amps = [[0.13*10**((v-(max(e)+min(e))/2)/20) for v in e] for e in errs]
        for i in range(length):
            env = min(1,i/edge,(length-1-i)/edge)
            samples = [round(32767*env*sum(a*math.sin(2*math.pi*f*i/sr)
                       for a,f in zip(ch,(250,500,750)))) for ch in amps]
            assert all(-32768 <= v <= 32767 for v in samples)
            frames.extend(struct.pack('<hh',*samples))
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,sr,0,'NONE','not compressed'))
        w.writeframes(frames)
    return dict(relative_error_span_dB=spans,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                samples_per_channel=len(frames)//4,sample_rate=sr)


if __name__ == '__main__':
    out = Path(__file__).parent/'run'
    out.mkdir(exist_ok=True)
    result = census()
    assert (result['population'],result['strictRadiusGap'],result['inconsistentPairMidpoints']) == (729,152,356)
    audio = render(out/'relative-gain.wav')
    assert audio['relative_error_span_dB'] == [[6,8],[12,8],[6,8]]
    assert audio == render(out/'relative-gain.wav')
    receipt = dict(census=result,audio=audio)
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
