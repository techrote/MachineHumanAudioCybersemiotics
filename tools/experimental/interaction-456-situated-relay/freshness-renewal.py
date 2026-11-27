"""Interaction #456 / Draft #457: synthetic freshness-bound renewal, no device control.
Run: python freshness-renewal.py grammar NEW_OUTPUT
Counter outside the restored snapshot is a stipulated fault boundary, not authentication.
"""
import collections, itertools, json, pathlib, runpy, shutil, sqlite3, sys, tempfile, wave
import numpy as np
PARENT='09c166145fc3e905630bb51a8ec9c5e5ed36877d'
POLICIES=('unbound','local-counter','separate-counter')
FAULTS=('clean','stale-grant','stale-request','dual-rollback','all-rollback','grant-loss','alternate')

def simulate(wire,targets,policy,fault,budget,root,api):
    root.mkdir(); init,state=api['init'],api['state']; local,peer,nonce=[root/x for x in ('issuer.db','peer.db','nonce.db')]
    init(local);init(peer)
    with sqlite3.connect(nonce) as d:d.execute('CREATE TABLE counter(n INTEGER NOT NULL)');d.execute('INSERT INTO counter VALUES(0)')
    ns=root/'nonce.snapshot';ps=root/'peer.snapshot';ls=root/'issuer.snapshot';shutil.copyfile(nonce,ns);shutil.copyfile(peer,ps)
    def challenge():
        with sqlite3.connect(nonce) as d:
            d.execute('PRAGMA synchronous=FULL');d.execute('BEGIN IMMEDIATE');n,=d.execute('SELECT n FROM counter').fetchone();assert 0<=n<289;d.execute('UPDATE counter SET n=?',(n+1,));return wire.c['digits'](n,2)
    requests={};grants={};sent={};events=[];clips=[];need=True
    for t,target in enumerate(targets):
        agent=t%2;slots=0;issued=chosen=origin=None;attempts=[];notice=False;reason=1
        def play(f):
            nonlocal slots
            assert slots+f['slots']<=budget;slots+=f['slots'];clips.append(f['pcm']);return f['word']
        rollback=t==4 and fault not in ('clean','alternate')
        if rollback:
            shutil.copyfile(ls,local);need=True
            if policy=='local-counter' or fault=='all-rollback':shutil.copyfile(ns,nonce)
            if fault in ('dual-rollback','all-rollback'):shutil.copyfile(ps,peer)
        g,n=state(local)
        if need or n==4:
            need=True;reason=2;h=[agent]+challenge();query=wire.frame([9]+h)
            for k in range(2):
                pg,_=state(peer)
                if pg==3:reason=1;break
                if slots+21>budget:break
                requests[t,k]=query;request_origin=(0,0) if fault=='stale-request' and t==4 and k==0 else (t,k)
                q=requests[request_origin];word=play(q);assert word is not None and word[0]==9
                pg,_=state(peer,lambda g,n:(g+1,0));fresh=wire.frame([10]+word[1:]+[pg]);grants[t,k]=fresh
                grant_origin=(0,0) if (fault in ('stale-grant','all-rollback') and t==4 and k==0) else (t,k)
                reply=grants[grant_origin]
                if fault=='grant-loss' and t==4 and k==0:reply=wire.frame(fresh['word'],True)
                got=play(reply);accepted=got is not None and got[:2]==[10,agent] and (policy=='unbound' or got[:-1]==[10]+h)
                attempts.append(dict(k=k,challenge=h,request_origin=request_origin,request_hash=q['hash'],request_emitted=query['hash'],grant_origin=grant_origin,grant_hash=reply['hash'],grant_emitted=fresh['hash'],decoded=got,accepted=accepted))
                if accepted:g,n=state(local,lambda g,n:(got[-1],0));need=False;break
                # Retry only missing transport, not a conflicting grant.
                if got is not None:break
        if t==0:shutil.copyfile(local,ls)
        if not need and slots+22<=budget:
            g,n=state(local);issued=[g,n,agent];state(local,lambda g,n:(g,n+1));assert play(wire.frame([6]+issued))==[6]+issued
            value=(target+1)%289 if fault=='alternate' and t%3==2 else target
            sent[t]=wire.frame([7]+issued+wire.c['digits'](value,2));origin=t
            if fault not in ('clean','alternate') and 4<=t<8 and t-4 in sent:origin=t-4
            reply=sent[origin];got=play(reply)
            if got is not None and got[:-2]==[7]+issued:chosen=wire.c['index'](got[-2:])
        elif need and slots+9<=budget:notice=play(wire.frame([8,agent,reason]))==[8,agent,reason]
        events.append(dict(t=t,agent=agent,rollback=rollback,attempts=attempts,issued=issued,origin=origin,emitted=sent[t]['hash'] if t in sent else None,received=sent[origin]['hash'] if origin is not None else None,target=target,chosen=chosen,slots=slots,notice=notice,reason=reason if need else None,status='refused' if need else 'abstain' if chosen is None else 'correct' if chosen==target else 'wrong'))
    return dict(policy=policy,fault=fault,budget=budget,events=events),clips

def audit(row):
    sent={};requests={};grants={}
    for e in row['events']:
        t=e['t'];assert e['slots']<=row['budget'];assert e['issued'] is not None or e['chosen'] is None
        for a in e['attempts']:
            key=(t,a['k']);requests[key]=a['request_emitted'];grants[key]=a['grant_emitted']
            assert a['request_hash']==requests[tuple(a['request_origin'])]
            if a['decoded'] is not None:assert a['grant_hash']==grants[tuple(a['grant_origin'])]
            if a['accepted'] and row['policy']!='unbound':assert a['decoded'][:-1]==[10]+a['challenge']
        if e['emitted'] is not None:sent[t]=e['emitted']
        if e['origin'] is not None:assert e['received']==sent[e['origin']]
        assert e['status']==('refused' if e['reason'] is not None else 'abstain' if e['chosen'] is None else 'correct' if e['chosen']==e['target'] else 'wrong')


def run(grammar,out):
    here=pathlib.Path(__file__).parent;api=runpy.run_path(str(here/'namespace-renewal.py'));sha=api['sha']
    for name,digest in [('namespace-renewal.py','165d10a3c6c2228ad1cf7f386d7ed0232b8379962b4db8aadb455b7fb15c38e6'),('persistent-issuance.py','1fa37fe83a4362501bc2550c33177e6147394a2828010c15e04eb2c4a29a94dc'),('epoch-repair.py','c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685')]:assert sha((here/name).read_bytes())==digest
    a,c=runpy.run_path(str(here/'epoch-repair.py'))['load'](grammar);Wire=runpy.run_path(str(here/'persistent-issuance.py'))['Wire'];out.mkdir();rows=[];stats={};frames=0
    with tempfile.TemporaryDirectory() as tmp:
        for seed in (4565700,4565701,4565702):
            wire=Wire(a,c,seed);targets=np.random.default_rng(seed).choice(289,12,replace=False).tolist()
            for p,f,b in itertools.product(POLICIES,FAULTS,(43,64)):
                path=pathlib.Path(tmp)/str(len(rows));r,clips=simulate(wire,targets,p,f,b,path,api);assert r==simulate(wire,targets,p,f,b,path.with_suffix('.repeat'),api)[0];r['seed']=seed;rows.append(r)
                audit(r)
                s=stats.setdefault(f'{p}:{f}:{b}',collections.Counter())
                for e in r['events']:
                    s[e['status']]+=1;s['slots']+=e['slots'];s['stale']+=int(e['chosen'] is not None and e['origin']!=e['t']);s['retries']+=max(0,len(e['attempts'])-1);s['notices']+=int(e['notice'])
                if seed==4565700 and b==64 and f=='stale-grant':
                    pcm=np.concatenate(clips).astype('<i2');assert abs(pcm.astype('int32')).max()<=1500
                    with wave.open(str(out/(p+'.wav')),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
            frames+=len(wire.bank)
    for b in (43,64):
        assert stats[f'local-counter:stale-grant:{b}']['stale']==12
        assert stats[f'separate-counter:stale-grant:{b}']['stale']==0
        assert stats[f'separate-counter:dual-rollback:{b}']['stale']==12
        assert stats[f'separate-counter:all-rollback:{b}']['stale']==12
        assert all(stats[f'{p}:clean:{b}']['correct']==36 for p in POLICIES)
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),stats=stats,python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,numpy=np.__version__,limits='Scripted closed SQLite snapshots; separate counter survives only stipulated faults; aligned PCM, unauthenticated, no human evidence.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Freshness renewal</title><h1>Freshness renewal laboratory</h1><p>Fictional actions only. Audio optional; start with low system volume.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565700])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=r.policy+' / '+r.fault+' / '+r.budget+' slots';s.append(o)});function draw(){document.querySelector('#event').textContent=JSON.stringify(rows[+s.value].events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
