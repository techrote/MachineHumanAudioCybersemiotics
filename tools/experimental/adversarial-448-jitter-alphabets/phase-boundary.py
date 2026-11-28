"""Refs #448/#449. Sub-slot overlap audit, synthetic only.
Usage: python phase-boundary.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22'
BLOBS=dict(zip(('causal-frame.py','competing-starts.py','control-namespace.py','discourse-sync.py','distributed-profile.py','frame-length-commit.py','interval-admission.py','migration-namespace.py','prefix-disjoint.py','version-bound-payload.py','version-bridge.py'),('fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60','af3f673f28e65bb4fc241a22cc603a6cbb041dfb','8e27fe89f2734a0b5fd666bb2018b0d379736493','cc6b996d6314fdcbb92edc85e12878d5d2077aa7','a780404e8c76820976ad6fb407429ec895a6313f','1538e258e53b62fc62315ca11eb9ba34496c5919','32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3','b3562781a974c47b41cbe066ceb755288a51b6b1','f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','7ef6881cefa9c34355d024aeea671d021b674a55','6400cf4c1b42fbe958b0265da43ef657bb355401')))
S=1280; SEED=448039; PHASES=(-30,-20,-10,-5,0,5,10,20,30)
def sha(b): return hashlib.sha256(b).hexdigest()
def run(root,out):
    for f,h in BLOBS.items():
        b=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h,f
    def load(f): return runpy.run_path(str(root/f))
    v=load('interval-admission.py'); p=load('competing-starts.py'); s=load('discourse-sync.py'); c=load('causal-frame.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    rng=np.random.default_rng(SEED); out.mkdir(parents=True,exist_ok=False); rows=[]; stats={}; gallery=[]; checks=0
    for j in range(8):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,k]]
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
        for phase in PHASES:
            offset=lead+int(2.5*S)+phase*16; pcm=np.zeros(32*S,np.int32); v['put'](pcm,x,lead); v['put'](pcm,y,offset); assert abs(pcm).max()<=3000; pcm=pcm.astype('<i2'); digest=sha(pcm.tobytes())
            # Oracle knows true body starts, not semantic identities; same extractor and codebook, no admission/causal comparison.
            oracle=[]
            for source,n,begin in ((a,18,lead),(b,13,offset)):
                obs=[c['observe'](pcm[begin+(q+2)*S:begin+(q+3)*S]) for q in range(n+2)]
                idx=joint(books[source][n],obs[:-2],2) if obs[-2:]==[18,18] and 18 not in obs[:-2] else None
                if idx is not None: oracle.append([source,n,idx])
            for policy,fn in (('replace-two',p['acquire']),('multiplex',v['acquire'])):
                ev=fn(pcm,books,c['observe'],joint,policy); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values())
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind'] in ('release','overlap-coadmission')}):
                        assert fn(pcm[:t],books,c['observe'],joint,policy)==[e for e in ev if e['sample']<=t]; checks+=1
                row=dict(pair=j,phase_ms=phase,policy=policy,pcm_sha256=digest,expected=want,decoded=got,oracle=oracle,correct=correct,wrong=len(got)-correct,missing=2-correct,events=ev); rows.append(row)
                stats.setdefault(str(phase),{}).setdefault(policy,Counter()).update(correct=correct,wrong=len(got)-correct,missing=2-correct,oracle_correct=sum((Counter(map(tuple,want))&Counter(map(tuple,oracle))).values()),starts=sum(e['kind']=='start' for e in ev),candidates=sum(e['kind']=='candidate' for e in ev))
            if j==0:
                name=f'phase-{phase:+d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                gallery.append(dict(file=name,phase_ms=phase,pcm_sha256=digest,peak=int(abs(pcm).max())))
    assert len(rows)==144 and all(r['wrong']+r['correct']==len(r['decoded']) and r['missing']+r['correct']==2 for r in rows)
    assert stats['0']['multiplex']['correct']==16
    receipt=dict(schema='mhac-phase-boundary-v1',pin=PIN,blobs=BLOBS,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,prefix_checks=checks,physical_pcm=72,observations=len(rows),stats=stats,specimens=gallery,limits='Fixed clock, equal component amplitude, 40ms active supports, 80ms slots. Exploratory fixed phase grid, 8 fresh pairs, no holdout. Oracle uses exact source/clock/length, not a deployable receiver. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Phase boundary</title><h1>Sub-slot overlap audit</h1><p>Equal-amplitude synthetic tones; start at low volume. Phase is onset shift relative to half-slot stagger. No autoplay.</p>'
    for g in gallery:
        html+=f'<h2>{g["phase_ms"]:+d} ms</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(g['phase_ms'])],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
