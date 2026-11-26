"""Exact rational row products and original enumerated stereo scores; same-agent check."""
from fractions import Fraction as F
from itertools import product, permutations
from pathlib import Path
from collections import Counter
import hashlib, json, math, random, struct, wave
ROOT = Path(__file__).resolve().parent
STATES = list(product((-1, 1), repeat=4))  # A,C,U,V

def model(alpha, beta):
    pi = [(1 + F(a*u,4) + F(c,4)*(alpha*u+beta*v) + F(a*c,4))/16 for a,c,u,v in STATES]
    assert sum(pi)==1 and min(pi)>0
    labels = {'A':[s[0] for s in STATES], 'C':[s[1] for s in STATES], 'B':[s[2:] for s in STATES]}
    kernels={}
    for stage,lab in labels.items():
        kernels[stage]=[[pi[j]/sum(pi[k] for k in range(16) if lab[k]==lab[i]) if lab[i]==lab[j] else F(0) for j in range(16)] for i in range(16)]
    return pi,kernels

def compose(left,right):
    return [[sum((a*b for a,b in zip(row,col)),F(0)) for col in zip(*right)] for row in left]

def run(kernels,word):
    result=kernels[word[0]]
    for stage in word[1:]: result=compose(result,kernels[stage])
    return result

def census():
    count=0; cycles=[]
    for alpha,beta in [(F(0),F(1)),(F(3,5),F(4,5)),(F(-3,5),F(4,5)),(F(1),F(0)),(F(-1),F(0))]:
        pi,kernels=model(alpha,beta); J=[pi]*16
        for p in kernels.values():
            assert compose(p,p)==p
            assert all(pi[i]*p[i][j]==pi[j]*p[j][i] for i in range(16) for j in range(16))
        for a,b in permutations('ABC',2):
            assert run(kernels,a+b)!=J
            if a!='B':
                # P_a P_b P_a has centered eigenvalue 1/16.
                expected=[[pi[j]+(kernels[a][i][j]-pi[j])/16 for j in range(16)] for i in range(16)]
                assert run(kernels,a+b+a)==expected
            count+=1
        for p in permutations('ABC'):
            w=''.join(p); K=run(kernels,w); K2=compose(K,K)
            assert (K==J)==(alpha==0 and w[1]=='B')
            assert (K2==J)==(alpha==0)
            # All three-stage centered operators rank <=1; cycle eigenvalue alpha/64.
            assert all(K2[i][j]-pi[j]==alpha*(K[i][j]-pi[j])/64 for i in range(16) for j in range(16))
            cycles.append({'alpha':str(alpha),'word':w,'reset':K==J,'worst_row_tv':str(max(sum(abs(v-p) for v,p in zip(row,pi))/2 for row in K))})
            count+=1
        K=run(kernels,'ABC')
        assert all(K[i][j]==pi[j]*(1+alpha*STATES[i][0]*STATES[j][1]/16) for i in range(16) for j in range(16))
    pi,K=model(F(-1),F(0)); x=run(K,'AAC'); y=run(K,'ABC')
    assert x!=[pi]*16 and y!=[pi]*16
    assert all((x[i][j]+4*y[i][j])/5==pi[j] for i in range(16) for j in range(16))
    return count,cycles

def score(r,n=64):
    out=[]
    for a,c in product((-1,1),repeat=2):
        k=n*(1+r*a*c)/4; assert k.denominator==1
        out.extend([(a,c)]*int(k))
    return out

def audio(name,pairs):
    pairs=list(pairs); random.Random(666).shuffle(pairs)
    rate=8000; size=320
    tones={s:[math.sin(2*math.pi*f*t/rate) for t in range(size)] for s,f in [(-1,300),(1,500)]}
    samples=[round(16000*tones[b][t]) for a,c in pairs for t in range(size) for b in (a,c)]
    path=ROOT/name
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed')); w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    with wave.open(str(path),'rb') as w:
        data=struct.unpack('<'+'h'*(2*w.getnframes()),w.readframes(w.getnframes()))
    decoded=[]
    for i in range(len(pairs)):
        decoded.append(tuple(max(tones,key=lambda b:sum(data[2*(i*size+t)+ch]*tones[b][t] for t in range(size))) for ch in (0,1)))
    assert decoded==pairs
    return {'file':name,'frames':len(pairs),'decoded_bits':2*len(pairs),'inventory':{str(k):v for k,v in sorted(Counter(decoded).items())},'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

if __name__=='__main__':
    count,cycles=census()
    x=score(F(1,4)); y=score(F(-1,16)); z=x+y*4
    out={'rational_word_checks':count,'cycles':cycles,'hidden_mixture_exact':True,'assertion_failures':0,'audio':[audio('retain-positive.wav',x),audio('retain-negative.wav',y),audio('hidden-mixture.wav',z)]}
    (ROOT/'native-execution.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
