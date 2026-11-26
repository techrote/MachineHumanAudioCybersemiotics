"""Refs #452/#453, Grammars lane. Synthetic aligned nine-slot profiles.
Original implementation; catalogue reconstructed from pinned protected-profile.py.
No human evidence, authentication, or canonical protocol change. GPT-6.2, no subagents.
"""
import collections, itertools, hashlib, json, math, pathlib, struct, sys, wave
import numpy as np
PINS = {'grammar':'7773a123a29881a22d7c1893df1dd609c4ef25d1',
        'measurement':'0a298d30d8e5b9b7bf16b3b074fd120fc9048d7d',
        'main':'495a98ca12bae467a507031f04931aa4254b1866'}

def digits(k,n): return tuple(k//17**i%17 for i in reversed(range(n)))
def semantic(row):
    pending=1
    for i,v in enumerate(row):
        if v in (0,1,2,3,14): pending-=1
        elif 4<=v<=10: pass
        elif v in (11,12): pending+=1
        else: return False
        if pending==0: return all(x==13 for x in row[i+1:])
    return False

def books():
    free=[k for k in range(4913,13*4913) if not semantic(digits(k,4))]
    pos=(0,1,4,5)
    mat=[[math.prod((x-j)*pow(i-j,-1,17) for j in pos if j!=i)%17 for i in pos] for x in range(9)]
    rows=[]; h=g=0; small=0
    for kind in ('ack','terminal','quote','certificate'):
        acts=list(itertools.combinations(range(20),2)) if kind=='certificate' else [(a,) for a in range(20)]
        for address in range(192):
            for i,act in enumerate(acts):
                j=address*len(acts)+i
                k=j if kind=='ack' else 14*4913+j if kind=='terminal' else free[36480+j] if kind=='quote' else free[j]
                msg=(kind,address,*act); w=tuple(sum(a*b for a,b in zip(r,digits(k,4)))%17 for r in mat)
                rows.append((0,msg,w))
                for v in w[:8]: h=(h*31+v+1)%1000000007; g=(g*37+v+1)%1000000009
                if address<16:
                    a,b,c=digits(small,3); small+=1
                    rows.append((1,msg,tuple((a+b*x+c*x*x)%17 for x in range(9))))
    assert (h,g,small)==(95787044,408117442,4000)
    return rows

def tag(p,w,mode):
    # Disjoint tone groups. Partition mode also conveys a reduced polynomial check.
    return (0 if p==0 else 8) if mode=='marker' else (w[8]%8 if p==0 else 8+w[8]%9)

def encode(row,mode):
    p,m,w=row; return w[:8]+(tag(p,w,mode),)

def index(rows,mask,mode,has_tag):
    d={}
    for p,m,w in rows:
        key=tuple(w[i] for i in mask)+((tag(p,w,mode),) if has_tag else ())
        # Semantic consensus: same meaning in different profiles is not ambiguity.
        if key not in d: d[key]=m
        elif d[key]!=m: d[key]=None
    return d

def decode(rows,body,mode):
    if len(body)!=9 or any(v is not None and (type(v)!=int or not 0<=v<17) for v in body): return None
    mask=tuple(i for i in range(8) if body[i] is not None)
    return index(rows,mask,mode,body[8] is not None).get(tuple(v for v in body if v is not None))

def audit(rows):
    results={}; masks=[]
    words=np.array([w for p,m,w in rows],dtype=np.int64)
    profiles=np.array([p for p,m,w in rows],dtype=np.int64)
    ids={m:i for i,m in enumerate(dict.fromkeys(m for p,m,w in rows))}
    meanings=np.array([ids[m] for p,m,w in rows],dtype=np.int64)
    marker=profiles*8
    partition=np.array([tag(p,w,'partition') for p,m,w in rows])
    for n in (2,3,4,8):
        totals=collections.Counter()
        for mask in itertools.combinations(range(8),n):
            counts=collections.Counter(); base=words[:,mask] @ (17**np.arange(n))
            for label,keys in (('missing',base),('marker',base*17+marker),('partition',base*17+partition)):
                order=np.argsort(keys); k=keys[order]; m=meanings[order]
                starts=np.r_[0,np.flatnonzero(k[1:]!=k[:-1])+1]
                lengths=np.diff(np.r_[starts,len(k)])
                good=np.repeat(np.minimum.reduceat(m,starts)==np.maximum.reduceat(m,starts),lengths)
                for p in (0,1):
                    select=profiles[order]==p
                    counts[f'{label}:{p}:total']=int(select.sum())
                    counts[f'{label}:{p}:correct']=int((select & good).sum())
                if mask==(0,1,2):
                    mode='partition' if label=='partition' else 'marker'; has=label!='missing'
                    d=index(rows,mask,mode,has)
                    for p in (0,1):
                        literal=sum(d[tuple(w[i] for i in mask)+((tag(p,w,mode),) if has else ())]==m for q,m,w in rows if q==p)
                        assert literal==counts[f'{label}:{p}:correct']
            totals.update(counts); masks.append({'positions':mask,'counts':dict(counts)})
        results[n]=dict(totals)
    return results,masks

def tag_faults(rows):
    counts=collections.Counter(); witnesses={}
    for mode in ('marker','partition'):
        d=index(rows,tuple(range(8)),mode,True)
        for row in rows:
            p,m,w=row; body=encode(row,mode)
            for v in range(17):
                if v==body[8]: continue
                got=d.get(body[:8]+(v,)); status='reject' if got is None else 'correct' if got==m else 'wrong'
                counts[f'{mode}:{p}:{status}']+=1
                if status=='wrong' and mode not in witnesses:
                    witnesses[mode]={'sent':m,'body':body,'damaged':body[:8]+(v,),'got':got}
    return dict(counts),witnesses

def audio(out,name,body):
    samples=[]; observed=[]
    for v in body:
        x=[0]*1280
        if v is not None:
            for n in range(960): x[n]=round(2048*min(1,n/80,(959-n)/80)*math.sin(2*math.pi*(400+100*v)*n/16000+.137))
        y=x[160:800]
        scores=[sum(a*math.cos(2*math.pi*f*n/16000) for n,a in enumerate(y))**2+sum(a*math.sin(2*math.pi*f*n/16000) for n,a in enumerate(y))**2 for f in range(400,2001,100)]
        observed.append(max(range(17),key=scores.__getitem__) if any(y) else None); samples+=x
    assert observed==list(body)
    with wave.open(str(out/name),'wb') as f:
        f.setparams((1,2,16000,len(samples),'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(samples),*samples))
    return observed,max(map(abs,samples))

def run(out):
    out.mkdir(parents=True,exist_ok=False); rows=books(); results,masks=audit(rows); faults,witnesses=tag_faults(rows)
    assert len(rows)==52000 and len(masks)==155
    for p in (0,1):
        assert results[8][f'partition:{p}:correct']==results[8][f'marker:{p}:correct']==(48000 if p==0 else 4000)
    assert results[3]['partition:0:correct']>results[3]['marker:0:correct']
    assert results[2]['partition:1:correct']>results[2]['marker:1:correct']
    specimens=[]
    for mode,w in witnesses.items():
        for name,body,expected in [('clean',w['body'],w['sent']),('tag-error',w['damaged'],w['got'])]:
            fn=f'{mode}-{name}.wav'; observed,peak=audio(out,fn,body)
            assert decode(rows,observed,mode)==expected
            specimens.append({'file':fn,'symbols':observed,'decoded':expected,'peak':peak})
    receipt={'schema':'mhac-profile-check-v1','pins':PINS,'rows':len(rows),'duration_ms':720,'counts':results,'masks':masks,'tag_faults':faults,'witnesses':witnesses,'specimens':specimens,'limits':'Known alignment/erasures; exact clean-mask counts and single tag substitution with intact body; no body substitutions, physical channel, authentication, or human evidence. Profile-tag alternatives share 17-tone alphabet, slot duration and amplitude; energy not exactly matched.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Profile check</title><h1>Profile check</h1><p>Original synthetic audio. Start at low volume. No autoplay.</p>'+''.join('<h2>'+s['file']+'</h2><p>'+str(s['decoded'])+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in specimens)+'<p><a href="receipt.json">Exact results and masks</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':results,'tag_faults':faults,'witnesses':witnesses,'specimens':specimens},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
