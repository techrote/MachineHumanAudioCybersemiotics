"""Refs #448/#449. Synthetic event transport, not acoustic authentication.
Usage: python transport-binding.py PINNED_PACKAGE NEW_OUTPUT_DIR
Common acquisition IDs are constructed from original observed same-hop starts,
not true transmitted identity. Trusted producer/epoch/clock is an assumption.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='5b4cfdf05080b4adc11d2618a0132631172598b4'
TRACE='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
LANES=('bank','fine'); ACQ={'start','overflow-ready-protected'}; TERM={'release','reject','timeout','evict'}
SLOT=1280

def envelopes(lanes,epoch):
    out=[]
    for lane in LANES:
        keys={}; seq=0
        for e in lanes[lane]:
            if e['kind'] not in ACQ|TERM: continue
            key=(e['source'],e['body_start'])
            if e['kind'] in ACQ: keys[key]=e['sample']
            assert key in keys
            out.append(dict(lane=lane,epoch=epoch,seq=seq,arrival=e['sample'],origin=keys[key],event=e.copy()))
            seq+=1
    return out

def replay(wire,h,epoch,ordered=True,wait=160,buffer_cap=4,cap=4,action=24*SLOT,retain=40*SLOT):
    """Finite replay. Output time is actual arrival/processing time, never origin.
    Per-lane sequence gaps fail closed for remaining epoch; no retransmit/reset.
    Active groups, reorder buffers and watermarks bounded, batch logs unbounded.
    Assumes trusted metadata; no cryptographic authenticity or physical binding.
    """
    assert 0<wait<action<=retain and buffer_cap>0 and cap>0
    groups={}; water={}; out=[]; peak=[0,0]; nxt=dict.fromkeys(LANES,0)
    pending={k:{} for k in LANES}; failed=set(); batch=C.defaultdict(list)
    times={h}
    for m in wire:
        t=m['arrival']
        if t<=h:
            batch[t].append(m); times.update(x for x in (t,t+wait,m['origin']+action,m['origin']+retain) if t<=x<=h)
    def emit(kind,t,**kw): out.append(dict(kind=kind,sample=t,**kw))
    def process(m,t):
        e=m['event']; lane=m['lane']; s=e['source']; o=m['origin']; key=(s,o); w=(lane,s)
        if s not in (0,1) or not 0<=o<=e['sample']<=m['arrival']<=t or t>o+retain:
            emit('invalid-or-expired',t,lane=lane,seq=m['seq']); return
        if e['kind'] in ACQ:
            if e['sample']!=o or o<=water.get(w,-1):
                emit('stale-start',t,lane=lane,key=key); return
            water[w]=o
            if key not in groups:
                if len(groups)>=cap: emit('capacity-refusal',t,key=key); return
                groups[key]={'starts':{},'done':{},'closed':False}
                peak[0]=max(peak[0],len(groups))
            d=groups[key]; d['starts'][lane]=e['body_start']
            if e['kind']!='start': d['done'][lane]=e
        elif e['kind'] in TERM:
            d=groups.get(key)
            if d is None or d['starts'].get(lane)!=e['body_start']:
                emit('orphan-terminal',t,lane=lane,key=key); return
            if lane in d['done']: emit('duplicate-terminal',t,lane=lane,key=key); return
            d['done'][lane]=e
        else: raise ValueError('unexpected event kind')
        if len(d['done'])==2:
            votes={k:v['identity'] for k,v in sorted(d['done'].items()) if v['kind']=='release'}
            vals={tuple(v) for v in votes.values()}
            kind='quarantine' if abs(d['starts']['bank']-d['starts']['fine'])>160 else 'conflict' if len(vals)>1 else 'settled' if vals else 'abstain'
            emit(kind,t,source=s,acquisition=o,identity=list(next(iter(vals))) if kind=='settled' else None,action_authorized=kind=='settled' and t<=o+action,votes=votes)
            del groups[key]
    def fail(lane,t,reason):
        failed.add(lane); pending[lane].clear(); emit('lane-failed',t,lane=lane,reason=reason)
    for t in sorted(times):
        for m in batch[t]:
            lane=m['lane']; seq=m['seq']
            if m['epoch']!=epoch: emit('stale-epoch',t,lane=lane); continue
            if lane in failed: emit('failed-lane-event',t,lane=lane); continue
            if not ordered: process(m,t); continue
            p=pending[lane]
            if seq<nxt[lane]: emit('stale-sequence',t,lane=lane,seq=seq); continue
            if seq in p:
                if {k:v for k,v in p[seq].items() if k!='arrival'}!={k:v for k,v in m.items() if k!='arrival'}: fail(lane,t,'conflicting-buffered-sequence')
                else: emit('duplicate-buffered',t,lane=lane,seq=seq)
                continue
            if seq==nxt[lane]:
                process(m,t); nxt[lane]+=1
                while nxt[lane] in p: process(p.pop(nxt[lane]),t); nxt[lane]+=1
            elif seq-nxt[lane]>buffer_cap or len(p)>=buffer_cap: fail(lane,t,'reorder-overflow')
            else: p[seq]=m; peak[1]=max(peak[1],sum(map(len,pending.values())))
        for lane,p in pending.items():
            if p and min(m['arrival'] for m in p.values())+wait<=t: fail(lane,t,'sequence-gap')
        for key,d in list(groups.items()):
            if not d['closed'] and t>=key[1]+action: emit('action-expired',t,key=key); d['closed']=True
            if t>=key[1]+retain: emit('retention-incomplete',t,key=key); del groups[key]
        assert len(groups)<=cap and all(len(p)<=buffer_cap for p in pending.values())
    return out,dict(peak_groups=peak[0],peak_buffer=peak[1],unresolved=len(groups))

def fault(wire,name):
    w=[dict(m,event=m['event'].copy()) for m in wire]; fine=[m for m in w if m['lane']=='fine']; a=fine[0]; b=next(m for m in fine if m['event']['kind'] in TERM)
    if name.startswith('start-delay'): a['arrival']+=int(name[11:])
    if name.startswith('terminal-delay'): b['arrival']+=int(name[14:])
    if name=='drop-start': w.remove(a)
    if name=='drop-terminal': w.remove(b)
    if name=='duplicate-terminal': w.append(dict(b,arrival=b['arrival']+80))
    if name=='stale-epoch': w.extend(dict(m,epoch='old',arrival=m['arrival']+80) for m in fine)
    if name=='start-after-terminal': a['arrival']=b['arrival']+80
    return sorted(w,key=lambda m:m['arrival'])

def fixtures():
    def lane(i=7): return [dict(kind='start',sample=0,source=0,body_start=100),dict(kind='release',sample=50,source=0,body_start=100,identity=[13,i])]
    w=envelopes(dict(bank=lane(),fine=lane()),'e')
    def r(w,**kw): return replay(sorted(w,key=lambda m:m['arrival']),300,'e',action=100,retain=200,wait=20,**kw)[0]
    assert r(w)[-1]['action_authorized']
    assert not any(x['kind']=='settled' for x in r(envelopes(dict(bank=lane(),fine=lane(8)),'e')))
    assert r(envelopes(dict(bank=lane(),fine=lane(8)),'e'))[-1]['kind']=='conflict'
    w2=fault(w,'start-after-terminal'); assert any(x['kind']=='lane-failed' for x in r(w2))
    w2=[dict(m,arrival=60) if m['lane']=='fine' and m['seq']==0 else m for m in w]
    assert any(x['kind']=='settled' for x in r(w2)) and not any(x['kind']=='settled' for x in r(w2,ordered=False))
    assert any(x['kind']=='retention-incomplete' for x in r(fault(w,'drop-terminal')))
    assert any(x['kind']=='stale-epoch' for x in r(fault(w,'stale-epoch')))
    late=[dict(m,arrival=110) if m['lane']=='fine' and m['seq']==1 else m for m in w]
    assert r(late)[-1]['kind']=='settled' and not r(late)[-1]['action_authorized']
    # Identical visible frame token and agreeing semantics, two hidden physical origins.
    hidden={'bank':'physical-A','fine':'physical-B'}
    assert len(set(hidden.values()))==2 and r(w)[-1]['action_authorized']
    # A conflicting old sequence cannot be detected by a high-water mark alone.
    changed=dict(w[-1],arrival=70,event=dict(w[-1]['event'],identity=[13,8]))
    assert r(w+[changed])[-1]['kind']=='stale-sequence'
    edge=[dict(m,arrival=100) if m['lane']=='fine' and m['seq']==1 else m for m in w]
    assert r(edge)[-1]['action_authorized']
    buffered=[dict(m,arrival=80) if m['lane']=='fine' and m['seq']==0 else m for m in w]
    altered=dict(w[-1],arrival=55,event=dict(w[-1]['event'],identity=[13,8]))
    assert any(x.get('reason')=='conflicting-buffered-sequence' for x in r(buffered+[altered]))
    jump=[dict(m,seq=6) if m['lane']=='fine' and m['seq']==1 else m for m in w]
    assert any(x.get('reason')=='reorder-overflow' for x in r(jump))
    doubled=w+ [dict(m,seq=m['seq']+2,event=dict(m['event'],source=1),arrival=m['arrival']+1) for m in w]
    assert any(x['kind']=='capacity-refusal' for x in r(doubled,cap=1,ordered=False))
    return 14

def run(root,out):
    sha=lambda b:hashlib.sha256(b).hexdigest(); src=root/'ensemble1/ensemble-traces.jsonl'; assert sha(src.read_bytes())==TRACE
    oldfile=root/'dual-deadline.py'; assert sha(oldfile.read_bytes())=='2551bd2294646c1829e00f17a64d80cd7131cebb108c0d57a113f9f4b66134bf'
    old=runpy.run_path(str(oldfile))['replay']; groups=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); groups[z['pair'],z['condition']][z['mode']]=z
    rows=[]; stats={}; checks=0; equivalent=0; common_ids=0; h=48*SLOT
    names=('clean','start-delay80','start-delay240','terminal-delay80','terminal-delay240','start-after-terminal','drop-start','drop-terminal','duplicate-terminal','stale-epoch')
    for key,g in sorted(groups.items()):
        assert len({v['pcm_sha256'] for v in g.values()})==1
        lanes={k:g[k]['events'] for k in LANES}; want=C.Counter(map(tuple,g['bank']['expected'])); epoch=f'{key[0]}:{key[1]}'; wire=envelopes(lanes,epoch)
        starts=C.defaultdict(list)
        for m in wire:
            if m['event']['kind'] in ACQ: starts[m['event']['source'],m['origin']].append(m)
        assert all(len(ms)==2 and {m['lane'] for m in ms}==set(LANES) and abs(ms[0]['event']['body_start']-ms[1]['event']['body_start'])<=160 for ms in starts.values())
        common_ids+=len(starts)
        baseline=old(lanes,h,retain=40*SLOT)[0]
        for name in names:
            w=fault(wire,name)
            for policy in ('id-only','seq160','seq640'):
                kw=dict(ordered=policy!='id-only',wait=640 if policy=='seq640' else 160)
                ev,state=replay(w,h,epoch,**kw)
                def signature(es): return sorted((e['sample'],e['source'],tuple(e['identity']),e['action_authorized']) for e in es if e['kind']=='settled')
                if name=='clean' and policy=='seq160': assert signature(ev)==signature(baseline); equivalent+=1
                def count(auth):
                    got=C.Counter((e['source'],*e['identity']) for e in ev if e['kind']=='settled' and (not auth or e['action_authorized'])); n=sum((got&want).values()); return n,sum(got.values())-n
                correct,wrong=count(False); authorized,bad=count(True); label=f'{name}/{policy}'
                s=stats.setdefault(label,C.Counter()); s.update(expected=sum(want.values()),correct=correct,wrong=wrong,authorized=authorized,wrong_authorized=bad); s.update(e['kind'] for e in ev if e['kind']!='settled')
                for k in ('peak_groups','peak_buffer'): s[k]=max(s[k],state[k])
                rows.append(dict(pair=key[0],condition=key[1],policy=label,correct=correct,wrong=wrong,authorized=authorized,wrong_authorized=bad,state=state,events=ev))
                for t in sorted({m['arrival'] for m in w}|{e['sample'] for e in ev}):
                    assert replay([m for m in w if m['arrival']<=t],t,epoch,**kw)[0]==[e for e in ev if e['sample']<=t]; checks+=1
    receipt=dict(parent=PARENT,trace_sha256=TRACE,source_sha256=sha(pathlib.Path(__file__).read_bytes()),captures=len(groups),evaluations=len(rows),prefix_checks=checks,baseline_equivalent=equivalent,common_ids=common_ids,fixtures=fixtures(),stats=stats,limits='Trusted producer-assigned common ID simulated from original acquisition observations, not true frame labels. Event faults only; not a shared acoustic front end. No authentication or real action. Sequence gaps fail closed, no retransmission. Bounded live state only, batch storage unbounded.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Event transport</title><h1>Event transport fault replay</h1><p>Synthetic event flags only. <a href="../ensemble1/index.html">Retained acoustic gallery</a></p><select id="p"></select><pre id="v"></pre><script>const d='+json.dumps(stats)+';const p=document.getElementById("p"),v=document.getElementById("v");for(const k of Object.keys(d))p.add(new Option(k,k));function draw(){v.textContent=JSON.stringify(d[p.value],null,2)}p.onchange=draw;draw()</script><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
