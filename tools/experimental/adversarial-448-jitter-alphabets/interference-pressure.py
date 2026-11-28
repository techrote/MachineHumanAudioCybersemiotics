"""Adversarial #448/#449: terminal interference and admitted decoy pressure.
OPENBLAS_NUM_THREADS=1 python interference-pressure.py RUN061_PACKAGE NEW_OUT
Synthetic PCM only; no human evidence or action authorization.
"""
import inspect, json, pathlib, runpy, sys

PARENT='e2bf0cfe93c07c45dab820338c469c19204cbaae'
PIN='670f3120ec8cea51c393b652b048dff53e86a77d'
SEED=4480620
CASES=('clean','tone025','tone050','tone100','tone200','tone400',
       'decoy1','decoy2','decoy3','decoy-only')

def run(root,out):
    stage=runpy.run_path(str(root/'stage-gates.py'))
    h=runpy.run_path(str(root/'gain-boundary.py'))
    assert h['blob'](root/'stage-gates.py')==PIN
    assert h['blob'](root/'gain-boundary.py')==stage['PIN']
    src=inspect.getsource(h['run'])
    def patch(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    patch('    env=dict(d);', '''    needle="    g['MODES']=MODES;"
    assert prefix.count(needle)==1
    prefix=prefix.replace(needle,"    src=src.replace('observe(pcm[a:b],z,True,True)', 'observe(pcm[a:b],z,True,True,seen)'); "+needle.strip())
    env=dict(d);''')
    patch("obs=p['observe_scaled'] if mode in MODES[:2] else lambda x,z,t,f:observe(x,z,t,f,mode=='joint-contrast')", "obs=(lambda x,z,t,f,seen:p['observe_scaled'](x,z,t,f)) if mode in MODES[:2] else lambda x,z,t,f,seen:stage_observe(x,z,seen,mode)")
    patch('lead=S+int(rng.integers(80))','lead=7*S+int(rng.integers(80))')
    patch('            pcm=np.rint(mix).astype', '''            if case.startswith('tone'):
                factor=int(case[4:])/100
                lo,hi=ends[1]-2*S,ends[1]
                t=np.arange(hi-lo)
                mix[lo:hi]+=factor*(900*np.sin(2*np.pi*1100*t/16000)+1100*np.sin(2*np.pi*1200*t/16000))
            if case.startswith('decoy'):
                n=3 if case=='decoy-only' else int(case[-1])
                if case=='decoy-only': mix=np.zeros_like(mix); want=[]; ends=[]
                for di in range(n):
                    cc=np.zeros_like(aa)
                    v['put'](cc,s['preamble']((a+di)%2),lead-(6-2*di)*S)
                    mix+=cc
            assert abs(mix).max()<32767
            pcm=np.rint(mix).astype''')
    patch('rows[i:i+4]', 'rows[i:i+len(MODES)]')
    patch('range(0,len(rows),4)', 'range(0,len(rows),len(MODES))')
    patch('result=dict(parent=PARENT,pins=PINS,', "result=dict(parent=PARENT,pins={**PINS,'stage-gates.py':PIN},")
    env=dict(h,MODES=stage['MODES'],CASES=CASES,SEED=SEED,PARENT=PARENT,PIN=PIN,stage_observe=stage['stage_observe'])
    exec(src,env); env['run'](root,out)
    rows=[json.loads(x) for x in (out/'traces.jsonl').read_text().splitlines()]
    prior=[json.loads(x) for x in (root/'stage-out'/'traces.jsonl').read_text().splitlines()]
    assert not ({tuple(w) for q in rows if q['split']=='fresh' for w in q['expected']} & {tuple(w) for q in prior if q['split']=='fresh' for w in q['expected']})
    summary={}
    for q in rows:
        if q['split']!='fresh': continue
        from collections import Counter
        expected=Counter(map(tuple,q['expected']))
        releases=[e for e in q['events'] if e['kind']=='release']
        got=Counter((e['source'],*e['identity']) for e in releases)
        strict=Counter((e['source'],*e['identity']) for e in releases if not(e['incomplete'] or e['decoder_incomplete'] or e['unadmitted']))
        assert q['correct']==sum((expected&got).values()) and q['wrong']==sum(got.values())-q['correct'] and q['strict']==sum((expected&strict).values())
        a=summary.setdefault(q['case'],{}).setdefault(q['mode'],Counter())
        a.update(expected=len(q['expected']),correct=q['correct'],strict=q['strict'],wrong=q['wrong'],timely=q['timely'],starts=q['starts'],early_starts=sum(e['kind']=='start' and e['sample']<7*1280 for e in q['events']),refused=sum(e['kind']=='refused' for e in q['events']),slots=q['work'].get('slots',0),cells=q['work'].get('book_cells',0))
    (out/'pressure-summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
