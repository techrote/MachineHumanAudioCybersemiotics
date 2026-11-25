"""Exact synthetic witness and PCM receipt renderer; no external dependencies."""
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial, sin, pi, sqrt
from pathlib import Path
import hashlib, json, struct, wave


def column(t, B):
    return [comb(B-1,j)*t**j*(1-t)**(B-1-j) for j in range(B)]


def det(A):
    A = [list(map(F, row)) for row in A]
    d = F(1)
    for j in range(len(A)):
        p = next((i for i in range(j,len(A)) if A[i][j]), None)
        if p is None:
            return F(0)
        if p != j:
            A[p],A[j] = A[j],A[p]
            d = -d
        v = A[j][j]
        d *= v
        for i in range(j+1,len(A)):
            r = A[i][j]/v
            for l in range(j,len(A)):
                A[i][l] -= r*A[j][l]
    return d


def mixtures(B,s,L=6):
    C = [column(F(i+1,L),B) for i in range(s+1)]
    v = [(-1)**i*comb(s,i) for i in range(s+1)]
    return [[sum((F(sign*x,2**(s-1))*C[i][j] for i,x in enumerate(v) if sign*x>0),F(0)) for j in range(B)] for sign in (1,-1)]


def render(path, powers):
    # Same oscillator phases for identical aggregate power receipts; not a microphone model.
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,8000,0,'NONE','not compressed'))
        samples = []
        for n in range(8000):
            x = sum(sqrt(float(p))*sin(2*pi*(300+200*j)*n/8000) for j,p in enumerate(powers))
            taper = min(1,n/160,(7999-n)/160)
            samples.append(round(10000*taper*x/sqrt(len(powers))))
        f.writeframes(struct.pack('<8000h',*samples))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    checks = 0
    for B in range(2,7):
        C = [column(F(i+1,7),B) for i in range(6)]
        for s in range(1,B+1):
            for R in combinations(range(B),s):
                for I in combinations(range(6),s):
                    assert det([[C[i][j] for i in I] for j in R]) > 0
                    checks += 1
    conditioning = []
    for k in range(1,6):
        m = 2*k-1
        for L in (20,100,1000):
            P,Q = mixtures(m+1,m,L)
            tv = sum(abs(x-y) for x,y in zip(P,Q))/2
            assert tv == F(factorial(m),L**m)
            conditioning.append([k,L,str(tv)])
    files, powers = {}, {}
    for B,s in ((3,3),(4,4),(5,4)):
        P,Q = mixtures(B,s)
        assert sum(P)==sum(Q)==1
        assert (P==Q)==(B<=s)
        for tag,p in (('a',P),('b',Q)):
            name = f'bands-{B}-{tag}.wav'
            files[name] = render(out/name,p)
            powers[name] = list(map(str,p))
        assert (files[f'bands-{B}-a.wav']==files[f'bands-{B}-b.wav'])==(B<=s)
    return {'fraction_minor_checks':checks,'conditioning':conditioning,'powers':powers,'sha256':files,'assertions':'PASS'}


if __name__ == '__main__':
    print(json.dumps(run(Path(__file__).parent/'results'),indent=2,sort_keys=True))
