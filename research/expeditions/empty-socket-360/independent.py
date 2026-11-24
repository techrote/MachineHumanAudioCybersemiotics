"""Independent SVD / vacancy-search checks and synthetic audio. Python + NumPy."""
from itertools import permutations
from collections import deque
from pathlib import Path
import hashlib, json, wave, sys
import numpy as np


def mat(p):
    return np.eye(len(p))[list(p)]


def bfs(n):
    start = tuple(range(n+1))
    dist = {start: 0}
    q = deque([start])
    while q:
        p = q.popleft()
        i = p.index(n)
        for j in range(n+1):
            if i == j:
                continue
            z = list(p)
            z[i], z[j] = z[j], z[i]
            z = tuple(z)
            if z not in dist:
                dist[z] = dist[p]+1
                q.append(z)
    return dist


def cost(p):
    # Independently count connected components via undirected union-find.
    roots = list(range(len(p)))
    def root(i):
        while roots[i] != i:
            i = roots[i]
        return i
    for i,j in enumerate(p):
        roots[root(i)] = root(j)
    sizes = {}
    for i in range(len(p)):
        r = root(i)
        sizes[r] = sizes.get(r, 0)+1
    return sum(k+1 for k in sizes.values() if k>1)


def check():
    counts=[]
    for n in range(1,8):
        d=bfs(n)
        pcount=0
        for p in permutations(range(n)):
            assert d[p+(n,)]==cost(p)
            pcount+=1
        counts.append(dict(n=n, endpoints=pcount, states=len(d)))
    rng=np.random.default_rng(360)
    errors=[]
    for n in range(2,17):
        for _ in range(100):
            a=rng.permutation(n)
            b=rng.permutation(n)
            # Derive relative cycle spectrum independently via eigvals.
            A,B=mat(a),mat(b)
            eig=np.linalg.eigvals(A.T@B)
            floor=np.min(np.abs((1+eig)/2))
            actual=np.linalg.svd((A+B)/2,compute_uv=False)[-1]
            errors.append(abs(actual-floor))
            a=rng.permutation(n+1); b=a.copy()
            v=np.where(a==n)[0][0]; j=(v+1)%(n+1)
            b[v],b[j]=b[j],b[v]
            t=float(rng.random())
            actual=np.linalg.svd(((1-t)*mat(a)+t*mat(b))[:,:n],compute_uv=False)[-1]
            errors.append(abs(actual-np.sqrt((1-t)**2+t*t)))
    # Signed orthogonal path is a falsifier to an unrestricted passive bound.
    # Rotation in zero-sum subspace fixes common-mode and has singular values 1.
    u=np.array([1,-1,0])/np.sqrt(2); v=np.array([1,1,-2])/np.sqrt(6)
    w=np.ones(3)/np.sqrt(3)
    Q=np.column_stack([w,u,v]); signed_min=1.; negative=False
    for theta in np.linspace(0,2*np.pi/3,121):
        c,s=np.cos(theta),np.sin(theta)
        M=Q@np.array([[1,0,0],[0,c,-s],[0,s,c]])@Q.T
        signed_min=min(signed_min,np.linalg.svd(M,compute_uv=False)[-1]); negative|=bool(M.min()<-1e-8)
        assert np.allclose(M.sum(0),1) and np.allclose(M.sum(1),1)
    assert negative and signed_min>1-1e-12
    assert max(errors)<1e-12
    return dict(bfs=counts,svd_checks=len(errors),max_error=max(errors),signed_path_min= signed_min)


def write_wav(path,data,rate=16000):
    data=np.asarray(data)
    assert np.max(np.abs(data))<=1
    pcm=np.rint(data*32767).astype('<i2')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(data.shape[1]); f.setsampwidth(2); f.setframerate(rate); f.writeframes(pcm.tobytes())
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(out):
    # Two active, opposite phase sources; third input exactly zero.
    rate=16000; block=16000; count=3*block
    sample=np.arange(count); t=np.arange(block)/ (block-1)
    carrier=.55*np.sin(2*np.pi*400*sample/rate)
    src=np.column_stack([carrier,-carrier,np.zeros(count)])
    # Direct: first ramp to midpoint, hold, then ramp to swap.
    progress=np.concatenate([.5*t,np.full(block,.5),.5+.5*t])
    a=mat((0,1,2)); b=mat((1,0,2))
    direct=np.einsum('tij,tj->ti',(1-progress[:,None,None])*a+progress[:,None,None]*b,src)
    # Vacancy: move A to spare, move B to A, move A to B.
    route=[(0,1,2),(2,1,0),(1,2,0),(1,0,2)]
    spare=np.concatenate([np.einsum('tij,tj->ti',(1-t[:,None,None])*mat(p)+t[:,None,None]*mat(q),src[k*block:(k+1)*block]) for k,(p,q) in enumerate(zip(route,route[1:]))])
    # Direct raw stems are exact zero over middle block; spare does not lose source rank.
    assert not np.any(direct[block:2*block]); assert np.allclose(direct[0],spare[0]); assert np.allclose(direct[-1],spare[-1])
    # Stereo monitor is artistic: route-vector norm times a common carrier's sign.
    monitor=np.column_stack([np.linalg.norm(direct,axis=1),np.linalg.norm(spare,axis=1)])*np.sign(carrier[:,None])
    hashes={name:write_wav(out/name,data) for name,data in [('direct-3ch.wav',direct),('vacancy-3ch.wav',spare),('energy-monitor.wav',monitor)]}
    return dict(hashes=hashes,frames=count,rate=rate,direct_middle_nonzero=int(np.count_nonzero(direct[block:2*block])),spare_middle_nonzero=int(np.count_nonzero(spare[block:2*block])))

if __name__=='__main__':
    out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
    out.mkdir(parents=True,exist_ok=True)
    result={'verification':check(),'audio':render(out)}
    (out/'independent-results.txt').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
