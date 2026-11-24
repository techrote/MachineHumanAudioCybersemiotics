"""Independent Fourier solve and LP oracle; deterministic synthetic WAV render."""
from pathlib import Path
from itertools import combinations
import hashlib, json, math, wave
import numpy as np
from scipy.optimize import linprog
from erasure import certificate, two_erasure_gain, one_remaining_gain


def basis(t,m):
    t=np.asarray(t)
    return np.column_stack([np.ones_like(t)]+[f(k*t) for k in range(1,m+1) for f in (np.cos,np.sin)])


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    count=0; max_rel=0.; census=[]
    for M in range(5,17):
        for r in range(1,min(4,M-1)+1):
            if (M-r)%2==0: continue
            m=(M-r-1)//2
            A=basis(2*np.pi*np.arange(M)/M,m)
            worst=(-1,None); least=(float('inf'),None)
            # rotational symmetry: move target to zero
            for tail in combinations(range(1,M),r-1):
                E=(0,)+tail
                c=certificate(M,E,0); J=list(c['weights'])
                w=np.linalg.solve(A[J].T,A[0])
                expected=np.array(list(c['weights'].values()))
                rel=float(np.max(np.abs(w-expected))/max(1,np.max(np.abs(expected))))
                max_rel=max(max_rel,rel); assert rel<2e-9
                gain=c['gain']; assert abs(np.dot(w,list(c['witness'].values()))-gain)<2e-9*gain
                if r==2: assert abs(gain-two_erasure_gain(M,tail[0]))<2e-9*gain
                if gain>worst[0]: worst=(gain,E)
                if gain<least[0]: least=(gain,E)
                count+=1
            census.append(dict(M=M,r=r,minimum=least,maximum=worst))
    lp_count=0; extra=[]
    for M in range(5,42,2):
        m=(M-3)//2; A=basis(2*np.pi*np.arange(M)/M,m)
        J=list(range(1,M))
        opt=linprog(-A[0],A_ub=np.vstack((A[J],-A[J])),b_ub=np.ones(2*len(J)),bounds=[(None,None)]*A.shape[1],method='highs')
        assert opt.success
        assert abs(-opt.fun-one_remaining_gain(M))<1e-8*M
        lp_count+=1
        extra.append(dict(M=M,adjacent=two_erasure_gain(M,1),spread=two_erasure_gain(M,M//2),one_remaining=one_remaining_gain(M)))
    # Explicit negative control: n-1 retained rows leave a nonzero nullspace.
    A=basis(2*np.pi*np.arange(9)/9,3)
    _,_,vh=np.linalg.svd(A[3:]); v=vh[-1]
    assert np.max(np.abs(A[3:]@v))<1e-12 and np.max(np.abs(A[:3]@v))>0.1
    # Audio: same retained amplitude bound, worst witness for adjacent vs separated erasures.
    M=9; m=3; A=basis(2*np.pi*np.arange(M)/M,m); sr=16000; period=80
    channels=[]; audio_cases=[]
    for d in (1,4):
        c=certificate(M,(0,d),0); J=list(c['weights'])
        coeff=np.linalg.solve(A[J],list(c['witness'].values()))
        y=basis(2*np.pi*np.arange(period)/period,m)@coeff
        channels.append(y); audio_cases.append(dict(erased=[0,d],gain=c['gain'],full_grid=(A@coeff).tolist(),dense_peak=float(np.max(np.abs(y)))))
    scale=.85/max(np.max(np.abs(y)) for y in channels)
    pcm=np.rint(np.tile(np.column_stack(channels),(400,1))*scale*32767).astype('<i2')
    path=out/'erasure-witness.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr); f.writeframes(pcm.tobytes())
    result=dict(cases=count,max_relative_weight_discrepancy=max_rel,lp_checks=lp_count,census=census,two_erasure=extra,audio=dict(cases=audio_cases,common_scale=float(scale),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=len(pcm),sample_rate=sr),versions=dict(numpy=np.__version__))
    (out/'results.synthetic.txt').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('census','two_erasure')},indent=2))


if __name__=='__main__':
    run(Path(__file__).parent/'run')
