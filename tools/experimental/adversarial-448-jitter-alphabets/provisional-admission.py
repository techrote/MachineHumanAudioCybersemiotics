"""Adversarial #448/#449. Run 063: provisional namespace admission.
OPENBLAS_NUM_THREADS=1 python provisional-admission.py RUN062_PACKAGE NEW_OUT
Exploratory synthetic PCM, AI-assisted; not human or physical evidence.
"""
import hashlib, inspect, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='6fe3ed738aec1941dda532a4a2bb0b8d3c0d09f3'
PIN='8a2d054e7dc4cfaf555fcd63b9d9930395293690'
SEED=4480630
MODES=('baseline','silence3','namespace1','radius2')
CASES=('clean','decoy2','decoy3','erase3','replace2','decoy-valid-prefix','weak-namespace','noise-only')

def reject(seen,mode):
    if len(seen)!=3 or mode=='baseline': return False
    if mode=='silence3': return all(x is None for x in seen)
    if mode=='namespace1': return not any(x in (0,16) for x in seen)
    # Exact necessary condition for either namespace at Hamming radius two.
    return min(sum(x is not None and x!=v for x in seen) for v in (0,16))>2

def run(root,out):
    def load(f): return runpy.run_path(str(root/f))
    h=load('gain-boundary.py'); stage=load('stage-gates.py'); d=load('decoder-budget.py')
    assert h['blob'](root/'interference-pressure.py')==PIN
    assert h['blob'](root/'stage-gates.py')=='670f3120ec8cea51c393b652b048dff53e86a77d'
    for f,b in {**h['PINS'],**load('window-holdout.py')['BLOBS']}.items(): assert h['blob'](root/f)==b,f
    src=inspect.getsource(d['run']).split("    g['SEED']=",1)[0]
    needle="    g['MODES']=MODES;"
    assert src.count(needle)==1
    src=src.replace(needle,'''    patch('observe(pcm[a:b],z,True,True)', 'observe(pcm[a:b],z,True,True,seen)')
    patch("                    if seen[-2:]==[18,18]:", "                    if reject(seen,gate):\\n                        h['done']=True; work['early_stops']+=1; h['exhausted']=gate!='radius2'; continue\\n                    if seen[-2:]==[18,18]:")
    '''+needle.strip())
    env=dict(d); receivers={}
    for gate in MODES:
        # Gate is a fixed receiver configuration, not ground truth.
        tmp=src.replace('env=dict(g,decode=decode)', 'env=dict(g,decode=decode,reject=reject,gate=gate)')
        ns=dict(env,reject=reject,gate=gate); exec(tmp+'    return g\n',ns)
        g=ns['run'](root,out,'fresh'); receivers[gate]=g['receive']
    ds=inspect.getsource(g['detect']); needle='scores[k]>=600 and scores[k]>=np.sqrt(np.mean(win**2))'; assert ds.count(needle)==1
    denv=dict(g); exec(ds.replace(needle,'scores[k]>=40 and scores[k]>=np.sqrt(np.mean(win**2))'),denv); detect=denv['detect']
    m=load('version-bound-payload.py'); v=load('interval-admission.py'); s=load('discourse-sync.py'); joint=load('prefix-disjoint.py')['joint']; S=g['S']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    for bylen in books.values():
        for n,book in bylen.items(): assert np.all(book[:,:3]==(0 if n==13 else 16))
    obs=lambda x,z,t,f,seen:stage['stage_observe'](x,z,seen,'all-hybrid')
    out.mkdir(parents=True,exist_ok=False); rows=[]; checks=0; specimens=[]
    def evaluate(pcm,want,ends,split,j,case,prior=None):
        nonlocal checks
        acq,det=detect(pcm); expected=Counter(map(tuple,want)); digest=h['sha'](pcm.tobytes())
        for mode,recv in receivers.items():
            ev,w=recv(pcm,acq,books,joint,obs,'prune1m')
            rel=[e for e in ev if e['kind']=='release']; got=Counter((e['source'],*e['identity']) for e in rel)
            strict=Counter((e['source'],*e['identity']) for e in rel if not(e['incomplete'] or e['decoder_incomplete'] or e['unadmitted']))
            correct=sum((expected&got).values()); strict_n=sum((expected&strict).values())
            row=dict(split=split,pair=j,case=case,mode=mode,expected=want,ends=ends,pcm_sha256=digest,correct=correct,strict=strict_n,wrong=sum(got.values())-correct,timely=sum(any([e['source'],*e['identity']]==a and e['sample']<=b+3200 for e in rel) for a,b in zip(want,ends)),work=w,events=ev)
            assert w.get('slots',0)<=66 and w.get('book_cells',0)<=1000000 and w.get('peak',0)<=4
            if prior is not None and mode=='baseline': assert digest==prior['pcm_sha256'] and ev==prior['events']
            rows.append(row)
            if j==0:
                for t in sorted({e['sample'] for e in ev}):
                    sub,_=detect(pcm[:t]); assert sub==[a for a in acq if a[0]<=t]
                    assert recv(pcm[:t],sub,books,joint,obs,'prune1m')[0]==[e for e in ev if e['sample']<=t]; checks+=1
    prior=[q for q in map(json.loads,(root/'pressure-out'/'traces.jsonl').read_text().splitlines()) if q['pair']==0 and q['mode']=='all-hybrid' and q['split']=='fresh']
    for q in prior:
        with wave.open(str(root/'pressure-out'/f"{q['case']}.wav"),'rb') as f: pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        evaluate(pcm,q['expected'],q['ends'],'retained',0,q['case'],q)
    rng=np.random.default_rng(SEED)
    for j in range(8):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=7*S+int(rng.integers(80)); off=lead+int(2.5*S)
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
        for ci,case in enumerate(CASES):
            aa=np.zeros(48*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); v['put'](bb,y,off)
            want=[[a,18,i],[b,13,k]]; ends=[lead+22*S,off+17*S]
            if case=='erase3': aa[lead+2*S:lead+5*S]=0
            if case=='replace2':
                aa[lead+2*S:lead+4*S]=0; v['put'](aa,[5,6],lead+2*S)
            if case=='weak-namespace': aa[lead+2*S:lead+5*S]//=30
            if case.startswith('decoy'):
                n=3 if case=='decoy3' else 2
                for di in range(n):
                    cc=np.zeros_like(aa); z=s['preamble']((a+di)%2)
                    if case=='decoy-valid-prefix': z=z+[0,0,0]
                    v['put'](cc,z,lead-(6-2*di)*S); aa+=cc
            mix=aa+bb
            if case=='noise-only': mix=np.random.default_rng(SEED*100+j).normal(0,100,len(aa)); want=[]; ends=[]
            assert abs(mix).max()<32767
            pcm=np.rint(mix).astype('<i2'); evaluate(pcm,want,ends,'fresh',j,case)
            if j==0:
                name=case+'.wav'
                with wave.open(str(out/name),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,pcm_sha256=h['sha'](pcm.tobytes())))
    summary={}
    for q in rows:
        for case in ('total',q['case']):
            summary.setdefault(q['split'],{}).setdefault(case,{}).setdefault(q['mode'],Counter()).update(expected=len(q['expected']),**{k:q[k] for k in ('correct','strict','wrong','timely')},**{k:q['work'].get(k,0) for k in ('slots','book_cells','early_stops')},refused=sum(e['kind']=='refused' for e in q['events']))
    # Exhaustive prefix-rule differential over the full symbol alphabet plus erasure.
    import itertools
    tests=0
    for p in itertools.product([None,*range(19)],repeat=3):
        assert reject(p,'radius2')==all(sum(x is not None and x!=v for x in p)>2 for v in (0,16)); tests+=1
    assert not reject([None]*3,'radius2') and reject([None]*3,'silence3')
    assert len({tuple(x) for q in rows if q['split']=='fresh' for x in q['expected']} & {tuple(x) for q in prior for x in q['expected']})==0
    (out/'traces.jsonl').write_text(''.join(json.dumps(q)+'\n' for q in rows))
    receipt=dict(parent=PARENT,parent_blob=PIN,seed=SEED,rows=len(rows),prefix_checks=checks,rule_checks=tests,summary=summary,specimens=specimens,limits='Heuristic early stops marked incomplete; exact radius2 rejects only impossible namespace prefixes, not all invalid messages. No human evidence; same local computational ceilings, not CPU parity.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
