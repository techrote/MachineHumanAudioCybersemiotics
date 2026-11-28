"""Adversarial #448/#449, Run 059. Synthetic PCM, exact bounded decoder.
Usage: OPENBLAS_NUM_THREADS=1 python decoder-budget.py PACKAGE OUT regression|fresh
AI-assisted exploratory research, no human evidence or action authorization.
"""
import inspect,json,pathlib,runpy,sys
from collections import Counter
import numpy as np
PARENT='71b4a26b9895eeaf64e2660f194891534c8c51f8'
PINS={'reserved-clock.py':'7cd43470479cc4d309b4de5f693c377713c99c46','shared-clock.py':'5876b059f8f6789d61e3fe7821f2a326eb170772'}
MODES={m:(4,'dual') for m in ('dense','prune','dense1m','prune1m')}
def decode(book,obs,limit,prune):
    """Return (unique radius-two index or None, comparison cells, exhausted).
    Candidate elimination is exact: mismatch counts never decrease. Erasures
    are ignored. Exhaustion never returns a partially verified identity.
    """
    keep=[i for i,x in enumerate(obs) if x is not None]; cost=0
    if not prune:
        cost=len(book)*len(keep)
        if cost>limit: return None,0,True
        hits=np.flatnonzero(np.count_nonzero(book[:,keep]!=[obs[i] for i in keep],axis=1)<=2)
    else:
        hits=np.arange(len(book)); errors=np.zeros(len(book),np.int16)
        # Payload first, then fixed namespace symbols; no ground truth used.
        for i in sorted(keep,key=lambda i:(i<3,i)):
            n=len(hits)
            if cost+n>limit: return None,cost,True
            cost+=n; errors+=book[hits,i]!=obs[i]; live=errors<=2
            hits=hits[live]; errors=errors[live]
            if not len(hits): break
    return (int(hits[0]) if len(hits)==1 else None),cost,False

def selftest():
    rng=np.random.default_rng(4480599); checks=0
    for n in (1,2,17,64):
        for _ in range(100):
            book=rng.integers(0,5,(n,13)); book[-1]=book[0] if n>1 and _%5==0 else book[-1]
            obs=book[int(rng.integers(n))].tolist()
            for i in rng.choice(13,4,replace=False): obs[i]=None if i%2 else int(rng.integers(5))
            a,c,_=decode(book,obs,10**9,False); b,d,e=decode(book,obs,10**9,True)
            assert a==b and d<=c and not e
            for prune in (False,True):
                x,w,stop=decode(book,obs,max(0,d-1),prune)
                assert w<=max(0,d-1) and (x is None if stop else x==a)
            checks+=1
    return checks

def run(root,out,split):
    p=runpy.run_path(str(root/'shared-clock.py')); g=p['run'].__globals__
    for f,b in PINS.items(): assert p['blob'](root/f)==b,f
    src=inspect.getsource(p['receive'])
    def patch(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    patch('cap,policy=MODES[mode];',"cap,policy=MODES[mode]; limit=1000000 if mode.endswith('1m') else 10**12;")
    patch('else [1.,scale]', 'else [scale,1.]')
    patch("free=cap-sum(len(q['hs']) for q in groups)","free=cap-sum(sum(not h['done'] for h in q['hs']) for q in groups)")
    patch('scales=list(dict.fromkeys(scales))[:free]',"proposed=list(dict.fromkeys(scales)); scales=proposed[:free]; g['unadmitted']=len(proposed)-len(scales); work['unadmitted']+=g['unadmitted']")
    patch("for z in scales: g['hs'].append(dict(scale=z,start=origin+round(2*S*z),seen=[],done=False,value=None))", "for i,z in enumerate(scales): g['hs'].append(dict(scale=z,start=origin+round(2*S*z),seen=[],done=False,value=None,primary=i==0,exhausted=False,decoder_stop=False))")
    assert src.count("sum(len(g['hs']) for g in groups)")==2
    src=src.replace("sum(len(g['hs']) for g in groups)","sum(sum(not h['done'] for h in g['hs']) for g in groups)")
    patch("                    a=start+round(len(seen)*S*z);", "                    owed=sum(22-len(k['seen']) for q in groups for k in q['hs'] if k['primary'] and not k['done'])+22*max(0,2-work['admitted'])\n                    if work['slots']>=66 or (not h['primary'] and 66-work['slots']<=owed):\n                        h['done']=h['exhausted']=True; work['quota_stops']+=1; break\n                    a=start+round(len(seen)*S*z);")
    patch("groups.append(g); emit('start',g,scales=scales)","groups.append(g); work['admitted']+=1; emit('start',g,scales=scales,unadmitted=g['unadmitted'])")
    patch("work['book_cells']+=len(book)*sum(v is not None for v in body); k=joint(book,body,2)","k,c,stop=decode(book,body,limit-work['book_cells'],mode.startswith('prune')); work['book_cells']+=c; work['decoder_stops']+=int(stop); h['decoder_stop']=stop")
    patch("seen=[h['seen'] for h in g['hs']]);", "seen=[h['seen'] for h in g['hs']],incomplete=any(h['exhausted'] for h in g['hs']),decoder_incomplete=any(h['decoder_stop'] for h in g['hs']),unadmitted=g['unadmitted']);")
    g['MODES']=MODES; env=dict(g,decode=decode); exec(src,env); g['receive']=env['receive']
    g['SEED']={'regression':4480580,'fresh':4480590}[split]
    if split=='fresh':
        g['CASES']=g['CASES']+[(30000,-30000,.55,240,25,18.0),(-30000,30000,1.1,200,-25,17.0),(0,0,1,80,0,None),(0,0,1,80,0,None)]
        runner=inspect.getsource(g['run']); needle='            pcm=np.rint(mix).astype'
        assert runner.count(needle)==1
        runner=runner.replace(needle,"            if ci==12: mix[off+5*S:off+6*S]=0\n            if ci==13: mix=np.clip(mix,-350,350)\n"+needle)
        exec(runner,g)
    g['run'](root,out)
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; stats={}; groups={}
    for r in rows:
        mode=r['mode']; w=r['work']; assert w.get('slots',0)<=66
        if mode.endswith('1m'): assert w.get('book_cells',0)<=1000000
        rel=[e for e in r['events'] if e['kind']=='release']; want=Counter(map(tuple,r['expected'])); got=Counter((e['source'],*e['identity']) for e in rel); assert r['correct']==sum((got&want).values()) and r['wrong']==sum(got.values())-r['correct']
        strict=Counter((e['source'],*e['identity']) for e in rel if not (e['incomplete'] or e['decoder_incomplete'] or e['unadmitted']))
        for key in ('total',str(r['condition'])):
            stats.setdefault(key,{}).setdefault(mode,Counter()).update(expected=len(r['expected']),correct=r['correct'],wrong=r['wrong'],timely=r['by200ms'],strict=sum((strict&want).values()),**{k:w.get(k,0) for k in ('slots','body_products','book_cells','decoder_stops','quota_stops','unadmitted')})
        groups.setdefault((r['pair'],r['condition']),{})[mode]=r
    for a in groups.values():
        assert len({r['pcm_sha256'] for r in a.values()})==1
        assert a['dense']['events']==a['prune']['events']
        assert a['prune']['work'].get('book_cells',0)<=a['dense']['work'].get('book_cells',0)
    if split=='regression':
        prior={(r['pair'],r['condition']):r for r in map(json.loads,(root/'reserved-fresh'/'traces.jsonl').read_text().splitlines()) if r['mode']=='reserve66'}
        for key,a in groups.items():
            r=a['dense']; q=prior[key]; assert r['pcm_sha256']==q['pcm_sha256'] and all(r[k]==q[k] for k in ('correct','wrong','by200ms'))
            assert [{k:v for k,v in e.items() if k not in ('decoder_incomplete','unadmitted')} for e in r['events']]==q['events']
    result=dict(parent=PARENT,pins=PINS,split=split,seed=g['SEED'],selftests=selftest(),rows=len(rows),paired_groups=len(groups),stats=stats,limits='66 body calls and 4 live slots; decoder 1M comparison-cell cap where named. Counts exclude candidate filtering, allocations and detector work; not CPU parity. Strict excludes unadmitted/stopped alternatives. Fresh cases 10/11 load and clock shift, 12 common dropout, 13 clipping; synthetic only.')
    (out/'decoder-budget.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(stats['total'],indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),sys.argv[3])
