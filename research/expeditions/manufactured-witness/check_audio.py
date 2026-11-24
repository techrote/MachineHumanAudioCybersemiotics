"""Independent integer convolution census and original phase-cycle audio.
Python 3.11+, stdlib only. Run from any directory; outputs beside this script.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib, json, math, struct, wave

OUT = Path(__file__).resolve().parent / 'run'

def cubic(f, amplitudes):
    # First convolve the two positive-frequency factors; then the conjugate.
    pairs = Counter()
    for x, a in zip(f, amplitudes):
        for y, b in zip(f, amplitudes):
            pairs[x+y] += a*b
    return [sum(pairs[t+z]*c for z,c in zip(f,amplitudes)) for t in f]

def metrics(f):
    n=len(f)
    residual=[v-(2*n-1) for v in cubic(f,[1]*n)]
    silent=[cubic(f,[int(i!=j) for i in range(n)])[j] for j in range(n)]
    midpoint=[r-s for r,s in zip(residual,silent)]
    diffs=[b-a for a,b in combinations(f,2)]
    assert (not any(residual)) == (len(diffs)==len(set(diffs))) == (not any(silent))
    return max(silent),sum(residual),not any(midpoint),not any(residual)

def census():
    rows=[]
    for n in range(3,7):
        for span in range(n-1,21):
            hist=Counter(); ap=sid=apfalse=0
            for middle in combinations(range(1,span),n-2):
                f=(0,*middle,span)
                p,t,a,s=metrics(f); hist[p,t]+=1; ap+=a; sid+=s; apfalse+=a and not s
            frontier=[list(v) for v in sorted(hist) if not any(u!=v and u[0]<=v[0] and u[1]<=v[1] for u in hist)]
            rows.append(dict(n=n,span=span,visited=sum(hist.values()),sidon=sid,apFree=ap,apFalse=apfalse,frontier=frontier))
    return rows

def sign(l,t):return -1 if (l&t).bit_count()%2 else 1

def cycle(f,labels,bits,amplitudes):
    n=len(f); sums=[0]*n
    for t in range(1<<bits):
        s=[sign(l,t) for l in labels]
        c=cubic(f,[a*x for a,x in zip(amplitudes,s)])
        for j in range(n): sums[j]+=c[j]*s[j]
    return sums

def phase_checks():
    # Independent direct convolution over every ternary amplitude word, including
    # inactive, negative and positive amplitudes, for contiguous grids n=2..8.
    solutions=[(0,[0,0]),(1,[0,0,1]),(2,[0,0,1,2]),(3,[0,0,1,2,4]),(3,[0,0,1,2,4,1]),(3,[0,0,1,2,4,1,3]),(3,[0,0,1,2,4,1,3,7])]
    checks=0
    for bits,labels in solutions:
        f=list(range(len(labels)))
        for a in product((-1,0,1),repeat=len(f)):
            expected=[(1<<bits)*x*(2*sum(y*y for y in a)-x*x) for x in a]
            assert cycle(f,labels,bits,a)==expected,(f,a)
            checks+=1
    return checks

def write_wav(name,left,right,freq=400,sr=16000):
    # Common gain, never independently normalize the two channels.
    # coefficients map onto one cosine; fading is a rendering-only operation.
    scale=.45/max(1,abs(left),abs(right)); frames=[]
    for i in range(sr*2):
        e=min(1,i/320,(sr*2-1-i)/320)
        x=e*scale*math.cos(2*math.pi*freq*i/sr)
        frames.append(struct.pack('<hh',round(32767*x*left),round(32767*x*right)))
    p=OUT/name
    with wave.open(str(p),'wb') as w:
        w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(frames))
    return dict(file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),coefficients=[left,right],commonGain=scale,frequencyHz=freq)

def main():
    OUT.mkdir(exist_ok=True)
    rows=census(); checks=phase_checks()
    f=[0,1,4,5]; labels=[0,0,0,1]
    # First carrier absent: 1+4-5=0 yields an entirely manufactured carrier.
    a=[0,1,1,1]
    raw=cubic(f,a)[0]; corrected=cycle(f,labels,1,a)[0]/2
    assert (raw,corrected)==(2,0)
    false=write_wav('manufactured-carrier.wav',raw,corrected)
    # Genuine carrier active; the diagonal cubic contribution survives cycling.
    a=[1,1,1,1]; raw=cubic(f,a)[0]; corrected=cycle(f,labels,1,a)[0]/2
    assert (raw,corrected)==(9,7)
    true=write_wav('genuine-carrier.wav',raw,corrected)
    # Negative control: a cubic-safe Sidon grid is not fifth-order safe.
    def fifth(f,a):
        c=Counter()
        for i,j,k,l,m in product(range(len(f)),repeat=5):
            c[f[i]+f[j]+f[k]-f[l]-f[m]]+=a[i]*a[j]*a[k]*a[l]*a[m]
        return [c[x] for x in f]
    f=[0,1,4,6]; a=[1,1,1,0]
    assert cubic(f,a)[3]==0
    val=fifth(f,a)[3]; assert val>0
    negative=[dict(grid=f,target=6,amplitudes=a,cubic=0,fifth=val)]
    result=dict(rows=rows,totals={k:sum(r[k] for r in rows) for k in ['visited','sidon','apFree','apFalse']},ternaryPhaseChecks=checks,audio=[false,true],fifthOrderFalseActivations=negative)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
