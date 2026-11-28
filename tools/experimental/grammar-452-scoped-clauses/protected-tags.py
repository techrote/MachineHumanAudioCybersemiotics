"""Grammar lane #452/#453. Original synthetic ten-slot profile experiment.
Run: python protected-tags.py NEW_OUTPUT. NumPy required. GPT-6.2, no subagents.
"""
import itertools as it, collections, math, json, hashlib, pathlib, sys, wave, html
import numpy as np
PINS={'main':'495a98ca12bae467a507031f04931aa4254b1866','grammar':'3ecd4769825c7fb41fc8581cd99c02efd0ed8c1f','measurement':'8c38c0053da3436f040b79216edba49bd7eb8740'}
MODES=('marker-pair','partition-pair','full-check')
def digits(k,n): return tuple(k//17**i%17 for i in reversed(range(n)))
def syntax(row):
    pending=1
    for i,v in enumerate(row):
        if v in (0,1,2,3,14): pending-=1
        elif v in (11,12): pending+=1
        elif not 4<=v<=10: return False
        if pending==0: return all(x==13 for x in row[i+1:])
    return False
def books():
    free=[k for k in range(4913,13*4913) if not syntax(digits(k,4))]; pos=(0,1,4,5)
    mat=[[math.prod((x-j)*pow(i-j,-1,17) for j in pos if j!=i)%17 for i in pos] for x in range(9)]
    w=[]; p=[]; m=[]; labels=[]; h=g=small=0
    for kind in ('ack','terminal','quote','certificate'):
        acts=list(it.combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i
                k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                word=tuple(sum(a*b for a,b in zip(r,digits(k,4)))%17 for r in mat)
                label=(kind,address,*act); mid=len(labels); labels.append(label); w.append(word); p.append(0); m.append(mid)
                for v in word[:8]: h=(h*31+v+1)%1000000007; g=(g*37+v+1)%1000000009
                if address<16:
                    a,b,c=digits(small,3); small+=1
                    w.append(tuple((a+b*x+c*x*x)%17 for x in range(9))); p.append(1); m.append(mid)
    assert (h,g,small)==(95787044,408117442,4000)
    return np.array(w),np.array(p),np.array(m),labels
def tags(w,p,mode):
    u=w[:,8]
    if mode=='full-check': return np.stack((u,(u+8*p)%17),axis=1)
    t=p*8 if mode=='marker-pair' else np.where(p==0,u%8,8+u%9)
    return np.stack((t,16-t),axis=1)
def consensus(keys,m,size):
    lo=np.full(size,len(m),dtype=np.int32); hi=np.full(size,-1,dtype=np.int32)
    np.minimum.at(lo,keys,m); np.maximum.at(hi,keys,m)
    return np.where(lo==hi,hi,-1)
def decode(w,p,m,mode,obs):
    if len(obs)!=10 or any(x is not None and (type(x)!=int or not 0<=x<17) for x in obs): return None
    words=np.column_stack((w[:,:8],tags(w,p,mode))); keep=np.ones(len(m),dtype=bool)
    for i,x in enumerate(obs):
        if x is not None: keep &= words[:,i]==x
    got=np.unique(m[keep]); return int(got[0]) if len(got)==1 else None
def audit(w,p,m):
    totals=collections.defaultdict(collections.Counter); masks=[]; checks=0
    for n in (2,3,4,8):
        for mask in it.combinations(range(8),n):
            _,inv=np.unique(w[:,mask] @ (17**np.arange(n)),return_inverse=True); size=int(inv.max())+1
            for mode in MODES:
                t=tags(w,p,mode); pairs,pi=np.unique(t[:,0]*17+t[:,1],return_inverse=True); width=len(pairs)
                table=consensus(inv*width+pi,m,size*width).reshape(size,width)
                singles=[consensus(inv*17+t[:,j],m,size*17).reshape(size,17) for j in (0,1)]
                count=collections.Counter()
                for q in (0,1):
                    sel=p==q; count[f'{q}:rows']=int(sel.sum())
                    for name,got in [('both',table[inv,pi]),('first',singles[0][inv,t[:,0]]),('second',singles[1][inv,t[:,1]])]:
                        assert not np.any(sel&(got>=0)&(got!=m)); count[f'{q}:{name}:correct']=int((sel&(got==m)).sum())
                    count[f'{q}:single:total']=32*int(sel.sum()); count[f'{q}:first-fault:total']=16*int(sel.sum())
                # Every unlisted pair is invalid. Enumerate every legal pair at Hamming distance one.
                for a,x in enumerate(pairs):
                    src=np.flatnonzero(pi==a)
                    for b,y in enumerate(pairs):
                        if a==b or ((x//17==y//17)+(int(x%17==y%17)))!=1: continue
                        got=table[inv[src],b]
                        for q in (0,1):
                            sel=p[src]==q; count[f'{q}:single:wrong']+=int((sel&(got>=0)&(got!=m[src])).sum()); count[f'{q}:single:correct']+=int((sel&(got==m[src])).sum())
                for v in range(17):
                    got=singles[0][inv,v]
                    for q in (0,1):
                        sel=(p==q)&(t[:,0]!=v); count[f'{q}:first-fault:wrong']+=int((sel&(got>=0)&(got!=m)).sum()); count[f'{q}:first-fault:correct']+=int((sel&(got==m)).sum())
                for q in (0,1):
                    for name in ('single','first-fault'):
                        count[f'{q}:{name}:reject']=count[f'{q}:{name}:total']-count[f'{q}:{name}:wrong']-count[f'{q}:{name}:correct']
                if mask in ((0,1),(0,1,2),tuple(range(8))):
                    literal=collections.defaultdict(set)
                    for word,pair,mid in zip(w,t,m): literal[tuple(word[list(mask)])+tuple(pair)].add(mid)
                    for i in range(0,len(m),997):
                        for j in (0,1):
                            for v in range(17):
                                pair=t[i].copy(); pair[j]=v; key=int(pair[0]*17+pair[1]); idx=np.searchsorted(pairs,key)
                                got=table[inv[i],idx] if idx<width and pairs[idx]==key else -1
                                candidates=literal.get(tuple(w[i,list(mask)])+tuple(pair),set())
                                assert got==(next(iter(candidates)) if len(candidates)==1 else -1); checks+=1
                totals[f'{n}:{mode}'].update(count); masks.append({'mask':mask,'mode':mode,'counts':dict(count)})
    for n in (2,3,4,8):
        for q in (0,1):
            for mode in MODES[:2]: assert totals[f'{n}:{mode}'][f'{q}:single:reject']==totals[f'{n}:{mode}'][f'{q}:single:total']
    assert totals['3:partition-pair']['0:both:correct']==757183 and totals['2:partition-pair']['1:both:correct']==22918
    assert totals['3:partition-pair']['0:first-fault:wrong']==9073571 and totals['2:partition-pair']['1:first-fault:wrong']==298902
    assert totals['3:full-check']['0:both:correct']==2688000 and totals['2:full-check']['1:both:correct']==112000
    return dict(totals),masks,checks
def audio(path,symbols):
    samples=[]; observed=[]
    for v in symbols:
        x=np.zeros(1280,dtype=np.int16); n=np.arange(960)
        if v is not None: x[:960]=np.rint(2048*np.minimum(1,np.minimum(n/80,(959-n)/80))*np.sin(2*np.pi*(400+100*v)*n/16000+.137)).astype(np.int16)
        y=x[160:800]; f=np.arange(400,2001,100); score=np.abs(np.exp(-2j*np.pi*f[:,None]*np.arange(640)/16000)@y)**2
        observed.append(int(np.argmax(score)) if np.any(y) else None); samples.extend(x.tolist())
    assert observed==symbols
    with wave.open(str(path),'wb') as a:
        a.setparams((1,2,16000,len(samples),'NONE','not compressed')); a.writeframes(np.array(samples,dtype='<i2').tobytes())
    return observed,max(map(abs,samples))
def run(out):
    w,p,m,labels=books(); totals,masks,checks=audit(w,p,m); out.mkdir(parents=True,exist_ok=False)
    # Measurement's pinned within-profile witness; two tag errors or one erased plus one wrong re-enable it.
    base=[0,13,13,None,None,None,None,None]; specimens=[]
    for name,symbols,expected in [('clean',[0,13,13,15,0,0,13,3,2,14],('ack',187,17)),('clean-erased',base+[2,14],None),('one-error',base+[0,14],None),('error-erasure',base+[0,None],('ack',189,5)),('two-errors',base+[0,16],('ack',189,5))]:
        fn=name+'.wav'; observed,peak=audio(out/fn,symbols); mid=decode(w,p,m,'partition-pair',observed); got=None if mid is None else labels[mid]; assert got==expected
        specimens.append({'file':fn,'symbols':observed,'decoded':got,'peak':peak})
    receipt={'schema':'mhac-protected-tags-v1','pins':PINS,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'duration_ms':800,'totals':totals,'masks':masks,'literal_checks':checks,'specimens':specimens,'limits':'Uniform finite symbolic counts; known alignment, clean surviving body, substitutions only in tags. No authentication or human evidence. Common alphabet, duration and amplitude; not exact energy or compute matched.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Protected tags</title><h1>Protected tags</h1><p>Synthetic aligned PCM. Start at low volume; no autoplay.</p>'+''.join('<h2>'+s['file']+'</h2><p>'+html.escape(str(s['decoded']))+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in specimens)+'<p><a href="receipt.json">Full masks and results</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'totals':totals,'literal_checks':checks,'specimens':specimens},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
