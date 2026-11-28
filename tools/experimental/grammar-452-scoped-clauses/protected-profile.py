"""Refs #452 / #453. Grammars lane: synthetic negotiated profile, not wire compatible.
One GPT-6.2 agent; no human evidence or change to accepted protocols.
"""
from collections import Counter, defaultdict
from itertools import combinations
from hashlib import sha256
from pathlib import Path
import json, math, sys, wave, struct

PINS = {'grammar': '0fe95f804a20a8f3a6e59a2f8089d8b83f438204',
        'grammar_blob': 'dae13404d68c00bbe537d128802a1848aac2d952',
        'measurement': 'ed648880b0588b2852a0b691a8f603a2a0a49a13',
        'measurement_blob': '6788b2a9d3df49eea24737062d414a19e95bb29b',
        'main': '495a98ca12bae467a507031f04931aa4254b1866'}
KINDS = ('ack', 'terminal', 'quote', 'certificate')
PAIRS = tuple(combinations(range(20), 2))
POSITIONS = tuple(range(8))

def semantic(row):
    pending = 1
    for i, v in enumerate(row):
        if v in (0, 1, 2, 3, 14): pending -= 1
        elif 4 <= v <= 10: pass
        elif v in (11, 12): pending += 1
        else: return False
        if pending == 0: return all(x == 13 for x in row[i+1:])
    return False

def digits(k, n):
    return tuple(k // 17**i % 17 for i in reversed(range(n)))

def matrix(pos):
    return [[math.prod((x-j)*pow(i-j, -1, 17) for j in pos if j != i)%17
             for i in pos] for x in POSITIONS]

def interpolate(w, vals):
    return tuple(sum(a*b for a,b in zip(row, vals))%17 for row in w)

def books():
    free = [k for k in range(4913, 13*4913) if not semantic(digits(k,4))]
    assert len(free) == 55858
    full, old, new = {}, {}, {}
    w = matrix((0,1,4,5)); h = g = 0
    for kind in KINDS:
        acts = PAIRS if kind == 'certificate' else tuple((a,) for a in range(20))
        for address in range(192):
            for i, act in enumerate(acts):
                j = address*len(acts)+i
                k = j if kind == 'ack' else 14*4913+j if kind == 'terminal' else free[36480+j] if kind == 'quote' else free[j]
                msg = (kind,address,*act); body = interpolate(w,digits(k,4))
                full[msg] = body
                for v in body:
                    h=(h*31+v+1)%1000000007; g=(g*37+v+1)%1000000009
                if address < 16: old[msg] = body
    assert (h,g)==(95787044,408117442) and len(set(full.values()))==48000
    # Degree <=2: same 17 frequencies and eight slots, smaller address space.
    for i,msg in enumerate(old):
        a,b,c=digits(i,3)
        new[msg]=tuple((a+b*x+c*x*x)%17 for x in POSITIONS)
    assert len(set(new.values()))==len(old)==4000
    return full, old, new

class Codec:
    def __init__(self, book, k):
        self.book, self.k = book,k
        self.reverse = {v:m for m,v in book.items()}
        self.weights = {p:matrix(p) for p in combinations(POSITIONS,k)}
    def encode(self, msg): return self.book[msg]
    def decode(self, body, minimum=None, correct=False):
        if len(body)!=8 or any(v is not None and (type(v)!=int or not 0<=v<17) for v in body): return None
        seen=tuple(i for i,v in enumerate(body) if v is not None)
        if len(seen)<max(self.k, minimum or self.k): return None
        # Correct only within 2e+s<d for degree-two profile; else consistency only.
        allow = int(correct and self.k==3 and len(seen)>=5)
        found=set()
        for p in combinations(seen,self.k) if allow else (seen[:self.k],):
            y=interpolate(self.weights[p],tuple(body[i] for i in p))
            if y in self.reverse and sum(y[i]!=body[i] for i in seen)<=allow:
                found.add(self.reverse[y])
        return next(iter(found)) if len(found)==1 else None

def mixed(book):
    # Four observed symbols, exactly one substituted: literal projection lookup.
    counts=Counter(); masks=[]; witness=None
    for p in combinations(POSITIONS,4):
        lookup={tuple(w[i] for i in p):m for m,w in book.items()}
        assert len(lookup)==len(book)
        n=0
        for vals,m in lookup.items():
            for j in range(4):
                for v in range(17):
                    if v==vals[j]: continue
                    got=lookup.get(vals[:j]+(v,)+vals[j+1:])
                    if got is None: continue
                    assert got!=m
                    n+=1; counts[m[0],got[0]]+=1
                    if witness is None and m[0]!=got[0]:
                        damaged=[None]*8
                        for i,x in zip(p,vals): damaged[i]=x
                        damaged[p[j]]=v
                        witness={'sent':m,'body':book[m],'damaged':damaged,'got':got}
        masks.append({'surviving':p,'wrong':n})
    return {'faults':len(book)*70*4*16,'wrong':sum(counts.values()),
            'cross_kind':sum(v for (a,b),v in counts.items() if a!=b),
            'matrix':{a:{b:counts[a,b] for b in KINDS} for a in KINDS},'masks':masks,'witness':witness}

def clean_masks(codec):
    result={}
    for n in (0,4,5):
        counts=Counter()
        for m,w in codec.book.items():
            for p in combinations(POSITIONS,n):
                body=tuple(None if i in p else v for i,v in enumerate(w))
                for name,minimum in [('normal',None),('strict5',5)]:
                    got=codec.decode(body,minimum)
                    assert got is None or got==m
                    counts[name]+=int(got==m)
        result[n]={'trials':len(codec.book)*math.comb(8,n),**counts}
    return result

def correction(old,new):
    # Fixed stratified 40 messages, all 56 three-erasure masks, all five
    # surviving positions, deterministic +1 substitution, same semantic inputs.
    result=Counter()
    for m in list(old.book)[::100]:
        for erased in combinations(POSITIONS,3):
            for j in POSITIONS:
                if j in erased: continue
                for name,c,correct in [('legacy',old,False),('protected',new,False),('protected_correct',new,True)]:
                    w=c.encode(m); body=tuple(None if i in erased else (v+1)%17 if i==j else v for i,v in enumerate(w))
                    got=c.decode(body,correct=correct)
                    assert got is None or got==m
                    result[name]+=int(got==m)
    return {'trials_per_policy':40*56*5,'correct':dict(result)}

def audio(out,name,body,codec,expected):
    samples=[0]*10240
    for i,v in enumerate(body):
        if v is not None:
            for n in range(960):
                samples[i*1280+n]=round(2048*min(1,n/80,(959-n)/80)*math.sin(2*math.pi*(400+100*v)*n/16000+.137))
    observed=[]
    for i in POSITIONS:
        x=samples[i*1280+160:i*1280+800]
        if not any(x): observed.append(None); continue
        scores=[sum(v*math.cos(2*math.pi*f*n/16000) for n,v in enumerate(x))**2+sum(v*math.sin(2*math.pi*f*n/16000) for n,v in enumerate(x))**2 for f in range(400,2001,100)]
        observed.append(max(range(17),key=scores.__getitem__))
    assert observed==list(body) and codec.decode(observed)==expected
    with wave.open(str(out/name),'wb') as f:
        f.setparams((1,2,16000,len(samples),'NONE','not compressed'))
        f.writeframes(struct.pack('<%dh'%len(samples),*samples))
    return {'name':name,'symbols':observed,'decoded':expected,'peak':max(map(abs,samples))}

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    full,b0,b1=books(); old,new=Codec(b0,4),Codec(b1,3)
    x,y=mixed(b0),mixed(b1); assert y['wrong']==0 and x['cross_kind']>0
    clean={'legacy':clean_masks(old),'protected':clean_masks(new)}
    cor=correction(old,new); assert cor['correct']=={'legacy':0,'protected':0,'protected_correct':11200}
    w=x['witness']; m=w['sent']; assert old.decode(w['damaged'])==w['got']
    p=next(i for i,v in enumerate(w['damaged']) if v is not None and v!=w['body'][i])
    damaged=tuple(None if v is None else (b1[m][i]+1)%17 if i==p else b1[m][i] for i,v in enumerate(w['damaged']))
    specimens=[audio(out,'legacy-clean.wav',b0[m],old,m),audio(out,'legacy-mixed.wav',w['damaged'],old,w['got']),audio(out,'protected-clean.wav',b1[m],new,m),audio(out,'protected-mixed.wav',damaged,new,None)]
    fullrev={v:m for m,v in full.items()}; overlaps=[(m,fullrev[v]) for m,v in b1.items() if v in fullrev]
    receipt={'schema':'mhac-negotiated-protection-v1','pins':PINS,'duration_ms':640,'capacity':{'full':48000,'matched':4000,'quadratic_total':4913,'addresses':16,'acts':20},'mixed':{'legacy':x,'protected':y},'clean':clean,'correction':cor,'profile_overlap':{'count':len(overlaps),'different_meaning':sum(a!=b for a,b in overlaps),'example':next(((a,b) for a,b in overlaps if a!=b),None)},'specimens':specimens,'limits':'Aligned synthetic PCM, uniform finite fault counts not probabilities; no profile negotiation, authentication, human evidence or energy matching. Original source not executed by this script.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Protected profile</title><h1>Protected profile</h1><p>Synthetic aligned audio. Start at low volume. Different wire profiles require explicit agreement.</p>'+''.join('<h2>'+s['name']+'</h2><p>'+str(s['decoded'])+'</p><audio controls preload="none" src="'+s['name']+'"></audio>' for s in specimens)+'<p><a href="receipt.json">Exact results</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='mixed'},indent=2)); print(json.dumps({k:{a:b for a,b in v.items() if a!='masks'} for k,v in receipt['mixed'].items()},indent=2))

if __name__=='__main__': run(Path(sys.argv[1]))
