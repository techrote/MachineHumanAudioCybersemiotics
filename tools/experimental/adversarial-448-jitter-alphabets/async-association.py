"""Refs #448/#449. Bounded asynchronous association, synthetic event replay only.
Usage: python async-association.py PINNED_PACKAGE OUTPUT_DIR
No real action, human inference, authentication or new acoustic trials.
"""
import collections as C
import hashlib, itertools, json, pathlib, runpy, sys
PARENT='196a420d7b97a6cc5cb1a84c4bd59caf75c766a3'
TRACE='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
LANES=('bank','fine'); ACQ={'start','overflow-ready-protected'}; TERM={'release','reject','timeout','evict'}
SLOT=1280

def replay(lanes,h,window=160,tol=160,action=24*SLOT,retain=40*SLOT,pcap=8,gcap=4):
    """Completed arrival-time batches; closed-window bipartite components.
    Only isolated pairs settle. Pending and active state bounded; batch logs not.
    Trusted unique monotone start keys per lane/source, no source authentication.
    Deadlines anchor to earliest observed start, not later association time.
    """
    assert 0<=window<action<=retain and pcap>0 and gcap>0
    pending={}; active={}; water={}; out=[]; peak=[0,0]; blocked_until=-1
    def emit(kind,t,**kw): out.append(dict(kind=kind,sample=t,**kw))
    def finish(t):
        for keys,d in list(active.items()):
            if len(d['done'])!=2: continue
            votes={k[0]:e['identity'] for k,e in d['done'].items() if e['kind']=='release'}
            values={tuple(v) for v in votes.values()}; kind='conflict' if len(values)>1 else 'settled' if values else 'abstain'
            emit(kind,t,source=keys[0][1],acquisition=d['t'],keys=keys,identity=list(next(iter(values))) if kind=='settled' else None,votes=votes,action_authorized=kind=='settled' and t<=d['t']+action)
            del active[keys]
    def expire(t):
        for keys,d in list(active.items()):
            if not d['closed'] and t>=d['t']+action:
                emit('action-expired',t,keys=keys); d['closed']=True
            if t>=d['t']+retain:
                emit('retention-incomplete',t,keys=keys); del active[keys]
    def associate(t):
        left=set(pending)
        while left:
            seed=min(left); comp={seed}; todo=[seed]; left.remove(seed)
            while todo:
                k=todo.pop()
                for j in sorted(left):
                    if k[0]!=j[0] and k[1]==j[1] and abs(k[2]-j[2])<=tol and abs(pending[k]['t']-pending[j]['t'])<=window:
                        comp.add(j); todo.append(j); left.remove(j)
            keys=tuple(sorted(comp)); oldest=min(pending[k]['t'] for k in keys)
            # Wait for both candidate windows to close. Bound chains by retention.
            if t<max(pending[k]['t'] for k in keys)+window and t<oldest+retain: continue
            ds=[pending.pop(k) for k in keys]
            if len(keys)!=2 or keys[0][0]==keys[1][0]:
                emit('association-quarantine',t,keys=keys); continue
            if len(active)>=gcap:
                emit('capacity-refusal',t,keys=keys); continue
            active[keys]=dict(t=oldest,done={k:d['done'] for k,d in zip(keys,ds) if d['done'] is not None},closed=False)
            emit('paired',t,keys=keys,acquisition=oldest)
            peak[1]=max(peak[1],len(active))
    events=C.defaultdict(list); times={h}
    for k,es in lanes.items():
        for e in es:
            t=e['sample']
            if t>h or e['kind'] not in ACQ|TERM: continue
            events[t].append((k,e)); times.add(t)
            if e['kind'] in ACQ:
                times.update(x for x in (t+window,t+action,t+retain) if x<=h)
    for t in sorted(times):
        batch=events[t]
        # Admission before same-batch terminal; duplicate/reordered keys fail closed.
        for lane,e in sorted(batch,key=lambda x:(x[0],x[1]['body_start'])):
            if e['kind'] not in ACQ: continue
            k=(lane,e['source'],e['body_start']); w=k[:2]
            if k[1] not in (0,1) or k[2]<=water.get(w,-1):
                emit('invalid-start',t,key=k); continue
            water[w]=k[2]
            if t<=blocked_until or len(pending)>=pcap:
                emit('pending-refusal',t,key=k); blocked_until=t+window
                if pending:
                    emit('association-quarantine',t,keys=tuple(sorted(pending))); pending.clear()
                continue
            pending[k]=dict(t=t,done=e if e['kind']!='start' else None); peak[0]=max(peak[0],len(pending))
        for lane,e in batch:
            if e['kind'] not in TERM: continue
            k=(lane,e['source'],e['body_start'])
            if k in pending:
                d=pending[k]; slot='done'
            else:
                d=next((v['done'] for ks,v in active.items() if k in ks),None); slot=k
            if d is None: emit('orphan-terminal',t,key=k); continue
            if d.get(slot) is not None: emit('duplicate-terminal',t,key=k); continue
            d[slot]=e
        finish(t); expire(t); associate(t); finish(t); expire(t)
        assert len(pending)<=pcap and len(active)<=gcap
    return out,dict(peak_pending=peak[0],peak_active=peak[1],unresolved=len(active)+len(pending))

def fixtures():
    def e(kind,t,b=100,i=1): return dict(kind=kind,sample=t,source=0,body_start=b,identity=[13,i])
    def r(a,b,**kw): return replay(dict(bank=a,fine=b),1000,window=10,tol=10,action=100,retain=200,**kw)[0]
    a=[e('start',0),e('release',50)]; b=[e('start',5),e('release',60)]
    assert [x['kind'] for x in r(a,b)]==['paired','settled']
    assert r(a,b)[0]['sample']==15
    assert r([e('start',0),e('release',1)],b)[-1]['kind']=='settled'
    assert r(a,[e('start',11),e('release',60)])[0]['kind']=='association-quarantine'
    assert r(a,[e('start',5),e('release',120)])[-1]['action_authorized']==False
    assert r(a,[e('start',5),e('release',60,i=2)])[-1]['kind']=='conflict'
    ambiguous=r([e('start',0),e('start',4,105),e('release',50),e('release',60,105)],b)
    assert not any(x['kind']=='settled' for x in ambiguous) and len(ambiguous[0]['keys'])==3
    # Unique but wrong pairing is fundamentally possible when true peers are absent.
    # Both lanes can agree on an identity despite belonging to distinct physical frames.
    assert r(a,b)[-1]['action_authorized']  # hidden truth is not part of the input
    assert any(x['kind']=='pending-refusal' for x in r(a,b,pcap=1))
    assert not any(x['kind']=='settled' for x in r(a,b,pcap=1))
    assert any(x['kind']=='invalid-start' for x in r([e('start',0,105),e('start',4,100)],[]))
    assert any(x['kind']=='retention-incomplete' for x in r(a,b[:1]))
    # Identical observable events, distinct hidden physical frame ownership.
    ownership={'bank':'physical-frame-A','fine':'physical-frame-B'}
    witness=r(a,b)[-1]; assert len({ownership[k[0]] for k in witness['keys']})==2
    return 12

def run(root,out):
    sha=lambda b:hashlib.sha256(b).hexdigest()
    src=root/'ensemble1/ensemble-traces.jsonl'; assert sha(src.read_bytes())==TRACE
    parent=root/'dual-deadline.py'; assert sha(parent.read_bytes())=='2551bd2294646c1829e00f17a64d80cd7131cebb108c0d57a113f9f4b66134bf'
    old=runpy.run_path(str(parent))['replay']; groups=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); groups[z['pair'],z['condition']][z['mode']]=z
    rows=[]; stats={}; checks=0; h=48*SLOT
    for key,g in sorted(groups.items()):
        want=C.Counter(map(tuple,g['bank']['expected'])); assert len({x['pcm_sha256'] for x in g.values()})==1
        for fault in ('clean','delay80','delay160','delay240','drop-terminal'):
            lanes={k:[dict(e) for e in g[k]['events']] for k in LANES}
            for i,e in enumerate(lanes['fine']):
                if fault.startswith('delay') and e['kind']=='start': e['sample']+=int(fault[5:]); break
                if fault=='drop-terminal' and e['kind'] in TERM: del lanes['fine'][i]; break
            for policy in ('same-hop','async'):
                ev,state=(old(lanes,h,retain=40*SLOT) if policy=='same-hop' else replay(lanes,h)); label=f'{fault}/{policy}'
                def count(auth):
                    got=C.Counter((e['source'],*e['identity']) for e in ev if e['kind']=='settled' and (not auth or e['action_authorized']))
                    n=sum((got&want).values()); return n,sum(got.values())-n
                correct,wrong=count(False); authorized,bad=count(True)
                s=stats.setdefault(label,C.Counter()); s.update(expected=sum(want.values()),correct=correct,wrong=wrong,authorized=authorized,wrong_authorized=bad)
                s.update(e['kind'] for e in ev if e['kind']!='settled')
                rows.append(dict(pair=key[0],condition=key[1],policy=label,correct=correct,wrong=wrong,authorized=authorized,wrong_authorized=bad,state=state,events=ev))
                if policy=='async':
                    for t in sorted({e['sample'] for e in ev}|{e['sample'] for es in lanes.values() for e in es}):
                        assert replay(lanes,t)[0]==[e for e in ev if e['sample']<=t]; checks+=1
    receipt=dict(parent=PARENT,trace_sha256=TRACE,source_sha256=sha(pathlib.Path(__file__).read_bytes()),captures=len(groups),evaluations=len(rows),prefix_checks=checks,fixtures=fixtures(),stats=stats,limits='Event delivery perturbations, not fresh PCM; no authentication. Unique temporal pair may still be physically wrong. Bounded pending and active groups only; input and audit batch storage unbounded. No human or device action evidence.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
