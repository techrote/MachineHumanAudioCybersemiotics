"""Refs #448/#449: synthetic joint source/schedule signatures; no human evidence."""
import hashlib, itertools, json, pathlib, sys, wave
import numpy as np

PIN = '2b113aa213c4e513540ae2ad40c4911830d2ae87'
BLOB = '03b11d55f667adbb8c42fda65059b3c4489d351c'
RATE = 8000
MASKS = [m for n in range(1,5) for m in itertools.combinations(range(4),n)]
BANK = np.array([[1,-1,1,-1],[1,1,1,-1]])
WALSH = np.array([[1,1,1,1],[1,1,-1,-1],[1,-1,1,-1],[1,-1,-1,1]])
PULSE = np.array([int(3000*(16-4*abs(j%16-8))*min(j,159-j)/(16*80)) for j in range(160)])
PILOTS = np.rint(1000*np.sin(2*np.pi*np.array([1000,1500])[:,None]*np.arange(64)/RATE)).astype(int)
E = PULSE@PULSE

def component(gain, label, prefix):
    body=np.rint(PULSE*gain*np.sqrt(.8 if prefix else 1)).astype(int)
    tag=np.rint(PILOTS[label]*gain*np.sqrt(.2*E/(PILOTS[label]@PILOTS[label]))).astype(int) if prefix else np.zeros(64,dtype=int)
    return body,tag

def scene(noise, gain, variant, kind, shift, ratio, onset, prefix):
    x=noise.copy(); energies=[]
    for g,v,l,o in [(gain,variant,0,onset),(gain*ratio,1-variant,int(kind=='honest'),onset+shift)]:
        body,tag=component(g,l,prefix); s=BANK[v] if prefix else WALSH[2*l+v]
        x[:,o:o+160]+=s[:,None]*body; x[:,:64]+=s[:,None]*tag
        energies.append(int(body@body+tag@tag))
    assert np.max(np.abs(x))<32768
    return x.astype('<i2'),energies

def features(x):
    body=np.stack([x[:,o:o+160]@PULSE/E for o in range(160,193)],axis=1)
    tag=x[:,:64]@PILOTS[0]/(PILOTS[0]@PILOTS[0])
    return body,tag

def scores(f,m,prefix):
    b,t=f; s=(BANK if prefix else WALSH[:2])[:,m]
    return s@b[list(m)]/len(m),s@t[list(m)]/len(m)

def candidates(q,threshold):
    return [set(np.flatnonzero((r>threshold)&(r>=.95*r.max()))+160) for r in q]

def decision(s):
    return int((min(s)+max(s)+1)//2) if s and max(s)-min(s)<=4 else None

def decode(f,m,threshold,prefix):
    q,t=scores(f,m,prefix); sets=candidates(q,threshold[0]); union=set().union(*sets)
    if prefix:
        p=np.flatnonzero((t>threshold[1])&(t>=.95*t.max()))
        return [decision(sets[p[0]]) if len(p)==1 else None,decision(union)]
    alias=any(sets[v] and any(np.array_equal(WALSH[v,list(m)],WALSH[w,list(m)]) for w in (2,3)) for v in (0,1))
    return [decision(union),None if alias else decision(union)]

def noise_for(seed,level):
    return np.random.default_rng(seed).integers(-level,level+1,size=(4,400))

def run(out):
    out.mkdir(); thresholds={}
    for prefix in (True,False):
        for m in MASKS:
            q=[scores(features(noise_for(seed,level)),m,prefix) for seed in range(1300,1312) for level in (0,128,512)]
            thresholds[prefix,m]=[max(0.,max(float(a.max()) for a,b in q)),max(0.,max(float(b.max()) for a,b in q))]
    rows=[]; summary={}; mismatch=0.; witness=None
    for seed in range(1400,1412):
        onset=176+seed%13-6
        for level in (0,128,512):
            noise=noise_for(seed,level)
            configs=[(0.,0,'null',10,0.)]+[(g,v,k,d,r) for g in (.125,.5) for v in (0,1) for k in ('honest','spoof','isolated') for d in (-10,10) for r in ((.5,1.,2.) if k!='isolated' else (0.,))]
            for g,v,k,d,r in configs:
                a,ea=scene(noise,g,v,k,d,r,onset,True); b,eb=scene(noise,g,v,k,d,r,onset,False)
                mismatch=max([mismatch]+[abs(x/y-1) for x,y in zip(ea,eb) if y]); fa,fb=features(a),features(b)
                hashes=[hashlib.sha256(x.tobytes()).hexdigest() for x in (a,b)]
                for m in MASKS:
                    ds=decode(fa,m,thresholds[True,m],True)+decode(fb,m,thresholds[False,m],False)
                    labels=['abstain' if z is None else 'correct' if g and abs(z-onset)<=2 else 'wrong' for z in ds]
                    key=k+'/'+''.join(map(str,m)); s=summary.setdefault(key,[[0,0,0] for _ in ds])
                    for j,z in enumerate(labels):s[j][['correct','wrong','abstain'].index(z)]+=1
                    rows.append([seed,level,g,v,k,d,r,onset,list(m),ds,labels,hashes])
                    if witness is None and k=='honest' and len(m)==2 and labels[2]=='wrong' and labels[3]=='abstain':
                        witness=rows[-1]; savewav(out/'honest-alias.wav',b,m)
    # Clean equal-gain same-label source swap: exact PCM indistinguishability.
    n=np.zeros((4,400),dtype=int)
    x,_=scene(n,.5,0,'spoof',10,1.,176,False); y,_=scene(n,.5,1,'spoof',-10,1.,186,False)
    assert np.array_equal(x,y); savewav(out/'spoof-swap.wav',x,tuple(range(4)))
    assert witness is not None
    assert np.array_equal(WALSH@WALSH.T,4*np.eye(4))
    aliases={''.join(map(str,m)):[[i,j] for i in (0,1) for j in (2,3) if np.array_equal(WALSH[i,list(m)],WALSH[j,list(m)])] for m in MASKS}
    receipt={'parent':PIN,'parent_blob':BLOB,'policies':['prefix-guided','prefix-union','joint-union','joint-alias-veto'],'development_seeds':[1300,1311],'evaluation_seeds':[1400,1411],'thresholds':{str(k):v for k,v in thresholds.items()},'rows':rows,'summary':summary,'max_component_energy_mismatch':mismatch,'aliases':aliases,'witness':witness,'swap_sha256':hashlib.sha256(x.tobytes()).hexdigest(),'limits':'Aligned 8kHz, 4x50ms, known mask/onset window and label, two variants, synthetic uniform sample noise; no matched occupied bandwidth or compute, no authentication; null-max calibration, finite grid only.'}
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':'))+'\n')
    (out/'manifest.json').write_text(json.dumps({'script':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}},indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'summary':{k:v for k,v in summary.items() if k.endswith('/0123') or k.endswith('/02')},'mismatch':mismatch,'aliases':aliases,'witness':witness},indent=2))

def savewav(path,x,m):
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(np.rint(np.array([x[i] if i in m else np.zeros(400) for i in range(4)])*.25).astype('<i2').tobytes())

if __name__=='__main__':run(pathlib.Path(sys.argv[1]))
