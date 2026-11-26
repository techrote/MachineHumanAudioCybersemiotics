"""Refs #452 / Draft #453. Synthetic time-interleaved interval admission.
python interval-admission.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No human evidence, real device control, authentication or general overlap guarantee.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='7053f813bf770c1ec195e0c4485d24f483505045'
PARENT='af3f673f28e65bb4fc241a22cc603a6cbb041dfb'
S=1280; SEED=45237
CASES=('early-dual','late-dual','old-timeout','young-terminal-loss','ready-eviction','dual-capacity','sequential')
POLICIES=('keep-two','replace-two','exclusive','multiplex')

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def acquire(audio,books,observe,joint,policy):
    """Two hypotheses; retain completed candidates at capacity. Wait for known
    overlapping hypotheses, then either report conflict or release both. Only
    starts detected by decision time are considered; no EOF flush."""
    basis=np.exp(-2j*np.pi*np.array([2400,2600])[:,None]*np.arange(320)/16000)
    last=None; count=0; onset=0; prior=None; active=[]; events=[]
    def emit(kind,h,**kw):
        events.append(dict(kind=kind,sample=t,source=h['source'],body_start=h['start'],**kw))
    def overlaps(a,b):
        return b['start']-2*S < a['start']+len(a['seen'])*S
    def release(h):
        _,ready,identity=h['done']; emit('release',h,identity=identity,ready_sample=ready,wait_samples=t-ready)
    for t in range(320,len(audio)+1,80):
        win=audio[t-320:t].astype(float); scores=abs(basis@win)*2/320
        k=int(scores.argmax()); rms=np.sqrt(np.mean(win**2)); v=k if scores[k]>=600 and scores[k]>=rms else None
        if v!=last: last=v; count=0; onset=t-160
        count+=1
        if v is not None and count==4:
            if prior is not None and prior[0]!=v and abs(onset-prior[1]-S)<=160:
                h=dict(source=prior[0],start=prior[1]+2*S,seen=[],done=None); prior=None
                if len(active)==2:
                    if active[-1]['done'] is None: emit('evict',active.pop())
                    else: emit('overflow-ready-protected',h); h=None
                if h is not None: active.append(h); emit('start',h)
            else: prior=(v,onset)
        for h in active:
            if h['done'] is not None: continue
            start=h['start']; seen=h['seen']; s=h['source']
            while t>=start+(len(seen)+1)*S:
                a=start+len(seen)*S; seen.append(observe(audio[a:a+S]))
                if seen[-2:]==[18,18]:
                    body=seen[:-2]; n=len(body)
                    i=joint(books[s][n],body,2) if n in books[s] and 18 not in body else None
                    h['done']=('valid' if i is not None else 'reject',t,[n,i] if i is not None else None)
                    emit('candidate' if i is not None else 'reject',h,identity=h['done'][2],seen=seen[:]); break
                if len(seen)==22: h['done']=('timeout',t,None); emit('timeout',h); break
        while active and active[0]['done'] is not None:
            h=active[0]
            if h['done'][0]!='valid': active.pop(0); continue
            rival=active[1] if len(active)==2 and overlaps(h,active[1]) else None
            if rival is not None and rival['done'] is None: break
            active.pop(0)
            if rival is not None and rival['done'][0]=='valid':
                active.remove(rival)
                emit('overlap-conflict' if policy=='exclusive' else 'overlap-coadmission',h,
                     candidates=[dict(source=x['source'],identity=x['done'][2],start=x['start']-2*S,end=x['start']+len(x['seen'])*S,ready=x['done'][1]) for x in (h,rival)])
                if policy=='multiplex': release(h); release(rival)
            else: release(h)
        assert len(active)<=2 and all(len(h['seen'])<=22 for h in active)
    return events

def put(pcm,word,offset):
    # 40 ms on, 40 ms off; half-slot stagger yields disjoint active supports.
    n=np.arange(S//2); env=np.minimum(1,np.minimum(n/30,(len(n)-1-n)/30))
    for k,v in enumerate(word):
        if v is not None:
            start=offset+k*S; pcm[start:start+len(n)]+=np.rint(1500*env*np.sin(2*np.pi*(400+100*v)*n/16000+.137)).astype(np.int32)

def run(root,out):
    assert blob(root/'competing-starts.py')==PARENT
    p=runpy.run_path(str(root/'competing-starts.py')); s=runpy.run_path(str(root/'discourse-sync.py'))
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':PARENT}
    for f,b in pins.items(): assert blob(root/f)==b,f
    c=runpy.run_path(str(root/'causal-frame.py')); m=runpy.run_path(str(root/'version-bound-payload.py')); joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']
    _,raw,names=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False); traces=[]; specimens=[]; checks=0; stats={}
    for j in range(8):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old)))
        lead=S+int(rng.integers(0,80)); A=[a,18,i]; B=[b,13,k]
        for case in CASES:
            offset=int((7.5 if case=='late-dual' else 23.5 if case=='sequential' else 2.5)*S)
            x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
            want=[A,B]
            if case in ('old-timeout','ready-eviction'): x[-2:]=[None,None]; want=[B]
            if case=='young-terminal-loss': y[-2:]=[None,None]; want=[A]
            pcm=np.zeros(55*S,dtype=np.int32); put(pcm,x,lead); put(pcm,y,lead+offset)
            if case in ('ready-eviction','dual-capacity'): put(pcm,s['preamble'](a),lead+int(19.5*S))
            assert np.max(np.abs(pcm))<=1500; pcm=pcm.astype('<i2'); digest=sha(pcm.tobytes())
            for policy in POLICIES:
                f=p['acquire'] if policy in ('keep-two','replace-two') else acquire
                ev=f(pcm,books,c['observe'],joint,policy); releases=[e for e in ev if e['kind']=='release']; got=[[e['source'],*e['identity']] for e in releases]
                for e in ev:
                    if e['kind'] in ('release','overlap-conflict','overlap-coadmission'):
                        assert f(pcm[:e['sample']],books,c['observe'],joint,policy)==[v for v in ev if v['sample']<=e['sample']]; checks+=1
                correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values())
                row=dict(case=case,pair=j,policy=policy,pcm_sha256=digest,expected=want,decoded=got,correct=correct,wrong=len(got)-correct,missing=len(want)-correct,events=ev)
                traces.append(row); q=stats.setdefault(case+':'+policy,Counter()); q.update(correct=correct,wrong=row['wrong'],missing=row['missing'],conflicts=sum(e['kind']=='overlap-conflict' for e in ev),coadmissions=sum(e['kind']=='overlap-coadmission' for e in ev),ready_protected=sum(e['kind']=='overflow-ready-protected' for e in ev)); q['max_wait_samples']=max([q['max_wait_samples']]+[e['wait_samples'] for e in releases])
            if j==0:
                fn=case+'.wav'
                with wave.open(str(out/fn),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=fn,pcm_sha256=digest,expected=want,meanings=[names[z[2]%len(old)] for z in want]))
    # Known-answer contract checks: generated ground truth, not receiver labels.
    for row in traces:
        case,policy=row['case'],row['policy']; dual=case in ('early-dual','late-dual','dual-capacity')
        expected=len(row['expected'])
        if dual and policy in ('keep-two','replace-two'): expected=1
        if dual and policy=='exclusive': expected=0
        if case=='ready-eviction' and policy=='replace-two': expected=0
        assert row['correct']==expected and row['wrong']==0, row
        assert sum(e['kind']=='overlap-conflict' for e in row['events'])==int(dual and policy=='exclusive')
        assert sum(e['kind']=='overlap-coadmission' for e in row['events'])==int(dual and policy=='multiplex')
    receipt=dict(schema='mhac-interval-admission-v1',pin=PIN,blobs=pins,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),physical_pcm=len(CASES)*8,observations=len(traces),prefix_checks=checks,stats=stats,specimens=specimens,limits='Constructed half-slot stagger, disjoint active tone supports despite overlapping frame intervals. Exclusive and multiplex are different application contracts, not authentication. Known detected starts only, fixed slot clock, capacity two, unbounded PCM and trace retention, no human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<h2>{v["file"]}</h2><p>Expected {v["expected"]}; meanings {v["meanings"]}</p><audio controls preload="none" src="{v["file"]}"></audio><pre>'+json.dumps({r['policy']:dict(decoded=r['decoded'],events=[e for e in r['events'] if e['kind'] in ('overlap-conflict','overlap-coadmission','overflow-ready-protected','release')]) for r in traces if r['pair']==0 and r['case']+'.wav'==v['file']},indent=2)+'</pre>' for v in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Interval admission</title><h1>Interval admission</h1><p>Synthetic time-interleaved tones. Begin at low volume. Exclusive means withhold overlapping valid messages; multiplex allows both. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
