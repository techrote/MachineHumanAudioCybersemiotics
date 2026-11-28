"""Refs #448/#449; synthetic held-out spectral retention stress test.
python heldout-retention.py PINNED_DIR NEW_OUTPUT_DIR
No fitted threshold, human evidence, or source authentication claim.
"""
import hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np

PINS={'grammar':'aca863378e825b26921388cfaab890f9eac86279','adversarial':'f4ecd30005c123d39452cac7937ca6266f791179','measurement':'9c69d4d11ecb5f84630d44b7a92800eb830de56a'}
BLOBS={'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','rival-tone-audit.py':'62a58dae6a86d86439a364d6644f92be63891bf6','candidate-retention.py':'af6e0f81143484a54baec8894f21e3090a8eb8c5'}
SEED=448032
# name, contested slots, rival gain, third gain, SNR dB (None=no noise), sample delay
CONDITIONS=[('clean',0,0,0,None,0),('noise0',0,0,0,0,0),('noise-12',0,0,0,-12,0),('delay30ms',0,0,0,None,480),('two4',4,2.5,0,None,0),('two7',7,2.5,0,None,0),('two4noise',4,2.5,0,-6,0),('two7noise',7,2.5,0,-6,0),('three4',4,2.5,1.6,None,0),('three7',7,2.5,1.6,None,0),('three4noise',4,2.5,1.6,-6,0),('three7delay',7,2.5,1.6,-6,480)]
POLICIES={'top2_.50':(2,.5),'top2_.39':(2,.39),'top3_.39':(3,.39),'top3_.25':(3,.25)}
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def main(root,out):
    for n,h in BLOBS.items(): assert blob((root/n).read_bytes())==h,n
    g=runpy.run_path(str(root/'control-namespace.py')); _,_,_,book,names,_=g['build'](root)
    assert book.shape==(68204,10)
    old=np.random.default_rng(448031); excluded=np.r_[old.choice(52000,16,replace=False),old.choice(np.arange(52000,len(book)),16,replace=False)]
    rng=np.random.default_rng(SEED); origins=np.r_[rng.choice(np.setdiff1d(np.arange(52000),excluded),16,replace=False),rng.choice(np.setdiff1d(np.arange(52000,len(book)),excluded),16,replace=False)]
    assert not np.intersect1d(origins,excluded).size
    out.mkdir(parents=True,exist_ok=False); rows=[]; specimens=[]; summary={}; checks=0
    fs=16000; t=np.arange(960)/fs; env=np.minimum(1,np.minimum(np.arange(960)/80,(959-np.arange(960))/80)); bins=np.arange(16,81,4)
    def tone(s,p): return env*np.sin(2*np.pi*(400+100*int(s))*t+p)
    def save(n,y):
        raw=y.astype('<i2').tobytes()
        with wave.open(str(out/n),'wb') as f: f.setparams((1,2,fs,0,'NONE','not compressed')); f.writeframes(raw)
        with wave.open(str(out/n),'rb') as f: assert f.getparams()[:4]==(1,2,fs,12800) and f.readframes(12800)==raw
        specimens.append({'file':n,'pcm_sha256':sha(raw),'peak':int(np.abs(y).max())})
    for i in origins:
        a=book[i]; j=int(rng.choice(np.flatnonzero(np.count_nonzero(book!=a,axis=1)==7))); b=book[j]
        pos=rng.permutation(np.flatnonzero(a!=b)); third=[int(rng.choice(np.setdiff1d(np.arange(17),[x,y]))) for x,y in zip(a,b)]
        phase=rng.uniform(0,2*np.pi,(10,3)); noise=rng.normal(size=12800); noise/=np.linalg.norm(noise)
        for label,k,r,q,snr,delay in CONDITIONS:
            signal=np.zeros((10,1280)); selected=pos[:k]
            for slot in range(10):
                base=tone(a[slot],phase[slot,0]); mix=base.copy()
                if slot in selected: mix+=r*tone(b[slot],phase[slot,1])+q*tone(third[slot],phase[slot,2])
                signal[slot,:960]=1024*mix*np.linalg.norm(base)/np.linalg.norm(mix)
            x=signal.ravel(); x=np.r_[np.zeros(delay),x][:12800]
            z=x if snr is None else x+noise*np.linalg.norm(x)*10**(-snr/20)
            scale=min(1,2048/max(abs(z))); pcm=np.rint(z*scale).astype('<i2').reshape(10,1280)
            mag=np.abs(np.fft.rfft(pcm[:,160:800],axis=1))[:,bins]; order=np.argsort(-mag,axis=1,kind='stable'); rel=mag/np.maximum(mag.max(axis=1,keepdims=True),1e-30)
            results={}; hard=order[:,0]; masks={'radius3':np.count_nonzero(book!=hard,axis=1)<=3}
            for p,(n,threshold) in POLICIES.items():
                allowed=np.zeros((10,17),bool); np.put_along_axis(allowed,order[:,:n],np.take_along_axis(rel,order[:,:n],axis=1)>=threshold,axis=1)
                masks[p]=allowed[np.arange(10),book].all(axis=1)
                if p=='top2_.50':
                    alt=order[:,1]; direct=((book==hard)|((book==alt)&(rel[np.arange(10),alt]>=.5))).all(axis=1); assert np.array_equal(direct,masks[p]); checks+=1
            for p,mask in masks.items():
                ids=np.flatnonzero(mask); retained=bool(mask[i]); outcome=('correct' if retained else 'wrong') if len(ids)==1 else ('empty' if not len(ids) else 'ambiguous')
                results[p]={'outcome':outcome,'retained':retained,'candidates':ids.tolist()}
                count=summary.setdefault(label,{}).setdefault(p,dict(correct=0,wrong=0,empty=0,ambiguous=0,retained=0)); count[outcome]+=1; count['retained']+=retained
                if label=='clean': assert outcome=='correct'
            row={'condition':label,'origin':int(i),'rival':j,'positions':selected.tolist(),'third':third,'top3':order[:,:3].tolist(),'relative_top3':np.take_along_axis(rel,order[:,:3],axis=1).tolist(),'pcm_sha256':sha(pcm.tobytes()),'peak':int(np.abs(pcm).max()),'scale':scale,'decisions':results}; rows.append(row)
            if i==origins[0] and label in ('clean','two7noise','three4','three7delay','noise-12'): save(label+'.wav',pcm)
    assert len(rows)==384 and checks==384
    assert all(sum(v[k] for k in ('correct','wrong','empty','ambiguous'))==32 for d in summary.values() for v in d.values())
    receipt={'schema':'mhac-heldout-retention-v1','pins':PINS,'blobs':BLOBS,'seed':SEED,'runtime':[sys.version.split()[0],np.__version__],'conditions':CONDITIONS,'policies':POLICIES,'origins':origins.tolist(),'excluded_origins':excluded.tolist(),'summary':summary,'rows':rows,'specimens':specimens,'checks':checks,'limits':'New origins and seeds, fixed policies; adversarial finite corpus, not statistical population. Known nominal slot grid, no synchronization or physical channel. Third tone is not an independent full codeword. Common PCM across policies, cost unmatched. SNR is whole-frame pre-quantization digital energy after shift, same normalized noise direction within origin; attenuation preserves nominal SNR. No human evidence.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Held-out retention</title><h1>Held-out retention audit</h1><p>Synthetic audio, no autoplay; low volume. Not calibrated SPL.</p>'+''.join('<p>'+s['file']+' <audio controls preload="none" src="'+s['file']+'"></audio></p>' for s in specimens)+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><a href="receipt.json">Full receipt</a>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
