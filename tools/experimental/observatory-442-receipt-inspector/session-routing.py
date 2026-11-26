"""Refs #442 / Draft #443. Synthetic session scheduling, not acoustic transport.
python session-routing.py PINNED_PARENT_DIR NEW_OUTPUT_DIR
No human evidence, authentication or action authority. One GPT-6.2 agent.
"""
import hashlib, itertools, json, pathlib, sys
from collections import defaultdict
PIN='5f5bae43f73479e0ee73634fd94386a1edcb020d'
GRAMMAR='33228efc8363a0814a36ebfd175ecfef9920e364'
PARENT_BLOB='a6204c17eeefdc23bb9ee69f51b83c821abaa0c8'
MODES=('full','eager-once','hint-once','hint-retry','budget-retry')
CONDS=('stable','initial-mismatch','sender-change','receiver-change','temporary-mismatch','first-setup-fault')
HINTS=('short','exact','long')
BUDGETS=(80,120,180,240,320)
sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def full(l):return 14+l
def cached(l):return 20+(l==18)
def environment(n,c,t):
    k=n//2
    return (not (c=='initial-mismatch' or (c in ('sender-change','receiver-change') and t>=k) or (c=='temporary-mismatch' and t<k)),c=='receiver-change' and t==k,c=='first-setup-fault')
def route(n,l,c,h,mode,budget):
    # Horizon is an exogenous simulated hint; actual n is only used by the environment.
    forecast={'short':max(1,n-2),'exact':n,'long':n+2}[h]
    active=False;attempts=0;next_try=0;spent=0;rows=[]
    for t in range(n):
        match,local_change,first_fault=environment(n,c,t)
        if local_change:active=False
        setup=False;reason='full';parts=[]
        if active and not match:
            parts.append(17);active=False;next_try=t+2;reason='negative-full'
        elif active:reason='cached'
        else:
            worthwhile=max(0,forecast-t)*(full(l)-cached(l))>24
            setup=(mode=='eager-once' and attempts==0 or mode=='hint-once' and attempts==0 and worthwhile or mode in ('hint-retry','budget-retry') and t>=next_try and worthwhile)
            if mode=='budget-retry' and budget-spent<24+full(l):setup=False
            if setup:
                parts.append(24);attempts+=1;active=match and not(first_fault and attempts==1);next_try=t+2
                reason='setup-cached' if active else 'setup-full'
        parts.append(cached(l) if active else full(l));cost=sum(parts)
        # No partially emitted exchange claimed: this is a completed-prefix slot ledger.
        row=dict(turn=t,forecast_remaining=max(0,forecast-t),local_change=local_change,route=reason,setup=setup,parts=parts,slots=cost,match=match,cache_after=active,complete=spent+cost<=budget)
        rows.append(row)
        if not row['complete']:break
        spent+=cost
    return dict(turns=n,length=l,condition=c,hint=h,mode=mode,budget=budget,completed=sum(r['complete'] for r in rows),spent=spent,attempts=sum(r['setup'] and r['complete'] for r in rows),trace=rows)
def check_parent(root):
    if blob((root/'session-cost-audit.py').read_bytes())!=PARENT_BLOB:raise ValueError('parent source identity')
    p=root/'session1';m=json.loads((p/'manifest.json').read_text());expected={'receipt.json','cases.json','index.html'}
    if set(m)!=expected or any(sha((p/f).read_bytes())!=v for f,v in m.items()):raise ValueError('parent manifest mismatch')
    receipt=json.loads((p/'receipt.json').read_text());assert receipt['pin']==GRAMMAR
    rows=json.loads((p/'cases.json').read_text());assert len(rows)==800
    audited=0
    for r in rows:
        tr=r['trace'];assert r['slots']==sum(sum(x['frames']) for x in tr)==sum(x['slots'] for x in tr)
        assert r['correct']==sum(x['status']=='correct' for x in tr) and r['wrong']==sum(x['status']=='wrong' for x in tr)
        if r['mode'] not in ('full','guarded8'):continue
        c={'clean':'stable','initial-shift':'initial-mismatch','sender-change':'sender-change','receiver-change':'receiver-change'}.get(r['condition'])
        if c is None or c.endswith('change') and r['change']!=r['turns']//2:continue
        a=route(r['turns'],r['length'],c,'exact','full' if r['mode']=='full' else 'eager-once',10000)
        assert [x['slots'] for x in a['trace']]==[x['slots'] for x in tr],(r,a)
        audited+=1
    return audited,m

def run(root,out):
    checked,inputs=check_parent(root);cases=[];summary=defaultdict(lambda:[0,0,0,0])
    for n,l,c,h,b in itertools.product(range(2,9),(13,18),CONDS,HINTS,BUDGETS):
        group=[route(n,l,c,h,m,b) for m in MODES];cases.extend(group)
        for r in group:
            tr=r['trace'];done=[x for x in tr if x['complete']];assert r['completed']==len(done) and r['spent']==sum(x['slots'] for x in done)<=b
            assert all(not x['cache_after'] or x['match'] for x in done)
            assert all(x['slots']==sum(x['parts']) for x in tr)
            assert len(tr)==len(done) or not tr[-1]['complete'] and r['spent']+tr[-1]['slots']>b
            if r['mode']=='full':assert r['completed']==min(n,b//full(l))
            k='|'.join((c,h,str(b),r['mode']));s=summary[k];s[0]+=r['completed'];s[1]+=n;s[2]+=r['spent'];s[3]+=r['attempts']
    # Known answers: stable amortization, hidden vs visible revocation, retry after failed setup, budget guard.
    assert route(8,13,'stable','exact','eager-once',1000)['spent']==184
    assert route(8,13,'sender-change','exact','eager-once',1000)['spent']==229
    assert route(8,13,'receiver-change','exact','eager-once',1000)['spent']==212
    assert route(8,13,'first-setup-fault','exact','hint-retry',1000)['attempts']==2
    assert route(8,13,'stable','exact','budget-retry',40)['completed']==1
    out.mkdir();(out/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n',encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    receipt=dict(schema='mhac-session-routing-v1',parent=PIN,grammar=GRAMMAR,parent_blob=PARENT_BLOB,parent_manifest=inputs,source_sha256=sha(pathlib.Path(__file__).read_bytes()),cases=len(cases),parent_ledgers_recounted=800,parent_route_equivalence=checked,turn_records=sum(len(r['trace']) for r in cases),groups=len(cases)//len(MODES),conditions=CONDS,hints=HINTS,budgets=BUDGETS,limits='Finite deterministic symbolic simulation; 80 ms slots, full bodies assumed always correct, guarded agreement assumed exact, no PCM, authentication, action authority or human evidence. Setup failure costs full 24 slots, retries after two turns, negative sender revocation costs 17; these are modeled costs, not new Grammar implementations. Horizon hints are constructed from true length for sensitivity, not learned forecasts. No partial exchange airtime, processing, turnaround or physical acquisition; completed-prefix deadline accounting only.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Session routing</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:1em}table{border-collapse:collapse;width:100%}td,th{padding:.5em;border:1px solid #888;text-align:left}label{display:inline-block;margin:.4em}pre{white-space:pre-wrap}</style><h1>Session routing: completed-prefix budget audit</h1><p>Synthetic symbolic model, not acoustic transport. 80 ms per slot. Full bodies and guarded agreement assumed correct. Forecasts are constructed, not measured.</p><label>Condition <select id="c"></select></label><label>Horizon hint <select id="h"></select></label><label>Budget (slots) <select id="b"></select></label><div id="t"></div><p>Totals across 14 sessions (2–8 turns, two body lengths). No partial frame airtime included. <a href="cases.json">Replay traces</a> · <a href="receipt.json">Receipt</a></p><script>const data=DATA, modes=MODES, $=id=>document.getElementById(id);for(const [id,vals] of Object.entries(OPTIONS))for(const v of vals)$(id).add(new Option(v,v));function draw(){$('t').innerHTML='<table><tr><th>Policy</th><th>Completed / requested</th><th>Completed slots</th><th>Completed setups</th></tr>'+modes.map(m=>{let r=data[[$('c').value,$('h').value,$('b').value,m].join('|')];return '<tr><td>'+m+'</td><td>'+r[0]+'/'+r[1]+'</td><td>'+r[2]+'</td><td>'+r[3]+'</td></tr>'}).join('')+'</table>'}for(const id of ['c','h','b'])$(id).onchange=draw;draw();</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(summary)).replace('MODES',json.dumps(MODES)).replace('OPTIONS',json.dumps(dict(c=CONDS,h=HINTS,b=BUDGETS))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
