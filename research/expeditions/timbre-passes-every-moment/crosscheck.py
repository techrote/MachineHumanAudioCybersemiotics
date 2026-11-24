"""Independent numerical LP and exact Fraction witness; no listener evidence."""
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import struct
import wave
import numpy as np
from scipy.optimize import linprog


def witness(xs):
    w = [Fraction(1, math.prod(x-y for j, y in enumerate(xs) if j != i))
         for i, x in enumerate(xs)]
    z = sum(v for v in w if v > 0)
    assert all(sum(v*x**j for v, x in zip(w, xs)) == 0
               for j in range(len(xs)-1))
    p = [max(v, 0)/z for v in w]
    q = [max(-v, 0)/z for v in w]
    return p, q


def lp_width(xs, k):
    x = np.asarray(xs, dtype=float)
    n = len(x)
    h = (x > 0).astype(float)
    moments = np.vstack([x**j for j in range(1, k+1)]) if k else np.empty((0,n))
    eq = np.vstack([np.r_[np.ones(n), np.zeros(n)],
                    np.r_[np.zeros(n), np.ones(n)],
                    np.hstack([moments, -moments])])
    result = linprog(np.r_[-h, h], A_eq=eq, b_eq=np.r_[1.,1.,np.zeros(k)],
                     bounds=(0,None), method='highs')
    assert result.success, result.message
    return max(0., -float(result.fun))


def cubic_width(d):
    c = math.sqrt((1+d+d*d)/3)
    t, s = 2*c**3, d*(1+d)
    return (t-s)/(t+s)


def render(out, offsets, powers, above=False):
    fs = 8000
    scale = 0.55/math.sqrt(len(offsets))
    amps = [scale*math.sqrt(float(p)) if not above or x > 0 else 0.
            for x, p in zip(offsets, powers)]
    samples = [round(32767*sum(a*math.sin(2*math.pi*(1000+x)*j/fs)
                               for a, x in zip(amps, offsets))) for j in range(fs)]
    assert max(map(abs, samples)) < 32767
    with wave.open(str(out), 'wb') as f:
        f.setparams((1, 2, fs, fs, 'NONE', 'not compressed'))
        f.writeframes(struct.pack('<'+'h'*fs, *samples))
    return {'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
            'integer_energy': sum(s*s for s in samples), 'bytes': out.stat().st_size}


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    grid = []
    for g in range(1,9):
        xs = [i/8 for i in range(-8,9) if abs(i)>=g]
        grid.append({'g':g, 'widths':[lp_width(xs,k) for k in range(min(8,len(xs))+1)]})
    continuum = []
    for d in [0.125,0.25,0.375,0.5,0.625,0.75,0.875]:
        c = math.sqrt((1+d+d*d)/3)
        xs = np.unique(np.r_[np.linspace(-1,-d,101),np.linspace(d,1,101),-c,c])
        exact = cubic_width(d)
        l3,l4 = lp_width(xs,3),lp_width(xs,4)
        assert abs(l3-exact)<1e-8 and abs(l4-exact)<1e-8
        continuum.append({'delta':d,'cubic_formula':exact,'lp3':l3,'lp4':l4})
    audio = {}
    for tag,offsets in [('near',[-800,-400,-1,1,400,800]),('wide',[-800,-400,-100,100,400,800])]:
        p,q = witness(offsets)
        audio[tag] = {'band_A':str(sum(v for x,v in zip(offsets,p) if x>0)),
                      'band_B':str(sum(v for x,v in zip(offsets,q) if x>0)), 'files':{}}
        for name,powers in [('A',p),('B',q)]:
            for above in [False,True]:
                file = tag+'-'+name+('-above' if above else '')+'.wav'
                audio[tag]['files'][file]=render(out/file,offsets,powers,above)
    result={'grid':grid,'continuum':continuum,'audio':audio,
            'qualification':'Numerical LP cross-check, exact Fraction witness, native PCM; not peer review.'}
    (out/'crosscheck.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    import sys
    main(Path(sys.argv[1] if len(sys.argv)>1 else 'crosscheck-output'))
