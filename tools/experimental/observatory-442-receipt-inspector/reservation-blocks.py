"""Refs #442 / Draft #443. Synthetic allocation experiment, not a security protocol.
python reservation-blocks.py NEW_OUTPUT_DIR (Python standard library only).
One exclusive serialized owner; reopen discards volatile reservations. No power-loss claim.
"""
import hashlib, itertools, json, pathlib, runpy, shutil, sqlite3, sys, tempfile
PARENT='dcf42f8c25d075b8a6856545bc898fad48ece2c7'
PARENT_SHA='8daedd95fab5c6d3439842a3d83cc35eb39a3f860c623e4e2424efe0d27775fc'
CAP=289*289
MODES=('epoch',1,8,32,289)

def upstream():
    p=pathlib.Path(__file__).with_name('epoch-capacity.py')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==PARENT_SHA
    return runpy.run_path(str(p))

class Blocks:
    def __init__(self,path,width,start=None):
        self.db=sqlite3.connect(path);self.width=width;self.lo=self.hi=0;self.pending=None;self.writes=0
        self.db.execute('PRAGMA synchronous=FULL')
        with self.db:
            self.db.execute('CREATE TABLE IF NOT EXISTS cursor (n INTEGER NOT NULL CHECK(n BETWEEN 0 AND 83521))')
            if start is not None:self.db.execute('INSERT INTO cursor VALUES(?)',(start,))
        assert self.db.execute('SELECT count(*) FROM cursor').fetchone()[0]==1
    def reserve(self):
        assert self.pending is None
        if self.lo==self.hi:
            with self.db:
                self.db.execute('BEGIN IMMEDIATE');n=self.cursor()
                if n==CAP:return None
                end=min(CAP,n+self.width,(n//289+1)*289)
                self.db.execute('UPDATE cursor SET n=?',(end,))
            self.lo,self.hi=n,end;self.writes+=1
        self.pending=divmod(self.lo,289);self.lo+=1;return self.pending
    def cursor(self):return self.db.execute('SELECT n FROM cursor').fetchone()[0]
    def consume(self,t):
        if t is None or self.pending!=t:return False
        self.pending=None;return True
    def abandon(self):self.pending=None
    def tail(self):return self.hi-self.lo
    def close(self):self.db.close()

def trial(root,up,mode,start,interval,budget,fault,horizon=64):
    path=root/'trial.db';lost=spent=correct=writes=0;events=[];seen=set();stop='horizon'
    if mode=='epoch':
        db=up['Ledger'](path,289,False)
        with db.db:db.db.execute('UPDATE state SET next=?',(start//289,))
        s=up['Session'](db)
        cursor=lambda:db.db.execute('SELECT next FROM state').fetchone()[0]*289
        tail=lambda:0 if s.epoch is None else 289-s.seq
    else:s=Blocks(path,mode,start);cursor=lambda:s.cursor();tail=lambda:s.tail()
    for i in range(horizon):
        if spent+26>budget:stop='deadline';break
        before=cursor();t=s.reserve();after=cursor()
        if t is None:stop='exhausted';break
        writes+=(2 if mode=='epoch' else 1)*int(after!=before)
        assert t not in seen and start<=t[0]*289+t[1]<CAP;seen.add(t)
        status=('correct','abandon','query-refused','reply-refused','correct')[i%5] if fault=='mixed' else 'correct'
        cost={'correct':26,'abandon':0,'query-refused':11,'reply-refused':26}[status]
        if status=='correct':assert s.consume(t);correct+=1
        else:s.abandon()
        spent+=cost;discard=0
        if interval and (i+1)%interval==0:
            discard=tail();lost+=discard
            if mode=='epoch':db.close();db=up['Ledger'](path,289,False);s=up['Session'](db)
            else:s.close();s=Blocks(path,mode)
            assert not s.consume(t)
        events.append(dict(turn=i,token=t,status=status,slots=cost,cursor=after,discard=discard))
    end=cursor();live=tail()
    assert end-start==len(events)+lost+live and spent<=budget
    assert len(seen)==len(events)
    if mode=='epoch':db.close()
    else:s.close()
    path.unlink()
    return dict(mode=mode,start=start,interval=interval,budget=budget,fault=fault,stop=stop,correct=correct,spent=spent,writes=writes,lost=lost,live_tail=live,unallocated=CAP-end,events=events)

def witnesses(root,up):
    a=trial(root,up,'epoch',CAP-289,1,9000,'clean',300)
    b=trial(root,up,1,CAP-289,1,9000,'clean',300)
    assert (a['correct'],a['lost'],a['stop'])==(1,288,'exhausted')
    assert (b['correct'],b['lost'],b['stop'])==(289,0,'exhausted')
    c=trial(root,up,8,0,0,9000,'clean',300)
    assert c['events'][288]['token']==(0,288) and c['events'][289]['token']==(1,0)
    rollback={}
    for width in (1,8,32,289):
        p=root/'rollback.db';snap=root/'snapshot.db';s=Blocks(p,width,0);s.close();shutil.copyfile(p,snap)
        s=Blocks(p,width);old=s.reserve();assert s.consume(old);s.close()
        s=Blocks(p,width);new=s.reserve();assert new!=old and not s.consume(old);s.close()
        shutil.copyfile(snap,p);s=Blocks(p,width);restored=s.reserve();assert restored==old and s.consume(old);s.close();p.unlink()
        rollback[str(width)]=dict(old=old,reopened=new,restored=restored)
    return dict(final_epoch=[a,b],rollover=c,rollback=rollback)

def run(out):
    up=upstream();out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp);w=witnesses(root,up)
        rows=[trial(root,up,*args) for args in itertools.product(MODES,(0,CAP-289),(0,1,4,16),(720,2600),('clean','mixed'))]
    for a,b in zip(rows[:32],rows[-32:]):
        assert {k:v for k,v in a.items() if k not in ('mode','writes')}=={k:v for k,v in b.items() if k not in ('mode','writes')}
    for r in rows:
        es=r['events'];assert sum(e['status']=='correct' for e in es)==r['correct'] and sum(e['discard'] for e in es)==r['lost'] and sum(e['slots'] for e in es)==r['spent']
    receipt=dict(schema='mhac-reservation-blocks-v1',parent=PARENT,parent_sha256=PARENT_SHA,source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,evaluations=len(rows),groups=len(rows)//len(MODES),events=sum(len(r['events']) for r in rows),limits='Actual SQLite transactions; one exclusive owner, close/reopen not crash or power loss. Allocation commits only (epoch baseline reserve+consume); excludes initialization, reopen cleanup, filesystem sync count and timing. Symbolic 11+15 slots, 80 ms each; complete-exchange preflight, no physical channel, MAC, action or human evidence. Deterministic schedules, no random sampling. Rollback remains unsafe.')
    for name,data in [('receipt',receipt),('traces',rows),('witnesses',w)]:
        (out/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    summary=[{k:v for k,v in r.items() if k!='events'} for r in rows]
    html='''<!doctype html><meta charset="utf-8"><title>Reservation blocks</title><style>body{font:16px system-ui;max-width:1050px;margin:2em auto;padding:1em;background:#14212a;color:#e0edf2}select{margin:1em;padding:.4em}table{border-collapse:collapse;width:100%}td,th{padding:.6em;border-bottom:1px solid #516474;text-align:left}a{color:#9bd9f5}</style><h1>Reservation block laboratory</h1><p>Native SQLite; symbolic communication. One exclusive owner; no power-loss, MAC or human evidence. Lost = unused identifiers discarded on restart; live tail remains usable until restart.</p><div id="filters"></div><table><thead><tr><th>Block</th><th>Correct</th><th>Lost</th><th>Live tail</th><th>Allocation commits</th><th>Slots</th><th>Stop</th></tr></thead><tbody id="rows"></tbody></table><p><a href="traces.json">Traces</a> | <a href="witnesses.json">Boundary witnesses</a> | <a href="receipt.json">Receipt</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;const fields={start:[0,83232],interval:[0,1,4,16],budget:[720,2600],fault:['clean','mixed']};for(const [k,vs] of Object.entries(fields)){const l=document.createElement('label');l.textContent=k;const s=document.createElement('select');s.id=k;for(const v of vs)s.add(new Option(v,v));s.onchange=draw;l.append(s);document.getElementById('filters').append(l)}function draw(){const a=data.filter(r=>Object.keys(fields).every(k=>String(r[k])===document.getElementById(k).value));document.getElementById('rows').replaceChildren(...a.map(r=>{const t=document.createElement('tr');for(const v of [r.mode,r.correct,r.lost,r.live_tail,r.writes,r.spent,r.stop]){const d=document.createElement('td');d.textContent=v;t.append(d)}return t}))}draw()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(summary,separators=(',',':'))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]))
