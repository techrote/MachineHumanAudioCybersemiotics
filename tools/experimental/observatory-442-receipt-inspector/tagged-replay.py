"""Measurement #442: replay complete PCM observations with hypothetical protected tags.
Synthetic only. Tags/association are ideal side information, not acoustic transport.
Run: python tagged-replay.py fresh64 run64 (fresh64 from diverse-retry.py with seed 4426401).
"""
import hashlib, importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path

PARENT = '927313814ec4fbd1045c522a6ba785982925e79a'
SOURCE = '59ad531f932a41d8eee3b6a358f423dc627825ba0c8ef755654dfb7ff11d66e2'
SEED = 4426401
BITS = (4, 8, 16, 256)
POL = ('union', 'replace', 'associated_replace', *(f'tag{n}' for n in BITS))

def sha(x): return hashlib.sha256(x).hexdigest()
def tag(frame, message, bits):
    return int(sha(json.dumps([frame, list(message)], separators=(',', ':')).encode()), 16) >> (256-bits)

def candidates(x, y, direct):
    choices = [sorted({u,v}-{None}) for u,v in zip(x,y)]
    return sorted({tuple(g) for z in itertools.product(*choices) if (g:=direct(list(z))) is not None})

def decide(x, y, frame, retry_frame, expected, policy, direct):
    bits = int(policy[3:]) if policy.startswith('tag') else None
    target = None if expected is None or bits is None else tag(frame,expected,bits)
    def good(g): return g is not None and (bits is None or (target is not None and tag(frame,g,bits)==target))
    first=direct(x)
    if good(first): return list(first),1,1
    if (bits is not None or policy=='associated_replace') and frame!=retry_frame: return None,2,0
    if bits is not None:
        matches=[g for g in candidates(x,y,direct) if good(g)]
        return (list(matches[0]) if len(matches)==1 else None),2,len(matches)
    if policy=='union' and any(u is not None and v is not None and u!=v for u,v in zip(x,y)): return None,2,0
    g=direct([v if v is not None else u for u,v in zip(x,y)])
    return g,2,int(g is not None)

def run(src,out):
    p=Path(__file__).with_name('diverse-retry.py'); assert sha(p.read_bytes())==SOURCE
    s=importlib.util.spec_from_file_location('diverse',p); d=importlib.util.module_from_spec(s); s.loader.exec_module(d)
    rec=json.loads((src/'receipt.json').read_text()); assert rec['seed']==SEED and rec['source_sha256']==SOURCE
    d.verify(src)
    rows=[json.loads(x) for x in (src/'traces.jsonl').read_text().splitlines()]
    def direct(x): return d.a.admit(x,'all_observed')
    by={(r['condition'],r['fixture']):r for r in rows}; traces=[]
    for r,stale in [(r,False) for r in rows]+[(r,True) for r in rows if r['condition']=='white']:
        other=by[(r['condition'],(r['fixture']+1)%54)] if stale else r
        frame=r['fixture']; retry_frame=other['fixture']; expected=None if r['condition']=='absent' else r['expected'][:5]
        x,y=r['observed'][0],other['observed'][2]
        decisions={}
        for k in POL:
            g,n,m=decide(x,y,frame,retry_frame,expected,k,direct)
            decisions[k]=dict(decoded=g,frames=n,matches=m,status='withheld' if g is None else 'correct' if g==expected else 'wrong')
        traces.append(dict(condition='stale_white' if stale else r['condition'],frame=frame,retry_frame=retry_frame,expected=expected,observed=[x,y],pcm_sha256=[r['pcm_sha256'][0],other['pcm_sha256'][2]],decisions=decisions))
    groups=[]
    for c in sorted({r['condition'] for r in traces}):
        for k in POL:
            ds=[r['decisions'][k] for r in traces if r['condition']==c]; counts=Counter(v['status'] for v in ds)
            groups.append(dict(condition=c,policy=k,n=len(ds),correct=counts['correct'],wrong=counts['wrong'],withheld=counts['withheld'],frames=sum(v['frames'] for v in ds)))
    # Exhaustive tag collision census: 108 possible meanings per frame ID, not a security bound.
    messages=[(lex,0,*q) for lex in range(4) for q in itertools.product(range(3),repeat=3)]
    collisions={str(n):sum(len(messages)-len({tag(f,m,n) for m in messages}) for f in range(54)) for n in BITS}
    assert collisions['256']==0
    assert all(r['decisions']['tag256']['status']!='wrong' for r in traces)
    assert all(r['decisions']['associated_replace']['frames']==1 or r['decisions']['associated_replace']['status']=='withheld' for r in traces if r['condition']=='stale_white')
    out.mkdir(); receipt=dict(parent=PARENT,seed=SEED,source_sha256=sha(Path(__file__).read_bytes()),input_sha256=sha((src/'traces.jsonl').read_bytes()),groups=groups,tag_collision_excess=collisions,limits='432 fresh PCM fixtures plus 54 stale observation replays. Tag and frame ID are perfectly delivered trusted side information; no feedback, tag transmission, authentication or human evidence measured. 240 ms per acoustic frame, no selective-slot rendering.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='<!doctype html><meta charset=utf-8><title>Tagged replay</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto}td,th{padding:.5em;text-align:right}td:first-child{text-align:left}</style><h1>Tagged evidence replay</h1><p>Ideal trusted side information; not an acoustic integrity protocol. Select a condition and hypothetical tag rate to include tag time in the cost estimate.</p><select id="c"></select> <label>Tag bit/s <input id="rate" type="number" min="1" value="100"></label><table><thead><tr><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Frames</th><th>Correct/s*</th></tr></thead><tbody id="rows"></tbody></table><p>*240 ms per frame plus one ideal tag per fixture; excludes feedback and frame-ID cost. <a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(groups)+';const c=document.getElementById("c"),r=document.getElementById("rate"),body=document.getElementById("rows");for(const v of new Set(d.map(x=>x.condition)))c.add(new Option(v,v));function draw(){body.replaceChildren(...d.filter(x=>x.condition===c.value).map(x=>{let t=document.createElement("tr"),b=x.policy.startsWith("tag")?Number(x.policy.slice(3)):0;for(const v of [x.policy,x.correct,x.wrong,x.withheld,x.frames,(x.correct/(x.frames*.24+x.n*b/Math.max(1,Number(r.value)||1))).toFixed(3)]){let e=document.createElement("td");e.textContent=v;t.append(e)}return t}))}c.onchange=r.oninput=draw;draw()</script>'
    (out/'index.html').write_text(html)
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    print(len(traces),len(traces)*len(POL),collisions)

if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]))
