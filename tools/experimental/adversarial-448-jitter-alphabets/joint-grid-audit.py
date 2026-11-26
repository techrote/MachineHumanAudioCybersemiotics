"""Refs #448/#449. Synthetic joint timing/spectral replay, not a new held-out corpus.
Usage: python joint-grid-audit.py PINNED_DIR FROZEN_HELDOUT_DIR NEW_OUTPUT_DIR
"""
import hashlib, json, pathlib, runpy, sys, contextlib, io, html
import numpy as np

PARENT='3e234a74cc4e5fc00307a73a270cd731249ff254'
MEASUREMENT='8f8ebb033f5ba76e9406f7227b982c7aeab28c1f'
SOURCE_BLOB='4fd5b8e65670ff2d06aab7ad602141f43c6f4c8c'
GRIDS=(0,160,320,480)  # samples at 16 kHz; no samples beyond the frame
RANKS=(3,17)
THRESHOLD=.25

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def decision(mask,i):
    ids=np.flatnonzero(mask)
    return dict(outcome=('correct' if mask[i] else 'wrong') if len(ids)==1 else ('ambiguous' if len(ids) else 'empty'),retained=bool(mask[i]),count=len(ids),unique=int(ids[0]) if len(ids)==1 else None)

def main(root,frozen,out):
    source=root/'heldout-retention.py'; assert blob(source.read_bytes())==SOURCE_BLOB
    for n,h in json.loads((frozen/'manifest.json').read_text()).items(): assert sha((frozen/n).read_bytes())==h,n
    old=json.loads((frozen/'receipt.json').read_text()); reference=old['rows']; assert len(reference)==384
    g=runpy.run_path(str(source)); maincode=g['main'].__code__
    needle='if i==origins[0] and label in'; lines=source.read_text().splitlines()
    targets=[j+1 for j,l in enumerate(lines) if needle in l]; assert len(targets)==1
    out.mkdir(parents=True,exist_ok=False); rows=[]; summary={}; operations=0
    def inspect(v):
        nonlocal operations
        pcm,book,i=v['pcm'],v['book'],int(v['i']); base=v['row']; ref=reference[len(rows)]
        assert (base['condition'],base['origin'],base['pcm_sha256'],base['decisions'])==(ref['condition'],ref['origin'],ref['pcm_sha256'],ref['decisions'])
        x=pcm.ravel(); mags=[]; scores=[]
        for off in GRIDS:
            windows=x[np.arange(10)[:,None]*1280+np.arange(160+off,800+off)[None,:]]
            mag=np.abs(np.fft.rfft(windows,axis=1))[:,np.arange(16,81,4)]; mags.append(mag)
            power=mag**2; scores.append(float(np.mean(power.max(axis=1)/np.maximum(power.sum(axis=1),1e-30))))
        best=int(np.argmax(scores)); oracle=GRIDS.index(v['delay']); results={}; per_grid={}
        for k in RANKS:
            masks=[]
            for mag in mags:
                order=np.argsort(-mag,axis=1,kind='stable'); rel=mag/np.maximum(mag.max(axis=1,keepdims=True),1e-30)
                allowed=np.zeros((10,17),bool); np.put_along_axis(allowed,order[:,:k],np.take_along_axis(rel,order[:,:k],axis=1)>=THRESHOLD,axis=1)
                masks.append(allowed[np.arange(10),book].all(axis=1)); operations+=len(book)*10
            if k==3:
                assert np.flatnonzero(masks[0]).tolist()==ref['decisions']['top3_.25']['candidates']
            union=np.logical_or.reduce(masks); assert all(np.all(~m|union) for m in masks)
            per_grid[str(k)]=[decision(m,i) for m in masks]
            for name,mask in [('nominal',masks[0]),('concentration',masks[best]),('union',union),('oracle',masks[oracle])]:
                d=decision(mask,i); p=f'k{k}_{name}'; results[p]=d
                c=summary.setdefault(base['condition'],{}).setdefault(p,dict(correct=0,wrong=0,empty=0,ambiguous=0,retained=0)); c[d['outcome']]+=1; c['retained']+=d['retained']
        rows.append(dict(condition=base['condition'],origin=i,rival=base['rival'],pcm_sha256=base['pcm_sha256'],actual_offset=GRIDS[oracle],chosen_offset=GRIDS[best],concentration=scores,per_grid=per_grid,decisions=results))
    def trace(frame,event,arg):
        if event=='call' and frame.f_code is maincode: return trace
        if frame.f_code is maincode:
            if event=='line' and frame.f_lineno==targets[0]: inspect(frame.f_locals)
            return trace
        return None
    try:
        sys.settrace(trace)
        with contextlib.redirect_stdout(io.StringIO()): g['main'](root,out/'upstream')
    finally: sys.settrace(None)
    assert len(rows)==384 and all(sum(v[k] for k in ('correct','wrong','empty','ambiguous'))==32 for d in summary.values() for v in d.values())
    aggregate={p:{k:sum(d[p][k] for d in summary.values()) for k in next(iter(summary.values()))[p]} for p in next(iter(summary.values()))}
    receipt=dict(schema='mhac-joint-grid-audit-v1',parent=PARENT,measurement=MEASUREMENT,source_blob=SOURCE_BLOB,frozen_receipt_sha256=sha((frozen/'receipt.json').read_bytes()),runtime=[sys.version.split()[0],np.__version__],seed=old['seed'],grids_samples=GRIDS,ranks=RANKS,threshold=THRESHOLD,summary=summary,aggregate=aggregate,rows=rows,scan_slot_comparisons=operations,limits='Frozen corpus replay, not held-out. Known frame extent; true offset oracle is diagnostic only. Grid union combines whole-frame hypotheses, never slots from different grids. Concentration picks largest mean strongest-tone power fraction of 17 bins, ties choose earliest grid. Unmatched compute; no streaming, drift, physical or human evaluation.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join('<p>'+html.escape(s['file'])+' <audio controls preload="none" src="upstream/'+s['file']+'"></audio></p>' for s in old['specimens'])
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Joint grid replay</title><h1>Joint grid replay</h1><p>Frozen synthetic corpus. No autoplay; low volume. Not calibrated SPL.</p>'+gallery+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script><h2>Aggregate</h2><pre>'+html.escape(json.dumps(aggregate,indent=2))+'</pre><h2>By condition</h2><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><a href="receipt.json">Full per-grid traces</a>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({str(p.relative_to(out)).replace('\\','/'):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(aggregate,indent=2))
if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
