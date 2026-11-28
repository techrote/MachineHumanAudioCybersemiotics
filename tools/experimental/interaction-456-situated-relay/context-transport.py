"""Refs #456 / Draft #457. Faulted PCM action/revocation bank + scheduling replay.
python context-transport.py grammar NEW_OUTPUT
Synthetic only. Aligned fixtures, no authentication or human evidence. AI-assisted.
"""
import hashlib, itertools, json, pathlib, random, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='1a9a53b8ee6dbf592790b9d1ae1ce54b3aa22be8'
PIN='1950e1e2782e457c8c8e9ae378a62576cfb00ec6bbbb3e5bcb7a9a204616e5ad'
POLICIES=('full','unguarded','typed4','horizon','horizon-invalidate')
FAULTS=('clean','noise','query-loss','reply-loss','alternate')
REGIMES=('stable-loss','mismatch','recovery','intermittent')
sha=lambda b:hashlib.sha256(b).hexdigest()

def bank(root,out,u):
    here=pathlib.Path(__file__).parent
    offers,spec=u['bank'](root,out)
    a,books=runpy.run_path(str(here/'acoustic-turns.py'))['load'](root)
    c=runpy.run_path(str(here/'catalogue-turns.py')); rows={}
    for s,compatible,fault,mode,variant in itertools.product(range(2),(False,True),FAULTS,('full','address','guard'),range(2)):
        l=(13,18)[s]; b=books[s][l]; width=4+s; target=123+variant*101; sent=target+1 if fault=='alternate' else target
        req=[s,variant,16 if mode=='full' else 12]; sd=2500 if fault=='noise' else 0; seed=4564700+len(rows)*2
        qo,qp,qt=a['exchange'](a['code'](req),sd,seed,-1 if fault=='query-loss' else None)
        q=a['recover'](qo) if qo is not None else None; pp=pt=None; got=None; status='unknown'
        reserve=16+l if mode=='full' else 18+width
        if q==req:
            revoke=mode=='guard' and not compatible
            if revoke: payload=a['code'](q[:2]+[11])
            elif mode=='full': payload=a['code'](q)+b[sent].tolist()
            else: payload=c['encode'](q+c['digits']((sent+int(not compatible))%len(b),width))
            po,pp,pt=a['exchange'](payload,sd,seed+1,-1 if fault=='reply-loss' else None)
            if po is not None:
                if len(po)==5 and mode!='full' and a['recover'](po)==req[:2]+[11]: status='revoke'
                elif mode=='full' and len(po)==5+l and a['recover'](po[:5])==req:
                    body=po[5:]; keep=[i for i,v in enumerate(body) if v is not None]; e=l-len(keep)
                    if e<=4:
                        found=np.flatnonzero(2*np.count_nonzero(b[:,keep]!=[body[i] for i in keep],axis=1)+e<=4)
                        if len(found)==1:got=int(found[0])
                elif mode!='full' and len(po)==3+width+4:
                    h=c['decode'](po)
                    if h is not None and h[:3]==req and c['index'](h[3:])<len(b):got=c['index'](h[3:])
                if got is not None:status='identity'
        occupied=qt['slots']+(2+pt['slots'] if pt else 0)
        assert occupied<=reserve
        k=f'{s}:{int(compatible)}:{fault}:{mode}:{variant}'
        rows[k]=dict(request=req,target=target,decoded=got,status=status,query=qt,reply=pt,occupied=occupied,reserved=reserve)
        if s==0 and variant==0 and mode=='guard' and not compatible and fault in ('clean','reply-loss'):
            clip=np.concatenate([qp.ravel(),np.zeros(2560,dtype='<i2'),pp.ravel()]); name='revocation-'+fault+'.wav'
            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(clip.tobytes())
            spec.append(dict(file=name,peak=int(np.abs(clip.astype('int32')).max()),pcm_sha256=sha(clip.tobytes())))
    return offers,rows,spec

def session(fixtures,offers,bank,mode,window):
    states=[dict(positive=False,until=0,reason='initial') for _ in range(2)]; events=[]; stats=Counter(); now=0
    for f in fixtures:
        r,s=f['round'],f['agent']; x=states[s]; deadline=r*window+(window//2+5 if s==0 else window)
        if s==0:now=r*window
        def spend(kind,key,e):
            nonlocal now
            start=now; fit=now+e['reserved']<=deadline
            if fit:now+=e['reserved'] if e['status']=='unknown' else e['occupied'];stats['slots']+=now-start;stats['frames']+=1+int(e['reply'] is not None)
            events.append(dict(round=r,agent=s,event=kind,key=key,start=start,end=now,deadline=deadline,fit=fit,status=e['status'] if fit else 'not-fit',decoded=e.get('decoded') if fit else None));return fit
        horizon=mode.startswith('horizon'); remaining=len(fixtures)//2-r
        if mode!='full' and not x['positive'] and r>=x['until'] and (not horizon or remaining>=7 and window>=100):
            k=f"{s}:{int(f['compatible'])}:{f['fault']}:{f['variant']}";e=offers[k]
            if spend('offer',k,e):
                stats['offers']+=1;z=e['status'];x.update(positive=z=='agree',reason=z,until=r+(4 if z=='reject' else 1))
        chosen=None; m='full' if not x['positive'] or mode=='full' else 'address' if mode=='unguarded' else 'guard'
        for attempt in range(2):
            fault=f['action'] if attempt==0 else f['fallback'];k=f"{s}:{int(f['compatible'])}:{fault}:{m}:{f['variant']%2}";e=bank[k]
            if not spend(m,k,e):break
            stats[m+'_attempts']+=1
            if e['status']=='identity':chosen=e['decoded'];break
            if e['status']=='revoke':stats['revocations']+=1;x.update(positive=False,until=r+1,reason='revoke');m='full';continue
            if m=='guard' and mode=='horizon-invalidate':x.update(positive=False,until=r+1,reason='unknown')
            break
        target=123+f['variant']%2*101; outcome='abstain' if chosen is None else 'correct' if chosen==target else 'wrong';stats[outcome]+=1
        events.append(dict(round=r,agent=s,event='outcome',start=now,end=now,deadline=deadline,status=outcome,chosen=chosen,target=target,state=dict(x)))
    result=dict(stats=dict(stats),events=events); audit(result,fixtures,offers,bank);return result

def audit(result,fixtures,offers,bank):
    events=result['events']; stats=result['stats']; last=0; found={}; counts=Counter(); frames=0; slots=0
    for e in events:
        assert last<=e['start']<=e['end']<=e['deadline'];last=e['end']; key=(e['round'],e['agent']);slots+=e['end']-e['start']
        if e['event']=='outcome':
            assert e['chosen']==found.pop(key,None); expected='abstain' if e['chosen'] is None else 'correct' if e['chosen']==e['target'] else 'wrong';assert e['status']==expected;counts[expected]+=1
        elif e['fit']:
            b=(offers if e['event']=='offer' else bank)[e['key']];assert e['status']==b['status'] and e['decoded']==b.get('decoded');assert e['end']-e['start']==(b['reserved'] if b['status']=='unknown' else b['occupied']);frames+=1+int(b['reply'] is not None)
            if e['event']!='offer' and b['status']=='identity':assert key not in found;found[key]=b['decoded']
        else:assert e['end']==e['start'] and e['decoded'] is None
    assert not found and sum(counts.values())==len(fixtures) and all(stats.get(k,0)==counts[k] for k in ('correct','wrong','abstain')) and slots==stats.get('slots',0) and frames==stats.get('frames',0)

def run(root,out):
    here=pathlib.Path(__file__).parent; assert sha((here/'context-uncertainty.py').read_bytes())==PIN
    u=runpy.run_path(str(here/'context-uncertainty.py'));out.mkdir();offers,rows,spec=bank(root,out,u); aggregate={}; examples=[]; count=0
    with (out/'traces.jsonl').open('w') as fp:
        for seed,regime,window,policy in itertools.product(range(4564700,4564708),REGIMES,(80,100),POLICIES):
            f=u['fixture'](seed,regime,12);rng=random.Random(seed+1)
            for v in f:v.update(action=rng.choices(FAULTS,(7,2,1,2,1))[0],fallback=rng.choices(FAULTS,(7,2,1,2,1))[0])
            x=session(f,offers,rows,policy,window);assert x==session(f,offers,rows,policy,window);count+=1;x.update(seed=seed,regime=regime,window=window,policy=policy,fixtures=f);fp.write(json.dumps(x)+'\n');aggregate.setdefault(f'{regime}:{window}:{policy}',Counter()).update(x['stats'])
            if seed==4564700:examples.append(x)
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),sessions=count,obligations=count*24,bank_frames=sum(1+int(v['reply'] is not None) for v in [*offers.values(),*rows.values()]),stats=aggregate,specimens=spec,limits='Synthetic aligned PCM evidence banks reused in scheduling. Fixed order, fixed target fixtures, known response lengths and timeout reservations; no nonce freshness, independent authentication, live device or human evidence.')
    for name,obj in [('receipt',receipt),('offer-bank',offers),('action-bank',rows)]: (out/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Context transport</title><h1>Context transport</h1><p>Synthetic aligned PCM replay. Start at low system volume.</p><select id="case" aria-label="Scenario"></select> <button id="prev">Previous</button> <button id="next">Next</button><p id="state"></p><pre id="event"></pre>'''+''.join(f'<p>{s["file"]} <audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="offer-bank.json">Offer evidence</a> | <a href="action-bank.json">Action evidence</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const sel=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.regime,r.window,r.policy].join(' / ');sel.append(o)});function draw(){let r=rows[+sel.value];document.querySelector('#state').textContent=`Event ${i+1}/${r.events.length} | ${JSON.stringify(r.stats)}`;document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2)}sel.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+sel.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('sessions','obligations','bank_frames','source_sha256')}))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
