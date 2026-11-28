"""Adversarial #448/#449: clock-order and work quota sensitivity, synthetic PCM.
Usage: python adaptive-clock.py PINNED_PACKAGE NEW_OUTPUT_DIR [regression|fresh]
"""
import hashlib,inspect,json,pathlib,runpy,sys
from collections import Counter
PARENT='fd1357140d0059c93c12bfb33c5e79b8a64dae63'
BLOB='5876b059f8f6789d61e3fe7821f2a326eb170772'
NEW={'finefirst2':(2,'finefirst'),'finefirst4':(4,'finefirst'),'reclaim4':(4,'finefirst'),'quota4':(4,'finefirst')}
def run(root,out,split):
    raw=(root/'shared-clock.py').read_bytes()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==BLOB
    p=runpy.run_path(str(root/'shared-clock.py')); g=p['run'].__globals__; src=inspect.getsource(p['receive'])
    def change(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    change('else [1.,scale]','else [scale,1.] if policy=="finefirst" else [1.,scale]')
    change("free=cap-sum(len(q['hs']) for q in groups)","free=cap-sum(sum(not h['done'] for h in q['hs']) if mode in ('reclaim4','quota4') else len(q['hs']) for q in groups)")
    change("work['peak']=max(work['peak'],sum(len(g['hs']) for g in groups))","work['peak']=max(work['peak'],sum(sum(not h['done'] for h in g['hs']) if mode in ('reclaim4','quota4') else len(g['hs']) for g in groups))")
    change("                    a=start+round(len(seen)*S*z);", "                    if mode=='quota4' and work['slots']>=48:\n                        h['done']=True; work['quota_stops']+=1; break\n                    a=start+round(len(seen)*S*z);")
    change("assert sum(len(g['hs']) for g in groups)<=cap", "assert sum(sum(not h['done'] for h in g['hs']) if mode in ('reclaim4','quota4') else len(g['hs']) for g in groups)<=cap")
    g['MODES']={k:v for k,v in p['MODES'].items() if k!='fine4'}; g['MODES'].update(NEW)
    env=dict(g); exec(src,env); g['receive']=env['receive']
    if split=='fresh': g['SEED']=4480570
    elif split!='regression': raise ValueError(split)
    g['run'](root,out)
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]
    receipt=json.loads((out/'receipt.json').read_text())
    baseline=[json.loads(s) for s in (root/'shared1'/'traces.jsonl').read_text().splitlines()]
    prior={(r['pair'],r['condition'],r['mode']):r for r in baseline}
    ids={tuple(w) for r in rows for w in r['expected']}; oldids={tuple(w) for r in baseline for w in r['expected']}
    if split=='regression':
        for r in rows:
            if r['mode'] not in NEW: assert r==prior[r['pair'],r['condition'],r['mode']]
    else: assert not ids&oldids,ids&oldids
    for r in rows:
        rel=[e for e in r['events'] if e['kind']=='release']; got=Counter((e['source'],*e['identity']) for e in rel)
        assert r['correct']==sum((got&Counter(map(tuple,r['expected']))).values())
        assert r['wrong']==sum(got.values())-r['correct']
        if r['mode']=='quota4': assert r['work'].get('slots',0)<=48
    info=dict(parent=PARENT,parent_blob=BLOB,wrapper_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),split=split,seed=g['SEED'],identities=len(ids),overlap=len(ids&oldids),recounts=len(rows),baseline_equivalences=sum(r['mode'] not in NEW for r in rows) if split=='regression' else 0,stats=receipt['stats'],prefix_checks=receipt['prefix_checks'],limits='Quota counts body observation calls only; detector and book work separate. Reclaim frees live processing slots, not stored completed histories. Quota-stop is treated as no value; could conceal conflict. No action or human evidence.')
    (out/'adaptive.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),sys.argv[3] if len(sys.argv)>3 else 'fresh')
