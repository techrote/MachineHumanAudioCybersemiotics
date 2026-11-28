"""Refs #448/#449: synthetic event replay, not a new acoustic experiment.
Usage: python dual-deadline.py PINNED_PACKAGE NEW_OUTPUT_DIR
Two clocks: acquisition-relative action expiry and evidence retention. No device action.
"""
import collections as C
import hashlib, itertools, json, pathlib, sys
PARENT='11fddcdead01e697a8db1be428f574bb144394bf'
BASE='495a98ca12bae467a507031f04931aa4254b1866'
TRACE_SHA='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
LANES=('bank','fine'); SLOT=1280; ACQ={'start','overflow-ready-protected'}
TERM={'release','reject','timeout','evict'}
def sha(b): return hashlib.sha256(b).hexdigest()
def replay(lanes,horizon,action=24*SLOT,retain=32*SLOT,cap=4):
    """Same-hop trusted association, inclusive deadlines, external append-only audit.
    Batch input and output logs are not bounded; only active groups are bounded.
    No future/ground-truth access; incomplete retention never authorizes action.
    """
    assert 0<action<=retain and cap>0
    active={}; lookup={}; out=[]; peak=0; water={}
    def emit(kind,t,g,**kw): out.append(dict(kind=kind,sample=t,source=g[0],acquisition=g[1],**kw))
    def remove(g):
        for k,v in active[g]['starts'].items(): del lookup[k,g[0],v]
        del active[g]
    def finish(g,t):
        d=active[g]; votes={k:e['identity'] for k,e in d['done'].items() if e['kind']=='release'}
        vals={tuple(v) for v in votes.values()}; kind='conflict' if len(vals)>1 else 'settled' if vals else 'abstain'
        emit(kind,t,g,identity=list(next(iter(vals))) if kind=='settled' else None,votes=votes,action_authorized=kind=='settled' and t<=g[1]+action)
        remove(g)
    def expire(t,inclusive):
        due=lambda d: d<t or inclusive and d==t
        for g in sorted(list(active),key=lambda g:(g[1],g[0])):
            d=active[g]; a=g[1]+action; r=g[1]+retain
            if not d['closed'] and due(a): emit('action-expired',a,g); d['closed']=True
            if due(r):
                emit('retention-incomplete',r,g,terminal={k:e['kind'] for k,e in d['done'].items()},votes={k:e['identity'] for k,e in d['done'].items() if e['kind']=='release'}); remove(g)
    events=sorted((e['sample'],k,i,e) for k,es in lanes.items() for i,e in enumerate(es) if e['sample']<=horizon)
    for t,chunk in itertools.groupby(events,key=lambda x:x[0]):
        expire(t,False); aq=C.defaultdict(list); batch=list(chunk)
        for _,k,_,e in batch:
            s=e['source']; b=e['body_start']; key=(k,s,b)
            if e['kind'] in ACQ:
                if s not in (0,1) or b<=water.get((k,s),-1): raise ValueError('nonmonotonic acquisition')
                water[k,s]=b; aq[s].append((k,e)); continue
            if e['kind'] not in TERM: continue
            g=lookup.get(key)
            if g is None: emit('orphan-terminal',t,(s,t),lane=k,body_start=b,terminal=e['kind']); continue
            if k in active[g]['done']: raise ValueError('duplicate terminal')
            active[g]['done'][k]=e
        for g in list(active):
            if len(active[g]['done'])==2: finish(g,t)
        expire(t,True)
        for s,es in sorted(aq.items()):
            g=(s,t); by=dict(es)
            if len(es)!=2 or set(by)!=set(LANES) or abs(by['bank']['body_start']-by['fine']['body_start'])>160:
                emit('association-quarantine',t,g,count=len(es)); continue
            if len(active)>=cap: emit('capacity-refusal',t,g); continue
            starts={k:e['body_start'] for k,e in by.items()}; active[g]=dict(starts=starts,done={k:e for k,e in by.items() if e['kind']!='start'},closed=False)
            for k,b in starts.items(): lookup[k,s,b]=g
            peak=max(peak,len(active))
            if len(active[g]['done'])==2: finish(g,t)
        assert len(active)<=cap and len(lookup)<=2*cap
    expire(horizon,True)
    return sorted(out,key=lambda e:e['sample']),dict(peak=peak,unresolved=len(active))
def fixtures():
    def e(kind,t,b=100,ident=(13,7)): return dict(kind=kind,sample=t,source=0,body_start=b,identity=list(ident))
    a=e('start',0); b=e('release',10); late=e('release',15)
    def r(x,y,h=40): return replay(dict(bank=x,fine=y),h,10,20)[0]
    assert r([a,b],[a,b])[-1]['action_authorized']
    assert [x['kind'] for x in r([a,b],[a,late])]==['action-expired','settled'] and not r([a,b],[a,late])[-1]['action_authorized']
    assert r([a,b],[a,e('release',20)])[-1]['kind']=='settled'
    assert [x['kind'] for x in r([a,b],[a,e('release',21)])]==['action-expired','retention-incomplete','orphan-terminal']
    assert r([a,b],[a,e('release',15,ident=(13,8))])[-1]['kind']=='conflict'
    assert [x['kind'] for x in r([a,b],[e('start',1),late])].count('association-quarantine')==2
    assert r([a,b],[a],19)[-1]['kind']=='action-expired'
    starts=[e('start',i*5,b=100+i) for i in range(6)]; ev,state=replay({k:starts for k in LANES},50,10,20,2)
    assert state==dict(peak=2,unresolved=0) and sum(x['kind']=='capacity-refusal' for x in ev)==2
    return 8
def run(root,out):
    src=root/'ensemble1/ensemble-traces.jsonl'; assert sha(src.read_bytes())==TRACE_SHA
    groups=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); groups[z['pair'],z['condition']][z['mode']]=z
    stats={}; rows=[]; checks=0; h=48*SLOT
    for key,group in sorted(groups.items()):
        ref=group['bank']; original={k:group[k]['events'] for k in LANES}; want=C.Counter(map(tuple,ref['expected']))
        assert len({z['pcm_sha256'] for z in group.values()})==1
        for fault in ('clean','drop-first-fine-terminal','delay-first-fine-start'):
            lanes={k:[dict(e) for e in es] for k,es in original.items()}
            for i,e in enumerate(lanes['fine']):
                if fault.startswith('drop') and e['kind'] in TERM: del lanes['fine'][i]; break
                if fault.startswith('delay') and e['kind']=='start': e['sample']+=80; break
            for slots in (24,32,40):
                ev,state=replay(lanes,h,retain=slots*SLOT); label=f'{fault}/{slots}'
                def count(action):
                    got=C.Counter((e['source'],*e['identity']) for e in ev if e['kind']=='settled' and (not action or e['action_authorized']))
                    n=sum((got&want).values()); return n,sum(got.values())-n
                correct,wrong=count(False); authorized,bad=count(True)
                row=dict(pair=key[0],condition=key[1],policy=label,expected=sum(want.values()),correct=correct,wrong=wrong,authorized=authorized,wrong_authorized=bad,**state,events=ev); rows.append(row)
                s=stats.setdefault(label,C.Counter()); s.update({k:row[k] for k in ('expected','correct','wrong','authorized','wrong_authorized','unresolved')}); s.update({k:sum(e['kind']==k for e in ev) for k in ('action-expired','retention-incomplete','orphan-terminal','association-quarantine','capacity-refusal','conflict')}); s['peak']=max(s['peak'],state['peak'])
                for t in sorted({e['sample'] for e in ev}|{e['sample'] for es in lanes.values() for e in es}):
                    short={k:[e for e in es if e['sample']<=t] for k,es in lanes.items()}; assert replay(short,t,retain=slots*SLOT)[0]==[e for e in ev if e['sample']<=t]; checks+=1
    receipt=dict(parent=PARENT,base=BASE,trace_sha256=TRACE_SHA,source_sha256=sha(pathlib.Path(__file__).read_bytes()),captures=len(groups),evaluations=len(rows),prefix_checks=checks,fixtures=fixtures(),action_slots=24,retention_slots=[24,32,40],stats=stats,limits='Frozen acoustic trace replay plus constructed event faults; no new PCM, independent detector, human evidence or real action. Action authorization is a simulated flag only. Missing terminal cannot authorize; late evidence after retention is logged as orphan, not reassociated. Same-hop pairing deliberately quarantines asynchronous starts. Batch logs unbounded; active groups capped at four. No independent scientific review.')
    out.mkdir(parents=True,exist_ok=False); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Dual deadlines</title><h1>Dual deadline replay</h1><p>Simulated event flags only. <a href="../ensemble1/index.html">Retained audio</a></p><select id="p"></select><pre id="v"></pre><script>const d='+json.dumps(stats)+';const p=document.getElementById("p"),v=document.getElementById("v");for(const k of Object.keys(d))p.add(new Option(k,k));function draw(){v.textContent=JSON.stringify(d[p.value],null,2)}p.onchange=draw;draw()</script><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p>')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
