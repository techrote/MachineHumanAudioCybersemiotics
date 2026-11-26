"""Independent literal rational checks and synthetic score renderer for MHAC #686.
Same agent; no physical channel or listening trial. Standard library only.
"""
from fractions import Fraction as F
from itertools import product, combinations
from math import comb, factorial, log, pi, sin
from pathlib import Path
from random import Random
from collections import Counter
import hashlib, json, struct, wave

ROOT = Path(__file__).resolve().parent

def solve(a,b):
    a=[list(map(F,row))+[F(v)] for row,v in zip(a,b)]
    n=len(a)
    for j in range(n):
        i=next(i for i in range(j,n) if a[i][j]); a[j],a[i]=a[i],a[j]
        z=a[j][j]; a[j]=[x/z for x in a[j]]
        for i in range(n):
            if i!=j:
                z=a[i][j]; a[i]=[x-z*y for x,y in zip(a[i],a[j])]
    return [r[-1] for r in a]

def moment(law,k): return sum((w*t**k for t,w in law), F(0))
def rows(law): return [[w*(1+s*t) for t,w in law] for s in (1,-1)]
def mi(K,p):
    out=[sum(p[i]*K[i][j] for i in range(len(p))) for j in range(len(K[0]))]
    return sum(float(p[i]*K[i][j])*log(float(K[i][j]/out[j])) for i in range(len(p)) for j in range(len(out)) if p[i] and K[i][j])

def main():
    counts=Counter(); examples=[]
    for m in range(2,13):
        n=2*m-1; grid=[F(2*j-n,n+1) for j in range(n+1)]
        A=[(grid[j],F(comb(n,j),2**(n-1))) for j in range(0,n+1,2)]
        B=[(grid[j],F(comb(n,j),2**(n-1))) for j in range(1,n+1,2)]
        for k in range(n):
            assert moment(A,k)==moment(B,k); counts['exact_moment_matches']+=1
        assert moment(A,n)!=moment(B,n)
        for law in (A,B):
            K=rows(law); assert all(sum(r)==1 for r in K)
            M=[moment(law,k) for k in range(2*m)]
            coeff=solve([[M[i+j] for j in range(m)] for i in range(m)],[-M[m+i] for i in range(m)])+[F(1)]
            roots=[t for t in grid if sum(c*t**j for j,c in enumerate(coeff))==0]
            assert len(roots)==m
            weights=solve([[t**j for t in roots] for j in range(m)],M[:m])
            assert list(zip(roots,weights))==law; counts['exact_hankel_reconstructions_on_known_grid']+=1
        for u in [F(j,8) for j in range(-7,8)]:
            assert abs(mi(rows(A),[(1+u)/2,(1-u)/2])-mi(rows(B),[(1-u)/2,(1+u)/2]))<1e-14
            counts['literal_entropy_reflection_checks']+=1
    for n in range(3,8):
        ss=list(product((-1,1),repeat=n)); A=[s for s in ss if sum(v==-1 for v in s)%2==0]; B=[s for s in ss if s not in A]
        e=F(1,2); K=lambda S:[[F(1+e*s[i],len(S)) for s in S] for i in range(n)]
        ka,kb=K(A),K(B)
        for r in range(1,n):
            for T in combinations(range(n),r):
                assert Counter(tuple(s[i] for i in T) for s in A)==Counter(tuple(s[i] for i in T) for s in B)
                counts['proper_support_counter_checks']+=1
        for l in range(1,n+1):
            val=lambda K:sum(sum(sorted(col,reverse=True)[:l]) for col in zip(*K))/n
            assert val(ka)-val(kb)==(F(0) if l==n else F((-1)**(n+l)*comb(n-2,l-1),n*2**(n-1)))
            counts['literal_shortlist_checks']+=1
        p=[F(1,n)]*n; gap=mi(ka,p)-mi(kb,p)
        assert gap*(-1)**(n+1)>0
        examples.append({'states':n,'plus_minus_nats':gap})
    audio={}
    for name,K in [('A',[[1,15],[7,9]]),('B',[[9,7],[15,1]])]:
        episodes=[(i,j) for i in range(2) for j in range(2) for _ in range(K[i][j])]
        Random(686).shuffle(episodes)
        rate=8000; length=640; frequencies=[300,500]; buf=bytearray()
        # left channel: known test input; right channel: observed tone
        templates=[[int(round(11000*sin(2*pi*f*t/rate)*sin(pi*t/(length-1))**2)) for t in range(length)] for f in frequencies]
        for i,j in episodes:
            for a,b in zip(templates[i],templates[j]): buf.extend(struct.pack('<hh',a,b))
        path=ROOT/f'channel-{name}.wav'
        with wave.open(str(path),'wb') as w: w.setparams((2,2,rate,0,'NONE','not compressed')); w.writeframes(buf)
        with wave.open(str(path),'rb') as w: data=list(struct.iter_unpack('<hh',w.readframes(w.getnframes())))
        decoded=[]
        for offset in range(0,len(data),length):
            block=data[offset:offset+length]
            decoded.append(tuple(min(range(2),key=lambda j:sum((x[c]-y)**2 for x,y in zip(block,templates[j]))) for c in range(2)))
        assert decoded==episodes
        counts['pcm_symbol_bits']+=2*len(decoded)
        assert [[decoded.count((i,j)) for j in range(2)] for i in range(2)]==K
        audio[name]={'counts':K,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(decoded),'seconds':len(data)/rate}
    result={'status':'PASS','counts':dict(counts),'positive_parity_examples':examples,'audio':audio,'limits':'Hankel root search uses the known fixture grid; numerical entropy checks are not proofs. Synthetic PCM only; no physical channel or human listening.'}
    (ROOT/'native-execution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
