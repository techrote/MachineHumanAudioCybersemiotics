"""Measurement #442: shared-frame coverage, not authenticated intent.
Run: python ambiguity-coverage.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='b9c0af501b38ac516f194a362c8688c95657b32b'; SEED=4424301; S=1280
GAINS=(0,.4,.55,.7,1,1.4); MODES=('hard25','list-exact','list-radius2')
def run(root,out):
    load=lambda f:runpy.run_path(str(root/f)); m=load('interval-admission.py'); p=load('competing-starts.py'); s=load('discourse-sync.py')
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':'32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3','list-evidence.py':'7e2f87a4ea7eb5e5e3773cf8023639f5116d5b65'}
    for f,h in pins.items(): assert m['blob'](root/f)==h,f
    l=load('list-evidence.py'); v=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']; _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](w,k,'polynomial') for k,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    def hits(book,obs,r):return np.flatnonzero(l['distances'](book,obs)<=r).tolist()
    def decode(book,obs,r):
        d=np.zeros(len(book),np.int16)
        for k,x in enumerate(obs):
            if x is not None:d+=~np.isin(book[:,k],x)
        ix=np.flatnonzero(d<=r);return int(ix[0]) if len(ix)==1 else None
    def report(ids,want):
        a,b=set(ids),set(want)
        return dict(count=len(a),ids=ids if len(a)<=8 else [],covered=len(a&b),foreign=len(a-b),exact=a==b,narrowed=len(b)>1 and len(a)==1 and a<=b,overflow=len(a)>8)
    assert report([0],[0,1])['narrowed'] and report(list(range(9)),[0,1])['ids']==[]
    dec={'hard25':joint,'list-exact':lambda b,o,r:decode(b,o,0),'list-radius2':decode}; obs={k:l['observer'](k) for k in MODES}
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False); rows=[]; specimens=[]; symbolic=[]; peak=0
    for source,bs in books.items():
        for n,book in bs.items():
            for pair,i in enumerate(rng.choice(len(book),3,False)):
                i=int(i); d=np.count_nonzero(book!=book[i],axis=1); d[i]=n+1
                for kind,j in [('nearest',int(d.argmin())),('random',int(rng.choice(np.flatnonzero(np.arange(len(book))!=i))))]:
                    union=[sorted({int(a),int(b)}) for a,b in zip(book[i],book[j])]; symbolic.append(dict(source=source,length=n,pair=pair,kind=kind,distance=int(d[j]),ideal={str(r):report(hits(book,union,r),[i,j]) for r in (0,2)}))
                    for gi,g in enumerate(GAINS):
                        x=np.zeros(26*S,np.int32); y=x.copy(); lead=S+40; m['put'](x,s['preamble'](source)+book[i].tolist()+[18,18],lead); m['put'](y,book[j].tolist(),lead+2*S)
                        ns=SEED*10000+len(symbolic)*100+gi; pcm=np.rint(x+g*y+np.random.default_rng(ns).normal(0,150,len(x))).astype('<i2'); peak=max(peak,int(abs(pcm).max())); digest=m['sha'](pcm.tobytes()); want=[i] if g==0 else [i,j]
                        for mode in MODES:
                            radius=0 if mode=='list-exact' else 2; ev=m['acquire'](pcm,books,obs[mode],dec[mode],'multiplex'); body=[e for e in ev if e['kind'] in ('candidate','reject') and e['source']==source and len(e['seen'])==n+2 and 18 not in e['seen'][:-2] and abs(e['body_start']-lead-2*S)<=160]; assert len(body)<=1
                            ids=hits(book,body[0]['seen'][:-2],radius) if body else []; rep=report(ids,want)
                            if body: assert body[0]['identity']==([n,ids[0]] if len(ids)==1 else None)
                            rel=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; expected=[[source,n,k] for k in want]; wrong=sum(z not in expected for z in rel)
                            rows.append(dict(source=source,length=n,pair=pair,kind=kind,distance=int(d[j]),gain=g,noise_sd=150,noise_seed=ns,expected=want,pcm_sha256=digest,mode=mode,body_observed=bool(body),report=rep,releases=rel,wrong=wrong,events=ev))
                        if source==0 and n==13 and pair==0 and g in (0,.55,1):
                            name=f'{kind}-{g}.wav'
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
                            specimens.append(dict(file=name,pcm_sha256=digest,peak=int(abs(pcm).max())))
    stats={}
    for r in rows:
        q=stats.setdefault(r['kind']+':'+str(r['gain'])+':'+r['mode'],Counter()); t=r['report']; q.update(trials=1,exact=int(t['exact']),covered=t['covered'],foreign=t['foreign'],narrowed=int(t['narrowed']),overflow=int(t['overflow']),release=len(r['releases']),wrong=r['wrong'],no_body=int(not r['body_observed']))
    receipt=dict(schema='mhac.ambiguity-coverage/1',pin=PIN,reference_blobs={'list-window.py':'ea61eb0f5534789eeff17c7eed07e96070eba9d0','ambiguity-admission.py':'cd49fa5280ef84b52c8a7335cab8d9d90802b9d6'},dependency_blobs=pins,measurement_pin='fcd72671f07540297195336338c567549e650093',seed=SEED,source_sha256=m['sha'](pathlib.Path(__file__).read_bytes()),physical_pcm=len(rows)//3,evaluations=len(rows),peak=peak,symbolic=symbolic,stats=stats,specimens=specimens,limits='Shared framing, not independently framed sources. Coverage of constructed alternatives is not knowledge of intent. Nearest and random rivals paired on same origin; fixed noise, finite synthetic corpus. Upstream receiver reused, observer transcribed in prior list-evidence.py. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    gallery=''.join(f'<p>{g["file"]}<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in specimens)
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Ambiguity coverage</title><style>body{font:16px system-ui;max-width:950px;margin:auto;padding:1em}pre{white-space:pre-wrap}td,th{padding:6px;border-bottom:1px solid #aaa}table{border-collapse:collapse}</style><h1>Shared-frame ambiguity coverage</h1><p>Synthetic only. Constructed alternatives are not authenticated meanings. Low volume, no autoplay.</p><label>Rival <select id="k"><option>nearest</option><option>random</option></select></label><label>Gain <select id="g"></select></label><table id="table"></table><label>Trace <select id="t"></select></label><pre id="detail"></pre>'''+gallery+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Complete traces</a></p><script>const rows='''+json.dumps(rows)+''';const k=document.getElementById('k'),g=document.getElementById('g'),t=document.getElementById('t'),d=document.getElementById('detail'),table=document.getElementById('table');for(const v of new Set(rows.map(r=>r.gain)))g.add(new Option(v,v));let selected=[];function show(){d.textContent=JSON.stringify(selected[+t.value],null,2)}function render(){selected=rows.filter(r=>r.kind===k.value&&r.gain===+g.value);table.innerHTML='<tr><th>Mode</th><th>Exact set</th><th>Narrowed</th><th>Foreign identities</th><th>Releases</th></tr>'+['hard25','list-exact','list-radius2'].map(m=>{const a=selected.filter(r=>r.mode===m);return '<tr><td>'+m+'</td>'+[a.filter(r=>r.report.exact).length+'/'+a.length,a.filter(r=>r.report.narrowed).length,a.reduce((n,r)=>n+r.report.foreign,0),a.reduce((n,r)=>n+r.releases.length,0)].map(v=>'<td>'+v+'</td>').join('')+'</tr>'}).join('');t.replaceChildren();selected.forEach((r,i)=>t.add(new Option(r.source+'/'+r.length+'/'+r.pair+'/'+r.mode,i)));show()}k.onchange=g.onchange=render;t.onchange=show;render();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:m['sha'](p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(stats))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
