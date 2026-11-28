"""MHAC #452 / Draft #453: synthetic recursive scope, no human evidence.
Vocabulary and ordered-tree convention from recursive.cjs, blob
7d9e305857b59e029913432bb40f713ab84b5a90 at f4f7afa55a2e64cd2a2be250f127247d505fe955.
Run: python polyphonic-depth.py output-directory (Python 3, NumPy).
"""
import itertools, json, sys, wave, hashlib
from pathlib import Path
from collections import Counter
import numpy as np

ATOMS = ('fault','open','stopped','overload')
UNARY = ('not','quote','question','verify','pump-reports','relay-reports','uncertain')
BINARY = ('and','if')
VOCAB = ATOMS + UNARY + BINARY
ARITY = (0,)*4 + (1,)*7 + (2,)*2
MODES = ('prefix','serial','poly')
RATE, SLOT, ACTIVE, AMP = 16000, 1280, 960, 1600
SEED = 452510
FREQ = (np.arange(13)*100+400, np.arange(4)*100+2100)
T = np.arange(ACTIVE)/RATE
W = np.minimum(1,np.minimum(np.arange(ACTIVE),np.arange(ACTIVE)[::-1])/80)
BASIS = [np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/RATE) for f in FREQ]

def catalogue():
    levels = [[], [(a,) for a in ATOMS]]
    for n in range(2,5):
        levels.append([(u,c) for u in UNARY for c in levels[n-1]] + [(b,x,y) for k in range(1,n-1) for b in BINARY for x in levels[k] for y in levels[n-1-k]])
    return sum(levels,[])

def encode(tree):
    out = []
    def walk(t,d):
        k = VOCAB.index(t[0])
        if d>3 or len(t)!=ARITY[k]+1 or len(out)>=4: raise ValueError('bounds')
        out.append((k,d))
        for c in t[1:]: walk(c,d+1)
    walk(tree,0)
    return out

def decode(rows,mode):
    if mode not in MODES or not 1<=len(rows)<=4: return None
    i = 0
    def parse(d):
        nonlocal i
        if i>=len(rows) or d>3: raise ValueError()
        k,depth = rows[i]; i += 1
        if k is None or not 0<=k<len(VOCAB) or (mode!='prefix' and depth!=d): raise ValueError()
        return (VOCAB[k],)+tuple(parse(d+1) for _ in range(ARITY[k]))
    try:
        tree = parse(0)
        return tree if i==len(rows) else None
    except ValueError: return None

def render(rows,mode,phase=0.):
    def tone(b,k):
        x=np.zeros(SLOT)
        if k is not None: x[:ACTIVE]=AMP*W*np.sin(2*np.pi*FREQ[b][k]*T+phase)
        return x
    frames=[]
    for k,d in rows:
        a,b=tone(0,k),tone(1,d)
        frames.extend([a] if mode=='prefix' else [a,b] if mode=='serial' else [a+b])
    return np.rint(np.concatenate(frames)).astype(np.int16)

def receive(pcm,mode):
    if mode not in MODES or len(pcm)%SLOT or not len(pcm): return []
    frames=np.asarray(pcm).reshape(-1,SLOT)[:,160:800].astype(float)
    def band(b):
        scores=np.abs(frames @ BASIS[b].T)*2/640
        order=np.argsort(scores,axis=1)
        return [int(i[-1]) if s[i[-1]]>=AMP*.45 and s[i[-1]]-s[i[-2]]>=AMP*.25 else None for s,i in zip(scores,order)]
    a,b=band(0),band(1)
    if mode=='serial': return list(zip(a[::2],b[1::2])) if len(a)%2==0 else []
    return list(zip(a,b if mode=='poly' else [None]*len(a)))

def classify(got,tree): return 'withheld' if got is None else 'correct' if got==tree else 'wrong'

def main(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    trees=catalogue(); rng=np.random.default_rng(SEED)
    symbolic={m:Counter() for m in MODES}; witnesses={}; traces=[]; energy={}; peak=0
    for m in MODES:
        seen=set()
        for tree in trees:
            rows=encode(tree); key=tuple((k,None if m=='prefix' else d) for k,d in rows)
            assert key not in seen and decode(rows,m)==tree; seen.add(key)
            for i,(k,d) in enumerate(rows):
                for kind,new in [('delete',rows[:i]+rows[i+1:])]+[('substitute',rows[:i]+[(j,d)]+rows[i+1:]) for j in range(13) if j!=k]:
                    got=decode(new,m); status=classify(got,tree); symbolic[m][kind+'_'+status]+=1
                    if status=='wrong': witnesses.setdefault(m+'_'+kind,dict(tree=tree,received=new,decoded=got))
    picks=[trees[i] for i in rng.choice(len(trees),96,replace=False)]
    for i,tree in enumerate(picks):
        rows=encode(tree); j=i%len(rows); k,d=rows[j]; phase=float(rng.uniform(0,2*np.pi))
        for m in MODES:
            for condition in ('clean','noise1000','noise3500','delete','substitute','depth_loss','node_loss'):
                r=rows.copy()
                if condition=='delete': r.pop(j)
                if condition=='substitute': r[j]=((k+1)%13,d)
                if condition=='depth_loss': r[j]=(k,None)
                if condition=='node_loss': r[j]=(None,d)
                pcm=render(r,m,phase) if r else np.array([],dtype=np.int16)
                if condition=='clean': energy[m]=energy.get(m,0)+int(np.sum(pcm.astype(np.int64)**2))
                if condition.startswith('noise'):
                    sd=int(condition[5:]); noise=np.random.default_rng(SEED+i).normal(0,sd,len(pcm)); pcm=np.clip(np.rint(pcm+noise),-32768,32767).astype(np.int16)
                gotrows=receive(pcm,m); got=decode(gotrows,m); status=classify(got,tree)
                if condition=='clean': assert status=='correct'
                peak=max(peak,int(np.max(np.abs(pcm.astype(int)),initial=0)))
                traces.append(dict(mode=m,condition=condition,tree=tree,observed=gotrows,decoded=got,status=status,samples=len(pcm),pcm_sha256=hashlib.sha256(pcm.astype('<i2').tobytes()).hexdigest(),fixture=i,phase=phase))
    specimens=[('outside',('not',('quote',('fault',)))),('inside',('quote',('not',('fault',)))),('conditional',('if',('fault',),('verify',('open',)))),('uncertain',('uncertain',('and',('open',),('stopped',))))]
    gallery=[]
    for name,tree in specimens:
        for m in MODES:
            pcm=render(encode(tree),m); p=out/(name+'-'+m+'.wav')
            with wave.open(str(p),'wb') as w: w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(pcm.astype('<i2').tobytes())
            gallery.append(dict(file=p.name,tree=tree,mode=m,ms=len(pcm)*1000/RATE,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    counts={m:{c:dict(Counter(t['status'] for t in traces if t['mode']==m and t['condition']==c)) for c in sorted({t['condition'] for t in traces})} for m in MODES}
    receipt=dict(schema='mhac-polyphonic-depth-v1',seed=SEED,trees=len(trees),symbolic=symbolic,witnesses=witnesses,pcm_cases=len(traces),pcm=counts,clean_energy=energy,max_trial_peak=peak,specimens=gallery,limitations='Aligned slots, four-node trees, constructed noise and faults; no human, authentication, blind acquisition or physical evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces),encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset=utf-8><title>MHAC polyphonic scope</title><h1>Recursive acoustic scope</h1><p>Synthetic specimens. Start at low volume. No human comprehension claim.</p>'+''.join('<p>'+str(s['tree'])+' / '+s['mode']+' / '+str(s['ms'])+' ms<br><audio controls preload="none" src="'+s['file']+'"></audio></p>' for s in gallery),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('trees','symbolic','pcm_cases','pcm','clean_energy','max_trial_peak')},indent=2))

if __name__=='__main__': main(sys.argv[1])
