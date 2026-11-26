"""Independent formulation: finite-box numerical LP and exact literal channel checks.
Run with Python 3 + NumPy/SciPy. Audio is synthetic, not human evidence.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json, math, random, struct, wave
import numpy as np
import scipy
from scipy.optimize import linprog

E = [(F(2,21), F(1,3)), (F(5,7), F(5,8)), (F(4,21), F(1,24))]
G = [(F(3,7), F(3,4)), (F(4,7), F(1,4))]
R = [(F(9,25), F(18,25)), (F(12,25), F(6,25)), (F(4,25), F(1,25))]
C = [(F(p,39), F(m,39)) for p,m in zip([9,14,12,4],[18,14,6,1])]
EPS, RHO = F(14,39), F(10973,78500)
counts = [3144,4716,3930,12152,14298,20268,16104,3888]
S = [(F(n-(10973 if j==0 else 0),67527), F(n-(10973 if j==0 else 0),67527)*F(2)**(-j)) for j,n in zip(range(-3,5),counts)]

def prod(A,B):
    return [(p*r,m*s) for p,m in A for r,s in B]

def h(A,z):
    return sum(max(0,p-z*m) for p,m in A)

def diff(A,z):
    return h(prod(E,A),z)-h(prod(G,A),z)

def knots(A):
    return sorted({p/m for p,m in prod(E,A)+prod(G,A)})

def good(A):
    return all(diff(A,z)>=0 for z in knots(A))

def erase(A,t):
    return [(p*(1-t),m*(1-t)) for p,m in A if t<1]+([(t,t)] if t else [])

for A in [E,G,R,C,S]:
    assert all(p>0 and m>0 for p,m in A)
    assert all(sum(r[i] for r in A)==1 for i in range(2))
assert good(C) and not good(R) and good(S) and good(erase(S,RHO))
assert good(erase(R,EPS)) and not good(erase(R,EPS-F(1,1000))) and not good(erase(R,EPS+F(1,1000)))
assert not good(erase(S,RHO+F(1,78500)))
# A merged off-grid pair passes every original grid knot, but fails between them.
M=C[:2]+[(C[2][0]+C[3][0],C[2][1]+C[3][1])]
assert all(diff(M,F(4,7)*F(2)**j)==diff(C,F(4,7)*F(2)**j) for j in range(-8,9))
assert diff(M,F(128,49))==F(-8,273) and not good(M)

# Numerical search uses literal hinge evaluations, not convolution coefficients.
results=[]
for B in range(1,13):
    idx=list(range(-B,B+1)); n=len(idx)
    L=[F(2)**j for j in idx]
    zvals=sorted({p/m*l for p,m in E+G for l in L})
    A=np.array([[float(h(E,z/l)-h(G,z/l)) for l in L] for z in zvals])
    f=np.zeros(n);f[B]=-1
    eq=np.array([np.ones(n),[float(1/l) for l in L]])
    exact=linprog(f,A_ub=-A,b_ub=np.zeros(len(A)),A_eq=eq,b_eq=[1,1],bounds=(0,None),method='highs')
    # c final row; variable e; require both final and raw (unnormalized) hinge nonnegative.
    D=np.c_[A,np.zeros(len(A))]; J=np.c_[A,-A[:,B]]
    N=np.zeros(n+1);N[B]=1;N[-1]=-1
    f=np.zeros(n+1);f[-1]=-1
    robust=linprog(f,A_ub=-np.vstack([D,J,N]),b_ub=np.zeros(2*len(A)+1),A_eq=np.c_[eq,[0,0]],b_eq=[1,1],bounds=(0,None),method='highs')
    assert exact.status in (0,2) and robust.status in (0,2)
    if B>=2: assert abs(-exact.fun-float(EPS))<1e-8
    else: assert exact.status==2
    if B>=4: assert abs(-robust.fun-float(RHO))<1e-8
    results.append({'B':B,'known':round(-exact.fun,12) if exact.success else None,'uniform':round(-robust.fun,12) if robust.success else None})

# Exact 39-frame inventories of C. Separate state files; erasure is an explicit tone.
root=Path(__file__).resolve().parent
freqs=[350,550,750,950]; sr=8000; n=400
bank=[[round(10000*math.sin(2*math.pi*f*i/sr)*math.sin(math.pi*i/(n-1))**2) for i in range(n)] for f in freqs]
audio={}; decoded=0
for name,inventory in [('plus',[9,14,12,4]),('minus',[18,14,6,1])]:
    symbols=[j for j,num in enumerate(inventory) for _ in range(num)]
    random.Random(707).shuffle(symbols)
    samples=[v for j in symbols for v in bank[j]]
    path=root/('erasure-'+name+'.wav')
    with wave.open(str(path),'wb') as out:
        out.setparams((1,2,sr,0,'NONE','not compressed'))
        out.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    with wave.open(str(path),'rb') as inp:
        pcm=struct.unpack('<'+'h'*inp.getnframes(),inp.readframes(inp.getnframes()))
    recovered=[min(range(4),key=lambda j:sum((v-w)**2 for v,w in zip(pcm[k:k+n],bank[j]))) for k in range(0,len(pcm),n)]
    assert recovered==symbols
    decoded+=len(recovered)
    audio[path.name]={'counts':inventory,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
receipt={'status':'PASS','numpy':np.__version__,'scipy':scipy.__version__,'LP_profiles':len(results)*2,'finite_box_results':results,'off_grid_hidden_hinge':'-8/273','decoded_frames':decoded,'audio':audio}
(root/'native-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
