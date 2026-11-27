"""Adversarial #448/#449. Shared acquisition, bounded clock hypotheses; synthetic only.
python shared-clock.py PINNED_PACKAGE NEW_OUTPUT_DIR
"""
import hashlib,json,pathlib,runpy,sys,wave
from collections import Counter
import numpy as np
S=1280; SEED=4480560; PIN='68232af33ab7b5666ab6a89d84a5e24d3532c973'
PARENT='6a4ec165b64cc16cb9620911a409e0034a45513f'
CASES=[(0,0,1,0,0,None),(20000,20000,1,0,0,None),(-20000,-20000,1,0,0,None),(24000,0,.8,120,10,None),(-24000,0,.8,120,-10,None),(15000,-15000,1,100,0,None),(0,0,1,0,0,19.5),(-20000,-20000,1,0,0,19.5),(0,0,1,0,0,10.5),(12000,12000,.65,180,-15,None)]
MODES={'nominal2':(2,'nominal'),'fine2':(2,'fine'),'dual2':(2,'dual'),'dual4':(4,'dual'),'nominal4':(4,'nominal'),'fine4':(4,'fine')}
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
GRID=np.arange(-12,13)/4
F=np.array([2400,2600])
COARSE=np.exp(-2j*np.pi*(F[:,None]*(1+np.arange(-3,4)/100)).reshape(-1,1)*np.arange(320)/16000)
FINE=np.exp(-2j*np.pi*(F[:,None]*(1+GRID/100))[:,:,None]*np.arange(320)/16000)
def detect(pcm):
    events=[]; last=None; count=0; prior=None; work=0
    for t in range(320,len(pcm)+1,80):
        win=pcm[t-320:t].astype(float); scores=(abs(COARSE@win)*2/320).reshape(2,7).max(axis=1); work+=14*320
        k=int(scores.argmax()); v=k if scores[k]>=600 and scores[k]>=np.sqrt(np.mean(win**2)) else None
        if v!=last: last=v; count=0; onset=t-160
        count+=1
        if v is not None and count==4:
            shift=float(GRID[abs(FINE[v]@win).argmax()]); work+=25*320
            if prior is not None and prior[0]!=v and abs(onset-prior[1]-S)<=160:
                events.append((t,prior[0],prior[1],1/(1+(prior[2]+shift)/200))); prior=None
            else: prior=(v,onset,shift)
    return events,work

def receive(pcm,acq,books,joint,observe,mode):
    cap,policy=MODES[mode]; groups=[]; events=[]; work=Counter(); ix=0
    def emit(kind,g,**kw): events.append(dict(kind=kind,sample=t,source=g['source'],origin=g['origin'],**kw))
    for t in range(320,len(pcm)+1,80):
        while ix<len(acq) and acq[ix][0]<=t:
            _,source,origin,scale=acq[ix]; ix+=1; g=dict(source=source,origin=origin,hs=[])
            free=cap-sum(len(q['hs']) for q in groups)
            scales=[1.] if policy=='nominal' else [scale] if policy=='fine' else [1.,scale]
            scales=list(dict.fromkeys(scales))[:free]
            if not scales: emit('refused',g); continue
            for z in scales: g['hs'].append(dict(scale=z,start=origin+round(2*S*z),seen=[],done=False,value=None))
            groups.append(g); emit('start',g,scales=scales)
        work['peak']=max(work['peak'],sum(len(g['hs']) for g in groups))
        for g in groups[:]:
            for h in g['hs']:
                z=h['scale']; seen=h['seen']; start=h['start']
                while not h['done'] and t>=start+round((len(seen)+1)*S*z):
                    a=start+round(len(seen)*S*z); b=start+round((len(seen)+1)*S*z)
                    seen.append(observe(pcm[a:b],z,True,True)); work['slots']+=1; work['body_products']+=18*(round(480*z)-round(80*z))
                    if seen[-2:]==[18,18]:
                        body=seen[:-2]; book=books[g['source']].get(len(body))
                        if book is not None and 18 not in body:
                            work['book_cells']+=len(book)*sum(v is not None for v in body); k=joint(book,body,2)
                            if k is not None: h['value']=(len(body),k)
                        h['done']=True
                    elif len(seen)==22: h['done']=True
            if all(h['done'] for h in g['hs']):
                vals={h['value'] for h in g['hs'] if h['value'] is not None}
                emit('release' if len(vals)==1 else 'conflict' if vals else 'abstain',g,identity=list(next(iter(vals))) if len(vals)==1 else None,seen=[h['seen'] for h in g['hs']]); groups.remove(g)
        assert sum(len(g['hs']) for g in groups)<=cap
    return events,dict(work)

def run(root,out):
    def load(f): return runpy.run_path(str(root/f))
    h=load('window-holdout.py'); p=load('clock-propagation.py'); r=load('clock-refinement.py'); m=load('version-bound-payload.py'); v=load('interval-admission.py'); s=load('discourse-sync.py'); joint=load('prefix-disjoint.py')['joint']
    pins={**h['BLOBS'],'clock-propagation.py':'7fe8f5f4ad93095932f9127e0e10f787e6ff7d99','clock-refinement.py':'dc24cdcac40e10252b070da8073028544c98ef21','window-holdout.py':'5bb0110f12858ca96009bb5dcbb70bc6689b7c26'}
    for f,b in pins.items(): assert blob(root/f)==b,f
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    rng=np.random.default_rng(SEED); rows=[]; stats={}; checks=0; specimens=[]; out.mkdir(parents=True,exist_ok=False)
    for j in range(8):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); q=int(rng.integers(len(old))); lead=S+int(rng.integers(80))
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]; z=s['preamble'](a)+books[a][13][q].tolist()+[18,18]
        clean=np.zeros(len(y)*S,np.int32); v['put'](clean,y,0)
        for ci,(pre,body,gain,noise,phase,third) in enumerate(CASES):
            aa=np.zeros(48*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); off=lead+int(2.5*S)+phase*16
            altered=r['stretch'](clean,pre) if pre==body else np.concatenate([r['stretch'](clean[:2*S],pre),r['stretch'](clean[2*S:],body)])
            bb[off:off+len(altered)]=altered; want=[[a,18,i],[b,13,k]]; ends=[lead+22*S,off+len(altered)]
            if third is not None:
                at=lead+round(third*S); v['put'](aa,z,at); want.append([a,13,q]); ends.append(at+17*S)
            ns=SEED*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(ns).normal(0,noise,len(aa)); assert abs(mix).max()<6000
            pcm=np.rint(mix).astype('<i2'); acq,det=detect(pcm); digest=sha(pcm.tobytes())
            for mode in MODES:
                ev,work=receive(pcm,acq,books,joint,p['observe_scaled'],mode); rel=[e for e in ev if e['kind']=='release']; got=[[e['source'],*e['identity']] for e in rel]; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); timely=sum(any([e['source'],*e['identity']]==w and e['sample']<=end+3200 for e in rel) for w,end in zip(want,ends))
                row=dict(pair=j,condition=ci,mode=mode,expected=want,ends=ends,correct=correct,wrong=len(got)-correct,by200ms=timely,pcm_sha256=digest,noise_seed=ns,work=work,detector_products=det,events=ev); rows.append(row)
                for key in ('total',str(ci)):
                    st=stats.setdefault(key,{}).setdefault(mode,Counter()); st.update(expected=len(want),correct=correct,wrong=row['wrong'],by200ms=timely,refused=sum(e['kind']=='refused' for e in ev),conflicts=sum(e['kind']=='conflict' for e in ev),**{k:v for k,v in work.items() if k!='peak'}); st['peak']=max(st['peak'],work.get('peak',0))
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind'] in ('start','release','refused')}):
                        sub,_=detect(pcm[:t]); assert sub==[e for e in acq if e[0]<=t]; assert receive(pcm[:t],sub,books,joint,p['observe_scaled'],mode)[0]==[e for e in ev if e['sample']<=t]; checks+=1
            if j==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,pcm_sha256=digest,peak=int(abs(pcm).max())))
    receipt=dict(parent=PARENT,grammar_pin=PIN,pins=pins,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,conditions=CASES,modes=MODES,stats=stats,prefix_checks=checks,evaluations=len(rows),specimens=specimens,limits='Shared detector offline replay, no EOF flush, refuse new acquisitions when global cap occupied, hold hypotheses until group settles. Counts are proxies, not CPU/energy parity. No inter-acquisition overlap arbitration, authentication or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(z)+'\n' for z in rows)); (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Shared clock</title><h1>Shared clock hypotheses (synthetic)</h1><pre>'+json.dumps(stats,indent=2)+'</pre>'+''.join(f'<p>{v["file"]} <audio controls preload="none" src="{v["file"]}"></audio></p>' for v in specimens)+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>'); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
