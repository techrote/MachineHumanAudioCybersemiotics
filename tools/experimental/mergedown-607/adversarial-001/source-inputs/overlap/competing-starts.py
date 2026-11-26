"""Refs #452 / Draft #453. Synthetic competing-start admission, not authentication.
Run: python competing-starts.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Uses NumPy; fixed clock, sequential PCM, no human evidence or device control.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='2a074c64797b310423824902d092ffb54eacf5e7'
SYNC_BLOB='cc6b996d6314fdcbb92edc85e12878d5d2077aa7'
SEED=45236
SLOT=1280
HOP=80
POLICIES=('locked','restart','keep-two','replace-two')
CASES=('clean','cut','lost-end','false-start','cut-false-start','cut-two-false-starts','early-cut','noise')

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def acquire(audio,books,observe,joint,policy):
    """Causal bounded hypotheses. Oldest valid frame wins overlapping intervals.
    A completed younger frame is held until older hypotheses resolve. At capacity,
    keep-two ignores the incoming start; replace-two evicts the youngest.
    No flush at EOF. The returned diagnostic trace is intentionally unbounded.
    """
    basis=np.exp(-2j*np.pi*np.array([2400,2600])[:,None]*np.arange(320)/16000)
    last=None; count=0; onset=0; prior=None; active=[]; events=[]
    cap=1 if policy in ('locked','restart') else 2
    def emit(kind,h,**kw):
        events.append(dict(kind=kind,sample=t,source=h['source'],body_start=h['start'],**kw))
    for t in range(320,len(audio)+1,HOP):
        win=audio[t-320:t].astype(float); scores=abs(basis@win)*2/320
        k=int(scores.argmax()); rms=np.sqrt(np.mean(win**2))
        v=k if scores[k]>=600 and scores[k]>=rms else None
        if v!=last: last=v; count=0; onset=t-160
        count+=1
        if v is not None and count==4:
            if prior is not None and prior[0]!=v and abs(onset-prior[1]-SLOT)<=160:
                h=dict(source=prior[0],start=prior[1]+2*SLOT,seen=[],done=None)
                prior=None
                if len(active)==cap:
                    if policy in ('restart','replace-two'):
                        emit('evict',active.pop())
                    else:
                        emit('ignore',h); h=None
                if h is not None:
                    active.append(h); emit('start',h)
            else: prior=(v,onset)
        # Completed younger candidates remain in the bounded queue.
        for h in active:
            if h['done'] is not None: continue
            start=h['start']; seen=h['seen']; s=h['source']
            while t>=start+(len(seen)+1)*SLOT:
                a=start+len(seen)*SLOT; seen.append(observe(audio[a:a+SLOT]))
                if seen[-2:]==[18,18]:
                    body=seen[:-2]; n=len(body)
                    i=joint(books[s][n],body,2) if n in books[s] and 18 not in body else None
                    h['done']=('valid' if i is not None else 'reject',t,[n,i] if i is not None else None)
                    emit('candidate' if i is not None else 'reject',h,identity=h['done'][2],seen=seen[:]); break
                if len(seen)==22:
                    h['done']=('timeout',t,None); emit('timeout',h); break
        while active and active[0]['done'] is not None:
            h=active.pop(0); status,ready,identity=h['done']
            if status!='valid': continue
            emit('release',h,identity=identity,ready_sample=ready,wait_samples=t-ready)
            end=h['start']+len(h['seen'])*SLOT
            # A later preamble starting inside a released frame cannot also own those samples.
            for rival in active[:]:
                if rival['start']-2*SLOT<end:
                    emit('suppress-overlap',rival); active.remove(rival)
        assert len(active)<=cap and all(len(h['seen'])<=22 for h in active)
    return events

def run(root,out):
    assert blob(root/'discourse-sync.py')==SYNC_BLOB
    sync=runpy.run_path(str(root/'discourse-sync.py'))
    for f,b in sync['BLOBS'].items(): assert blob(root/f)==b,f
    c=runpy.run_path(str(root/'causal-frame.py')); m=runpy.run_path(str(root/'version-bound-payload.py'))
    joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']; _,raw,names=m['build'](root); old,new=raw
    long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False)
    stats={}; traces=[]; specimens=[]; prefix_checks=0; baseline_checks=0
    def render(w,seed): return c['pcm'](w,seed,0).ravel()
    def ident(e): return [e['source'],*e['identity']]
    for j in range(8):
        s=j%2; n=13 if j%2 else 18; n2=31-n
        i=int(rng.integers(len(books[s][n]))); i2=int(rng.integers(len(books[1-s][n2])))
        first=sync['preamble'](s)+books[s][n][i].tolist()+[18,18]
        second=sync['preamble'](1-s)+books[1-s][n2][i2].tolist()+[18,18]
        for k,case in enumerate(CASES):
            seed=SEED+100*j+k; a=first[:]; want=[[s,n,i],[1-s,n2,i2]]
            if case.startswith('cut'):
                a=a[:8]; want=want[1:]
                if case!='cut': a[4:6]=sync['preamble'](1-s)
                if case=='cut-two-false-starts': a[6:8]=sync['preamble'](s)
            if case=='early-cut': a=a[:3]; want=want[1:]
            if case=='lost-end': a[-2:]=[None,None]; want=want[1:]
            if case=='false-start': a[8:10]=sync['preamble'](1-s)
            lead=int(rng.integers(321,2500)); gap=int(rng.integers(0,240))
            if case=='early-cut': gap=640
            pcm=np.concatenate([np.zeros(lead,dtype='<i2'),render(a,seed),np.zeros(gap,dtype='<i2'),render(second,seed),np.zeros(24*SLOT,dtype='<i2')])
            if case=='noise': pcm=np.clip(np.rint(pcm.astype(float)+np.random.default_rng(seed).normal(0,100,len(pcm))),-2048,2048).astype('<i2')
            filename=f'{case}.wav'
            if j==0:
                with wave.open(str(out/filename),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=filename,pcm_sha256=sha(pcm.tobytes()),expected=want))
            for policy in POLICIES:
                ev=acquire(pcm,books,c['observe'],joint,policy); rel=[e for e in ev if e['kind']=='release']; got=list(map(ident,rel))
                if policy in ('locked','restart'):
                    original=sync['acquire'](pcm,books,c['observe'],joint,policy=='restart')
                    assert [(e['sample'],ident(e)) for e in original if e['kind']=='release']==[(e['sample'],ident(e)) for e in rel]
                    baseline_checks+=1
                for e in rel:
                    assert acquire(pcm[:e['sample']],books,c['observe'],joint,policy)==[x for x in ev if x['sample']<=e['sample']]
                    prefix_checks+=1
                correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); wrong=len(got)-correct; missing=len(want)-correct
                counts=stats.setdefault(case+':'+policy,Counter()); counts.update(correct=correct,wrong=wrong,missing=missing,wait_samples=sum(e['wait_samples'] for e in rel),ignored=sum(e['kind']=='ignore' for e in ev),evicted=sum(e['kind']=='evict' for e in ev))
                counts['max_wait_samples']=max([counts['max_wait_samples']]+[e['wait_samples'] for e in rel])
                traces.append(dict(case=case,pair=j,seed=seed,policy=policy,pcm_sha256=sha(pcm.tobytes()),expected=want,decoded=got,correct=correct,wrong=wrong,missing=missing,events=ev))
    assert len(traces)==len(CASES)*8*len(POLICIES)
    receipt=dict(schema='mhac-competing-starts-v1',pin=PIN,blobs={**sync['BLOBS'],'discourse-sync.py':SYNC_BLOB},seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),observations=len(traces),physical_pcm=len(CASES)*8,prefix_checks=prefix_checks,baseline_checks=baseline_checks,stats=stats,specimens=specimens,limits='Fixed aligned symbol clock after acquisition; sequential PCM; capacity two; oldest-first overlap priority, not joint ambiguity consensus; no EOF flush; no authentication, human evidence, real-time or bounded input-storage claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<h2>{s["file"]}</h2><p>Expected {s["expected"]}</p><audio controls preload="none" src="{s["file"]}"></audio><pre>'+json.dumps({r['policy']:r['decoded'] for r in traces if r['pair']==0 and r['case']+'.wav'==s['file']},indent=2)+'</pre>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Competing starts</title><h1>Competing starts</h1><p>Synthetic PCM. Start at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
