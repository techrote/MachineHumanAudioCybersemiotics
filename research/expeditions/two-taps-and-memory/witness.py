"""Exact finite synthetic witness for MHAC #733 (Python >=3.11, stdlib)."""
from fractions import Fraction as Q
from itertools import combinations, product
from math import prod, factorial
from pathlib import Path
import json, wave, struct, hashlib


def h(p, a, d, l):
    return p*p*a**3*(int((l-d)%p==0)-int((l+d)%p==0))


def active(ps,d,l):
    return tuple(p for p in ps if h(p,1,d,l))


def compile_pair(ps,i,j):
    D=prod(p for p in ps if p not in (i,j))
    return (D,D) if 2*D<j else ((j-i)//2,(j+i)//2)


def component(p,a,d,r):
    return p*a*(int(r%p==0)-int((r+d)%p==0))


def midpoint(ps, amps,d,l):
    # Truncated exponential-generating polynomial, keeping even total degree
    # for each independent private component; coefficient (3,3) times 3!^2.
    pol={(0,0):Q(1)}
    for p,a in zip(ps,amps):
        vals=[(component(p,a,d,r),component(p,a,d,r+l)) for r in range(p)]
        nxt={}
        for u,v in product(range(4),repeat=2):
            if (u+v)%2: continue
            m=Q(sum(z**u*w**v for z,w in vals),p*factorial(u)*factorial(v))
            for (i,j),b in pol.items():
                if i+u<=3 and j+v<=3:
                    key=i+u,j+v
                    nxt[key]=nxt.get(key,Q(0))+b*m
        pol=nxt
    return 36*pol.get((3,3),0)


def predict(ps,amps,s,d,l):
    hs=[h(p,a,d,l) for p,a in zip(ps,amps)]
    return midpoint(ps,amps,d,l)-18*sum(hs[i]*hs[j]*s[i]*s[j] for i,j in combinations(range(len(ps)),2))


def signal(ps,amps,s):
    return [(-1)**(t%2)*sum(a*sg*(p*int(t%p==0)-1) for p,a,sg in zip(ps,amps,s)) for t in range(2*prod(ps))]


def filtered(x,d):
    k=d%len(x)
    return [u-(-1)**(d%2)*v for u,v in zip(x,x[k:]+x[:k])]


def receipt(y,l):
    z=[v**3 for v in y]; k=l%len(z)
    return Q((-1)**(l%2)*sum(u*v for u,v in zip(z,z[k:]+z[:k])),len(z))


def write_wav(path,x,rate,repeats,scale):
    vals=[v*scale for v in x]*repeats
    assert max(map(abs,vals))<=32767
    data=struct.pack('<'+'h'*len(vals),*vals)
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed')); f.writeframes(data)
    with wave.open(str(path),'rb') as f:
        assert f.readframes(f.getnframes())==data
    return {'frames':len(vals),'peak':max(map(abs,vals)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    counts={'local_mixed_moments':0,'aperture_optima':0,'candidate_apertures':0,'literal_receipts':0,'one_tap_negative':0,'gain_checks':0}
    for p in (3,5,7,11,13,17):
        for a,d,l in product((1,2),range(1,p+1),range(p+1)):
            z=[component(p,a,d,r) for r in range(p)]
            w=[component(p,a,d,r+l) for r in range(p)]
            assert sum(v**3 for v in z)==sum(v**3 for v in w)==0
            assert Q(sum(u*u*v for u,v in zip(z,w)),p)==h(p,a,d,l)
            assert Q(sum(u*v*v for u,v in zip(z,w)),p)==-h(p,a,d,l)
            counts['local_mixed_moments']+=1
    for n in range(2,6):
        for ps in combinations((3,5,7,11,13,17),n):
            for i,j in combinations(ps,2):
                d,l=compile_pair(ps,i,j); assert active(ps,d,l)==(i,j)
                for b in range(2,d+l):
                    for k in range(1,b):
                        assert active(ps,k,b-k)!=(i,j)
                        counts['candidate_apertures']+=1
                counts['aperture_optima']+=1
            for l in range(2*max(ps)+1):
                for i,j in combinations(ps,2):
                    a=(i-1)*(i-2); b=(j-1)*(j-2)
                    c=a if l%i==0 else -(i-2); e=b if l%j==0 else -(j-2)
                    assert 2*a*b+18*c*e!=0
                    counts['one_tap_negative']+=1
    for ps,amps in [((3,5),(1,2)),((3,5,7),(2,1,1)),((5,7,11),(1,1,1))]:
        for tail in product((-1,1),repeat=len(ps)-1):
            s=(1,)+tail; x=signal(ps,amps,s)
            for d,l in product(range(1,9),range(9)):
                y=filtered(x,d); actual=receipt(y,l)
                assert actual==predict(ps,amps,s,d,l)
                counts['literal_receipts']+=1
            for i,j in combinations(ps,2):
                d,l=compile_pair(ps,i,j); y=filtered(x,d)
                power=Q(sum(v*v for v in y),len(y))
                assert power==2*sum(p*a*a for p,a in zip(ps,amps) if d%p)
                assert receipt([3*v for v in y],l)/(9*power)**3==receipt(y,l)/power**3
                counts['gain_checks']+=1
    ps=(5,7,11,13,17); amps=(1,)*5; d,l=compile_pair(ps,5,17)
    cases=[]
    for s in [(1,1,1,-1,1),(1,1,1,-1,-1)]:
        x=signal(ps,amps,s); y=filtered(x,d)
        actual=receipt(y,l); assert actual==predict(ps,amps,s,d,l)
        counts['literal_receipts']+=1
        cases.append({'signs':s,'raw_sixth':str(Q(sum(v**6 for v in x),len(x))),'lagged_cubic':str(actual),'power':str(Q(sum(v*v for v in y),len(y)))})
    assert cases[0]['raw_sixth']==cases[1]['raw_sixth']=='5111904'
    assert Q(cases[0]['lagged_cubic'])-Q(cases[1]['lagged_cubic'])==260100
    # Small exact PCM specimens: two-tap filtered signals and cubic outputs.
    ps=(5,7,11); amps=(1,1,1); d,l=compile_pair(ps,5,7); audio={}; small=[]
    for name,s in [('plus',(1,1,1)),('minus',(1,-1,1))]:
        y=filtered(signal(ps,amps,s),d); val=receipt(y,l)
        small.append({'signs':s,'lagged_cubic':str(val),'zero_lag_cubic':str(receipt(y,0))})
        for kind,arr,scale in [('filtered',y,500),('cubed',[v**3 for v in y],1)]:
            fn=f'{kind}-{name}.wav'; audio[fn]=write_wav(Path(__file__).parent/fn,arr,15400,20,scale)
    assert small[0]['zero_lag_cubic']==small[1]['zero_lag_cubic']
    assert Q(small[0]['lagged_cubic'])-Q(small[1]['lagged_cubic'])==44100
    report={'counts':counts,'five_prime_collision':cases,'small_pcm':small,'audio':audio,'status':'pass'}
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=='__main__': main()
