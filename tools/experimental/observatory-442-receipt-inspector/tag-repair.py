"""Measurement #442: exact set-valued tag repair, synthetic only. Python + NumPy.
Run python tag-repair.py NEW_OUTPUT. GPT-6.2; no human evidence or subagents.
"""
import collections as co, hashlib, html, itertools as it, json, pathlib, sys, wave
import numpy as np
PINS={'main':'495a98ca12bae467a507031f04931aa4254b1866','grammar':'7eed95ec03c998439e1be061a07d2f924a46ca17','grammar_blob':'10d321972f156db8b7c1578aeb5fd003cbd0784d','measurement':'8c38c0053da3436f040b79216edba49bd7eb8740'}

def catalogue():
    def syntax(k):
        d=1
        for i,v in enumerate(k):
            if v in (0,1,2,3,14): d-=1
            elif v in (11,12): d+=1
            elif v not in range(4,11): return False
            if d==0: return k[i+1:]==(13,)*(3-i)
        return False
    digits=lambda k,n: tuple(k//17**i%17 for i in reversed(range(n)))
    free=[k for k in range(4913,13*4913) if not syntax(digits(k,4))]
    # Independent polynomial enumeration, indexed by evaluations at 0,1,4,5.
    coeff=np.array(list(it.product(range(17),repeat=4)),dtype=np.int64)
    x=np.arange(9); vals=(coeff @ (x[None,:]**np.arange(4)[:,None]))%17
    lookup=np.empty((17**4,9),dtype=np.int64); lookup[vals[:,[0,1,4,5]] @ np.array([4913,289,17,1])]=vals
    w=[]; p=[]; m=[]; labels=[]; h=g=small=0
    for kind in ('ack','terminal','quote','certificate'):
        acts=list(it.combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i; k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                word=lookup[k]; mid=len(labels); labels.append((kind,address,*act)); w.append(word); p.append(0); m.append(mid)
                for v in word[:8]: h=(31*h+int(v)+1)%1000000007; g=(37*g+int(v)+1)%1000000009
                if address<16:
                    a,b,c=digits(small,3); small+=1; w.append((a+b*x+c*x*x)%17); p.append(1); m.append(mid)
    assert (h,g,small)==(95787044,408117442,4000)
    w,p,m=np.array(w),np.array(p),np.array(m); t=np.where(p==0,w[:,8]%8,8+w[:,8]%9)
    return w,p,m,t,labels

def bounds(keys,m,size):
    lo=np.full(size,len(m),dtype=np.int32); hi=np.full(size,-1,dtype=np.int32)
    np.minimum.at(lo,keys,m); np.maximum.at(hi,keys,m); return lo,hi

def unique(lo,hi): return np.where(lo==hi,hi,-1)

def literal(w,m,t,obs,policy):
    keep=np.ones(len(m),dtype=bool)
    for i,v in enumerate(obs[:8]):
        if v is not None: keep &= w[:,i]==v
    a,b=obs[8:]
    if a is not None and b is not None:
        if a+b==16: keep &= t==a
        elif policy=='list': keep &= (t==a)|(t==16-b)
        elif policy=='reject': return -1
    elif policy=='trust' and (a is not None or b is not None): keep &= t==(a if a is not None else 16-b)
    got=np.unique(m[keep]); return int(got[0]) if len(got)==1 else -1

def audit(w,p,m,t):
    totals=co.defaultdict(co.Counter); rows=[]; checks=0; witness=None
    for n in (2,3,4,8):
        for mask in it.combinations(range(8),n):
            _,inv=np.unique(w[:,mask] @ 17**np.arange(n),return_inverse=True); size=int(inv.max())+1
            bl,bh=bounds(inv,m,size); body=unique(bl[inv],bh[inv]); lo,hi=bounds(inv*17+t,m,size*17); lo=lo.reshape(size,17); hi=hi.reshape(size,17)
            tl,th=lo[inv,t],hi[inv,t]; clean=unique(tl,th); c=co.Counter()
            for q in (0,1):
                sel=p==q; c[f'{q}:rows']=int(sel.sum()); c[f'{q}:clean']=int((sel&(clean==m)).sum()); c[f'{q}:body']=int((sel&(body==m)).sum()); c[f'{q}:faults']=16*int(sel.sum())
            for u in range(17):
                al,ah=lo[inv,u],hi[inv,u]; trust=unique(al,ah); repair=unique(np.minimum(tl,al),np.maximum(th,ah)); changed=t!=u
                assert not np.any(changed&(repair>=0)&(repair!=m))
                for q in (0,1):
                    sel=changed&(p==q)
                    for name,got in [('trust',trust),('repair',repair),('ignore',body)]:
                        c[f'{q}:{name}:correct']+=int((sel&(got==m)).sum()); c[f'{q}:{name}:wrong']+=int((sel&(got>=0)&(got!=m)).sum())
                if witness is None and n==3:
                    ix=np.flatnonzero(changed&(repair==m)&(body<0))
                    if len(ix): witness=(int(ix[0]),mask,u)
                if mask in ((0,1),(0,1,2),tuple(range(8))):
                    for i in range(0,len(m),997):
                        if not changed[i]: continue
                        obs=[int(w[i,j]) if j in mask else None for j in range(8)]
                        for pair,policy,expected in [([u,16-int(t[i])],'list',repair[i]),([int(t[i]),16-u],'list',repair[i]),([u,None],'trust',trust[i]),([u,None],'list',body[i]),([u,16-u],'list',trust[i])]:
                            assert literal(w,m,t,obs+pair,policy)==expected; checks+=1
            for q in (0,1):
                for name in ('trust','repair','ignore'):
                    c[f'{q}:{name}:abstain']=c[f'{q}:faults']-c[f'{q}:{name}:correct']-c[f'{q}:{name}:wrong']
                assert c[f'{q}:ignore:correct']==16*c[f'{q}:body'] and c[f'{q}:ignore:wrong']==0
            totals[str(n)].update(c); rows.append({'mask':mask,'counts':dict(c)})
    assert totals['3']['0:clean']==757183 and totals['2']['1:clean']==22918
    assert totals['3']['0:trust:wrong']==9073571 and totals['2']['1:trust:wrong']==298902
    assert witness is not None
    return dict(totals),rows,checks,witness

def audio(path,obs):
    frames=[]; detected=[]; n=np.arange(960); f=np.arange(400,2001,100); basis=np.exp(-2j*np.pi*f[:,None]*np.arange(640)/16000)
    for v in obs:
        a=np.zeros(1280,dtype='<i2')
        if v is not None: a[:960]=np.rint(2048*np.minimum(1,np.minimum(n/80,(959-n)/80))*np.sin(2*np.pi*(400+100*v)*n/16000+.137)).astype('<i2')
        y=a[160:800]; detected.append(int(np.argmax(abs(basis@y))) if np.any(y) else None); frames.append(a)
    assert detected==obs
    pcm=np.concatenate(frames)
    with wave.open(str(path),'wb') as out: out.setparams((1,2,16000,len(pcm),'NONE','not compressed')); out.writeframes(pcm.tobytes())
    return int(np.max(abs(pcm)))

def run(out):
    w,p,m,t,labels=catalogue(); totals,rows,checks,(i,mask,u)=audit(w,p,m,t); out.mkdir(parents=True,exist_ok=False)
    base=[int(w[i,j]) if j in mask else None for j in range(8)]; v=int(t[i]); old=[0,13,13,None,None,None,None,None]; specimens=[]
    for name,obs in [('repair-clean',base+[v,16-v]),('repair-invalid',base+[u,16-v]),('repair-erased',base+[u,None]),('within-clean',old+[2,14]),('within-invalid',old+[0,14]),('within-erased',old+[0,None]),('within-double',old+[0,16])]:
        decisions={}
        for policy in ('reject','trust','list'):
            mid=literal(w,m,t,obs,policy); decisions[policy]=None if mid<0 else labels[mid]
        fn=name+'.wav'; specimens.append({'file':fn,'symbols':obs,'decisions':decisions,'peak':audio(out/fn,obs)})
    assert specimens[1]['decisions']['list']==labels[m[i]] and specimens[1]['decisions']['reject'] is None
    assert specimens[5]['decisions']['trust']==('ack',189,5) and specimens[5]['decisions']['list'] is None
    assert specimens[6]['decisions']['list']==('ack',189,5)
    receipt={'schema':'mhac-tag-repair-v1','pins':PINS,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'duration_ms':800,'fault_unit':'16 alternatives per transmitted word/mask; invalid pair occurs in either coordinate (same repair result); double coordinated pair or one surviving substituted tag use same trust counts','limits':'Uniform finite symbolic counts; clean surviving body, known alignment/erasures, at most one tag substitution for repair guarantee. No source authentication, human evidence or physical channel probability. Common amplitude, not matched waveform energy.','totals':totals,'masks':rows,'literal_checks':checks,'repair_witness':{'truth':labels[m[i]],'mask':mask,'tag':v,'alternative':u},'specimens':specimens}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    doc=['<!doctype html><meta charset="utf-8"><title>Tag repair inspector</title><h1>Tag repair inspector</h1><p>Synthetic, clean body, aligned 800 ms. Invalid pair: list union of both possible original tags. One observed tag: ignore under possible corruption. Start at low volume; no autoplay.</p><p><a href="receipt.json">Full receipt</a></p>']
    for s in specimens: doc.append('<h2>'+s['file']+'</h2><pre>'+html.escape(json.dumps(s,indent=2))+'</pre><audio controls preload="none" src="'+s['file']+'"></audio>')
    for r in rows: doc.append('<details><summary>Body mask '+str(r['mask'])+'</summary><pre>'+html.escape(json.dumps(r['counts'],indent=2))+'</pre></details>')
    (out/'index.html').write_text('\n'.join(doc),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'totals':totals,'literal_checks':checks,'repair_witness':receipt['repair_witness'],'specimens':specimens},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
