"""Synthetic higher-order correlation checks; no listener evidence."""
import argparse
import hashlib
import itertools
import json
import math
import struct
import wave
from pathlib import Path


def shell(r):
    for a in range(-r, r + 1):
        b = r - abs(a)
        for v in (b, -b) if b else (0,):
            if a > 0 or (a == 0 and v > 0):
                yield a, v


def det(u, v):
    return u[0] * v[1] - u[1] * v[0]


def cyclic_order(n, p, q):
    """Find first r at which relations of l1 length <= r generate kernel."""
    target = n // math.gcd(n, p, q)
    seen, index, first_rank2 = [], 0, None
    for r in range(1, n + 1):
        for u in shell(r):
            if (u[0] * p + u[1] * q) % n:
                continue
            for v in seen:
                index = math.gcd(index, abs(det(u, v)))
            seen.append(u)
        if index and first_rank2 is None:
            first_rank2 = r
        if index == target:
            return r, first_rank2
    raise AssertionError('kernel not generated')


def finite_grid(n, p, q, r):
    # Independent oracle: enumerate all phase pairs in Z/(2n), then test
    # every literal ordered product of r signed frequencies (zero pads).
    modulus = 2 * n
    freq = (0, p, -p, q, -q)
    exponents = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    # Deduplicate ordered tuples via their multisets, but no lattice test.
    relations = set()
    for inds in itertools.combinations_with_replacement(range(5), r):
        if sum(freq[i] for i in inds) % n == 0:
            relations.add(tuple(sum(exponents[i][j] for i in inds) for j in (0, 1)))
    actual = {(a, b) for a in range(modulus) for b in range(modulus)
              if all((u*a + v*b) % modulus == 0 for u, v in relations)}
    translation = {((2*p*t) % modulus, (2*q*t) % modulus) for t in range(n)}
    assert translation <= actual
    return len(actual), len(translation)


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    interval_checks = continuous_checks = lattice_profiles = grid_profiles = 0
    # Exact integer frequency sums, by repeated convolution of sets.
    for n in range(3, 81):
        for k in range(1, (n-1)//2 + 1):
            first = (n+k-1)//k
            sums = {0}
            for r in range(1, first + 1):
                sums = {s+j for s in sums for j in range(-k, k+1)}
                assert (n in sums) == (r == first)
                interval_checks += 1
    for p in range(1, 25):
        for q in range(p+1, 41):
            g = math.gcd(p, q)
            threshold = (p+q)//g
            # Every nonzero relation below the threshold must fail.
            for r in range(1, threshold+1):
                rel = [u for u in shell(r) if p*u[0]+q*u[1] == 0]
                assert bool(rel) == (r == threshold)
                continuous_checks += 1
    examples = []
    max_gap = (0, None)
    for n in range(5, 51):
        for p in range(1, (n-1)//2):
            for q in range(p+1, (n-1)//2+1):
                r, rank2 = cyclic_order(n, p, q)
                lattice_profiles += 1
                if r-rank2 > max_gap[0]:
                    max_gap = (r-rank2, [n,p,q,r,rank2])
                if n <= 16:
                    actual, expected = finite_grid(n, p, q, r)
                    assert actual == expected
                    grid_profiles += 1
                    # At lower order, the grid can miss a finite ambiguity
                    # whose prime factors do not divide 2n. Record, don't assert.
                    prev, _ = finite_grid(n, p, q, r-1)
                    examples.append([n,p,q,r,rank2,prev,expected])
    # Direct witness on a continuous circle: ordinary moments (zero lags)
    # first differ at degree m+1. Compute coefficients exactly by convolution.
    # F(0)=3, F(+-1)=1, F(+-m)=+/-1: all waveforms nonnegative? DC must
    # be >=4, so choose 5. This is independent of the analytic proof.
    moment_checks = 0
    for m in range(2, 21):
        a = {0:5, 1:1, -1:1, m:1, -m:1}
        b = dict(a); b[m] = b[-m] = -1
        def mul(x, y):
            z = {}
            for i, v in x.items():
                for j, w in y.items():
                    z[i+j] = z.get(i+j, 0) + v*w
            return z
        x = y = {0:1}
        for r in range(1, m+2):
            x, y = mul(x,a), mul(y,b)
            assert (x[0] == y[0]) == (r <= m)
            moment_checks += 1
        assert x[0]-y[0] == 4*(m+1)
    # Render original phase variants at 200 Hz and 1400 Hz, no DC in audio.
    # The mathematical model uses DC=5; audio is its zero-mean AC component.
    files = {}
    for label, sign in [('aligned',1),('inverted',-1)]:
        samples = [round(6500*(math.cos(2*math.pi*200*i/8000)+sign*math.cos(2*math.pi*1400*i/8000))) for i in range(8000)]
        path = out / (label+'.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,8000,0,'NONE','not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(samples),*samples))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(set(files.values())) == 2
    result = dict(interval_sum_checks=interval_checks,continuous_relation_shell_checks=continuous_checks,
                  cyclic_lattice_profiles=lattice_profiles,grid_profiles=grid_profiles,
                  grid_missed_lower_order=sum(row[-2]==row[-1] for row in examples),
                  largest_rank2_to_full_gap=max_gap,example_n31_p4_q7=cyclic_order(31,4,7),
                  example_n24_p3_q5=cyclic_order(24,3,5),moment_checks=moment_checks,
                  audio_sha256=files)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('results'))
    run(parser.parse_args().out)
