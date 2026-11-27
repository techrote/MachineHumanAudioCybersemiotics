"""Refs #456, Draft #457. Synthetic offer evidence replay; action transport symbolic.
Run: python context-uncertainty.py grammar NEW_OUTPUT. One slot = 80 ms.
No human evidence, security or physical transport claims. AI-assisted.
"""
import hashlib, itertools, json, pathlib, random, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='f3992e17efa590ab09f818eb5875b66bab17182f'
PINS={'context-economics.py':'7961bc2839ebb7c245a2125643d47d20990fd5046ef193fd34f9d50ec2bf87ec','catalogue-turns.py':'a407e139a74ad49befe7cc0554c293bdc1e5f22d575fb84a930d3986057bc45b','acoustic-turns.py':'d14f133f592f6b9ea97ca8bce18d28eede9eb65dd9958029b1ee40edfefb9e6d'}
MODES=('full','retry','conflate4','typed4','typed-backoff')
REGIMES=('stable-loss','mismatch','recovery','intermittent')
FAULTS=('clean','noise','query-loss','reply-loss')
sha=lambda b:hashlib.sha256(b).hexdigest()

def bank(root,out):
    here=pathlib.Path(__file__).parent
    for f,h in PINS.items():assert sha((here/f).read_bytes())==h,f
    c=runpy.run_path(str(here/'catalogue-turns.py'));a,books=runpy.run_path(str(here/'acoustic-turns.py'))['load'](root)
    rows={};spec=[]
    for s,compatible,fault,variant in itertools.product(range(2),(False,True),FAULTS,range(4)):
        l=(13,18)[s];b=books[s][l];rd=c['digest'](s,l,b).hexdigest();sd=c['digest'](s,l,b if compatible else np.roll(b,1,axis=0)).hexdigest()
        tag=lambda d:int(d,16)%17**8
        assert (tag(rd)==tag(sd))==compatible
        k=f'{s}:{int(compatible)}:{fault}:{variant}';req=[s,variant,13];sdnoise=2500 if fault=='noise' else 0
        q,qp,qt=a['exchange'](a['code'](req),sdnoise,4564600+len(rows)*2,-1 if fault=='query-loss' else None)
        p=pp=pt=None;decoded=None
        if q is not None and a['recover'](q)==req:
            p,pp,pt=a['exchange'](c['encode'](req+c['digits'](tag(sd),8)),sdnoise,4564601+len(rows)*2,-1 if fault=='reply-loss' else None)
            decoded=c['decode'](p) if p is not None else None
        status='unknown' if decoded is None or decoded[:3]!=req else 'agree' if c['index'](decoded[3:])==tag(rd) else 'reject'
        assert status==('unknown' if fault.endswith('loss') else 'agree' if compatible else 'reject'),(k,status)
        rows[k]=dict(status=status,request=req,receiver_digest=rd,sender_digest=sd,query=qt,reply=pt,decoded=decoded,occupied=qt['slots']+(2+pt['slots'] if pt else 0),reserved=26)
        if s==0 and variant==0 and (compatible or fault=='clean'):
            clip=np.concatenate([qp.ravel(),np.zeros(2560,dtype='<i2'),pp.ravel()] if pp is not None else [qp.ravel()]);name=k.replace(':','-')+'.wav'
            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(clip.tobytes())
            spec.append(dict(file=name,peak=int(np.abs(clip.astype('int32')).max()),pcm_sha256=sha(clip.tobytes())))
    return rows,spec

def fixture(seed,regime,rounds):
    rng=random.Random(seed);recover=[rng.randrange(2,rounds) for _ in range(2)];phase=[rng.randrange(4) for _ in range(2)];rows=[]
    for r in range(rounds):
        for s in range(2):
            compatible=regime=='stable-loss' or regime=='recovery' and r>=recover[s] or regime=='intermittent' and (r+phase[s])%6<3
            fault=rng.choices(FAULTS,weights=(4,3,2,3) if regime=='stable-loss' else (7,2,1,2))[0]
            rows.append(dict(round=r,agent=s,compatible=compatible,fault=fault,variant=rng.randrange(4)))
    return rows

def session(fixtures,rows,mode,window):
    state=[dict(positive=False,until=0,reason=None,misses=0) for _ in range(2)];events=[];stats=Counter();now=0
    for f in fixtures:
        r,s=f['round'],f['agent'];x=state[s];deadline=r*window+(window//2+5 if s==0 else window)
        if s==0:now=r*window
        def spend(kind,cost,**kw):
            nonlocal now
            start=now;fit=now+cost<=deadline
            if fit:now+=cost;stats['slots']+=cost
            events.append(dict(round=r,agent=s,event=kind,start=start,end=now,deadline=deadline,cost=cost,fit=fit,**kw));return fit
        if x['positive'] and not f['compatible']:
            if spend('revocation',19):x.update(positive=False,until=r,reason=None,misses=0)
        if mode!='full' and not x['positive'] and r>=x['until']:
            k=f"{s}:{int(f['compatible'])}:{f['fault']}:{f['variant']}";e=rows[k]
            if spend('offer',e['reserved'],bank=k,status=e['status']):
                z=e['status'];stats[z]+=1;stats['offers']+=1;stats['offer_pcm_slots']+=e['occupied'];x['reason']=z
                if z=='agree':x.update(positive=True,until=r,misses=0)
                elif z=='reject' or mode=='conflate4':x.update(until=r+(4 if mode in ('conflate4','typed4','typed-backoff') else 1),misses=0)
                else:
                    x['misses']+=1;x['until']=r+(min(4,2**(x['misses']-1)) if mode=='typed-backoff' else 1)
        elif mode!='full' and not x['positive']:
            stats['skipped']+=1;stats['compatible_skips']+=int(f['compatible']);events.append(dict(round=r,agent=s,event='skip',start=now,end=now,deadline=deadline,reason=x['reason'],until=x['until']))
        # Faithful action transport and revocation are stipulated, not PCM-decoded.
        short=x['positive'] and f['compatible'] and mode!='full'
        ok=spend('address' if short else 'full',(22+s) if short else (29+5*s));stats['correct' if ok else 'abstain']+=1;stats['short']+=int(short and ok)
        events.append(dict(round=r,agent=s,event='outcome',start=now,end=now,deadline=deadline,status='correct' if ok else 'abstain',state=dict(x)))
    assert stats['correct']+stats['abstain']==len(fixtures)
    assert all(e['start']<=e['end']<=e['deadline'] for e in events)
    assert stats['slots']==sum(e['end']-e['start'] for e in events)
    assert stats['offers']==sum(e['event']=='offer' and e['fit'] for e in events)
    assert not any(e['event']=='address' and not fixtures[2*e['round']+e['agent']]['compatible'] for e in events)
    return dict(stats=dict(stats),events=events)

def run(root,out):
    out.mkdir();rows,spec=bank(root,out);aggregate={};examples=[];count=0
    with (out/'traces.jsonl').open('w') as fp:
        for seed,regime,rounds,window,mode in itertools.product(range(4564600,4564616),REGIMES,(6,12),(80,100),MODES):
            f=fixture(seed,regime,rounds);x=session(f,rows,mode,window);assert x==session(f,rows,mode,window);count+=1
            x.update(seed=seed,regime=regime,rounds=rounds,window=window,mode=mode,fixtures=f);fp.write(json.dumps(x)+'\n');aggregate.setdefault(f'{regime}:{rounds}:{window}:{mode}',Counter()).update(x['stats'])
            if seed==4564600:examples.append(x)
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),sessions=count,bank_frames=sum(1+int(v['reply'] is not None) for v in rows.values()),stats=aggregate,specimens=spec,limits='Actual aligned offer PCM bank; fixture replays share observations, not independent acoustic trials. Fixed serialized turns, reserved timeout 26 slots, revocation and action transport stipulated reliable. No authentication, wrong-content or human study. Synthetic exogenous distributions, no population inference.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'offer-bank.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Context uncertainty</title><h1>Context uncertainty</h1><p>Aligned acoustic offer evidence, simulated action transport. Start at low volume.</p><select id="case"></select> <button id="prev">Previous</button> <button id="next">Next</button><p id="state"></p><pre id="event"></pre>'''+''.join(f'<p>{s["file"]} <audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="offer-bank.json">Offer evidence</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const sel=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.regime,r.rounds,r.window,r.mode].join(' / ');sel.append(o)});function draw(){let r=rows[+sel.value];document.querySelector('#state').textContent=`Event ${i+1}/${r.events.length} | ${JSON.stringify(r.stats)}`;document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2)}sel.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+sel.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('sessions','bank_frames','source_sha256')}))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
