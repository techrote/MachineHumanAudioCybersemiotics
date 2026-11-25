"""Independent full-grid LP oracle and synthetic half-delay audio renderer."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import wave
import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent


def reference(L, degree):
    # Exact Lagrange formula on centered squared coordinates, then reflection.
    shells = [F(2*j+1, 2)**2 for j in range(L+1)]
    ids = [0, L] if degree == 3 else [0, max(range(1, L), key=lambda j: (shells[j]-shells[0])*(shells[L]-shells[j])), L]
    weights = {}
    for i in ids:
        w = F(1, 2)
        for j in ids:
            if i != j:
                w *= -shells[j]/(shells[i]-shells[j])
        weights[-i] = weights[i+1] = w
    return [weights.get(k, F(0)) for k in range(-L, L+2)]


def lp(nodes, alpha, degree):
    # No symmetry or sparsity constraint: positive and negative part at every tap.
    k = np.array(nodes, float)-alpha
    k /= max(1, np.max(np.abs(k)))
    a = np.vstack([k**j for j in range(degree+1)])
    n = len(k)
    z = linprog(np.r_[np.zeros(n), np.ones(n)], A_eq=np.c_[a, -a], b_eq=[1]+[0]*degree, bounds=(0, None), method='highs')
    assert z.success, z.message
    return z.fun


def gain(L, degree, f):
    h = np.array(reference(L, degree), float)
    k = np.arange(-L, L+2)-.5
    return np.cos(2*np.pi*np.asarray(f)[..., None]*k) @ h


def save(name, samples, fs):
    assert np.max(np.abs(samples)) < 1
    pcm = np.rint(samples*32767).astype('<i2')
    path = ROOT/name
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(fs)
        w.writeframes(pcm.tobytes())
    return dict(frames=len(pcm), peak_pcm=int(np.max(np.abs(pcm.astype('int32')))), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def audio():
    fs = 48000
    # Actual stencil applied to a continuous analytic chirp, with all support available.
    t = np.arange(4*fs)/fs
    duration = len(t)/fs
    f0, f1 = 100, 18000
    def x(t):
        return .55*np.sin(2*np.pi*(f0*t+(f1-f0)*t*t/(2*duration)))
    ideal = x(t-.5/fs)
    def filt(L, degree):
        return sum(float(w)*x(t-k/fs) for k,w in zip(range(-L,L+2),reference(L,degree)) if w)
    short, far = filt(1,3), filt(16,3)
    # Reference residual not normalized separately; same scale both channels.
    residual = np.column_stack([short-ideal,far-ideal])*.7
    outputs = {'cubic-sweep.wav':np.column_stack([short,far]), 'cubic-residual.wav':residual}
    return {name:save(name,v,fs) for name,v in outputs.items()}


def main():
    errors=[]
    for L in range(1,33):
        for degree in (3,5):
            if degree==5 and L==1: continue
            h=reference(L,degree)
            b=sum(-w for w in h if w<0)
            errors.append(abs(lp(range(-L,L+2),.5,degree)-float(b)))
    # Asymmetric irregular grids, independent numerical full-grid optimization.
    from itertools import combinations
    extra=[-5,-2,-1,2,4,7]
    for n in range(1,len(extra)+1):
        for subset in combinations(extra,n):
            nodes=sorted([0,1,*subset]); M=max(k*(k-1) for k in nodes)
            for a in [F(1,7),F(1,2),F(4,5)]:
                errors.append(abs(lp(nodes,float(a),2)-float(a*(1-a)/M)))
    assert max(errors)<1e-8
    f=np.linspace(0,.5,2001)
    rows=[]
    for L in [1,2,4,8,16,32]:
        for degree in [3,5]:
            if L==1 and degree==5: continue
            h=reference(L,degree); g=gain(L,degree,f)
            rows.append(dict(L=L,degree=degree,negative_mass=str(sum(-w for w in h if w<0)),gain_at_0_05=float(gain(L,degree,.05)),gain_at_0_125=float(gain(L,degree,.125)),max_abs_gain=float(np.max(np.abs(g))),max_error_dc_to_0_1=float(np.max(np.abs(g[f<=.1]-1)))))
    assert abs(gain(16,3,.05)-1)>abs(gain(1,3,.05)-1)
    a=audio(); assert a==audio()
    report=dict(lp_cases=len(errors),max_lp_discrepancy=max(errors),response_grid_points=len(f),responses=rows,audio=a,repeat_audio_identical=True)
    (ROOT/'independent.synthetic.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
