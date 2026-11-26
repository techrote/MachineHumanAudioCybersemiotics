"""Adversarial lane, Refs #448/#449, synthetic aligned PCM only.
python rival-tone-audit.py PINNED_SOURCE_DIRECTORY NEW_OUTPUT_DIRECTORY
No fitted thresholds, no participant data, no changes to candidate grammar.
"""
import hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np

PIN = 'aca863378e825b26921388cfaab890f9eac86279'
MEASUREMENT = '8b9abd7ccc7b2d8c4bd278b1233c8d9183cdbc51'
PARENT = '09654d45a051960e8f7a27d51d82469f9d1e7b8e'
BLOBS = {'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493', 'migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1', 'distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f', 'menu-transition-audit.py':'3eac4ea7f661a2abaff2710dbfbfcb84824b2754'}
SEED = 448031
FS=16000; SLOT=1280; ACTIVE=960; PEAK=1024
RATIOS=(0.8,1.1,1.6,2.5); COUNTS=(4,5,7); MARGIN=0.5
POLICIES=('hard_exact','hard_radius3','margin_erasure','two_tone_set')
OUTCOMES=('correct','abstain','wrong')
T=np.arange(ACTIVE)/FS
ENV=np.minimum(1,np.minimum(np.arange(ACTIVE)/80,(959-np.arange(ACTIVE))/80))
BINS=np.arange(16,81,4)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def gitblob(raw): return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()

def render(a,b,positions,ratio,phases):
    y=np.zeros((10,SLOT),dtype='<i2')
    for j in range(10):
        base=ENV*np.sin(2*np.pi*(400+100*int(a[j]))*T+phases[j,0])
        mix=base.copy()
        if j in positions:
            mix+=ratio*ENV*np.sin(2*np.pi*(400+100*int(b[j]))*T+phases[j,1])
        # Hold slot energy constant before integer rounding, including ramp.
        mix*=PEAK*np.linalg.norm(base)/np.linalg.norm(mix)
        y[j,:ACTIVE]=np.rint(mix).astype('<i2')
    assert np.max(np.abs(y))<2048
    return y

def extract(y):
    magnitudes=np.abs(np.fft.rfft(y[:,160:800],axis=1))[:,BINS]
    order=np.argsort(-magnitudes,axis=1,kind='stable')
    top,second=order[:,0],order[:,1]
    ratios=magnitudes[np.arange(10),second]/magnitudes[np.arange(10),top]
    return top,second,ratios

def unique(mask):
    indices=np.flatnonzero(mask)
    return (int(indices[0]) if len(indices)==1 else None),int(len(indices))

def decisions(book,y):
    top,second,ratios=extract(y); uncertain=ratios>=MARGIN
    match=book==top; dist=10-match.sum(axis=1)
    keep=~uncertain; e=min(3,max(0,(6-int(uncertain.sum()))//2))
    erased_dist=np.count_nonzero(~match[:,keep],axis=1)
    # A declared bounded-distance decoder; with >6 erasures no guarantee,
    # but exact survivor consensus can still accept a unique row.
    sets=match | ((book==second)&uncertain)
    out={ 'hard_exact':unique(dist==0), 'hard_radius3':unique(dist<=3),
          'margin_erasure':unique(erased_dist<=e), 'two_tone_set':unique(sets.all(axis=1)) }
    return out,top,second,ratios,e

def main(root,out):
    for name,blob in BLOBS.items():
        assert gitblob((root/name).read_bytes())==blob, name
    upstream=runpy.run_path(str(root/'control-namespace.py'))
    _,_,_,book,names,_=upstream['build'](root)
    assert len(book)==68204
    out.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(SEED)
    origins=np.concatenate([rng.choice(52000,16,replace=False),rng.choice(np.arange(52000,len(book)),16,replace=False)])
    rows=[]; witnesses={}; maximum=0; energy_error=0.; literal_checks=0
    def evaluate(i,j,kind,positions,ratio,phases):
        nonlocal maximum,energy_error,literal_checks
        a,b=book[i],book[j]; y=render(a,b,positions,ratio,phases)
        base=render(a,a,(),0,phases)
        energy=lambda z: np.sum(z.astype(np.float64)**2,axis=1)
        energy_error=max(energy_error,float(np.max(np.abs(energy(y)/energy(base)-1))))
        maximum=max(maximum,int(np.max(np.abs(y))))
        outc,top,second,ratios,e=decisions(book,y)
        expected=a.copy()
        if ratio>1: expected[list(positions)]=b[list(positions)]
        assert np.array_equal(top,expected), (i,j,ratio,positions)
        # Independent direct upstream hard decoder check on every 32nd row.
        if len(rows)%32==0:
            assert upstream['decode'](book,top.tolist(),3)==outc['hard_radius3'][0]
            literal_checks+=1
        if ratio and 0.5<=ratio<=2:
            assert np.array_equal(np.flatnonzero(ratios>=MARGIN),np.array(sorted(positions)))
            assert outc['two_tone_set'][0] in (i,None)
            if len(positions)<7: assert outc['two_tone_set']==(i,1)
        if not ratio: assert all(v==(i,1) for v in outc.values())
        result={p:{'row':v,'candidates':n,'outcome':'correct' if v==i else 'abstain' if v is None else 'wrong'} for p,(v,n) in outc.items()}
        row={'origin':int(i),'rival':int(j),'kind':kind,'distance':int(np.count_nonzero(a!=b)), 'positions':list(map(int,positions)),'ratio':ratio,'top':top.tolist(),'second':second.tolist(),'second_over_first':ratios.tolist(),'margin_budget':e,'decisions':result}
        rows.append(row)
        if kind=='near' and len(positions)==4 and ratio in (1.1,2.5) and result['hard_radius3']['outcome']=='wrong':
            key=f'four-slot-r{ratio}'
            if key not in witnesses: witnesses[key]=(row,y.copy(),base.copy(),render(b,b,(),0,phases))
        if kind=='near' and len(positions)==7 and ratio==1.1 and 'seven-slot-ambiguity' not in witnesses:
            assert result['two_tone_set']['candidates']>=2
            witnesses['seven-slot-ambiguity']=(row,y.copy(),base.copy(),render(b,b,(),0,phases))
    for i in origins:
        d=np.count_nonzero(book!=book[i],axis=1)
        near=int(rng.choice(np.flatnonzero(d==7))); far=int(rng.choice(np.flatnonzero(d>=8)))
        phases=rng.uniform(0,2*np.pi,(10,2))
        evaluate(i,i,'clean',(),0.,phases)
        for kind,j in [('near',near),('far',far)]:
            # One seeded nested slot ordering per rival, identical across ratios.
            changed=rng.permutation(np.flatnonzero(book[i]!=book[j]))
            for k in COUNTS:
                for ratio in RATIOS: evaluate(i,j,kind,tuple(changed[:k]),ratio,phases)
    assert len(rows)==800
    summary={}
    for r in rows:
        key=f"{r['kind']}:k{len(r['positions'])}:r{r['ratio']}"
        group=summary.setdefault(key,{p:dict.fromkeys(OUTCOMES,0) for p in POLICIES})
        for p in POLICIES: group[p][r['decisions'][p]['outcome']]+=1
    assert len(summary)==25 and all(sum(v.values())==32 for g in summary.values() for v in g.values())
    assert len(witnesses)==3
    specimens=[]
    for key,(r,y,base,rival) in witnesses.items():
        for suffix,z in [('source',base),('mixture',y),('rival',rival)]:
            fn=f'{key}-{suffix}.wav'; raw=z.tobytes()
            with wave.open(str(out/fn),'wb') as f: f.setparams((1,2,FS,0,'NONE','not compressed')); f.writeframes(raw)
            with wave.open(str(out/fn),'rb') as f: assert f.getparams()[:4]==(1,2,FS,12800) and f.readframes(12800)==raw
            specimens.append({'file':fn,'case':key,'type':suffix,'pcm_sha256':sha(raw),'digital_peak':int(np.max(np.abs(z))),'origin_identity':names[r['origin']],'rival_identity':names[r['rival']]})
    receipt={'schema':'mhac-rival-tone-audit-v1','pins':{'grammar':PIN,'measurement':MEASUREMENT,'adversarial_parent':PARENT},'source_blobs':BLOBS,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'runtime':{'python':sys.version.split()[0],'numpy':np.__version__},'threshold_second_over_first':MARGIN,'origins':origins.tolist(),'summary':summary,'rows':rows,'witnesses':{k:v[0] for k,v in witnesses.items()},'specimens':specimens,'maximum_pcm_peak':maximum,'max_relative_slot_energy_error':energy_error,'literal_upstream_checks':literal_checks,'limits':'Aligned 80 ms slots, known single desired source, no noise/drift/room/streaming, rival symbol only in selected differing slots, random phases, matched per-slot digital energy before PCM rounding. Artificial targeted interference, not real-world rate. Threshold fixed, no training or population inference. Set receiver assumes true tone survives threshold. Computational cost not matched; no human evidence or physical audition.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    parts=['<!doctype html><meta charset="utf-8"><title>Rival tone audit</title><h1>Rival tone audit</h1><p>Original synthetic PCM. No autoplay. Start at low volume. Same per-slot digital energy; this is not SPL.</p>']
    for key,(r,*_) in witnesses.items():
        parts.append('<h2>'+html.escape(key)+'</h2><pre>'+html.escape(json.dumps(r['decisions'],indent=2))+'</pre>')
        for s in specimens:
            if s['case']==key: parts.append('<p>'+s['type']+' <audio controls preload="none" src="'+s['file']+'"></audio></p>')
    parts.append('<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><p><a href="receipt.json">Complete trace and summary</a></p>')
    (out/'index.html').write_text('\n'.join(parts),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'summary':summary,'maximum_pcm_peak':maximum,'max_relative_slot_energy_error':energy_error,'literal_upstream_checks':literal_checks},indent=2))

if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
