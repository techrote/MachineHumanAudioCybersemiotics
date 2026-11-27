"""Synthetic heteronym salon: finite revision dynamics, not human judgments."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import json
import math
import struct
import wave

SEED = (0, 0, 3, 1, 2, 3)
DRAFTS = sorted(set(permutations(SEED)))
NAMES = ('Surveyor', 'Spark', 'Archivist')


def costs(s, seed):
    return (sum(abs(a-b) for a,b in zip(s,s[1:])),
            sum(a == b for a,b in zip(s,s[1:])),
            sum(a != b for a,b in zip(s,seed)))


def neighbors(s):
    return sorted({s[:j]+(s[j+1],s[j])+s[j+2:] for j in range(len(s)-1)}-{s})


def revise(s, seed, critic, guarded=False):
    old = costs(s,seed)
    candidates = [t for t in neighbors(s) if costs(t,seed)[critic] < old[critic]]
    if guarded:
        candidates = [t for t in candidates if all(a<=b for a,b in zip(costs(t,seed),old))]
    return min(candidates,key=lambda t:(costs(t,seed)[critic],t),default=s)


def trajectory(seed, order=(0,1,2), guarded=False):
    s, phase = seed, 0
    seen, trace = {}, []
    while (s,phase) not in seen:
        seen[s,phase] = len(trace)
        c = order[phase]
        t = revise(s,seed,c,guarded)
        assert Counter(t)==Counter(seed)
        a,b = costs(s,seed),costs(t,seed)
        if t != s:
            assert t in neighbors(s) and b[c]<a[c]
            if guarded:
                assert all(x<=y for x,y in zip(b,a)) and sum(b)<sum(a)
        trace.append(dict(critic=NAMES[c],before=s,after=t,cost_before=a,cost_after=b))
        s,phase = t,(phase+1)%len(order)
        assert len(trace)<=len(DRAFTS)*len(order)
    return trace,seen[s,phase]


def census():
    histogram, guarded_hist = Counter(),Counter()
    for seed in DRAFTS:
        for order in permutations(range(3)):
            for guarded,h in [(False,histogram),(True,guarded_hist)]:
                trace,start=trajectory(seed,order,guarded)
                loop=trace[start:]
                changing=any(r['before']!=r['after'] for r in loop)
                h[(len(loop),changing)]+=1
                if guarded:
                    assert not changing
    def encode(h):
        return [{'period_turns':k,'changing':v,'cases':n} for (k,v),n in sorted(h.items())]
    return {'seeds':len(DRAFTS),'orders_per_seed':6,'cases_per_policy':len(DRAFTS)*6,
            'ordinary':encode(histogram),'guarded':encode(guarded_hist)}


def render(path, scores):
    rate,n=16000,3200
    tiles={p:struct.pack('<'+'h'*n,*[round(10000*math.sin(2*math.pi*f*j/rate)*math.sin(math.pi*j/(n-1))**2) for j in range(n)]) for p,f in enumerate((220,261.626,329.628,440))}
    pcm=b''.join(tiles[p] for s in scores for p in s)
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,rate,len(pcm)//2,'NONE','not compressed'));w.writeframes(pcm)
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,rate,len(pcm)//2)
        assert w.readframes(w.getnframes())==pcm
    return dict(frames=len(pcm)//2,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scores=scores)


def main():
    trace,start=trajectory(SEED)
    assert start==0 and len(trace)==6 and all(r['before']!=r['after'] for r in trace)
    assert len({r['before'] for r in trace})==4
    guarded,gstart=trajectory(SEED,guarded=True)
    assert gstart==0 and all(r['before']==r['after'] for r in guarded)
    out=Path(__file__).parent/'audio';out.mkdir(exist_ok=True)
    scores=[r['before'] for r in trace]
    editions={'salon-cycle.wav':scores+[SEED], 'unanimous-refusal.wav':[SEED]*7,
              'surveyor.wav':[trace[0]['after']], 'spark.wav':[trace[1]['after']]}
    receipt={'synthetic':True,'census':census(),'trace':trace,'cycle_start':start,
             'audio':{name:render(out/name,s) for name,s in editions.items()}}
    assert len({v['sha256'] for v in receipt['audio'].values()})==4
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt['census'],indent=2))


if __name__=='__main__':
    main()
