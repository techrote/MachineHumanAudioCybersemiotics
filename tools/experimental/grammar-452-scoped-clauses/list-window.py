"""Refs #452 / Draft #453. List-valued observations in overlapping discourse.
Run: python list-window.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Synthetic finite experiment; no authentication, physical or human evidence.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='68232af33ab7b5666ab6a89d84a5e24d3532c973'
ADVERSARIAL='e2cbc57d92a6af386b8745a3891b3cc7d818ef70'
WINDOW_BLOB='83eafc7eae1fd9ff8961bb510af22afa4eb4a0fb'
SEED=452390; S=1280
# Fixed exploratory conditions: phase ms, gain B/A, noise SD counts, onset-only drift ppm.
CASES=[(0,1,0,0),(-30,1,0,0),(30,1,0,0),(-35,1,0,0),(35,1,0,0),(-30,.6,250,0),(30,1.7,250,0),(0,.6,400,0),(0,1.7,400,0),(-20,1,200,10000),(20,1,200,-10000),(-35,1,200,5000),(35,1,200,-5000)]
MODES=('hard25','list-exact','list-radius2')

def observer(mode):
    # Same 400 samples and bank for each policy; retain at most two body tones.
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(400)/16000)
    def observe(slot):
        scores=abs(basis@slot[80:480])*2/400; order=np.argsort(-scores,kind='stable'); k,j=map(int,order[:2])
        if scores[k]<200: return None
        if k==17: return 18
        if mode=='hard25': return k
        return [k,j] if j!=17 and scores[j]>=max(200,.45*scores[k]) else [k]
    return observe

def list_joint(book,obs,radius):
    misses=np.zeros(len(book),np.int16)
    for i,values in enumerate(obs):
        if values is not None:
            misses+=~np.isin(book[:,i],values)
    hits=np.flatnonzero(misses<=radius)
    return int(hits[0]) if len(hits)==1 else None

def run(root,out):
    load=lambda f:runpy.run_path(str(root/f))
    m=load('interval-admission.py'); p=load('competing-starts.py'); s=load('discourse-sync.py'); w=load('window-admission.py')
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':w['BLOB'],'window-admission.py':WINDOW_BLOB}
    for f,h in pins.items(): assert m['blob'](root/f)==h,f
    v=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']; _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](word,i,'polynomial') for i,word in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    # Known-answer checks: ambiguity never silently resolves, even at exact radius.
    small=np.array([[0,1],[1,1],[2,2]])
    assert list_joint(small,[[0,1],[1]],0) is None
    assert list_joint(small,[[0],[1,2]],0)==0
    assert list_joint(small,[[2],[1]],0) is None
    obs={k:observer(k) for k in MODES}; dec={'hard25':joint,'list-exact':lambda b,o,r:list_joint(b,o,0),'list-radius2':list_joint}
    out.mkdir(parents=True,exist_ok=False); rows=[]; stats={}; specimens=[]; checks=0; rng=np.random.default_rng(SEED)
    for pair in range(6):
        a=pair%2; b=1-a; i=int(rng.integers(len(long))); j=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,j]]
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][j].tolist()+[18,18]
        for ci,(phase,gain,noise,ppm) in enumerate(CASES):
            aa=np.zeros(32*S,np.int32); bb=aa.copy(); m['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16
            for q,tok in enumerate(y): m['put'](bb,[tok],offset+round(q*S*(1+ppm/1e6)))
            ns=SEED*10000+pair*100+ci; mix=aa+gain*bb+np.random.default_rng(ns).normal(0,noise,len(aa)); assert abs(mix).max()<7000
            pcm=np.rint(mix).astype('<i2'); digest=m['sha'](pcm.tobytes())
            for mode in MODES:
                ev=m['acquire'](pcm,books,obs[mode],dec[mode],'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); wrong=len(got)-correct
                for e in ev:
                    if pair==0 and e['kind']=='release':
                        t=e['sample']; assert m['acquire'](pcm[:t],books,obs[mode],dec[mode],'multiplex')==[z for z in ev if z['sample']<=t]; checks+=1
                rows.append(dict(pair=pair,condition=ci,mode=mode,noise_seed=ns,expected=want,decoded=got,correct=correct,wrong=wrong,missing=2-correct,pcm_sha256=digest,events=ev))
                stats.setdefault(str(ci),{}).setdefault(mode,Counter()).update(correct=correct,wrong=wrong,missing=2-correct,starts=sum(e['kind']=='start' for e in ev))
            if pair==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    for k in {(r['pair'],r['condition']) for r in rows}: assert len({r['pcm_sha256'] for r in rows if (r['pair'],r['condition'])==k})==1
    totals={k:{v:sum(r[v] for r in rows if r['mode']==k) for v in ('correct','wrong','missing')} for k in MODES}
    receipt=dict(schema='mhac-list-window-v1',pin=PIN,adversarial_design_ref=ADVERSARIAL,blobs=pins,source_sha256=m['sha'](pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,conditions=CASES,condition_fields=['phase_ms','gain_B_over_A','noise_sd_counts','B_onset_drift_ppm'],modes=MODES,physical_pcm=6*len(CASES),evaluations=len(rows),prefix_checks=checks,stats=stats,totals=totals,specimens=specimens,limits='Exploratory fixed conditions, no independent holdout claim. Same PCM, preamble detector, terminal winner and 400-sample window; list secondary threshold .45, absolute threshold 200. Exact list means zero mismatches among retained non-erased slots; radius2 permits two. Unique codeword only, no guarantee of origin. Onset-only drift, no pitch shift. No bounded streaming memory, human or physical evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>List window</title><h1>Overlapping discourse: list observations</h1><p>Synthetic only. Opt-in audio, start at low volume. Same capture across policies.</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {CASES[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(ci)],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:m['sha'](p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(totals))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
