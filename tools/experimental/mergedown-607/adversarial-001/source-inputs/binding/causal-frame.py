"""Refs #452 / Draft #453. Causal aligned PCM frame admission, synthetic only.
Usage: python causal-frame.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Two-slot silence vs two-slot explicit terminal (2200 Hz); no EOF admission.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='9e45f77a11c637c03f7e1ac50b6b6802ffc97cfc'
BLOBS={'prefix-disjoint.py':'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55'}
SEED=45234
SLOT=1280
END=18
HORIZON=22
CASES=('clean','noise','one-drop','two-drop','header-flip','cut-flip','false-end-flip','terminal-drop','terminal-loss')

def sha(b): return hashlib.sha256(b).hexdigest()
def pcm(tokens,seed,noise):
    n=np.arange(960); a=np.zeros((len(tokens),SLOT),dtype=float)
    for i,v in enumerate(tokens):
        if v is not None: a[i,:960]=1500*np.minimum(1,np.minimum(n/80,(959-n)/80))*np.sin(2*np.pi*(400+100*v)*n/16000+.137)
    if noise: a+=np.random.default_rng(seed).normal(0,noise,a.shape)
    return np.clip(np.rint(a),-2048,2048).astype('<i2')

BASIS=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(640)/16000)
def observe(slot):
    scores=abs(BASIS@slot[160:800])*2/640; k=int(scores.argmax())
    return (END if k==17 else k) if scores[k]>=200 else None

def receive(chunks,books,terminal,joint):
    # One aligned frame attempt, bounded memory and horizon. No endpoint argument.
    seen=[]; run=0; block=np.empty(0,dtype='<i2'); got=None; release=None; reason='timeout'; end=None
    for chunk in chunks:
        block=np.concatenate((block,chunk))
        while len(block)>=SLOT:
            v=observe(block[:SLOT]); block=block[SLOT:]; seen.append(v)
            run=run+1 if v==terminal else 0
            if run==2:
                body=seen[:-2]; end=len(body); reason='boundary'
                if end in books and END not in body:
                    i=joint(books[end],body,2)
                    if i is not None: got=[end,i]; release=len(seen)
                return got,release,reason,end,seen
            if len(seen)==HORIZON: return got,release,reason,end,seen
    return got,release,'incomplete-capture',end,seen

def scenario(word,case,terminal):
    n=len(word); v=list(word)+[terminal,terminal]
    if case=='one-drop': v[6]=None
    if case=='two-drop': v[6:8]=[None,None]
    if case in ('header-flip','cut-flip','false-end-flip'):
        v[:2]=[16-v[0]]*2
    if case=='cut-flip': v=v[:13] if n==18 else v[:9]
    if case=='false-end-flip':
        k=13 if n==18 else 9; v[k:k+2]=[terminal,terminal]
    if case=='terminal-drop': v[n]=None
    if case=='terminal-loss': v[n:n+2]=[None,None]
    return v+[None]*(HORIZON-len(v))

def run(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b
    m=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,names=m['build'](root)
    joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']; old,new=raw
    lookup={tuple(w):i for i,w in enumerate(old)}
    aliases=[j for j,w in enumerate(new) if tuple(w) in lookup and lookup[tuple(w)]!=j]
    rng=np.random.default_rng(SEED)
    origins=[(13,int(i)) for i in rng.choice(len(old),8,False)]+[(18,int(i)) for i in rng.choice(len(old),8,False)]+[(18,len(old)+int(i)) for i in rng.choice(aliases,8,False)]
    short=np.column_stack((np.zeros((len(old),3),dtype=int),old))
    body=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    def meaning(n,i): return names[i if n==13 or i<len(old) else i-len(old)]
    out.mkdir(parents=True,exist_ok=False); stats={}; traces=[]; specimens=[]
    for mode in ('independent','quartic'):
        long=np.column_stack((np.full((len(body),3),16),(body+np.arange(15)**4)%17 if mode=='quartic' else body)); books={13:short,18:long}
        for framing,terminal in [('silence',None),('tone',END)]:
            for case in CASES:
                for j,(n,i) in enumerate(origins):
                    word=books[n][i].tolist(); tokens=scenario(word,case,terminal); seed=SEED+100*CASES.index(case)+j
                    a=pcm(tokens,seed,60 if case=='noise' else 0).ravel()
                    result=receive((a[k:k+503] for k in range(0,len(a),503)),books,terminal,joint)
                    assert result==receive((a[k:k+SLOT] for k in range(0,len(a),SLOT)),books,terminal,joint)
                    got,release,reason,end,seen=result
                    if release is not None:
                        assert receive([a[:(release-1)*SLOT]],books,terminal,joint)[0] is None
                    intended=meaning(n,i); decoded=meaning(*got) if got is not None else None
                    assert seen==tokens[:len(seen)]
                    # No full capture or endpoint is needed to reproduce the decision.
                    outcome='correct' if got==[n,i] else 'wrong' if got is not None else 'abstain'
                    key=f'{mode}:{framing}:{case}'; stats.setdefault(key,Counter())[outcome]+=1
                    traces.append({'mode':mode,'framing':framing,'case':case,'origin':[n,i],'seed':seed,'tokens':tokens,'seen':seen,'decoded':got,'intended_meaning':intended,'decoded_meaning':decoded,'outcome':outcome,'boundary':end,'release_slot':release,'reason':reason,'pcm_sha256':sha(a.tobytes())})
                    if j==16 and case in ('clean','two-drop','cut-flip','false-end-flip','terminal-loss'):
                        f=f'{mode}-{framing}-{case}.wav'
                        with wave.open(str(out/f),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(a.tobytes())
                        specimens.append({'file':f,'outcome':outcome,'origin':[n,i],'decoded':got,'intended_meaning':intended,'decoded_meaning':decoded,'pcm_sha256':sha(a.tobytes())})
    assert len(traces)==864
    assert all(t['release_slot'] is None or t['release_slot']==t['boundary']+2 for t in traces)
    assert all(t['outcome']=='correct' for t in traces if t['case'] in ('clean','noise','one-drop','header-flip'))
    receipt={'schema':'mhac-causal-frame-v1','pin':PIN,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'origins':origins,'slots_ms':80,'horizon_slots':HORIZON,'terminal_hz':2200,'observations':len(traces),'stats':stats,'specimens':specimens,'limits':'Aligned start, fixed slot clock, single frame attempt, radius-two unique decoder with known erasures, 22-slot horizon. Silence is also dropout. Explicit delimiter needs an extra tone and energy; equal slot budgets, not energy or compute matched. Synthetic noise only; no source attribution, authentication, insertion/deletion recovery, real audition or human evidence.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}: {s["outcome"]}; intended {s["intended_meaning"]}; decoded {s["decoded_meaning"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Causal frame admission</title><h1>Causal frame admission</h1><p>Synthetic, aligned. Start at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
