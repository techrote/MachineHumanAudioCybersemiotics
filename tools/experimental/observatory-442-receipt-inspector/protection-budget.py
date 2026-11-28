"""Refs #442: equal scheduled slot budget, synthetic aligned catalogue exchanges.
Run: python protection-budget.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Measurement comparator, not a new protocol or blind receiver. See receipt limits.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='4e120c8d315aebf75cb874715a5cc12dc975dcad'; BLOB='09e6be58b1ebffc9be44d9a04a4d3d6fdce7bfe7'
CONTEXT='755fa4849843a8226063465ce6426fca49fd8b86'; SEED=4424701
# query parity, reply parity, markers per frame; total redundancy always six plus four basic markers.
MODES={'reply-heavy':(2,4,2),'query-heavy':(4,2,2),'balanced-markers':(2,2,3),'query-markers':(4,0,3),'reply-markers':(0,4,3)}
# sub/erase probabilities per direction, and marker exposure.
CONDS={'clean':(0,0,0,0,False),'payload-mixed':(.05,.05,.05,.05,False),'all-mixed':(.05,.05,.05,.05,True),'all-severe':(.10,.10,.10,.10,True),'query-heavy-fault':(.10,.10,.01,.01,True),'reply-heavy-fault':(.01,.01,.10,.10,True),'marker-only':(0,0,0,0,True)}
sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(raw):return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
def run(root,out):
    p=root/'framed-cost-audit.py';assert blob(p.read_bytes())==BLOB
    a=runpy.run_path(str(p)); encode,decode=a['encode'],a['decode']; tones,basis,S,F=a['TONES'],a['BASIS'],a['S'],a['F']
    for f,b in a['BLOBS'].items():assert blob((root/f).read_bytes())==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    def marker_ok(obs,m):
        expected=[17]+[18]*(m-1);actual=[obs[0]]+obs[-(m-1):]
        return sum(x==y for x,y in zip(actual,expected))>=2
    def frame(payload,m,draw,sub,erase,expose,marker_only):
        clean=[17,*payload,*([18]*(m-1))];sent=clean.copy();u,d=draw
        for i,x in enumerate(clean):
            marker=i==0 or i>len(payload);j=0 if i==0 else 31-(len(clean)-1-i) if marker else i
            ps,pe=(.05,.05) if marker and marker_only else (sub,erase)
            if marker and not expose:continue
            if u[j]<pe:sent[i]=None
            elif u[j]<ps+pe:sent[i]=(x+1)%19 if marker else (x+int(d[j]))%17
        pcm=np.zeros((len(sent),S),dtype='<i2')
        for i,x in enumerate(sent):
            if x is not None:pcm[i,:S//2]=tones[x]
        scores=abs(pcm[:,80:480]@basis.T)*2/400;obs=[int(z.argmax()) if z.max()>=600 else None for z in scores];assert obs==sent
        ok=marker_ok(obs,m);body=obs[1:1+len(payload)]
        return body if ok else None,pcm,dict(clean=clean,observed=obs,marker_ok=ok,slots=len(clean),pcm_sha256=sha(pcm.tobytes()),energy=int(np.square(pcm.astype(np.int64)).sum()))
    # Exhaustive marker known-answer checks over correct, erased and substituted markers.
    import itertools
    checks=0
    for m in (2,3):
        for faults in itertools.product(range(3),repeat=m):
            expected=[17]+[18]*(m-1);x=[z if f==0 else None if f==1 else (z+1)%19 for z,f in zip(expected,faults)];assert marker_ok([x[0],0,*x[1:]],m)==(faults.count(0)>=2);checks+=1
    rng=np.random.default_rng(SEED);out.mkdir();stats={};rows=[];spec=[];group=0
    for source,bylen in books.items():
        for length,book in bylen.items():
            width=4 if length==13 else 5
            for _ in range(64):
                group+=1;target=int(rng.integers(len(book)));request=[(group//17)%17,group%17,15];seed=SEED+group;g=np.random.default_rng(seed);draws=[(g.random(32),g.integers(1,17,32)) for i in range(2)]
                for cond,(qs,qe,rs,re,markers) in CONDS.items():
                    for mode,(qp,rp,m) in MODES.items():
                        qbody,qpcm,qt=frame(encode(request,qp),m,draws[0],qs,qe,markers,cond=='marker-only');q=decode(qbody,qp);rt=None;returned=None;reason='query-frame' if qbody is None else 'query-code'
                        # Sender responds to decoded query (not privileged equality). Receiver checks echo.
                        if q is not None and q[2]==15:
                            rb,rpcm,rt=frame(encode(q+a['digits'](target,width),rp),m,draws[1],rs,re,markers,cond=='marker-only');h=decode(rb,rp);reason='reply-frame' if rb is None else 'reply-code'
                            if h is not None:
                                reason='correlation' if h[:3]!=request else 'address-range'
                                if h[:3]==request and a['index'](h[3:])<len(book):returned=a['index'](h[3:]);reason='correct' if returned==target else 'wrong'
                            if group==1 and cond in ('clean','all-mixed','marker-only'):
                                name=f'{mode}-{cond}.wav';pcm=np.concatenate((qpcm,rpcm));b=pcm.tobytes()
                                with wave.open(str(out/name),'wb') as w:w.setparams((1,2,F,0,'NONE','not compressed'));w.writeframes(b)
                                spec.append(dict(file=name,pcm_sha256=sha(b),peak=int(abs(pcm).max())))
                        elif q is not None:reason='query-opcode'
                        planned=3+qp+m+3+width+rp+m;assert planned==16+width
                        slots=qt['slots']+(rt['slots'] if rt else 0);status='withheld' if returned is None else 'correct' if returned==target else 'wrong';assert cond!='clean' or status=='correct'
                        c=stats.setdefault(cond+':'+mode,Counter());c[status]+=1;c['reason_'+reason]+=1;c['slots']+=slots;c['planned']+=planned;c['energy']+=qt['energy']+(rt['energy'] if rt else 0)
                        rows.append(dict(group=group,seed=seed,source=source,length=length,target=target,mode=mode,condition=cond,request=request,decoded_query=q,returned=returned,status=status,reason=reason,query=qt,reply=rt,slots=slots,planned=planned))
    for z in rows:
        assert z['status']==('withheld' if z['returned'] is None else 'correct' if z['returned']==z['target'] else 'wrong');assert z['slots']==sum(f['slots'] for f in (z['query'],z['reply']) if f);assert z['reply'] is None or z['slots']==z['planned']
    receipt=dict(schema='mhac-protection-budget-v1',parent=PARENT,parent_blob=BLOB,grammar_context=CONTEXT,catalogue_pin=a['PIN'],catalogue_blobs=a['BLOBS'],source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,groups=group,evaluations=len(rows),marker_checks=checks,modes=MODES,conditions=CONDS,stats=stats,specimens=spec,limits='Equal planned slots, not emitted energy after query refusal. Known timing, source, length, frame boundaries, reply format and identical catalogue order. Three-marker majority checks only expected positions, not blind acquisition or false-start rejection. Marker-only faults are 5% substitutions + 5% erasures. Independent random per-slot substitutions/erasures rendered as tones/silence, no added noise. Sender follows decoded query; receiver checks nonce/opcode echo, not authentication. No retries, turnaround, human evidence or device control. Fresh exploratory corpus; no tuning or deployment recommendation.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(z)+'\n' for z in rows));(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Equal protection budget</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}td,th{padding:.5em;border:1px solid #888}table{border-collapse:collapse}pre{white-space:pre-wrap}</style><h1>Equal protection budget</h1><p>Synthetic aligned PCM; no human evidence. All policies have equal scheduled slots. No autoplay, start with low system volume.</p><label>Condition <select id="c"></select></label><div id="t"></div><p><a href="receipt.json">Receipt</a> · <a href="traces.jsonl">Full traces</a></p>'''+''.join(f'<p>{z["file"]}<br><audio controls preload="none" src="{z["file"]}"></audio></p>' for z in spec)+'''<script>const d='''+json.dumps(stats)+''',c=document.getElementById('c'),t=document.getElementById('t');for(const k of [...new Set(Object.keys(d).map(k=>k.split(':')[0]))])c.add(new Option(k,k));function draw(){t.innerHTML='<table><tr><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Query frame</th><th>Reply frame</th><th>Mean emitted ms</th></tr>'+Object.keys(d).filter(k=>k.startsWith(c.value+':')).map(k=>{let r=d[k];return '<tr><td>'+k.split(':')[1]+'</td>'+['correct','wrong','withheld','reason_query-frame','reason_reply-frame'].map(n=>'<td>'+(r[n]||0)+'</td>').join('')+'<td>'+Math.round(r.slots*80/256)+'</td></tr>'}).join('')+'</table>'}c.onchange=draw;draw();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''');(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(groups=group,evaluations=len(rows),stats=stats)))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
