"""Synthetic independent transition-enumeration oracle and pulse-gate renderer."""
from functools import cache
from itertools import product
from pathlib import Path
import hashlib, json, math, struct, wave


def check():
    totals = dict(inputs=0, terminalPairs=0, multiple=0, snapshotUnreachable=0, twoCycles=0)
    for n in range(3, 13):
        @cache
        def ends(x):
            children = []
            for i in range(n):
                if x[i-1] == x[(i+1)%n] != x[i]:
                    children.append(x[:i] + (1-x[i],) + x[i+1:])
            return frozenset().union(*(ends(y) for y in children)) if children else frozenset([x])
        for x in product((0, 1), repeat=n):
            e = ends(x)
            totals['inputs'] += 1
            totals['terminalPairs'] += len(e)
            totals['multiple'] += len(e) > 1
            seen = set()
            y = x
            while y not in seen:
                seen.add(y)
                z = tuple(int(sum((y[i-1], y[i], y[(i+1)%n])) >= 2) for i in range(n))
                if z == y:
                    totals['snapshotUnreachable'] += y not in e
                    break
                y = z
            else:
                totals['twoCycles'] += 1
    assert totals == dict(inputs=8184, terminalPairs=18036, multiple=4894, snapshotUnreachable=2654, twoCycles=10), totals
    return totals


def path(x, indices):
    frames = [tuple(x)]
    for i in indices:
        assert x[i-1] == x[(i+1)%len(x)] != x[i]
        x = x[:i] + [1-x[i]] + x[i+1:]
        frames.append(tuple(x))
    return frames


def render(out, name, left, right):
    assert len(left) == len(right)
    rate, block = 16000, 3200
    n = len(left[0]); peak = 0; pcm = bytearray()
    for frame, (a,b) in enumerate(zip(left,right)):
        for j in range(block):
            t = (frame*block+j)/rate
            env = min(1, j/160, (block-1-j)/160)
            vals = [round(25000*env/n*sum(v*math.sin(2*math.pi*(220+55*i)*t) for i,v in enumerate(x))) for x in (a,b)]
            peak = max(peak, *(abs(v) for v in vals))
            pcm.extend(struct.pack('<hh', *vals))
    p = out/name
    with wave.open(str(p),'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed')); w.writeframes(pcm)
    return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), peak=peak, frames=len(left)*block, final_ones=[sum(left[-1]),sum(right[-1])])


if __name__ == '__main__':
    out = Path(__file__).parent
    result = check()
    x = [i%2 for i in range(12)]
    l = path(x,list(range(1,12,2))); r = path(x,list(range(0,12,2)))
    x2 = [0,0,1,0,1,1]
    a = path(x2,[2]); b = path(x2,[3]); snap = (0,0,0,1,1,1)
    result['audio'] = {
        'same-start.wav':render(out,'same-start.wav',l+[l[-1]]*5,r+[r[-1]]*5),
        'snapshot-vs-in-place.wav':render(out,'snapshot-vs-in-place.wav',[tuple(x2),snap]+[snap]*8,a+[a[-1]]*8),
    }
    assert sum(a[-1])==2 and sum(b[-1])==4 and sum(snap)==3
    (out/'independent-results.txt').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
