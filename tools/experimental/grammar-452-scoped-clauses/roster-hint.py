"""Refs #452 / Draft #453. Roster-scoped acoustic verification hints.
Run: python roster-hint.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Synthetic aligned frames, public fixture key, no human or security qualification.
"""
import hashlib,hmac,json,pathlib,runpy,sys,wave
from collections import Counter
import numpy as np
PIN='36eab4b0abf5e17c25f99a5d27b9bf0edba99e34'
SEED=452500
sha=lambda b:hashlib.sha256(b).hexdigest()

def hinted(roster,events,tag,hints):
    # Never infer uniqueness from received bodies: use the declared full roster.
    bodies={k:set() for k in roster}; tags=set()
    for role,w in events:
        if w is None:continue
        if role=='body' and tuple(w[:5]) in bodies:bodies[tuple(w[:5])].add(tuple(w))
        if role=='tag' and len(w)==9:tags.add(tuple(w))
    result={};checks=0
    for k in roster:
        if len(bodies[k])!=1 or list(hints.values()).count(hints[k])!=1:continue
        w=next(iter(bodies[k])); candidates=[t for t in tags if t[0]==hints[k]]
        checks+=len(candidates)
        if any(t[1:]==tag(w) for t in candidates):result[k]=w
    return result,checks

def run(root,out):
    prev=runpy.run_path(str(root/'concurrent-association.py'));pins=dict(prev['PINS'],**{'concurrent-association.py':'3b756bfdb4149edefdd119ff2f9e54d2dc70280e','detached-verification.py':'dfa11f3af03e9330ca14b8a865456d497c40a823','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401'})
    for f,b in pins.items():assert prev['blob']((root/f).read_bytes())==b,f
    z,c,a,g,v=[runpy.run_path(str(root/f)) for f in ('anchored-epoch.py','catalogue-reply.py','acoustic-clarification.py','catalogue-agreement.py','version-bound-payload.py')]
    _,raw,_=v['build'](root);old,new=raw;long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED);out.mkdir(parents=True,exist_ok=False);rows=[];stats={};spec=[]
    for s,profiles in books.items():
        for length,book in profiles.items():
            n=len(book);width=4 if length==13 else 5;ctx=g['digest'](s,length,book).digest()
            roster=[tuple(c['digits'](8,2)+c['digits'](j,2)+[15]) for j in range(3)]
            def body(j,i):return roster[j]+tuple(c['digits'](int(i),width))
            def tag(w):return tuple(c['digits'](int.from_bytes(hmac.digest(z['KEY'],b'MHAC-048-recipient\0'+bytes([1])+ctx+bytes(w),'sha256'),'big')%17**8,8))
            cases=['clean','reverse','noise','missing-body','missing-tag','conflict','hint-alias']
            if (s,length)==(0,18):
                assert tag(body(0,65931))==tag(body(1,14976))==(5,8,14,12,7,4,1,1)
                cases+=['collision','collision-missing-body','collision-missing-tag','collision-relabel']
            for sample in range(4):
                targets=list(map(int,rng.choice(n,3,False)))
                for case in cases:
                    ids=targets if not case.startswith('collision') else [65931,14976,next(i for i in targets if i not in (65931,14976))]
                    bs=[body(j,i) for j,i in enumerate(ids)];ts=[tag(w) for w in bs]
                    for mode in ('header','graph','hint'):
                        hints=dict(zip(roster,[0,0,1] if case=='hint-alias' else [0,1,2]));events=[];traces=[];pcm=[];seed=SEED*1000+len(rows)*20
                        def emit(role,w):
                            obs,x,tr=a['exchange'](c['encode'](list(w),4),2500 if case=='noise' else 0,seed+len(events));got=c['decode'](obs,4) if obs is not None else None
                            assert tuple(got)==tuple(w);events.append((role,got));traces.append(dict(role=role,**tr));pcm.append(x)
                        for j,w in enumerate(bs):
                            if j==1 and case in ('missing-body','collision-missing-body'):continue
                            emit('body',w)
                        if case=='conflict':emit('body',body(1,(ids[1]+1)%n))
                        for j in ([2,1,0] if case=='reverse' else range(3)):
                            if j==1 and case=='missing-tag' or j==0 and case in ('collision-missing-tag','collision-relabel'):continue
                            k=0 if j==1 and case=='collision-relabel' else j
                            prefix=roster[k] if mode=='header' else (hints[roster[k]],) if mode=='hint' else ()
                            emit('tag',prefix+ts[j])
                        returned,checks=hinted(roster,events,tag,hints) if mode=='hint' else prev['associate'](mode,roster,events,tag)
                        values=[c['index'](returned[k][5:]) if k in returned else None for k in roster];status=['withheld' if x is None else 'correct' if x==y else 'wrong' for x,y in zip(values,ids)]
                        if case in ('collision-missing-tag','collision-relabel') and values[0] is not None:status[0]='unwitnessed'
                        row=dict(source=s,length=length,sample=sample,case=case,mode=mode,seed=seed,roster=roster,hints=list(hints.values()),targets=ids,returned=values,status=status,checks=checks,frames=traces,slots=sum(t['slots'] for t in traces));rows.append(row);stats.setdefault(mode+':'+case,Counter()).update(status)
                        if (s,length,sample)==(0,18,0) and case in ('missing-body','collision-missing-tag','collision-relabel'):
                            name=mode+'-'+case+'.wav';x=np.concatenate(pcm)
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(x.tobytes())
                            spec.append(dict(file=name,pcm_sha256=sha(x.tobytes()),status=status,peak=int(abs(x).max())))
    for r in rows:
        if r['mode']=='hint' and r['case']=='hint-alias':assert r['status']==['withheld','withheld','correct']
        if r['mode']=='hint' and r['case']=='collision-relabel':assert r['status']==['unwitnessed','withheld','correct']
        if r['mode']=='hint' and r['case'] in ('missing-body','missing-tag','conflict','collision-missing-body'):assert r['status']==['correct','withheld','correct']
    receipt=dict(schema='mhac-roster-hint-v1',pin=PIN,blobs=pins,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,batches=len(rows),frames=sum(len(r['frames']) for r in rows),stats=stats,specimens=spec,limits='Predeclared roster and shared hint assignment; no roster negotiation, no retry, known aligned frame roles, externally supplied closure; same recipient and catalogue. One hint digit supports at most 17 unique simultaneous assignments. Aliased slots refused even when received bodies seem unique. Collision retained from Run 049, relabelled header/hint is validly re-encoded, not a random fault. Public test key; no authentication or human evidence. One GPT-6.2 worker, no independent review.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Roster hints</title><h1>Roster-scoped verification hints</h1><p>Synthetic only. Low volume, no autoplay.</p>'+''.join(f'<p>{s["file"]}: {s["status"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>');(out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
