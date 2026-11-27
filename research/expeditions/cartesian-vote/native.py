import itertools, math, json
import numpy as np
from scipy.optimize import linprog
from scipy import sparse

def design(ps):
    X=np.array(list(itertools.product(*(range(p) for p in ps))))
    return X,np.column_stack([np.ones(len(X),dtype=int)]+[(X[:,i]==r).astype(int) for i,p in enumerate(ps) for r in range(1,p)])

def solve(A,z=None):
    A=sparse.csr_matrix(A); n,k=A.shape; I=sparse.eye(n,format='csr')
    C=sparse.vstack([sparse.hstack([A,-I]),sparse.hstack([-A,-I])],format='csr')
    rhs=np.zeros(2*n) if z is None else np.r_[z,-z]
    eq=sparse.hstack([A[0],sparse.csr_matrix((1,n))]) if z is None else None
    fit=linprog(np.r_[np.zeros(k),np.ones(n)],A_ub=C,b_ub=rhs,A_eq=eq,b_eq=[1] if z is None else None,bounds=[(None,None)]*k+[(0,None)]*n,method='highs')
    assert fit.success,fit.message
    return fit.fun,fit.x[:k]

def main():
    rng=np.random.default_rng(763); rows=[]; trials=0; maxerr=0.
    for ps in [(2,3,5),(3,5,7),(3,5,11),(2,3,5,7),(3,5,7,11),(2,)*3,(2,)*6,(3,)*3,(4,)*4]:
        X,A=design(ps); n,k=A.shape; d=n//max(ps); opt,_=solve(A)
        if all(math.gcd(p,q)==1 for p,q in itertools.combinations(ps,2)):
            assert abs(opt-d)<1e-6
            for e,f in [(0,d-1),((d-1)//2,(d-1)%2),(1,0)]:
                for _ in range(4):
                    theta=rng.integers(-10,11,k); z=A@theta; perm=rng.permutation(n); z[perm[:e]]+=rng.choice([-1,1],e)*rng.integers(100,10001,e)
                    keep=np.ones(n,dtype=bool); keep[perm[e:e+f]]=False
                    _,t=solve(A[keep],z[keep]); err=float(np.max(np.abs(t-theta))); assert err<1e-6; maxerr=max(err,maxerr); trials+=1
        rows.append({'levels':ps,'cells':n,'distance':d,'minimum_l1_at_unit_cell':round(opt,9)})
    X,A=design((2,)*6); h=3-X.sum(axis=1); F=np.argsort(-abs(h),kind='stable')[:15]; z=np.zeros(len(h)); z[F]=h[F]; cost,_=solve(A,z); assert np.sum(abs(z))==31 and np.sum(abs(z-h))==29 and cost<=29+1e-8
    print(json.dumps({'profiles':rows,'correction_trials':trials,'maximum_parameter_error':round(maxerr,9),'binary_failure':{'true_cost':31,'alternative_cost':29,'actual_LAD_minimum':round(cost,9)}},indent=2))
if __name__=='__main__': main()
