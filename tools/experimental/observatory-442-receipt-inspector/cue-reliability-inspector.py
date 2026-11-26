"""Measurement #442 / synthetic-only. python cue-reliability-inspector.py ROOT OUT
Independent receipt audit and reliability sensitivity, not human evidence.
"""
import collections, hashlib, json, pathlib, shutil, sys, wave
PIN='abb0324c2b112dacc161c14ff6ce237516ed3236'
GRAMMAR='aca863378e825b26921388cfaab890f9eac86279'
BLOBS={'cue-binding-audit.py':'bea7c2f1f257916efdb130aae5a23b4f420ae704','asynchronous-attribution.py':'134b56746da67eca0e0f7ff9da9b2b4740c5bc8b','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','temporal-admission.py':'6a2821c9c4453c1f462da279f439aa8fb601e3ed'}
RECEIPT='12d2ecaf4891b8579817e3274d132e261af7a761ac1b556bd67747bd7f435556'
def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def reason(row,name):
    d=row['decisions'][name]; p=row['primary']; s=row['secondary']
    if p is None and name!='blind-fallback': return 'missing-cue'
    if name=='corroborated' and p!=s: return 'cue-disagreement'
    grids=[(v,v) for v in (-20,-10,0,10,20,30,40)]+[(c-d/2,c+d/2) for c in (-10,10,30) for d in (-40,40)]
    if p is not None and not any(max(abs(a-b) for a,b in zip(p,g))<=(30 if name=='wide-union' else 20) for g in grids): return 'no-grid'
    return 'acoustic-empty' if d['count']==0 else d['outcome']
def audit(r):
    totals=collections.Counter(); rows=r['rows']; policies=r['policies']; faults=r['faults']; hashes=set(); paircounts=collections.Counter()
    require(len(rows)==1728 and len(r['pairs'])==24,'corpus size')
    for k in range(0,len(rows),12):
        block=rows[k:k+12]; require(len({x['pcm_sha256'] for x in block})==1,'PCM pairing'); hashes.add(block[0]['pcm_sha256'])
        for f in faults:
            a,b=[x for x in block if x['fault']==f]; require(a['role']=='A' and b['role']=='B' and a['target']==b['rival'] and b['target']==a['rival'],'role pairing')
            for n in policies:
                paircounts[f,n, str(a['decisions'][n]['outcome']=='correct')+'/'+str(b['decisions'][n]['outcome']=='correct')]+=1
        for row in block:
            for n in policies:
                d=row['decisions'][n]; count=d['count']; unique=d['unique']; status='empty' if not count else 'ambiguous' if count>1 else 'correct' if unique==row['target'] else 'wrong'
                require(status==d['outcome'] and (unique is not None)==(count==1),'decision semantics')
                if count==1: require(d['target_retained']==(unique==row['target']) and d['rival_retained']==(unique==row['rival']),'unique retention')
                if count==0: require(not d['target_retained'] and not d['rival_retained'],'empty retention')
                why=reason(row,n); require(why==status or status=='empty','gate inconsistency'); d['reason']=why
                totals[row['fault'],n,why]+=1; totals[row['fault'],n,'original-'+status]+=1; totals[row['fault'],n,'rival_wrong']+=unique==row['rival']
        for s in (0,1):
            for n in policies:
                if n!='corroborated': require(block[s+2]['decisions'][n]['unique']==block[1-s]['decisions'][n]['unique'],'swapped singleton')
                require(block[s+10]['decisions'][n]['unique']==block[1-s]['decisions'][n]['unique'],'common swap singleton')
    require(len(hashes)==144,'distinct PCM hashes')
    categories=('correct','wrong','ambiguous','missing-cue','cue-disagreement','no-grid','acoustic-empty')
    summary={f:{n:{s:totals[f,n,s] for s in categories} for n in policies} for f in faults}
    for f in faults:
        for n in policies:
            for s in ('correct','wrong','ambiguous','empty','rival_wrong'):
                require(totals[f,n,s if s=='rival_wrong' else 'original-'+s]==r['summary'][f][n][s],'summary recount')
            require(sum(summary[f][n].values())==288,'partition')
    paired={f:{n:{s:paircounts[f,n,s] for s in ('True/True','True/False','False/True','False/False')} for n in policies} for f in faults}
    return summary,paired

def risk(summary,p,q):
    require(0<=p<=1 and 0<=q<=1,'probability range')
    weights={'clean':1-p,'swap':p*(1-q),'both-swapped':p*q}
    result={}
    for n in summary['clean']:
        c,w=[sum(weights[f]*summary[f][n][k]/288 for f in weights) for k in ('correct','wrong')]
        result[n]=dict(correct=c,wrong=w,withheld=max(0,1-c-w),wrong_given_release=w/(c+w) if c+w else None)
    return result

def main(root,out):
    for n,h in BLOBS.items():
        b=(root/n).read_bytes(); require(hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h,n)
    raw=(root/'cue1/receipt.json').read_bytes(); require(sha(raw)==RECEIPT,'input digest'); r=json.loads(raw)
    require(sha((root/'async1/receipt.json').read_bytes())==r['prior_sha256'],'prior digest')
    summary,paired=audit(r)
    for s in r['specimens']:
        with wave.open(str(root/'cue1'/s['file']),'rb') as w: require(sha(w.readframes(w.getnframes()))==s['pcm_sha256'],'WAV payload')
    out.mkdir(parents=True,exist_ok=False)
    result=dict(schema='mhac-cue-reliability-v1',source_ref=PIN,grammar_ref=GRAMMAR,source_blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),input_sha256=RECEIPT,seed=r['seed'],runtime=sys.version.split()[0],physical_mixtures=144,receipt_decisions=8640,summary=summary,paired=paired,risk=[dict(p=p,q=q,policies=risk(summary,p,q)) for p in (0,.01,.05,.1,.25,1) for q in (0,.1,.5,1)],rows=r['rows'],limits='Receipt-level independent audit, not independent feature extraction. Paired finite corpus. Hypothetical fault mixture, not estimated prevalence. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for s in r['specimens']: shutil.copyfile(root/'cue1'/s['file'],out/s['file'])
    page='''<!doctype html><meta charset="utf-8"><title>Cue reliability inspector</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:0 1em}pre{white-space:pre-wrap}label{display:block;margin:.7em 0}table{border-collapse:collapse}td,th{padding:.5em;border:1px solid #aaa;text-align:right}</style><h1>Cue reliability inspector</h1><p>Synthetic finite corpus. Same PCM across cue faults; risk mixture is hypothetical.</p><label>Fault <select id="fault"></select></label><div id="summary"></div><h2>Paired observations</h2><label>Physical mixture <input id="pair" type="range" min="0" max="143" value="0"> <output id="which"></output></label><pre id="detail"></pre><h2>Hypothetical fault mixture</h2><label>Primary swap probability (%) <input id="p" type="range" min="0" max="100" value="10"> <output id="pv"></output></label><label>Secondary also swapped given primary swap (%) <input id="q" type="range" min="0" max="100" value="10"> <output id="qv"></output></label><div id="risk"></div><h2>Original specimens (opt-in)</h2><p>Start low; no calibrated SPL. Unchanged upstream mixtures.</p>'''
    page+=''.join(f'<p>{s["file"]} <audio controls preload="none" src="{s["file"]}"></audio></p>' for s in r['specimens'])
    page+='<p><a href="receipt.json">Complete replay receipt</a></p><script>const S='+json.dumps(summary)+';const R='+json.dumps(r['rows'])+''';const $=id=>document.getElementById(id);for(const f of Object.keys(S))$('fault').add(new Option(f,f));document.querySelectorAll('audio').forEach(a=>a.volume=.2);function table(head,rows){return '<table><tr>'+head.map(v=>'<th>'+v+'</th>').join('')+'</tr>'+rows.map(r=>'<tr>'+r.map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('')+'</table>'}function draw(){const f=$('fault').value,i=+$('pair').value,a=Object.entries(S[f]),keys=Object.keys(a[0][1]);$('summary').innerHTML=table(['Policy',...keys],a.map(([n,d])=>[n,...keys.map(k=>d[k])]));$('which').value=i+1;$('detail').textContent=JSON.stringify(R.slice(i*12,i*12+12).filter(x=>x.fault===f),null,2);const p=+$('p').value/100,q=+$('q').value/100;$('pv').value=p*100;$('qv').value=q*100;const pct=x=>(100*x).toFixed(2)+'%';$('risk').innerHTML=table(['Policy','Correct','Wrong','Withheld','Wrong | release'],Object.keys(S.clean).map(n=>{const c=(1-p)*S.clean[n].correct/288+p*(1-q)*S.swap[n].correct/288+p*q*S['both-swapped'][n].correct/288,w=(1-p)*S.clean[n].wrong/288+p*(1-q)*S.swap[n].wrong/288+p*q*S['both-swapped'][n].wrong/288;return [n,pct(c),pct(w),pct(1-c-w),c+w?pct(w/(c+w)):'undefined']}))}for(const id of ['fault','pair','p','q'])$(id).addEventListener('input',draw);draw()</script>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(summary=summary,paired=paired),indent=2))
if __name__=='__main__': main(*(pathlib.Path(x) for x in sys.argv[1:]))
