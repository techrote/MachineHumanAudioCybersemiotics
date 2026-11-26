"""MHAC #694: exact bounded-decision compiler, native LP cross-check, PCM scores.
Synthetic mathematics only; Python 3.11+, NumPy/SciPy for independent-method LP.
"""
from fractions import Fraction as F
from itertools import product
from math import comb, sin, pi, cos
from pathlib import Path
from random import Random
from hashlib import sha256
import json, wave, struct, sys
import numpy as np
import scipy
from scipy.optimize import linprog

OUT = Path(__file__).resolve().parent
ZERO = F(0)
ONE = F(1)

def hinge(law, k):
    return sum(w * max(ZERO, t-k) for t,w in law)

def support(a,b):
    return sorted({F(-1), ZERO, ONE, *(t for t,w in a+b)})

def compiler(a,b, knots=None, values=None):
    xs = support(a,b) if knots is None else knots
    hs = {k:hinge(a,k)-hinge(b,k) for k in xs} if values is None else values
    two = max([(ZERO, [])]+[(hs[k]/(1+abs(k)), [(k,1/(1+abs(k)))]) for k in xs],key=lambda z:z[0])
    best = two
    for k in xs:
        if k>=0: continue
        for l in xs:
            if l<=0: continue
            p,q = l/(l-k), -k/(l-k)
            v = p*hs[k]+q*hs[l]
            if v>best[0]: best=(v,[(k,p),(l,q)])
    return two,best

def menu(terms):
    # Initial action's state payoffs, followed by the supporting line increments.
    p=ZERO; q=sum((w*(1+k) for k,w in terms),ZERO)
    result=[(p,q)]
    for k,w in terms:
        p+=w*(1-k); q-=w*(1+k)
        result.append((p,q))
    assert all(0<=x<=1 for a in result for x in a)
    return result

def reward(law, actions):
    return sum(w*max(((1+t)*p+(1-t)*q)/2 for p,q in actions) for t,w in law)

def joint(law):
    return np.array([[float(w*(1+s*t)/2) for t,w in law] for s in [1,-1]])

def garbling_lp(target, source):
    """Minimize TV between target joint law and source joint law followed by a stochastic kernel."""
    A,B=joint(target),joint(source); n=A.shape[1]; m=B.shape[1]; v=m*n
    C=np.r_[np.zeros(v),np.full(2*n,.5)]
    E=np.zeros((m,v+2*n))
    for j in range(m): E[j,j*n:(j+1)*n]=1
    U=[]; rhs=[]
    for s in range(2):
        for i in range(n):
            row=np.zeros(v+2*n); row[i:v:n]=B[s,:]; row[v+s*n+i]=-1
            U.append(row); rhs.append(A[s,i])
            row=-row; row[v+s*n+i]=-1
            U.append(row); rhs.append(-A[s,i])
    fit=linprog(C,A_ub=U,b_ub=rhs,A_eq=E,b_eq=np.ones(m),bounds=(0,None),method='highs')
    assert fit.success,fit.message
    return fit.fun

def law(rng):
    n=rng.randrange(2,8); x=rng.sample(range(-20,21),n); w=[rng.randrange(1,10) for _ in x]
    W=sum(w); mean=F(sum(a*b for a,b in zip(x,w)),W)
    return [( (F(t)-mean)/41, F(z,W)) for t,z in zip(x,w)]

def check_law(a):
    assert sum(w for t,w in a)==1 and sum(t*w for t,w in a)==0
    assert all(-1<t<1 and w>0 for t,w in a)

def bayes_accuracy(a, p):
    return sum(w*max(p*(1+t),(1-p)*(1-t)) for t,w in a)

def check_grid(a,b,n):
    xs=[F(-1)+F(2*i,n) for i in range(n+1)]
    if ZERO not in xs: ks=sorted(xs+[ZERO])
    else: ks=xs
    H={x:hinge(a,x)-hinge(b,x) for x in xs}
    def interp(t):
        j=min(n-1,max(0,int((t+1)*n/2))); l,r=xs[j:j+2]
        return ((r-t)*H[l]+(t-l)*H[r])/(r-l)
    for k in support(a,b)+ks:
        assert abs(hinge(a,k)-hinge(b,k)-interp(k))<=F(1,2*n)
    for k in xs:
        p=(1-k)/2
        assert H[k]==bayes_accuracy(a,p)-bayes_accuracy(b,p)
    approximate=compiler(a,b,ks,{k:interp(k) for k in ks})[1][0]
    exact=compiler(a,b)[1][0]
    assert abs(approximate-exact)<=F(1,2*n)
    return len(xs)

def binomial_pair(N,r):
    nodes=[(r*F(2*j-N,N),F(comb(N,j),2**(N-1))) for j in range(N+1)]
    return nodes[::2],nodes[1::2]

def tone(f, i, n, rate):
    return round(7000*sin(2*pi*f*i/rate)*(0.5-0.5*cos(2*pi*i/n)))

def score(name,a):
    rng=Random(694); freqs={t:int(500+250*t) for t,w in a}
    inventory=[]
    for s in [1,-1]:
        for t,w in a:
            count=20*w*(1+s*t); assert count.denominator==1
            inventory.extend([(s,t)]*int(count))
    assert len(inventory)==40
    rng.shuffle(inventory)
    rate=8000;n=640
    state_freq={1:700,-1:300}
    templates={f:np.array([tone(f,i,n,rate) for i in range(n)],dtype=np.float64) for f in set(freqs.values())|set(state_freq.values())}
    path=OUT/name
    with wave.open(str(path),'wb') as out:
        out.setparams((2,2,rate,0,'NONE','not compressed'))
        raw=bytearray()
        for s,t in inventory:
            for x,y in zip(templates[state_freq[s]],templates[freqs[t]]): raw+=struct.pack('<hh',int(x),int(y))
        out.writeframes(raw)
    with wave.open(str(path),'rb') as inp: pcm=np.frombuffer(inp.readframes(inp.getnframes()),dtype='<i2').reshape(-1,n,2)
    def decode(v,fs): return max(fs,key=lambda f:float(v@templates[f])/np.linalg.norm(templates[f]))
    assert [(decode(frame[:,0],list(state_freq.values())),decode(frame[:,1],list(freqs.values()))) for frame in pcm]==[(state_freq[s],freqs[t]) for s,t in inventory]
    return {'file':name,'frames':len(inventory),'symbols_decoded':2*len(inventory),'sha256':sha256(path.read_bytes()).hexdigest()}

def main():
    rng=Random(694); err=0.0; checks=0; menu_checks=0; grid_checks=0
    for j in range(160):
        a,b=law(rng),law(rng);check_law(a);check_law(b)
        for x,y in [(a,b),(b,a)]:
            two,best=compiler(x,y)
            assert two[0]<=best[0]<=2*two[0]
            for val,terms in (two,best): assert reward(x,menu(terms))-reward(y,menu(terms))==val
            lp=garbling_lp(x,y); err=max(err,abs(lp-float(best[0]))); assert abs(lp-float(best[0]))<1e-8
            checks+=1
            for _ in range(12):
                actions=[(F(rng.randrange(21),20),F(rng.randrange(21),20)) for _ in range(rng.randrange(2,10))]
                assert reward(x,actions)-reward(y,actions)<=best[0]; menu_checks+=1
            grid_checks+=check_grid(x,y,2+j%17)
    for b in [F(1,2),F(3,4),F(9,10),F(99,100),F(999,1000)]:
        d=(1-b)/2; a=[(-b-d,F(1,4)),(-b+d,F(1,4)),(b-d,F(1,4)),(b+d,F(1,4))];v=[(-b,F(1,2)),(b,F(1,2))]
        two,best=compiler(a,v); assert best[0]==d/4 and two[0]==d/4/(1+b)
    # Sharp interpolation example: midpoint atom vs endpoint mixture, all grid receipts equal.
    for n in range(3,22,2):
        a=[(-F(1,n),F(1,2)),(F(1,n),F(1,2))]; b=[(ZERO,ONE)]
        assert all(hinge(a,F(-1)+F(2*i,n))==hinge(b,F(-1)+F(2*i,n)) for i in range(n+1))
        assert compiler(a,b)[1][0]==F(1,2*n)
    rows=[]; moment_checks=0; hinge_checks=0
    for m in range(2,19):
        N=2*m-1;r=F(1,2);a,b=binomial_pair(N,r);check_law(a);check_law(b)
        for k in range(N):
            assert sum(w*t**k for t,w in a)==sum(w*t**k for t,w in b);moment_checks+=1
        for k in range(1,N):
            t=r*F(2*k-N,N)
            assert hinge(a,t)-hinge(b,t)==(-1)**(k+1)*F(2*r,N)*F(comb(N-2,k-1),2**(N-1));hinge_checks+=1
        # W1 of equal-spaced alternating binomial laws via literal CDF differences.
        w1=sum(abs(sum(w for t,w in a if t<=r*F(2*j-N,N))-sum(w for t,w in b if t<=r*F(2*j-N,N)))*2*r/N for j in range(N))
        assert w1==2*r/N
        k=m-1; t=r*F(2*k-N,N)
        lower=abs(hinge(a,t)-hinge(b,t))/(1+abs(t));upper=4*r**N/(N*(N-1)*(1-r))
        # Independent positive entropy-tail bound; direct floating subtraction not used at tiny gaps.
        rows.append({'m':m,'matched_moments':N-1,'entropy_gap_upper':float(upper),'decision_gap_lower':float(lower),'W1':float(w1),'actual_D':float(max(compiler(a,b)[1][0],compiler(b,a)[1][0]))})
    a=[(F(-4,5),F(1,4)),(F(-1,5),F(1,4)),(F(1,5),F(1,4)),(F(4,5),F(1,4))]; b=[(F(-1,2),F(1,2)),(F(1,2),F(1,2))]
    two,best=compiler(a,b);assert two[0]==F(1,20) and best[0]==F(3,40)
    actions=[(0,1),(F(3,4),F(3,4)),(1,0)]
    assert reward(a,actions)==F(33,40) and reward(b,actions)==F(3,4)
    result={'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'seed':694,'directional_garbling_LPs':checks,'max_LP_error':err,'random_menu_checks':menu_checks,'grid_receipt_checks':grid_checks,'sharp_factor_profiles':5,'sharp_grid_profiles':10,'exact_moment_checks':moment_checks,'exact_hinge_checks':hinge_checks,'fixture':{'two_actions':str(two[0]),'three_actions':str(best[0]),'reward_A':'33/40','reward_B':'3/4'},'binomial_family':rows,'audio':[score('spread.wav',a),score('concentrated.wav',b)],'status':'PASS'}
    (OUT/'native-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
