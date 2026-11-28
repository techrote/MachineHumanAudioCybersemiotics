"""Refs #448/#449. Adversarial audit of Grammar #453 source-bound short frames.
Run: python source-binding-boundary.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Synthetic PCM only. Target selection is adversarial, not an error-rate estimate.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='2a074c64797b310423824902d092ffb54eacf5e7'
SYNC_BLOB='cc6b996d6314fdcbb92edc85e12878d5d2077aa7'
SEED=448037
CASES=(('clean',False,0,0),('label-only',True,0,0),('swap-1',True,1,0),('swap-2',True,2,0),('swap-3',True,3,0),('swap-erase3',True,0,3),('swap-2-erase1',True,2,1),('correct-label-3',False,3,0))

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def hits(book,obs):
    keep=[i for i,x in enumerate(obs) if x is not None]
    return np.flatnonzero(np.count_nonzero(book[:,keep]!=[obs[i] for i in keep],axis=1)<=2).tolist()

def run(root,out):
    assert blob(root/'discourse-sync.py')==SYNC_BLOB
    d=runpy.run_path(str(root/'discourse-sync.py'))
    for f,b in d['BLOBS'].items(): assert blob(root/f)==b,f
    c=runpy.run_path(str(root/'causal-frame.py'))
    m=runpy.run_path(str(root/'version-bound-payload.py'))
    joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']
    _,raw,names=m['build'](root); old,new=raw
    long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False)
    traces=[]; stats={}; specimens=[]; targets=[]
    for s in (0,1):
        for j,i in enumerate(rng.choice(len(old),8,replace=False)):
            i=int(i); a=books[s][13][i]; rival=books[1-s][13]
            distances=np.count_nonzero(rival!=a,axis=1); k=int(distances.argmin()); b=rival[k]
            delta=np.flatnonzero(a!=b).tolist(); assert len(delta)>=5
            # Select the first nearest target, then edit its mismatching positions in order.
            targets.append({'source':s,'row':i,'target_row':k,'distance':len(delta),'nearest_ties':int(np.count_nonzero(distances==len(delta))),'different_meaning':bool(names[i]!=names[k])})
            for case,swap,e,z in CASES:
                label=1-s if swap else s; obs=a.tolist()
                for pos in delta[:e]: obs[pos]=int(b[pos])
                for pos in delta[e:e+z]: obs[pos]=None
                lead=int(rng.integers(321,2500)) if case=='clean' else lead
                tokens=d['preamble'](label)+obs+[18,18]
                pcm=np.concatenate([np.zeros(lead,dtype='<i2'),c['pcm'](tokens,SEED,0).ravel(),np.zeros(4*d['SLOT'],dtype='<i2')])
                ev=d['acquire'](pcm,books,c['observe'],joint,True)
                decisions=[x for x in ev if x['kind'] in ('release','reject')]; assert len(decisions)==1,(case,ev)
                event=decisions[0]; assert event['source']==label and event['seen']==obs+[18,18]
                prefix=d['acquire'](pcm[:event['sample']],books,c['observe'],joint,True)
                assert prefix==[x for x in ev if x['sample']<=event['sample']]
                hs={v:hits(books[v][13],obs) for v in (0,1)}
                union=[(v,k0) for v in (0,1) for k0 in hs[v]]
                gated=(label,event['identity'][1]) if event['kind']=='release' else None
                assert gated==((label,hs[label][0]) if len(hs[label])==1 else None)
                free=union[0] if len(union)==1 else None
                strict=free if free is not None and free[0]==label else None
                outcomes={}
                for policy,got in [('label-gated',gated),('union',free),('union-agreement',strict)]:
                    outcome='withheld' if got is None else 'correct' if got==(s,i) else 'wrong'
                    stats.setdefault(case,{}).setdefault(policy,Counter())[outcome]+=1
                    outcomes[policy]={'decoded':got,'outcome':outcome,'meaning_changed':got is not None and names[got[1]]!=names[i]}
                row={'case':case,'origin':[s,i],'target':[1-s,k],'label':label,'distance':len(delta),'substitutions':delta[:e],'erasures':delta[e:e+z],'symbols':obs,'hits':hs,'events':ev,'outcomes':outcomes,'pcm_sha256':sha(pcm.tobytes()),'intended_meaning':names[i],'target_meaning':names[k]}
                traces.append(row)
                if j==0:
                    fn=f's{s}-{case}.wav'
                    with wave.open(str(out/fn),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                    with wave.open(str(out/fn),'rb') as w: assert sha(w.readframes(w.getnframes()))==row['pcm_sha256']
                    specimens.append({'file':fn,'case':case,'origin':row['origin'],'target':row['target'],'outcomes':outcomes,'pcm_sha256':row['pcm_sha256'],'peak':int(np.max(np.abs(pcm.astype(int))))})
    assert len(traces)==128
    assert all(r['outcomes']['label-gated']['outcome']=='correct' for r in traces if r['case']=='clean')
    assert all(r['outcomes']['label-gated']['outcome']=='withheld' for r in traces if r['case'] in ('label-only','swap-1','swap-2'))
    receipt={'schema':'mhac-source-binding-boundary-v1','grammar_pin':PIN,'blobs':{'discourse-sync.py':SYNC_BLOB,**d['BLOBS']},'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'origins':targets,'catalogue_rows_per_source':len(old),'observations':len(traces),'stats':stats,'specimens':specimens,'limits':'Short aligned fixed-clock frames; actual upstream acquisition with leading silence. Isolated preamble label swap plus targeted body edits, no overlap/drift/noise/authentication. Target search exhaustive per sampled origin, not full all-pairs census. Union policies use same acquired symbols and extra catalogue search; not compute matched. No human evidence.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}: intended {s["origin"]}; outcomes {s["outcomes"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Source-binding boundary</title><h1>Source-binding boundary</h1><p>Synthetic adversarial specimens. No autoplay. Start at low volume.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'origins':targets,'stats':stats},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
