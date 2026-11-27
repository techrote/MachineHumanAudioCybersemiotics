"""Refs #452 / Draft #453: bounded multi-response association, synthetic aligned PCM.
Run: python concurrent-association.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Public fixture key; no authentication, semantic truth, action authority or human evidence.
One GPT-6.2 worker; no independent review. Events are whole aligned frames, not overlap.
"""
import hashlib,hmac,json,pathlib,runpy,sys,wave
from collections import Counter
import numpy as np
PIN='2b351ea8b770bd628bf6963bd938f6f6de7af933'
PINS={'detached-verification.py':'dfa11f3af03e9330ca14b8a865456d497c40a823','anchored-epoch.py':'44c5766ffd3250fa230fee36208b8498dc24538d','catalogue-reply.py':'8b07a9dde7dd7250b490263c3044aeb798453019','acoustic-clarification.py':'71e527852c278fb91088ed9fdcf5d7d6027426a3','catalogue-agreement.py':'8b0f4f6365e3c908a2f9c7a8a7e97fa245fe6580','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55'}
SEED=452490
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def associate(mode,roster,events,tag):
    bodies={k:set() for k in roster}; tags=[]; order=[]
    for role,word in events:
        if word is None:continue
        if role=='body' and tuple(word[:5]) in bodies:
            k=tuple(word[:5]);w=tuple(word)
            if not bodies[k]:order.append(k)
            bodies[k].add(w)
        elif role=='tag' and tuple(word) not in tags:tags.append(tuple(word))
    good={k:next(iter(v)) for k,v in bodies.items() if len(v)==1}
    # Detached matching must know the complete roster at closure; missing/conflicting bodies may hide a collision.
    if mode=='graph' and len(good)!=len(roster):return {},0
    edges=[];checks=0
    for j,t in enumerate(tags):
        for k,w in good.items():
            if mode=='fifo' and (j>=len(order) or order[j]!=k):continue
            if mode=='header' and t[:5]!=k:continue
            checks+=1
            if tag(w)==t[-8:]:edges.append((j,k))
    return {k:good[k] for j,k in edges if sum(x==j for x,y in edges)==1 and sum(y==k for x,y in edges)==1},checks

def run(root,out):
    for f,b in PINS.items():assert blob((root/f).read_bytes())==b,f
    z,c,a,g,v=[runpy.run_path(str(root/f)) for f in ('anchored-epoch.py','catalogue-reply.py','acoustic-clarification.py','catalogue-agreement.py','version-bound-payload.py')]
    _,raw,_=v['build'](root);old,new=raw;long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(SEED);rows=[];stats={};spec=[];witness=None
    for s,profiles in books.items():
        for length,book in profiles.items():
            width=4 if length==13 else 5;n=len(book);ctx=g['digest'](s,length,book).digest()
            def tag(w,recipient=1):return tuple(c['digits'](int.from_bytes(hmac.digest(z['KEY'],b'MHAC-048-recipient\0'+bytes([recipient])+ctx+bytes(w),'sha256'),'big')%17**8,8))
            roster=[tuple(c['digits'](8,2)+c['digits'](j,2)+[15]) for j in range(3)]
            def body(j,i):return roster[j]+tuple(c['digits'](int(i),width))
            cases=['clean','reverse-tags','tags-first','noise','missing-body','missing-tag','duplicate-tag','foreign-tag','conflicting-body']
            collision=None
            if s==0 and length==18:
                seen={tag(body(0,i)):i for i in range(n)}
                for j in range(n):
                    t=tag(body(1,j))
                    if t in seen and seen[t]!=j:
                        collision=(seen[t],j);witness=dict(source=s,length=length,addresses=collision,tag=t,searched_left=n,searched_right=j+1);break
                assert collision is not None
                cases+=['collision','collision-missing-body','collision-missing-tag']
            for sample in range(4):
                targets=list(map(int,rng.choice(n,3,False)))
                for case in cases:
                    ids=targets if not case.startswith('collision') else [*collision,next(i for i in targets if i not in collision)]
                    bs=[body(j,i) for j,i in enumerate(ids)];ts=[tag(w) for w in bs]
                    for mode in ('fifo','header','graph'):
                        events=[];traces=[];pcm=[];seed=SEED*1000+len(rows)*20
                        def emit(role,w):
                            obs,x,tr=a['exchange'](c['encode'](list(w),4),2500 if case=='noise' else 0,seed+len(events));got=c['decode'](obs,4) if obs is not None else None
                            assert tuple(got)==tuple(w);events.append((role,got));traces.append(dict(role=role,**tr));pcm.append(x)
                        def bodies():
                            for j,w in enumerate(bs):
                                if j==1 and case in ('missing-body','collision-missing-body'):continue
                                emit('body',w)
                            if case=='conflicting-body':emit('body',body(1,(ids[1]+1)%n))
                        def tags():
                            for j in ([2,1,0] if case=='reverse-tags' else range(3)):
                                if j==1 and case=='missing-tag' or j==0 and case=='collision-missing-tag':continue
                                t=tag(bs[j],2) if j==1 and case=='foreign-tag' else ts[j];w=roster[j]+t if mode=='header' else t
                                emit('tag',w)
                                if j==0 and case=='duplicate-tag':
                                    events.append(events[-1]);traces.append(dict(traces[-1],replay=True));pcm.append(pcm[-1])
                        if case=='tags-first':tags();bodies()
                        else:bodies();tags()
                        returned,checks=associate(mode,roster,events,tag);values=[c['index'](returned[k][5:]) if k in returned else None for k in roster];status=['withheld' if x is None else 'correct' if x==y else 'wrong' for x,y in zip(values,ids)]
                        if case=='collision-missing-tag' and values[0] is not None:status[0]='unwitnessed'
                        row=dict(source=s,length=length,sample=sample,case=case,mode=mode,seed=seed,targets=ids,returned=values,status=status,checks=checks,frames=traces,slots=sum(t['slots'] for t in traces));rows.append(row);stats.setdefault(mode+':'+case,Counter()).update(status)
                        if s==0 and length==18 and sample==0 and case in ('reverse-tags','collision','collision-missing-body','collision-missing-tag'):
                            name=mode+'-'+case+'.wav';x=np.concatenate(pcm)
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(x.tobytes())
                            spec.append(dict(file=name,pcm_sha256=sha(x.tobytes()),status=status,peak=int(abs(x).max())))
    receipt=dict(schema='mhac-concurrent-association-v1',pin=PIN,blobs=PINS,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,trials=len(rows),frames=sum(len(r['frames']) for r in rows),stats=stats,collision=witness,specimens=spec,limits='Three predeclared pending headers; same recipient and catalogue per batch; known frame roles and boundaries, closure supplied externally; queries not rendered, reply-only cost. Exact duplicate decoded tag words collapsed, conflicting bodies refused. No timeout, blind acquisition, overlap, allocator, secret key, active forgery, human evidence or action authority. Collision selected, not a random channel rate. Unwitnessed means correct body admitted without its own transmitted tag in the collision-missing-tag fixture.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Concurrent association</title><h1>Concurrent association</h1><p>Synthetic only. Low volume, no autoplay.</p>'+''.join(f'<p>{s["file"]}: {s["status"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>');(out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
