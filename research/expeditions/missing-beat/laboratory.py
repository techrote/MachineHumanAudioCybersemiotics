"""MHAC #428. Exact onset geometry, bounded census and original PCM witnesses.
Python >=3.11; numpy/scipy used only for independent LP/MILP checks.
Run: python laboratory.py (writes execution.json and WAV files beside script).
"""
from fractions import Fraction as F
from itertools import combinations, product
from functools import lru_cache
from math import gcd, sin, pi, ceil
from pathlib import Path
import hashlib, json, random, struct, wave


def canon(xs):
    if len(xs)<2: return tuple(range(len(xs)))
    return tuple(F(x-xs[0],xs[-1]-xs[0]) for x in xs)


def fingerprints(xs,m):
    return {canon(s) for s in combinations(xs,m)}


def ratios(xs):
    return {F(y-x,z-x) for x,y,z in combinations(xs,3)}


def max_overlap(x,y):
    # Independent registration oracle: try every ordered endpoint pair.
    Y=set(y); best=1
    for a,b in combinations(x,2):
        for c,d in combinations(y,2):
            scale=F(d-c,b-a)
            best=max(best,sum(c+scale*(z-a) in Y for z in x))
    return best


def shapes(L,n):
    return [x for t in combinations(range(1,L+1),n-1)
            if gcd(*t)==1 for x in [(0,)+t]]


def greedy_ratios(R,delta):
    chosen=[]
    for r in sorted(R):
        if not chosen or r-chosen[-1]>delta: chosen.append(r)
    return chosen


def packing_exact(sets):
    universe=sorted(set().union(*sets)); bits={r:1<<i for i,r in enumerate(universe)}
    masks=tuple(sorted({sum(bits[r] for r in s) for s in sets}))
    @lru_cache(None)
    def solve(available):
        eligible=[m for m in masks if m&available==m]
        if not eligible:return ()
        active=0
        for m in eligible:active|=m
        if active!=available:return solve(active)
        # Branch on whether the least frequent used resource is unused or used by a single edge.
        piv=min((1<<i for i in range(len(universe)) if active>>i&1),key=lambda b:sum(bool(m&b) for m in eligible))
        best=solve(active^piv)
        for m in eligible:
            if m&piv:
                cand=(m,)+solve(active^m)
                if len(cand)>len(best):best=cand
        return best
    selected=solve((1<<len(universe))-1)
    assert all(not a&b for a,b in combinations(selected,2))
    return len(selected),solve.cache_info().currsize


def receipts(x,U,d,i):
    return {frozenset(Y) for k in range(len(U)+1) for Y in combinations(U,k)
            if len(set(x)-set(Y))<=d and len(set(Y)-set(x))<=i}


def render(name, points, root):
    sr=8000; frames=[0]*9600
    for t in points:
        start=round(float(t)*sr)
        for j in range(160):
            frames[start+j]+=round(11000*sin(2*pi*500*j/sr)*sin(pi*j/159)**2)
    pcm=struct.pack('<'+'h'*len(frames),*frames)
    path=root/(name+'.wav')
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,sr,len(frames),'NONE','not compressed'));w.writeframes(pcm)
    return {'onset_samples':[round(float(t)*sr) for t in points],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    import numpy as np
    from scipy.optimize import linprog, milp, Bounds, LinearConstraint
    from scipy import __version__ as scipy_version
    root=Path(__file__).resolve().parent
    count={'affine_alignment_pairs':0,'fixed_frame_receipt_checks':0,'integer_quadruples':0,'fibonacci_checks':0,'triple_lp_checks':0,'grid_spacing_checks':0}
    X=shapes(8,4)
    for x,y in combinations(X,2):
        m=max(k for k in range(1,5) if fingerprints(x,k)&fingerprints(y,k))
        assert m==max_overlap(x,y)
        count['affine_alignment_pairs']+=1
    U=tuple(range(6)); W=list(combinations(U,4))
    for d,i in product(range(4),repeat=2):
        bags=[receipts(x,U,d,i) for x in W]
        for a,b in combinations(range(len(W)),2):
            assert bool(bags[a]&bags[b])==(4-len(set(W[a])&set(W[b]))<=d+i)
            count['fixed_frame_receipt_checks']+=1
    hist={2:0,3:0,4:0}
    for a,b,c in product(range(1,41),repeat=3):
        R=ratios((0,a,a+b,a+b+c)); hist[len(R)]+=1
        assert len(R)>=3
        count['integer_quadruples']+=1
    fib=[]; p,q=2,1
    for _ in range(17):
        x=(0,p,p+q,2*p+q);R=ratios(x)
        delta=abs(F(p,p+q)-F(p+q,2*p+q))
        assert len(R)==4 and delta==F(1,(p+q)*(2*p+q))
        assert abs(F(p,2*p+q)-F(q,p+q))==delta
        fib.append({'p':p,'q':q,'span':2*p+q,'ratio_gap':str(delta),'normalized_jitter_threshold':str(delta/4)})
        p,q=p+q,p;count['fibonacci_checks']+=1
    rng=random.Random(428); maxerr=0.; example=None
    # LP with independent scales >=1, free translation, and common jitter radius.
    for _ in range(400):
        x=sorted(rng.sample(range(25),3));y=sorted(rng.sample(range(25),3))
        A=[]
        for a,b in zip(x,y):A.extend([[a,-b,-1,-2],[-a,b,1,-2]])
        lp=linprog([0,0,0,1],A_ub=A,b_ub=[0]*6,bounds=[(1,None),(1,None),(None,None),(0,None)],method='highs')
        assert lp.success
        rx=canon(x)[1];ry=canon(y)[1]; expected=float(max(x[-1]-x[0],y[-1]-y[0])*abs(rx-ry)/4)
        maxerr=max(maxerr,abs(lp.fun-expected));assert abs(lp.fun-expected)<1e-8
        count['triple_lp_checks']+=1
    # Endpoint-matched scaling is not generally optimal for four or more points.
    for x,y in combinations(shapes(8,4),2):
        A=[]
        for a,b in zip(x,y):A.extend([[a,-b,-1,-2],[-a,b,1,-2]])
        lp=linprog([0,0,0,1],A_ub=A,b_ub=[0]*8,bounds=[(1,None),(1,None),(None,None),(0,None)],method='highs')
        xx,yy=canon(x),canon(y); dif=[a-b for a,b in zip(xx,yy)]
        endpoint=float(max(x[-1],y[-1])*(max(dif)-min(dif))/4)
        if lp.fun<endpoint-1e-8:
            example={'x':x,'y':y,'lp_jitter':lp.fun,'endpoint_jitter':endpoint,'lp_variables':list(lp.x)};break
    assert example is not None
    grid=[]
    for L in range(3,19):
        words=shapes(L,4);sets=[ratios(x) for x in words]
        R={F(a,b) for b in range(2,L+1) for a in range(1,b)}; rr=sorted(R)
        A=np.array([[int(r in s) for s in sets] for r in rr])
        res=milp(-np.ones(len(words)),integrality=np.ones(len(words)),bounds=Bounds(0,1),constraints=LinearConstraint(A,0,1),options={'time_limit':15})
        if res.x is None: raise RuntimeError(res.message)
        idx=[i for i,v in enumerate(res.x) if v>.5]; assert all(not sets[a]&sets[b] for a,b in combinations(idx,2))
        assert len(idx)<=len(R)//3
        exact=None
        if L<=8:
            exact,states=packing_exact(sets);assert exact==len(idx) and res.status==0
        row={'L':L,'primitive_shapes':len(words),'ratio_universe':len(R),'packing_upper':len(R)//3,'milp_witness_count':len(idx),'milp_status':int(res.status),'milp_gap':float(res.mip_gap),'exact_dp':exact,'witness':[words[i] for i in idx]}
        for d in [F(0),F(1,100),F(1,20),F(1,10)]:
            code=greedy_ratios(R,d);assert all(b-a>d for a,b in zip(code,code[1:]));count['grid_spacing_checks']+=1
            row['triple_code_gap_'+str(d)]=len(code)
        grid.append(row)
    # Exact golden family in algebraic coordinates is proved in report. A rational approximation is rendered.
    p,q=144,89; r1=F(p,p+q);r3=F(p+q,2*p+q)
    audio={}
    audio['four_onsets']=render('four_onsets',[F(1,10)+F(4,5)*F(t,2*p+q) for t in (0,p,p+q,2*p+q)],root)
    audio['delete_last']=render('delete_last',[F(1,10),F(1,10)+F(4,5)*r1,F(9,10)],root)
    audio['delete_second']=render('delete_second',[F(1,10),F(1,10)+F(4,5)*r3,F(9,10)],root)
    # The pair may or may not land on the same PCM sample; record rather than force.
    audio['same_rendered_receipt']=audio['delete_last']['sha256']==audio['delete_second']['sha256']
    out={'scope':'synthetic; no human or independent review','counts':count,'integer_fingerprint_histogram':hist,'fibonacci':fib,'max_triple_lp_error':maxerr,'endpoint_alignment_counterexample':example,'grid':grid,'audio':audio,'scipy':scipy_version}
    (root/'execution.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'counts':count,'hist':hist,'lp_maxerr':maxerr,'counterexample':example,'grid':[[v['L'],v['primitive_shapes'],v['ratio_universe'],v['milp_witness_count'],v['milp_status'],v['exact_dp']] for v in grid],'audio':audio},indent=2))

if __name__=='__main__':main()
