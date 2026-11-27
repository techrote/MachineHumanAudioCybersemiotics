"""Measurement #442 / Draft #443. Synthetic capacity accounting, no action authority.
Run: python epoch-capacity.py NEW_OUTPUT_DIR
Ledger and Session excerpts from pinned Grammar; no new PCM or security claim.
"""
import hashlib, json, pathlib, shutil, sqlite3, sys, tempfile
from collections import Counter
from itertools import product
PIN='a9dfa879ea17c2adc33d40ebb0d41e6cae34addd'
ANCHOR='ad0ec7c854459af609283602def017cf17e5c8f0'

class Ledger:
    # One serialized receiver per DB, one outstanding query. Reopen abandons pending.
    def __init__(self,path,limit,wrap):
        self.db=sqlite3.connect(path);self.limit=limit;self.wrap=wrap
        self.db.execute('PRAGMA synchronous=FULL')
        with self.db:
            self.db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), next INTEGER NOT NULL, pending INTEGER)')
            self.db.execute('INSERT OR IGNORE INTO state VALUES(1,0,NULL)')
            self.db.execute('UPDATE state SET pending=NULL WHERE id=1')
    def reserve(self):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE');n,p=self.db.execute('SELECT next,pending FROM state').fetchone()
            if p is not None:raise ValueError('outstanding query')
            if not self.wrap and n>=self.limit:return None
            token=n%self.limit;self.db.execute('UPDATE state SET next=?,pending=?',(n+1,token));return token
    def consume(self,token):
        with self.db:
            cur=self.db.execute('UPDATE state SET pending=NULL WHERE pending=?',(token,));return cur.rowcount==1
    def abandon(self):
        with self.db:self.db.execute('UPDATE state SET pending=NULL')
    def close(self):self.db.close()

class Session:
    # Allocator must be outside the rollback boundary for the anchored claim.
    def __init__(self,allocator):self.allocator=allocator;self.epoch=None;self.seq=289;self.pending=None
    def reserve(self):
        if self.pending is not None:raise ValueError('outstanding')
        if self.seq==289:
            self.epoch=self.allocator.reserve()
            if self.epoch is None:return None
            assert self.allocator.consume(self.epoch);self.seq=0
        self.pending=(self.epoch,self.seq);self.seq+=1;return self.pending
    def abandon(self):self.pending=None
    def consume(self,t):
        if self.pending!=t or t is None:return False
        self.pending=None;return True

MODES=('wrap17','durable289','anchored','anchored-mac')
FAULTS=('clean','abandon','query','reply','restart','mixed')
def costs(mode,length):
    width=4 if length==13 else 5
    return (7,9+width) if mode in MODES[:2] else (11,11+width+(19 if mode=='anchored-mac' else 0))
def fault(case,i):
    if case=='mixed':return ('ok','abandon','query','reply','restart')[i%5]
    return case if case!='clean' and i%3==1 else 'ok'
def simulate(path,mode,length,start,budget,case):
    anchored=mode in MODES[2:];db=Ledger(path,17 if mode=='wrap17' else 289,mode=='wrap17');s=Session(db) if anchored else db
    for _ in range(start):
        assert s.reserve() is not None;s.abandon()
    q,r=costs(mode,length);spent=0;events=[];seen=set();counts=Counter()
    for i in range(24):
        f=fault(case,i)
        # Admission checks the complete scheduled exchange before burning a token.
        if spent+q+r>budget:events.append(dict(turn=i,status='deadline',spent=spent));break
        token=s.reserve()
        if token is None:events.append(dict(turn=i,status='exhausted',spent=spent));break
        repeated=token in seen;seen.add(token);counts['reuse']+=repeated
        if f=='abandon':s.abandon();cost=0;status=f
        elif f=='query':s.abandon();cost=q;status=f
        elif f=='reply':s.abandon();cost=q+r;status=f
        elif f=='restart':
            # Reservation committed, then process restarts before emitting a query.
            db.close();db=Ledger(path,17 if mode=='wrap17' else 289,mode=='wrap17');s=Session(db) if anchored else db;cost=0;status=f
        else:assert s.consume(token);cost=q+r;status='correct'
        spent+=cost;counts[status]+=1;counts['reservations']+=1
        events.append(dict(turn=i,status=status,token=token,reused=repeated,cost=cost,spent=spent))
    epochs=db.db.execute('SELECT next FROM state').fetchone()[0];db.close()
    assert spent==sum(e.get('cost',0) for e in events)<=budget
    assert counts['reservations']==sum(counts[k] for k in ('correct','abandon','query','reply','restart'))
    return dict(mode=mode,length=length,start=start,budget=budget,case=case,spent=spent,allocator_next=epochs,counts=dict(counts),stop=events[-1]['status'] if len(events)<24 or events[-1]['status'] in ('deadline','exhausted') else 'horizon',events=events)
def witnesses(root):
    p=root/'rollback.db';d=Ledger(p,289,False);d.close();snap=root/'snapshot.db';shutil.copyfile(p,snap)
    d=Ledger(p,289,False);old=d.reserve();assert d.consume(old);d.close()
    d=Ledger(p,289,False);new=d.reserve();assert not d.consume(old);d.abandon();d.close()
    shutil.copyfile(snap,p);d=Ledger(p,289,False);restored=d.reserve();assert d.consume(old);d.close()
    p=root/'anchor.db';d=Ledger(p,289,False);d.close();snap=root/'anchor-snapshot.db';shutil.copyfile(p,snap)
    d=Ledger(p,289,False);s=Session(d);old_a=s.reserve();assert s.consume(old_a);s=Session(d);new_a=s.reserve();assert not s.consume(old_a);d.close()
    shutil.copyfile(snap,p);d=Ledger(p,289,False);s=Session(d);restored_a=s.reserve();assert s.consume(old_a);d.close()
    assert old==restored and old!=new and old_a==restored_a and old_a!=new_a
    p=root/'last-epoch.db';d=Ledger(p,289,False)
    for i in range(288):assert d.reserve()==i;assert d.consume(i)
    s=Session(d);assert s.reserve()==(288,0);assert s.consume((288,0))
    # Restart discards all 288 unused sequence values in the last allocated epoch.
    s=Session(d);assert s.reserve() is None;d.close()
    return dict(local=dict(old=old,reopened=new,restored=restored),anchor=dict(old=old_a,session_restart=new_a,allocator_rollback=restored_a),last_epoch=dict(allocated=289,used_in_last=1,stranded_by_restart=288,next_reservation=None))
def run(out):
    out.mkdir(parents=True,exist_ok=False);rows=[]
    with tempfile.TemporaryDirectory() as t:
        root=pathlib.Path(t);w=witnesses(root)
        for i,(mode,length,start,budget,case) in enumerate(product(MODES,(13,18),(0,14,280),(120,360,720),FAULTS)):
            p=root/'trial.db';rows.append(simulate(p,mode,length,start,budget,case));p.unlink()
    receipt=dict(schema='mhac-epoch-capacity-v1',pins=dict(epoch=PIN,anchor=ANCHOR),sqlite=sqlite3.sqlite_version,python=sys.version.split()[0],source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),groups=len(rows)//4,evaluations=len(rows),events=sum(len(r['events']) for r in rows),witnesses=w,limits='Actual serialized SQLite reserve/consume/abandon/reopen. Symbolic channel outcomes, no PCM, no MAC computation, no malicious replay injection except token-level rollback witnesses. Preconsumed tokens have zero session airtime; reuse counts are within the observed session only. MAC mode charges the pinned tag-frame cost but does not calculate or verify tags. Full budget preflight; no partial frames, retry, fallback, turnaround or physical timing. 80ms per slot. No human evidence, authentication or action authority.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    compact=[{k:v for k,v in r.items() if k!='events'} for r in rows]
    html='''<!doctype html><meta charset="utf-8"><title>Epoch capacity</title><style>body{font:16px system-ui;background:#14212a;color:#e0edf2;max-width:1000px;margin:2em auto;padding:1em}select{margin:.4em;padding:.4em}table{border-collapse:collapse;width:100%}td,th{padding:.6em;border-bottom:1px solid #516474;text-align:left}a{color:#9bd9f5}</style><h1>Epoch capacity laboratory</h1><p>Synthetic symbolic channel; native SQLite reservations. No human or authentication evidence. Full-budget preflight, no partial airtime.</p><div id="controls"></div><table><thead><tr><th>Policy</th><th>Correct</th><th>Burned</th><th>Reused (observed)</th><th>Slots spent</th><th>Stop</th></tr></thead><tbody id="rows"></tbody></table><p><a href="receipt.json">Receipt</a> | <a href="traces.json">Full event traces</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;const fields={length:[13,18],start:[0,14,280],budget:[120,360,720],case:['clean','abandon','query','reply','restart','mixed']};for(const [k,vs] of Object.entries(fields)){const l=document.createElement('label');l.textContent=k;const s=document.createElement('select');s.id=k;for(const v of vs)s.add(new Option(v,v));s.onchange=draw;l.append(s);document.getElementById('controls').append(l)}function draw(){const selected=data.filter(r=>Object.keys(fields).every(k=>String(r[k])===document.getElementById(k).value));document.getElementById('rows').replaceChildren(...selected.map(r=>{const tr=document.createElement('tr');for(const v of [r.mode,r.counts.correct||0,(r.counts.reservations||0)-(r.counts.correct||0),r.counts.reuse||0,r.spent,r.stop]){const td=document.createElement('td');td.textContent=v;tr.append(td)}return tr}))}draw()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(compact,separators=(',',':'))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]))
