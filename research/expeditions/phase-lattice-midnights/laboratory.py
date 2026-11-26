"""Phase lattice expedition: exact Smith census and PCM readback.
Requires sympy for integer normal forms; Python 3.11+.
Run: python laboratory.py (writes execution.json and audio/ beside source).
"""
from itertools import combinations
from pathlib import Path
from collections import Counter
from math import gcd, prod, tau, cos, sin, hypot
import cmath, json, struct, wave, hashlib, sys
import sympy
from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_form

ROOT = Path(__file__).resolve().parent

def relations(S):
    idx = {s:i for i,s in enumerate(S)}
    rows = []
    for a,b in ((a,b) for a in S for b in S if a<=b and a+b in idx):
        row = [0]*len(S)
        row[idx[a]] += 1; row[idx[b]] += 1; row[idx[a+b]] -= 1
        rows.append(row)
    return rows

def smith(rows, n):
    if not rows: return []
    D=smith_normal_form(Matrix(rows), domain=ZZ)
    return [abs(int(D[i,i])) for i in range(min(D.shape)) if D[i,i]]

def family(r):
    return sorted({3*2**i for i in range(r+3)} | {5*2**i for i in range(r+2)} | {15*2**r})

def phases(S,r,j):
    # Turns represented by integer numerators modulo 5*2**r.
    modulus=5*2**r
    return [j*(s//3) % modulus if s%3==0 and s%5!=0 else 0 for s in S]

def audit():
    receipt={'python':sys.version.split()[0], 'sympy':sympy.__version__, 'families':[], 'census':{}, 'audio':{}}
    for r in range(13):
        S=family(r); rows=relations(S); diag=smith(rows,len(S))
        assert len(diag)==len(S)-1 and prod(diag)==2**r
        row=[int(s in (3,12))-int(s in (5,10)) for s in S]
        assert sum(s*c for s,c in zip(S,row))==0
        assert smith(rows+[row],len(S))==[1]*(len(S)-1)
        m=5*2**r
        for j in range(2**r):
            p=phases(S,r,j)
            assert all(sum(a*b for a,b in zip(v,p))%m==0 for v in rows)
            assert sum(a*b for a,b in zip(row,p))%m==5*j
        # Multiscale quartic witnesses: each difference has one antipodal receipt.
        for delta in range(1,2**r):
            assert any((delta*2**i)%(2**r)==2**(r-1) for i in range(r))
        receipt['families'].append({'r':r,'support_size':len(S),'max_harmonic':max(S),'cubic_rows':len(rows),'smith':diag,'classes':2**r})
    counts=Counter(); witnesses=[]
    for size in range(2,13):
        for S in combinations(range(1,13),size):
            diag=smith(relations(S),size)
            rank=len(diag); finite=rank==size-1
            counts['supports']+=1
            counts['finite' if finite else 'continuous']+=1
            if finite and prod(diag)>1:
                counts['finite_nontrivial']+=1; witnesses.append(list(S))
            if rank<size-1 and prod(diag)>1: counts['continuous_with_torsion']+=1
    receipt['census']={'max_harmonic':12,**counts,'finite_nontrivial_witnesses':witnesses}
    # Real waveforms: all frequencies integer multiples of 40 Hz, 20 exact periods.
    r=1; S=family(r); fs=8000; frames=4000; gain=0.8/len(S); mod=5*2**r
    out=ROOT/'audio';out.mkdir(exist_ok=True)
    coeffs=[]
    for j in (0,1):
        p=phases(S,r,j)
        samples=[round(32767*gain*sum(cos(tau*(40*s*t/fs+a/mod)) for s,a in zip(S,p))) for t in range(frames)]
        path=out/f'class-{j}.wav'
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,fs,0,'NONE','not compressed')); f.writeframes(struct.pack('<'+'h'*frames,*samples))
        with wave.open(str(path),'rb') as f:
            read=struct.unpack('<'+'h'*frames,f.readframes(frames))
        c={s:sum(v*cmath.exp(-1j*tau*40*s*t/fs) for t,v in enumerate(read))*2/(frames*32767*gain) for s in S}
        coeffs.append(c)
        receipt['audio'][str(j)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'max_carrier_error':max(abs(c[s]-cmath.exp(1j*tau*a/mod)) for s,a in zip(S,p))}
    a,b=coeffs
    cubic=lambda c: [c[x]*c[y]*c[x+y].conjugate() for x in S for y in S if x<=y and x+y in S]
    quartic=lambda c:c[3]*c[12]*(c[5]*c[10]).conjugate()
    receipt['audio']['max_power_difference']=max(abs(abs(a[s])**2-abs(b[s])**2) for s in S)
    receipt['audio']['max_cubic_difference']=max(abs(x-y) for x,y in zip(cubic(a),cubic(b)))
    receipt['audio']['quartic_difference']=abs(quartic(a)-quartic(b))
    assert receipt['audio']['max_power_difference']<0.001
    assert receipt['audio']['max_cubic_difference']<0.001
    assert abs(receipt['audio']['quartic_difference']-2)<0.001
    (ROOT/'execution.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'census':receipt['census'],'largest':receipt['families'][-1],'audio':receipt['audio']},indent=2))
if __name__=='__main__': audit()
