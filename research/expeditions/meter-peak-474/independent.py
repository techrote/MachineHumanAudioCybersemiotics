"""Independent brute census and integer audio demonstration for MHAC #474."""
import argparse
import hashlib
import itertools
import json
import math
import struct
import wave
from pathlib import Path


def compositions(n, total):
    # Stars and bars, independently of the JavaScript recursive enumerator.
    for bars in itertools.combinations(range(total+n-1), n-1):
        edges = (-1, *bars, total+n-1)
        yield tuple(b-a-1 for a, b in zip(edges, edges[1:]))


def direct(x, w):
    doubled = x+x
    return tuple(sum(doubled[i:i+w]) for i in range(len(x)))


def census():
    out = {}
    for n in range(1, 9):
        traces = classes = 0
        for size in (1, 2):
            for ws in itertools.combinations(range(1, n+1), size):
                groups = {}
                for total in range(6):
                    for x in compositions(n, total):
                        key = tuple(direct(x,w) for w in ws)
                        groups.setdefault(key, []).append(max(x))
                        traces += 1
                g = math.gcd(n, *ws)
                for peaks in groups.values():
                    # The primary solver is not imported: only direct observations count.
                    assert len(set(peaks)) == max(peaks)-min(peaks)+1
                    assert len(peaks) == 1 or g > 1
                    classes += 1
        out[str(n)] = dict(traces=traces, classes=classes)
    return out


def render(out):
    # 16 blocks per repeating period, 320 samples/block, 500 Hz triangle.
    # Left constant amplitude; right 4x amplitude in one block, zero elsewhere.
    # Both have exactly equal squared sample sums in every 5120-sample window.
    rate, block, g = 16000, 320, 16
    tone = tuple(1000-125*abs(i%32-16) for i in range(block))
    left = tone*g
    right = tuple(4*v for v in tone)+(0,)*(block*(g-1))
    period = len(left)
    assert sum(v*v for v in left)==sum(v*v for v in right)
    assert max(map(abs,right))==4*max(map(abs,left))
    # Verify all circular start phases at both 320ms and 640ms apertures.
    energy = [tuple(v*v for v in a) for a in (left,right)]
    def rolling(a, w):
        s=sum(a[i%period] for i in range(w)); result=[]
        for i in range(period):
            result.append(s)
            s+=a[(i+w)%period]-a[i]
        return result
    for w in (period,2*period):
        assert rolling(energy[0],w)==rolling(energy[1],w)
    assert rolling(energy[0],period-block)!=rolling(energy[1],period-block)
    out.mkdir(parents=True,exist_ok=True)
    path=out/'same-meter-different-peak.wav'
    payload=struct.pack('<'+'hh'*period, *itertools.chain.from_iterable(zip(left,right)))
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(payload*10)
    return dict(sample_rate=rate, frames=period*10, peak_left=max(map(abs,left)),
                peak_right=max(map(abs,right)), energy_per_period=sum(energy[0]),
                windows_samples=[period,2*period], equal_window_pairs=period*2,
                distinguishing_width_samples=period-block,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=Path('build/meter-peak-474'))
    a=p.parse_args(); by_n=census()
    result=dict(byN=by_n,traces=sum(x['traces'] for x in by_n.values()),
                measurementClasses=sum(x['classes'] for x in by_n.values()), audio=render(a.out))
    (a.out/'independent.synthetic.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
