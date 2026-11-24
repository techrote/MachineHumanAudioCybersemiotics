"""Synthetic exact integer circular splitter and inverse; not a listening study."""
import math, wave, struct, hashlib, json
from pathlib import Path


def render(q,d,path):
    # Integer samples with even parity make the half-sums exactly representable.
    n=q*1024
    x=[2*round(6000*math.sin(2*math.pi*(i%q)/q)) for i in range(n)]
    y=[(x[i]+x[(i-d)%n])//2 for i in range(n)]
    z=[(x[(i-d)%n]-x[i])//2 for i in range(n)]
    # The symmetric two-port matrix is inverted by transposing and advancing.
    rec=[(y[i]+y[(i+d)%n]-z[i]+z[(i+d)%n])//2 for i in range(n)]
    leak=[(-y[i]+y[(i+d)%n]+z[i]+z[(i+d)%n])//2 for i in range(n)]
    assert rec==x and not any(leak)
    e=sum(v*v for v in x); a=sum(v*v for v in y); b=sum(v*v for v in z)
    assert a+b==e and max(map(abs,y+z))<32768
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,48000,n,'NONE','not compressed'))
        w.writeframes(struct.pack('<'+'h'*(2*n),*(v for pair in zip(y,z) for v in pair)))
    return {'q':q,'delay':d,'frames':n,'left_energy':a,'right_energy':b,'input_energy':e,'left_fraction':a/e,'ideal_left_fraction':math.cos(math.pi*d/q)**2,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


if __name__=='__main__':
    out=Path(__file__).parent
    result=[render(q,16,out/f'q{q}.wav') for q in (64,81)]
    print(json.dumps(result,indent=2))
