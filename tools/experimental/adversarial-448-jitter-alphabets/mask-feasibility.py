"""Refs #448/#449: bounded PCM source attribution; synthetic only, single AI agent."""
import hashlib, itertools, json, pathlib, sys, wave
import numpy as np

PIN = '50ae75f6303d4dd57aba337a6784aa21895b1622'
BLOB = '08fc9dc5d2553f181ee48b3a28db5eeb9263598c'
W = np.array([[1,1,1,1],[1,1,-1,-1],[1,-1,1,-1],[1,-1,-1,1]])
P = np.array([int(3000*(16-4*abs(j%16-8))*min(j,159-j)/(16*80)) for j in range(160)])
MASKS = [m for n in range(1,5) for m in itertools.combinations(range(4),n)]
GAINS = (.125,.5)
POLICIES = ['union','alias-veto','honest-feasible','spoof-feasible','spoof-target-required']

def signal(g,v,o):
    x=np.zeros((4,400),dtype=np.int16)
    x[:,o:o+160]=W[v,:,None]*np.rint(P*g).astype(np.int16)
    return x

def bank():
    meta=[(-1,'null')]; waves=[signal(0,0,176)]
    def add(o,k,x):
        meta.append((o,k)); waves.append(x)
    for o in range(160,193):
        for v in (0,1):
            for g in GAINS:
                x=signal(g,v,o); add(o,'isolated',x)
                for k,l in [('honest',2),('spoof',0)]:
                    for d,r in itertools.product((-10,10),(.5,1.,2.)):
                        add(o,k,x+signal(g*r,l+1-v,o+d))
            for g in sorted({g*r for g in GAINS for r in (.5,1.,2.)}):
                add(-1,'honest-only',signal(g,2+v,o))
                add(-1,'spoof-only',signal(g,v,o))
    return np.array(waves),np.array([o for o,k in meta]),np.array([k for o,k in meta])

def decide(s):
    return (min(s)+max(s)+1)//2 if s and min(s)>=0 and max(s)-min(s)<=4 else None

def baseline(x,m,level):
    b=np.stack([x[:,o:o+160].astype(np.int64)@P/(P@P) for o in range(160,193)],axis=1)
    q=W[:2,list(m)]@b[list(m)]/len(m)
    threshold=level*np.abs(P).sum()/(P@P)
    sets=[set((np.flatnonzero((r>threshold+1e-12)&(r>=.95*r.max()))+160).tolist()) for r in q]
    z=decide(set.union(*sets)); alias=any(sets[v] and any(np.array_equal(W[v,list(m)],W[w,list(m)]) for w in (2,3)) for v in (0,1))
    return [z,None if alias else z]

def compatible(templates,x,level):
    # Necessary anchor test, followed by exact all-sample integer check.
    a=np.arange(160,352,4); good=[]
    for i in range(4):
        idx=np.flatnonzero(np.all(np.abs(templates[:,i,a].astype(np.int32)-x[i,a])<=level,axis=1))
        ok=idx[np.all(np.abs(templates[idx,i,:].astype(np.int32)-x[i])<=level,axis=1)]
        row=np.zeros(len(templates),dtype=bool); row[ok]=True; good.append(row)
    return np.array(good)

def wav(path,x,m):
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,8000,0,'NONE','not compressed'))
        w.writeframes(np.rint(np.array([x[i] if i in m else np.zeros(400) for i in range(4)])*.25).astype('<i2').tobytes())

def run(out):
    out.mkdir(); templates,onsets,kinds=bank(); honest=~np.isin(kinds,['spoof','spoof-only']); required=onsets>=0
    rows=[]; summary={}; witness={}; checks=0
    for seed,level in itertools.product(range(1500,1506),(0,128,512)):
        noise=np.random.default_rng(seed).integers(-level,level+1,size=(4,400)); o=176+seed%13-6; v=seed%2; d=10 if seed%3 else -10
        configs=[('null',-1,noise)];
        for g in GAINS:
            x=signal(g,v,o); configs += [('isolated',o,x+noise),('honest-only',-1,signal(g,2+v,o)+noise),('spoof-only',-1,x+noise)]
            for r,k in itertools.product((.5,1.,2.),('honest','spoof')):
                configs.append((k,o,x+signal(g*r,(2 if k=='honest' else 0)+1-v,o+d)+noise))
            configs += [('gain-shift',o,signal(g*1.25,v,o)+noise),('timing-shift',o,x+signal(g,3-v,o+7)+noise)]
        for ci,(k,truth,x) in enumerate(configs):
            x=x.astype(np.int16); good=compatible(templates,x,level)
            if seed==1500 and level==128:
                direct=np.max(np.abs(templates.astype(np.int32)-x),axis=2)<=level
                assert np.array_equal(good,direct.T); checks+=1
            for m in MASKS:
                fit=good[list(m)].all(axis=0); sets=[set(onsets[fit&f].tolist()) for f in (honest,np.ones(len(onsets),bool),required)]
                ds=baseline(x,m,level)+[decide(s) for s in sets]
                if k not in ('gain-shift','timing-shift'):
                    assert truth in sets[1]; checks+=1
                    if k not in ('spoof','spoof-only'): assert truth in sets[0]; checks+=1
                    if truth>=0: assert truth in sets[2]; checks+=1
                labels=['abstain' if z is None else 'correct' if truth>=0 and abs(z-truth)<=2 else 'wrong' for z in ds]
                if k not in ('gain-shift','timing-shift'): assert labels[3]!='wrong'; checks+=1
                if k not in ('spoof','spoof-only','gain-shift','timing-shift'): assert labels[2]!='wrong'; checks+=1
                if truth>=0 and k not in ('gain-shift','timing-shift'): assert labels[4]!='wrong'; checks+=1
                key=k+'/'+''.join(map(str,m)); s=summary.setdefault(key,[[0,0,0] for _ in ds])
                for j,z in enumerate(labels): s[j][['correct','wrong','abstain'].index(z)]+=1
                row=[seed,level,k,truth,list(m),ds,labels,[sorted(s) for s in sets],hashlib.sha256(x.astype('<i2').tobytes()).hexdigest(),ci]; rows.append(row)
                for name,test in [('rescue',k=='honest' and len(m)<4 and labels[1]!='correct' and labels[2]=='correct'),('false-source',k=='spoof-only' and labels[2]=='wrong' and labels[3]=='abstain'),('mismatch',k in ('gain-shift','timing-shift') and labels[3]=='wrong')]:
                    if test and name not in witness: witness[name]=row; wav(out/(name+'.wav'),x,m)
    x=signal(.5,0,176); y=signal(.5,0,176) # Same-label rival alone, versus target alone.
    assert np.array_equal(x,y); checks+=1
    a=x+signal(.5,1,186); b=signal(.5,1,186)+signal(.5,0,176)
    assert np.array_equal(a,b); checks+=1
    wav(out/'equal-gain-swap.wav',a,(0,1,2,3))
    wav(out/'source-or-impersonator.wav',x,(0,1,2,3))
    receipt={'parent':PIN,'parent_blob':BLOB,'policies':POLICIES,'seeds':[1500,1505],'templates':len(templates),'checks':checks,'row_fields':['seed','noise_bound','condition','truth','mask','decisions','labels','candidate_onsets','pcm_sha256','config_index'],'rows':rows,'summary':summary,'witness':witness,'limits':'Known aligned packet mask and uniform sample noise bound, fixed waveform/gain/offset catalogue; spoof-aware includes absent target and same-label rival. Gain-shift and timing-shift deliberately outside catalogue. No human evidence or physical-channel claim; same PCM per policy, not matched computation.'}
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':'))+'\n')
    (out/'manifest.json').write_text(json.dumps({'script':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}},indent=2)+'\n')
    print(json.dumps({'templates':len(templates),'rows':len(rows),'checks':checks,'summary':{k:v for k,v in summary.items() if k.endswith('/0123')},'witness':witness},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
