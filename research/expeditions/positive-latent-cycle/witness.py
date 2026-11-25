"""Synthetic cycle support specimens and exact capped-mixture cross-check."""
from fractions import Fraction as F
from itertools import combinations, product
from collections import Counter
from pathlib import Path
import hashlib, json, math, random, struct, wave
ROOT=Path(__file__).resolve().parent

def allowed(i,j,n): return j==i or j==(i+1)%n

def vertices(n,D,T):
    m,r=divmod(T,D)
    for full in combinations(range(n),m):
        for extra in (set(range(n))-set(full) if r else [None]):
            yield tuple(D if i in full else r if i==extra else 0 for i in range(n))

def capcheck():
    profiles=pairs=0
    for n in range(3,7):
        for D in (2,3,5):
            for T in range(1,n*D+1):
                vs=list(vertices(n,D,T)); best=0
                for x in vs:
                    w=[x[j]+x[(j-1)%n] for j in range(n)]
                    for y in vs:
                        best=max(best,sum(a*b for a,b in zip(w,y))); pairs+=1
                expected=T*T if T<=D else 2*T*D-D*D+max(0,T-(n-1)*D)**2
                assert best==expected,(n,D,T,best,expected)
                profiles+=1
    return dict(profiles=profiles,pairs=pairs)

def tensorcheck():
    out=[]
    for n,d in [(3,1),(4,1),(6,1),(8,1),(3,2),(4,2)]:
        V=list(product(range(n),repeat=d)); N=len(V)
        A=[{j for j,y in enumerate(V) if all(allowed(a,b,n) for a,b in zip(x,y))} for x in V]
        best=0; rect=0
        for r in range(1,N+1):
            for ix in combinations(range(N),r):
                cols=set.intersection(*(A[i] for i in ix)); best=max(best,r*len(cols));rect+=2**len(cols)-1
        assert best==2**d
        out.append(dict(n=n,d=d,max_rectangle=best,rectangles=rect))
    return out

def block(n,k):
    assert n%k==0
    t=n//k
    return [(i,j%n) for b in range(k) for i in range(b*t,(b+1)*t) for j in range(b*t+1,(b+1)*t+1)]

def tv(p,q):
    return sum(abs(p.get(c,0)-q.get(c,0)) for c in p.keys()|q.keys())/2

def distribution(cells): return {x:F(v,len(cells)) for x,v in Counter(cells).items()}

def render(name,cells,n=8):
    assert len(cells)==64
    rng=random.Random(618);cells=list(cells);rng.shuffle(cells)
    rate=8000; slot=640
    tones=[tuple(round(9500*math.sin(2*math.pi*(250+50*i)*j/rate)*math.sin(math.pi*j/slot)**2) for j in range(slot)) for i in range(n)]
    path=ROOT/'audio'/f'{name}.wav';path.parent.mkdir(exist_ok=True)
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed'))
        w.writeframes(b''.join(struct.pack('<hh',a,b) for i,j in cells for a,b in zip(tones[i],tones[j])))
    with wave.open(str(path),'rb') as w: raw=struct.unpack('<'+'h'*(w.getnframes()*2),w.readframes(w.getnframes()))
    decoded=[]
    for offset in range(0,len(raw),2*slot):
        decoded.append(tuple(max(range(n),key=lambda k:sum(a*b for a,b in zip(raw[offset+c:offset+2*slot:2],tones[k]))) for c in (0,1)))
    assert decoded==cells
    assert Counter(i for i,j in decoded)==Counter(j for i,j in decoded)==Counter({i:8 for i in range(n)})
    return dict(name=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),decoded_slots=len(decoded),forbidden=sum(not allowed(i,j,n) for i,j in decoded),left_counts=[8]*n,right_counts=[8]*n)

def main():
    n=8; target=[(i,j) for i in range(n) for j in (i,(i+1)%n)]; compressed=block(n,4);independent=list(product(range(n),repeat=2))
    P=distribution(target); Q=distribution(compressed);U=distribution(independent)
    assert tv(P,Q)==F(1,4) and tv(P,U)==F(3,4)
    result=dict(cap=capcheck(),tensor=tensorcheck(),audio=[render('target',target*4),render('four-parents',compressed*4),render('one-parent',independent)],tv={'four_parents':str(tv(P,Q)),'one_parent':str(tv(P,U))},assertions='PASS')
    (ROOT/'native-execution.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
