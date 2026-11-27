"""Adversarial #448/#449: exploratory liveness windows on synthetic PCM.
OPENBLAS_NUM_THREADS=1 python staged-liveness.py RUN063_PACKAGE NEW_OUT
No human, physical or action-authorization evidence.
"""
import inspect, json, pathlib, runpy, sys
PARENT='a3b3ade63e8b22672bd50beddacf3fb355fd3cad'
PIN='394b254cf07c6f61a56c3e72d94d7b98b4a05814'
SEED=4480640
MODES=('baseline','silence3','silence5','gap5','staged5_3')
CASES=('clean','decoy2','decoy3','erase3','erase5','gap3','decoy-valid-prefix','decoy-erase3','noise-only')

def reject(seen,mode):
    if mode=='baseline': return False
    if mode in ('silence3','silence5'):
        return len(seen)==int(mode[-1]) and all(x is None for x in seen)
    # A longer acquisition grace window; after positive evidence, a shorter
    # rolling inactivity deadline. Neither criterion proves impossibility.
    limit=3 if mode=='staged5_3' and any(x is not None for x in seen) else 5
    return len(seen)>=limit and all(x is None for x in seen[-limit:])

def main(root,out):
    p=runpy.run_path(str(root/'provisional-admission.py'))
    assert runpy.run_path(str(root/'shared-clock.py'))['blob'](root/'provisional-admission.py')==PIN
    src=inspect.getsource(p['run'])
    def patch(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    patch("root/'pressure-out'/'traces.jsonl'", "root/'admission-out'/'traces.jsonl'")
    patch("q['mode']=='all-hybrid'", "q['mode']=='baseline'")
    patch("root/'pressure-out'/f", "root/'admission-out'/f")
    patch('lead=7*S+', 'lead=16*S+')
    patch('np.zeros(48*S,np.int32)', 'np.zeros(58*S,np.int32)')
    patch("if case=='erase3': aa[lead+2*S:lead+5*S]=0", "if case in ('erase3','decoy-erase3'): aa[lead+2*S:lead+5*S]=0\n            if case=='erase5': aa[lead+2*S:lead+7*S]=0\n            if case=='gap3': aa[lead+7*S:lead+10*S]=0")
    patch("v['put'](cc,z,lead-(6-2*di)*S); aa+=cc", "at=lead-((14-7*di) if case=='decoy-valid-prefix' else (6-2*di))*S\n                    v['put'](cc,z,at); assert not np.any(cc[lead:]); aa+=cc")
    # Replace predecessor-specific prefix-rule enumeration with known answers.
    a=src.index('    # Exhaustive prefix-rule'); b=src.index('    assert len({tuple(x)',a)
    src=src[:a]+'''    tests=0
    for n in range(1,23):
        for mode in MODES:
            assert reject([None]*n,mode)==(False if mode=='baseline' else n==int(mode[-1]) if mode.startswith('silence') else n>=5)
            assert not reject([0]*n,mode)
            tests+=2
    assert reject([0,None,None,None],'staged5_3')
    assert not reject([0,None,None,None],'gap5')
    tests+=2
'''+src[b:]
    env=dict(p,PARENT=PARENT,PIN=p['PIN'],SEED=SEED,MODES=MODES,CASES=CASES,reject=reject)
    exec(src,env); env['run'](root,out)
    rows=[json.loads(x) for x in (out/'traces.jsonl').read_text().splitlines()]
    old={(q['case'],q['mode']):q for q in map(json.loads,(root/'admission-out'/'traces.jsonl').read_text().splitlines()) if q['split']=='fresh' and q['pair']==0}
    checked=0
    for q in rows:
        if q['split']=='retained' and q['mode'] in ('baseline','silence3'):
            prev=old[q['case'],q['mode']]
            assert q['pcm_sha256']==prev['pcm_sha256'] and q['events']==prev['events']
            checked+=1
    assert checked==16
    f=out/'receipt.json'; r=json.loads(f.read_text())
    r.update(parent_blob=PIN,interference_ancestor_blob=p['PIN'],retained_event_checks=checked,limits='Heuristic inactivity stops annotated incomplete; not impossibility proofs. Matched local ceilings, not CPU parity. Synthetic PCM only; no human evidence. Valid-prefix decoys have no emitted overlap with legitimate waveforms, but stale receiver interpretations may consume later legitimate evidence.')
    f.write_text(json.dumps(r,indent=2)+'\n')

if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
