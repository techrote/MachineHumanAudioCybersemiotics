"""MHAC #703: independent-method rational channel witness and PCM inventory."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from collections import Counter
import hashlib, json, math, random, struct, wave

ROOT = Path(__file__).resolve().parent

def hinge(e, z):
    return sum(max(Q(0), p-z*q) for p,q in zip(*e))

def join(e,r):
    return [[p*q for p,q in product(a,b)] for a,b in zip(e,r)]

def check(e,f):
    knots={p/q for g in (e,f) for p,q in zip(*g)}
    return all(hinge(e,z)>=hinge(f,z) for z in knots), len(knots)

def fixture(a):
    # Closed-form rows derived from slope jumps, unlike JS slope construction.
    mass=Q(15,2)+3*a; moment=6+3*a
    e=[[1/moment,3*(a+1)/moment,2/moment],
       [4/mass,3*(a+1)/mass,Q(1,2)/mass]]
    f=[[(3+a)/moment,(3+2*a)/moment],
       [(6+2*a)/mass,(a+Q(3,2))/mass]]
    for g in (e,f):
        assert all(sum(row)==1 and min(row)>0 for row in g)
    return e,f

def multiplier(a):
    u,v=Q(0),Q(1); c=[]
    while v>0:
        c.append(v);u,v=v,a*v-u
    return c

def side(c):
    q=[v/2**j for j,v in enumerate(c)]
    return [[v/sum(row) for v in row] for row in (c,q)]

def render(name,counts,seed):
    # One conditional side-symbol inventory. Not a full compound inventory.
    fs=8000; n=400; freqs=[300,500,700,900]
    templates=[[round(13000*math.sin(2*math.pi*f*i/fs)*math.sin(math.pi*i/(n-1))**2)
                for i in range(n)] for f in freqs]
    seq=[j for j,c in enumerate(counts) for _ in range(c)]
    random.Random(seed).shuffle(seq)
    file=ROOT/name
    with wave.open(str(file),'wb') as w:
        w.setparams((1,2,fs,0,'NONE','not compressed'))
        w.writeframes(b''.join(struct.pack('<'+str(n)+'h',*templates[j]) for j in seq))
    with wave.open(str(file),'rb') as w:
        pcm=w.readframes(w.getnframes())
    decoded=[]
    for i in range(len(seq)):
        v=struct.unpack_from('<'+str(n)+'h',pcm,i*2*n)
        decoded.append(min(range(4),key=lambda j:sum((x-y)**2 for x,y in zip(v,templates[j]))))
    assert decoded==seq and [Counter(decoded)[j] for j in range(4)]==counts
    return {'frames':len(seq),'counts':counts,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}

def main():
    profiles=knots=negative=0
    for den in range(2,19):
        for num in range(1,2*den):
            a=Q(num,den);e,f=fixture(a);c=multiplier(a)
            ok,k=check(join(e,side(c)),join(f,side(c)));assert ok;knots+=k
            # Test the count-compressed repeated binary side: P+ half/half,
            # P- 2/3,1/3; likelihood ratio spacing 2.
            n=2*math.ceil(2/(2-a))-3
            repeated=[Q(math.comb(n,i)) for i in range(n+1)]
            ok,k=check(join(e,side(repeated)),join(f,side(repeated)));assert ok;knots+=k
            shorter=[Q(math.comb(n-1,i)) for i in range(n)]
            ok,k=check(join(e,side(shorter)),join(f,side(shorter)));assert not ok;knots+=k
            ok,k=check(join(e,side(c[:-1])),join(f,side(c[:-1])));assert not ok;knots+=k
            profiles+=1;negative+=2
    a=Q(3,2);e,f=fixture(a);r=side(multiplier(a))
    assert r==[[Q(8,33),Q(12,33),Q(10,33),Q(3,33)],[Q(64,135),Q(48,135),Q(20,135),Q(3,135)]]
    receipt={'profiles':profiles,'literal_product_knot_checks':knots,'negative_controls':negative,
             'audio':{'plus':render('side-plus.wav',[8,12,10,3],703),
                      'minus':render('side-minus.wav',[64,48,20,3],704)}}
    (ROOT/'native-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
