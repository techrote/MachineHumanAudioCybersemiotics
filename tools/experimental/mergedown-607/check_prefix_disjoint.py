"""Refs #607/#452. Independent aligned-symbol audit, not acoustic or human qualification.
Usage: python check_prefix_disjoint.py PINNED_SOURCE_DIR GENERATED_PREFIX_DIR
"""
import collections, hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np

PIN = '9e45f77a11c637c03f7e1ac50b6b6802ffc97cfc'
BLOBS = {
    'control-namespace.py': '8e27fe89f2734a0b5fd666bb2018b0d379736493',
    'distributed-profile.py': 'a780404e8c76820976ad6fb407429ec895a6313f',
    'migration-namespace.py': 'b3562781a974c47b41cbe066ceb755288a51b6b1',
    'version-bridge.py': '6400cf4c1b42fbe958b0265da43ef657bb355401',
    'version-bound-payload.py': '7ef6881cefa9c34355d024aeea671d021b674a55',
    'frame-length-commit.py': '1538e258e53b62fc62315ca11eb9ba34496c5919',
    'prefix-disjoint.py': 'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942',
}

def sha(b): return hashlib.sha256(b).hexdigest()

def require(ok, label):
    if not ok: raise ValueError(label)

def interpolate(w):
    # Lagrange basis over GF(17), independently of upstream finite differences.
    basis = []
    for j in range(4):
        row = []
        for x in range(15):
            a = 1
            for k in range(4):
                if k != j: a = a * (x-k) * pow(j-k,-1,17) % 17
            row.append(a)
        basis.append(row)
    return w[:, :4] @ np.array(basis) % 17

def run(root, out):
    for name, pin in BLOBS.items():
        b = (root/name).read_bytes()
        require(hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest() == pin, name)
    manifest = json.loads((out/'manifest.json').read_text())
    require(set(manifest) == {p.name for p in out.iterdir()}-{'manifest.json'}, 'manifest coverage')
    for name, digest in manifest.items(): require(sha((out/name).read_bytes()) == digest, name)
    r = json.loads((out/'receipt.json').read_text())
    require(r['source_sha256'] == sha((root/'prefix-disjoint.py').read_bytes()), 'source digest')
    # Catalogue constructor is reused; encoding, enumeration and decoding below are separate.
    _, raw, _ = runpy.run_path(str(root/'version-bound-payload.py'))['build'](root)
    old, new = raw
    polys = [interpolate(w) for w in raw]
    for w,p in zip(raw,polys): require(np.array_equal(w,p[:,:10]), 'cubic body')
    polys[1][:,10:] = (polys[1][:,10:]+1)%17
    long = np.concatenate(polys)
    short = np.column_stack((np.zeros((len(old),3),int),old))
    delta = np.array([pow(x,4,17) for x in range(15)])
    books = {m:{13:short,18:np.column_stack((np.full((len(long),3),16), (long+d)%17))} for m,d in [('independent',0),('quartic',delta)]}
    # Exhaustively enumerate all cubic differences, not all 6.25B catalogue pairs.
    x = np.arange(10); a = np.array(list(itertools.product(range(17),repeat=4)))
    diffs = a @ (x[None,:]**np.arange(4)[:,None]) % 17
    distance_hist = np.bincount(np.count_nonzero((diffs+delta[:10])%17,axis=1),minlength=11)
    require(int(np.flatnonzero(distance_hist)[0])==6, 'cross-body bound')
    lookup = {m:{n:{tuple(w):i for i,w in enumerate(b[:,3:])} for n,b in bs.items()} for m,bs in books.items()}
    for m,bs in books.items():
        require(all(len(lookup[m][n])==len(b) for n,b in bs.items()),'unique bodies')
    expected = {(m,n,i,''.join(p),cut) for m in books for n,i in r['origins'] for p in itertools.product('CFE',repeat=3) for cut in range(3,n+1)}
    stats = collections.Counter(); seen = set()
    for line in (out/'traces.jsonl').read_text().splitlines():
        m,n,i,p,cut,got,result = json.loads(line); key = (m,n,i,p,cut)
        require(key in expected and key not in seen,'trace key'); seen.add(key)
        score = p.count('C')-p.count('F')
        declared = n if score>0 else 31-n if score<0 else None
        w = books[m][n][i]
        actual = lookup[m][cut].get(tuple(w[3:cut])) if declared==cut and cut in (13,18) else None
        outcome = 'abstain' if actual is None else 'correct' if (cut,actual)==(n,i) else 'wrong'
        require((got,result)==(actual,outcome),'trace decision')
        stats[f'{m}:{"full" if cut==n else "cut"}:{outcome}'] += 1
    require(seen==expected and dict(stats)==r['stats'] and len(seen)==r['observations'],'trace totals')
    collision = {}; paths = {}
    for w in r['witnesses']:
        m=w['mode']; bs=books[m]
        collision[m]=len(set(lookup[m][13]) & {tuple(x[3:13]) for x in bs[18]})
        require(collision[m]==w['prefix_collisions'],'collision census')
        src=bs[18][len(old)+w['long_row'],:13]; dst=bs[13][w['short_row']]
        require(src.tolist()==w['source_prefix'] and dst.tolist()==w['target'],'witness words')
        distance=np.count_nonzero(bs[13]!=src,axis=1)
        require(int(distance.min())==w['distance'],'minimum witness')
        positions=np.flatnonzero(src!=dst); path=[]
        for e in range(len(positions)+1):
            obs=src.copy(); obs[positions[:e]]=dst[positions[:e]]
            hits=np.flatnonzero(np.count_nonzero(bs[13]!=obs,axis=1)<=2)
            path.append(int(hits[0]) if len(hits)==1 else None)
        require(path==w['radius2_path'],'radius path'); paths[m]=path
    peaks=[]
    for specimen in r['specimens']:
        with wave.open(str(out/specimen['file']),'rb') as f:
            require(f.getparams()[:4]==(1,2,16000,1280*len(specimen['symbols'])),'wav format')
            pcm=f.readframes(f.getnframes())
        require(sha(pcm)==specimen['pcm_sha256'],'pcm hash')
        peaks.append(int(np.abs(np.frombuffer(pcm,dtype='<i2').astype(int)).max()))
    require(max(peaks)<=2048,'peak bound')
    return {'pin':PIN,'verified_blobs':len(BLOBS),'manifest_entries':len(manifest),'trace_rows':len(seen),'counts':dict(stats),'collision_counts':collision,'cubic_differences':len(a),'cross_body_distance_histogram':distance_hist.tolist(),'radius_paths':paths,'pcm_hashes':len(peaks),'peak_pcm16':max(peaks),'receipt_sha256':sha((out/'receipt.json').read_bytes())}

if __name__=='__main__':
    print(json.dumps(run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2])),indent=2,sort_keys=True))
