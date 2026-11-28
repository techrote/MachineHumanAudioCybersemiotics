"""Measurement #442 / #443: synthetic clean-frame menu and prefix audit.
CLI: python menu-transition-audit.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Requires NumPy; source files are exact pinned upstream, not installed packages.
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave, html
import numpy as np
PIN='aca863378e825b26921388cfaab890f9eac86279'
BLOBS={'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
def sha(b): return hashlib.sha256(b).hexdigest()
def keys(w,n): return w[:,:n] @ (17**np.arange(n,dtype=np.int64))
def groups(w,ids,n):
    d={}
    for k,i in zip(keys(w,n),ids): d.setdefault(int(k),[]).append(int(i))
    return d

def compare(a,ai,b,bi,n):
    g=groups(a,ai,n); h=groups(b,bi,n); same=wrong=0; witness=None
    for k in g.keys() & h.keys():
        for i in g[k]:
            for j in h[k]:
                if i==j: same+=1
                else:
                    wrong+=1
                    if witness is None or (i,j)<witness: witness=(i,j)
    return {'compatible_pairs':same,'incompatible_pairs':wrong,'shared_observations':len(g.keys() & h.keys()),'witness':witness}

def census(books,menu,n):
    union={}
    for name in menu:
        w,ids=books[name]
        for k,i in zip(keys(w,n),ids): union.setdefault(int(k),[]).append((name,int(i)))
    result={}
    for name in menu:
        w,ids=books[name]; semantic=outer=0; entropy=0.
        for k,i in zip(keys(w,n),ids):
            hits=union[int(k)]; semantic+=len({j for _,j in hits})==1
            outer+=len({f for f,_ in hits})==1
            entropy+=np.log2(len(hits))
        result[name]={'total':len(ids),'unique_strict_identity':semantic,'unique_outer_format':outer,'mean_log2_candidate_origins':float(entropy/len(ids))}
    return result

def audit(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes()
        if hashlib.sha1(('blob %d'%len(raw)).encode()+bytes([0])+raw).hexdigest()!=b: raise ValueError('source mismatch '+f)
    c=runpy.run_path(str(root/'control-namespace.py')); u,old,naive,fixed,names,info=c['build'](root)
    m=runpy.run_path(str(root/'migration-namespace.py')); original,free,modes,*_=m['construct'](u)
    b,_,_,_,_=u['catalogue'](); assert np.array_equal(old,original)
    data=np.arange(52000); allids=np.arange(len(fixed)); controls=allids[52000:]
    books={'tag':(old,data),'free':(free,data),'reserved':(b['reserved-cubic'],data),'relocated':(modes['relocated-cubic'],data),'unified':(fixed,allids)}
    assert len(fixed)==68204
    for name,(w,ids) in books.items():
        assert len(groups(w,ids,10))==len(ids)
        if name!='tag': assert not np.any(np.diff(w,n=4,axis=1)%17)
    pairs={}; examples=[]; out.mkdir(parents=True,exist_ok=False)
    def specimen(label,word,detail):
        file=label+'.wav'; u['audio'](out/file,word.tolist())
        with wave.open(str(out/file),'rb') as f:
            assert f.getparams()[:4]==(1,2,16000,1280*len(word)); pcm=f.readframes(f.getnframes())
        assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2')))==2048
        examples.append({'file':file,'symbols':word.tolist(),'duration_ms':80*len(word),'pcm_sha256':sha(pcm),'detail':detail})
    for a,b in itertools.combinations(books,2):
        w,i=books[a]; v,j=books[b]; r=compare(w,i,v,j,10); pairs[a+' / '+b]=r
        if r['witness'] is not None:
            x,y=r['witness']; wx=w[np.flatnonzero(i==x)[0]]; vy=v[np.flatnonzero(j==y)[0]]
            assert np.array_equal(wx,vy) and x!=y
            assert list(i[np.all(w==wx,axis=1)])==[x] and list(j[np.all(v==wx,axis=1)])==[y]
            if b=='unified': specimen(a+'-unified-alias',wx,{'origin':a,'origin_identity':names[x],'unified_identity':names[y]})
    assert pairs['free / unified']['incompatible_pairs']==1769
    assert pairs['relocated / unified']['incompatible_pairs']==2031
    menus=[['unified'],['tag','unified'],['free','unified'],['relocated','unified'],['reserved','unified'],list(books)]
    menu_results={' + '.join(menu):census(books,menu,10) for menu in menus}
    # Eight-slot historical control prefixes use the upstream transcription, NOT original CJS.
    historical=naive[52000:,:8]; prefix={}
    for a,(w,i) in books.items():
        r=compare(w,i,historical,controls,8); prefix[a]=r
        if r['witness'] is not None:
            x,y=r['witness']; wx=w[np.flatnonzero(i==x)[0]]; vy=historical[y-52000]
            assert np.array_equal(wx[:8],vy) and x!=y
            specimen(a+'-prefix-full',wx,{'ten_slot_identity':names[x],'early_control_identity':names[y]})
            specimen(a+'-prefix-eight',vy,{'historical_control_identity':names[y],'same_first_640ms_as':a+'-prefix-full.wav'})
    assert prefix['unified']['incompatible_pairs']==0
    for a in books:
        if prefix[a]['witness'] is None: continue
        with wave.open(str(out/(a+'-prefix-eight.wav')),'rb') as f: short=f.readframes(f.getnframes())
        with wave.open(str(out/(a+'-prefix-full.wav')),'rb') as f: full=f.readframes(f.getnframes())
        assert len(short)==20480 and full[:len(short)]==short
    for a in ('tag','free','reserved','relocated'):
        r=pairs[a+' / unified']; d=menu_results[a+' + unified']
        for name in (a,'unified'):
            assert d[name]['total']-d[name]['unique_strict_identity']==r['incompatible_pairs']
            assert d[name]['total']-d[name]['unique_outer_format']==r['shared_observations']
    receipt={'schema':'mhac-menu-transition-audit-v1','grammar_commit':PIN,'source_blobs':BLOBS,'audit_sha256':sha(pathlib.Path(__file__).read_bytes()),'python':sys.version.split()[0],'numpy':np.__version__,'pairs':pairs,'menus':menu_results,'historical_prefix':prefix,'specimens':examples,'limits':'Clean aligned slots, closed menus, no channel distribution. Strict identity includes profile but not outer format. Equal prior over format/row origins only for mean log2 candidate count. Historical eight-slot controls are transcribed by pinned Python upstream, not independently executed CJS. Prefix alias is conditional on early acceptance without external framing; not a measured streaming detector result. No human evidence, physical listening, or matched energy claim.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    data=json.dumps(menu_results).replace('<','\\u003c')
    page='<!doctype html><meta charset="utf-8"><title>Grammar transition inspector</title><style>body{font:16px system-ui;max-width:900px;margin:auto;padding:20px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #888;text-align:right}audio{width:100%}</style><h1>Grammar transition inspector</h1><p>Synthetic clean-symbol census. No autoplay. Start with low volume.</p><label>Supported formats <select id="menu"></select></label><div id="results"></div><h2>Historical eight-slot prefix comparisons</h2><pre>'+html.escape(json.dumps(prefix,indent=2))+'</pre><h2>Auditionable witnesses</h2>'
    page+=''.join('<h3>'+html.escape(s['file'])+'</h3><p>'+html.escape(str(s['detail']))+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in examples)
    page+='<p><a href="receipt.json">Complete receipt</a></p><script>const d='+data+';const m=document.querySelector("#menu"),r=document.querySelector("#results");Object.keys(d).forEach(k=>m.add(new Option(k,k)));function render(){r.innerHTML="<table><tr><th>Origin</th><th>Total</th><th>Unique identity</th><th>Unique format</th></tr>"+Object.entries(d[m.value]).map(([k,v])=>"<tr><td>"+k+"</td><td>"+v.total+"</td><td>"+v.unique_strict_identity+"</td><td>"+v.unique_outer_format+"</td></tr>").join("")+"</table>"}m.onchange=render;render();document.querySelectorAll("audio").forEach(a=>a.volume=.2);</script>'
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('pairs','menus','historical_prefix')},indent=2))
if __name__=='__main__': audit(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
