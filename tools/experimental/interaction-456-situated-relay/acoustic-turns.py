"""Interaction #456 / #457, synthetic only. Python + NumPy.
python acoustic-turns.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Two ordered clarification obligations on one serialized channel. Uses exact
Grammar framed PCM functions; scheduling, deadlines and prior nonce ledger
are local models. No blind acquisition, authenticated identity, real devices,
human evidence or durable anti-replay state. One slot = 80 ms.
"""
import hashlib, json, pathlib, runpy, sys, wave, itertools
from collections import Counter
import numpy as np
PIN='feba52809552355db1beb33a36dd7fdd619b2e0f'
PARENT='e0218598dbb32e84dbaff1f32b5af3d0035c7367'
BLOBS={'acoustic-clarification.py':'71e527852c278fb91088ed9fdcf5d7d6027426a3','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1'}
POLICIES=('compact','full','escalate','fresh-full','fresh-escalate')
FAULTS=('clean','omitted','old-replay','matching-forgery','two-errors','noise','erasure')
sha=lambda b:hashlib.sha256(b).hexdigest()

def load(root):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    a=runpy.run_path(str(root/'acoustic-clarification.py')); v=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,_=v['build'](root)
    old,new=raw; long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    return a,{s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}

def fixture(books,seed):
    rng=np.random.default_rng(seed); tasks=[]
    for agent in range(2):
        length=13 if (seed+agent)%2==0 else 18; book=books[agent][length]
        target=int(rng.integers(len(book))); ids=sorted([target,*map(int,rng.choice(np.delete(np.arange(len(book)),target),3,False))]); counts=[Counter(map(int,book[ids,p])) for p in range(3,length)]
        pos=min(range(3,length),key=lambda p:(max(counts[p-3].values()),sum(n*n for n in counts[p-3].values()),p)); rival=next(i for i in ids if book[i,pos]!=book[target,pos]); omitted=next(int(i) for i in np.flatnonzero(book[:,pos]==book[target,pos]) if i not in ids)
        tasks.append(dict(agent=agent,length=length,ids=ids,pos=pos,target=target,rival=rival,omitted=omitted))
    return tasks

def simulate(a,books,tasks,seed,fault,policy,deadlines,keep_audio=False):
    now=0; budget=deadlines[-1]; used={0,1}; events=[]; outcomes=[]; clips=[]
    for task,deadline in zip(tasks,deadlines):
        agent=task['agent']; length=task['length']; book=books[agent][length]; target=task['omitted'] if fault=='omitted' else task['target']; ids=task['ids']; pos=task['pos']; chosen=None
        modes=['full'] if policy.endswith('full') else ['compact','full'] if policy.endswith('escalate') else ['compact']
        for attempt,mode in enumerate(modes):
            cost=17 if mode=='compact' else 16+length # 7 query + 2 turnaround + (8 or 7+length) reply
            if now+cost>min(deadline,budget): events.append(dict(t=now,event='cannot-fit',agent=agent,mode=mode,required=cost,deadline=deadline)); break
            nonce=agent+2*attempt
            if policy.startswith('fresh'):
                nonce=next(n for n in range(289) if n not in used)
            reused=nonce in used; used.add(nonce); request=[nonce//17,nonce%17,pos-3 if mode=='compact' else 16]; ns=seed*1000+agent*100+attempt*10; sd=2500 if fault=='noise' else 0
            qo,qpcm,qt=a['exchange'](a['code'](request),sd,ns); q=a['recover'](qo) if qo is not None else None
            start=now; now+=qt['slots']; events.append(dict(t=now,event='query',agent=agent,start=start,mode=mode,request=request,decoded=q,reused=reused,wire=qt)); clips.append(qpcm.reshape(-1)) if keep_audio else None
            got=[]; rt=None
            if q is not None and (q[2]==16 or 0<=q[2]<length-3):
                now+=2; sender=task['rival'] if fault in ('old-replay','matching-forgery') else target; echo=[0,agent] if fault=='old-replay' else q[:2]
                def payload(i): return a['code'](echo+[q[2],int(book[i,q[2]+3])]) if q[2]!=16 else a['code'](echo+[16])+book[i].tolist()
                wire=payload(sender)
                if fault=='two-errors':
                    other=payload(task['rival']); diff=[i for i in range(len(wire)) if wire[i]!=other[i]]
                    for i in diff[:2]: wire[i]=other[i]
                ro,rpcm,rt=a['exchange'](wire,sd,ns+1,len(wire)-1 if fault=='erasure' else None); start=now; now+=rt['slots']
                if keep_audio: clips.extend([np.zeros(2*1280,dtype='<i2'),rpcm.reshape(-1)])
                if ro is not None and mode=='compact' and len(ro)==6:
                    h=a['recover'](ro)
                    if h is not None and h[:3]==request: got=[i for i in ids if book[i,pos]==h[3]]
                if ro is not None and mode=='full' and len(ro)==5+length:
                    h=a['recover'](ro[:5]); body=ro[5:]; keep=[i for i,x in enumerate(body) if x is not None]; e=length-len(keep)
                    if h==request and e<=4:
                        found=np.flatnonzero(2*np.count_nonzero(book[:,keep]!=[body[i] for i in keep],axis=1)+e<=4); got=found.tolist() if len(found)==1 else []
                events.append(dict(t=now,event='reply',agent=agent,start=start,mode=mode,returned=got,wire=rt))
            assert now<=deadline and now<=budget
            if len(got)==1:
                chosen=got[0]; events.append(dict(t=now,event='action',agent=agent,identity=chosen)); break
        outcomes.append(dict(agent=agent,target=target,chosen=chosen,status='abstain' if chosen is None else 'correct' if chosen==target else 'wrong',deadline=deadline))
    row=dict(seed=seed,fault=fault,policy=policy,deadlines=deadlines,tasks=tasks,outcomes=outcomes,events=events,elapsed=now,wire_slots=sum(e['wire']['slots'] for e in events if 'wire' in e))
    return row, np.concatenate(clips) if clips else None

def audit(row):
    last=0; replies={}; actions={}; seen=set(); wire=0
    for e in row['events']:
        assert e['t']>=last; last=e['t']; agent=e['agent']
        if 'wire' in e:
            assert e['t']-e['start']==e['wire']['slots']; wire+=e['wire']['slots']
        if e['event']=='query':
            nonce=tuple(e['request'][:2]); assert e['reused']==(nonce in seen or nonce in {(0,0),(0,1)}); seen.add(nonce)
            if row['policy'].startswith('fresh'): assert not e['reused']
        if e['event']=='reply': replies[agent]=e['returned']
        if e['event']=='action':
            assert agent not in actions and replies[agent]==[e['identity']] and e['t']<=row['deadlines'][agent]; actions[agent]=e['identity']
    assert row['wire_slots']==wire and last<=row['deadlines'][-1]
    for o in row['outcomes']: assert o['chosen']==actions.get(o['agent']) and o['status']==('abstain' if o['chosen'] is None else 'correct' if o['chosen']==o['target'] else 'wrong')

def run(root,out):
    a,books=load(root); out.mkdir(parents=True,exist_ok=False); rows=[]; stats={}; examples=[]; specimens=[]
    for seed,fault,policy,deadlines in itertools.product(range(4564200,4564216),FAULTS,POLICIES,((30,50),(40,72))):
        tasks=fixture(books,seed); save=seed==4564200 and deadlines==(30,50) and fault in ('clean','old-replay','matching-forgery') and policy in ('compact','full','fresh-full')
        row,pcm=simulate(a,books,tasks,seed,fault,policy,deadlines,save); audit(row); rows.append(row)
        k=f'{deadlines[0]}:{fault}:{policy}'; c=stats.setdefault(k,Counter()); c.update(o['status'] for o in row['outcomes']); c['wire_slots']+=row['wire_slots']; c['elapsed']+=row['elapsed']; c['agent0_correct']+=row['outcomes'][0]['status']=='correct'; c['agent1_correct']+=row['outcomes'][1]['status']=='correct'
        if save and pcm is not None:
            name=f'{fault}-{policy}.wav'; b=pcm.tobytes()
            with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(b)
            specimens.append(dict(file=name,pcm_sha256=sha(b),peak=int(np.abs(pcm.astype(np.int32)).max())))
        if seed==4564200: examples.append(row)
    for row in rows:
        if row['fault']=='old-replay' and row['policy'].startswith('fresh'): assert all(o['status']=='abstain' for o in row['outcomes'])
        if row['fault']=='clean' and row['policy'].endswith('full'): assert all(o['status']!='wrong' for o in row['outcomes'])
    receipt=dict(schema='mhac-interaction-acoustic-turns-v1',pin=PIN,parent=PARENT,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,runs=len(rows),stats=stats,specimens=specimens,limits='Constructed candidate sets; aligned individual PCM frames, known source/length and clock; serialized scheduling and two-slot turnaround stipulated. No frame acquisition or real-time transport, no authentication, durable nonce ledger or human evidence. Old replay is synthetic stale content with previous nonce; matching forgery uses current nonce. Different lengths are not energy matched. Deadlines are from session origin.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Acoustic turns</title><h1>Acoustic clarification turns</h1><p>Two simulated obligations. Synthetic aligned PCM; no real actions. Select a trace and step through it. Start at low system volume.</p><select id="case"></select> <button id="back">Previous</button> <button id="next">Next</button><p id="state"></p><pre id="event"></pre><h2>Original PCM exchanges</h2>'''+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)+'''<p><a href="receipt.json">Metrics</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const sel=document.querySelector('#case');for(const [j,r] of rows.entries()){let o=document.createElement('option');o.value=j;o.textContent=[r.fault,r.policy,r.deadlines].join(' / ');sel.append(o)}function draw(){let r=rows[+sel.value],e=r.events[i];document.querySelector('#state').textContent=`Event ${i+1}/${r.events.length}, slot ${e.t}; deadlines ${r.deadlines}; final outcomes ${r.outcomes.map(o=>o.status).join(', ')}`;document.querySelector('#event').textContent=JSON.stringify(e,null,2)}sel.onchange=()=>{i=0;draw()};document.querySelector('#back').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+sel.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>'''); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(dict(runs=len(rows),stats=stats)))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
