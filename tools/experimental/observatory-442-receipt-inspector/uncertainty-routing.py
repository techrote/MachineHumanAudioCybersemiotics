"""Refs #442 / #443. Frozen synthetic clarification replay, not a new PCM trial.
Usage: python uncertainty-routing.py COVERAGE_DIR CLARIFICATION_DIR NEW_OUTPUT_DIR
Standard library only. Prior aligned reply payload costs exclude framing and queries.
"""
import hashlib, json, pathlib, sys
from collections import Counter, defaultdict

PINS = {'coverage':'185738e06eae9cd36a8bbbac533027e478c6c3a3','clarification':'0dfce1da3df5d9713b94a148e708a2889bade381','framed_reference':'feba52809552355db1beb33a36dd7fdd619b2e0f'}
HASHES = {'coverage':('fa977026f70ad01096537da03213ba184095e76a11fc47c550254e72608611f6','c7aa523e0b7ed351c1bb67531755a91af982e8c5165831049fdce346438dc054'),'clarification':('c1720723f88f97042f93ed1decebfad32e1be7357d44cedbc4828e5a46cf74e4','996b8a8805786c1de5b1a142f7ea8d5a8ae46b57d70b1cd91f8c4c3be697b8e9')}
POLICIES = ('query-only','empty','singleton-signal','all-singletons','all-multiple','signal-or-multiple','full-always')
def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok, msg):
    if not ok: raise ValueError(msg)
def read(root, name):
    receipt, trace = [(root/f).read_bytes() for f in ('receipt.json','traces.jsonl')]
    require((sha(receipt),sha(trace))==HASHES[name],name+' frozen hash mismatch')
    return [json.loads(line) for line in trace.splitlines()]
def route(policy,n,dual):
    # No target, gain, fault condition, or future reply observation is available here.
    return {'query-only':False,'empty':n==0,'singleton-signal':n==0 or (n==1 and dual>0),'all-singletons':n<=1,'all-multiple':n!=1,'signal-or-multiple':n!=1 or dual>0,'full-always':True}[policy]
def outcome(returned,target):
    return 'correct' if returned==[target] else 'wrong-singleton' if len(returned)==1 else 'retained' if target in returned else 'wrong-set' if returned else 'withheld'
def measure(coverage,audit):
    cases={}; controls=Counter(); grouped=defaultdict(dict)
    for r in coverage:
        key=(r['mode'],r['pcm_sha256']); require(key not in cases,'duplicate initial observation')
        events=[e for e in r['events'] if e['kind'] in ('candidate','reject')]
        require(len(events)==1,'unexpected body event count')
        seen=events[0]['seen'][:r['length']]; require(len(seen)==r['length'],'body length')
        dual=sum(isinstance(v,list) and len(v)>1 for v in seen)
        cases[key]=(r,dual)
        if r['gain']==0:
            for p in POLICIES: controls[(r['mode'],p)]+=int(route(p,len(r['report']['ids']),dual))
    for r in audit:
        key=(r['input_mode'],r['input_pcm'],r['target'],r['condition'])
        require(r['policy'] not in grouped[key],'duplicate clarification comparator')
        grouped[key][r['policy']]=r
    rows=[]; totals=defaultdict(Counter); baseline=defaultdict(lambda:[0,0,0,0])
    for key,comparators in sorted(grouped.items()):
        mode,pcm,target,condition=key; a,dual=cases[(mode,pcm)]; n=len(a['report']['ids'])
        require(set(comparators)=={'query-only','fallback-on-empty','full-always'},'missing comparator')
        q,f=map(comparators.get,('query-only','full-always'))
        require(target in a['expected'] and a['gain']!=0,'unexpected target')
        for r in comparators.values():
            require(r['initial']==a['report']['ids'] and r['length']==a['length'] and r['source']==a['source'],'cross-trace mismatch')
            require(r['status']==outcome(r['returned'],target),'outcome mismatch')
            require(r['full_pcm']==f['full_pcm'] and r['full_observed']==f['full_observed'],'full observation mismatch')
        require(q['reply_slots']==(5 if n>1 else 0) and f['reply_slots']==a['length'],'payload cost mismatch')
        require(set(q['returned'])<=set(q['initial']),'query escaped initial set')
        # Same observed initial state routes both hypothetical target assignments and all reply faults.
        for p in POLICIES:
            full=route(p,n,dual); selected=f if full else q; st=outcome(selected['returned'],target)
            k=(mode,condition,p); totals[k].update({st:1,'slots':selected['reply_slots'],'full':int(full),'trials':1,'omitted':int(target not in q['initial'])})
            rows.append(dict(mode=mode,pcm=pcm,target=target,condition=condition,policy=p,source=a['source'],length=a['length'],pair=a['pair'],kind=a['kind'],gain=a['gain'],initial=q['initial'],dual=dual,full=full,returned=selected['returned'],status=st,slots=selected['reply_slots'],reply_pcm=selected['full_pcm'] if full else selected['query_pcm']))
        # Cost-matched uniform singleton verification within each length stratum.
        # Expected values over random selection, not an executed random policy or probability of intent.
        if n==1:
            b=baseline[(mode,condition,a['length'])]; b[0]+=1; b[1]+=int(dual>0); b[2]+=int(q['status']=='correct'); b[3]+=int(f['status']=='correct')-int(q['status']=='correct')
    require(len(cases)==432 and len(grouped)==2160 and len(rows)==15120,'unexpected corpus dimensions')
    expected={}
    for (mode,condition,length),(n,k,correct,delta) in baseline.items():
        z=expected.setdefault(mode+':'+condition,{'singleton_trials':0,'full_slots':0,'expected_correct_singletons':0.0})
        z['singleton_trials']+=n; z['full_slots']+=k*length; z['expected_correct_singletons']+=correct+k*delta/n
    summary=[dict(mode=m,condition=c,policy=p,**dict(totals[m,c,p])) for m,c,p in sorted(totals)]
    return rows,summary,expected,[dict(mode=m,policy=p,full=n) for (m,p),n in sorted(controls.items())]
def main(coverage,clarification,out):
    rows,summary,expected,controls=measure(read(coverage,'coverage'),read(clarification,'clarification'))
    out.mkdir(parents=True,exist_ok=False)
    receipt=dict(schema='mhac.uncertainty-routing/1',pins=PINS,input_hashes=HASHES,source_sha256=sha(pathlib.Path(__file__).read_bytes()),trials=len(rows),summary=summary,matched_singleton_baseline=expected,single_message_controls=controls,limits='Retrospective policy replay of aligned payload observations; no fresh PCM, no acquisition, query framing or turnaround cost. Fixed policies, not calibrated confidence. Hypothetical target assignments equally enumerated, not human intent. Framed reference pin is contextual only; its costs/results are not used. Controls measure routing only, not retransmission outcomes.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    # All detailed rows available offline with no fetch or network dependency.
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Uncertainty routing</title><style>body{font:16px system-ui;max-width:1050px;margin:auto;padding:1em}td,th{padding:.45em;border-bottom:1px solid #aaa;text-align:right}td:first-child{text-align:left}pre{white-space:pre-wrap}select{max-width:100%}</style><h1>Uncertainty-conditioned clarification replay</h1><p>Frozen synthetic target assignments, not human evidence. Payload only; no query, acquisition or turnaround costs. Routing sees candidate count and dual-symbol count, never the target or future fault.</p><label>Receiver <select id="m"></select></label> <label>Reply fault <select id="c"></select></label><table id="t"></table><p id="b"></p><label>Policy <select id="p"></select></label> <label>Trace <select id="r"></select></label><pre id="d"></pre><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps(rows,separators=(',',':'))+''',s='''+json.dumps(summary)+''',b='''+json.dumps(expected)+''';const [m,c,t,p,r,d]=['m','c','t','p','r','d'].map(x=>document.getElementById(x));for(const [el,k] of [[m,'mode'],[c,'condition'],[p,'policy']])for(const v of new Set(s.map(x=>x[k])))el.add(new Option(v,v));let a=[];function detail(){d.textContent=JSON.stringify(a[+r.value],null,2)}function draw(){t.innerHTML='<tr><th>Policy</th><th>Correct</th><th>Wrong</th><th>Other</th><th>Full</th><th>Mean payload ms</th></tr>'+s.filter(x=>x.mode===m.value&&x.condition===c.value).map(x=>'<tr>'+[x.policy,x.correct||0,(x['wrong-singleton']||0)+(x['wrong-set']||0),x.trials-(x.correct||0)-(x['wrong-singleton']||0)-(x['wrong-set']||0),x.full,(80*x.slots/x.trials).toFixed(1)].map(y=>'<td>'+y+'</td>').join('')+'</tr>').join('');document.getElementById('b').textContent='Cost-matched uniform singleton baseline: '+JSON.stringify(b[m.value+':'+c.value]);a=rows.filter(x=>x.mode===m.value&&x.condition===c.value&&x.policy===p.value);r.replaceChildren();a.forEach((x,i)=>r.add(new Option(x.kind+' / '+x.gain+' / '+x.target,i)));detail()}m.onchange=c.onchange=p.onchange=draw;r.onchange=detail;draw()</script>''',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'trials':len(rows),'summary':summary,'matched_singleton_baseline':expected,'controls':controls}))
def selftest(coverage,clarification):
    import copy
    a,b=read(coverage,'coverage'),read(clarification,'clarification')
    rows,summary,expected,controls=measure(a,b)
    ix={(r['mode'],r['condition'],r['policy']):r for r in summary}
    for condition in ('clean','noise2500','two-substitutions'):
        r=ix['list-radius2',condition,'signal-or-multiple']; require((r['correct'],r['wrong-singleton'],r['slots'])==(234,6,3564),'known answer')
        require(ix['list-radius2',condition,'full-always']['correct']==240,'full comparator')
    require(expected['list-radius2:clean']['expected_correct_singletons']==32,'random baseline')
    require(all(r['full']==0 for r in controls if r['policy']=='singleton-signal'),'control routing')
    require(not route('singleton-signal',1,0) and route('singleton-signal',1,1),'route boundary')
    for field,value in [('status','invented'),('initial',[-999]),('reply_slots',-1)]:
        bad=copy.deepcopy(b); bad[0][field]=value
        try: measure(a,bad)
        except ValueError: pass
        else: raise RuntimeError('accepted tampered '+field)
    print('Known-answer, route/control and three tamper tests PASS')
if __name__=='__main__':
    if sys.argv[1]=='--test': selftest(*map(pathlib.Path,sys.argv[2:]))
    else: main(*map(pathlib.Path,sys.argv[1:]))
