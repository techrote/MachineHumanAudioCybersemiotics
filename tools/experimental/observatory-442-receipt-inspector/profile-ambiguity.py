"""Refs #442/#443. Measurement lane, synthetic finite codebook audit, not human evidence.
Reconstructs protected-profile.py at pinned source; no runtime upstream dependency.
"""
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
import hashlib, html, json, math, struct, sys, wave

PIN = '7773a123a29881a22d7c1893df1dd609c4ef25d1'
BLOB = 'd1f598e10a79f4ca09f45eb88d26e7422e69ec81'
KINDS = ('ack', 'terminal', 'quote', 'certificate')
P = tuple(range(8))

def digits(n,k):
    return tuple(n//17**i%17 for i in reversed(range(k)))

def legal(row):
    pending=1
    for i,v in enumerate(row):
        if v in (0,1,2,3,14): pending-=1
        elif 4<=v<=10: pass
        elif v in (11,12): pending+=1
        else: return False
        if not pending: return all(x==13 for x in row[i+1:])
    return False

def books():
    free=[k for k in range(4913,13*4913) if not legal(digits(k,4))]
    pos=(0,1,4,5)
    weights=[[math.prod((x-j)*pow(i-j,-1,17) for j in pos if j!=i)%17 for i in pos] for x in P]
    old={}; new={}; h=g=0
    for kind in KINDS:
        acts=list(combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i
                k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                m=(kind,address,*act); d=digits(k,4)
                w=tuple(sum(a*b for a,b in zip(row,d))%17 for row in weights)
                old[m]=w
                for v in w: h=(h*31+v+1)%1000000007; g=(g*37+v+1)%1000000009
                if address<16:
                    a,b,c=digits(len(new),3); new[m]=tuple((a+b*x+c*x*x)%17 for x in P)
    assert (h,g)==(95787044,408117442)
    assert len(old)==len(set(old.values()))==48000 and len(new)==len(set(new.values()))==4000
    return old,new

def project(w,pos): return tuple(w[i] for i in pos)

def audit(old,new,pos):
    # Exact consistency candidates, including legacy lists below its normal decoder minimum.
    maps=[]
    for book in (old,new):
        d=defaultdict(list)
        for m,w in book.items(): d[project(w,pos)].append(m)
        maps.append(d)
    totals={}; witnesses={}
    for name,book in [('legacy',old),('legacy_matched',{m:old[m] for m in new}),('protected',new)]:
        count=Counter()
        for m,w in book.items():
            key=project(w,pos); a=maps[0].get(key,()); b=maps[1].get(key,()); union=set(a)|set(b)
            assert m in union
            count['trials']+=1
            count['both_profiles']+=bool(a and b)
            count['semantic_singleton']+=len(union)==1
            count['semantic_ambiguity']+=len(union)>1
            count['same_kind_address_singleton']+=sum(x[:2]==m[:2] for x in union)==1
            count['candidate_sum']+=len(union)
            count['max_candidates']=max(count['max_candidates'],len(union))
            for label,seq in [('legacy_first',(a if len(a)==1 and len(pos)>=4 else b)),('protected_first',(b if len(b)==1 else a if len(pos)>=4 else ()))]:
                got=seq[0] if len(seq)==1 else None
                count[label+('_abstain' if got is None else '_correct' if got==m else '_wrong')]+=1
            if len(union)>1 and name not in witnesses:
                witnesses[name]={'message':m,'body':w,'surviving':pos,'observation':key,'candidates':sorted(union)}
        assert count['semantic_singleton']+count['semantic_ambiguity']==count['trials']
        totals[name]=dict(count)
    return totals,witnesses

def render(path,body):
    s=[]
    for v in body:
        s.extend([0]*1280 if v is None else [round(2048*min(1,n/80,(959-n)/80)*math.sin(2*math.pi*(400+100*v)*n/16000+.137)) if n<960 else 0 for n in range(1280)])
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,16000,len(s),'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(s),*s))
    return max(map(abs,s))

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    old,new=books(); rows=[]; examples={}
    for n in (8,4,3):
        for pos in combinations(P,n):
            counts,w=audit(old,new,pos); rows.append({'surviving':pos,'counts':counts})
            for k,v in w.items(): examples.setdefault(str(n)+'_'+k,v)
    full=rows[0]['counts']; assert full['protected']['both_profiles']==2604 and full['protected']['semantic_ambiguity']==2603
    assert all(r['counts']==full for r in rows if len(r['surviving'])==4)
    witness=examples['8_protected']; assert old[witness['candidates'][0]]==witness['body'] or old.get(witness['candidates'][1])==witness['body']
    peak=render(out/'shared-body.wav',witness['body'])
    three=examples['3_protected']; masked=[v if i in three['surviving'] else None for i,v in enumerate(three['body'])]
    peak=max(peak,render(out/'three-survivors.wav',masked))
    receipt={'schema':'mhac-profile-ambiguity-v1','source_commit':PIN,'source_blob':BLOB,'rows':rows,'witnesses':examples,'peak_pcm16':peak,'limits':'Clean aligned symbol erasures only, exact consistency lists; no noise or channel probabilities, no authentication or human inference. Legacy-first/protected-first use minimum 4/3 symbols respectively. Perfect kind/address filtering is oracle side information.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    data=json.dumps(rows,separators=(',',':'))
    page='''<!doctype html><meta charset="utf-8"><title>Profile ambiguity inspector</title><h1>Profile ambiguity inspector</h1><p>Exact synthetic codebook projections, not physical channel probabilities. Select a surviving-position mask and source vocabulary.</p><label>Mask <select id="mask"></select></label> <label>Source <select id="source"><option>protected</option><option>legacy_matched</option><option>legacy</option></select></label><pre id="result"></pre><h2>Clean shared-body witness</h2><p>One waveform, different valid meanings.</p><audio controls preload="none" src="shared-body.wav"></audio><h2>Three surviving symbols</h2><audio controls preload="none" src="three-survivors.wav"></audio><p>Start with low playback volume. <a href="receipt.json">Full receipt and semantic witnesses</a></p><script>const rows=DATA;const mask=document.getElementById('mask'),source=document.getElementById('source'),result=document.getElementById('result');rows.forEach((r,i)=>mask.add(new Option(r.surviving.join(','),i)));function show(){result.textContent=JSON.stringify(rows[+mask.value].counts[source.value],null,2)}mask.onchange=source.onchange=show;show()</script>'''
    (out/'index.html').write_text(page.replace('DATA',data),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(full,indent=2)); print('masks',len(rows),'peak',peak)

if __name__=='__main__': run(Path(sys.argv[1]))
