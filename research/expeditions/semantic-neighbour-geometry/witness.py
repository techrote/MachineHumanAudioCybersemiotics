#!/usr/bin/env python3
"""Independent exact Gram checks, ternary grid search, and PCM codebooks for #600."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from math import sqrt, sin, pi
import hashlib, json, struct, wave

ROOT = Path(__file__).resolve().parent

def centered_gram(D):
    k = len(D)
    rows = [sum(row)/k for row in D]
    total = sum(rows)/k
    return [[-(D[i][j]-rows[i]-rows[j]+total)/2 for j in range(k)] for i in range(k)]

def psd_rank(G):
    """Exact symmetric elimination; negative diagonal or nonzero zero-pivot row rejects PSD."""
    A = [row[:] for row in G]
    rank = 0
    while A:
        if any(A[i][i] < 0 for i in range(len(A))):
            return False, rank
        piv = next((i for i in range(len(A)) if A[i][i] > 0), None)
        if piv is None:
            return not any(v for row in A for v in row), rank
        idx = [i for i in range(len(A)) if i != piv]
        A = [[A[i][j]-A[i][piv]*A[piv][j]/A[piv][piv] for j in idx] for i in idx]
        rank += 1
    return True, rank

def distances(m,n,far,near):
    return [[F(0) if i==j else far if (i<m)==(j<m) else near for j in range(m+n)] for i in range(m+n)]

def exact_geometry():
    profiles = equal_energy = 0
    for m,n in product(range(2,10), repeat=2):
        a,b = 2*F(m-1,m),2*F(n-1,n)
        assert psd_rank(centered_gram(distances(m,n,F(4),a+b))) == (True,m+n-2)
        assert not psd_rank(centered_gram(distances(m,n,F(4),a+b-F(1,100))))[0]
        cutoff = 4/(a+b)
        assert psd_rank(centered_gram(distances(m,n,cutoff,F(1)))) == (True,m+n-2)
        assert psd_rank(centered_gram(distances(m,n,(1+cutoff)/2,F(1)))) == (True,m+n-1)
        assert not psd_rank(centered_gram(distances(m,n,cutoff+F(1,100),F(1))))[0]
        profiles += 1
        for j in [1,2,3,5,10]:
            diff=abs(a-b)/j
            u,v=(j+diff)/2,(j-diff)/2
            E=min(a,b)+u*u
            assert E==max(a,b)+v*v
            c=a+b+diff*diff
            D=distances(m,n,F(4),c)
            G=[[E-D[i][k]/2 for k in range(m+n)] for i in range(m+n)]
            expected=m+n-1 # positive centroid axis; j>=1, all a,b>0, common centre not zero
            assert psd_rank(G)==(True,expected)
            if a!=b:
                eps=diff*diff
                assert E==(a+b)/2+eps/4+(a-b)**2/(4*eps)
            equal_energy+=1
    return dict(gram_profiles=profiles,gram_certificates=profiles*5,equal_energy_gram_profiles=equal_energy)

def ternary_search():
    """Literal finite grid search, not a proof of the continuous lower bound."""
    checked=0; results=[]; examined=0
    for d in (1,2,3):
        pts=list(product((-1,0,1), repeat=d))
        ds=[[max(abs(x-y) for x,y in zip(a,b)) for b in pts] for a in pts]
        for m,n in product(range(2,5), repeat=2):
            found=False
            for A in combinations(range(len(pts)),m):
                examined+=1
                if any(ds[i][j]!=2 for i,j in combinations(A,2)):continue
                eligible=[i for i in range(len(pts)) if all(ds[i][j]==1 for j in A)]
                if any(all(ds[i][j]==2 for i,j in combinations(B,2)) for B in combinations(eligible,n)):
                    found=True;break
            need=(m-1).bit_length()+(n-1).bit_length()
            assert found==(d>=need),(m,n,d,found)
            results.append([m,n,d,found]);checked+=1
    return dict(ternary_profiles=checked,first_class_sets_examined=examined,profiles=results)

def vectors(m,n,E=None,maximum_norm=False):
    if maximum_norm:
        p,q=(m-1).bit_length(),(n-1).bit_length()
        return [[(1 if (i>>j)&1 else -1) if j<p else 0 for j in range(p+q)] for i in range(m)]+[[0 if j<p else (1 if (i>>(j-p))&1 else -1) for j in range(p+q)] for i in range(n)]
    out=[]
    for i in range(m+n):
        k,lo=(m,0) if i<m else (n,m)
        v=[sqrt(2)*((j==i)-1/k) if lo<=j<lo+k else 0 for j in range(m+n)]
        v.append(0 if E is None else sqrt(max(0,E-2*(1-1/k))))
        out.append(v)
    return out

def pcm():
    (ROOT/'audio').mkdir(exist_ok=True)
    m,n=2,6;sr=8000;N=1600;gap=400;gain=.08;scale=32767*gain
    out={}
    for name,E,inf in [('free',None,False),('equal-low',5/3,False),('equal-high',8,False),('max-coordinate',None,True)]:
        V=vectors(m,n,E,inf); basis=[[sqrt(2)*sin(2*pi*(200+100*j)*i/sr) for i in range(N)] for j in range(len(V[0]))]
        tokens=[[round(scale*sum(c*basis[j][i] for j,c in enumerate(v))) for i in range(N)] for v in V]
        assert max(abs(s) for t in tokens for s in t)<32767
        energy=[sum(s*s for s in t)/(N*scale**2) for t in tokens]
        def sd(x,y):return sum((a-b)**2 for a,b in zip(x,y))/(N*scale**2)
        err=max(abs(sd(tokens[i],tokens[j])-sum((a-b)**2 for a,b in zip(V[i],V[j]))) for i,j in combinations(range(m+n),2))
        assert err<.002,err
        if E is not None:assert max(abs(e-E) for e in energy)<.002
        if inf:
            assert all(max(abs(a-b) for a,b in zip(V[i],V[j]))==(2 if (i<m)==(j<m) else 1) for i,j in combinations(range(m+n),2))
        cross=[sd(tokens[i],tokens[j]) for i in range(m) for j in range(m,m+n)]
        payload=[s for t in tokens for s in t+[0]*gap]
        path=ROOT/'audio'/f'{name}.wav'
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes(struct.pack('<'+'h'*len(payload),*payload))
        out[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),energy_min=min(energy),energy_max=max(energy),cross_squared_min=min(cross),cross_squared_max=max(cross),max_distance_squared_error=err,coefficients=V)
    return dict(sample_rate=sr,token_samples=N,gap_samples=gap,common_gain=gain,codebooks=out)

if __name__=='__main__':
    result=dict(exact=exact_geometry(),search=ternary_search(),audio=pcm())
    (ROOT/'native-execution.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({**result['exact'],**{k:v for k,v in result['search'].items() if k!='profiles'},'audio':{k:{l:v for l,v in r.items() if l!='coefficients'} for k,r in result['audio']['codebooks'].items()}},indent=2))
