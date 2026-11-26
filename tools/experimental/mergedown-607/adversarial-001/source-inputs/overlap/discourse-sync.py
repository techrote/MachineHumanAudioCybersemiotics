"""Refs #452 / #453. Sequential source-labelled acoustic discourse, synthetic only.
Usage: python discourse-sync.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No physical devices, human evidence, or authentication. Fixed nominal clock.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='80e65d26ab3e209fb0bf345a2ee9fc67fa743a8a'
BLOBS={'causal-frame.py':'fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60','prefix-disjoint.py':'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','frame-length-commit.py':'1538e258e53b62fc62315ca11eb9ba34496c5919','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493'}
SEED=45235
SLOT=1280
HOP=80
CASES=('clean','cut','lost-end','lost-start','swapped-label','interior-drop','noise','spoof','false-start')
POLICIES=('locked','restart','bound-restart')

def sha(b): return hashlib.sha256(b).hexdigest()
def preamble(s): return [20,22] if s==0 else [22,20]

def acquire(audio,books,observe,joint,restart):
    # Fixed 20ms analysis window, 5ms hop. Access only samples already arrived.
    basis=np.exp(-2j*np.pi*np.array([2400,2600])[:,None]*np.arange(320)/16000)
    last=None; count=0; onset=0; prior=None; active=None; events=[]
    for t in range(320,len(audio)+1,HOP):
        win=audio[t-320:t].astype(float); scores=abs(basis@win)*2/320
        k=int(scores.argmax()); rms=np.sqrt(np.mean(win**2))
        v=k if scores[k]>=600 and scores[k]>=rms else None
        if v!=last: last=v; count=0; onset=t-160
        count+=1
        if v is not None and count==4:
            if prior is not None and prior[0]!=v and abs(onset-prior[1]-SLOT)<=160:
                source=prior[0]; start=prior[1]+2*SLOT
                if active is None or restart:
                    events.append({'kind':'restart' if active else 'start','sample':t,'source':source,'body_start':start})
                    active=[source,start,[]]
                else: events.append({'kind':'ignored-start','sample':t,'source':source})
                prior=None
            else: prior=(v,onset)
        if active is None: continue
        source,start,seen=active
        while t>=start+(len(seen)+1)*SLOT:
            a=start+len(seen)*SLOT; seen.append(observe(audio[a:a+SLOT]))
            if seen[-2:]==[18,18]:
                body=seen[:-2]; n=len(body); i=None
                if n in books[source] and 18 not in body: i=joint(books[source][n],body,2)
                events.append({'kind':'release' if i is not None else 'reject','sample':t,'source':source,'identity':[n,i] if i is not None else None,'seen':seen})
                active=None; break
            if len(seen)==22:
                events.append({'kind':'timeout','sample':t,'source':source}); active=None; break
    return events

def run(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    c=runpy.run_path(str(root/'causal-frame.py')); m=runpy.run_path(str(root/'version-bound-payload.py'))
    joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']; _,raw,names=m['build'](root); old,new=raw
    long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    def book(s):
        return {13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))}
    unbound={0:book(0),1:book(0)}; bound={0:unbound[0],1:book(1)}
    rng=np.random.default_rng(SEED); pairs=[]
    for j in range(12):
        pairs.append([(13 if j%2 else 18,int(rng.integers(len(old)))),(18 if j%2 else 13,int(rng.integers(len(long) if j%2 else len(old))))])
    out.mkdir(parents=True,exist_ok=False); traces=[]; stats={}; specimens=[]
    for case in CASES:
        for j,pair in enumerate(pairs):
            order=[j%2,1-j%2]; lead=int(rng.integers(321,2500)); gap=int(rng.integers(0,240)); seed=SEED+100*CASES.index(case)+j
            expected=[[s,*p] for s,p in zip(order,pair)]
            for policy in POLICIES:
                books=bound if policy=='bound-restart' else unbound; words=[]
                for k,(s,(n,i)) in enumerate(zip(order,pair)):
                    label=1-s if k==1 and case in ('swapped-label','spoof') else s
                    body_source=label if k==1 and case=='spoof' else s
                    w=preamble(label)+books[body_source][n][i].tolist()+[18,18]
                    if k==0 and case=='cut': w=w[:8]
                    if k==0 and case=='false-start': w[8:10]=preamble(1-s)
                    if k==0 and case=='lost-end': w[-2:]=[None,None]
                    if k==1 and case=='lost-start': w[:2]=[None,None]
                    if k==1 and case=='interior-drop': w[8:10]=[None,None]
                    words.append(w)
                a=np.concatenate([np.zeros(lead,dtype='<i2'),c['pcm'](words[0],seed,0).ravel(),np.zeros(gap,dtype='<i2'),c['pcm'](words[1],seed,0).ravel(),np.zeros(4*SLOT,dtype='<i2')])
                if case=='noise': a=np.clip(np.rint(a.astype(float)+np.random.default_rng(seed).normal(0,100,len(a))),-2048,2048).astype('<i2')
                ev=acquire(a,books,c['observe'],joint,policy!='locked'); releases=[e for e in ev if e['kind']=='release']; got=[[e['source'],*e['identity']] for e in releases]
                want=expected[1:] if case in ('cut','lost-end') else expected
                assert len(got)==len(set(map(tuple,got)))
                correct=sum(x in want for x in got); wrong=len(got)-correct; missing=len(want)-correct
                key=f'{case}:{policy}'; stats.setdefault(key,Counter()).update(correct=correct,wrong=wrong,missing=missing)
                # Prefix invariance: no future samples needed for any release.
                for e in releases:
                    assert acquire(a[:e['sample']],books,c['observe'],joint,policy!='locked')==[x for x in ev if x['sample']<=e['sample']]
                row={'case':case,'policy':policy,'pair':j,'seed':seed,'lead_samples':lead,'gap_samples':gap,'frame_starts':[lead,lead+len(words[0])*SLOT+gap],'expected':want,'decoded':got,'expected_meanings':[names[i if n==13 or i<len(old) else i-len(old)] for s,n,i in want],'decoded_meanings':[names[i if n==13 or i<len(old) else i-len(old)] for s,n,i in got],'events':ev,'correct':correct,'wrong':wrong,'missing':missing,'pcm_sha256':sha(a.tobytes())}; traces.append(row)
                if j==0 and case in ('clean','cut','swapped-label','spoof','false-start'):
                    f=f'{case}-{policy}.wav'
                    with wave.open(str(out/f),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(a.tobytes())
                    specimens.append({'file':f,'expected':want,'decoded':got,'expected_meanings':row['expected_meanings'],'decoded_meanings':row['decoded_meanings'],'pcm_sha256':row['pcm_sha256']})
    assert len(traces)==324
    for case in CASES:
        for j in range(12):
            x=[r for r in traces if r['case']==case and r['pair']==j]; assert x[0]['pcm_sha256']==x[1]['pcm_sha256']
    receipt={'schema':'mhac-discourse-sync-v1','pin':PIN,'blobs':BLOBS,'seed':SEED,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'stats':stats,'observations':len(traces),'specimens':specimens,'limits':'Sequential nonoverlapping senders, fixed 80ms clock, 160ms labelled preamble, explicit terminal, offline causal-prefix analysis, radius two, no authentication, no drift, no human evidence. Bound policy changes payload tones; same nominal duration/amplitude, not measured energy matching.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}: expected {s["expected"]} {s["expected_meanings"]}; decoded {s["decoded"]} {s["decoded_meanings"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Discourse synchronization</title><h1>Discourse synchronization</h1><p>Synthetic only. Start at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(stats,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
