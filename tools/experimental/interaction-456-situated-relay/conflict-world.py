"""Refs #456 / Draft #457. Synthetic situated world on frozen PCM-derived traces.
Input: interval1/traces.jsonl regenerated from Grammar #453 f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22.
No acoustic wire for grants, no authentication, no human evidence. World mapping is stipulated.
"""
import argparse, collections, hashlib, json, pathlib, math, struct, wave

PIN='f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22'
TRACE='be415c34c0766326a8dcd5db87f97dd07e03acab982a3b6856e9ae55346e101c'
POLICIES=('direct','release-grant','report-grant')
WORLDS=('independent','exclusive')
FAULTS=('clean','stale','mismatch')

def replay(events,policy,world,deadlines,budget,delay,fault):
    """Decisions receive events only, never expected identities or future events."""
    queue=collections.defaultdict(list); log=[]; known={}; pending={}; ready={}; acted={}; spent=0
    for e in events:
        if e['kind'] in ('release','overlap-conflict'): queue[e['sample']].append(e)
    for d in deadlines: queue[d]
    def emit(t,kind,**kw): log.append(dict(sample=t,kind=kind,**kw))
    while queue:
        t=min(queue); batch=queue.pop(t)
        for e in batch:
            kind=e['kind']
            if kind=='grant':
                a=e['agent']; p=pending.pop(a,None)
                ok=p is not None and e['qid']==p[0] and e['identity']==p[1] and t<deadlines[a]
                emit(t,'grant-accepted' if ok else 'grant-rejected',agent=a,qid=e['qid'],identity=e['identity'])
                if ok: ready[a]=e['identity']
                continue
            candidates=[e] if kind=='release' else e['candidates'] if policy=='report-grant' else []
            for c in candidates:
                a=c['source']; identity=[a,*c['identity']]
                if a not in known:
                    known[a]=identity; emit(t,'evidence',agent=a,identity=identity,origin=kind)
                    if policy=='direct': ready[a]=identity
        # In this stipulated world source A has exclusive priority until its deadline.
        for a in (0,1):
            if a not in ready or a in acted or t>=deadlines[a]: continue
            if policy!='direct' and world=='exclusive' and (acted or (a==1 and t<deadlines[0])): continue
            acted[a]=ready[a]; emit(t,'act',agent=a,identity=ready[a])
        if policy=='direct': continue
        for a in (0,1):
            if a not in known or a in pending or a in ready or a in acted or t+delay>=deadlines[a] or spent>=budget: continue
            if any(e['kind']=='query' and e['agent']==a for e in log): continue
            if world=='exclusive' and (acted or (a==1 and t<deadlines[0])): continue
            spent+=1; qid=spent; identity=known[a]; pending[a]=(qid,identity)
            emit(t,'query',agent=a,qid=qid,identity=identity,cost=1)
            reply=identity if fault!='mismatch' else [a,identity[1],identity[2]+1]
            queue[t+delay].append(dict(kind='grant',agent=a,qid=qid if fault!='stale' else qid-1,identity=reply))
    return log

def score(row,log,world,deadlines,budget):
    expected={x[0]:x for x in row['expected']}; desired=set(expected) if world=='independent' else {min(expected)}
    acts=[e for e in log if e['kind']=='act']; queries=[e for e in log if e['kind']=='query']; accepted=[e for e in log if e['kind']=='grant-accepted']
    assert len(queries)<=budget and len({e['agent'] for e in acts})==len(acts)
    assert all(e['sample']<deadlines[e['agent']] for e in acts)
    for e in accepted:
        assert any(q['qid']==e['qid'] and q['identity']==e['identity'] and q['sample']<e['sample'] for q in queries)
    identity_wrong=sum(e['identity']!=expected.get(e['agent']) for e in acts)
    nonpreferred=sum(e['agent'] not in desired and e['identity']==expected.get(e['agent']) for e in acts)
    correct=len(acts)-identity_wrong-nonpreferred
    return dict(correct=correct,identity_wrong=identity_wrong,nonpreferred=nonpreferred,missing=len(desired)-correct,queries=len(queries),resource_violation=int(world=='exclusive' and len(acts)>1),completed=int(correct==len(desired) and len(acts)==correct))

def generate(source,out):
    raw=source.read_bytes(); assert hashlib.sha256(raw).hexdigest()==TRACE,'frozen trace mismatch'
    rows=[json.loads(l) for l in raw.splitlines()]; assert len(rows)==224
    out.mkdir(parents=True,exist_ok=False); stats={}; traces=[]; hashes=[]
    for world in WORLDS:
      for deadlines in ((32000,56000),(40000,64000)):
       for budget in (1,2):
        for delay in (1280,3840):
         for fault in FAULTS:
          for policy in POLICIES:
           for row in rows:
            log=replay(row['events'],policy,world,deadlines,budget,delay,fault); assert log==replay(row['events'],policy,world,deadlines,budget,delay,fault)
            m=score(row,log,world,deadlines,budget)
            if policy!='direct':
                assert not m['resource_violation']
                for e in log:
                    if e['kind']=='act': assert any(g['kind']=='grant-accepted' and g['identity']==e['identity'] and g['sample']<=e['sample'] for g in log)
                if fault!='clean': assert not m['correct'] and not m['identity_wrong'] and not m['nonpreferred']
            k=':'.join(map(str,(world,deadlines[0],budget,delay,fault,policy,row['policy'])))
            stats.setdefault(k,collections.Counter()).update(m)
            r=dict(world=world,deadlines=deadlines,budget=budget,delay=delay,fault=fault,policy=policy,case=row['case'],pair=row['pair'],grammar_policy=row['policy'],pcm_sha256=row['pcm_sha256'],expected=row['expected'],metrics=m,events=log)
            hashes.append(hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest())
            if row['pair']==0 and row['case'] in ('early-dual','late-dual','old-timeout','sequential') and row['policy'] in ('exclusive','multiplex') and deadlines[0]==32000 and delay==1280 and fault=='clean': traces.append(r)
    prefix_checks=0
    for row in rows:
        for policy in POLICIES:
            for world in WORLDS:
                full=replay(row['events'],policy,world,(32000,56000),2,1280,'clean')
                for cut in (29520,32000,32800,53200):
                    short=replay([e for e in row['events'] if e['sample']<=cut],policy,world,(32000,56000),2,1280,'clean')
                    assert [e for e in full if e['sample']<=cut]==[e for e in short if e['sample']<=cut]
                    prefix_checks+=1
    receipt=dict(prefix_checks=prefix_checks,schema='mhac-conflict-world-v1',grammar_pin=PIN,trace_sha256=TRACE,cases=len(hashes),stats=stats,hashes=hashes)
    for name,obj in [('receipt.json',receipt),('traces.json',traces)]: (out/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    # Event sonification, not wire encoding. Three comparable policy replays.
    for p in POLICIES:
        r=next(r for r in traces if r['world']=='exclusive' and r['grammar_policy']=='multiplex' and r['case']=='early-dual' and r['budget']==2 and r['policy']==p)
        samples=[0]*32000
        for e in r['events']:
            f={'evidence':330,'query':440,'grant-accepted':550,'grant-rejected':220,'act':660}[e['kind']]+110*e['agent']; start=e['sample']//2
            for i in range(min(480,len(samples)-start)): samples[start+i]+=round(400*math.sin(2*math.pi*f*i/8000)*min(i/40,(479-i)/40,1))
        with wave.open(str(out/(p+'.wav')),'wb') as w: w.setparams((1,2,8000,0,'NONE','not compressed')); w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    page='<!doctype html><meta charset="utf-8"><title>Conflict world</title><h1>Conflict world</h1><p>Synthetic world using frozen PCM-derived Grammar events. Grant replies are symbolic. No human evidence.</p><select id="case"></select><input id="time" type="range" min="0" max="64000" step="80" value="64000"><output id="ms"></output><pre id="trace"></pre>'
    for p in POLICIES: page+=f'<p>{p}: <audio controls preload="none" src="{p}.wav"></audio></p>'
    page+='<p><a href="receipt.json">Receipt</a> | <a href="traces.json">Replay export</a></p><script>const rows='+json.dumps(traces)+';const c=document.getElementById("case"),t=document.getElementById("time");rows.forEach((r,i)=>c.add(new Option([r.world,r.case,r.grammar_policy,r.policy,r.budget].join(" / "),i)));function show(){const r=rows[+c.value];document.getElementById("ms").textContent=(+t.value/16)+" ms";document.getElementById("trace").textContent=JSON.stringify({events:r.events.filter(e=>e.sample<=+t.value),final:r.metrics},null,2)}c.onchange=t.oninput=show;show();document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>'
    (out/'index.html').write_text(page,encoding='utf-8'); (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(cases=len(hashes),replays=len(traces))))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('traces',type=pathlib.Path); p.add_argument('out',type=pathlib.Path); a=p.parse_args(); generate(a.traces,a.out)
