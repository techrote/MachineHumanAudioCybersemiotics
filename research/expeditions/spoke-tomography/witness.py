"""MHAC #690: native exact channel/PCM witness, standard library only."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import hashlib, json, math, random, struct, wave
from pathlib import Path

ROOT=Path(__file__).resolve().parent
A=((5,4,3),(4,3,5),(3,5,4))
B=((3,4,5),(4,5,3),(5,3,4))


def posterior(rows):
    assert all(sum(r)==12 and min(r)>0 for r in rows)
    return {tuple(F(rows[i][j]-4,4) for i in range(3)): F(1,3) for j in range(3)}


def project(law,v):
    c=Counter()
    for p,w in law.items(): c[sum(x*y for x,y in zip(p,v))]+=w
    return c


def curvature(law,v,u):
    return sum(w*t*t/(1+u*t) for t,w in project(law,v).items())


def info(rows,p):
    q=[sum(p[i]*rows[i][j]/12 for i in range(3)) for j in range(3)]
    return sum(p[i]*rows[i][j]/12*math.log((rows[i][j]/12)/q[j]) for i in range(3) for j in range(3))


def reward(law,sgn):
    return sum(w*max(F(0),sgn*(b[0]-b[1])/3-F(1,12)) for b,w in law.items())


def acoustic(rows,name):
    sr, n = 8000, 640
    freqs=(300,500,700)
    template=[[math.sin(2*math.pi*f*k/sr)*math.sin(math.pi*k/(n-1))**2 for k in range(n)] for f in freqs]
    score=[(i,j) for i in range(3) for j in range(3) for _ in range(rows[i][j])]
    random.Random(690).shuffle(score)
    samples=[]
    for i,j in score:
        for k in range(n): samples.extend((round(12000*template[i][k]),round(12000*template[j][k])))
    path=ROOT/name
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,sr,0,'NONE','not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    with wave.open(str(path),'rb') as f:
        data=struct.unpack('<'+'h'*(f.getnframes()*2),f.readframes(f.getnframes()))
    decoded=[]
    for j in range(len(score)):
        vals=[]
        for c in range(2):
            block=data[2*j*n+c:2*(j+1)*n:2]
            vals.append(max(range(3),key=lambda i:sum(x*y for x,y in zip(block,template[i]))))
        decoded.append(tuple(vals))
    assert decoded==score
    assert Counter(decoded)==Counter({(i,j):rows[i][j] for i in range(3) for j in range(3)})
    return {'frames':len(score),'symbol_bits_not_claimed':True,'symbols_decoded':2*len(score),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duration_seconds':len(score)*n/sr}


def main():
    a,b=posterior(A),posterior(B)
    assert set(a).isdisjoint(b)
    assert reward(a,1)==reward(b,-1)==0
    assert reward(a,-1)==reward(b,1)==F(1,36)
    maxgap=0; checks=0
    for axis in range(3):
        v=tuple(F(int(i==axis))-F(1,3) for i in range(3))
        assert project(a,v)==project(b,v)
        for k in range(-49,100):
            u=F(k,100)
            assert curvature(a,v,u)==curvature(b,v,u)
            p=[float(F(1,3)+u*x) for x in v]
            maxgap=max(maxgap,abs(info(A,p)-info(B,p)))
            checks+=1
    assert maxgap<1e-14
    v=(1,-1,0); u=F(1,4)
    assert curvature(a,v,u)!=curvature(b,v,u)
    p=[float(F(1,3)+u*x) for x in v]
    off=info(A,p)-info(B,p)
    assert abs(off)>1e-7
    # Adaptive support-grid reconstruction using exact integer weighted projections.
    rng=random.Random(690); profiles=0; maxgrid=0; maxbase=0
    for d in range(2,6):
        for m in range(2,5):
            for _ in range(15):
                pts=set()
                while len(pts)<m: pts.add(tuple(rng.randrange(-4,5) for _ in range(d)))
                law={p:rng.randrange(1,8) for p in sorted(pts)}
                axes=[tuple(int(j==i) for j in range(d)) for i in range(d)]
                grid=list(product(*(sorted(project(law,v)) for v in axes)))
                t=0
                while True:
                    v=tuple(t**i for i in range(d)); codes=[sum(x*y for x,y in zip(p,v)) for p in grid]
                    if len(set(codes))==len(codes): break
                    t+=1
                inv=dict(zip(codes,grid))
                rebuilt={inv[z]:w for z,w in project(law,v).items()}
                assert rebuilt==law
                profiles+=1; maxgrid=max(maxgrid,len(grid)); maxbase=max(maxbase,t)
    out={'schema':'mhac-690-native-v1','axis_curvature_exact_checks':checks,'max_raw_info_spoke_gap_nats':maxgap,'off_spoke_info_A_minus_B_nats':off,'adaptive_profiles':profiles,'max_candidate_grid':maxgrid,'max_integer_direction_parameter':maxbase,'decision_gap_exact':'1/36','audio':{name:acoustic(rows,name) for rows,name in [(A,'prism-A.wav'),(B,'prism-B.wav')]},'assertion_failures':0,'scope':'Exact synthetic fixtures; numerical raw mutual information; no human or physical transmission tests.'}
    (ROOT/'native-execution.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
