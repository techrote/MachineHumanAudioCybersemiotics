"""Refs #448/#449. Synthetic asynchronous whole-codeword mixtures, Run 035.
Usage: python asynchronous-attribution.py PINNED_DIR NEW_OUTPUT_DIR
No perceptual or human evidence. All timing priors fixed before execution.
"""
import hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np
PARENT='71910f5f4a8f07cce0786deb4d65b8006f56778b'
GRAMMAR='aca863378e825b26921388cfaab890f9eac86279'
BLOBS={'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','temporal-admission.py':'6a2821c9c4453c1f462da279f439aa8fb601e3ed'}
SEED=448035
# Name, A/B arrival endpoints ms, B/A RMS gain, mixture SNR dB.
CASES=[('shared',(17,17),(17,17),1,None),('separated',(-13,-13),(37,37),1,None),('opposite',(-13,33),(27,-18),1,None),('opposite-noise',(-13,33),(27,-18),1,-6),('opposite-louder',(-13,33),(27,-18),2.5,None),('separated-noise',(-13,-13),(37,37),1,-6)]
FS=16000; N=12800; PAD=1280; T=np.arange(N); CAP=np.arange(N+2*PAD); BINS=np.arange(16,81,4)
GRIDS=[(v,v) for v in (-20,-10,0,10,20,30,40)]+[(c-d/2,c+d/2) for c in (-10,10,30) for d in (-40,40)]
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def arrival(g): return PAD+T+np.linspace(g[0]*16,g[1]*16,N)
def feature(pcm,g):
    pos=arrival(g); assert pos.min()>=0 and pos.max()<=CAP[-1]
    z=np.interp(pos,CAP,pcm).reshape(10,1280)
    p=np.abs(np.fft.rfft(z[:,160:800],axis=1))[:,BINS]**2
    mag=np.sqrt(p); rel=mag/np.maximum(mag.max(axis=1,keepdims=True),1e-30)
    return rel>=.25,float(np.mean(p.max(axis=1)/np.maximum(p.sum(axis=1),1e-30))),float(np.sum(z[:,960:]**2)/max(np.sum(z**2),1e-30))
def main(root,out):
    for n,h in BLOBS.items(): assert blob((root/n).read_bytes())==h,n
    _,_,_,book,names,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    assert book.shape==(68204,10)
    excluded=np.array([],dtype=int)
    for seed in (448031,448032,448034):
        rng=np.random.default_rng(seed); excluded=np.r_[excluded,rng.choice(np.setdiff1d(np.arange(52000),excluded),16,False),rng.choice(np.setdiff1d(np.arange(52000,len(book)),excluded),16,False)]
    rng=np.random.default_rng(SEED); origins=np.r_[rng.choice(np.setdiff1d(np.arange(52000),excluded),12,False),rng.choice(np.setdiff1d(np.arange(52000,len(book)),excluded),12,False)]
    packed=[[int.from_bytes(np.packbits(book[:,s]==v,bitorder='little').tobytes(),'little') for v in range(17)] for s in range(10)]
    def candidates(allowed):
        m=(1<<len(book))-1
        for s in range(10):
            v=0
            for k in np.flatnonzero(allowed[s]): v|=packed[s][k]
            m&=v
        return m
    def union(ms):
        u=0
        for m in ms: u|=m
        return u
    env=np.minimum(1,np.minimum(np.arange(960)/80,(959-np.arange(960))/80)); t=np.arange(960)/FS
    def render(word,ph,g):
        z=np.zeros((10,1280)); z[:,:960]=env*np.sin(2*np.pi*(400+100*word[:,None])*t+ph[:,None]); x=np.interp(CAP,arrival(g),z.ravel(),left=0,right=0); return x/np.linalg.norm(x)
    out.mkdir(parents=True,exist_ok=False); rows=[]; summary={}; specimens=[]; checks=0; used=set(map(int,np.r_[excluded,origins]))
    for i in origins:
        i=int(i); pool=np.flatnonzero(np.count_nonzero(book!=book[i],axis=1)==7); j=int(rng.choice(np.setdiff1d(pool,list(used)))); used.add(j)
        ph=rng.uniform(0,2*np.pi,(2,10)); noise=rng.normal(size=len(CAP)); noise/=np.linalg.norm(noise)
        for label,ga,gb,gain,snr in CASES:
            a=render(book[i],ph[0],ga); b=render(book[j],ph[1],gb)*gain; x=a+b
            if snr is not None: x=x+noise*np.linalg.norm(x)*10**(-snr/20)
            scale=2048/max(abs(x)); pcm=np.rint(x*scale).astype('<i2'); raw=pcm.tobytes()
            # Literal role reversal, same sources and noise; no role marker in PCM.
            y=b+a
            if snr is not None: y=y+noise*np.linalg.norm(y)*10**(-snr/20)
            assert np.array_equal(pcm,np.rint(y*(2048/max(abs(y)))).astype('<i2'))
            f=[feature(pcm,g) for g in GRIDS]; masks=[candidates(v[0]) for v in f]; guard=[v[2] for v in f]; conc=[v[1] for v in f]
            if i==int(origins[0]):
                for v,m in zip(f,masks):
                    dense=np.flatnonzero(v[0][np.arange(10),book].all(axis=1)); assert m==sum(1<<int(k) for k in dense); checks+=1
            base={'nominal':masks[2],'concentration':masks[int(np.argmax(conc))],'union':union(masks),'guard08':union(m for m,v in zip(masks,guard) if v<=min(guard)+.08)}
            for role,target,rival,g in [('A',i,j,ga),('B',j,i,gb)]:
                # External target timing cue: endpoints rounded to nearest 10ms, tolerance 20ms.
                cue=tuple(round(v/10)*10 for v in g); admitted=[k for k,h in enumerate(GRIDS) if max(abs(u-v) for u,v in zip(h,cue))<=20]; assert admitted
                p=dict(base,cue_union=union(masks[k] for k in admitted),cue_guard08=union(masks[k] for k in admitted if guard[k]<=min(guard[n] for n in admitted)+.08),oracle=candidates(feature(pcm,g)[0]))
                decisions={}
                for n,m in p.items():
                    count=m.bit_count(); retained=bool(m&(1<<target)); outcome=('correct' if retained else 'wrong') if count==1 else ('ambiguous' if count else 'empty')
                    decisions[n]=dict(outcome=outcome,count=count,retained=retained,rival_retained=bool(m&(1<<rival)),unique=m.bit_length()-1 if count==1 else None)
                    d=summary.setdefault(label,{}).setdefault(n,dict(correct=0,wrong=0,empty=0,ambiguous=0,retained=0)); d[outcome]+=1; d['retained']+=retained
                rows.append(dict(condition=label,role=role,target=target,rival=rival,target_semantics=names[target],rival_semantics=names[rival],pcm_sha256=sha(raw),cue=cue,admitted=admitted,guard=guard,concentration=conc,target_support=sum(bool(m&(1<<target)) for m in masks),rival_support=sum(bool(m&(1<<rival)) for m in masks),decisions=decisions))
            if i==int(origins[0]):
                fn=label+'.wav'
                with wave.open(str(out/fn),'wb') as w: w.setparams((1,2,FS,0,'NONE','not compressed')); w.writeframes(raw)
                with wave.open(str(out/fn),'rb') as w: assert w.readframes(len(CAP))==raw
                specimens.append(dict(file=fn,sha256=sha(raw),A=i,B=j,peak=int(max(abs(pcm)))))
    assert len(rows)==288 and checks==78
    for a,b in zip(rows[::2],rows[1::2]):
        assert a['pcm_sha256']==b['pcm_sha256'] and a['target']==b['rival']
        for p in ('nominal','concentration','union','guard08'):
            assert a['decisions'][p]['unique']==b['decisions'][p]['unique']
            assert not (a['decisions'][p]['outcome']==b['decisions'][p]['outcome']=='correct')
    aggregate={p:{k:sum(d[p][k] for d in summary.values()) for k in next(iter(summary.values()))[p]} for p in rows[0]['decisions']}
    receipt=dict(schema='mhac-asynchronous-attribution-v1',parent=PARENT,grammar=GRAMMAR,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),runtime=[sys.version.split()[0],np.__version__],seed=SEED,excluded=excluded.tolist(),origins=origins.tolist(),cases=CASES,grids=GRIDS,summary=summary,aggregate=aggregate,rows=rows,specimens=specimens,dense_checks=checks,limits='24 fresh pairs; full ten-slot rival codeword, independent affine arrival maps, equal RMS except louder case. Both role labels on each identical PCM, not independent trials. Complete capture, no edge padding within extraction. Cue derives from simulator true target timing, not acoustic inference. Oracle knows exact timing, not source waveform. No tuning, matched PCM, unequal compute. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join('<p>'+html.escape(s['file'])+' (A '+str(s['A'])+', B '+str(s['B'])+') <audio controls preload="none" src="'+s['file']+'"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Asynchronous attribution</title><h1>Same PCM, two intended identities</h1><p>Opt-in synthetic specimens; start low. No calibrated SPL.</p>'+gallery+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><a href="receipt.json">Full receipt</a>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(aggregate,indent=2))
if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
