"""Measurement #442/#443: coverage and candidate attribution of frozen #449.
Run: python guard-coverage-inspector.py PINNED_DIR FROZEN_OUTPUT NEW_OUTPUT
Uses the exact upstream generator; no receiver tuning or fresh holdout claim.
"""
import hashlib, html, json, pathlib, runpy, sys
import numpy as np

PIN='71910f5f4a8f07cce0786deb4d65b8006f56778b'
SOURCE_BLOB='6a2821c9c4453c1f462da279f439aa8fb601e3ed'
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def write(p,d): p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def coverage(pcm,coords):
    valid=(coords>=0)&(coords<=len(pcm)-1)
    z=np.interp(coords,np.arange(len(pcm)),pcm,left=0,right=0)
    guard=np.arange(len(coords))%1280>=960
    e=z*z; a=float(e[~guard].sum()); g=float(e[guard].sum())
    na=int((valid&~guard).sum()); ng=int((valid&guard).sum())
    # Standardize observed mean-square energy to nominal 3:1 active/guard sample counts.
    # This is a sensitivity diagnostic, not an estimator of unobserved audio.
    x=3*a/na; y=g/ng
    return dict(active_samples=na,guard_samples=ng,active_energy=a,guard_energy=g,
                raw=g/max(a+g,1e-30),standardized=y/max(x+y,1e-30))
def main(root,frozen,out):
    for n,h in json.loads((frozen/'manifest.json').read_text()).items(): assert sha((frozen/n).read_bytes())==h,n
    source=root/'temporal-admission.py'; assert blob(source.read_bytes())==SOURCE_BLOB
    up=runpy.run_path(str(source)); env=up['main'].__globals__; original=env['feature']
    _,_,_,book,_,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    # Independent catalogue enumeration via progressive row filtering, not upstream bitsets.
    def candidate_ids(allowed):
        ids=np.arange(len(book))
        for s in range(10): ids=ids[allowed[s,book[ids,s]]]
        return ids.tolist()
    calls=[]
    def observe(pcm,grid):
        allowed,conc,raw=original(pcm,grid)
        c=coverage(pcm,env['arrival'](grid)); assert abs(c['raw']-raw)<1e-12
        c.update(grid=list(grid),ids=candidate_ids(allowed),pcm_sha256=sha(pcm.tobytes()))
        calls.append(c)
        return allowed,conc,raw
    out.mkdir(parents=True,exist_ok=False); env['feature']=observe
    env['main'](root,out/'reproduced')
    old=json.loads((frozen/'receipt.json').read_text()); new=json.loads((out/'reproduced/receipt.json').read_text())
    assert len(old['rows'])==len(new['rows'])==288 and len(calls)==288*14
    assert old['aggregate']==new['aggregate'] and old['summary']==new['summary']
    rows=[]
    for k,(a,b) in enumerate(zip(old['rows'],new['rows'])):
        assert a['pcm_sha256']==b['pcm_sha256'] and a['decisions']==b['decisions']
        grids=calls[14*k:14*k+13]; oracle=calls[14*k+13]
        support={}
        for j,g in enumerate(grids):
            assert g['pcm_sha256']==a['pcm_sha256'] and len(g['ids'])==a['grid_counts'][j]
            assert (a['origin'] in g['ids'])==a['grid_retained'][j]
            for ident in g['ids']: support[ident]=support.get(ident,0)|(1<<j)
            g['source']=a['origin'] in g['ids']; g['rival']=a['rival'] in g['ids']; g['count']=len(g.pop('ids'))
        assert oracle['pcm_sha256']==a['pcm_sha256'] and len(oracle['ids'])==a['decisions']['oracle']['count']
        assert (a['origin'] in oracle['ids'])==a['decisions']['oracle']['retained']; oracle.pop('ids')
        hist=[0]*14
        for ident,mask in support.items():
            if ident!=a['origin']: hist[mask.bit_count()]+=1
        source_mask=support.get(a['origin'],0); rival_mask=support.get(a['rival'],0)
        raw_best=min(range(13),key=lambda j:grids[j]['raw']); assert raw_best==a['selected_guard']
        standardized_best=min(range(13),key=lambda j:grids[j]['standardized'])
        rows.append(dict(condition=a['condition'],origin=a['origin'],rival=a['rival'],pcm_sha256=a['pcm_sha256'],
                         grids=grids,oracle=oracle,source_mask=source_mask,rival_mask=rival_mask,
                         other_support_hist=hist,raw_best=raw_best,standardized_best=standardized_best,
                         admitted08=a['admitted08'],decisions=a['decisions']))
    def summarize(rs):
        return dict(n=len(rs),best_changed=sum(r['raw_best']!=r['standardized_best'] for r in rs),
                    source_leads=sum(r['source_mask'].bit_count()>max([j for j,v in enumerate(r['other_support_hist']) if v]+[0]) for r in rs),
                    rival_leads_source=sum(r['rival_mask'].bit_count()>r['source_mask'].bit_count() for r in rs),
                    single_grid_competitors=sum(r['other_support_hist'][1] for r in rs),
                    all_grid_competitors=sum(r['other_support_hist'][13] for r in rs),
                    raw_best_missing_guard=sum(r['grids'][r['raw_best']]['guard_samples']<3200 for r in rs),
                    raw_best_missing_active=sum(r['grids'][r['raw_best']]['active_samples']<9600 for r in rs))
    summary={c:summarize([r for r in rows if r['condition']==c]) for c in old['summary']}; summary['all']=summarize(rows)
    receipt=dict(schema='mhac-guard-coverage-v1',pin=PIN,source_blob=SOURCE_BLOB,dependency_blobs=up['BLOBS'],
                 frozen_receipt_sha256=sha((frozen/'receipt.json').read_bytes()),source_sha256=sha(pathlib.Path(__file__).read_bytes()),
                 runtime=[sys.version.split()[0],np.__version__],seed=old['seed'],grids_ms=old['grids_ms'],summary=summary,rows=rows)
    write(out/'receipt.json',receipt)
    # Self-contained offline inspector; original WAV gallery remains in reproduced/.
    data=json.dumps(rows,separators=(',',':')).replace('</','<\\/')
    page='''<!doctype html><meta charset="utf-8"><title>Guard coverage inspector</title><style>body{font:16px system-ui;margin:2rem;max-width:1100px}table{border-collapse:collapse}td,th{padding:.4rem;border:1px solid #aaa}tr.best{background:#d7e8f2;color:#111}select{max-width:100%}</style><h1>Guard coverage inspector</h1><p>Synthetic matched replay. Energy in PCM-count squared; missing samples are not observed silence. Standardization is a sensitivity diagnostic, not a receiver or a calibrated confidence measure.</p><label>Observation <select id="pick"></select></label><p id="info"></p><table><thead><tr><th>Grid ms</th><th>Active samples /9600</th><th>Guard samples /3200</th><th>Raw guard fraction</th><th>Standardized</th><th>Candidates</th><th>Source</th><th>Rival</th></tr></thead><tbody id="body"></tbody></table><p><a href="receipt.json">Machine-readable trace</a> · <a href="reproduced/index.html">Original opt-in WAV gallery</a></p><h2>Summary</h2><pre>'''+html.escape(json.dumps(summary,indent=2))+'''</pre><script>const rows=DATA;const pick=document.getElementById('pick');rows.forEach((r,i)=>pick.add(new Option(r.condition+' / '+r.origin,i)));function show(){const r=rows[+pick.value];document.getElementById('info').textContent='Raw best grid '+r.raw_best+'; standardized best '+r.standardized_best+'; source mask '+r.source_mask.toString(2).padStart(13,'0')+'; rival mask '+r.rival_mask.toString(2).padStart(13,'0');document.getElementById('body').innerHTML=r.grids.map((g,i)=>'<tr class="'+(i===r.raw_best?'best':'')+'">'+[g.grid.join(' → '),g.active_samples,g.guard_samples,g.raw.toFixed(6),g.standardized.toFixed(6),g.count,g.source,g.rival].map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('')}pick.onchange=show;show()</script>'''
    (out/'index.html').write_text(page.replace('DATA',data),encoding='utf-8')
    write(out/'manifest.json',{str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main(*(pathlib.Path(s) for s in sys.argv[1:]))
