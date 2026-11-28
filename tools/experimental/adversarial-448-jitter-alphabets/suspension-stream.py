"""Refs #448/#449. Synthetic aligned PCM hypothesis suspension experiment.
Standalone model, not a reproduction of the pinned longer-body receiver.
"""
import argparse, hashlib, json, wave
from pathlib import Path
from collections import Counter
import numpy as np

SEEDS=(4480741,4480742)
MODES=('hold2','drop3','suspend3','hold4')
CASES=('clean','initial5','interior3','interior5','decoy2','decoy4','prefix2','decoy_initial5','late_decoy_initial5','prefix_interior5','overlap','noise')
N=320; FS=16000; BODY=24; PRE=(13,14,15); END=(12,12)
T=np.arange(N)/FS
BANK=np.exp(2j*np.pi*np.arange(1000,2600,100)[:,None]*T)

def sha(x): return hashlib.sha256(x).hexdigest()

def render(seed,case,j):
    rng=np.random.default_rng(np.random.SeedSequence([seed,j])); data=rng.integers(0,8,11).tolist()
    data+=[sum(data)%8]; target=20
    pcm=rng.normal(0,700,(55,N)); phase=rng.uniform(0,2*np.pi,(8,55))
    def put(at,word,voice=0):
        for k,v in enumerate(word):
            if v is not None: pcm[at+k]+=1600*np.sin(2*np.pi*(1000+100*v)*T+phase[voice,at+k])
    body=data*2
    holes={'initial5':range(5),'interior3':range(7,10),'interior5':range(7,12),'decoy_initial5':range(5),'late_decoy_initial5':range(5),'prefix_interior5':range(7,12)}.get(case,())
    for k in holes: body[k]=None
    if case!='noise': put(target,[*PRE,*body,*END])
    ds={'decoy2':[0,8],'decoy4':[0,4,8,12],'prefix2':[0,8],'decoy_initial5':[0,8],'late_decoy_initial5':[8,12],'prefix_interior5':[0,8],'overlap':[18]}.get(case,[])
    for i,d in enumerate(ds): put(d,[*PRE,*([0,1] if case in ('prefix2','prefix_interior5') else [])],i+1)
    return np.rint(pcm).clip(-32768,32767).astype('<i2'),(target,data) if case!='noise' else None

def observe(pcm):
    amp=2*abs(pcm.astype(float)@BANK.conj().T)/N
    order=np.argsort(amp,axis=1); a=amp[np.arange(len(pcm)),order[:,-1]]; b=amp[np.arange(len(pcm)),order[:,-2]]
    return [int(k) if x>=700 and x>=1.35*y else None for k,x,y in zip(order[:,-1],a,b)]

def decode(obs):
    if tuple(obs[-2:])!=END: return None
    result=[]
    for a,b in zip(obs[:12],obs[12:24]):
        values={v for v in (a,b) if v is not None}
        if len(values)!=1 or not values<=set(range(8)): return None
        result.append(values.pop())
    return result if sum(result[:11])%8==result[11] else None

def receive(symbols,mode):
    live={}; sleeping={}; events=[]; releases=[]; updates=probes=peak=active_peak=0
    cap=4 if mode=='hold4' else 2; memory=4 if mode=='suspend3' else cap
    def log(t,k,on): events.append([t,k,on])
    for t,s in enumerate(symbols):
        for on in sorted([*live,*sleeping]):
            asleep=on in sleeping; h=(sleeping if asleep else live)[on]
            pos=t-on-3
            if pos<0: continue
            v=s if (s is not None and (s<8 if pos<BODY else s==12)) else None
            if asleep:
                probes+=1
                if v is not None and len(live)<cap:
                    live[on]=sleeping.pop(on); asleep=False; log(t,'wake',on)
            if not asleep:
                updates+=1; h[pos]=v
            if pos==BODY+1:
                result=decode(h); (sleeping if asleep else live).pop(on)
                if result is not None: releases.append([on,result]); log(t,'release',on)
                else: log(t,'expire',on)
            elif not asleep and mode in ('drop3','suspend3') and pos>=2 and all(x is None for x in h[pos-2:pos+1]):
                live.pop(on); log(t,'sleep' if mode=='suspend3' else 'drop',on)
                if mode=='suspend3': sleeping[on]=h
        if t>=2 and tuple(symbols[t-2:t+1])==PRE:
            on=t-2
            if len(live)>=cap: log(t,'refuse_active',on)
            else:
                if len(live)+len(sleeping)>=memory:
                    old=min(sleeping); sleeping.pop(old); log(t,'evict',old)
                live[on]=[None]*(BODY+2); log(t,'admit',on)
        peak=max(peak,len(live)+len(sleeping)); active_peak=max(active_peak,len(live))
        assert len(live)<=cap and len(live)+len(sleeping)<=memory
    return dict(releases=releases,events=events,updates=updates,probes=probes,peak=peak,active_peak=active_peak)

def main(out):
    out.mkdir(parents=True,exist_ok=False); rows=[]; agg={}; checks=0
    for seed in SEEDS:
        for case in CASES:
            for j in range(32):
                pcm,want=render(seed,case,j); symbols=observe(pcm); digest=sha(pcm.tobytes())
                if seed==SEEDS[0] and j==0:
                    with wave.open(str(out/(case+'.wav')),'wb') as f:
                        f.setparams((1,2,FS,0,'NONE','not compressed')); f.writeframes(np.rint(pcm/4).astype('<i2').tobytes())
                for mode in MODES:
                    q=receive(symbols,mode); good=sum(want is not None and [want[0],want[1]]==x for x in q['releases']); wrong=len(q['releases'])-good
                    if j==0:
                        for t in (10,20,30,40,55):
                            assert receive(symbols[:t],mode)['events']==[e for e in q['events'] if e[0]<t]; checks+=1
                    row=dict(seed=seed,case=case,j=j,mode=mode,pcm_sha256=digest,want=want,symbols=symbols,correct=good,wrong=wrong,**q); rows.append(row)
                    agg.setdefault(case,{}).setdefault(mode,Counter()).update(correct=good,wrong=wrong,withheld=int(want is not None and not good),updates=q['updates'],probes=q['probes'],wakes=sum(e[1]=='wake' for e in q['events']),refused=sum(e[1]=='refuse_active' for e in q['events']))
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt=dict(seeds=SEEDS,rows=len(rows),prefix_checks=checks,summary=agg,source_sha256=sha(Path(__file__).read_bytes()),model='aligned slot PCM; no source separation; no human evidence')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('out',type=Path); main(p.parse_args().out)
