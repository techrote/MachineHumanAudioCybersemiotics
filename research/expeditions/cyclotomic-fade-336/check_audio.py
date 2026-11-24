"""Independent centered-phase census and original undamped-resonator audio (#336)."""
import argparse
import cmath
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import wave


def centered(w):
    # Work in Q(phi), phi^2=phi+1. 4|P|^2 = (X+(Y-X)phi)^2
    # + (3-phi)(U phi+V)^2, derived by centering the four phases.
    a,b,c,d=w
    x,y,u,v=a+d,b+c,d-a,c-b
    h=y-x
    r0,r1=x*x+h*h,2*x*h+h*h
    i0,i1=v*v+u*u,2*v*u+u*u
    c0,c1=r0+3*i0-i1,r1+2*i1-i0
    assert (2*c0+c1)%4==0 and c1%4==0
    return (2*c0+c1)//4,c1//4


def sign(a,b):
    if a==0: return (b>0)-(b<0)
    if b==0: return (a>0)-(a<0)
    if a>0 and b>0: return 1
    if a<0 and b<0: return -1
    return ((a*a>5*b*b)-(a*a<5*b*b))*(1 if a>0 else -1)


def census():
    rows=[]
    for m in range(1,65):
        best=None; ties=0; count=0; winner=None
        for a in range(m+1):
            for b in range(m-a+1):
                for c in range(m-a-b+1):
                    w=(a,b,c,m-a-b-c)
                    z=centered(w); count+=1
                    s=-1 if best is None else sign(z[0]-best[0],z[1]-best[1])
                    if s<0: best=z; winner=w; ties=1
                    elif s==0: ties+=1
        assert count==math.comb(m+3,3)
        assert best[0]**2-5*best[1]**2>=4
        rows.append((m,*best,count,ties,*winner))
    return rows


def gain(w,q=5):
    return abs(sum(x*cmath.exp(2j*math.pi*j/q) for j,x in enumerate(w))/sum(w))


RATE=16000
GRID=8  # 0.5 ms, one fifth of the 400 Hz period
SEG=4000


def render(left,right):
    # Each increment excites an ideal unit-amplitude undamped sine resonator.
    # Repeat a finite demonstration, with identical 20 ms end tapers and resets.
    def tone(w,i):
        v=sum(x*math.sin(2*math.pi*400*(i-j*GRID)/RATE)
              for j,x in enumerate(w) if i>=j*GRID)/sum(w)
        return round(18000*v*min(1,(SEG-1-i)/320))
    one=b''.join(struct.pack('<hh',tone(left,i),tone(right,i)) for i in range(SEG))
    buf=io.BytesIO()
    with wave.open(buf,'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(one*8)
    return buf.getvalue()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    out=p.parse_args().out;out.mkdir(parents=True,exist_ok=True)
    rows=census()
    tsv=''.join(','.join(map(str,r))+'\n' for r in rows).encode()
    (out/'census.csv').write_bytes(tsv)
    cases={'short-vs-exact':([1]*4,[1]*5),'same-deadline':([1]*4,[21,8,8,21])}
    audio={}
    for name,(l,r) in cases.items():
        a=render(l,r);assert a==render(l,r)
        (out/(name+'.wav')).write_bytes(a)
        with wave.open(io.BytesIO(a)) as f:
            frames=list(struct.iter_unpack('<hh',f.readframes(f.getnframes())))
            assert len(frames)==32000 and f.getframerate()==RATE
        # Untapered steady-state integer PCM over 20 complete periods.
        tail=frames[100:900]
        peaks=[max(abs(x[i]) for x in tail) for i in range(2)]
        audio[name]={'left':l,'right':r,'gain':[gain(l),gain(r)],'tail_pcm_peak':peaks,
                     'sha256':hashlib.sha256(a).hexdigest(),'bytes':len(a)}
    assert audio['short-vs-exact']['tail_pcm_peak'][1]==0
    assert audio['same-deadline']['tail_pcm_peak'][1]>0
    # Stable integer digest also independently checkable in JS, not cryptographic.
    fnv=14695981039346656037
    for byte in tsv: fnv=((fnv^byte)*1099511628211)&((1<<64)-1)
    manifest={'classification':'synthetic','census_rows':len(rows),'candidates':sum(r[3] for r in rows),
              'census_fnv1a64':format(fnv,'016x'),'census_sha256':hashlib.sha256(tsv).hexdigest(),
              'audio':audio}
    (out/'verification.synthetic.txt').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__': main()
