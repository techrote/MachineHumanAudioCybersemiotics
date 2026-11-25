"""Synthetic complex-coherence relay laboratory. Python 3.11+, stdlib only."""
import cmath
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import random
import struct
import wave

TAU = math.tau
TOL = 1e-9


def disk(p, q):
    if max(abs(p), abs(q)) > 1 + TOL:
        raise ValueError('non-normalized receipt')
    return p*q, math.sqrt(max(0, (1-abs(p)**2)*(1-abs(q)**2)))


def circle_candidates(disks):
    # A maximum-depth point is a center or a pair of boundary intersections.
    yield 0j
    for c, _ in disks:
        yield c
    for (c, r), (d, s) in it.combinations(disks, 2):
        dist = abs(d-c)
        if dist < TOL or dist > r+s+TOL or dist < abs(r-s)-TOL:
            continue
        u = (d-c)/dist
        x = (dist*dist+r*r-s*s)/(2*dist)
        h = math.sqrt(max(0, r*r-x*x))
        yield c+u*complex(x,h)
        yield c+u*complex(x,-h)


def max_depth(disks):
    return max((sum(abs(z-c)<=r+TOL for c,r in disks) for z in circle_candidates(disks)), default=0)


def common_center(disks):
    return next((z for z in circle_candidates(disks) if all(abs(z-c)<=r+TOL for c,r in disks)), None)


def enclosing_arc(phases):
    if not phases:
        return 0., 0.
    a = sorted(x % TAU for x in phases)
    gaps = [b-c for c,b in zip(a,a[1:]+[a[0]+TAU])]
    i = max(range(len(a)), key=gaps.__getitem__)
    return TAU-gaps[i], a[(i+1)%len(a)]


def arc_radius(phases):
    width, start = enclosing_arc(phases)
    if width >= math.pi:
        return 1., 0j
    return math.sin(width/2), math.cos(width/2)*cmath.exp(1j*(start+width/2))


def relay_limit(phases):
    return 1/math.sqrt(1+arc_radius(phases)[0])


def retained(phases, rho):
    # Exact combinatorial rule in real arithmetic; floating endpoints use TOL.
    if rho <= 1/math.sqrt(2)+TOL or not phases:
        return len(phases)
    width = 2*math.asin(min(1, (1-rho*rho)/(rho*rho)))
    a = sorted(x % TAU for x in phases)
    n = len(a)
    a += [x+TAU for x in a]
    j = best = 0
    for i in range(n):
        j = max(j,i)
        while j < i+n and a[j]-a[i] <= width+TOL:
            j += 1
        best = max(best,j-i)
    return best


def inner(a,b):
    return sum(x.conjugate()*y for x,y in zip(a,b))


def realize(pairs, z):
    # Common A and B, independent residual coordinates per relay.
    n = len(pairs)+2
    s = math.sqrt(max(0, 1-abs(z)**2))
    A = [1+0j]+[0j]*(n-1)
    B = [z,s]+[0j]*(n-2)
    vectors = [A,B]
    for j,(p,q) in enumerate(pairs):
        if s < TOL:
            assert abs(q-p.conjugate()*z)<1e-7
            v = 0j
        else:
            v = (q-p.conjugate()*z).conjugate()/s
        w2 = 1-abs(p)**2-abs(v)**2
        assert w2 >= -1e-7, (pairs,z,w2)
        x = [p,v]+[0j]*(n-2)
        x[j+2] = math.sqrt(max(0,w2))
        vectors.append(x)
        assert abs(inner(A,x)-p)<1e-7 and abs(inner(x,B)-q)<1e-7
        assert abs(inner(x,x)-1)<1e-7
    return vectors


def wav_bank(path, pairs, z):
    vectors = realize(pairs,z)
    sr, frames = 8000, 4000
    d = len(vectors[0]); scale = 10000/math.sqrt(d)
    frequencies = [200+100*j for j in range(d)]
    basis = [[cmath.exp(1j*TAU*f*t/sr) for f in frequencies] for t in range(frames)]
    samples = [[round(scale*sum(x*y for x,y in zip(v,b)).real) for v in vectors] for b in basis]
    assert max(abs(x) for row in samples for x in row)<32767
    with wave.open(str(path),'wb') as w:
        w.setparams((len(vectors),2,sr,frames,'NONE','not compressed'))
        w.writeframes(struct.pack('<'+'h'*(frames*len(vectors)),*(x for row in samples for x in row)))
    # Read PCM back, then demodulate. No human listening claims.
    with wave.open(str(path),'rb') as w:
        raw = struct.unpack('<'+'h'*(frames*len(vectors)),w.readframes(frames))
    recovered = [[2*sum(raw[t*len(vectors)+i]*basis[t][j].conjugate() for t in range(frames))/(scale*frames) for j in range(d)] for i in range(len(vectors))]
    normed = [[x/math.sqrt(inner(v,v).real) for x in v] for v in recovered]
    error = max(abs(inner(a,b)-inner(c,e)) for a,c in zip(vectors,normed) for b,e in zip(vectors,normed))
    assert error < 0.0001
    return {'channels':len(vectors),'frames':frames,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'max_coherence_error':round(error,10)}


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    counts = dict(phase_sets=0, equal_radius_profiles=0, depth_checks=0, false_pair_accepts=0, unequal_radius_profiles=0, triple_checks=0, gram_constructions=0, gauge_checks=0)
    grid = [TAU*j/12 for j in range(12)]
    rhos = [0., .5, .7, 1/math.sqrt(2), .72, 1/math.sqrt(1+math.sqrt(3)/2), .8, 1.]
    max_pair_rho = 1/math.sqrt(1+math.sqrt(3)/2)
    for k in range(1,7):
        for phases in it.combinations(grid,k):
            counts['phase_sets'] += 1
            R, center = arc_radius(phases)
            assert all(abs(cmath.exp(1j*x)-center)<=R+TOL for x in phases)
            for rho in rhos:
                pairs = [(rho+0j,rho*cmath.exp(1j*x)) for x in phases]
                disks = [disk(*p) for p in pairs]
                depth = max_depth(disks)
                assert depth == retained(phases,rho), (phases,rho,depth)
                counts['depth_checks'] += 1
                ok = rho <= relay_limit(phases)+TOL
                assert ok == (depth==k), (phases,rho,depth)
                counts['equal_radius_profiles'] += 1
                pair_ok = all(abs(c-d)<=r+s+TOL for (c,r),(d,s) in it.combinations(disks,2))
                if pair_ok and not ok:
                    counts['false_pair_accepts'] += 1
                    assert 1/math.sqrt(2) < rho <= max_pair_rho+TOL
                if ok:
                    realize(pairs,rho*rho*center)
                    counts['gram_constructions'] += 1
    rng = random.Random(614)
    for _ in range(600):
        pairs = [(rng.random()*cmath.exp(1j*rng.random()*TAU),rng.random()*cmath.exp(1j*rng.random()*TAU)) for j in range(rng.randint(3,7))]
        disks = [disk(*p) for p in pairs]
        z = common_center(disks)
        triple_ok = True
        for triple in it.combinations(disks,3):
            triple_ok &= common_center(triple) is not None
            counts['triple_checks'] += 1
        assert triple_ok == (z is not None)
        counts['unequal_radius_profiles'] += 1
        if z is not None:
            realize(pairs,z)
            counts['gram_constructions'] += 1
        gA,gB = [cmath.exp(1j*rng.random()*TAU) for j in range(2)]
        rotated = []
        for p,q in pairs:
            g = cmath.exp(1j*rng.random()*TAU)
            rotated.append((gA.conjugate()*g*p,g.conjugate()*gB*q))
        rd = [disk(*p) for p in rotated]
        assert all(abs(c*gA.conjugate()*gB-d)<TOL and abs(r-s)<TOL for (c,r),(d,s) in zip(disks,rd))
        assert max_depth(disks)==max_depth(rd)
        counts['gauge_checks'] += 1
    equilateral = [0.,TAU/3,2*TAU/3]
    bad = [(.72+0j,.72*cmath.exp(1j*x)) for x in equilateral]
    good = [(.7+0j,.7*cmath.exp(1j*x)) for x in equilateral]
    assert common_center([disk(*p) for p in bad]) is None
    assert retained(equilateral,.72)==2
    audio = {'common.wav':wav_bank(out/'common.wav',good,0j)}
    for i,j in it.combinations(range(3),2):
        pairs = [bad[i],bad[j]]
        z = (pairs[0][0]*pairs[0][1]+pairs[1][0]*pairs[1][1])/2
        name = f'local-{i+1}-{j+1}.wav'
        audio[name] = wav_bank(out/name,pairs,z)
    # Degeneracy: two point disks; equal and incompatible exact unit receipts.
    assert common_center([disk(1,1),disk(1,1)]) == 1
    assert common_center([disk(1,1),disk(1,-1)]) is None
    realize([(1,1)],1)
    receipt = {'counts':counts,'equilateral':{'global_rho_limit':1/math.sqrt(2),'pair_rho_limit':max_pair_rho,'tested_rho':.72,'max_consistent_relays':2},'audio':audio,'assertions':'passed','method':'arc and literal circle-arrangement checks; numerical tolerance 1e-9; no independent peer review'}
    (out/'execution.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__ == '__main__':
    run(Path(__file__).resolve().parent/'results')
