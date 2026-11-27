import json
import numpy as np
import sympy as s
from fractions import Fraction
from pathlib import Path
P=[5,7,11,13,17]
def design(n,nuisance=True):
    return np.array([[int(t%p==r)-int(t%p==p-1) for p in P for r in range(p-1)]+([1,(-1)**t] if nuisance else []) for t in range(n)],dtype=np.int64)
def expand(B):
    out=[]; k=0
    for p in P:
        c=B[k:k+p-1]; out.append(np.vstack([c,-c.sum(axis=0)])); k+=p-1
    return out
# exact certificates use rational inverse at minimal dimension and rational Gram inverse at 64
exact={}
for n,nu in [(48,False),(50,True),(64,True)]:
    X=s.Matrix(design(n,nu).tolist()); B=X.inv() if X.rows==X.cols else (X.T*X).inv()*X.T
    assert B*X==s.eye(X.cols)
    k=0; norms=[]; l1=[]
    for p in P:
        rows=[B.row(i) for i in range(k,k+p-1)]; rows.append(-sum(rows,s.zeros(1,n))); k+=p-1
        norms.append(max(sum(v*v for v in row) for row in rows)); l1.append(max(sum(abs(v) for v in row) for row in rows))
    exact[str(n)]={'max_row_variance':str(max(norms)),'max_row_l1':str(max(l1)),'variance_float':float(max(norms)),'l1_float':float(max(l1))}
    if n==50:
        z=B[:, -1]; assert X*z==s.eye(n)[:,-1]; exact[str(n)]['last_impulse_max_coefficient']=str(max(abs(v) for v in z)); assert X[:-1,:]*z==s.zeros(n-1,1)
# numerical cross check, actual direct recovery on randomly selected phases and signed gains
rng=np.random.default_rng(20261127); profiles=100; results=[]
for n,nu in [(48,False),(50,True),(64,True),(80,True),(96,True),(128,True),(256,True),(512,True)]:
    X=design(n,nu); B=np.linalg.pinv(X); comps=expand(B); var=max(float(np.max((c*c).sum(axis=1))) for c in comps); l1=max(float(np.max(abs(c).sum(axis=1))) for c in comps)
    err=0.; recovered=0
    for _ in range(profiles):
        phases=[int(rng.integers(p)) for p in P]; gains=rng.choice([-3,-2,-1,1,2,3],len(P)); truth=[a*(p*(np.arange(p)==r)-1) for p,r,a in zip(P,phases,gains)]; theta=np.concatenate([v[:-1] for v in truth]+([np.array([3,-7])] if nu else [])); obs=X@theta
        for c,v,r,a in zip(comps,truth,phases,gains):
            y=c@obs; err=max(err,float(np.max(abs(y-v)))); i=int(np.argmax(abs(y))); assert i==r and np.sign(y[i])==np.sign(a); recovered+=1
    assert err<1e-5
    if str(n) in exact: assert abs(var/exact[str(n)]['variance_float']-1)<1e-7
    results.append(dict(samples=n,nuisance=nu,condition=float(np.linalg.cond(X)),max_variance=var,max_l1=l1,clean_error=err,recovered=recovered))
# Construct bounded perturbation attaining worst residue error exactly in numerical arithmetic.
X=design(64); C=np.vstack(expand(np.linalg.pinv(X))); row=C[np.argmax(abs(C).sum(axis=1))]; e=np.sign(row)*.1; observed=float(row@e); assert abs(observed-.1*exact['64']['l1_float'])<1e-10
receipt={'exact':exact,'numeric':results,'adversarial_error_at_64':observed,'numpy':np.__version__,'sympy':s.__version__,'seed':20261127}
print(json.dumps(receipt,indent=2))
