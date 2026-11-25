"""Independent exact interpolation witnesses and steady-state PCM rendering."""
from fractions import Fraction as Q
from pathlib import Path
from math import sin, cos, pi, prod, comb, factorial
import hashlib, json, struct, wave

ROOT = Path(__file__).resolve().parent


def solve(a, b):
    m = [list(row) + [rhs] for row, rhs in zip(a, b)]
    n = len(m)
    for j in range(n):
        i = next(i for i in range(j, n) if m[i][j])
        m[i], m[j] = m[j], m[i]
        v = m[j][j]
        m[j] = [x/v for x in m[j]]
        for i in range(n):
            if i != j:
                v = m[i][j]
                m[i] = [x-v*y for x, y in zip(m[i], m[j])]
    return [row[-1] for row in m]


def pair(lambdas, probes, magnitude=False):
    # Solve linear equal-receipt constraints directly, rather than using residues.
    rows = [[Q(1) for _ in lambdas]]
    for w in probes:
        rows.append([l*l/(l*l+w*w) for l in lambdas])
        if not magnitude:
            rows.append([-l*w/(l*l+w*w) for l in lambdas])
    x = solve([r[:-1] for r in rows], [-r[-1] for r in rows]) + [Q(1)]
    assert all(v != 0 for v in x)
    p = sum(v for v in x if v > 0)
    assert p == -sum(v for v in x if v < 0)
    a = [(l, v/p) for l,v in zip(lambdas,x) if v > 0]
    b = [(l,-v/p) for l,v in zip(lambdas,x) if v < 0]
    assert len(a) == len(b) == len(lambdas)//2
    return a,b


def h(p, w):
    return (sum(v*l*l/(l*l+w*w) for l,v in p),
            -sum(v*l*w/(l*l+w*w) for l,v in p))


def mag(p,w):
    return h(p,w)[0]


def render(path, profile, freqs):
    rate = 16000
    data = bytearray()
    for f in freqs:
        re, im = map(float,h(profile,Q(f)))
        for i in range(rate//2):
            phase = 2*pi*250*f*i/rate
            # Integer PCM of analytic steady-state response; common taper.
            taper = min(1, i/160, (rate//2-1-i)/160)
            data.extend(struct.pack('<h',round(18000*taper*(re*cos(phase)-im*sin(phase)))))
    with wave.open(str(path),'wb') as fp:
        fp.setparams((1,2,rate,0,'NONE','not compressed'))
        fp.writeframes(data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    counts = dict(complex_cases=0, magnitude_cases=0, shared_receipt_checks=0,
                  spectral_factor_forward_checks=0, extra_probe_checks=0)
    for k in range(1,7):
        for shift in range(3):
            ls = [Q(i+shift+1) for i in range(2*k)]
            for magnitude in (False,True):
                n = 2*k-2 if magnitude else k-1
                probes = [Q(j+1,shift+1) for j in range(n)]
                a,b = pair(ls,probes,magnitude)
                metric = mag if magnitude else h
                for w in probes:
                    assert metric(a,w) == metric(b,w)
                    counts['shared_receipt_checks'] += 1
                assert metric(a,Q(n+1,shift+1)) != metric(b,Q(n+1,shift+1))
                counts['extra_probe_checks'] += 1
                counts['magnitude_cases' if magnitude else 'complex_cases'] += 1
            a = [(l,Q(i+1,k*(k+1)//2)) for i,l in enumerate(ls[:k])]
            v = [(l,2*w*sum(u*q/(q+l) for q,u in a)) for l,w in a]
            assert sum(w for _,w in v) == 1
            for j in range(10):
                w = Q(j,3)
                assert sum(x*x for x in h(a,w)) == mag(v,w)
                counts['spectral_factor_forward_checks'] += 1
    a,b = pair(list(map(Q,[1,2,3,4])),[Q(1)])
    assert h(a,Q(1)) == h(b,Q(1)) == (Q(7,8),Q(-5,16))
    hashes = {name:render(ROOT/(name+'.wav'),p,fs) for name,p,fs in (
        ('calibration-a',a,[1]),('calibration-b',b,[1]),
        ('challenge-a',a,[1,2]),('challenge-b',b,[1,2]))}
    assert hashes['calibration-a'] == hashes['calibration-b']
    assert hashes['challenge-a'] != hashes['challenge-b']
    out = dict(counts=counts, audio_sha256=hashes,
               example_profiles=[[[str(l),str(w)] for l,w in p] for p in (a,b)],
               calibration=[str(x) for x in h(a,Q(1))],
               challenge=[[str(x) for x in h(p,Q(2))] for p in (a,b)])
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
