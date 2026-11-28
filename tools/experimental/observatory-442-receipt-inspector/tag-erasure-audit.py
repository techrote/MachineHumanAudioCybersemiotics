"""Refs #442/#443. Synthetic tag substitution + clean body erasure audit.
Original measurement code; grammar reconstructed from pinned profile-check.py.
GPT-6.2, no subagents. No human evidence or authentication claim.
Run: python tag-erasure-audit.py NEW_OUTPUT_DIR (NumPy required).
"""
import collections, hashlib, html, itertools, json, math, pathlib, struct, sys, wave
import numpy as np

PINS = {'main':'495a98ca12bae467a507031f04931aa4254b1866',
        'grammar':'3ecd4769825c7fb41fc8581cd99c02efd0ed8c1f',
        'grammar_blob':'a7b7e93c407a5a4321d41337f2ece01bb1aee494',
        'measurement_parent':'0a298d30d8e5b9b7bf16b3b074fd120fc9048d7d'}

def catalogue():
    def digits(k,n): return tuple(k//17**i%17 for i in reversed(range(n)))
    def syntax(v):
        pending=1
        for i,x in enumerate(v):
            if x in (0,1,2,3,14): pending-=1
            elif x in (11,12): pending+=1
            elif not 4<=x<=10: return False
            if pending==0: return all(y==13 for y in v[i+1:])
        return False
    free=[k for k in range(4913,13*4913) if not syntax(digits(k,4))]
    pos=(0,1,4,5)
    mat=[[math.prod((x-j)*pow(i-j,-1,17) for j in pos if j!=i)%17 for i in pos] for x in range(9)]
    words=[]; profiles=[]; meanings=[]; labels=[]; h=g=small=0
    for kind in ('ack','terminal','quote','certificate'):
        acts=list(itertools.combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i
                k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                w=tuple(sum(a*b for a,b in zip(r,digits(k,4)))%17 for r in mat)
                label=(kind,address,*act); m=len(labels); labels.append(label)
                words.append(w); profiles.append(0); meanings.append(m)
                for v in w[:8]: h=(h*31+v+1)%1000000007; g=(g*37+v+1)%1000000009
                if address<16:
                    a,b,c=digits(small,3); small+=1
                    words.append(tuple((a+b*x+c*x*x)%17 for x in range(9))); profiles.append(1); meanings.append(m)
    assert (h,g,small)==(95787044,408117442,4000)
    return np.array(words),np.array(profiles),np.array(meanings),labels

def tags(w,p,mode):
    return p*8 if mode=='marker' else np.where(p==0,w[:,8]%8,8+w[:,8]%9)

def consensus(keys,m,size):
    lo=np.full(size,len(m),dtype=np.int32); hi=np.full(size,-1,dtype=np.int32)
    np.minimum.at(lo,keys,m); np.maximum.at(hi,keys,m)
    return np.where(lo==hi,hi,-1)

def audit():
    w,p,m,labels=catalogue(); totals=collections.defaultdict(collections.Counter); rows=[]; witnesses={}; checks=0
    for n in (2,3,4,8):
        for mask in itertools.combinations(range(8),n):
            _,inv=np.unique(w[:,mask] @ (17**np.arange(n)),return_inverse=True)
            size=int(inv.max())+1; missing=consensus(inv,m,size)[inv]
            for mode in ('marker','partition'):
                t=tags(w,p,mode); lookup=consensus(inv*17+t,m,size*17).reshape(size,17)
                clean=lookup[inv,t]; count=collections.Counter()
                for q in (0,1):
                    select=p==q
                    count[f'{q}:clean_correct']=int((select&(clean==m)).sum())
                    count[f'{q}:erased_correct']=int((select&(missing==m)).sum())
                    assert not np.any(select & (clean>=0) & (clean!=m))
                for v in range(17):
                    got=lookup[inv,v]; changed=t!=v
                    for q in (0,1):
                        sel=(p==q)&changed; scope='cross' if (v>=8)!=bool(q) else 'within'
                        for status,cond in [('correct',got==m),('wrong',(got>=0)&(got!=m)),('reject',got<0)]:
                            count[f'{q}:{scope}:{status}']+=int((sel&cond).sum())
                        hit=np.flatnonzero(sel&(got>=0)&(got!=m)); key=f'{n}:{mode}:{q}:{scope}'
                        if len(hit) and key not in witnesses:
                            i=int(hit[0]); body=[int(w[i,j]) if j in mask else None for j in range(8)]
                            witnesses[key]={'mask':mask,'sent':labels[m[i]],'decoded':labels[got[i]],'complete':w[i,:8].tolist()+[int(t[i])],'observed':body+[v]}
                for q in (0,1):
                    assert sum(count[f'{q}:{s}:{r}'] for s in ('cross','within') for r in ('correct','wrong','reject'))==16*int((p==q).sum())
                if mask in ((0,1),(0,1,2),(0,1,2,3),tuple(range(8))):
                    literal=collections.defaultdict(set)
                    for word,tag,meaning in zip(w,t,m): literal[tuple(word[list(mask)])+(tag,)].add(meaning)
                    for i in range(0,len(m),997):
                        for v in range(17):
                            candidates=literal.get(tuple(w[i,list(mask)])+(v,),set())
                            assert lookup[inv[i],v]==(next(iter(candidates)) if len(candidates)==1 else -1); checks+=1
                totals[f'{n}:{mode}'].update(count); rows.append({'mask':mask,'mode':mode,'counts':dict(count)})
    assert len(rows)==310
    for mode in ('marker','partition'):
        assert sum(totals[f'8:{mode}'][f'{q}:cross:wrong'] for q in (0,1))==5206
        assert totals[f'8:{mode}']['0:clean_correct']==48000 and totals[f'8:{mode}']['1:clean_correct']==4000
    assert totals['3:partition']['0:clean_correct']==757183 and totals['2:partition']['1:clean_correct']==22918
    return dict(totals),rows,witnesses,checks

def audio(path,symbols):
    samples=[]
    for v in symbols:
        x=[0]*1280
        if v is not None:
            for n in range(960): x[n]=round(2048*min(1,n/80,(959-n)/80)*math.sin(2*math.pi*(400+100*v)*n/16000+.137))
        y=x[160:800]
        scores=[sum(a*math.cos(2*math.pi*f*n/16000) for n,a in enumerate(y))**2+sum(a*math.sin(2*math.pi*f*n/16000) for n,a in enumerate(y))**2 for f in range(400,2001,100)]
        assert (max(range(17),key=scores.__getitem__) if any(y) else None)==v
        samples+=x
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,16000,len(samples),'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(samples),*samples))
    return max(map(abs,samples))

def run(out):
    totals,rows,witnesses,checks=audit(); out.mkdir(parents=True,exist_ok=False); specimens=[]
    for key in ('3:partition:0:cross','3:partition:0:within'):
        if key not in witnesses: continue
        item=witnesses[key]
        for name,symbols in [('complete',item['complete']),('damaged',item['observed']),('tag-erased',item['observed'][:8]+[None])]:
            fn=key.replace(':','-')+'-'+name+'.wav'; peak=audio(out/fn,symbols)
            specimens.append({'file':fn,'symbols':symbols,'peak':peak,'witness':key,'condition':name})
    receipt={'schema':'mhac-tag-erasure-audit-v1','pins':PINS,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'totals':totals,'masks':rows,'witnesses':witnesses,'literal_checks':checks,'specimens':specimens,'limits':'Uniform exhaustive symbolic faults; one tag substitution, known aligned clean surviving body tones; no body errors, no physical or human evidence. 720 ms, common amplitude, not exact waveform energy matched.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    opts=''.join(f'<option>{k}</option>' for k in totals)
    gallery=''.join('<h3>'+html.escape(s['file'])+'</h3><audio controls preload="none" src="'+s['file']+'"></audio>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Tag erasure audit</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:1em}td,th{padding:.5em;text-align:right}td:first-child{text-align:left}</style><h1>Tag erasure audit</h1><p>Synthetic exact counts, not physical error rates. Select surviving-body count and tag scheme. Original WAVs: start at low volume; no autoplay.</p><select id="condition">'+opts+'</select><table id="counts"></table>'+gallery+'<p><a href="receipt.json">Full masks, witnesses and source pins</a></p><script>const data='+json.dumps(totals)+';const c=document.getElementById("condition"),t=document.getElementById("counts");function show(){t.replaceChildren();for(const [k,v] of Object.entries(data[c.value])){let r=t.insertRow();r.insertCell().textContent=k;r.insertCell().textContent=v.toLocaleString()}}c.onchange=show;show()</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'totals':totals,'literal_checks':checks,'specimens':specimens},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
