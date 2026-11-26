"""Native synthetic cross-check and original audio; Python >=3.11 + NumPy."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import wave
import numpy as np

OUT = Path(__file__).resolve().parent

def fixture(r):
    n = 3 * 2**r
    js = list(range(0, r-2, 2))
    return n, [2**i for i in range(r+1)], [n//2-2**j for j in js], js

def primitive(n,p):
    for z in range(2,p):
        if pow(z,n,p)==1 and pow(z,n//2,p)!=1 and pow(z,n//3,p)!=1:
            return z
    raise AssertionError('no primitive root')

def modular_signal(n,base,extra,bits,p):
    z=primitive(n,p)
    vals=[]
    for t in range(n):
        x=2*(len(base)+len(extra))+1
        for a in base:
            x+=pow(z,(a*t)%n,p)+pow(z,(-a*t)%n,p)
        for i,a in enumerate(extra):
            x+=(-1)**((bits>>i)&1)*(pow(z,(a*t)%n,p)+pow(z,(-a*t)%n,p))
        vals.append(x%p)
    return np.array(vals,dtype=np.int64)

def triple(x,p):
    n=len(x)
    shifted=x[(np.arange(n)[:,None]+np.arange(n)[None,:])%n]
    return ((shifted*x)@shifted.T)%p

def dft(x,a,p):
    n=len(x);z=primitive(n,p)
    return sum(int(v)*pow(z,(-a*t)%n,p) for t,v in enumerate(x))*pow(n,-1,p)%p

def spectral_trip(x):
    f=np.fft.fft(x)/len(x); idx=np.arange(len(x))
    return f[:,None]*f[None,:]*np.conj(f[(idx[:,None]+idx[None,:])%len(x)])

def main():
    receipt={'scope':'synthetic finite-field and numerical cross-check; not human validation', 'numpy':np.__version__, 'finite_field':[], 'audio':[]}
    for r,p in [(3,97),(5,193),(7,769)]:
        n,base,extra,js=fixture(r)
        reference=triple(modular_signal(n,base,extra,0,p),p)
        seen=set()
        for bits in range(1<<len(extra)):
            x=modular_signal(n,base,extra,bits,p)
            assert np.array_equal(triple(x,p),reference)
            q=[]
            for j,a in zip(js,extra):
                q.append(dft(x,a,p)*dft(x,2**j,p)*dft(x,-base[-1],p)*dft(x,-base[-2],p)%p)
            assert q==[1 if not (bits>>i)&1 else p-1 for i in range(len(js))]
            seen.add(tuple(q))
        assert len(seen)==1<<len(extra)
        receipt['finite_field'].append({'N':n,'prime':p,'classes':len(seen),'time_domain_triple_entries_checked':n*n*len(seen),'quartic_witnesses_checked':len(seen)*len(js)})
    # AC render of all four N=96 translation classes; constant DC omitted.
    n,base,extra,js=fixture(5);fs=9600;t=np.arange(n);scale=.8/len(base+extra)
    reference=None;ideal_reference=None
    for bits in range(1<<len(extra)):
        ideal=scale*sum(((-1)**((bits>>extra.index(a))&1) if a in extra else 1)*np.cos(2*np.pi*a*t/n) for a in base+extra)
        pcm=np.rint(32767*ideal).astype('<i2')
        path=OUT/f'parliament-{bits:02b}.wav'
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,fs,0,'NONE','not compressed'));w.writeframes(np.tile(pcm,120).tobytes())
        with wave.open(str(path),'rb') as w:
            read=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
        assert np.array_equal(read,np.tile(pcm,120))
        actual=read[:n].astype(float)/32767
        b=spectral_trip(actual);bi=spectral_trip(ideal)
        if reference is None:reference=b;ideal_reference=bi
        f=np.fft.fft(actual)/n
        q=[float((f[a]*f[2**j]*np.conj(f[base[-1]])*np.conj(f[base[-2]])).real) for a,j in zip(extra,js)]
        assert all((v<0)==bool((bits>>i)&1) for i,v in enumerate(q))
        receipt['audio'].append({'file':path.name,'bits':bits,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sample_rate':fs,'samples':len(read),'peak_pcm':int(np.max(np.abs(read))),'ideal_bispectrum_max_delta':float(np.max(np.abs(bi-ideal_reference))),'pcm_bispectrum_max_delta':float(np.max(np.abs(b-reference))),'quartic_real':q})
    receipt['assertion_failures']=0
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
