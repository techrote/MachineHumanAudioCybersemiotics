"""Adversarial #448, Run 036. Synthetic only. CLI: python cue-binding-audit.py ROOT OUT.
ROOT holds Run 035 portable sources and async1/receipt.json. No tuning or human claims.
"""
import hashlib, html, json, pathlib, runpy, sys, wave
import numpy as np
PARENT='9486d2db02cc8bd0cea3f1e4d440ff38e7304683'
MEASUREMENT='a1f5c1fa4adced1281926730a2d90ce41313d273'
PRIOR='aa5a818b5762e6f5f78cfa9823565bddf3c7ddfb593dfcea97b4fc49660b63e8'
SEED=448036
FAULTS=('clean','swap','missing','shift+20','shift-20','both-swapped')
POLICIES=('cue-union','cue-guard','wide-union','corroborated','blind-fallback')
def sha(b): return hashlib.sha256(b).hexdigest()
def main(root,out):
    raw=(root/'async1/receipt.json').read_bytes(); assert sha(raw)==PRIOR
    prior=json.loads(raw); src=root/'asynchronous-attribution.py'
    assert sha(src.read_bytes())==prior['source_sha256']
    u=runpy.run_path(str(src)); assert u['PARENT']==prior['parent']
    for n,h in u['BLOBS'].items(): assert u['blob']((root/n).read_bytes())==h,n
    _,_,_,book,names,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    excluded=set(prior['excluded'])|{r['target'] for r in prior['rows']}; assert len(excluded)==144
    rng=np.random.default_rng(SEED); origins=rng.choice(np.setdiff1d(np.arange(len(book)),list(excluded)),24,False)
    used=excluded|set(map(int,origins)); cap=u['CAP']; grids=u['GRIDS']; fs=u['FS']
    packed=[[int.from_bytes(np.packbits(book[:,s]==v,bitorder='little').tobytes(),'little') for v in range(17)] for s in range(10)]
    def candidates(a):
        m=(1<<len(book))-1
        for s in range(10):
            p=0
            for v in np.flatnonzero(a[s]): p|=packed[s][v]
            m&=p
        return m
    def union(ms):
        m=0
        for x in ms: m|=x
        return m
    env=np.minimum(1,np.minimum(np.arange(960)/80,(959-np.arange(960))/80)); t=np.arange(960)/fs
    def render(word,ph,g):
        z=np.zeros((10,1280)); z[:,:960]=env*np.sin(2*np.pi*(400+100*word[:,None])*t+ph[:,None])
        x=np.interp(cap,u['arrival'](g),z.ravel(),left=0,right=0); return x/np.linalg.norm(x)
    def cue(g): return tuple(round(v/10)*10 for v in g)
    def admit(c,tol): return [] if c is None else [k for k,g in enumerate(grids) if max(abs(a-b) for a,b in zip(c,g))<=tol]
    out.mkdir(parents=True,exist_ok=False); rows=[]; specimens=[]; summary={}; pairs=[]; checks=0
    for i in map(int,origins):
        j=int(rng.choice(np.setdiff1d(np.flatnonzero(np.count_nonzero(book!=book[i],axis=1)==7),list(used)))); used.add(j); pairs.append([i,j])
        ph=rng.uniform(0,2*np.pi,(2,10)); noise=rng.normal(size=len(cap)); noise/=np.linalg.norm(noise)
        for label,ga,gb,gain,snr in u['CASES']:
            x=render(book[i],ph[0],ga)+gain*render(book[j],ph[1],gb)
            if snr is not None: x+=noise*np.linalg.norm(x)*10**(-snr/20)
            pcm=np.rint(x*(2048/max(abs(x)))).astype('<i2'); digest=sha(pcm.tobytes())
            f=[u['feature'](pcm,g) for g in grids]; masks=[candidates(v[0]) for v in f]; guard=[v[2] for v in f]
            if i==int(origins[0]):
                for v,m in zip(f,masks):
                    assert m==sum(1<<int(k) for k in np.flatnonzero(v[0][np.arange(10),book].all(axis=1))); checks+=1
            def gu(ks): return union(masks[k] for k in ks if guard[k]<=min(guard[n] for n in ks)+.08) if ks else 0
            blind=gu(range(len(grids)))
            for fault in FAULTS:
                role_rows=[]; role_masks=[]
                for role,target,rival,g,h in [('A',i,j,ga,gb),('B',j,i,gb,ga)]:
                    truth=cue(g); other=cue(h); primary={'clean':truth,'swap':other,'missing':None,'shift+20':tuple(v+20 for v in truth),'shift-20':tuple(v-20 for v in truth),'both-swapped':other}[fault]
                    secondary=other if fault=='both-swapped' else truth
                    ks=admit(primary,20); m=gu(ks)
                    ps=[union(masks[k] for k in ks),m,union(masks[k] for k in admit(primary,30)),m if primary==secondary else 0,m if primary is not None else blind]
                    role_masks.append(ps); ds={}
                    for name,p in zip(POLICIES,ps):
                        n=p.bit_count(); unique=p.bit_length()-1 if n==1 else None; status=('correct' if unique==target else 'wrong') if n==1 else ('ambiguous' if n else 'empty')
                        ds[name]=dict(outcome=status,count=n,unique=unique,target_retained=bool(p&(1<<target)),rival_retained=bool(p&(1<<rival)))
                        d=summary.setdefault(fault,{}).setdefault(name,dict(correct=0,wrong=0,ambiguous=0,empty=0,rival_wrong=0)); d[status]+=1; d['rival_wrong']+=unique==rival
                    role_rows.append(dict(condition=label,fault=fault,role=role,target=target,rival=rival,pcm_sha256=digest,primary=primary,secondary=secondary,truth=truth,admitted=ks,decisions=ds))
                for r in role_rows: r['paired_overlap']={n:(a&b).bit_count() for n,a,b in zip(POLICIES,*role_masks)}
                rows.extend(role_rows)
            if i==int(origins[0]):
                fn=label+'.wav'
                with wave.open(str(out/fn),'wb') as w: w.setparams((1,2,fs,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                with wave.open(str(out/fn),'rb') as w: assert sha(w.readframes(len(cap)))==digest
                specimens.append(dict(file=fn,pcm_sha256=digest,A=i,B=j,peak=int(max(abs(pcm)))))
    assert len(rows)==1728 and len(used-excluded)==48 and checks==78
    # A swapped primary is literally the other role's clean input; common-mode
    # corruption also defeats equality of the two supplied cues.
    for k in range(0,len(rows),12):
        block=rows[k:k+12]; assert len({r['pcm_sha256'] for r in block})==1
        for s in (0,1):
            for p in ('cue-union','cue-guard','wide-union','blind-fallback'):
                assert block[s+2]['decisions'][p]['unique']==block[1-s]['decisions'][p]['unique']
            assert block[s+10]['decisions']['corroborated']['unique']==block[1-s]['decisions']['corroborated']['unique']
    receipt=dict(schema='mhac-cue-binding-v1',parent=PARENT,measurement=MEASUREMENT,prior_sha256=PRIOR,source_sha256=sha(pathlib.Path(__file__).read_bytes()),runtime=[sys.version.split()[0],np.__version__],seed=SEED,pairs=pairs,excluded=sorted(excluded),faults=FAULTS,policies=POLICIES,summary=summary,rows=rows,specimens=specimens,dense_checks=checks,limits='Fixed 24 fresh pairs, six upstream conditions, paired roles, matched PCM across faults. Shift faults are constant endpoint errors, not a delay simulation. Secondary cue is privileged clean except common-mode swap; no acquisition/authentication or equal side-information budget. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join(f'<p>{html.escape(s["file"])} <audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Cue binding audit</title><h1>Same PCM, corrupted external identity cues</h1><p>Opt-in synthetic specimens; start low. No calibrated SPL.</p>'+gallery+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><a href="receipt.json">Full paired receipt</a>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
