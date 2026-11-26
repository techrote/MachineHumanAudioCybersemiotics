"""Refs #442 / #443. Synthetic catalogue session accounting; no human evidence.
Independent symbolic audit of Grammar session-catalogue.py, not a native PCM receiver.
Run: python session-cost-audit.py PINNED_CATALOGUE_DIR NEW_OUTPUT_DIR
"""
import hashlib, itertools, json, pathlib, runpy, sys
import numpy as np
PIN='33228efc8363a0814a36ebfd175ecfef9920e364'
RULES={'session-catalogue.py':'46704d34946ca860cad7543914d00f5a95a683b5','catalogue-agreement.py':'8b0f4f6365e3c908a2f9c7a8a7e97fa245fe6580'}
BLOBS={'version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def witness(s,l,book):
    prefix=hashlib.sha256(b'MHAC-order-v1\0'+bytes([s,l])+len(book).to_bytes(4,'little')+book[:-10].astype('u1').tobytes())
    seen={};tail=book[-10:].astype('u1')
    for count,p in enumerate(itertools.permutations(range(10)),1):
        if count>20000:break
        d=prefix.copy();d.update(tail[list(p)].tobytes());raw=d.digest();tag=int.from_bytes(raw,'big')%17**4
        if tag in seen:
            q,other=seen[tag];different=sum(x!=y for x,y in zip(p,q))
            if different>=4:
                assert raw!=other and int.from_bytes(other,'big')%17**4==tag
                return dict(source=s,length=l,size=len(book),tries=count,tag4=tag,tag8_equal=int.from_bytes(raw,'big')%17**8==int.from_bytes(other,'big')%17**8,changed=different,sender_tail=list(q),receiver_tail=list(p),sender_sha256=other.hex(),receiver_sha256=raw.hex())
        seen[tag]=(p,raw)
    raise ValueError('pinned bounded collision witness not reproduced')
def ledger(n,l,mode,condition,change):
    # Explicit frame sizes transcribed from session-catalogue.py; clean aligned frames only.
    w=4 if l==13 else 5; full=[7,7+l]; index=[7,9+w]; tagged=[7,13+w]
    cached=mode in ('cached4','cached8','guarded8'); guarded=mode=='guarded8'; valid=cached
    rows=[]
    for t in range(n):
        frames=[];result='correct';route='full'
        if t==0 and cached:
            frames.extend([7,9+(4 if mode=='cached4' else 8)])
            if condition=='initial-shift' or (condition=='collision4' and mode!='cached4'):valid=False
        shifted=condition=='initial-shift' or (condition in ('receiver-change','sender-change') and t>=change)
        if mode=='per-turn4':
            frames.extend(tagged);route='tagged'
            if shifted:frames.extend(full);route='tagged-fallback'
            elif condition=='collision4':result='wrong' # targeted differing address only
        elif valid:
            if guarded and shifted:
                if condition=='sender-change':frames.extend([7,10])
                valid=False;frames.extend(full);route='revoked-full'
            else:
                frames.extend(index);route='cached'
                if shifted or condition=='collision4':result='wrong'
        else:frames.extend(full)
        rows.append(dict(turn=t,route=route,frames=frames,slots=sum(frames),status=result))
    return rows
MODES=('full','per-turn4','cached4','cached8','guarded8')
CONDS=('clean','initial-shift','collision4','receiver-change','sender-change')
def run(root,out):
    for f,h in BLOBS.items():assert blob((root/f).read_bytes())==h,f
    v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    witnesses=[witness(s,l,b) for s,d in books.items() for l,b in d.items()];assert not any(x['tag8_equal'] for x in witnesses)
    cases=[]
    for n in range(1,9):
        for l in (13,18):
            for c in CONDS:
                for change in range(1,n) if c.endswith('-change') else [0]:
                    for m in MODES:
                        r=ledger(n,l,m,c,change);cases.append(dict(turns=n,length=l,condition=c,change=change,mode=m,slots=sum(x['slots'] for x in r),correct=sum(x['status']=='correct' for x in r),wrong=sum(x['status']=='wrong' for x in r),trace=r))
    # Independent arithmetic known answers from documented frame lengths.
    for l in (13,18):
        w=4 if l==13 else 5
        for n in range(1,9):
            assert sum(x['slots'] for x in ledger(n,l,'guarded8','clean',0))==24+n*(16+w)
            assert sum(x['slots'] for x in ledger(n,l,'full','clean',0))==n*(14+l)
            assert sum(x['slots'] for x in ledger(n,l,'per-turn4','clean',0))==n*(20+w)
            for t in range(1,n):
                a=ledger(n,l,'guarded8','receiver-change',t);b=ledger(n,l,'guarded8','sender-change',t)
                assert all(x['status']=='correct' for x in a+b) and sum(x['slots'] for x in b)-sum(x['slots'] for x in a)==17
    out.mkdir();receipt=dict(schema='mhac-session-cost-audit-v1',pin=PIN,rules=RULES,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,witnesses=witnesses,cases=len(cases),limits='Exact finite permutation witness reproduction; eight-digit tags tested only on four four-digit collision pairs. Collision target cases deliberately target changed addresses; uniform address risk is conditional on these fixed catalogue pairs, not a real-world probability. Symbolic frame-slot accounting, clean transport, no retries beyond scripted fallback, no elapsed processing, physical acquisition, authentication or human evidence. Session horizon restricted to eight turns, as in pinned implementation. No new audio.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
    html='''<!doctype html><meta charset="utf-8"><title>Session cost audit</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto;padding:1em}table{border-collapse:collapse}td,th{padding:.5em;border:1px solid #888}pre{white-space:pre-wrap}</style><h1>Catalogue session cost audit</h1><p>Symbolic replay of clean frame costs. Collision cases target changed addresses; not human evidence or transport qualification.</p><label>Turns <select id="n"></select></label> <label>Body length <select id="l"><option>13</option><option>18</option></select></label> <label>Condition <select id="c"></select></label> <label>Change before turn (zero-based) <select id="k"></select></label> <label>Budget (slots) <input id="b" type="number" min="0" value="180"></label><div id="t"></div><p>Budget counts completed serial exchanges; no retries beyond the recorded policy.</p><h2>Reproduced collision witnesses</h2><div id="w"></div><p><a href="receipt.json">Receipt</a> · <a href="cases.json">Replay traces</a></p><script>const data=DATA,wit=WIT;const $=id=>document.getElementById(id),n=$('n'),l=$('l'),c=$('c'),k=$('k'),b=$('b');for(let i=1;i<=8;i++)n.add(new Option(i,i));n.value=8;for(const x of [...new Set(data.map(r=>r.condition))])c.add(new Option(x,x));function draw(){let change=c.value.endsWith('-change'),old=+k.value;if(change&&+n.value===1)n.value=2;k.replaceChildren();for(let i=change?1:0;i< (change?+n.value:1);i++)k.add(new Option(i,i));k.value=change?Math.min(+n.value-1,Math.max(1,old)):0;k.disabled=!change;let rows=data.filter(r=>r.turns===+n.value&&r.length===+l.value&&r.condition===c.value&&r.change===+k.value);$('t').innerHTML='<table><tr><th>Policy</th><th>Total slots</th><th>ms</th><th>Correct</th><th>Wrong</th><th>Correct within budget</th><th>Wrong within budget</th></tr>'+rows.map(r=>{let s=0,z=r.trace.filter(x=>(s+=x.slots)<=+b.value);return '<tr><td>'+r.mode+'</td><td>'+r.slots+'</td><td>'+r.slots*80+'</td><td>'+r.correct+'</td><td>'+r.wrong+'</td><td>'+z.filter(x=>x.status==='correct').length+'</td><td>'+z.filter(x=>x.status==='wrong').length+'</td></tr>'}).join('')+'</table>'}for(const x of [n,l,c,k,b])x.onchange=draw;draw();$('w').innerHTML='<table><tr><th>Source</th><th>Length</th><th>Catalogue rows</th><th>Changed rows</th><th>Conditional uniform mismatch</th><th>8-digit collision?</th></tr>'+wit.map(x=>'<tr><td>'+x.source+'</td><td>'+x.length+'</td><td>'+x.size+'</td><td>'+x.changed+'</td><td>'+(100*x.changed/x.size).toFixed(5)+'%</td><td>'+x.tag8_equal+'</td></tr>').join('')+'</table>'</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(cases,separators=(',',':'))).replace('WIT',json.dumps(witnesses)));(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
