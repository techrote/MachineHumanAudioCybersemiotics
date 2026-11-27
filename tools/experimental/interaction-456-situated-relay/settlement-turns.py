"""Interaction #456 / Draft #457. Synthetic acoustic settlement; no real devices.
python settlement-turns.py grammar NEW_OUTPUT
Pinned Grammar collision: 36eab4b0abf5e17c25f99a5d27b9bf0edba99e34, concurrent-association.py.
One AI worker; public fixture key, aligned frames, stipulated roles and roster.
"""
import hashlib, hmac, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PARENT='964c5060d9a86eba548488a06c959add0a121b89'
PIN='36eab4b0abf5e17c25f99a5d27b9bf0edba99e34'
KEY=b'MHAC PUBLIC SYNTHETIC TEST KEY 047'
CASES=('clean','reverse','duplicate','lost-close','retry-close','late-conflict','early-close','alternate','collision','collision-missing-tag','collision-late-body','collision-late-unwitnessed')
POLICIES=('eager','closed','undo-24','undo-96')
DEADLINES=((85,110),(120,150))
sha=lambda b:hashlib.sha256(b).hexdigest()

def capture(a,c,books,seed,case):
    rng=np.random.default_rng(seed);events=[];audio=[];now=0
    book=books[0][18];ctx=c['digest'](0,18,book).digest();epoch=8 if case.startswith('collision') else seed%289
    hdr=[c['digits'](epoch,2)+c['digits'](i,2)+[15] for i in range(2)]
    targets=[65931,14976] if case.startswith('collision') else list(map(int,rng.choice(len(book),2,False)))
    def body(i,n):return hdr[i]+c['digits'](n,5)
    def tag(w):return c['digits'](int.from_bytes(hmac.digest(KEY,b'MHAC-048-recipient\0'+bytes([1])+ctx+bytes(w),'sha256'),'big')%17**8,8)
    bs=[body(i,(n+1)%len(book) if case=='alternate' and i==1 else n) for i,n in enumerate(targets)];ts=list(map(tag,bs));close=c['digits'](epoch,2)+[2,16,14]
    if case.startswith('collision'):assert ts[0]==ts[1]==[5,8,14,12,7,4,1,1]
    def emit(role,w,origin=None,lost=False):
        nonlocal now
        obs,x,tr=a['exchange'](c['encode'](w),0,seed*100+len(events),-1 if lost else None);got=c['decode'](obs) if obs is not None else None
        assert got==(None if lost else w);now+=tr['slots'];events.append(dict(t=now,role=role,word=got,origin=origin,wire=tr));audio.append(x.ravel())
    for h in hdr:emit('query',h)
    emit('body',bs[0]);
    if case not in ('collision-late-body','collision-late-unwitnessed'):emit('body',bs[1])
    for i in ([1,0] if case=='reverse' else [1] if case in ('collision-missing-tag','collision-late-unwitnessed') else [0] if case=='collision-late-body' else [0,1]):emit('tag',ts[i],i)
    if case=='duplicate':emit('tag',ts[0],0)
    if case=='late-conflict':emit('body',body(0,(targets[0]+1)%len(book)))
    emit('close',close,lost=case in ('lost-close','retry-close'))
    if case=='retry-close':emit('close',close)
    if case=='early-close':
        now+=20;audio.append(np.zeros(20*1280,dtype='<i2'));emit('body',body(0,(targets[0]+1)%len(book)))
    if case in ('collision-late-body','collision-late-unwitnessed'):emit('body',bs[1]);emit('tag',ts[1],1)
    return dict(seed=seed,case=case,headers=hdr,targets=targets,context=ctx.hex(),close=close,events=events),np.concatenate(audio)

def replay(row,policy,deadlines):
    headers=list(map(tuple,row['headers']));ctx=bytes.fromhex(row['context']);bodies=[set(),set()];tags=set();origins=[set(),set()];actions={};log=[];closed=False;revoked=set();invalid=set();retention=int(policy.split('-')[1]) if policy.startswith('undo') else 0
    def tag(w):return tuple(int.from_bytes(hmac.digest(KEY,b'MHAC-048-recipient\0'+bytes([1])+ctx+bytes(w),'sha256'),'big')//17**j%17 for j in range(8))
    for e in row['events']:
        t=e['t'];w=e['word'];role=e['role']
        if w is not None:
            w=tuple(w)
            if role=='body' and w[:5] in headers:bodies[headers.index(w[:5])].add(w)
            if role=='tag':tags.add(w);origins[e['origin']].add(w) # origin is offline evidence ONLY
            if role=='close' and w==tuple(row['close']):closed=True
        good={i:next(iter(v)) for i,v in enumerate(bodies) if len(v)==1}
        # Include *all* observed bodies in ambiguity checks, even conflicting ones.
        edges={z:[i for i,v in enumerate(bodies) if any(tag(b)==z for b in v)] for z in tags}
        valid={i:b for i,b in good.items() if edges.get(tag(b))==[i]}
        log.append(dict(t=t,event=role,closed=closed,body_counts=list(map(len,bodies)),valid=sorted(valid)))
        for i,act in actions.items():
            if i in revoked:continue
            if i not in valid or valid[i]!=act['body']:
                invalid.add(i)
                if retention and t-act['t']<=retention:revoked.add(i);log.append(dict(t=t,event='rollback',agent=i))
        if policy=='closed' and (not closed or not all(bodies)):continue
        for i,b in sorted(valid.items()):
            if i not in actions and t<=deadlines[i]:
                actions[i]=dict(t=t,body=b,witnessed=tag(b) in origins[i]);log.append(dict(t=t,event='action',agent=i,identity=sum(v*17**j for j,v in enumerate(b[5:]))))
    outcomes=[]
    for i,target in enumerate(row['targets']):
        a=actions.get(i);chosen=None if a is None else sum(v*17**j for j,v in enumerate(a['body'][5:]));status='abstain' if a is None else 'rolled-back' if i in revoked else 'correct' if chosen==target else 'wrong'
        if a:assert a['t']<=deadlines[i]
        outcomes.append(dict(agent=i,target=target,chosen=chosen,status=status,admitted_at=None if a is None else a['t'],unwitnessed=a is not None and not a['witnessed'],invalidated=i in invalid,invalid_remaining=i in invalid and i not in revoked))
    return dict(seed=row['seed'],case=row['case'],policy=policy,deadlines=deadlines,outcomes=outcomes,log=log)

def run(root,out):
    here=pathlib.Path(__file__).parent
    for f,h in [('acoustic-turns.py','d14f133f592f6b9ea97ca8bce18d28eede9eb65dd9958029b1ee40edfefb9e6d'),('catalogue-turns.py','a407e139a74ad49befe7cc0554c293bdc1e5f22d575fb84a930d3986057bc45b')]:assert sha((here/f).read_bytes())==h
    a,books=runpy.run_path(str(here/'acoustic-turns.py'))['load'](root);c=runpy.run_path(str(here/'catalogue-turns.py'));out.mkdir();bank=[];rows=[];stats={};spec=[]
    for seed,case in itertools.product(range(4564900,4564904),CASES):
        b,pcm=capture(a,c,books,seed,case);bank.append(b)
        if seed==4564900 and case in ('clean','retry-close','early-close','collision-late-body'):
            name=case+'.wav'
            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
            spec.append(dict(file=name,peak=int(np.abs(pcm.astype('int32')).max()),pcm_sha256=sha(pcm.tobytes())))
        for p,d in itertools.product(POLICIES,DEADLINES):
            x=replay(b,p,d);assert x==replay(b,p,d);rows.append(x);s=stats.setdefault(f'{case}:{d[0]}:{p}',Counter())
            for o in x['outcomes']:s[o['status']]+=1;s.update(k for k in ('unwitnessed','invalidated','invalid_remaining') if o[k])
    assert stats['collision:120:eager']['abstain']==8
    assert stats['collision-late-body:120:eager']['invalid_remaining']==4
    assert stats['collision-late-body:120:undo-96']['rolled-back']==4
    assert stats['collision-late-unwitnessed:120:eager']['unwitnessed']==4
    assert stats['collision-late-unwitnessed:120:undo-96']['rolled-back']==4
    assert stats['lost-close:120:closed']['abstain']==8
    assert stats['retry-close:120:closed']['correct']==8
    assert stats['alternate:120:closed']['wrong']==4
    receipt=dict(parent=PARENT,grammar_reference=PIN,source_sha256=sha(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,captures=len(bank),frames=sum(len(b['events']) for b in bank),replays=len(rows),stats=stats,specimens=spec,limits='Aligned PCM, externally known frame roles, shared roster, public key, local unauthenticated closure, no turnaround allowance. Undo is simulated compensation, not prevention; historical exposure is retained. Rollback horizon, not bounded memory; all evidence stays in RAM. Collision witness reused, not an estimated collision rate. No human evidence.')
    for name,data in [('bank',bank),('traces',rows)]: (out/(name+'.jsonl')).write_text(''.join(json.dumps(x)+'\n' for x in data))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    examples=[x for x in rows if x['seed']==4564900]
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Settlement turns</title><h1>Settlement turns</h1><p>Fictional world only. Lower system volume first. No autoplay.</p><label>Scenario <select id="case"></select></label><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="state"></pre>'''+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="bank.jsonl">Evidence</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const s=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.case,r.policy,r.deadlines].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#state').textContent=JSON.stringify(r.outcomes,null,2);document.querySelector('#event').textContent=JSON.stringify(r.log[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].log.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
