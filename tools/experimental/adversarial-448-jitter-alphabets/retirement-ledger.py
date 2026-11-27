"""Refs #448/#449. Bounded retrospective ledger, synthetic event replay.
Usage: python retirement-ledger.py PINNED_PACKAGE NEW_OUTPUT_DIR
Experimental exact-parent instrumentation, not a production receiver.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='60bab29c38dfe336add58751aca79e090fde991a'
TRACE='05571c3f1f4e74ca44d361acca18255b8ef03229fa09a58ec3cb5b84e779b551'
LOCAL='fda63c200d0bbf213ac2303aac280976e04556cdbed59a17a068fb72104dc919'
TRANSPORT='911c805c9fec20cbe2360ae54d7bd0267e695d87afe9671d014c03cc3e45b3c7'
sha=lambda b:hashlib.sha256(b).hexdigest()
SLOT=1280

class Ledger:
    def __init__(self,limit):
        assert limit>0
        self.limit=limit; self.records={}; self.floor={}; self.peak=0; self.evicted=0
    def purge(self,t):
        for k,(expiry,_) in list(self.records.items()):
            if expiry<t: del self.records[k]
    def close(self,key,d,t,retain):
        if len(self.records)>=self.limit:
            k=min(self.records,key=lambda k:(self.records[k][0],k))
            del self.records[k]; self.floor[k[0]]=max(k[1],self.floor.get(k[0],-1)); self.evicted+=1
        self.records[key]=(key[1]+retain,{(p,lane):self.digest(e) for p in ('starts','done') for lane,e in d[p].items()})
        self.peak=max(self.peak,len(self.records))
    @staticmethod
    def digest(e): return sha(json.dumps(e,sort_keys=True,separators=(',',':')).encode())
    def classify(self,key,lane,e):
        if key in self.records:
            vals=self.records[key][1]; p='starts' if e['kind'] in ('start','overflow-ready-protected') else 'done'
            saved=vals.get((p,lane))
            return 'retired-unseen' if saved is None else 'retired-duplicate' if saved==self.digest(e) else 'retired-conflict'
        return 'retired-floor' if key[1]<=self.floor.get(key[0],-1) else None

# Keep admission, timing and evidence rules identical to exact Run050 parent.
# Checked one-occurrence replacements are deliberately narrow; never edit parent.
def variant(path,limit):
    assert sha(path.read_bytes())==LOCAL
    src=path.read_text()
    edits=[('retired={}', 'retired=Ledger(limit)'),
           ('retired[key[0]]=max(key[1],retired.get(key[0],-1)); del groups[key]', 'retired.close(key,groups[key],t,retain); del groups[key]'),
           ('for t in sorted(times):', 'for t in sorted(times):\n        retired.purge(t)'),
           ("if o<=retired.get(s,-1): emit('retired-or-older',t,key=key); continue", "reason=retired.classify(key,lane,e)\n                if reason: emit(reason,t,key=key,lane=lane); continue"),
           ('len(retired)<=2','len(retired.records)<=limit and len(retired.floor)<=2'),
           ('unresolved=len(groups))','unresolved=len(groups),peak_retired=retired.peak,evicted_retired=retired.evicted)')]
    for a,b in edits:
        assert src.count(a)==1,(a,src.count(a)); src=src.replace(a,b)
    ns=dict(__name__='retirement_variant',Ledger=Ledger,limit=limit); exec(compile(src,str(path),'exec'),ns)
    return ns['replay']

def signature(es): return [e for e in es if e['kind']=='settled']

def fixtures(base,variants,envelopes):
    def frame(o,i):
        lane=[dict(kind='start',sample=o,source=0,body_start=o+2),dict(kind='release',sample=o+5,source=0,body_start=o+2,identity=[13,i])]
        return envelopes(dict(bank=lane,fine=lane),'e')
    older=frame(0,1); newer=frame(10,2)
    w=newer+[dict(m,arrival=20) for m in older]
    def r(f,w): return f(w,200,'e',action=100,retain=150)[0]
    assert len(signature(r(base,w)))==1
    assert all(len(signature(r(f,w)))==2 for f in variants.values())
    # One-slot eviction must still suppress replays, but loses conflict classification.
    a,b=frame(0,1),frame(10,2); late=dict(a[-1],arrival=30,event=dict(a[-1]['event'],identity=[13,9])); w=a+b+[late]
    assert r(variants[1],w)[-1]['kind']=='retired-floor'
    assert r(variants[4],w)[-1]['kind']=='retired-conflict'
    assert len(signature(r(variants[4],w)))==2
    # No resurrection at or after retention boundary: exact boundary still classifiable.
    w=a+[dict(a[-1],arrival=150),dict(a[-1],arrival=151)]
    ev=r(variants[4],w); assert [e['kind'] for e in ev][-2:]==['retired-duplicate','invalid-or-expired']
    return 6

def run(root,out):
    src=root/'ensemble1/ensemble-traces.jsonl'; p=root/'acquisition-local.py'; q=root/'transport-binding.py'
    assert sha(src.read_bytes())==TRACE and sha(p.read_bytes())==LOCAL and sha(q.read_bytes())==TRANSPORT
    base=runpy.run_path(str(p))['replay']; old=runpy.run_path(str(q)); variants={n:variant(p,n) for n in (1,2,4,8)}
    fs={'watermark':base,**{str(n):f for n,f in variants.items()}}; captures=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); captures[z['pair'],z['condition']][z['mode']]=z
    stats={}; rows=[]; checks=equiv=injected=0; h=48*SLOT
    for key,g in sorted(captures.items()):
        epoch=str(key); w=old['envelopes']({k:g[k]['events'] for k in ('bank','fine')},epoch); want=C.Counter(map(tuple,g['bank']['expected']))
        orig=signature(base(w,h,epoch)[0]); extras=[]
        for s in orig:
            t=s['sample']+80
            if t>min(h,s['acquisition']+40*SLOT): continue
            m=next(m for m in w if m['origin']==s['acquisition'] and m['event']['source']==s['source'] and m['event']['kind']=='release')
            extras.append(dict(m,arrival=t))
        injected+=len(extras)
        for fault in ('clean','duplicate','contradiction','drop-start','drop-terminal','start-after-terminal'):
            wire=list(w)
            if fault=='duplicate': wire+=extras
            elif fault=='contradiction': wire+=[dict(m,event=dict(m['event'],identity=[-1,-1])) for m in extras]
            elif fault!='clean': wire=old['fault'](w,fault)
            for label,f in fs.items():
                ev,state=f(wire,h,epoch); settled=signature(ev)
                if fault=='clean': assert settled==orig; equiv+=1
                if fault in ('duplicate','contradiction'): assert settled==orig
                got=C.Counter((e['source'],*e['identity']) for e in settled); correct=sum((got&want).values()); auth=sum(e['action_authorized'] for e in settled)
                s=stats.setdefault(fault+'/'+label,C.Counter()); s.update(expected=sum(want.values()),correct=correct,wrong=sum(got.values())-correct,authorized=auth,evicted=state.get('evicted_retired',0)); s.update(e['kind'] for e in ev if e['kind']!='settled'); s['peak_retired']=max(s['peak_retired'],state.get('peak_retired',0))
                rows.append(dict(capture=key,fault=fault,policy=label,events=ev,state=state))
                if label=='4':
                    for t in sorted({m['arrival'] for m in wire}|{e['sample'] for e in ev}):
                        if t>h: continue
                        assert f(wire,t,epoch)[0]==[e for e in ev if e['sample']<=t]; checks+=1
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),trace_sha256=TRACE,captures=len(captures),evaluations=len(rows),prefix_checks=checks,clean_equivalence=equiv,injected_per_fault=injected,fixtures=fixtures(base,variants,old['envelopes']),stats=stats,limits='No new PCM or repair; trusted envelopes and atomic batches; SHA256 is a fingerprint, not authentication. Bounded retired groups and two source floors; floor may reject unseen older acquisitions. No retroactive revocation; batch logs unbounded. Exploratory retained replay, not holdout.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
