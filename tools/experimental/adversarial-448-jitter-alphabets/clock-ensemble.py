"""Refs #448/#449. Two independent receiver lanes + causal output arbiter.
python clock-ensemble.py PINNED_PACKAGE NEW_OUTPUT_DIR
Synthetic only; doubled capacity, no authentication or human evidence.
"""
import inspect, json, pathlib, runpy, sys
from collections import Counter
import numpy as np
PARENT='804d133a95503e5c5b53ea14bce3cc269faa5b2f'
S=1280; WAIT=24*S; TOL=160
MODES=('bank','fine','first','deadline','agreement')

def fuse(lanes,limit,mode):
    groups=[]; out=[]; lookup={}
    def settle(g,t):
        if g['closed']: return
        g['closed']=True; values=set(g['votes'].values())
        if len(values)>1: kind='conflict'
        elif values and (mode!='agreement' or len(g['votes'])==2): kind='release'
        else: kind='abstain'
        out.append(dict(kind=kind,sample=t,source=g['source'],body_start=g['start'],votes=dict(g['votes']),identity=list(next(iter(values))) if kind=='release' else None))
    events=sorted((e['sample'],lane,i,e) for lane,es in lanes.items() for i,e in enumerate(es) if e['sample']<=limit)
    for t,lane,_,e in events:
        for g in groups:
            if g['deadline']<t: settle(g,g['deadline'])
        key=(lane,e['source'],e['body_start'])
        if e['kind']=='start':
            choices=[g for g in groups if not g['closed'] and g['source']==e['source'] and lane not in g['lanes'] and abs(g['start']-e['body_start'])<=TOL]
            if len(choices)==1: g=choices[0]
            else:
                g=dict(source=e['source'],start=e['body_start'],deadline=t+WAIT,lanes=set(),votes={},closed=False); groups.append(g)
            g['lanes'].add(lane); lookup[key]=g
        elif e['kind']=='release':
            g=lookup[key]
            if not g['closed']:
                g['votes'][lane]=tuple(e['identity'])
                if mode=='first' or len(g['votes'])==2: settle(g,t)
    for g in groups:
        if g['deadline']<=limit: settle(g,g['deadline'])
    return sorted(out,key=lambda e:e['sample'])

def run(root,out):
    r=runpy.run_path(str(root/'clock-refinement.py')); p=runpy.run_path(str(root/'clock-propagation.py'))
    assert p['blob'](root/'clock-refinement.py')=='dc24cdcac40e10252b070da8073028544c98ef21'
    # Reuse exact fixture generator with explicit, checked instrumentation; fresh seed.
    src=inspect.getsource(r['run']); old='for mode,receive in receivers.items():'
    assert src.count(old)==1
    src=src.replace(old,'capture(j,ci,pcm,expected,starts,receivers,books,obs,joint)\n            '+old)
    src=src.replace('if j==0:\n                    for t in sorted','if False:\n                    for t in sorted')
    rows=[]; checks=0
    def capture(j,ci,pcm,expected,starts,receivers,books,obs,joint):
        nonlocal checks
        lanes={k:receivers[k](pcm,books,obs,joint,'multiplex') for k in ('bank','fine')}
        # Physical end, not decoder readiness, defines deadline metrics.
        pre,body,*_=env['CASES'][ci]; ends=[starts[0]+20*S,starts[1]+round(15*S*(1+body/1e6))]+([starts[2]+15*S] if len(starts)==3 else [])
        policies={**lanes,**{k:fuse(lanes,len(pcm),k) for k in MODES[2:]}}
        for mode,ev in policies.items():
            releases=[e for e in ev if e['kind']=='release']; want=Counter(map(tuple,expected)); got=Counter((e['source'],*e['identity']) for e in releases); correct=sum((want&got).values())
            timely=[]
            for budget in (0,3200,8000):
                timely.append(sum(any((e['source'],*e['identity'])==tuple(z) and e['sample']<=end+budget for e in releases) for z,end in zip(expected,ends)))
            rows.append(dict(pair=j,condition=ci,mode=mode,expected=expected,ends=ends,correct=correct,wrong=sum(got.values())-correct,timely=timely,pcm_sha256=p['sha'](pcm.tobytes()),events=ev))
        if j==0:
            for t in sorted({e['sample'] for k in MODES[2:] for e in policies[k]}):
                short={k:receivers[k](pcm[:t],books,obs,joint,'multiplex') for k in lanes}
                for k in MODES[2:]:
                    assert fuse(short,t,k)==[e for e in policies[k] if e['sample']<=t]; checks+=1
    env=dict(r,capture=capture,SEED=4480450)
    env['CASES']=r['CASES']+[(12500,-12500,.7,120,10,None),(-12500,12500,.7,120,-10,None)]
    exec(src,env); env['run'](root,out)
    assert all(len({z['pcm_sha256'] for z in rows if z['pair']==j and z['condition']==c})==1 for j in range(6) for c in range(len(env['CASES'])))
    # Direct arbiter negative fixture: same start, different valid identities.
    def event(kind,t,identity=None): return dict(kind=kind,sample=t,source=0,body_start=100,identity=identity)
    witness={'bank':[event('start',10),event('release',1000,[13,1])],'fine':[event('start',10),event('release',2000,[13,2])]}
    assert fuse(witness,2000,'deadline')[0]['kind']=='conflict' and fuse(witness,2000,'agreement')[0]['kind']=='conflict'
    assert fuse(witness,2000,'first')[0]['identity']==[13,1]
    stats={}
    for z in rows:
        for group in ('total',str(z['condition'])):
            q=stats.setdefault(group,{}).setdefault(z['mode'],Counter()); q.update(expected=len(z['expected']),correct=z['correct'],wrong=z['wrong'],by_end=z['timely'][0],by_200ms=z['timely'][1],by_500ms=z['timely'][2],conflicts=sum(e['kind']=='conflict' for e in z['events']),abstentions=sum(e['kind']=='abstain' for e in z['events']))
    (out/'ensemble-traces.jsonl').write_text(''.join(json.dumps(z)+'\n' for z in rows)); receipt=dict(parent=PARENT,seed=env['SEED'],conditions=env['CASES'],source_sha256=p['sha'](pathlib.Path(__file__).read_bytes()),prefix_checks=checks,stats=stats,limits='Two independent capacity-two receivers, up to four hypotheses; causal output fusion, not matched-budget or shared admission. Start matching tolerance 10 ms; deadline 24 slots after first acquisition. First policy can emit duplicates or premature interpretations. No EOF flush. Constructed disagreement fixture is event-level only. No human evidence.')
    (out/'ensemble.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'ensemble.html').write_text('<!doctype html><meta charset="utf-8"><title>Clock ensemble</title><h1>Clock ensemble</h1><p>Two independent decoders; synthetic only. <a href="index.html">Original WAV gallery</a> (opt-in playback).</p><pre>'+json.dumps(stats,indent=2)+'</pre><a href="ensemble-traces.jsonl">Traces</a>')
    (out/'manifest.json').unlink(); (out/'manifest.json').write_text(json.dumps({f.name:p['sha'](f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
