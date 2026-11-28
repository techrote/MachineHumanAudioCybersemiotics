"""Measurement #442: matched slot-fault clarification audit, synthetic aligned PCM.
Run: python framed-cost-audit.py PINNED_CATALOGUE_DIR NEW_OUTPUT_DIR
Transcribed framing and polynomial evaluation rules from Grammar #453, independent
fault model, parity recovery, candidate accounting and experiment. Not blind acquisition.
"""
import functools, hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='6f97617400c4e2dc1d8d6a979edcba53c64e1f62'
RULES={'catalogue-reply.py':'8b07a9dde7dd7250b490263c3044aeb798453019','acoustic-clarification.py':'71e527852c278fb91088ed9fdcf5d7d6027426a3','discriminating-reply.py':'32ffadda8146153ebbb90ebcd343129986512de8'}
BLOBS={'version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
SEED=4424601; S=1280; F=16000
sha=lambda b:hashlib.sha256(b).hexdigest()
def code(d): return list(d)+[sum(d)%17,sum((i+1)*v for i,v in enumerate(d))%17]
def recover(y):
    if y is None:return None
    n=len(y); holes=[i for i,v in enumerate(y) if v is None]; x=[0 if v is None else v for v in y]; found=[]
    if len(holes)>2:return None
    # Independently enumerate erasures or a single substitution, checking both parity equations.
    for p in [tuple(holes)] if holes else [(),*((i,) for i in range(n))]:
        for vals in itertools.product(range(17),repeat=len(p)):
            z=x.copy()
            for i,v in zip(p,vals):z[i]=v
            if code(z[:-2])==z and z[:-2] not in found:found.append(z[:-2])
        if found and not p:break
    return found[0] if len(found)==1 else None
@functools.lru_cache(None)
def matrix(p,n):
    a=np.ones((len(p),n),dtype=np.int64)
    for i,x in enumerate(p):
        for y in p:
            if x!=y:a[i]=a[i]*(np.arange(n)-y)*pow((x-y)%17,-1,17)%17
    return a
def encode(d,r):return (np.array(d)@matrix(tuple(range(len(d))),len(d)+r)%17).tolist()
@functools.lru_cache(None)
def plans(k,n,keep):
    p=list(itertools.combinations(keep,k));return np.array(p),np.stack([matrix(z,n) for z in p])
def decode(y,r):
    if y is None:return None
    n=len(y);k=n-r;keep=tuple(i for i,v in enumerate(y) if v is not None);e=n-len(keep)
    if e>r:return None
    x=np.array([0 if v is None else v for v in y]);p,m=plans(k,n,keep);w=np.einsum('bi,bij->bj',x[p],m)%17;v=w[2*np.count_nonzero(w[:,keep]!=x[list(keep)],axis=1)+e<=r]
    if len(v):
        assert np.all(v==v[0]);return v[0,:k].tolist()
def digits(i,k):return [(i//17**j)%17 for j in range(k)]
def index(x):return sum(v*17**j for j,v in enumerate(x))
T=np.arange(S//2); ENV=np.minimum(1,np.minimum(T/30,(len(T)-1-T)/30)); HZ=np.arange(400,2300,100)
TONES=np.rint(1500*ENV*np.sin(2*np.pi*HZ[:,None]*T/F+.137)).astype('<i2'); BASIS=np.exp(-2j*np.pi*HZ[:,None]*np.arange(400)/F)
def frame(payload,draw,sub,erase,marker):
    clean=[17,*payload,18]; sent=clean.copy(); u,d=draw
    for i,v in enumerate(clean):
        j=0 if i==0 else 31 if i==len(clean)-1 else i
        if (i==0 or i==len(clean)-1) and not marker:continue
        if u[j]<erase:sent[i]=None
        elif u[j]<erase+sub:sent[i]=(v+int(d[j]))%17 if 0<i<len(clean)-1 else (v+1)%19
    x=np.zeros((len(sent),S),dtype='<i2')
    for i,v in enumerate(sent):
        if v is not None:x[i,:S//2]=TONES[v]
    scores=abs(x[:,80:480]@BASIS.T)*2/400;obs=[int(a.argmax()) if a.max()>=600 else None for a in scores];assert obs==sent
    data=obs[1:-1] if obs[0]==17 and obs[-1]==18 and all(v is None or v<17 for v in obs[1:-1]) else None
    return data,x,dict(clean=clean,sent=sent,observed=obs,pcm_sha256=sha(x.tobytes()),slots=len(sent),energy=int(np.square(x.astype(np.int64)).sum()),sub=sum(a!=b and b is not None for a,b in zip(clean,sent)),erase=sent.count(None))
def run(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw;long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED);out.mkdir();rows=[];stats={};spec=[];checks=0
    for k in (7,8):
        for r in (2,4):
            for _ in range(20):
                d=rng.integers(0,17,k).tolist();w=encode(d,r);perm=rng.permutation(len(w));t=int(rng.integers(0,r//2+1));e=r-2*t
                for i in perm[:t]:w[i]=(w[i]+1)%17
                for i in perm[t:t+e]:w[i]=None
                assert decode(w,r)==d;checks+=1
    conditions=[('clean',0,0,False,False),('s01',.01,0,False,False),('s05',.05,0,False,False),('s10',.10,0,False,False),('e10',0,.10,False,False),('mixed',.05,.05,False,False),('mixed-markers',.05,.05,True,False),('omitted-clean',0,0,False,True)]
    serial=0
    for source,bylen in books.items():
        for length,book in bylen.items():
            width=4 if length==13 else 5
            for sample in range(32):
                serial+=1;ids=sorted(map(int,rng.choice(len(book),4,False)));target=ids[sample%4];nonce=[serial//17,serial%17]
                pos=min((max(Counter(map(int,col)).values()),sum(n*n for n in Counter(map(int,col)).values()),j) for j,col in enumerate(book[ids].T) if len(set(col))>1)[2]
                omitted=next(int(i) for i in np.flatnonzero(book[:,pos]==book[target,pos]) if i not in ids)
                # Same random draws for all modes AND nested fault rates in this group; markers paired by role.
                seed=SEED+serial;g=np.random.default_rng(seed);draws=[(g.random(32),g.integers(1,17,32)) for _ in range(2)]
                for condition,sub,erase,marker,omit in conditions:
                    actual=omitted if omit else target
                    for mode in ('compact','index2','index4','full'):
                        request=nonce+[pos-3 if mode=='compact' else 16 if mode=='full' else 15];qo,qpcm,qt=frame(code(request),draws[0],sub,erase,marker);q=recover(qo);got=[];rt=None
                        if q==request:
                            r=4 if mode=='index4' else 2
                            payload=code(q+[int(book[actual,pos])]) if mode=='compact' else code(q)+book[actual].tolist() if mode=='full' else encode(q+digits(actual,width),r)
                            ro,rpcm,rt=frame(payload,draws[1],sub,erase,marker)
                            if ro is not None:
                                if mode=='compact':
                                    h=recover(ro);got=[i for i in ids if book[i,pos]==h[3]] if h is not None and h[:3]==request else []
                                elif mode=='full':
                                    h=recover(ro[:5]);body=ro[5:];keep=[i for i,x in enumerate(body) if x is not None];e=length-len(keep)
                                    if h==request and e<=4:
                                        found=np.flatnonzero(2*np.count_nonzero(book[:,keep]!=[body[i] for i in keep],axis=1)+e<=4);got=found.tolist() if len(found)==1 else []
                                else:
                                    h=decode(ro,r)
                                    if h is not None and h[:3]==request and index(h[3:])<len(book):got=[index(h[3:])]
                            if serial==1 and condition in ('clean','mixed-markers','omitted-clean'):
                                name=f'{mode}-{condition}.wav';pcm=np.concatenate((qpcm,rpcm));b=pcm.tobytes()
                                with wave.open(str(out/name),'wb') as w:w.setparams((1,2,F,0,'NONE','not compressed'));w.writeframes(b)
                                spec.append(dict(file=name,sha256=sha(b),peak=int(abs(pcm).max())))
                        status='withheld' if not got else 'wrong-set' if actual not in got else 'resolved' if len(got)==1 else 'retained';slots=qt['slots']+(rt['slots'] if rt else 0);energy=qt['energy']+(rt['energy'] if rt else 0)
                        if condition=='clean':assert actual in got
                        if condition=='omitted-clean':assert status==('wrong-set' if mode=='compact' else 'resolved')
                        c=stats.setdefault(condition+':'+mode,Counter());c.update([status]);c['slots']+=slots;c['energy']+=energy;c['query_refused']+=int(q!=request);c['reply_frame_refused']+=int(rt is not None and (rt['observed'][0]!=17 or rt['observed'][-1]!=18))
                        rows.append(dict(group=serial,seed=seed,source=source,length=length,ids=ids,target=actual,mode=mode,condition=condition,request=request,decoded_query=q,returned=got,status=status,query=qt,reply=rt,slots=slots,energy=energy))
    recount={}
    for z in rows:
        expected='withheld' if not z['returned'] else 'wrong-set' if z['target'] not in z['returned'] else 'resolved' if len(z['returned'])==1 else 'retained';assert expected==z['status'];assert z['slots']==sum(f['slots'] for f in (z['query'],z['reply']) if f);recount.setdefault(z['condition']+':'+z['mode'],Counter()).update([expected])
    assert all(all(stats[k][s]==n for s,n in c.items()) for k,c in recount.items())
    receipt=dict(schema='mhac-framed-cost-audit-v1',pin=PIN,rules=RULES,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,conditions=conditions,groups=serial,evaluations=len(rows),checks=checks,stats=stats,specimens=spec,limits='Synthetic aligned PCM, no noise beyond explicit symbol substitutions/erasures. Common random draws by payload position and marker role, not matched total energy, duration, or realized error count. Query equality gate has privileged original request. Catalogue order/source/length known. No turnaround, retries, authentication, human evidence or action authority. Omitted target deliberately shares a queried symbol. 32 groups per source/length, reused across rates.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(z)+'\n' for z in rows));
    html='<!doctype html><meta charset="utf-8"><title>Framed cost audit</title><style>body{font:16px system-ui;max-width:900px;margin:auto;padding:20px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #888;text-align:right}pre{white-space:pre-wrap}</style><h1>Matched slot-fault audit</h1><p>Synthetic aligned PCM. 128 exchanges per mode/condition. Correct singleton and retained set are separate outcomes. Start at low volume; no autoplay.</p><label>Condition <select id="c"></select></label><div id="t"></div><p><a href="receipt.json">Receipt</a> · <a href="traces.jsonl">Trace export</a></p>'+''.join(f'<p>{z["file"]}<br><audio controls preload="none" src="{z["file"]}"></audio></p>' for z in spec)+'''<script>const data='''+json.dumps(stats)+''';const c=document.getElementById('c'),t=document.getElementById('t');for(const k of [...new Set(Object.keys(data).map(k=>k.split(':')[0]))])c.add(new Option(k,k));function draw(){t.innerHTML='<table><tr><th>Mode</th><th>Resolved</th><th>Retained</th><th>Wrong</th><th>Withheld</th><th>Mean ms</th><th>Query refused</th></tr>'+['compact','index2','index4','full'].map(m=>{const r=data[c.value+':'+m];return '<tr><td>'+m+'</td>'+['resolved','retained','wrong-set','withheld'].map(k=>'<td>'+(r[k]||0)+'</td>').join('')+'<td>'+Math.round(r.slots*80/128)+'</td><td>'+r.query_refused+'</td></tr>'}).join('')+'</table>'}c.onchange=draw;draw();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(html);(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(groups=serial,evaluations=len(rows),checks=checks,stats=stats)))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
