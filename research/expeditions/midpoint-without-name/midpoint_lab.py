"""Synthetic exact inverse-calibration bounds and an original PCM score."""
from fractions import Fraction as F
from itertools import product, accumulate
from pathlib import Path
import hashlib, json, struct, wave, argparse


def bounds(t, anchors=((F(0), F(0)), (F(1), F(1))), lo=F(1,2), hi=F(2)):
    """Exact feasible x interval for f(x)=t, given secant slope bounds."""
    t, lo, hi = map(F, (t, lo, hi))
    a = tuple((F(x), F(y)) for x,y in anchors)
    if not (0 < lo <= hi and 0 <= t <= 1 and len(a)>=2 and a[0]==(0,0) and a[-1]==(1,1)):
        raise ValueError('invalid domain or bounds')
    for (x,y),(z,w) in zip(a,a[1:]):
        if not (z>x and lo*(z-x)<=w-y<=hi*(z-x)):
            raise ValueError('inconsistent anchors')
    for (x,y),(z,w) in zip(a,a[1:]):
        if y<=t<=w:
            return max(x+(t-y)/hi,z-(w-t)/lo), min(x+(t-y)/lo,z-(w-t)/hi)
    raise AssertionError('no containing segment')


def witness(t,x,anchors=((F(0),F(0)),(F(1),F(1))),lo=F(1,2),hi=F(2)):
    t,x=F(t),F(x)
    low,high=bounds(t,anchors,lo,hi)
    if not low<=x<=high: raise ValueError('outside feasible interval')
    return tuple(sorted(set(tuple((F(a),F(b)) for a,b in anchors)+((x,t),))))


def interp(points,t):
    t=F(t)
    for (x,y),(z,w) in zip(points,points[1:]):
        if x<=t<=z:return y+(w-y)*(t-x)/(z-x)
    raise ValueError('outside chart')


def grid_census():
    ts=[F(i,16) for i in range(17)]
    groups={None:[[],[]], F(1,2):[[],[]], F(3,8):[[],[]]}
    # Independent discretized search: increments of 1..4 sixteenths across eight equal x cells.
    ranges={k:{t:[F(1),F(0)] for t in ts} for k in groups}
    counts={k:0 for k in groups}
    for d in product(range(1,5),repeat=8):
        if sum(d)!=16:continue
        ys=(0,*accumulate(d)); keys=[None]
        if F(ys[4],16) in (F(1,2),F(3,8)):keys.append(F(ys[4],16))
        for k in keys:counts[k]+=1
        j=0
        for i,t in enumerate(ts):
            while ys[j+1]<i:j+=1
            x=F(j,8)+F(i-ys[j],8*d[j])
            for k in keys:
                r=ranges[k][t];r[0]=min(r[0],x);r[1]=max(r[1],x)
    rows=[]
    for k in groups:
        a=((0,0),(1,1)) if k is None else ((0,0),(F(1,2),k),(1,1))
        for t in ts:
            exact=bounds(t,a); empirical=tuple(ranges[k][t])
            assert exact[0]<=empirical[0]<=empirical[1]<=exact[1]
            rows.append({'anchor_y':str(k),'t':str(t),'exact':list(map(str,exact)),'grid':list(map(str,empirical)),'grid_attains_both':exact==empirical})
    return {'enumerated_increment_vectors':4**8,'valid_charts':{str(k):v for k,v in counts.items()},'rows':rows}


def score(out):
    out.mkdir(parents=True,exist_ok=True)
    # A single gesture, nine t values. Each note restarts phase, fixed amplitude and duration.
    ts=[F(i,8) for i in range(9)]
    charts={'identity':tuple((t,t) for t in ts),'early':witness(F(1,2),F(1,4)),'late':witness(F(1,2),F(3,4))}
    results={}
    for name,chart in charts.items():
        inv=tuple((y,x) for x,y in chart)
        xs=[interp(inv,t) for t in ts]
        hz=[int(200+800*x) for x in xs]
        data=bytearray();rate=16000;length=3200
        for f in hz:
            for n in range(length):
                # integer triangular oscillator, 10 ms ramps; no platform-dependent transcendental functions
                p=(n*f)%rate; tri=4*min(p,rate-p)-rate
                amp=min(n,length-1-n,160)
                sample=tri*7000*amp//(rate*160)
                data.extend(struct.pack('<h',sample))
        path=out/(name+'.wav')
        with wave.open(str(path),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(data)
        results[name]={'frequencies_hz':hz,'x':[str(x) for x in xs],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return results


def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args()
    r={'grid':grid_census(),'score':score(a.out)}
    (a.out/'results.json').write_text(json.dumps(r,indent=2)+'\n')

if __name__=='__main__':main()
