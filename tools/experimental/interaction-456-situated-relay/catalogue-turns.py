"""Refs #456 / Draft #457. Synthetic catalogue clarification on a serialized channel.
python catalogue-turns.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Uses the preceding exact PCM adapter; local GF(17) and fingerprint implementations
follow the pinned Grammar catalogue designs, not their complete executables.
"""
import functools, hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PARENT='d575a5ebed6cc82029bc9ba159bdee9b6bd874d2'
PARENT_SHA='d14f133f592f6b9ea97ca8bce18d28eede9eb65dd9958029b1ee40edfefb9e6d'
REFERENCES={'catalogue-reply.py':'6f97617400c4e2dc1d8d6a979edcba53c64e1f62','catalogue-agreement.py':'755fa4849843a8226063465ce6426fca49fd8b86'}
POLICIES=('compact','index4','tagged','full','fallback','reserve')
FAULTS=('clean','ambiguous','omitted','shift','shift-first','collision','stale','two-errors')
DEADLINES=((30,50),(40,72),(64,78),(64,90))
sha=lambda b:hashlib.sha256(b).hexdigest()

@functools.lru_cache(None)
def matrix(points,n):
    return np.array([[functools.reduce(lambda a,j:a*(x-j)*pow((i-j)%17,-1,17)%17,(j for j in points if j!=i),1) for x in range(n)] for i in points],dtype=np.int64)
def encode(data):
    return (np.array(data)@matrix(tuple(range(len(data))),len(data)+4)%17).tolist()
def decode(obs):
    n=len(obs); k=n-4; keep=tuple(i for i,x in enumerate(obs) if x is not None); e=n-len(keep)
    if e>4:return None
    y=np.array([0 if x is None else x for x in obs]);
    for p in itertools.combinations(keep,k):
        w=y[list(p)]@matrix(p,n)%17
        if 2*np.count_nonzero(w[list(keep)]!=y[list(keep)])+e<=4:return w[:k].tolist()
    return None # unique within distance-five bound

def digits(i,k):return [(i//17**j)%17 for j in range(k)]
def index(x):return sum(v*17**j for j,v in enumerate(x))
def digest(s,l,b):return hashlib.sha256(b'MHAC-order-v1\0'+bytes([s,l])+len(b).to_bytes(4,'little')+b.astype('u1').tobytes())
def tag(h):return int.from_bytes(h.digest(),'big')%17**4

def orders(s,l,b):
    normal=np.arange(len(b)); shifted=np.roll(normal,1)
    prefix=hashlib.sha256(b'MHAC-order-v1\0'+bytes([s,l])+len(b).to_bytes(4,'little')+b[:-10].astype('u1').tobytes()); tail=b[-10:].astype('u1'); seen={}
    for count,p in enumerate(itertools.permutations(range(10)),1):
        if count>20000:raise RuntimeError('collision search bound')
        h=prefix.copy();h.update(tail[list(p)].tobytes());t=tag(h)
        if t in seen and sum(x!=y for x,y in zip(p,seen[t]))>=4:
            ca=normal.copy();cb=normal.copy();ca[-10:]=len(b)-10+np.array(seen[t]);cb[-10:]=len(b)-10+np.array(p);break
        seen[t]=p
    else:raise RuntimeError('no collision')
    assert digest(s,l,b[ca]).digest()!=digest(s,l,b[cb]).digest() and tag(digest(s,l,b[ca]))==tag(digest(s,l,b[cb]))
    assert tag(digest(s,l,b))!=tag(digest(s,l,b[shifted]))
    return {f:(x,y,tag(digest(s,l,b[x])),tag(digest(s,l,b[y]))) for f,x,y in [('clean',normal,normal),('shift',normal,shifted),('collision',ca,cb)]}

# index4: 7 query + 2 turnaround + 2 markers + 3 header + width + 4 parity = 18+width
def cost(mode,l):return {'compact':17,'index4':18+(4 if l==13 else 5),'tagged':22+(4 if l==13 else 5),'full':16+l}[mode]

def simulate(a,books,ordering,tasks,seed,fault,policy,deadlines,audio=False):
    now=0; events=[]; outcomes=[]; clips=[]; nonce=1
    for t,d in zip(tasks,deadlines):
        s,l=t['agent'],t['length']; b=books[s][l]; width=4 if l==13 else 5; so,ro,st,rt=ordering[s,l]['shift' if fault=='shift-first' and s==0 else fault if fault in ('shift','collision') else 'clean']; target=t['omitted'] if fault=='omitted' else t['target']; ids=t['ids'].copy(); pos=t['pos']; chosen=None
        if fault=='ambiguous':ids=sorted(set(ids+[t['omitted']]))
        if fault=='collision':target=int(so[np.flatnonzero(so!=ro)[seed%np.count_nonzero(so!=ro)]])
        modes=['tagged','full'] if policy in ('fallback','reserve') else [policy]
        for j,mode in enumerate(modes):
            c=cost(mode,l); remaining=cost('tagged',tasks[1]['length']) if policy=='reserve' and s==0 and j==1 else 0
            if now+c>d or now+c+remaining>deadlines[-1]:events.append(dict(t=now,event='skip',agent=s,mode=mode,cost=c,reserved=remaining));break
            op=pos-3 if mode=='compact' else {'index4':15,'tagged':14,'full':16}[mode]; request=[nonce//17,nonce%17,op];nonce+=1
            def send(payload,kind):
                nonlocal now
                obs,pcm,w=a['exchange'](payload,0,seed*100+nonce*2+int(kind=='reply'));start=now;now+=w['slots'];events.append(dict(t=now,start=start,event=kind,agent=s,mode=mode,request=request,wire=w))
                if audio:clips.append(pcm.ravel())
                return obs
            start=now; qo=send(a['code'](request),'query'); q=a['recover'](qo) if qo is not None else None; got=[]; reason='query-invalid'
            events[-1]['decoded']=q
            if q==request: # clean query fixture; not a general sender authentication gate
                now+=2
                if audio:clips.append(np.zeros(2560,dtype='<i2'))
                sender=(target+1)%len(b) if fault=='stale' else target; echo=[0,0,op] if fault=='stale' else q
                def payload(i):
                    if mode=='compact':return a['code'](echo+[int(b[i,pos])])
                    if mode=='full':return a['code'](echo)+b[i].tolist()
                    addr=int(np.flatnonzero(so==i)[0]);return encode(echo+digits(addr,width)+(digits(st,4) if mode=='tagged' else []))
                wire=payload(sender)
                if fault=='two-errors':
                    if mode in ('index4','tagged'):
                        addr=int(np.flatnonzero(so==sender)[0]); other=digits(addr,width);other[0]=(other[0]+1)%17
                        if index(other)>=len(b):other[0]=(other[0]-2)%17
                        rival=int(so[index(other)])
                    else:rival=t['rival']
                    alt=payload(rival); diff=[i for i in range(len(wire)) if wire[i]!=alt[i]]
                    assert len(diff)>=2
                    for i in diff[:2]:wire[i]=alt[i]
                obs=send(wire,'reply'); reason='correlation-or-code'
                if obs is not None:
                    if mode=='compact':
                        h=a['recover'](obs);got=[i for i in ids if b[i,pos]==h[3]] if h is not None and h[:3]==request else []
                    elif mode=='full' and len(obs)==5+l:
                        h=a['recover'](obs[:5]); body=obs[5:];keep=[i for i,x in enumerate(body) if x is not None];e=l-len(keep)
                        if h==request and e<=4:got=np.flatnonzero(2*np.count_nonzero(b[:,keep]!=[body[i] for i in keep],axis=1)+e<=4).tolist()
                    elif mode in ('index4','tagged') and len(obs)==3+width+4+(4 if mode=='tagged' else 0):
                        h=decode(obs)
                        if h is not None and h[:3]==request and index(h[3:3+width])<len(b):
                            if mode=='tagged' and index(h[3+width:])!=rt:reason='catalogue-mismatch'
                            else:got=[int(ro[index(h[3:3+width])])]
                assert now-start==c,(mode,l,now-start,c)
            if got:reason='unique' if len(got)==1 else 'ambiguous'
            events.append(dict(t=now,event='decision',agent=s,mode=mode,reason=reason,returned=got,sender_tag=st,receiver_tag=rt))
            if len(got)==1:chosen=got[0];events.append(dict(t=now,event='action',agent=s,identity=chosen));break
        outcomes.append(dict(agent=s,target=target,length=l,candidates=ids,position=pos,chosen=chosen,status='abstain' if chosen is None else 'correct' if chosen==target else 'wrong'))
    row=dict(seed=seed,fault=fault,policy=policy,deadlines=deadlines,outcomes=outcomes,events=events,elapsed=now,wire_slots=sum(e['wire']['slots'] for e in events if 'wire' in e))
    return row,np.concatenate(clips) if clips else None

def audit(row):
    last=0; decisions={};actions={};queries=set();frames=0
    for e in row['events']:
        assert last<=e['t']<=row['deadlines'][-1];last=e['t'];s=e['agent']
        if 'wire' in e:assert e['t']-e['start']==e['wire']['slots'];frames+=e['wire']['slots']
        if e['event']=='query':n=tuple(e['request'][:2]);assert n not in queries;queries.add(n)
        if e['event']=='decision':decisions[s]=e['returned']
        if e['event']=='action':assert s not in actions and decisions[s]==[e['identity']] and e['t']<=row['deadlines'][s];actions[s]=e['identity']
    assert frames==row['wire_slots'] and last==row['elapsed']
    for o in row['outcomes']:assert o['chosen']==actions.get(o['agent']) and o['status']==('abstain' if o['chosen'] is None else 'correct' if o['chosen']==o['target'] else 'wrong')

def run(root,out):
    predecessor=pathlib.Path(__file__).with_name('acoustic-turns.py');assert sha(predecessor.read_bytes())==PARENT_SHA; p=runpy.run_path(str(predecessor));a,books=p['load'](root);ordering={(s,l):orders(s,l,b) for s,ls in books.items() for l,b in ls.items()};out.mkdir(parents=True,exist_ok=False);rows=[];stats={};spec=[]
    for seed,fault,policy,ds in itertools.product(range(4564300,4564308),FAULTS,POLICIES,DEADLINES):
        tasks=p['fixture'](books,seed);save=seed==4564300 and ds==DEADLINES[-1] and fault in ('clean','shift','collision','shift-first') and policy in ('index4','fallback','full');r,pcm=simulate(a,books,ordering,tasks,seed,fault,policy,ds,save);audit(r);rows.append(r);c=stats.setdefault(f'{ds[0]}/{ds[1]}:{fault}:{policy}',Counter());c.update(o['status'] for o in r['outcomes']);c['slots']+=r['elapsed'];c['agent0_correct']+=r['outcomes'][0]['status']=='correct';c['agent1_correct']+=r['outcomes'][1]['status']=='correct'
        if save and pcm is not None:
            name=f'{fault}-{policy}.wav';raw=pcm.tobytes()
            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(raw)
            spec.append(dict(file=name,pcm_sha256=sha(raw),peak=int(abs(pcm).max())))
    for k in (7,8,11,12):
        data=list(range(k)); w=encode(data); assert decode(w)==data
        for errors in itertools.combinations(range(len(w)),2):
            o=w.copy()
            for i in errors:o[i]=(o[i]+1)%17
            assert decode(o)==data
        o=w.copy();o[:4]=[None]*4;assert decode(o)==data
    import copy
    sample=next(r for r in rows if any(e['event']=='action' for e in r['events'])); altered=copy.deepcopy(sample);next(e for e in altered['events'] if e['event']=='action')['identity']=-1
    try:audit(altered)
    except AssertionError:pass
    else:raise AssertionError('altered action accepted')
    witnesses=[]
    for (s,l),cases in ordering.items():
        so,ro,st,rt=cases['collision'];b=books[s][l];witnesses.append(dict(source=s,length=l,tag=st,sender_tail=so[-10:].tolist(),receiver_tail=ro[-10:].tolist(),sender_sha256=digest(s,l,b[so]).hexdigest(),receiver_sha256=digest(s,l,b[ro]).hexdigest()))
    receipt=dict(schema='mhac-catalogue-turns-v1',parent=PARENT,parent_sha256=PARENT_SHA,grammar_refs=REFERENCES,pcm_blobs=p['BLOBS'],source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,runs=len(rows),stats=stats,collision_witnesses=witnesses,specimens=spec,limits='Local GF(17)/fingerprint adapter, actual frozen PCM functions; known alignment, source and length, clean query, stipulated turnaround and sequential task order. Collision fixtures deliberately selected. No authentication, durable nonce state, actual human evidence or energy-matched comparisons.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));examples=[r for r in rows if r['seed']==4564300];(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Catalogue turns</title><h1>Catalogue turns</h1><p>Synthetic dialogue. Start at low volume. Select a scenario and step through events.</p><select id="case"></select> <button id="prev">Previous</button> <button id="next">Next</button><p id="state"></p><pre id="event"></pre><h2>Actual generated PCM</h2>'''+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const sel=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.fault,r.policy,r.deadlines].join(' / ');sel.append(o)});function draw(){let r=rows[+sel.value],e=r.events[i];document.querySelector('#state').textContent=`Event ${i+1}/${r.events.length} | slot ${e.t} | final ${r.outcomes.map(o=>o.status).join(', ')}`;document.querySelector('#event').textContent=JSON.stringify(e,null,2)}sel.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+sel.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''');(out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(runs=len(rows),stats=stats)))

if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
