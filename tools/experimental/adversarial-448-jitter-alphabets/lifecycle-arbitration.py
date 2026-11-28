"""Refs #448/#449. Event-level lifecycle arbitration for synchronized clock lanes.
Usage: python lifecycle-arbitration.py PINNED_PACKAGE NEW_OUTPUT_DIR
Replays frozen Run 045 traces (not a new acoustic run), plus constructed faults.
No human evidence, no shared acquisition or matched receiver budget claim.
"""
import collections as C
import hashlib, itertools, json, pathlib, runpy, sys
PARENT='a41af9b42388ac69bfef29eaefa3d61b9ec42701'
BASE='495a98ca12bae467a507031f04931aa4254b1866'
TRACE_SHA='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
LANES=('bank','fine'); HOP=80; TOL=160; LIMIT=4
ACQ={'start','overflow-ready-protected'}
TERMINAL={'release','reject','timeout','evict','overflow-ready-protected'}
def sha(b): return hashlib.sha256(b).hexdigest()

def lifecycle(lanes,limit,mode='union'):
    """Completed-hop batch API. Same detector clock required; no EOF flush.
    At most 4 unsettled groups; each lane contributes one terminal disposition.
    Unpaired/ambiguous acquisition is quarantined, not silently associated.
    No candidate is authorized until an upstream release. Output log is external.
    Trusted lane events require monotonically increasing start keys per source.
    A repeated key across hops fails the capture; this is not authentication.
    """
    assert mode in ('union','agreement')
    active={}; lookup={}; out=[]; peak=0; watermarks={}
    def emit(kind,t,g,**kw):
        out.append(dict(kind=kind,sample=t,source=g[0],acquisition=g[1],**kw))
    def settle(g,t):
        d=active[g]; votes={k:e['identity'] for k,e in d['done'].items() if e['kind']=='release'}
        values={tuple(v) for v in votes.values()}
        kind='conflict' if len(values)>1 else 'release' if values and (mode=='union' or len(votes)==2) else 'abstain'
        emit(kind,t,g,identity=list(next(iter(values))) if kind=='release' else None,votes=votes,terminal={k:e['kind'] for k,e in d['done'].items()},body_start=d['starts']['bank'])
        for k,v in d['starts'].items(): lookup.pop((k,g[0],v),None)
        del active[g]
    events=sorted((e['sample'],k,i,e) for k,es in lanes.items() for i,e in enumerate(es) if e['sample']<=limit)
    for t,batch in itertools.groupby(events,key=lambda x:x[0]):
        batch=list(batch); acquisitions=C.defaultdict(list)
        # Validate acquisition keys before processing any terminal at this hop.
        updates={}
        for _,k,_,e in batch:
            if e['kind'] not in ACQ: continue
            key=(k,e['source']); v=e['body_start']
            if e['source'] not in (0,1) or v<=watermarks.get(key,-1): raise ValueError('nonmonotonic acquisition key')
            updates[key]=max(v,updates.get(key,-1))
        watermarks.update(updates)
        # First retire existing hypotheses; then associate new acquisitions at the same hop.
        for _,k,_,e in batch:
            if e['kind'] in ACQ: acquisitions[e['source']].append((k,e)); continue
            if e['kind'] not in TERMINAL: continue
            g=lookup.get((k,e['source'],e['body_start']))
            if g is None: continue  # quarantined or unknown; no output authority
            d=active[g]
            if k in d['done']: raise ValueError('duplicate terminal event')
            d['done'][k]=e
        for g in list(active):
            if len(active[g]['done'])==2: settle(g,t)
        for source,es in sorted(acquisitions.items()):
            g=(source,t); by=dict(es)
            if len(es)!=2 or set(by)!=set(LANES) or abs(by['bank']['body_start']-by['fine']['body_start'])>TOL:
                emit('association-quarantine',t,g,count=len(es)); continue
            starts={k:e['body_start'] for k,e in by.items()}
            if any((k,source,v) in lookup for k,v in starts.items()):
                emit('association-quarantine',t,g,count=len(es)); continue
            if len(active)>=LIMIT:
                emit('capacity-refusal',t,g); continue
            active[g]=dict(starts=starts,done={k:e for k,e in by.items() if e['kind']!='start'})
            for k,v in starts.items(): lookup[k,source,v]=g
            peak=max(peak,len(active))
            if len(active[g]['done'])==2: settle(g,t)
        assert len(active)<=LIMIT and len(lookup)<=2*LIMIT
    return out,dict(peak_groups=peak,unresolved=len(active))

def fixtures():
    def e(kind,t,identity=None,start=4000): return dict(kind=kind,sample=t,source=0,body_start=start,identity=identity)
    a=e('start',3200); late=e('release',36000,[13,7]); early=e('release',24000,[13,7]); bad=e('release',28000,[13,9]); ev=e('evict',28000)
    cases=[('late-agreement',{'bank':[a,late],'fine':[a,early]},'release',36000),('disagreement',{'bank':[a,bad],'fine':[a,early]},'conflict',28000),('eviction',{'bank':[a,ev],'fine':[a,early]},'release',28000),('overflow',{'bank':[e('overflow-ready-protected',3200)],'fine':[a,early]},'release',24000),('unpaired',{'bank':[a,late],'fine':[]},'association-quarantine',3200),('ambiguous',{'bank':[a,a,late],'fine':[a,early]},'association-quarantine',3200),('unresolved',{'bank':[a],'fine':[a,early]},None,None)]
    for name,lanes,kind,t in cases:
        out,_=lifecycle(lanes,40000)
        assert [(x['kind'],x['sample']) for x in out]==([(kind,t)] if kind else []),name
    # Artificial missing terminal events: fifth group refused, never silently evicted.
    lanes={k:[e('start',3200+i*HOP,start=4000+i*HOP) for i in range(5)] for k in LANES}
    out,state=lifecycle(lanes,40000); assert state==dict(peak_groups=4,unresolved=4) and out[0]['kind']=='capacity-refusal'
    try:
        lifecycle({k:[a,e('start',3280)] for k in LANES},40000)
    except ValueError as err: assert str(err)=='nonmonotonic acquisition key'
    else: raise AssertionError('reused acquisition key')
    return len(cases)+2

def run(root,out):
    src=root/'ensemble1/ensemble-traces.jsonl'; assert sha(src.read_bytes())==TRACE_SHA
    parent=runpy.run_path(str(root/'clock-ensemble.py')); assert sha((root/'clock-ensemble.py').read_bytes())=='2b8b6b371e5d2e814a6b824b7751331b2f5da9f3708dba57e378a9e06f0c0e44'
    inputs=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); inputs[z['pair'],z['condition']][z['mode']]=z
    rows=[]; stats={}; checks=0; peaks=C.Counter(); unresolved=C.Counter(); equivalence=0; recounts=0; max_delta=0; paired=0
    for (pair,case),group in sorted(inputs.items()):
        ref=group['bank']; lanes={k:group[k]['events'] for k in LANES}; limit=48*1280
        assert len({z['pcm_sha256'] for z in group.values()})==1
        acq=[{(e['source'],e['sample']):e['body_start'] for e in lanes[k] if e['kind'] in ACQ} for k in LANES]
        assert acq[0].keys()==acq[1].keys()
        paired+=len(acq[0]); max_delta=max([max_delta]+[abs(v-acq[1][key]) for key,v in acq[0].items()])
        for mode in ('first','deadline','agreement'):
            assert json.loads(json.dumps(parent['fuse'](lanes,limit,mode)))==group[mode]['events']; equivalence+=1
        policies={k:group[k]['events'] for k in group}
        for mode in ('union','agreement'):
            ev,state=lifecycle(lanes,limit,mode); policies['lifecycle-'+mode]=ev; peaks[mode]=max(peaks[mode],state['peak_groups']); unresolved[mode]+=state['unresolved']
            for t in sorted({e['sample'] for es in lanes.values() for e in es}):
                short={k:[e for e in es if e['sample']<=t] for k,es in lanes.items()}
                assert lifecycle(short,t,mode)[0]==[e for e in ev if e['sample']<=t]; checks+=1
        want=C.Counter(map(tuple,ref['expected']))
        for mode,ev in policies.items():
            rel=[e for e in ev if e['kind']=='release']; got=C.Counter((e['source'],*e['identity']) for e in rel); correct=sum((got&want).values())
            timely=[sum(any((e['source'],*e['identity'])==tuple(z) and e['sample']<=end+b for e in rel) for z,end in zip(ref['expected'],ref['ends'])) for b in (0,3200,8000)]
            if mode in group:
                assert (correct,sum(got.values())-correct,timely)==(group[mode]['correct'],group[mode]['wrong'],group[mode]['timely']); recounts+=1
            row=dict(pair=pair,condition=case,mode=mode,expected=ref['expected'],ends=ref['ends'],pcm_sha256=ref['pcm_sha256'],correct=correct,wrong=sum(got.values())-correct,timely=timely,events=ev); rows.append(row)
            for c in ('total',str(case)):
                stats.setdefault(c,{}).setdefault(mode,C.Counter()).update(expected=sum(want.values()),correct=correct,wrong=row['wrong'],by_end=timely[0],by_200ms=timely[1],by_500ms=timely[2],**{k:sum(e['kind']==k for e in ev) for k in ('conflict','abstain','association-quarantine','capacity-refusal')})
    receipt=dict(parent=PARENT,base=BASE,trace_sha256=TRACE_SHA,source_sha256=sha(pathlib.Path(__file__).read_bytes()),captures=len(inputs),replayed_baseline_checks=equivalence,baseline_recounts=recounts,paired_acquisitions=paired,max_body_start_delta_samples=max_delta,prefix_checks=checks,constructed_tests=fixtures(),peak_groups=peaks,unresolved_groups=unresolved,stats=stats,limits='Frozen event trace replay only; this script does not run the native acoustic decoder. Both lanes have identical acquisition clock in this corpus, independently computed; same-hop association contract is intentionally narrow; trusted ordered events, monotonic keys; not robust to arbitrary event forgery. Four unsettled groups maximum; external event logs and batch input not bounded; no recovery from missing terminal evidence; no EOF flush. Not authentication, shared-resource operation or human evidence.')
    out.mkdir(parents=True,exist_ok=False); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(z)+'\n' for z in rows))
    # self-contained comparison, no dependency on file-fetch permissions
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lifecycle arbitration</title><h1>Lifecycle arbitration replay</h1><p>Frozen synthetic traces, no new acoustic evidence. <a href="../ensemble1/index.html">Original audio gallery</a></p><label>Condition <select id="case"></select></label><pre id="view"></pre><script>const data='+json.dumps(stats)+'; const s=document.getElementById("case"),v=document.getElementById("view"); for(const k of Object.keys(data)){s.add(new Option(k,k))} s.value="total"; function draw(){v.textContent=JSON.stringify(data[s.value],null,2)} s.onchange=draw;draw()</script><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p>')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
