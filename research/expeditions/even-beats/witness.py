"""MHAC #698: literal finite experiment comparisons and original PCM inventory.
Run Python 3.11+; standard library only. No human observations.
"""
from fractions import Fraction as F
from itertools import product
from collections import Counter
from pathlib import Path
import hashlib, json, math, random, struct, wave

A = [(F(133,400),F(7,400)),(F(260,400),F(260,400)),(F(7,400),F(133,400))]
B = [(F(3,4),F(1,4)),(F(1,4),F(3,4))]
S = [(F(19,20),F(1,20)),(F(1,20),F(19,20))]

def tensor(a,b):
    return [(p*u,q*v) for p,q in a for u,v in b]

def repeat(a,n):
    result=[(F(1),F(1))]
    for _ in range(n):
        result=tensor(result,a)
    return result

def posterior(a):
    result=Counter()
    for p,q in a:
        if p+q:
            result[(p-q)/(p+q)]+=(p+q)/2
    assert sum(result.values())==1
    assert sum(t*w for t,w in result.items())==0
    return result

def call(law,k):
    return sum(w*max(F(0),t-k) for t,w in law.items())

def compare(a,b):
    u,v=posterior(a),posterior(b)
    gaps=[call(u,k)-call(v,k) for k in set(u)|set(v)|{F(-1),F(0),F(1)}]
    return min(gaps),max(gaps),call(u,0)-call(v,0)

def accuracy(a,p=F(1,2)):
    return sum(max(p*u,(1-p)*v) for u,v in a)

def ternary(a,r):
    return [(r*(1+a)/2,r*(1-a)/2),(1-r,1-r),(r*(1-a)/2,r*(1+a)/2)]

def binary(b):
    return [((1+b)/2,(1-b)/2),((1-b)/2,(1+b)/2)]

def render(path,table,frequencies,seed):
    # Integer score inventory: 400 draws per state, then deterministic shuffle.
    score=[]
    for state in range(2):
        for j,pair in enumerate(table):
            count=pair[state]*400
            assert count.denominator==1
            score.extend([(state,j)]*int(count))
    random.Random(seed).shuffle(score)
    length=320;rate=8000
    def carrier(f):
        return [round(10000*(0.5-0.5*math.cos(2*math.pi*i/(length-1)))*math.sin(2*math.pi*f*i/rate)) for i in range(length)]
    left=[carrier(f) for f in (300,700)]
    right=[carrier(f) for f in frequencies]
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed'))
        w.writeframes(b''.join(struct.pack('<hh',l,r) for s,j in score for l,r in zip(left[s],right[j])))
    with wave.open(str(path),'rb') as w:
        assert w.getnframes()==len(score)*length
        samples=struct.unpack('<'+'h'*(2*w.getnframes()),w.readframes(w.getnframes()))
    def decode(segment,templates):
        return min(range(len(templates)),key=lambda j:sum((x-y)**2 for x,y in zip(segment,templates[j])))
    decoded=[]
    for i in range(len(score)):
        frame=samples[2*i*length:2*(i+1)*length]
        decoded.append((decode(frame[::2],left),decode(frame[1::2],right)))
    assert decoded==score
    assert Counter(decoded)==Counter(score)
    return {'episodes':len(score),'symbols_recovered':2*len(score),'seconds':len(score)*length/rate,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    results=[]
    for n in range(1,8):
        x,y=repeat(A,n),repeat(B,n)
        lo,hi,gap=compare(x,y)
        assert (lo>=0)==(n not in (1,3)) and hi>0
        assert accuracy(x)-accuracy(y)==gap
        results.append({'n':n,'A':str(accuracy(x)),'B':str(accuracy(y)),'min_call_gap':str(lo),'max_call_gap':str(hi)})
    count=0
    for ai,bi,ri in product(range(1,10),repeat=3):
        a,b,r=F(ai,10),F(bi,10),F(ri,10)
        x,y=repeat(ternary(a,r),2),repeat(binary(b),2)
        expected=a>=b and a*r*(2-r)>=b and r*r*a*(1-a*a)>=2*b-a*(1+b*b)
        assert (compare(x,y)[0]>=0)==expected
        count+=1
    C=[(p/2,q/2) for p,q in A+B]
    assert compare(tensor(A,C),tensor(B,C))[0]>=0
    assert compare(S,C)[0]>=0
    assert compare(tensor(A,S),tensor(B,S))[0]<0
    skew=F(1,20)
    x,y=accuracy(tensor(A,S),skew),accuracy(tensor(B,S),skew)
    assert (x,y)==(F(77197,80000),F(779,800))
    # Explicit two-read garbling into B's three posterior classes.
    u=posterior(repeat(A,2));v=posterior(repeat(B,2));target=F(4,5)
    scale=target*v[target]/call(u,0)
    top_mass=scale*sum(w for t,w in u.items() if t>0)
    neutral_fill=v[target]-top_mass
    assert 0<=scale<=1 and 0<=2*neutral_fill<=u[F(0)]
    # Keep fraction scale of each sign; allocate neutral_fill to each; rest goes to zero.
    joint=Counter()
    for t,w in u.items():
        if t>0: allocations={target:scale,F(0):1-scale}
        elif t<0: allocations={-target:scale,F(0):1-scale}
        else: allocations={target:neutral_fill/w,-target:neutral_fill/w,F(0):1-2*neutral_fill/w}
        for z,f in allocations.items():
            assert f>=0
            for state,s in enumerate((1,-1)):
                joint[state,z]+=w*(1+s*t)*f/2
    for z,w in v.items():
        for state,s in enumerate((1,-1)):
            assert joint[state,z]==w*(1+s*z)/2
    out=Path(__file__).resolve().parent
    audio={'A':render(out/'selective.wav',A,(750,550,350),698),
           'B':render(out/'continuous.wav',B,(750,350),699)}
    receipt={'method':'literal ordered products; Fraction posterior calls; explicit rational garbling; original PCM inventory',
             'horizons':results,'two_read_grid_profiles':count,'garbling_scale':str(scale),'garbling_neutral_mass_per_sign':str(neutral_fill),
             'side_accuracy_at_1_20':[str(x),str(y)],'audio':audio,'assertion_failures':0}
    # x and y here remain the two skew-prior accuracy fractions.
    (out/'native-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
