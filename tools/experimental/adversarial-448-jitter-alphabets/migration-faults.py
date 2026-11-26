"""Adversarial #448: exact one-substitution migration census, synthetic only.
Usage: python migration-faults.py PINNED_DISTRIBUTED_PROFILE.py NEW_OUTPUT
Requires NumPy; the upstream source is checked before execution.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import defaultdict
import numpy as np

PIN='28d0433bd9f8a7ad96c616f0544caa9089c8e8e6'
BLOB='a780404e8c76820976ad6fb407429ec895a6313f'
AUDIT='beb414f2a501e5ca1df825c53d7cb5d0b81742c7'
MODES=('tag-pair','free-cubic','reserved-cubic')

def observation(word,v):
    j,d=divmod(v,16); x=word.copy(); x[j]=(x[j]+d+1)%17; return x

def variant(x,y,j):
    return 16*int(j)+(int(y[j])-int(x[j]))%17-1

def run(source,out):
    raw=source.read_bytes()
    if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=BLOB: raise ValueError('pinned source blob mismatch')
    u=runpy.run_path(str(source)); books,ids,p,labels,_=u['catalogue']()
    assert tuple(books)==MODES and len(ids)==52000
    # Distinct cubic bodies disagree in >=5 of 8 slots. A received word
    # within radius one of both origins requires origin distance <=2.
    groups={}
    for mode,w in books.items():
        assert not np.any(np.diff(w[:,:8],n=4,axis=1)%17)
        g=defaultdict(list)
        for i,x in enumerate(w): g[tuple(x[:8])].append(i)
        groups[mode]=g
    report={}; witnesses=[]; checks=0
    for m,w in books.items():
        # Boolean conflict planes; true meaning always retained at radius one.
        conflict={z:np.zeros((len(ids),160),bool) for z in MODES}
        exact={z:defaultdict(set) for z in MODES}
        pairs={z:[0,0,0] for z in MODES}
        for i,x in enumerate(w):
            for z,b in books.items():
                for h in groups[z].get(tuple(x[:8]),()):
                    y=b[h]; d=np.flatnonzero(x!=y); k=len(d); assert k<=2
                    different=ids[i]!=ids[h]
                    if different:
                        pairs[z][k]+=1
                        if k==0: conflict[z][i,:]=True
                        elif k==1: conflict[z][i,16*d[0]:16*(d[0]+1)]=True
                        else:
                            for j in d: conflict[z][i,variant(x,y,j)]=True
                    if k==1: exact[z][160*i+variant(x,y,d[0])].add(int(ids[h]))
        policies={'known':(m,), 'all':MODES}
        if m!='reserved-cubic': policies['tag-free']=MODES[:2]
        for policy,formats in policies.items():
            bad=np.logical_or.reduce([conflict[z] for z in formats]); ex=defaultdict(set)
            for z in formats:
                for k,s in exact[z].items(): ex[k].update(s)
            c=sum(len(s)==1 and int(ids[k//160]) in s for k,s in ex.items())
            wrong=sum(len(s)==1 and int(ids[k//160]) not in s for k,s in ex.items())
            n=160*len(ids); ambiguous=int(bad.sum())
            report[m+':'+policy]={'formats':formats,'total':n,'radius1':[n-ambiguous,ambiguous,0], 'exact':[c,n-c-wrong,wrong], 'pair_counts_by_other_format':{z:pairs[z] for z in formats}}
            # Compare both accelerated outcomes with literal complete-catalogue
            # distances on randomly drawn plus deliberately ambiguous observations.
            rng=np.random.default_rng(44829); picks=list(rng.integers(n,size=12))
            picks+=list(np.flatnonzero(bad)[:8]); picks+=list(sorted(ex)[:8])
            for k in picks:
                i,v=divmod(int(k),160); obs=observation(w[i],v)
                dsets=[set(),set()]
                for z in formats:
                    ds=np.count_nonzero(books[z]!=obs,axis=1)
                    for budget in (0,1): dsets[budget].update(map(int,ids[ds<=budget]))
                assert dsets[0]==ex.get(k,set())
                assert int(ids[i]) in dsets[1] and (len(dsets[1])>1)==bool(bad[i,v]); checks+=1
            if policy=='tag-free':
                # Exact receiver accepts wrong meaning after one substitution.
                k=next((k for k,s in sorted(ex.items()) if len(s)==1 and int(ids[k//160]) not in s),None)
                if k is not None:
                    i,v=divmod(k,160); obs=observation(w[i],v); possible={}
                    for z in formats:
                        ds=np.count_nonzero(books[z]!=obs,axis=1)
                        possible[z]=[sorted(set(map(int,ids[ds<=b]))) for b in (0,1)]
                    witnesses.append({'mode':m,'row':i,'word':w[i].tolist(),'observation':obs.tolist(),'expected':labels[ids[i]],'wrong':labels[next(iter(ex[k]))],'candidate_ids_exact_radius1':possible})
    out.mkdir(parents=True,exist_ok=False)
    for i,s in enumerate(witnesses):
        for kind in ('word','observation'):
            name=f'witness-{i}-{kind}.wav'; u['audio'](out/name,s[kind])
            with wave.open(str(out/name),'rb') as f:
                assert f.getparams()[:4]==(1,2,16000,12800); pcm=f.readframes(12800)
            s[kind+'_file']=name; s[kind+'_pcm_sha256']=hashlib.sha256(pcm).hexdigest()
    receipt={'schema':'mhac-migration-faults-v1','grammar_pin':PIN,'grammar_blob':BLOB,'measurement_pin':AUDIT,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'seed_literal_checks':44829,'literal_checks':checks,'outcomes':['correct','abstain','wrong'],'results':report,'witnesses':witnesses,'limits':'Exactly one substitution, aligned full frames, closed catalogue, semantic IDs collapse profiles, all alternatives counted equally (not channel probabilities). Same observations for each policy; compute not matched. No human evidence.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'results':report,'literal_checks':checks,'witnesses':len(witnesses)},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
