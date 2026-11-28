"""Adversarial lane, Refs #448/#449. Acquisition-local event fault isolation.
Run: python acquisition-local.py PINNED_PACKAGE NEW_OUTPUT_DIR
Synthetic replay only. Trusted epoch, source and origin; no physical authentication.
One start and one terminal per lane per acquisition (overflow is both).
A terminal may precede its start on delivery, but cannot authorize alone.
No retransmission; repair-needed is a diagnostic, not an executed repair.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='de1ac58b1abc0d381541ba1ff93bb8179a009ca9'
TRACE='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
OLD='911c805c9fec20cbe2360ae54d7bd0267e695d87afe9671d014c03cc3e45b3c7'
LANES=('bank','fine'); ACQ={'start','overflow-ready-protected'}; TERM={'release','reject','timeout','evict'}
SLOT=1280

def replay(wire,h,epoch,cap=4,action=24*SLOT,retain=40*SLOT):
    assert cap>0 and 0<action<=retain
    groups={}; retired={}; out=[]; peak=0; batch=C.defaultdict(list); times={h}
    for m in wire:
        t=m['arrival']
        if t<=h:
            batch[t].append(m); times.update(x for x in (t,m['origin']+action,m['origin']+retain) if t<=x<=h)
    def emit(kind,t,**kw): out.append(dict(kind=kind,sample=t,**kw))
    def close(key):
        retired[key[0]]=max(key[1],retired.get(key[0],-1)); del groups[key]
    for t in sorted(times):
        for m in batch[t]:
            e=m['event']; lane=m['lane']; s=e['source']; o=m['origin']; key=(s,o)
            if m['epoch']!=epoch: emit('stale-epoch',t); continue
            if lane not in LANES or s not in (0,1) or not 0<=o<=e['sample']<=t<=o+retain or e['kind'] not in ACQ|TERM or (e['kind'] in ACQ and e['sample']!=o):
                emit('invalid-or-expired',t,key=key); continue
            if key not in groups:
                if o<=retired.get(s,-1): emit('retired-or-older',t,key=key); continue
                if len(groups)>=cap: emit('capacity-refusal',t,key=key); continue
                groups[key]={'starts':{},'done':{},'closed':False,'bad':False}; peak=max(peak,len(groups))
            d=groups[key]
            def put(part):
                if lane in d[part]:
                    if d[part][lane]!=e: d['bad']=True; emit('contradictory-envelope',t,key=key,lane=lane)
                    else: emit('duplicate-envelope',t,key=key,lane=lane)
                else: d[part][lane]=e
            if e['kind'] in ACQ: put('starts')
            if e['kind']!='start':
                put('done')
                if lane not in d['starts']: emit('repair-needed',t,key=key,lane=lane,missing='start')
            if d['bad']:
                emit('quarantine',t,key=key); close(key); continue
        # Settle after the complete delivery-time batch, including duplicates.
        for key,d in list(groups.items()):
            o=key[1]
            if len(d['starts'])==len(d['done'])==2:
                a,b=[d['starts'][k]['body_start'] for k in LANES]
                votes={k:v['identity'] for k,v in sorted(d['done'].items()) if v['kind']=='release'}
                vals={tuple(v) for v in votes.values()}
                mismatch=abs(a-b)>160 or any(d['starts'][k]['body_start']!=d['done'][k]['body_start'] for k in LANES)
                kind='quarantine' if mismatch else 'conflict' if len(vals)>1 else 'settled' if vals else 'abstain'
                emit(kind,t,source=key[0],acquisition=o,identity=list(next(iter(vals))) if kind=='settled' else None,action_authorized=kind=='settled' and t<=o+action,votes=votes); close(key); continue
            if not d['closed'] and t>=o+action: emit('action-expired',t,key=key); d['closed']=True
            if t>=o+retain:
                emit('retention-incomplete',t,key=key,missing={p:[k for k in LANES if k not in d[p]] for p in ('starts','done')}); close(key)
        assert len(groups)<=cap and len(retired)<=2
    return out,dict(peak_groups=peak,unresolved=len(groups))

def fixtures(envelopes):
    def lane(i): return [dict(kind='start',sample=0,source=0,body_start=100),dict(kind='release',sample=50,source=0,body_start=100,identity=[13,i])]
    w=envelopes(dict(bank=lane(7),fine=lane(7)),'e')
    def r(w): return replay(w,300,'e',action=100,retain=200)[0]
    def settles(ev): return [e for e in ev if e['kind']=='settled']
    assert settles(r(w))[0]['action_authorized']
    delay=[dict(m,arrival=80) if m['lane']=='fine' and m['seq']==0 else m for m in w]
    assert settles(r(delay))[0]['sample']==80 and any(e['kind']=='repair-needed' for e in r(delay))
    assert not settles(r([m for m in delay if not(m['lane']=='fine' and m['seq']==0)]))
    altered=dict(w[-1],event=dict(w[-1]['event'],identity=[13,8]))
    assert not settles(r(w+[altered])) and any(e['kind']=='quarantine' for e in r(w+[altered]))
    # A contradictory terminal after settlement cannot revoke an earlier action flag.
    assert settles(r(w+[dict(altered,arrival=60)]))==settles(r(w))
    assert r(w+[dict(altered,arrival=60)])[-1]['kind']=='retired-or-older'
    late=[dict(m,arrival=110) if m['lane']=='fine' and m['seq']==0 else m for m in w]
    assert not settles(r(late))[0]['action_authorized']
    return 7

def run(root,out):
    sha=lambda b:hashlib.sha256(b).hexdigest(); src=root/'ensemble1/ensemble-traces.jsonl'; oldfile=root/'transport-binding.py'
    assert sha(src.read_bytes())==TRACE and sha(oldfile.read_bytes())==OLD
    old=runpy.run_path(str(oldfile)); groups=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); groups[z['pair'],z['condition']][z['mode']]=z
    names=('clean','start-delay240','terminal-delay240','start-after-terminal','drop-start','drop-terminal','duplicate-terminal','stale-epoch')
    stats={}; rows=[]; checks=equiv=0; h=48*SLOT
    def sig(es): return sorted((e['sample'],e['source'],tuple(e['identity']),e['action_authorized']) for e in es if e['kind']=='settled')
    for key,g in sorted(groups.items()):
        epoch=str(key); wire=old['envelopes']({k:g[k]['events'] for k in LANES},epoch); want=C.Counter(map(tuple,g['bank']['expected']))
        for name in names:
            w=old['fault'](wire,name)
            for policy in ('id-only','seq640','local'):
                f=(lambda w,h:replay(w,h,epoch)) if policy=='local' else (lambda w,h:old['replay'](w,h,epoch,ordered=policy!='id-only',wait=640))
                ev,state=f(w,h); label=name+'/'+policy
                if name=='clean' and policy=='local': assert sig(ev)==sig(old['replay'](w,h,epoch,ordered=False)[0]); equiv+=1
                def count(auth):
                    got=C.Counter((e['source'],*e['identity']) for e in ev if e['kind']=='settled' and (not auth or e['action_authorized'])); n=sum((got&want).values()); return n,sum(got.values())-n
                n,b=count(False); a,c=count(True); s=stats.setdefault(label,C.Counter()); s.update(expected=sum(want.values()),correct=n,wrong=b,authorized=a,wrong_authorized=c); s.update(e['kind'] for e in ev if e['kind']!='settled'); s['peak_groups']=max(s['peak_groups'],state['peak_groups'])
                rows.append(dict(pair=key[0],condition=key[1],policy=label,correct=n,wrong=b,authorized=a,wrong_authorized=c,events=ev,state=state))
                if policy=='local':
                    for t in sorted({m['arrival'] for m in w}|{e['sample'] for e in ev}):
                        assert f([m for m in w if m['arrival']<=t],t)[0]==[e for e in ev if e['sample']<=t]; checks+=1
    receipt=dict(parent=PARENT,trace_sha256=TRACE,source_sha256=sha(pathlib.Path(__file__).read_bytes()),captures=len(groups),evaluations=len(rows),prefix_checks=checks,clean_equivalence=equiv,fixtures=fixtures(old['envelopes']),stats=stats,limits='Batch replay; bounded four active groups and two source retirement watermarks; older unseen starts may be refused after newer settlement. Same timestamp batch is atomic. No repair execution, authenticity, new PCM or human evidence; cannot revoke a prior authorization.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Acquisition-local fault isolation</title><h1>Acquisition-local fault isolation</h1><p>Retained synthetic event replay, not human evidence.</p><a href="../ensemble1/index.html">Acoustic gallery</a><select id="p"></select><pre id="v"></pre><script>const d='+json.dumps(stats)+';const p=document.getElementById("p"),v=document.getElementById("v");for(const k of Object.keys(d))p.add(new Option(k,k));function draw(){v.textContent=JSON.stringify(d[p.value],null,2)}p.onchange=draw;draw()</script><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
