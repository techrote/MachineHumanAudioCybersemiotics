"""Refs #442/#443: aligned PCM control recovery, synthetic only."""
import itertools, json, sys, wave
from pathlib import Path
from collections import Counter
import numpy as np
PARENT='d4b007e2a6ab86521256fe6e822a4ca04be3984f'
SEED=4427501
# Pin the predecessor and its own transitive imports.
import hashlib, runpy
p=Path(__file__).with_name('escalation-lab.py')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='af56d9128c861211e52255078788d34834253687cf7b255535cbfed06f890cc4'
e=runpy.run_path(str(p)); s,a,b,l=(e[k] for k in ('s','a','b','l'))
POL=('abort','retry','rank1','rank3')
# initial control RMS, feedback RMS, first-cycle-only burst, body corruption
CONDS={'white':(1000,1000,False,False),'feedback2500':(1000,2500,False,False),'feedback3500':(1000,3500,False,False),'burst':(1000,3500,True,False),'weak_initial':(3500,1000,False,False),'transient':(1000,1000,False,True),'absent':(1000,1000,False,False)}

def run(out):
    out.mkdir(); rng=np.random.default_rng(SEED); rows=[]; gallery={}
    train=l.null(l.SEED+1,(0,.5,1),a.MODE)
    th=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)[:,0]
    for i,(lex,ep,src,op) in enumerate(itertools.product(range(4),range(3),range(3),range(3))):
        expected=[lex,0,*b.code((ep,src,op),a.MODE)]; phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT)); ctrl=rng.normal(size=(12,7,s.SLOT))
        for c,(hsd,fsd,burst,corrupt) in CONDS.items():
            present=c!='absent'; changed=expected.copy()
            if corrupt: changed[2]=(ep+1)%3; changed[3]=(src+2)%3; changed[6]=None
            scale=1600/np.max(abs(a.p.render(expected,a.MODE,27,phase,2)))
            signal=a.p.render(changed,a.MODE,27,phase,2)*scale if present else np.zeros_like(a.p.render(expected,a.MODE,27,phase,2))
            y=b.d.pcm(signal+1000*l.a.mix(z,0)); win,j,d,h=l.measure(y[:,160:800].astype(float),a.MODE)
            initial=[v if j[k]>=max(80,th[k]*d[k,0]) else None for k,v in enumerate(win)]
            packet=s.packet([i,e['rank'](expected)]) if present else [None]*6
            copies=[s.channel(packet,ctrl[k],27,hsd,0) for k in (0,10,11)]
            hd=s.unpack(copies[0][0]); eligible=hd is not None and hd[0]==i and hd[1]<108
            for policy in POL:
                parts=[]; audio=[]; state=list(initial); tag=None; body_count=0; timeouts=0
                if policy.startswith('rank'):
                    n=int(policy[-1]); used=copies[:n]; tags={v[1] for obs,_,_ in used if (v:=s.unpack(obs)) is not None and v[0]==i and v[1]<108}; tag=next(iter(tags)) if len(tags)==1 else None
                    ms=120*n; audio=[v[1].ravel() for v in used]; parts=[{'direct':v[2]} for v in used]
                else:
                    ms=360; audio=[copies[0][1].ravel(),y.ravel()]; g=e['valid'](state,hd[1]) if eligible else None
                    for cycle in range(3 if policy=='retry' else 2):
                        if not eligible or g is not None or body_count==2: break
                        mask=sum(1<<k for k,v in enumerate(state) if v is None) if body_count==0 else 127; mask=mask or 127
                        ids=[k for k in range(7) if mask>>k&1]; sd=1000 if burst and cycle>0 else fsd
                        q,qy,qt=s.channel(s.packet([i,mask]),ctrl[1+3*cycle],27,sd,0); ms+=130; audio.extend([np.zeros(160,dtype='<i2'),qy.ravel()]); part={'mask':mask,'request':qt}; parts.append(part)
                        if s.unpack(q)!=[i,mask]:
                            ms+=270; timeouts+=1; audio.append(np.zeros(4320,dtype='<i2'))
                            if policy=='abort': break
                            continue
                        rh,ry,rt=s.channel(s.packet([i,mask]),ctrl[2+3*cycle],27,sd,0)
                        v,by,bt=s.channel([expected[k] for k in ids],ctrl[3+3*cycle][ids],27,1000,0); body_count+=1; ms+=130+20*len(ids); audio.extend([np.zeros(160,dtype='<i2'),ry.ravel(),by.ravel()]); part.update(reply=rt,body=bt)
                        if s.unpack(rh)!=[i,mask]:
                            if policy=='abort': break
                            continue
                        for k,w in zip(ids,v): state[k]=w
                        g=e['valid'](state,hd[1])
                    tag=e['rank'](g) if g is not None else None
                status='withheld' if tag is None else 'correct' if present and tag==e['rank'](expected) else 'wrong'
                assert sum(len(x) for x in audio)==ms*16
                assert len(parts)<=(3 if policy in ('retry','rank3') else 2) and body_count<=2
                rows.append(dict(condition=c,fixture=i,policy=policy,expected=e['rank'](expected) if present else None,initial=initial,initial_sha=s.sha(y.tobytes()),header=copies[0][2],parts=parts,tag=tag,status=status,ms=ms,timeouts=timeouts,body_count=body_count))
                if i==0 and c in ('burst','feedback3500'): gallery[c+'-'+policy]=np.concatenate(audio)
    groups=[]
    for c,policy in itertools.product(CONDS,POL):
        rr=[r for r in rows if (r['condition'],r['policy'])==(c,policy)]; n=Counter(r['status'] for r in rr); groups.append(dict(condition=c,policy=policy,correct=n['correct'],wrong=n['wrong'],withheld=n['withheld'],ms=sum(r['ms'] for r in rr),timeouts=sum(r['timeouts'] for r in rr),bodies=sum(r['body_count'] for r in rr)))
    verify(rows,groups)
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,seed=SEED,conditions=CONDS,groups=groups,source_sha256=s.sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__),indent=2)+'\n')
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Control recovery</title><h1>Control recovery (synthetic aligned PCM)</h1><p>Rank copies are scheduled, not feedback-driven. Costs differ. No authentication or human evidence.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{n}<br><audio controls preload="none" src="{n}.wav"></audio></p>' for n in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(groups)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.condition)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.condition===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({p.name:s.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')

def verify(rows,groups):
    assert len(rows)==108*len(CONDS)*len(POL)
    for r in rows:
        i=r['fixture']; policy=r['policy']; parts=r['parts']; h=s.unpack(r['header']['observed']); tag=None
        if policy.startswith('rank'):
            tags=set(); ms=120*len(parts); assert len(parts)==int(policy[-1]); assert parts[0]['direct']==r['header']
            for part in parts:
                v=s.unpack(part['direct']['observed'])
                if v is not None and v[0]==i and v[1]<108: tags.add(v[1])
            if len(tags)==1: tag=tags.pop()
        else:
            ms=360; x=list(r['initial']); g=None; count=0; waits=0
            if h is not None and h[0]==i and h[1]<108: g=e['valid'](x,h[1])
            for k,part in enumerate(parts):
                assert h is not None and h[0]==i and h[1]<108 and g is None and count<2
                mask=part['mask']; ms+=130
                if 'body' not in part:
                    assert s.unpack(part['request']['observed'])!=[i,mask]; waits+=1; ms+=270
                    if policy=='abort': assert k==len(parts)-1
                    continue
                assert s.unpack(part['request']['observed'])==[i,mask]; count+=1; ms+=130+20*len(part['body']['observed'])
                if s.unpack(part['reply']['observed'])==[i,mask]:
                    for j,v in zip([j for j in range(7) if mask>>j&1],part['body']['observed']): x[j]=v
                    g=e['valid'](x,h[1])
                elif policy=='abort': assert k==len(parts)-1
            assert waits==r['timeouts'] and count==r['body_count'] and count<=2 and len(parts)<=(3 if policy=='retry' else 2)
            if g is not None: tag=e['rank'](g)
        assert tag==r['tag'] and ms==r['ms'] and r['status']==('withheld' if tag is None else 'correct' if tag==r['expected'] else 'wrong')
    for j in range(0,len(rows),4): assert len({(r['initial_sha'],r['header']['pcm_sha256']) for r in rows[j:j+4]})==1
    for g in groups:
        rr=[r for r in rows if r['condition']==g['condition'] and r['policy']==g['policy']]; assert len(rr)==108 and all(sum(r['status']==v for r in rr)==g[v] for v in ('correct','wrong','withheld')) and sum(r['ms'] for r in rr)==g['ms']
    print('verified',len(rows),'decisions',len(groups),'groups')

if __name__=='__main__': run(Path(sys.argv[1]))
