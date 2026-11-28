"""Grammar #452: distributed profile identity, original synthetic experiment.
Python 3 + NumPy. CLI: python distributed-profile.py NEW_OUTPUT
"""
import itertools as it, hashlib, json, pathlib, sys, wave, html
import numpy as np

PINS={'main':'495a98ca12bae467a507031f04931aa4254b1866','grammar':'7eed95ec03c998439e1be061a07d2f924a46ca17','measurement':'51de5ccf34186c5f7d64eb994a63ee83152ef90f'}
MODES=('tag-pair','free-cubic','reserved-cubic')
POS=(0,1,4,5)
X=np.arange(10,dtype=np.int64)
def digits(k,n): return tuple(k//17**i%17 for i in reversed(range(n)))
def syntax(row):
    pending=1
    for i,v in enumerate(row):
        if v in (0,1,2,3,14): pending-=1
        elif v in (11,12): pending+=1
        elif not 4<=v<=10: return False
        if pending==0: return all(x==13 for x in row[i+1:])
    return False

def catalogue():
    free=[k for k in range(4913,13*4913) if not syntax(digits(k,4))]
    coeff=np.array(list(it.product(range(17),repeat=4)),dtype=np.int64)
    val=(coeff @ X[None,:]**np.arange(4)[:,None])%17
    rank=val[:,POS] @ np.array([4913,289,17,1]); lookup=np.argsort(rank)
    assert np.array_equal(rank[lookup],np.arange(17**4))
    legacy=[]; protected=[]; labels=[]
    for kind in ('ack','terminal','quote','certificate'):
        acts=list(it.combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i
                k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                legacy.append(int(lookup[k])); labels.append((kind,address,*act))
                if address<16: protected.append(len(labels)-1)
    legacy=np.array(legacy); protected=np.array(protected)
    h=g=0
    for v in val[legacy,:8].flat:
        h=(h*31+int(v)+1)%1000000007; g=(g*37+int(v)+1)%1000000009
    assert (h,g,len(legacy),len(protected))==(95787044,408117442,48000,4000)
    mids=np.concatenate((np.arange(len(legacy)),protected)); p=np.arange(len(mids))>=len(legacy)
    q=(np.array([digits(i,3) for i in range(len(protected))]) @ X[None,:]**np.arange(3)[:,None])%17
    old=np.vstack((val[legacy],q)); t=np.where(p,8+old[:,8]%9,old[:,8]%8)
    base=np.column_stack((old[:,:8],t,16-t))
    used=np.zeros(len(val),bool); used[legacy]=True
    spare=np.flatnonzero(~used)
    freewords=np.vstack((val[legacy],val[spare[:4000]]))
    # Reserve a fixed cubic coefficient, choosing the least disruptive slice.
    c=int(np.argmin(np.bincount(coeff[legacy,3],minlength=17)))
    collide=coeff[legacy,3]==c; relocated=legacy.copy()
    dest=spare[coeff[spare,3]!=c][:int(collide.sum())]; relocated[collide]=dest
    protected_poly=np.arange(4000)*17+c
    reserved=np.vstack((val[relocated],val[protected_poly]))
    for words in (base,freewords,reserved): assert len(np.unique(words,axis=0))==52000
    assert np.array_equal(freewords[:48000,:8],old[:48000,:8])
    assert np.array_equal(reserved[48000:],(q+c*X**3)%17)
    return dict(zip(MODES,(base,freewords,reserved))),mids,p,labels,{'reserved_cubic_coefficient':c,'legacy_relocated':int(collide.sum()),'legacy_unchanged_free':48000}

def project(words,mids,mask):
    keys=words[:,mask] @ (17**np.arange(len(mask),dtype=np.int64))
    _,inv=np.unique(keys,return_inverse=True)
    lo=np.full(int(inv.max())+1,len(mids)); hi=np.full_like(lo,-1)
    np.minimum.at(lo,inv,mids); np.maximum.at(hi,inv,mids)
    return (lo[inv]==hi[inv])

def decode(words,mids,obs,budget):
    if len(obs)!=10 or budget not in (0,1) or any(v is not None and (type(v)!=int or not 0<=v<17) for v in obs): raise ValueError('invalid observation')
    mask=[i for i,v in enumerate(obs) if v is not None]
    diff=np.count_nonzero(words[:,mask]!=np.array([obs[i] for i in mask]),axis=1)
    possible=np.unique(mids[diff<=budget]); return int(possible[0]) if len(possible)==1 else -1

def audit(books,mids,p):
    clean={}; faults={}; witnesses={}; rng=np.random.default_rng(261126)
    for n in (3,4,5,6,10):
        masks=list(it.combinations(range(10),n)); picks=[masks[0],masks[-1]] if len(masks)>1 else masks
        trials=[]
        for profile in (0,1):
            pool=np.flatnonzero(p==profile)
            for i in rng.choice(pool,32,replace=False):
                for mask in picks: trials.append((int(i),mask,int(rng.integers(n)),int(rng.integers(1,17))))
        for mode,words in books.items():
            totals=[0,0]
            for mask in masks:
                good=project(words,mids,mask)
                for profile in (0,1): totals[profile]+=int(np.count_nonzero(good&(p==profile)))
            clean[f'{mode}:{n}']={'correct':totals,'total':[48000*len(masks),4000*len(masks)],'masks':len(masks)}
            count=np.zeros((2,2,3),dtype=int)
            for i,mask,j,delta in trials:
                obs=[int(words[i,k]) if k in mask else None for k in range(10)]; obs[mask[j]]=(obs[mask[j]]+delta)%17
                for budget in (0,1):
                    got=decode(words,mids,obs,budget); outcome=0 if got==mids[i] else 1 if got<0 else 2
                    count[int(p[i]),budget,outcome]+=1
                    if budget==1: assert outcome!=2
                    if outcome==2 and mode not in witnesses: witnesses[mode]={'row':i,'obs':obs,'wrong':got,'true':int(mids[i])}
            faults[f'{mode}:{n}']=count.tolist()
            if mode!='tag-pair' and n>=4: assert totals==clean[f'{mode}:{n}']['total']
            if mode!='tag-pair' and n>=6: assert np.all(count[:,1,1:]==0)
    return clean,faults,witnesses

def audio(path,obs):
    frames=[]; n=np.arange(960); basis=np.exp(-2j*np.pi*np.arange(400,2001,100)[:,None]*np.arange(640)/16000)
    for v in obs:
        a=np.zeros(1280,dtype='<i2')
        if v is not None: a[:960]=np.rint(2048*np.minimum(1,np.minimum(n/80,(959-n)/80))*np.sin(2*np.pi*(400+100*v)*n/16000+.137)).astype('<i2')
        y=a[160:800]; assert (int(np.argmax(abs(basis@y))) if np.any(y) else None)==v; frames.append(a)
    with wave.open(str(path),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(np.concatenate(frames).tobytes())

def run(out):
    books,mids,p,labels,changes=catalogue(); clean,faults,witnesses=audit(books,mids,p); out.mkdir(parents=True,exist_ok=False)
    specimens=[]
    # Find a shared protected message whose corrupted six-symbol baseline is ambiguous.
    i=next(i for i in range(48000,52000) if decode(books['tag-pair'],mids,[(int(books['tag-pair'][i,0])+1)%17]+books['tag-pair'][i,1:6].tolist()+[None]*4,1)<0)
    for mode,words in books.items():
        for case in ('clean','four-survivors','six-one-error'):
            obs=[int(v) for v in words[i]]; budget=int(case=='six-one-error')
            if case!='clean': obs=[v if j<(6 if budget else 4) else None for j,v in enumerate(obs)]
            if budget: obs[0]=(obs[0]+1)%17
            got=decode(words,mids,obs,budget); fn=f'{mode}-{case}.wav'; audio(out/fn,obs)
            specimens.append({'file':fn,'obs':obs,'budget':budget,'decoded':None if got<0 else labels[got],'expected':labels[mids[i]]})
    for mode,w in witnesses.items():
        obs=w['obs']; got=decode(books[mode],mids,obs,0); assert got==w['wrong']!=w['true']
        assert decode(books[mode],mids,obs,1)<0
        fn=f'{mode}-unsafe-exact.wav'; audio(out/fn,obs)
        specimens.append({'file':fn,'obs':obs,'budget':0,'decoded':labels[got],'expected':labels[w['true']]})
    receipt={'schema':'mhac-distributed-profile-v1','pins':PINS,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'duration_ms':800,'changes':changes,'clean':clean,'faults':faults,'fault_axes':'profile, error budget 0/1, correct/abstain/wrong; same row/mask/delta across modes','seed':261126,'witnesses':witnesses,'specimens':specimens,'limits':'Known frame/slot alignment; surviving clean symbols except declared substitution; closed catalogue and known outer format; not source authentication or human evidence. Common nominal amplitude and duration, not exact energy or computational cost.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Distributed profile</title><h1>Distributed profile</h1><p>Original synthetic PCM. Start at low volume. No autoplay.</p>'+''.join('<h2>'+s['file']+'</h2><p>'+html.escape(str(s['decoded']))+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in specimens)+'<p><a href="receipt.json">Receipt</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changes':changes,'clean':clean,'faults':faults},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
