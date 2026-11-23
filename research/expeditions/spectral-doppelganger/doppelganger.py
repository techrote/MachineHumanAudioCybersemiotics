"""Exact cyclic rhythm feature audit and deterministic integer PCM witnesses."""
import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
import struct
import wave


def orbit(s, n):
    return {tuple(sorted((sign*x+k) % n for x in s))
            for sign in (1, -1) for k in range(n)}


def canonical(s, n):
    return min(orbit(s, n))


def autocorr(s, n):
    a = [0]*n
    for x in s:
        for y in s:
            a[(y-x) % n] += 1
    return tuple(a)


def triples(s, n):
    a = [0]*(n*n)
    for x in s:
        for y in s:
            for z in s:
                a[((y-x) % n)*n+(z-x) % n] += 1
    return tuple(a)


def triple_invariant(s, n):
    return min(triples(s, n), triples(tuple((-x) % n for x in s), n))


def survey(n):
    groups = defaultdict(list)
    for k in range(n+1):
        for s in itertools.combinations(range(n), k):
            if s == canonical(s, n):
                groups[autocorr(s, n)].append(s)
    ambiguous = [g for g in groups.values() if len(g) > 1]
    unresolved = []
    for g in ambiguous:
        refined = defaultdict(list)
        for s in g:
            refined[triple_invariant(s, n)].append(s)
        unresolved.extend(v for v in refined.values() if len(v) > 1)
    return {'n': n, 'raw_patterns': 2**n,
            'bracelets': sum(map(len, groups.values())),
            'pair_classes': len(groups), 'ambiguous_pair_classes': len(ambiguous),
            'ambiguous_pair_bracelets': sum(map(len, ambiguous)),
            'unresolved_triple_classes': len(unresolved),
            'unresolved_triple_bracelets': sum(map(len, unresolved)),
            'first_pair': ambiguous[0][:2] if ambiguous else None,
            'first_unresolved': unresolved[0][:2] if unresolved else None}


def antipodal_survey(n):
    # Exactly one event in each opposite pair; complement is a half-turn.
    groups = defaultdict(list)
    for bits in itertools.product((0,1), repeat=n//2):
        s = tuple(sorted(i+b*(n//2) for i,b in enumerate(bits)))
        if s == canonical(s,n):
            groups[autocorr(s,n)].append(s)
    collisions = [g for g in groups.values() if len(g)>1]
    return {'n':n,'raw_patterns':2**(n//2),
            'bracelets':sum(map(len,groups.values())),
            'pair_collision_classes':len(collisions),
            'first_pair':collisions[0][:2] if collisions else None}


def fourth(s, n):
    a = [0]*(n**3)
    for x,y,z,w in itertools.product(s,repeat=4):
        a[((y-x)%n*n+(z-x)%n)*n+(w-x)%n] += 1
    return tuple(a)


def fourth_invariant(s,n):
    return min(fourth(s,n),fourth(tuple((-x)%n for x in s),n))


def render(s, n, step=1800):
    # Integer bipolar triangular click, identical for all events; no overlap.
    # Sampling grid = 12 kHz, each step = 150 ms at default.
    samples = [0]*(n*step)
    for x in s:
        for i in range(120):
            tri = 30-abs((i % 60)-30)
            samples[x*step+i] = (1 if i < 60 else -1)*400*tri
    return samples


def write_wav(path, left, right, repeats=4):
    payload = b''.join(struct.pack('<hh', a, b) for a,b in zip(left,right))*repeats
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, 12000, 0, 'NONE', 'not compressed'))
        f.writeframes(payload)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(out, max_n=14):
    out.mkdir(parents=True, exist_ok=True)
    a,b = (0,1,4,6),(0,1,3,7)
    # Anchor-independent three-point feature: 0,1,4 vs 0,1,3.
    ta,tb = triple_invariant(a,12),triple_invariant(b,12)
    diffs = [(i//12,i%12,x,y) for i,(x,y) in enumerate(zip(ta,tb)) if x != y]
    rows = [survey(n) for n in range(3,max_n+1)]
    antipodal = [antipodal_survey(n) for n in range(8,25,2)]
    first = next(r for r in antipodal if r['first_pair'])
    hashes = {'pair.wav':write_wav(out/'pair.wav',render(a,12),render(b,12))}
    x,y = first['first_pair']; n = first['n']
    assert triples(x,n)==triples(y,n)
    f,g = fourth_invariant(x,n),fourth_invariant(y,n)
    assert f!=g
    hashes['third-order-collision.wav'] = write_wav(out/'third-order-collision.wav',render(x,n),render(y,n))
    result = {'survey': rows, 'classic_pair': [a,b], 'classic_autocorr':autocorr(a,12),
              'classic_triple_differences':diffs,'antipodal_survey':antipodal,
              'fourth_difference_count':sum(a!=b for a,b in zip(f,g)),
              'wav_sha256':hashes,
              'scope':'synthetic exact integer cyclic event model; no human data'}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path('run'))
    p.add_argument('--max-n',type=int,choices=range(3,17),default=16)
    args=p.parse_args()
    print(json.dumps(report(args.out,args.max_n),indent=2))
