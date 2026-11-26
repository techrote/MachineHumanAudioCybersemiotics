"""Refs #448/#449, #452. Synthetic overlap stress. No human evidence.
Usage: python overlap-admission-audit.py PINNED_DIR NEW_OUTPUT_DIR
One AI agent; 2026-11-26. No authentication or physical audition claims.
"""
import hashlib, inspect, json, pathlib, runpy, sys, wave, html
from collections import Counter
import numpy as np
PIN='7053f813bf770c1ec195e0c4485d24f483505045'
PARENT='3aa52100c32f10b89638db67193608e8fe9b04b6'
BLOBS={'competing-starts.py':'af3f673f28e65bb4fc241a22cc603a6cbb041dfb','discourse-sync.py':'cc6b996d6314fdcbb92edc85e12878d5d2077aa7','causal-frame.py':'fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60','prefix-disjoint.py':'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','frame-length-commit.py':'1538e258e53b62fc62315ca11eb9ba34496c5919','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493'}
SEED=448038; SLOT=1280; FS=16000
OFFSETS=(1,0,-1,-2,-3,-4); GAINS=(0.75,1.0,1.35)
POLICIES=('locked','restart','replace-two','body-only','no-suppression')
def sha(b): return hashlib.sha256(b).hexdigest()
def ident(e): return (e['source'],*e['identity'])
def run(root,out):
    for f,h in BLOBS.items():
        b=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h,f
    comp=runpy.run_path(str(root/'competing-starts.py')); sync=runpy.run_path(str(root/'discourse-sync.py')); c=runpy.run_path(str(root/'causal-frame.py')); m=runpy.run_path(str(root/'version-bound-payload.py'))
    joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']; _,raw,names=m['build'](root); old,new=raw
    long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    original=comp['acquire']; source=inspect.getsource(original); condition="if rival['start']-2*SLOT<end:"
    assert source.count(condition)==1
    def variant(replacement):
        ns=dict(original.__globals__); exec(source.replace(condition,replacement),ns); return ns['acquire']
    body=variant("if rival['start']<end:"); free=variant('if False:')
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False); traces=[]; summary={}; specimens=[]; prefix=0
    for j in range(8):
        s=j%2; n=13 if j%2 else 18; n2=31-n
        i=int(rng.integers(len(books[s][n]))); k=int(rng.integers(len(books[1-s][n2])))
        want=[(s,n,i),(1-s,n2,k)]; lead=int(rng.integers(400,1900))
        a,b=[c['pcm'](sync['preamble'](u)+books[u][v][w].tolist()+[18,18],SEED+j,0).ravel().astype(float) for u,v,w in want]
        for off in OFFSETS:
            start=lead+len(a)+off*SLOT
            for gain in GAINS:
                mix=np.zeros(start+len(b)+24*SLOT); mix[lead:lead+len(a)]+=a; mix[start:start+len(b)]+=gain*b
                pcm=np.rint(mix).astype('<i2'); assert np.max(abs(mix))<32768
                h=sha(pcm.tobytes()); case=f'{off}:{gain}'; rows=[]
                for p in POLICIES:
                    fn,mode=(body,'replace-two') if p=='body-only' else (free,'replace-two') if p=='no-suppression' else (original,p)
                    ev=fn(pcm,books,c['observe'],joint,mode); rel=[e for e in ev if e['kind']=='release']; got=list(map(ident,rel))
                    correct=sum((Counter(want)&Counter(got)).values()); wrong=len(got)-correct; missing=2-correct
                    stats=summary.setdefault(case,{}).setdefault(p,Counter()); stats.update(correct=correct,wrong=wrong,missing=missing,suppressed=sum(e['kind']=='suppress-overlap' for e in ev),wait=sum(e['wait_samples'] for e in rel))
                    if j==0:
                        for e in rel:
                            assert fn(pcm[:e['sample']],books,c['observe'],joint,mode)==[x for x in ev if x['sample']<=e['sample']]; prefix+=1
                    row=dict(pair=j,offset_slots=off,gain_b_over_a=gain,policy=p,expected=want,decoded=got,correct=correct,wrong=wrong,missing=missing,pcm_sha256=h,events=ev); traces.append(row); rows.append(row)
                if j==0:
                    f=f'pair{j}-offset{off}-gain{gain}.wav'
                    with wave.open(str(out/f),'wb') as w: w.setparams((1,2,FS,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                    with wave.open(str(out/f),'rb') as w: assert sha(w.readframes(w.getnframes()))==h
                    specimens.append(dict(file=f,offset_slots=off,gain_b_over_a=gain,pcm_sha256=h,peak=int(np.max(abs(pcm.astype(int)))),expected=want,decoded={r['policy']:r['decoded'] for r in rows}))
    assert len(traces)==8*len(OFFSETS)*len(GAINS)*len(POLICIES)
    assert all(v['correct']+v['missing']==16 for d in summary.values() for v in d.values())
    receipt=dict(schema='mhac-overlap-admission-audit-v1',pin=PIN,parent=PARENT,blobs=BLOBS,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),runtime=[sys.version.split()[0],np.__version__],offset_slots=OFFSETS,gains=GAINS,physical_pcm=len(traces)//len(POLICIES),decisions=len(traces),prefix_checks=prefix,summary=summary,specimens=specimens,limits='Aligned additive two-source PCM, offsets relative to first nominal end, no drift/noise/clipping. Gain ratios are amplitude, not energy matched across conditions; matched PCM within condition. Body-only and no-suppression variants differ only in overlap suppression test; experimental alternatives, not independent receiver implementations. Both source messages expected even during overlap. Fixed seeded exploratory corpus, no prevalence, human or authentication claims.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join('<h2>'+html.escape(s['file'])+'</h2><audio controls preload="none" src="'+s['file']+'"></audio><pre>'+html.escape(json.dumps(s['decoded'],indent=2))+'</pre>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Overlap admission audit</title><h1>Overlap admission audit</h1><p>Synthetic PCM; low hardware volume; no autoplay. Gain 20% on load.</p>'+gallery+'<a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': run(*(pathlib.Path(s) for s in sys.argv[1:]))
