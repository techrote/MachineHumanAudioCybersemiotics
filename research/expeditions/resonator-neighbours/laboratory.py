"""Exact synthetic graph experiments and optional original PCM sonification."""
import itertools as it
from collections import Counter
import json, math, wave, struct, hashlib, sys
from pathlib import Path

V = list(it.product(range(4), repeat=2))
N = len(V)

def graph(kind):
    steps = {(1,0),(3,0),(0,1),(0,3),(1,1),(3,3)}
    return [[int(u != v and (u[0] == v[0] or u[1] == v[1]) if kind == 'rook'
                 else ((u[0]-v[0])%4,(u[1]-v[1])%4) in steps) for v in V] for u in V]

def mv(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]

def unit(u):
    return [int(i == u) for i in range(N)]

def mul(x,y):
    return [a*b for a,b in zip(x,y)]

def witness(A,u,v):
    z = mv(A, [a+b for a,b in zip(unit(u),unit(v))])
    c = [a*(a-1)//2 for a in z]
    w = mul(c,mv(A,c))
    return mv(A,w)[u], z, c, w

def census(A):
    for u in range(N):
        assert sum(A[u]) == 6
        assert not A[u][u]
        for v in range(N):
            assert A[u][v] == A[v][u]
            assert sum(mul(A[u],A[v])) == (6 if u == v else 2)
    kernels = []
    for u in range(N):
        x = unit(u)
        trace = []
        for t in range(13):
            classes = [x[u], {x[v] for v in range(N) if A[u][v]},
                       {x[v] for v in range(N) if v != u and not A[u][v]}]
            assert len(classes[1]) == len(classes[2]) == 1
            trace.append([classes[0],next(iter(classes[1])),next(iter(classes[2]))])
            x = mv(A,x)
        kernels.append(trace)
    assert all(k == kernels[0] for k in kernels)
    pair_profiles, pair_witness, triple_profiles, triple_witness = {},Counter(),Counter(),Counter()
    for u,v in it.combinations(range(N),2):
        s,z,c,w = witness(A,u,v)
        rel = A[u][v]
        profile = sorted(Counter((int(i==u),int(i==v),A[u][i],A[v][i]) for i in range(N)).items())
        assert pair_profiles.setdefault(rel,profile) == profile
        assert sum(c) == 2 and s == sum(w) == sum(A[i][j] for i,j in it.combinations(range(N),2) if c[i] and c[j])*2
        pair_witness[f'{rel}:{s}'] += 1
    for S in it.combinations(range(N),3):
        edges = sum(A[u][v] for u,v in it.combinations(S,2))
        common = sum(all(A[u][i] for u in S) for i in range(N))
        triple_profiles[edges] += 1
        triple_witness[f'{edges}:{common}'] += 1
    cliques = sum(all(A[u][v] for u,v in it.combinations(S,2)) for S in it.combinations(range(N),4))
    # Exhaust all three-class states in a small signed integer cube.
    quotient_checks = 0
    for u in range(N):
        cls = [0 if v==u else 1 if A[u][v] else 2 for v in range(N)]
        for a,b,c in it.product(range(-2,3), repeat=3):
            x = [(a,b,c)[j] for j in cls]
            y = (6*b, a+2*b+3*c, 2*b+4*c)
            assert mv(A,x) == [y[j] for j in cls]
            quotient_checks += 1
    return dict(kernels=kernels[0], pair_profiles=pair_profiles,pair_witness=dict(pair_witness),
                triple_profiles=dict(triple_profiles),triple_witness=dict(triple_witness),
                four_cliques=cliques,quotient_checks=quotient_checks)

def pcm(path, values):
    # 0.12 s per value, continuous sine with a short symmetric taper per slot.
    data = bytearray()
    for v in values:
        for i in range(960):
            a = min(1,i/40,(959-i)/40)
            data.extend(struct.pack('<h',round(12000*v*a*math.sin(2*math.pi*250*i/8000))))
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,8000,0,'NONE','not compressed')); w.writeframes(data)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main(out=None):
    R,S = graph('rook'),graph('shrikhande')
    r,s = census(R),census(S)
    assert r['kernels']==s['kernels'] and r['pair_profiles']==s['pair_profiles'] and r['triple_profiles']==s['triple_profiles']
    assert r['pair_witness']['1:2']==48 and s['pair_witness']['1:0']==48
    assert r['triple_witness']['3:1']==32 and s['triple_witness']['3:0']==32
    assert (r['four_cliques'],s['four_cliques'])==(8,0)
    # Same adjacent port pair (0,1); normalized return pulse and nonlinear witness.
    linear = [row[0]/6**t for t,row in enumerate(r['kernels'])]
    audio = {}
    if out:
        out.mkdir(parents=True,exist_ok=True)
        for name,A in [('rook',R),('shrikhande',S)]:
            score = linear + [witness(A,0,1)[0]/2]
            audio[name+'-linear.wav'] = pcm(out/(name+'-linear.wav'),linear)
            audio[name+'-intervention.wav'] = pcm(out/(name+'-intervention.wav'),score)
        assert audio['rook-linear.wav']==audio['shrikhande-linear.wav']
        assert audio['rook-intervention.wav']!=audio['shrikhande-intervention.wav']
    return dict(rook=r,shrikhande=s,audio_sha256=audio)

if __name__=='__main__':
    print(json.dumps(main(Path(sys.argv[1]) if len(sys.argv)>1 else None),sort_keys=True,indent=2))
