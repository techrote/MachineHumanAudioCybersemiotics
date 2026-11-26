"""Measurement lane, Refs #442/#443. Synthetic frozen replay, no new receiver qualification.
Usage: python grid-support-inspector.py PINNED_DIR HELDOUT_DIR GRID_DIR NEW_OUTPUT_DIR
"""
import contextlib, hashlib, html, io, json, pathlib, runpy, sys
import numpy as np

REF='cd3d36265f8208ee7d9b488028c2c541c79f012c'
PARENT='3e234a74cc4e5fc00307a73a270cd731249ff254'
PINS={'joint-grid-audit.py':'1bf6eecfac00af924f1d2fc542525c8ec0ae63b3','heldout-retention.py':'4fd5b8e65670ff2d06aab7ad602141f43c6f4c8c','rival-tone-audit.py':'62a58dae6a86d86439a364d6644f92be63891bf6','candidate-retention.py':'af6e0f81143484a54baec8894f21e3090a8eb8c5','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
OFFSETS=(0,160,320,480)
RANKS=(3,17)
THRESHOLD=.25

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def verify(d):
    for n,h in json.loads((d/'manifest.json').read_text()).items():
        assert sha((d/n).read_bytes())==h,n

def decision(ids,i):
    n=len(ids); retained=i in ids
    return dict(outcome=('correct' if retained else 'wrong') if n==1 else ('ambiguous' if n else 'empty'),retained=retained,count=n,unique=int(ids[0]) if n==1 else None)

def topology(sets,i):
    # Identity support is a four-bit mask, not an independent-vote probability.
    support={}
    for j,ids in enumerate(sets):
        for c in ids: support[c]=support.get(c,0)|(1<<j)
    source=support.get(i,0); rival={c:m for c,m in support.items() if c!=i}
    maxr=max((m.bit_count() for m in rival.values()),default=0)
    hist=[sum(m==j for m in rival.values()) for j in range(16)]
    assert sum(hist)==len(rival)
    return dict(source_mask=source,rival_max_support=maxr,rival_mask_hist=hist,
                rival_ids_by_mask={str(j):sorted(c for c,m in rival.items() if m==j) for j in range(1,16) if hist[j]},
                support_margin=source.bit_count()-maxr,
                unique_support_interval=source.bit_count()>maxr)

def selftest():
    t=topology([[1,2],[1],[2,3],[1,3]],1)
    assert t['source_mask']==11 and t['rival_max_support']==2 and t['rival_mask_hist'][5]==1 and t['rival_mask_hist'][12]==1 and t['unique_support_interval']
    assert not topology([[1,2],[],[],[]],1)['unique_support_interval']
    assert not topology([[],[],[],[]],1)['unique_support_interval']
    assert not topology([[2],[2],[1],[2]],1)['unique_support_interval']

PAGE='''<!doctype html><meta charset="utf-8"><title>Grid support inspector</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:0 1em}table{border-collapse:collapse}td,th{padding:.4em;border:1px solid #aaa;text-align:left}select{margin:.5em}pre{white-space:pre-wrap;overflow-wrap:anywhere}audio{display:block}</style><h1>Timing-grid identity support</h1><p>Frozen synthetic PCM replay. Each bit identifies a whole-frame timing hypothesis, not an independent observation or probability. Offsets are 0, 10, 20, 30 ms (bit 0 to 3). Diagnostic truth labels are not receiver inputs.</p><label>Condition <select id="condition"></select></label><label>Origin <select id="origin"></select></label><label>Rank <select id="rank"><option>3</option><option selected>17</option></select></label><p id="detail"></p><table><thead><tr><th>Support mask (30→0 ms)</th><th>Source</th><th>Rivals</th><th>Rival IDs (first 20)</th></tr></thead><tbody id="cells"></tbody></table><h2>Matched upstream specimens</h2>GALLERY<h2>Aggregate diagnostics</h2><pre id="summary"></pre><p><a href="receipt.json">Machine-readable complete candidate support</a></p><script>const data=DATA; const $=x=>document.getElementById(x), cond=$("condition"), orig=$("origin"), rank=$("rank"); function opts(el,vs){el.replaceChildren(...vs.map(v=>new Option(v,v)))}opts(cond,[...new Set(data.rows.map(r=>r.condition))]);function origins(){opts(orig,data.rows.filter(r=>r.condition===cond.value).map(r=>r.origin));draw()}function draw(){const r=data.rows.find(r=>r.condition===cond.value&&r.origin===Number(orig.value)), t=r.ranks[rank.value];$("detail").textContent=`Origin ${r.origin}; rival ${r.rival}; actual offset ${r.actual_offset/16} ms. Source support ${t.source_mask.toString(2).padStart(4,"0")}; maximum rival support ${t.rival_max_support}; support margin ${t.support_margin}.`;$("cells").replaceChildren(...Array.from({length:15},(_,j)=>j+1).filter(m=>t.rival_mask_hist[m]||m===t.source_mask).map(m=>{const tr=document.createElement("tr");for(const v of [m.toString(2).padStart(4,"0"),m===t.source_mask?"yes":"",t.rival_mask_hist[m],(t.rival_ids_by_mask[m]||[]).slice(0,20).join(", ")]){const td=document.createElement("td");td.textContent=v;tr.append(td)}return tr}));}cond.onchange=origins;orig.onchange=rank.onchange=draw;origins();$("summary").textContent=JSON.stringify(data.summary,null,2);document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>'''

def main(root,held,grid,out):
    selftest()
    for n,h in PINS.items(): assert blob((root/n).read_bytes())==h,n
    verify(held); verify(grid)
    frozen=json.loads((grid/'receipt.json').read_text()); old=json.loads((held/'receipt.json').read_text())
    assert frozen['schema']=='mhac-joint-grid-audit-v1' and frozen['parent']==PARENT and frozen['frozen_receipt_sha256']==sha((held/'receipt.json').read_bytes())
    assert tuple(frozen['grids_samples'])==OFFSETS and tuple(frozen['ranks'])==RANKS and frozen['threshold']==THRESHOLD
    out.mkdir(parents=True,exist_ok=False)
    g=runpy.run_path(str(root/'heldout-retention.py')); code=g['main'].__code__
    targets=[j+1 for j,l in enumerate((root/'heldout-retention.py').read_text().splitlines()) if 'if i==origins[0] and label in' in l]; assert len(targets)==1
    rows=[]; checks=0; packed=None
    def inspect(v):
        nonlocal packed,checks
        base=v['row']; i=int(v['i']); book=v['book']; ref=frozen['rows'][len(rows)]; previous=old['rows'][len(rows)]
        assert (base['condition'],i,base['pcm_sha256'],base['decisions'])==(previous['condition'],previous['origin'],previous['pcm_sha256'],previous['decisions'])
        assert (ref['condition'],ref['origin'],ref['pcm_sha256'])==(base['condition'],i,base['pcm_sha256'])
        if packed is None:
            packed=np.packbits(book.T[:,None,:]==np.arange(17)[None,:,None],axis=-1)
        x=v['pcm'].ravel(); sets={str(k):[] for k in RANKS}; scores=[]
        for off in OFFSETS:
            windows=np.stack([x[j*1280+160+off:j*1280+800+off] for j in range(10)])
            mag=np.abs(np.fft.rfft(windows,axis=1))[:,np.arange(16,81,4)]
            rel=mag/np.maximum(mag.max(axis=1,keepdims=True),1e-30); order=np.argsort(-mag,axis=1,kind='stable')
            power=mag**2; scores.append(float(np.mean(power.max(axis=1)/np.maximum(power.sum(axis=1),1e-30))))
            for k in RANKS:
                bits=np.full(packed.shape[-1],255,dtype=np.uint8)
                for slot in range(10):
                    eligible=[f for f in order[slot,:k] if rel[slot,f]>=THRESHOLD]
                    if not eligible: bits[:]=0; break
                    bits &= np.bitwise_or.reduce(packed[slot,eligible],axis=0)
                ids=np.flatnonzero(np.unpackbits(bits)[:len(book)]).tolist(); sets[str(k)].append(ids)
                assert decision(ids,i)==ref['per_grid'][str(k)][len(scores)-1]; checks+=1
        best=int(np.argmax(scores)); oracle=OFFSETS.index(v['delay']); assert OFFSETS[best]==ref['chosen_offset'] and OFFSETS[oracle]==ref['actual_offset']
        r=dict(condition=base['condition'],origin=i,rival=base['rival'],actual_offset=OFFSETS[oracle],pcm_sha256=base['pcm_sha256'],ranks={})
        for k in RANKS:
            ss=sets[str(k)]; union=sorted(set().union(*ss))
            for label,ids in [('nominal',ss[0]),('concentration',ss[best]),('union',union),('oracle',ss[oracle])]:
                assert decision(ids,i)==ref['decisions'][f'k{k}_{label}']; checks+=1
            t=topology(ss,i); assert sum(t['rival_mask_hist'])+bool(t['source_mask'])==len(union)
            r['ranks'][str(k)]=t
        rows.append(r)
    def trace(frame,event,arg):
        if event=='call' and frame.f_code is code: return trace
        if frame.f_code is code:
            if event=='line' and frame.f_lineno==targets[0]: inspect(frame.f_locals)
            return trace
        return None
    try:
        sys.settrace(trace)
        with contextlib.redirect_stdout(io.StringIO()): g['main'](root,out/'upstream')
    finally: sys.settrace(None)
    assert len(rows)==384 and checks==6144
    summary={}
    for group in ['all']+list(old['summary']):
        subset=[r for r in rows if group=='all' or r['condition']==group]
        summary[group]={}
        for k in RANKS:
            ts=[r['ranks'][str(k)] for r in subset]
            summary[group][str(k)]=dict(n=len(ts),source_support_hist=[sum(t['source_mask'].bit_count()==j for t in ts) for j in range(5)],strict_source_support_lead=sum(t['unique_support_interval'] for t in ts),rival_support_tie=sum(t['source_mask']!=0 and t['support_margin']==0 for t in ts),rival_support_lead=sum(t['support_margin']<0 for t in ts),source_absent_no_rival=sum(t['source_mask']==0 and t['rival_max_support']==0 for t in ts),rivals_on_one_grid=sum(sum(t['rival_mask_hist'][m] for m in (1,2,4,8)) for t in ts),rivals_on_all_grids=sum(t['rival_mask_hist'][15] for t in ts))
    receipt=dict(schema='mhac-grid-support-v1',source_ref=REF,parent=PARENT,pins=PINS,seed=old['seed'],frozen_grid_sha256=sha((grid/'receipt.json').read_bytes()),frozen_heldout_sha256=sha((held/'receipt.json').read_bytes()),runtime=[sys.version.split()[0],np.__version__],checks=checks,summary=summary,rows=rows,limits='Frozen replay; support counts correlate overlapping windows and are not calibrated probabilities. Strict source support lead is an oracle diagnostic for minimum-grid-count filters only; not held-out performance. Rival counts are identity-observation incidences. Known extent and four fixed offsets; no physical or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join('<p>'+html.escape(s['file'])+'<audio controls preload="none" src="upstream/'+s['file']+'"></audio></p>' for s in old['specimens'])
    for s in old['specimens']: assert sha((out/'upstream'/s['file']).read_bytes())==sha((held/s['file']).read_bytes())
    (out/'index.html').write_text(PAGE.replace('GALLERY',gallery).replace('DATA',json.dumps(dict(rows=rows,summary=summary),separators=(',',':'))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
