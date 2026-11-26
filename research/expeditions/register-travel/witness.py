"""Independent-style literal enumeration and original acoustic score. Same agent, not peer review."""
from collections import Counter
from itertools import product
from pathlib import Path
import json, math, struct, wave, hashlib
ROOT = Path(__file__).resolve().parent

def shift(w, direction, digit):
    return w[1:] + (digit,) if direction == 1 else (digit,) + w[:-1]

def run(initial, directions, digits):
    w = initial
    for direction, digit in zip(directions, digits, strict=True):
        w = shift(w, direction, digit)
    return w

def census():
    profiles = rows = 0
    for q, h in [(2,2),(2,3),(2,4),(3,2),(3,3)]:
        alphabet = range(q)
        for k in range(6):
            draws = list(product(alphabet, repeat=k))
            for directions in product((-1,1), repeat=k):
                p = 0; visited = {p}
                for d in directions:
                    p += d; visited.add(p)
                m = max(0, h-(max(visited)-min(visited)))
                rowtypes = set()
                for start in product(alphabet, repeat=h):
                    c = Counter(run(start,directions,z) for z in draws)
                    assert len(c)==q**(h-m) and all(v*len(c)==q**k for v in c.values())
                    rowtypes.add(frozenset(c.items())); rows += 1
                assert len(rowtypes)==q**m
                profiles += 1
    return profiles, rows

def audio(name,directions):
    # Enumerated score inventory, not an actual random sample or listening trial.
    h=4; rate=8000; count=640; initial=(1,0,1,1)
    score=[run(initial,directions,z) for z in product((0,1),repeat=4)]
    tones=[[tuple(math.sin(2*math.pi*(250+100*j+50*b)*t/rate) for t in range(count)) for b in (0,1)] for j in range(h)]
    pcm=[round(6000*sum(tones[j][b][t] for j,b in enumerate(word))) for word in score for t in range(count)]
    path=ROOT/name
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
    with wave.open(str(path),'rb') as f: data=struct.unpack('<'+'h'*f.getnframes(),f.readframes(f.getnframes()))
    decoded=[]
    for i in range(len(score)):
        frame=data[i*count:(i+1)*count]
        decoded.append(tuple(max((0,1),key=lambda b: sum(x*y for x,y in zip(frame,tones[j][b]))) for j in range(h)))
    assert decoded==score
    return {'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(score),'decoded_bits':len(score)*h,'inventory':dict(sorted(Counter(''.join(map(str,w)) for w in decoded).items()))}

if __name__=='__main__':
    profiles,rows=census()
    report={'profiles':profiles,'rows':rows,'assertion_failures':0,'audio':[audio('forward.wav',(1,1,1,1)),audio('alternating.wav',(1,-1,1,-1))]}
    (ROOT/'native-execution.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
