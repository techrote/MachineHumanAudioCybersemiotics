"""Refs #448/#449. Fresh synthetic timing-admission falsification, not perception.
python temporal-admission.py PINNED_DIR NEW_OUTPUT_DIR
"""
import hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np

PINS={'grammar':'aca863378e825b26921388cfaab890f9eac86279','adversarial':'cd3d36265f8208ee7d9b488028c2c541c79f012c','measurement':'d628756682460ab95d95e0c96ff95be3dae0ecd8'}
BLOBS={'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','joint-grid-audit.py':'1bf6eecfac00af924f1d2fc542525c8ec0ae63b3','heldout-retention.py':'4fd5b8e65670ff2d06aab7ad602141f43c6f4c8c'}
SEED=448034
# label, start/end arrival offsets in ms, contested slots, rival/third gains, mixture SNR dB
CASES=[('clean',0,0,0,0,0,None),('offset17',17,17,0,0,0,None),('offset-neg13-noise',-13,-13,0,0,0,-12),('drift-up',-13,33,0,0,0,None),('drift-down-noise',27,-18,0,0,0,-6),('interference-offset',17,17,7,2.5,1.6,-6),('interference-drift-up',-13,33,7,2.5,1.6,-6),('interference-drift-down',27,-18,7,2.5,1.6,-6),('four-contested-drift',-13,33,4,2.5,1.6,-6)]
# Fixed prior to observing outputs. Seven constant offsets plus six affine warps.
GRIDS=[(v,v) for v in (-20,-10,0,10,20,30,40)]+[(c-d/2,c+d/2) for c in (-10,10,30) for d in (-40,40)]
FS=16000; N=12800; T=np.arange(N); BINS=np.arange(16,81,4)
POLICIES=('nominal','prior_union','constant_union','affine_union','concentration','guard_best','guard03_union','guard08_union','oracle')
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def arrival(grid): return T+np.linspace(grid[0]*16,grid[1]*16,N)
def feature(pcm,grid):
    z=np.interp(arrival(grid),T,pcm,left=0,right=0).reshape(10,1280)
    power=np.abs(np.fft.rfft(z[:,160:800],axis=1))[:,BINS]**2
    mag=np.sqrt(power); rel=mag/np.maximum(mag.max(axis=1,keepdims=True),1e-30)
    concentration=float(np.mean(power.max(axis=1)/np.maximum(power.sum(axis=1),1e-30)))
    guard=float(np.sum(z[:,960:]**2)/max(np.sum(z**2),1e-30))
    return rel>=.25,concentration,guard

def main(root,out):
    for n,h in BLOBS.items(): assert blob((root/n).read_bytes())==h,n
    _,_,_,book,names,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    assert book.shape==(68204,10)
    # Reconstruct both prior origin samples exactly, then exclude both.
    a=np.random.default_rng(448031); old=np.r_[a.choice(52000,16,False),a.choice(np.arange(52000,len(book)),16,False)]
    a=np.random.default_rng(448032); old2=np.r_[a.choice(np.setdiff1d(np.arange(52000),old),16,False),a.choice(np.setdiff1d(np.arange(52000,len(book)),old),16,False)]
    excluded=np.r_[old,old2]; rng=np.random.default_rng(SEED)
    origins=np.r_[rng.choice(np.setdiff1d(np.arange(52000),excluded),16,False),rng.choice(np.setdiff1d(np.arange(52000,len(book)),excluded),16,False)]
    assert not np.intersect1d(origins,excluded).size
    packed=[[int.from_bytes(np.packbits(book[:,s]==v,bitorder='little').tobytes(),'little') for v in range(17)] for s in range(10)]
    def candidates(allowed):
        mask=(1<<len(book))-1
        for s in range(10):
            m=0
            for v in np.flatnonzero(allowed[s]): m|=packed[s][v]
            mask&=m
        return mask
    def ids(m):
        return np.flatnonzero(np.unpackbits(np.frombuffer(m.to_bytes((len(book)+7)//8,'little'),dtype=np.uint8),bitorder='little')[:len(book)]).tolist()
    def union(ms):
        u=0
        for m in ms: u|=m
        return u
    out.mkdir(parents=True,exist_ok=False); rows=[]; summary={}; specimens=[]; checked=0
    env=np.minimum(1,np.minimum(np.arange(960)/80,(959-np.arange(960))/80)); t=np.arange(960)/FS
    def tone(s,p): return env*np.sin(2*np.pi*(400+100*int(s))*t+p)
    for i in origins:
        i=int(i); a=book[i]; j=int(rng.choice(np.flatnonzero(np.count_nonzero(book!=a,axis=1)==7))); b=book[j]
        pos=rng.permutation(np.flatnonzero(a!=b)); third=[int(rng.choice(np.setdiff1d(np.arange(17),[x,y]))) for x,y in zip(a,b)]
        phase=rng.uniform(0,2*np.pi,(10,3)); noise=rng.normal(size=N); noise/=np.linalg.norm(noise)
        for label,start,end,k,r,q,snr in CASES:
            signal=np.zeros((10,1280))
            for s in range(10):
                base=tone(a[s],phase[s,0]); mix=base.copy()
                if s in pos[:k]: mix+=r*tone(b[s],phase[s,1])+q*tone(third[s],phase[s,2])
                signal[s,:960]=1024*mix*np.linalg.norm(base)/np.linalg.norm(mix)
            x=np.interp(T,arrival((start,end)),signal.ravel(),left=0,right=0)
            z=x if snr is None else x+noise*np.linalg.norm(x)*10**(-snr/20)
            pcm=np.rint(z*min(1,2048/max(abs(z)))).astype('<i2'); assert np.max(np.abs(pcm))<=2048
            grids=[feature(pcm,g) for g in GRIDS]; masks=[candidates(f[0]) for f in grids]
            oracle=candidates(feature(pcm,(start,end))[0]); conc=[f[1] for f in grids]; guard=[f[2] for f in grids]
            if i==int(origins[0]):
                for f,m in zip(grids,masks):
                    assert ids(m)==np.flatnonzero(f[0][np.arange(10),book].all(axis=1)).tolist(); checked+=1
            c=int(np.argmax(conc)); g=int(np.argmin(guard)); g03=[n for n,v in enumerate(guard) if v<=guard[g]+.03]; g08=[n for n,v in enumerate(guard) if v<=guard[g]+.08]
            allmask=union(masks); p={'nominal':masks[2],'prior_union':union(masks[2:6]),'constant_union':union(masks[:7]),'affine_union':allmask,'concentration':masks[c],'guard_best':masks[g],'guard03_union':union(masks[n] for n in g03),'guard08_union':union(masks[n] for n in g08),'oracle':oracle}
            assert tuple(p)==POLICIES and not (p['guard03_union']&~p['guard08_union']) and not (p['guard08_union']&~allmask)
            decisions={}
            for name,m in p.items():
                n=m.bit_count(); retained=bool(m&(1<<i)); outcome=('correct' if retained else 'wrong') if n==1 else ('ambiguous' if n else 'empty')
                decisions[name]=dict(outcome=outcome,count=n,retained=retained,unique=m.bit_length()-1 if n==1 else None)
                v=summary.setdefault(label,{}).setdefault(name,dict(correct=0,wrong=0,empty=0,ambiguous=0,retained=0)); v[outcome]+=1; v['retained']+=retained
            if label=='clean': assert decisions['nominal']['outcome']=='correct' and decisions['oracle']['outcome']=='correct'
            raw=pcm.tobytes(); row=dict(condition=label,origin=i,rival=j,origin_semantics=names[i],rival_semantics=names[j],positions=pos[:k].tolist(),third=third,pcm_sha256=sha(raw),peak=int(np.max(np.abs(pcm))),concentration=conc,guard_fraction=guard,selected_concentration=c,selected_guard=g,admitted03=g03,admitted08=g08,grid_counts=[m.bit_count() for m in masks],grid_retained=[bool(m&(1<<i)) for m in masks],decisions=decisions); rows.append(row)
            # First origin for every condition; also first wrong guard03 and affine-union witnesses per condition.
            tags=(['first'] if i==int(origins[0]) else [])+[name for name in ('guard03_union','affine_union') if decisions[name]['outcome']=='wrong' and not any(s['condition']==label and s['tag']==name for s in specimens)]
            for tag in tags:
                fn=f'{label}-{tag}.wav'
                with wave.open(str(out/fn),'wb') as f: f.setparams((1,2,FS,0,'NONE','not compressed')); f.writeframes(raw)
                with wave.open(str(out/fn),'rb') as f: assert f.getparams()[:4]==(1,2,FS,N) and f.readframes(N)==raw
                specimens.append(dict(file=fn,tag=tag,condition=label,origin=i,pcm_sha256=sha(raw),peak=row['peak']))
    assert len(rows)==32*len(CASES) and checked==len(CASES)*len(GRIDS)
    assert all(sum(v[k] for k in ('correct','wrong','empty','ambiguous'))==32 for d in summary.values() for v in d.values())
    aggregate={p:{k:sum(d[p][k] for d in summary.values()) for k in next(iter(summary.values()))[p]} for p in POLICIES}
    receipt=dict(schema='mhac-temporal-admission-v1',pins=PINS,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),runtime=[sys.version.split()[0],np.__version__],seed=SEED,origins=origins.tolist(),excluded=excluded.tolist(),conditions=CASES,grids_ms=GRIDS,threshold=.25,guard_margins=[.03,.08],summary=summary,aggregate=aggregate,rows=rows,specimens=specimens,dense_checks=checked,limits='Fixed synthetic corpus and no tuning; known cropped 800ms buffer. Affine arrival offsets at first/last source sample; linear interpolation in both render and inverse sampling, zero outside capture; this models sample-rate warp, not oscillator-independent scheduling drift. Guard fraction measures energy in last 20ms of each hypothesized slot; full rank .25 candidates. Third tone is not an independent message. Oracle uses known true warp, nondeployable. Matched PCM across policies, differing compute; no human/physical/streaming claims.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join('<p>'+html.escape(s['file'])+' <audio controls preload="none" src="'+s['file']+'"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Temporal admission</title><h1>Temporal admission</h1><p>Synthetic PCM; start low, no autoplay, not calibrated SPL.</p>'+gallery+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><h2>Aggregate</h2><pre>'+html.escape(json.dumps(aggregate,indent=2))+'</pre><h2>Conditions</h2><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><a href="receipt.json">Full trace receipt</a>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(aggregate,indent=2))
if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
