"""Adversarial #448/#449: matched body-call ceilings and primary reservations.
Usage: OPENBLAS_NUM_THREADS=1 python reserved-clock.py PINNED_PACKAGE NEW_OUT regression|fresh
AI-assisted synthetic PCM experiment; no action authorization or human evidence.
"""
import inspect,json,pathlib,runpy,sys
from collections import Counter
PARENT='8f53505b1a9eb9f3143f55897c8324ac2c4eefcc'
PINS={'adaptive-clock.py':'1f7fe14570611075bf12b15c1d766462dd995a99','shared-clock.py':'5876b059f8f6789d61e3fe7821f2a326eb170772'}
MODES={f'{p}{b}':(4,'finefirst') for b in (48,66) for p in ('greedy','reserve')}
def run(root,out,split):
    p=runpy.run_path(str(root/'shared-clock.py')); g=p['run'].__globals__
    for f,b in PINS.items(): assert p['blob'](root/f)==b,f
    src=inspect.getsource(p['receive'])
    def patch(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    patch('cap,policy=MODES[mode];', "cap,policy=MODES[mode]; budget=int(mode[-2:]); reserve=mode.startswith('reserve');")
    patch('else [1.,scale]', 'else [scale,1.]')
    patch("free=cap-sum(len(q['hs']) for q in groups)","free=cap-sum(sum(not h['done'] for h in q['hs']) for q in groups)")
    patch("for z in scales: g['hs'].append(dict(scale=z,start=origin+round(2*S*z),seen=[],done=False,value=None))", "for i,z in enumerate(scales): g['hs'].append(dict(scale=z,start=origin+round(2*S*z),seen=[],done=False,value=None,primary=i==0,exhausted=False))")
    assert src.count("sum(len(g['hs']) for g in groups)")==2
    src=src.replace("sum(len(g['hs']) for g in groups)","sum(sum(not h['done'] for h in g['hs']) for g in groups)")
    patch("                    a=start+round(len(seen)*S*z);", "                    owed=sum(22-len(k['seen']) for q in groups for k in q['hs'] if k['primary'] and not k['done'])\n                    owed+=22*max(0,2-work['admitted'])\n                    if work['slots']>=budget or (reserve and not h['primary'] and budget-work['slots']<=owed):\n                        h['done']=h['exhausted']=True; work['quota_stops']+=1; work['primary_stops']+=int(h['primary']); break\n                    a=start+round(len(seen)*S*z);")
    patch("groups.append(g); emit('start',g,scales=scales)","groups.append(g); work['admitted']+=1; emit('start',g,scales=scales)")
    patch("seen=[h['seen'] for h in g['hs']]);", "seen=[h['seen'] for h in g['hs']],incomplete=any(h['exhausted'] for h in g['hs']));")
    g['MODES']=MODES; env=dict(g); exec(src,env); g['receive']=env['receive']
    g['SEED']={'fresh':4480580,'regression':4480570}[split]; g['run'](root,out)
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; prior=[json.loads(s) for s in (root/'fresh'/'traces.jsonl').read_text().splitlines()]
    old={(r['pair'],r['condition']):r for r in prior if r['mode']=='quota4'}
    ids={tuple(w) for r in rows for w in r['expected']}; oldids={tuple(w) for r in prior for w in r['expected']}; stats={}; witnesses=[]
    for r in rows:
        assert r['work'].get('slots',0)<=int(r['mode'][-2:])
        releases=[e for e in r['events'] if e['kind']=='release']; got=Counter((e['source'],*e['identity']) for e in releases); want=Counter(map(tuple,r['expected'])); assert r['correct']==sum((got&want).values()); assert r['wrong']==sum(got.values())-r['correct']
        strict=Counter((e['source'],*e['identity']) for e in releases if not e['incomplete']); n=sum((strict&want).values())
        for key in ('total',str(r['condition'])):
            stats.setdefault(key,{}).setdefault(r['mode'],Counter()).update(correct=r['correct'],wrong=r['wrong'],expected=len(r['expected']),timely=r['by200ms'],strict_correct=n,strict_wrong=sum(strict.values())-n,incomplete_releases=sum(e['incomplete'] for e in releases),**{k:r['work'].get(k,0) for k in ('slots','body_products','book_cells','quota_stops','primary_stops')})
        if split=='regression':
            q=old[r['pair'],r['condition']]; assert r['pcm_sha256']==q['pcm_sha256']
            if r['mode']=='greedy48':
                assert all(r[k]==q[k] for k in ('correct','wrong','by200ms'))
                assert [{k:v for k,v in e.items() if k!='incomplete'} for e in r['events']]==q['events']
        if r['pair']==0 and r['condition']==1: witnesses.append(r)
    if split=='fresh': assert not ids&oldids
    receipt=json.loads((out/'receipt.json').read_text())
    result=dict(parent=PARENT,pins=PINS,split=split,seed=g['SEED'],identities=len(ids),prior_overlap=len(ids&oldids),rows=len(rows),prefix_checks=receipt['prefix_checks'],stats=stats,witnesses=witnesses,limits='Reserve two primary paths, 22 calls each. Fine-first; stop alternatives rather than defer. Strict view withholds incomplete releases. Matched body-call ceilings only; detector and decoder work separate. Offline PCM, no human evidence.')
    (out/'reservation.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(stats['total'],indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),sys.argv[3])
