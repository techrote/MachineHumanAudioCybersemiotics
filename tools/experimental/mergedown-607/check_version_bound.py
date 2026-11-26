"""Refs #607: independent distance/decoder audit, synthetic aligned symbols only.
Usage: python check_version_bound.py SOURCE_DIR BRIDGE_RECEIPT BOUND_RECEIPT
Catalogue construction reused; census, extension and decoder independently implemented.
"""
import hashlib, json, math, pathlib, runpy, sys
import numpy as np
PIN='9e45f77a11c637c03f7e1ac50b6b6802ffc97cfc'
BLOBS={'version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
def require(ok, label):
    if not ok: raise ValueError(label)
def audit(root, bridge_receipt, bound_receipt):
    for name, expected in BLOBS.items():
        b=(root/name).read_bytes(); require(hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==expected,name)
    vb=runpy.run_path(str(root/'version-bridge.py')); vp=runpy.run_path(str(root/'version-bound-payload.py'))
    _, menus, local, global_, nl, ng=vb['build'](root)
    require([nl,ng]==[bridge_receipt['local_spares'],bridge_receipt['all_menu_spares']], 'spares')
    require(global_.tolist()==[r['symbols'] for r in bridge_receipt['identities']], 'bridge identities')
    pairs=0; bins=0; minima={}
    for label, codes in [('baseline',local),('bridge',global_)]:
        minima[label]={}
        for name, menu in menus.items():
            # Coordinate-wise equality accumulation in bounded batches, no original census call.
            n=menu.shape[1]; hist=np.zeros(n+1,dtype=np.int64)
            for chunk in np.array_split(codes,10):
                matches=np.zeros((len(chunk),len(menu)),dtype=np.uint8)
                for k in range(n): matches+=chunk[:,k,None]==menu[None,:,k]
                hist+=np.bincount((n-matches).ravel(),minlength=n+1)
            rec=bridge_receipt[label][name]; minimum=int(np.flatnonzero(hist)[0]); minima[label][name]=minimum
            require(hist.tolist()==rec['distance_counts'] and int(hist.sum())==rec['pairs'] and minimum==rec['minimum'], f'{label}/{name}')
            i,j,a,b=rec['witness']; require(codes[i].tolist()==a and menu[j].tolist()==b and sum(x!=y for x,y in zip(a,b))==minimum,'witness')
            pairs+=int(hist.sum()); bins+=len(hist)
    _, raw, names=vp['build'](root)
    lookup={tuple(w):i for i,w in enumerate(raw[1])}; aliases=[(i,lookup[tuple(w)]) for i,w in enumerate(raw[0]) if tuple(w) in lookup]; wrong=[(i,j) for i,j in aliases if names[i]!=names[j]]
    require([len(aliases),len(wrong)]==[bound_receipt['aliases'],bound_receipt['incompatible_aliases']], 'alias count')
    # Independent Lagrange interpolation using first four sample values, at x=10..14.
    weights=np.array([[math.prod(x-j for j in range(4) if j!=i)*pow(math.prod(i-j for j in range(4) if j!=i)%17,-1,17)%17 for x in range(10,15)] for i in range(4)])
    rng=np.random.default_rng(bound_receipt['seed']); cases=[]
    for e,s in ((0,0),(2,0),(1,2),(0,4),(3,0),(4,0),(5,0),(2,6),(0,11)):
        for v in (0,1):
            for row in rng.choice(len(raw[v]),24,False): cases.append((e,s,v,int(row),rng.permutation(15),rng.integers(1,17,size=e)))
    decisions=0; allstats={}; boundaries={}
    for mode in ('marker','polynomial'):
        books=[np.column_stack((w, np.full((len(w),5),v) if mode=='marker' else (w[:,:4]@weights+v)%17)) for v,w in enumerate(raw)]
        for v,w in enumerate(books): require(np.array_equal(w,vp['extend'](raw[v],v,mode)), 'extension mismatch')
        def decode(obs,e,version=None):
            hits=[]; keep=[i for i,x in enumerate(obs) if x is not None]
            for v,w in enumerate(books):
                if version is not None and v!=version: continue
                matches=np.zeros(len(w),dtype=np.uint8)
                for k in keep: matches+=w[:,k]==obs[k]
                hits.extend((v,int(i)) for i in np.flatnonzero(matches>=max(0,len(keep)-e)))
                if len(hits)>1: return None
            return hits[0] if hits else None
        stats={}
        for e,s,v,row,p,delta in cases:
            obs=books[v][row].tolist()
            for k in p[:s]: obs[k]=None
            for k,d in zip(p[s:s+e],delta): obs[k]=(obs[k]+int(d))%17
            for known in (False,True):
                got=decode(obs,e,v if known else None); expected=vp['decode'](books,obs,e,v if known else None)
                require(got==expected,'decision mismatch'); decisions+=1
                counts=stats.setdefault(f'e{e}s{s}:{"known" if known else "union"}',[0,0,0]); counts[0 if got==(v,row) else 1 if got is None else 2]+=1
        require(stats==bound_receipt['results'][mode]['stats'],'receipt stats')
        i,j=wrong[0]; a=books[0][i].tolist(); b=books[1][j].tolist()
        require(decode(a[:10]+[None]*5,0) is None,'tail erasure')
        require(decode(a[:10]+b[10:13]+a[13:],2)==(1,j),'wrong version boundary')
        # A trusted but incorrect version cue can turn complete tail erasure into a wrong unique meaning.
        require(decode(a[:10]+[None]*5,0,1)==(1,j),'wrong version cue')
        boundaries[mode]={'old_row':i,'new_row':j,'wrong_version_cue_with_tail_erasure':True}; allstats[mode]=stats
    return {'pin':PIN,'source_blobs':BLOBS,'bridge_pairs':pairs,'histogram_bins':bins,'minima':minima,'aliases':len(aliases),'incompatible_aliases':len(wrong),'version_decisions':decisions,'stats':allstats,'boundaries':boundaries,'limitations':'Catalogue builders reused; aligned symbolic simulation; no human or streaming evidence.'}
if __name__=='__main__':
    print(json.dumps(audit(pathlib.Path(sys.argv[1]),json.loads(pathlib.Path(sys.argv[2]).read_text()),json.loads(pathlib.Path(sys.argv[3]).read_text())),indent=2))
