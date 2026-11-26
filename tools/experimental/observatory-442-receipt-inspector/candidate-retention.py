"""Measurement lane, Refs #442/#443. Exact candidate retention on frozen synthetic PCM traces.
python candidate-retention.py PINNED_DIRECTORY RIVAL_EXPORT NEW_OUTPUT_DIRECTORY
No human evidence, source attribution, fitted confidence or new adversarial search.
"""
import hashlib, itertools, json, math, pathlib, runpy, shutil, sys, wave
import numpy as np

PINS={'main':'495a98ca12bae467a507031f04931aa4254b1866','measurement_parent':'8b9abd7ccc7b2d8c4bd278b1233c8d9183cdbc51','grammar':'aca863378e825b26921388cfaab890f9eac86279','adversarial':'f4ecd30005c123d39452cac7937ca6266f791179'}
BLOBS={'rival-tone-audit.py':'62a58dae6a86d86439a364d6644f92be63891bf6','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','menu-transition-audit.py':'3eac4ea7f661a2abaff2710dbfbfcb84824b2754'}
RECEIPT='e7690272694850b1d2f7b97c15d00020ec7830d00eae1bffca9a933deaf635d0'
THRESHOLDS=(.25,.35,.39,.4,.41,.5,.6,.7,.8,.9,1.)
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def candidates(book,index,top,second,ratio):
    # Every matching word must have one of the 16 first-four projections.
    # Injectivity of this projection is checked when building the index.
    got=[]
    for key in itertools.product(*zip(top[:4],second[:4])):
        i=index.get(key)
        if i is None: continue
        w=book[i]; other=w!=top
        if np.any(other & (w!=second)): continue
        cap=float(min(ratio[other])) if np.any(other) else 1.
        got.append((i,cap))
    return sorted(got)

def stats(rows,t):
    s=dict(correct=0,wrong=0,empty=0,ambiguous=0,source_retained=0,ambiguous_source_missing=0,list_size_sum=0)
    for r in rows:
        keep=[i for i,c in r['candidates'] if c>=t]; n=len(keep); present=r['origin'] in keep
        s['source_retained']+=present; s['list_size_sum']+=n
        s['empty' if not n else 'ambiguous' if n>1 else 'correct' if present else 'wrong']+=1
        s['ambiguous_source_missing']+=n>1 and not present
    assert sum(s[k] for k in ('correct','wrong','empty','ambiguous'))==len(rows)
    assert s['source_retained']==s['correct']+s['ambiguous']-s['ambiguous_source_missing']
    return s

def run(root,up,out):
    for name,h in BLOBS.items(): assert blob((root/name).read_bytes())==h,name
    raw=(up/'receipt.json').read_bytes(); assert sha(raw)==RECEIPT
    src=json.loads(raw); manifest=json.loads((up/'manifest.json').read_text())
    for name,h in manifest.items(): assert sha((up/name).read_bytes())==h,name
    _,_,_,book,names,_=runpy.run_path(str(root/'control-namespace.py'))['build'](root)
    index={tuple(w[:4]):i for i,w in enumerate(book)}; assert len(index)==len(book)==68204
    rows=[]; groups={}; full_checks=0
    for j,r in enumerate(src['rows']):
        top,second,ratio=map(np.asarray,(r['top'],r['second'],r['second_over_first']))
        assert len(top)==len(second)==len(ratio)==10 and np.all(top!=second) and np.all((ratio>=0)&(ratio<=1))
        cs=candidates(book,index,top,second,ratio)
        # Independent full-table oracle, including exact continuous breakpoints.
        literal=np.flatnonzero(np.all((book==top)|(book==second),axis=1))
        expected=[(int(i),float(min(ratio[book[i]!=top])) if np.any(book[i]!=top) else 1.) for i in literal]
        assert cs==expected; full_checks+=1
        keep=[i for i,c in cs if c>=.5]; orig=r['decisions']['two_tone_set']
        assert len(keep)==orig['candidates'] and (keep[0] if len(keep)==1 else None)==orig['row']
        cap=dict(cs).get(r['origin'],-1.); competitor=max((c for i,c in cs if i!=r['origin']),default=-1.)
        row={'id':j,'origin':r['origin'],'rival':r['rival'],'kind':r['kind'],'ratio':r['ratio'],'slots':len(r['positions']),'top':r['top'],'second':r['second'],'second_over_first':r['second_over_first'],'source_word':book[r['origin']].tolist(),'candidates':cs,'source_cap':cap,'competitor_cap':competitor,'has_unique_correct_interval':cap>max(0.,competitor)}
        rows.append(row); groups.setdefault(f"{r['kind']}:k{row['slots']}:r{r['ratio']}",[]).append(row)
    assert len(rows)==800 and len(groups)==25
    groups={'all':rows,**groups}; summary={k:[stats(v,t) for t in THRESHOLDS] for k,v in groups.items()}
    for v in summary.values(): assert all(a['source_retained']>=b['source_retained'] and a['list_size_sum']>=b['list_size_sum'] for a,b in zip(v,v[1:]))
    assert summary['all'][5]['correct']==512 and summary['all'][5]['wrong']==32
    out.mkdir(parents=True,exist_ok=False)
    specimens=[]
    for s in src['specimens']:
        f=up/s['file']
        with wave.open(str(f),'rb') as w:
            assert w.getparams()[:4]==(1,2,16000,12800); pcm=w.readframes(12800)
        assert sha(pcm)==s['pcm_sha256'] and max(abs(np.frombuffer(pcm,dtype='<i2').astype(int)))<=2048
        shutil.copyfile(f,out/f.name); specimens.append(s)
    result={'schema':'mhac-candidate-retention-v1','pins':PINS,'source_blobs':BLOBS,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'upstream_receipt_sha256':RECEIPT,'upstream_seed':src['seed'],'thresholds':THRESHOLDS,'summary':summary,'rows':rows,'identities':{i:names[i] for i in sorted({i for r in rows for i in [r['origin'],r['rival']]+[i for i,c in r['candidates']]})},'specimens':specimens,'full_catalogue_checks':full_checks,'limits':'Exact replay of one targeted aligned PCM corpus; threshold sweep is descriptive, not held-out evaluation or posterior probability. Candidate cap is min observed second/first magnitude for required runner-up slots; -1 denotes absent. No calibration to real channels, human evidence or authentication. Nine copied original upstream specimens, not new recordings. No compute budget match.'}
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Candidate retention inspector</title><style>body{font:16px system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;background:#f5f6f8;color:#182335}section{background:white;padding:1rem;margin:1rem 0;border:1px solid #d8dce3;border-radius:8px}select,input{font:inherit;max-width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:.4rem;border-bottom:1px solid #ddd}audio{max-width:100%}</style><h1>Candidate retention inspector</h1><p>Frozen synthetic PCM traces. Threshold is runner-up / strongest spectral magnitude. A unique candidate is not proof of source identity.</p><section><label>Condition <select id="group"></select></label> <label>Threshold <input id="t" type="range" min="0" max="10" value="5"><output id="v"></output></label><div id="summary"></div></section><section><label>Trace <select id="row"></select></label><pre id="detail"></pre></section><section><h2>Original upstream witnesses</h2><p>Opt-in audio; start at low volume. Digital energy is not acoustic SPL.</p><div id="audio"></div></section><p><a href="receipt.json">Machine-readable receipt</a></p><script>const D=DATA;const $=id=>document.getElementById(id);const g=$('group'),t=$('t'),r=$('row');for(const k of Object.keys(D.summary))g.add(new Option(k,k));function select(){r.replaceChildren();for(const x of D.rows){if(g.value==='all'||g.value===`${x.kind}:k${x.slots}:r${x.ratio}`||g.value==='clean:k0:r0.0'&&x.kind==='clean')r.add(new Option(`${x.id}: origin ${x.origin}`,x.id));}show()}function show(){const h=D.thresholds[+t.value],s=D.summary[g.value][+t.value];$('v').textContent=h;$('summary').innerHTML='<table>'+Object.entries(s).map(([k,v])=>`<tr><th>${k}</th><td>${v}</td></tr>`).join('')+'</table>';const x=D.rows[+r.value];if(!x)return;const keep=x.candidates.filter(y=>y[1]>=h);$('detail').textContent=JSON.stringify({...x,retained:keep.map(y=>({row:y[0],identity:D.identities[y[0]],cap:y[1]})),outcome:keep.length!==1?'abstain':keep[0][0]===x.origin?'correct':'wrong'},null,2)}g.onchange=select;t.oninput=r.onchange=show;for(const s of D.specimens){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=s.file+' ';a.controls=true;a.preload='none';a.volume=.2;a.src=s.file;p.append(a);$('audio').append(p)}select();</script>'''
    (out/'index.html').write_text(page.replace('const D=DATA','const D='+json.dumps(result,separators=(',',':')).replace('</','<\\/')),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'thresholds':THRESHOLDS,'all':summary['all'],'unique_correct_interval':sum(r['has_unique_correct_interval'] for r in rows),'full_catalogue_checks':full_checks},indent=2))

if __name__=='__main__': run(*map(pathlib.Path,sys.argv[1:]))
