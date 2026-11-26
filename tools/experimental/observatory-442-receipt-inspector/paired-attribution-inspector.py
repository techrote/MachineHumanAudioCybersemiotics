"""Refs #442/#443. Synthetic paired source-attribution audit; no human evidence.
python paired-attribution-inspector.py PINNED_DIR FROZEN_OUTPUT NEW_OUTPUT
"""
import collections, hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np
PIN='9486d2db02cc8bd0cea3f1e4d440ff38e7304683'
BLOBS={'asynchronous-attribution.py':'134b56746da67eca0e0f7ff9da9b2b4740c5bc8b','temporal-admission.py':'6a2821c9c4453c1f462da279f439aa8fb601e3ed','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def audit(root,frozen,out):
    for n,h in BLOBS.items(): assert blob((root/n).read_bytes())==h,n
    for n,h in json.loads((frozen/'manifest.json').read_text()).items(): assert sha((frozen/n).read_bytes())==h,n
    ref=json.loads((frozen/'receipt.json').read_text()); u=runpy.run_path(str(root/'asynchronous-attribution.py'))
    _,_,_,book,_,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    rng=np.random.default_rng(ref['seed']); excluded=np.array(ref['excluded']); origins=np.r_[rng.choice(np.setdiff1d(np.arange(52000),excluded),12,False),rng.choice(np.setdiff1d(np.arange(52000,len(book)),excluded),12,False)]; assert origins.tolist()==ref['origins']
    used=set(map(int,np.r_[excluded,origins])); cap=u['CAP']; t=np.arange(960)/16000; env=np.minimum(1,np.minimum(np.arange(960)/80,(959-np.arange(960))/80))
    def render(k,phase,g):
        z=np.zeros((10,1280)); z[:,:960]=env*np.sin(2*np.pi*(400+100*book[k,:,None])*t+phase[:,None]); x=np.interp(cap,u['arrival'](g),z.ravel(),left=0,right=0); return x/np.linalg.norm(x)
    def candidates(pcm,g):
        allowed,conc,guard=u['feature'](pcm,g); idx=np.arange(len(book))
        for s in range(10): idx=idx[allowed[s,book[idx,s]]]
        return set(map(int,idx)),conc,guard
    def union(sets): return set().union(*sets)
    def verdict(s,target,rival):
        n=len(s); return dict(outcome=('correct' if target in s else 'wrong') if n==1 else ('ambiguous' if n else 'empty'),count=n,retained=target in s,rival_retained=rival in s,unique=next(iter(s)) if n==1 else None)
    rows=[]; summary={}; checks=0; grids=u['GRIDS']; refs=iter(ref['rows'])
    for i in map(int,origins):
        j=int(rng.choice(np.setdiff1d(np.flatnonzero(np.count_nonzero(book!=book[i],axis=1)==7),list(used)))); used.add(j)
        ph=rng.uniform(0,2*np.pi,(2,10)); noise=rng.normal(size=len(cap)); noise/=np.linalg.norm(noise)
        for label,ga,gb,gain,snr in u['CASES']:
            x=render(i,ph[0],ga)+gain*render(j,ph[1],gb)
            if snr is not None: x=x+noise*np.linalg.norm(x)*10**(-snr/20)
            pcm=np.rint(x*(2048/max(abs(x)))).astype('<i2'); digest=sha(pcm.tobytes()); f=[candidates(pcm,g) for g in grids]; sets,conc,guard=map(list,zip(*f))
            base=dict(nominal=sets[2],concentration=sets[int(np.argmax(conc))],union=union(sets),guard08=union(s for s,v in zip(sets,guard) if v<=min(guard)+.08)); pair=[]; cue_sets=[]
            for target,rival,g in [(i,j,ga),(j,i,gb)]:
                r=next(refs); assert (r['target'],r['rival'],r['condition'],r['pcm_sha256'])==(target,rival,label,digest)
                cue=tuple(round(v/10)*10 for v in g); adm=[k for k,h in enumerate(grids) if max(abs(a-b) for a,b in zip(h,cue))<=20]; assert adm==r['admitted']
                selected=[k for k in adm if guard[k]<=min(guard[n] for n in adm)+.08]; p=dict(base,cue_union=union(sets[k] for k in adm),cue_guard08=union(sets[k] for k in selected),oracle=candidates(pcm,g)[0]); v={n:verdict(s,target,rival) for n,s in p.items()}; assert v==r['decisions']; checks+=len(v); assert sum(target in s for s in sets)==r['target_support']
                pair.append(dict(target=target,cue=cue,admitted=adm,selected=selected,decisions=v)); cue_sets.append(p['cue_guard08'])
            record=dict(condition=label,pcm_sha256=digest,A=pair[0],B=pair[1],grid_counts=[len(s) for s in sets],A_support=[k for k,s in enumerate(sets) if i in s],B_support=[k for k,s in enumerate(sets) if j in s],cue_candidate_overlap=len(cue_sets[0]&cue_sets[1])); rows.append(record)
            d=summary.setdefault(label,dict(pairs=0,cue_identical=0,admission_identical=0,both_correct=0,A_only=0,B_only=0,neither=0,candidate_overlap=0)); d['pairs']+=1; d['cue_identical']+=pair[0]['cue']==pair[1]['cue']; d['admission_identical']+=pair[0]['admitted']==pair[1]['admitted']; a,b=[p['decisions']['cue_guard08']['outcome']=='correct' for p in pair]; d['both_correct' if a and b else 'A_only' if a else 'B_only' if b else 'neither']+=1; d['candidate_overlap']+=bool(record['cue_candidate_overlap'])
    assert next(refs,None) is None and checks==2016
    out.mkdir(); receipt=dict(schema='mhac-paired-attribution-inspector-v1',upstream=PIN,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frozen_receipt_sha256=sha((frozen/'receipt.json').read_bytes()),runtime=[sys.version.split()[0],np.__version__],checks=checks,summary=summary,rows=rows,limits='Paired finite synthetic corpus, no new holdout; same PCM with two intended roles. Privileged rounded cue not inferred or authenticated. No causal or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    for s in ref['specimens']:
        p=frozen/s['file']; (out/p.name).write_bytes(p.read_bytes())
        with wave.open(str(p),'rb') as w: assert sha(w.readframes(w.getnframes()))==s['sha256']
    gallery=''.join('<p>'+html.escape(s['file'])+' <audio controls preload="none" src="'+s['file']+'"></audio></p>' for s in ref['specimens'])
    page='''<!doctype html><meta charset="utf-8"><title>Paired attribution inspector</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}select{max-width:100%}</style><h1>Paired source attribution</h1><p>Same PCM, two intended roles. Cue is simulator truth, not an acoustic measurement. No human evidence.</p><label>Mixture <select id="pick"></select></label><pre id="detail"></pre><h2>Condition summary</h2><pre>SUMMARY</pre><h2>Frozen upstream audio examples</h2><p>Opt-in playback, start low; no calibrated SPL.</p>GALLERY<a href="receipt.json">Complete replay receipt</a><script>const rows=ROWS;const p=document.getElementById('pick'),d=document.getElementById('detail');rows.forEach((r,i)=>p.add(new Option(r.condition+' / '+r.A.target+' vs '+r.B.target,i)));function show(){d.textContent=JSON.stringify(rows[+p.value],null,2)}p.onchange=show;show();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(page.replace('SUMMARY',html.escape(json.dumps(summary,indent=2))).replace('GALLERY',gallery).replace('ROWS',json.dumps(rows).replace('</','<\\/')),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,indent=2))
if __name__=='__main__': audit(*(pathlib.Path(s) for s in sys.argv[1:]))
