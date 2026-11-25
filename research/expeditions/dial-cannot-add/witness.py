"""Original sonification of four contradictory priority comparisons; no listener data."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib, json, math, struct, wave

R=((1,2,3,6),(4,5,8,9),(7,10,11,12))
PAIRS=(((0,2),(1,0)),((1,1),(0,3)),((2,0),(1,2)),((1,3),(2,1)))
LOCAL=(((0,1,2),(0,5,8),(0,2,4)),((0,1,3),(0,3,8),(0,2,6)),
       ((0,2,3),(0,5,8),(0,4,6)),((1,2,3),(0,3,8),(0,2,4)))

def verify():
    for cols,a,b in LOCAL:
        vals=[(R[i][j],a[i]+b[k]) for i in range(3) for k,j in enumerate(cols)]
        s=[v for _,v in sorted(vals)]; assert all(x<y for x,y in zip(s,s[1:]))
    for axis in (0,1):
        assert sorted(p[0][axis] for p in PAIRS)==sorted(p[1][axis] for p in PAIRS)
    def base(c): return 4*c[0]+2*c[1]
    def repaired(c): return base(c)+ (F(1,2) if R[c[0]][c[1]] in (4,6,8,10,12) else F(-1,2))
    s=[repaired(c) for c in sorted(((i,j) for i in range(3) for j in range(4)),key=lambda c:R[c[0]][c[1]])]
    assert min(y-x for x,y in zip(s,s[1:]))==1
    assert all(base(lo)==base(hi) and repaired(hi)-repaired(lo)==1 for lo,hi in PAIRS)
    return base,repaired


def render(path,score):
    rate=8000; length=1600; gap=480; samples=[]
    for lo,hi in PAIRS:
        for c in (lo,hi):
            freq=220+35*float(score(c))
            samples.extend(round(10000*math.sin(2*math.pi*freq*t/rate)*math.sin(math.pi*t/(length-1))**2) for t in range(length))
            samples.extend([0]*gap)
        samples.extend([0]*gap)
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    return dict(samples=len(samples),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

if __name__=='__main__':
    base,repaired=verify(); out=Path(__file__).parent/'results';out.mkdir(exist_ok=True)
    receipt={name:render(out/name,fn) for name,fn in [('additive-ties.wav',base),('interaction-repair.wav',repaired)]}
    print(json.dumps(receipt,indent=2))
