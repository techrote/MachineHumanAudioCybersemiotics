"""Exact cyclic-window run-length audit; original synthetic PCM, no human data."""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from math import ceil, sin, pi
import hashlib
import json
import wave
import struct


def histogram(word, r):
    wrap = word + word[:r-1]
    return Counter(wrap[i:i+r] for i in range(len(word)))


def runs(word, bit):
    if bit not in word:
        return []
    if len(set(word)) == 1:
        return [len(word)]
    start = word.index(str(1-int(bit)))
    rotated = word[start:] + word[:start]
    return [len(x) for x in rotated.split(str(1-int(bit))) if x]


def interval(hist, r, bit):
    other = str(1-int(bit))
    def count(w):
        return sum(v for s, v in hist.items() if s.startswith(w))
    long = count(other + bit*(r-1))
    excess = count(bit*r)
    if long:
        return r-1 + ceil(excess/long), r-1 + excess
    peak = max((j for j in range(1, r-1) if count(other+bit*j+other)), default=0)
    return peak, peak


def worst(n, r):
    if r == 1:
        return max((h-ceil(h/(n-h)) for h in range(1,n)), default=0)
    return max((n-(l-1)*r-ceil(n/l) for l in range(1,n//r+1)), default=0)


def compositions(total, count):
    if count == 1:
        yield (total,)
    else:
        for x in range(total+1):
            for tail in compositions(total-x,count-1):
                yield (x,)+tail


def census():
    profiles=[]
    words_seen=fibres_seen=rectangles=0
    negative=None
    for n in range(2,13):
        words=[''.join(bits) for bits in product('01',repeat=n) if len(set(bits))==2]
        rs={w: (runs(w,'0'),runs(w,'1')) for w in words}
        for r in range(1,n+1):
            fibres=defaultdict(set)
            for w in words:
                h=histogram(w,r)
                key=tuple(sorted(h.items()))
                peaks=tuple(max(x) for x in rs[w])
                fibres[key].add(peaks)
                if r>=2:
                    for bit in '01':
                        lo,hi=interval(h,r,bit)
                        assert lo<=peaks[int(bit)]<=hi
            words_seen+=len(words)
            widths=[]
            for key, points in fibres.items():
                widths.append(max(p[1] for p in points)-min(p[1] for p in points))
                if r>=2:
                    a,b=interval(dict(key),r,'0')
                    c,d=interval(dict(key),r,'1')
                    assert points==set(product(range(a,b+1),range(c,d+1)))
                    rectangles+=1
            fibres_seen+=len(fibres)
            observed=max(widths,default=0)
            assert observed==worst(n,r), (n,r,observed,worst(n,r))
            profiles.append([n,r,len(fibres),observed])
        if n>=4 and negative is None:
            seen={}
            for w in words:
                key=tuple(tuple(sorted(x)) for x in rs[w])
                h=histogram(w,4)
                if key in seen and h!=histogram(seen[key],4):
                    negative=[seen[key],w]
                    break
                seen[key]=w
    cases=0
    for l in range(1,7):
        for e in range(13):
            for s in range(1,8):
                actual={(sum(x>=s for x in xs),sum(max(0,x-s+1) for x in xs)) for xs in compositions(e,l)}
                predicted={(q,g) for q in range(l+1) for g in range(e+1)
                           if q<=g and (q==0)==(g==0) and
                           q*(s-1)+g<=e<=l*(s-1)+g}
                assert actual==predicted,(l,e,s)
                cases+=1
    return dict(words_by_horizon=words_seen, fibres=fibres_seen, joint_rectangles=rectangles,
                gate_frontiers=cases, run_histogram_counterexample=negative, profiles=profiles)


def render(out):
    a='0'+'1'*9
    a*=4
    b=('0'+'1'*3)*3+'0'+'1'*27
    assert len(a)==len(b)==40 and histogram(a,4)==histogram(b,4)
    assert histogram(a,5)!=histogram(b,5)
    slot=[round(4500*sin(2*pi*(i%16)/16)) for i in range(640)]
    receipts={}
    for name,w in [('balanced',a),('concentrated',b)]:
        pcm=[v for bit in w for v in (slot if bit=='1' else [0]*640)]
        dest=out/(name+'.wav')
        with wave.open(str(dest),'wb') as f:
            f.setparams((1,2,8000,0,'NONE','not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
        receipts[name]=dict(word=w,peak=max(runs(w,'1')),energy=sum(v*v for v in pcm),
                            sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    assert receipts['balanced']['energy']==receipts['concentrated']['energy']
    assert receipts['balanced']['sha256']!=receipts['concentrated']['sha256']
    return receipts


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('build'))
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    result=census()
    result['audio']=render(args.out)
    result['status']='PASS'
    (args.out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k!='profiles'})
