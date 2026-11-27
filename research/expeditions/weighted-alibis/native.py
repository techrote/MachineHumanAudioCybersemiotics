"""Independent numerical cross-check; synthetic data only."""
import json
import numpy as np
from scipy.optimize import linprog
import scipy

PERIODS = (5, 7, 11, 13, 17)

def design(n):
    t = np.arange(n)
    return np.column_stack([np.ones(n)] + [(t % p == j).astype(float) for p in PERIODS for j in range(1,p)])

def geometry(n):
    a = design(n)
    q, _ = np.linalg.qr(a, mode='complete')
    h = q[:, a.shape[1]:].T
    g = h.T @ h
    u = np.diag(g)
    w = np.abs(g)
    pair = []
    for i in range(n):
        for j in range(i+1,n):
            U,V,W = u[i],u[j],w[i,j]
            d = U-W*W/V if W>V else V-W*W/U if W>U else U+V-2*W
            pair.append((d,i,j))
    d,i,j=min(pair)
    return h,g,float(np.sqrt(min(d,min(u)))/2),[i,j]

def run():
    profiles=[]
    for n in [51,52,53,55,57,60,64,70,85]:
        h,g,r,pair=geometry(n)
        profiles.append({'N':n,'radius':r,'pair':pair})
    h,g,_,_=geometry(51)
    # Use the independently derived projection to compute normalized weights.
    weights=np.sqrt(np.diag(g)); weights/=max(weights)
    # Exact single-error recovery is certified by the integer JS witness.
    # These LPs are numerical evidence only, and close margins can be difficult.
    aeq=np.concatenate([h,-h],axis=1)
    costs=np.tile(weights,2)
    # Test both signs at each location; compute solution residual & objective.
    statuses={}; failures=[]; max_error=0.
    for i in range(51):
        for sign in [-1,1]:
            target=np.zeros(51);target[i]=sign
            sol=linprog(costs,A_eq=aeq,b_eq=h@target,bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
            statuses[str(sol.status)]=statuses.get(str(sol.status),0)+1
            if not sol.success: failures.append([i,sign,'solver']);continue
            got=sol.x[:51]-sol.x[51:];err=float(np.max(np.abs(got-target)));max_error=max(max_error,err)
            if err>1e-5:failures.append([i,sign,err])
    # Independent support selection under bounded raw l2 noise at 0.99 times
    # the globally sharp radius, with a lower bound of 1 on fault magnitude.
    rng=np.random.default_rng(771); trials=0;wrong=0
    for n in [51,57,64,85]:
        h,g,r,_=geometry(n);u=np.diag(g)
        for i in range(n):
            for k in range(4):
                target=h[:,i]*(1+k/3)*(-1)**k
                perturb=rng.normal(size=n);perturb*=0.99*r/np.linalg.norm(perturb)
                s=target+h@perturb
                c=h.T@s/u
                # Two rays per coordinate; choose closest admissible amplitude.
                b=np.sign(c)*np.maximum(np.abs(c),1);b[c==0]=1
                residual=np.sum((s[:,None]-h*b[None,:])**2,axis=0)
                prediction=int(np.argmin(residual));trials+=1;wrong+=prediction!=i or np.dot(s,s)<residual[prediction]
    assert wrong==0
    return {'numpy':np.__version__,'scipy':scipy.__version__,'profiles':profiles,'weighted_lp':{'trials':102,'statuses':statuses,'failures':failures,'max_error':max_error},'bounded_noise_trials':trials,'wrong':int(wrong)}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
