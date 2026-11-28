"""Refs #452 / Draft #453. Synthetic aligned acoustic replay, no action authority.
python epoch-replay.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
One GPT-6.2 worker; no human evidence, authentication or independent review.
"""
import hashlib, json, pathlib, runpy, shutil, sqlite3, sys, tempfile, wave
from collections import Counter
import numpy as np
PIN='33228efc8363a0814a36ebfd175ecfef9920e364'
PINS={'session-catalogue.py':'46704d34946ca860cad7543914d00f5a95a683b5','catalogue-reply.py':'8b07a9dde7dd7250b490263c3044aeb798453019'}
SEED=452460
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

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

def run(root,out):
    c=runpy.run_path(str(root/'catalogue-reply.py')); pins={**PINS,**c['BLOBS']}
    for f,b in pins.items():assert blob((root/f).read_bytes())==b,f
    a=runpy.run_path(str(root/'acoustic-clarification.py'));v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root)
    lengths={13:len(raw[0]),18:sum(map(len,raw))};out.mkdir(parents=True,exist_ok=False)
    rows=[];stats={};spec=[];rng=np.random.default_rng(SEED);frames=0
    def receive(pcm):
        scores=abs(pcm[:,80:480]@a['BASIS'].T)*2/400
        obs=[int(z.argmax()) if z.max()>=600 else None for z in scores]
        return obs[1:-1] if obs[0]==17 and obs[-1]==18 and all(x is None or x<17 for x in obs[1:-1]) else None
    modes=('volatile17','durable17','durable289');cases=('clean','duplicate','wrap17','restart','pending-crash','rollback','fresh-alternate','exhaustion')
    for source in (0,1):
        for length,n in lengths.items():
            width=4 if length==13 else 5
            for case in cases:
                old,target=map(int,rng.choice(n,2,False))
                for mode in modes:
                    limit=289 if mode=='durable289' else 17;wrap=mode!='durable289';seed=SEED*1000+len(rows)*10
                    with tempfile.TemporaryDirectory() as tmp:
                        path=pathlib.Path(tmp)/'state.db';db=Ledger(path,limit,wrap)
                        db.close();snapshot=path.with_suffix('.snapshot');shutil.copyfile(path,snapshot);db=Ledger(path,limit,wrap)
                        def reopen(reset=False):
                            nonlocal db
                            db.close()
                            if reset:path.unlink()
                            db=Ledger(path,limit,wrap)
                        def reply(token,identity,offset):
                            nonlocal frames
                            req=c['digits'](token,2)+[15];obs,qpcm,qt=a['exchange'](a['code'](req),0,seed+offset);frames+=1
                            q=a['recover'](obs);assert q==req
                            _,pcm,rt=a['exchange'](c['encode'](q+c['digits'](identity,width),4),0,seed+offset+1);frames+=1
                            return pcm,qt,rt
                        def admit(pcm):
                            obs=receive(pcm);z=c['decode'](obs,4) if obs is not None and len(obs)==7+width else None
                            if z is None or z[2]!=15 or c['index'](z[3:])>=n:return None
                            return c['index'](z[3:]) if db.consume(c['index'](z[:2])) else None
                        t0=db.reserve();assert t0==0;capture,q0,r0=reply(t0,old,0)
                        if case=='pending-crash':reopen(mode=='volatile17')
                        else:assert admit(capture)==old
                        if case=='restart':reopen(mode=='volatile17')
                        if case=='rollback':
                            db.close();shutil.copyfile(snapshot,path);db=Ledger(path,limit,wrap) # restore old committed state
                        if case in ('wrap17','exhaustion'):
                            count=16 if case=='wrap17' else 288
                            for _ in range(count):assert db.reserve() is not None;db.abandon()
                        token=None if case=='duplicate' else db.reserve();qt=rt=None
                        if case=='clean' or case=='fresh-alternate':
                            pcm,qt,rt=reply(token,target if case=='clean' else old,2)
                        else:
                            pcm=capture.copy() # actual byte-identical recorded response replay
                            if token is not None:
                                req=c['digits'](token,2)+[15];obs,_,qt=a['exchange'](a['code'](req),0,seed+2);frames+=1
                                assert a['recover'](obs)==req
                        got=admit(pcm);db.close()
                        status='withheld' if got is None else 'correct' if got==target else 'wrong'
                        expected='correct' if case=='clean' else 'wrong' if case in ('rollback','fresh-alternate') or (case in ('wrap17','exhaustion') and wrap) or (case in ('restart','pending-crash') and mode=='volatile17') else 'withheld'
                        assert status==expected,(case,mode,status)
                        if case=='exhaustion' and not wrap:assert token is None
                        row=dict(source=source,length=length,mode=mode,case=case,target=target,old=old,token=token,returned=got,status=status,seed=seed,original_reply=r0,original_query=q0,new_query=qt,new_reply=rt,replayed=rt is None,input_sha256=sha(pcm.tobytes()),reply_slots=len(pcm));rows.append(row);stats.setdefault(case+':'+mode,Counter())[status]+=1
                        if row['replayed']:assert row['input_sha256']==r0['pcm_sha256']
                        if source==0 and length==13 and mode=='durable289' and case in ('clean','wrap17','rollback','fresh-alternate'):
                            name=case+'.wav';b=pcm.tobytes()
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b)
                            spec.append(dict(file=name,pcm_sha256=sha(b),peak=int(abs(pcm).max()),status=status))
    receipt=dict(schema='mhac-epoch-replay-v1',pin=PIN,blobs=pins,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,sqlite=sqlite3.sqlite_version,trials=len(rows),generated_frames=frames,stats=stats,specimens=spec,limits='Known static catalogue/source/length and aligned slots. Actual stored PCM replay, synthetic fresh alternate response. Serialized single-process SQLite, committed reserve/consume, clean close/reopen or deliberate DB deletion/snapshot restore; no power loss, rollback protection, authentication, real transport or human evidence. Exhaustion and wrap advanced by abandoned reservations, not PCM exchanges. Replay injections synthesize a current query when a reservation exists; abandoned reservation costs are not airtime. Same wire size, no retries or fallback. No action authority.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Epoch replay</title><h1>Epoch replay</h1><p>Synthetic only. Start at low volume; no autoplay.</p>'+''.join(f'<p>{s["file"]}: {s["status"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
