"""Synthetic timing audit: direct release LP vs partial transport LP; PCM comb."""
import hashlib, json, math, random, struct, wave
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
import scipy, sys

OUT = Path(__file__).resolve().parent

def solve(a,b,M,alpha,d,direct):
    n=len(a); L=n+M
    if direct:
        edges=[(s,i,t) for s in range(2) for i in range(n) for t in range(i,i+M+1)]
        N=len(edges); E=np.zeros((2*n,N+L)); G=np.zeros((2*L+1,N+L)); c=np.zeros(N+L)
        c[N:]=-1
        for k,(s,i,t) in enumerate(edges):
            E[s*n+i,k]=1; G[s*L+t,k]=-1; G[-1,k]=(alpha if s==0 else 1-alpha)*(t-i)
        for s in range(2):
            for t in range(L): G[s*L+t,N+t]=1
        res=linprog(c,A_ub=G,b_ub=[0.]*(2*L)+[d],A_eq=E,b_eq=a+b,bounds=(0,None),method='highs')
    else:
        edges=[(i,j) for i in range(n) for j in range(n) if abs(i-j)<=M]
        G=np.zeros((2*n+1,len(edges)))
        for k,(i,j) in enumerate(edges):
            G[i,k]=1; G[n+j,k]=1; G[-1,k]=alpha*max(j-i,0)+(1-alpha)*max(i-j,0)
        res=linprog(-np.ones(len(edges)),A_ub=G,b_ub=a+b+[d],bounds=(0,None),method='highs')
    assert res.success,res.message
    return -res.fun

def main():
    rng=random.Random(715); maxerr=0.; profiles=0
    for _ in range(120):
        n=rng.randint(2,6); M=rng.randrange(n); alpha=rng.choice([0,.2,.5,.8,1.])
        a=[rng.randrange(6) for _ in range(n)]; b=[rng.randrange(6) for _ in range(n)]
        if not sum(a) or not sum(b): continue
        a=[x/sum(a) for x in a]; b=[x/sum(b) for x in b]
        for d in [0.,.1,.5,2.]:
            err=abs(solve(a,b,M,alpha,d,True)-solve(a,b,M,alpha,d,False)); maxerr=max(maxerr,err)
            assert err<1e-8; profiles+=1
    # A and B alternating comb, cap M=1, matched start/answer waveform; 12 episodes.
    n=12; sr=8000; tick=80; frame=4160; width=48; decoded=0; hashes={}; decoded_scores=[]
    pulse=[round(12000*math.sin(2*math.pi*500*k/sr)*math.sin(math.pi*k/(width-1))**2) for k in range(width)]
    for s in (0,1):
        times=[2*(2*j+s) for j in range(n)]; rng.shuffle(times)
        releases=[t+(i%2) for i,t in enumerate(times)]
        pcm=[]
        for t in releases:
            left=[0]*frame; right=[0]*frame; left[:width]=pulse; start=160+tick*t; right[start:start+width]=pulse
            pcm.extend(v for pair in zip(left,right) for v in pair)
        path=OUT/('comb-A.wav' if s==0 else 'comb-B.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((2,2,sr,0,'NONE','not compressed')); f.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
        with wave.open(str(path),'rb') as f: data=struct.unpack('<'+'h'*(f.getnframes()*2),f.readframes(f.getnframes()))
        recovered=[]
        for i,t in enumerate(releases):
            right=data[2*i*frame+1:2*(i+1)*frame:2]
            found=next(k for k,x in enumerate(right) if x)
            first=next(k for k,x in enumerate(pulse) if x)
            assert (found-first-160)%tick==0
            recovered.append((found-first-160)//tick)
        assert recovered==releases; decoded+=len(recovered); decoded_scores.append(recovered)
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert not set(decoded_scores[0]) & set(decoded_scores[1])
    assert max(abs(sum(x<=t for x in decoded_scores[0])-sum(x<=t for x in decoded_scores[1])) for t in range(49))==1
    result={'python':sys.version.split()[0],'scipy':scipy.__version__,'weighted_budget_lp_pairs':profiles,'max_lp_error':maxerr,'pcm_releases_decoded':decoded,'pcm_hashes':hashes,'decoded_scores':decoded_scores,'failures':0}
    (OUT/'native-execution.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
