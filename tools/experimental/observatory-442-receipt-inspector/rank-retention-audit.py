"""Refs #442/#443; full-spectrum rank/threshold measurement on frozen synthetic PCM.
Usage: python rank-retention-audit.py PINNED_DIR FROZEN_OUTPUT NEW_OUTPUT
No human listener, timing search, calibrated posterior or receiver recommendation.
"""
import contextlib, hashlib, html, io, json, pathlib, runpy, sys, wave
import numpy as np

REF = '3e234a74cc4e5fc00307a73a270cd731249ff254'
BLOB = '4fd5b8e65670ff2d06aab7ad602141f43c6f4c8c'
RANKS = (1, 2, 3, 4, 5, 8, 17)
THRESHOLDS = (.25, .39, .50)

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p, x): p.write_text(json.dumps(x, indent=2)+'\n', encoding='utf-8')
def measure(book, mag, origin):
    """Rank ties resolved by ascending tone index; thresholds inclusive."""
    order = np.argsort(-mag, axis=1, kind='stable')
    rel = mag / np.maximum(mag.max(axis=1, keepdims=True), 1e-30)
    rank = np.argsort(order, axis=1)+1
    slot = np.arange(book.shape[1])
    maxrank = rank[slot, book].max(axis=1)
    caps = rel[slot, book].min(axis=1)
    result = {}
    for k in RANKS:
        eligible = maxrank <= k
        rivals = eligible.copy(); rivals[origin] = False
        other = float(caps[rivals].max()) if rivals.any() else 0.0
        true = float(caps[origin])
        result[str(k)] = {'unique_interval': bool(eligible[origin] and true > other),
                          'strongest_other_cap': other, 'thresholds': {}}
        for t in THRESHOLDS:
            ids = np.flatnonzero(eligible & (caps >= t))
            kept = bool(eligible[origin] and true >= t)
            outcome = ('correct' if kept else 'wrong') if len(ids)==1 else ('ambiguous' if len(ids) else 'empty')
            loss = ('both' if true<t else 'rank') if not eligible[origin] else ('threshold' if true<t else 'retained')
            result[str(k)]['thresholds'][str(t)] = dict(outcome=outcome, loss=loss, count=len(ids), retained=kept,
                unique_id=int(ids[0]) if len(ids)==1 else None)
    return dict(max_source_rank=int(maxrank[origin]), source_cap=float(caps[origin]),
                source_slot_ranks=rank[slot, book[origin]].tolist(), source_slot_ratios=rel[slot,book[origin]].tolist(),
                rank_results=result), order, rel

def main(root, frozen, out):
    src = root/'heldout-retention.py'; assert blob(src.read_bytes()) == BLOB
    upstream = runpy.run_path(str(src))
    for n, h in upstream['BLOBS'].items(): assert blob((root/n).read_bytes()) == h, n
    manifest = load(frozen/'manifest.json')
    for n, h in manifest.items(): assert sha((frozen/n).read_bytes()) == h, n
    ref = load(frozen/'receipt.json'); out.mkdir(parents=True, exist_ok=False)
    # Observe the actual native FFT results without replacing their calculation.
    # Scope interception to the pinned CLI invocation and restore on failure.
    spectra = []; original = np.fft.rfft
    def capture(x, *a, **kw):
        y = original(x, *a, **kw)
        if x.shape == (10,640): spectra.append(np.abs(y[:,np.arange(16,81,4)]).copy())
        return y
    try:
        np.fft.rfft = capture
        with contextlib.redirect_stdout(io.StringIO()): upstream['main'](root,out/'upstream')
    finally: np.fft.rfft = original
    native = load(out/'upstream'/'receipt.json')
    assert len(spectra)==len(native['rows'])==len(ref['rows'])==384
    assert {k:v for k,v in native.items() if k!='rows'} == {k:v for k,v in ref.items() if k!='rows'}
    scale_deltas = [abs(a['scale']-b['scale']) for a,b in zip(native['rows'],ref['rows'])]
    for a,b in zip(native['rows'],ref['rows']):
        assert {k:v for k,v in a.items() if k!='scale'} == {k:v for k,v in b.items() if k!='scale'}
    assert max(scale_deltas) < 1e-12
    g = runpy.run_path(str(root/'control-namespace.py')); _,_,_,book,_,_=g['build'](root)
    assert book.shape==(68204,10)
    rows=[]; summary={}; checks=0
    for r,mag in zip(native['rows'],spectra):
        origin=r['origin']; row,order,rel=measure(book,mag,origin)
        assert order[:,:3].tolist()==r['top3']
        assert np.array_equal(np.take_along_axis(rel,order[:,:3],axis=1),r['relative_top3'])
        for p,(k,t) in upstream['POLICIES'].items():
            v=row['rank_results'][str(k)]['thresholds'][str(t)]; expected=r['decisions'][p]
            assert (v['outcome'],v['retained'],v['count'])==(expected['outcome'],expected['retained'],len(expected['candidates']))
            if v['count']==1: assert v['unique_id']==expected['candidates'][0]
            checks+=1
        # Literal independent threshold mask check for full spectrum at .25.
        ids=np.flatnonzero((rel[np.arange(10),book]>=.25).all(axis=1))
        assert len(ids)==row['rank_results']['17']['thresholds']['0.25']['count']
        for group in ('all',r['condition']):
            for k, rr in row['rank_results'].items():
                for t,v in rr['thresholds'].items():
                    s=summary.setdefault(group,{}).setdefault(k+'/'+t,dict(correct=0,wrong=0,empty=0,ambiguous=0,rank=0,threshold=0,both=0,retained=0,unique_interval=0))
                    s[v['outcome']]+=1; s[v['loss']]+=1; s['unique_interval']+=rr['unique_interval']
        rows.append(dict(condition=r['condition'],origin=origin,pcm_sha256=r['pcm_sha256'],**row))
    for group, d in summary.items():
        for s in d.values():
            n=384 if group=='all' else 32
            assert sum(s[z] for z in ('correct','wrong','empty','ambiguous'))==n
            assert sum(s[z] for z in ('rank','threshold','both','retained'))==n
    for s in ref['specimens']:
        p=out/'upstream'/s['file']; assert p.read_bytes()==(frozen/s['file']).read_bytes()
        with wave.open(str(p),'rb') as w: assert sha(w.readframes(w.getnframes()))==s['pcm_sha256']
    receipt=dict(schema='mhac-rank-retention-v1',source_ref=REF,source_blob=BLOB,dependency_blobs=upstream['BLOBS'],dependency_refs=upstream['PINS'],seed=ref['seed'],runtime=[sys.version.split()[0],np.__version__],frozen_receipt_sha256=sha((frozen/'receipt.json').read_bytes()),native_receipt_sha256=sha((out/'upstream'/'receipt.json').read_bytes()),scale_delta_count=sum(d>0 for d in scale_deltas),scale_delta_max=max(scale_deltas),policy_crosschecks=checks,full_spectrum_crosschecks=len(rows),summary=summary,rows=rows,limits='Fixed nominal timing, aligned analysis grid as upstream; 384 synthetic observations, repeated origins across conditions, no independent population inference. Rank and magnitude cutoffs are descriptive, not tuned defaults. Unique interval is an oracle bound, not calibrated confidence or source authentication.')
    dump(out/'receipt.json',receipt)
    data=json.dumps(summary,separators=(',',':'))
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Rank retention inspector</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}table{border-collapse:collapse}td,th{padding:.4em;border:1px solid #999;text-align:right}label{display:inline-block;margin:.5em}</style><h1>Rank retention inspector</h1><p>Frozen synthetic corpus. Rank and magnitude limits are distinct; no human evidence or confidence calibration.</p><label>Condition <select id="g"></select></label><label>Magnitude cutoff <select id="t"><option>0.25</option><option>0.39</option><option>0.5</option></select></label><table id="tab"></table><p>Unique interval: oracle count with some positive threshold yielding correct unique identity. Not a deployed receiver.</p><p>Original upstream audio, opt-in, default 20% player gain; no calibrated SPL.</p>'''+''.join('<p>'+html.escape(s['file'])+' <audio controls preload="none" src="upstream/'+html.escape(s['file'])+'"></audio></p>' for s in ref['specimens'])+'''<p><a href="receipt.json">Full replay and source-rank traces</a></p><script>const data='''+data+''';const g=document.querySelector('#g'),t=document.querySelector('#t'),tab=document.querySelector('#tab');Object.keys(data).forEach(x=>g.add(new Option(x,x)));function render(){tab.innerHTML='<tr><th>Max rank</th><th>Correct</th><th>Wrong</th><th>Empty</th><th>Ambiguous</th><th>Rank only</th><th>Threshold only</th><th>Both</th><th>Retained</th><th>Unique interval</th></tr>';[1,2,3,4,5,8,17].forEach(k=>{let s=data[g.value][k+'/'+t.value];let tr=tab.insertRow();[k,...['correct','wrong','empty','ambiguous','rank','threshold','both','retained','unique_interval'].map(x=>s[x])].forEach(v=>tr.insertCell().textContent=v)})}g.onchange=t.onchange=render;render();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''',encoding='utf-8')
    dump(out/'manifest.json',{str(p.relative_to(out)).replace('\\','/'):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(dict(scale_delta_count=receipt['scale_delta_count'],scale_delta_max=max(scale_deltas),policy_crosschecks=checks,all=summary['all'],three7delay=summary['three7delay']),indent=2))

if __name__=='__main__': main(*(pathlib.Path(x) for x in sys.argv[1:]))
