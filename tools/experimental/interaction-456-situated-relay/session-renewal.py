"""Interaction #456 / Draft #457, synthetic-only, AI-assisted.
Run: python session-renewal.py grammar NEW_OUTPUT
Aligned PCM, honest peers, no authentication, no human evidence or device control.
"""
import collections, contextlib, itertools, json, pathlib, runpy, shutil, sqlite3, sys, tempfile, wave
import numpy as np
PARENT='e1f8d1b27d64f54c9cb30460af8ddcdf28f3406c'
POLICIES=('header','bound','header-idempotent','bound-idempotent')
FAULTS=('clean','dual-rollback','all-rollback','stale-request','stale-grant','grant-loss','alternate','exhaustion')
CAP=4

def sql(path, fn, create=False):
    with contextlib.closing(sqlite3.connect(str(path) if create else path.resolve().as_uri()+'?mode=rw',uri=not create)) as db:
        db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE')
        result=fn(db);db.commit();return result

def provision(path,ddl):
    def init(db):
        for statement in ddl:db.execute(statement)
    sql(path,init,True)

def grant(path,request,idempotent):
    agent,lo,hi=request[1:];nonce=lo+17*hi
    def allocate(db):
        old=db.execute('SELECT g FROM grants WHERE agent=? AND nonce=?',(agent,nonce)).fetchone()
        if idempotent and old is not None:return old[0],False
        n,=db.execute('SELECT n FROM counter').fetchone()
        if n==CAP:return 16,False
        db.execute('UPDATE counter SET n=n+1');db.execute('INSERT OR REPLACE INTO grants VALUES(?,?,?)',(agent,nonce,n));return n,True
    return sql(path,allocate)

def simulate(wire,targets,policy,fault,budget,root):
    root.mkdir();issuer,peer,counter=(root/x for x in ('issuer.db','peer.db','nonce.db'))
    provision(issuer,['CREATE TABLE state(g,n,lo,hi)','INSERT INTO state VALUES(-1,0,0,0)'])
    provision(peer,['CREATE TABLE counter(n)','INSERT INTO counter VALUES(0)','CREATE TABLE grants(agent,nonce,g,PRIMARY KEY(agent,nonce))'])
    provision(counter,['CREATE TABLE counter(n)','INSERT INTO counter VALUES(0)'])
    for p in (issuer,peer,counter):shutil.copyfile(p,p.with_suffix('.snapshot'))
    def challenge(db):
        n,=db.execute('SELECT n FROM counter').fetchone();assert 0<=n<289
        db.execute('UPDATE counter SET n=n+1');return wire.c['digits'](n,2)
    events=[];clips=[];sent={};queries={};grants={};bound=policy.startswith('bound');idem=policy.endswith('idempotent')
    for t,target in enumerate(targets):
        agent=t%2;slots=0;attempts=[];chosen=origin=header=received=None;notice=False;reason=None
        def play(f):
            nonlocal slots
            slots+=f['slots'];assert slots<=budget;clips.append(f['pcm']);return f['word']
        if t==4 and fault in ('dual-rollback','all-rollback','stale-request','stale-grant','grant-loss'):
            shutil.copyfile(issuer.with_suffix('.snapshot'),issuer)
            if fault in ('dual-rollback','all-rollback'):shutil.copyfile(peer.with_suffix('.snapshot'),peer)
            if fault=='all-rollback':shutil.copyfile(counter.with_suffix('.snapshot'),counter)
        g,n,lo,hi=sql(issuer,lambda d:d.execute('SELECT * FROM state').fetchone())
        if g<0 or n==CAP:
            reason='renewal-unavailable';h=[agent]+sql(counter,challenge);q=wire.frame([9]+h)
            for k in range(2):
                if slots+q['slots']+11>budget:break
                key=(t,k);queries[key]=q;qo=(0,0) if fault=='stale-request' and key==(4,0) else key
                actual=play(queries[qo]);new,allocated=grant(peer,actual,idem);grants[key]=wire.frame([10]+actual[1:]+[new]);fresh=grants[key]
                go=(0,0) if fault in ('stale-grant','all-rollback') and key==(4,0) else key
                reply=grants[go];lost=fault=='grant-loss' and key==(4,0)
                if lost:reply=wire.frame(fresh['word'],True)
                got=play(reply);matches=got is not None and got[:-1]==[10]+h
                attempts.append(dict(k=k,challenge=h,query_origin=qo,query_hash=queries[qo]['hash'],query_emitted=q['hash'],grant_origin=go,grant_hash=reply['hash'],grant_emitted=fresh['hash'],allocated=allocated,decoded=got,match=matches))
                if matches:
                    if got[-1]==16:reason='exhausted';break
                    g,n,lo,hi=got[-1],0,*h[1:];sql(issuer,lambda d:d.execute('UPDATE state SET g=?,n=?,lo=?,hi=?',(g,n,lo,hi)));reason=None;break
        if reason is None and slots+26<=budget:
            header=[g,n,agent,lo,hi];sql(issuer,lambda d:d.execute('UPDATE state SET n=n+1'))
            q=play(wire.frame([6]+header));assert q==[6]+header
            value=(target+1)%289 if fault=='alternate' and t%3==2 else target
            sent[t]=wire.frame([7]+q[1:]+wire.c['digits'](value,2));origin=t
            if fault in ('dual-rollback','all-rollback') and 4<=t<8 and t-4 in sent:origin=t-4
            r=sent[origin];received=r['hash'];got=play(r)
            if got is not None and (got[:-2]==[7]+header if bound else got[:4]==[7]+header[:3]):chosen=wire.c['index'](got[-2:])
        elif reason is not None and slots+9<=budget:notice=play(wire.frame([8,agent,1 if reason=='exhausted' else 2])) is not None
        events.append(dict(t=t,agent=agent,attempts=attempts,header=header,target=target,chosen=chosen,origin=origin,emitted=sent[t]['hash'] if t in sent else None,received=received,notice=notice,reason=reason,slots=slots,status='refused' if reason else 'abstain' if chosen is None else 'correct' if chosen==target else 'wrong'))
    return dict(policy=policy,fault=fault,budget=budget,events=events),clips

def audit(row):
    sent={};queries={};grants={};s=collections.Counter()
    for e in row['events']:
        t=e['t'];assert e['slots']<=row['budget'];assert e['chosen'] is None or e['header'] is not None
        for a in e['attempts']:
            key=(t,a['k']);queries[key]=a['query_emitted'];grants[key]=a['grant_emitted'];assert a['query_hash']==queries[a['query_origin']]
            if a['decoded'] is not None:assert a['grant_hash']==grants[a['grant_origin']]
            if a['match']:assert a['decoded'][:-1]==[10]+a['challenge']
            s['allocations']+=a['allocated']
        if e['emitted'] is not None:sent[t]=e['emitted']
        if e['origin'] is not None:assert e['received']==sent[e['origin']]
        assert e['status']==('refused' if e['reason'] else 'abstain' if e['chosen'] is None else 'correct' if e['chosen']==e['target'] else 'wrong')
        s[e['status']]+=1;s['slots']+=e['slots'];s['stale']+=int(e['chosen'] is not None and e['origin']!=t);s['notices']+=e['notice']
    return s

def run(grammar,out):
    here=pathlib.Path(__file__).parent;api=runpy.run_path(str(here/'epoch-repair.py'));sha=api['sha']
    for name,digest in [('freshness-renewal.py','16d613b11099e700523bde06e4891496d6e5306e7c49afd2330dd09aa93cad82'),('persistent-issuance.py','1fa37fe83a4362501bc2550c33177e6147394a2828010c15e04eb2c4a29a94dc'),('epoch-repair.py','c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685')]:assert sha((here/name).read_bytes())==digest
    a,c=api['load'](grammar);Wire=runpy.run_path(str(here/'persistent-issuance.py'))['Wire'];out.mkdir();rows=[];stats={};frames=0
    with tempfile.TemporaryDirectory() as tmp:
        for seed in (4565800,4565801):
            wire=Wire(a,c,seed);targets=np.random.default_rng(seed).choice(289,20,replace=False).tolist()
            for p,f,b in itertools.product(POLICIES,FAULTS,(47,68)):
                path=pathlib.Path(tmp)/str(len(rows));ts=targets if f in ('exhaustion','grant-loss') else targets[:12];r,clips=simulate(wire,ts,p,f,b,path);assert r==simulate(wire,ts,p,f,b,path.with_suffix('.repeat'))[0];r['seed']=seed;rows.append(r);stats.setdefault(f'{p}:{f}:{b}',collections.Counter()).update(audit(r))
                if seed==4565800 and b==68 and p in ('header','bound-idempotent') and f in ('dual-rollback','grant-loss'):
                    pcm=np.concatenate(clips).astype('<i2');assert abs(pcm.astype('int32')).max()<=1500
                    with wave.open(str(out/(p+'-'+f+'.wav')),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
            frames+=len(wire.bank)
    for b in (47,68):
        assert stats[f'header:dual-rollback:{b}']['stale']==8 and stats[f'bound:dual-rollback:{b}']['stale']==0
        assert stats[f'bound-idempotent:all-rollback:{b}']['stale']==8
        assert all(stats[f'{p}:clean:{b}']['correct']==24 for p in POLICIES)
        assert all(stats[f'{p}:exhaustion:{b}']['refused']==8 for p in POLICIES)
    assert stats['bound-idempotent:grant-loss:68']['correct']>stats['bound:grant-loss:68']['correct']
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),stats=stats,python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,numpy=np.__version__,limits='Scripted SQLite snapshots, aligned PCM, unauthenticated honest peer; no human evidence.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Session renewal</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto}pre{white-space:pre-wrap}</style><h1>Session renewal laboratory</h1><p>Fictional repair requests. Choose a policy and fault, step through actual decoded events, compare namespace allocations and outcomes. Audio optional; start with low system volume.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><p id="summary"></p><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565800])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=r.policy+' / '+r.fault+' / '+r.budget+' slots';s.append(o)});function draw(){const r=rows[+s.value];document.querySelector('#summary').textContent=(i+1)+' / '+r.events.length+' | '+r.events[i].status;document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows),sum(len(r['events']) for r in rows))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
