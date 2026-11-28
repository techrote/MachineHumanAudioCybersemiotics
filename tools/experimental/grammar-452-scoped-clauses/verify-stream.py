"""Verify custody, rerender hashes, and cross-check local candidate/grammar logic."""
import hashlib,itertools,json,math,runpy,sys,wave
from pathlib import Path
from collections import Counter
import numpy as np
S=runpy.run_path(str(Path(__file__).with_name('stream-grammar.py')))
G=S['G']; V=G['VOCAB']; A=G['ARITY']; BOOK=S['BOOK']
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(rows):
    stack=[]
    for k,d in reversed(rows):
        if len(stack)<A[k]:return None
        children=[stack.pop() for _ in range(A[k])]
        if any(cd!=d+1 for cd,_ in children):return None
        stack.append((d,[V[k],*[ct for _,ct in children]]))
    return stack[0][1] if len(stack)==1 and stack[0][0]==0 else None

def check_candidates(obs,start,end):
    if len(obs) not in (3,4) or not .34<=end-start<=.69:return []
    answer=[]
    for mask in itertools.combinations(range(4),len(obs)):
        for k,intervals in enumerate(BOOK):
            p=[0,intervals[0],sum(intervals[:2]),sum(intervals)]
            if any(abs(12*math.log2(b['f']/a['f'])-(p[j]-p[i]))>.85 for a,b,i,j in zip(obs,obs[1:],mask,mask[1:])):continue
            for d in range(4):
                t=[.04,.1625+.085*d,.5075+.085*d,.88]
                if all(abs((e['t']-start)/(end-start)-t[i])<=.04 for e,i in zip(obs,mask)):answer.append([k,d,list(mask)])
    return answer

def main(path,repeat=None):
    p=Path(path);r=json.loads((p/'receipt.json').read_text());rows=json.loads((p/'traces.json').read_text());manifest=json.loads((p/'manifest.json').read_text());assert all(sha((p/k).read_bytes())==v for k,v in manifest.items());wavs=[k for k in manifest if k.endswith('.wav')]
    for k in wavs:
        with wave.open(str(p/k)) as w:assert w.getframerate()==16000 and w.getsampwidth()==2 and w.getnchannels()==1 and w.getnframes()>0
    counts={c:{m:Counter() for m in S['MODES']} for c in S['CONDITIONS']};replayed=0;local=0;grammar=0;hashes=0
    for row in rows:
        tree=G['catalogue']()[row['tree_index']];x,b=S['render'](G['encode'](tree),row['condition'],row['seed']);assert sha(x.tobytes())==row['pcm_sha256'] and b==row['true_bounds'];hashes+=1
        ev=S['observe'](x);assert ev==row['observations']
        for mode,res in row['outcomes'].items():
            got,proof=S['decode'](ev,mode,b if mode=='oracle' else None);assert json.loads(json.dumps(dict(status=G['classify'](got,tree),meaning=got,proof=proof)))==res;replayed+=1
            counts[row['condition']][mode][res['status']]+=1
            nodes=[]
            for f in res['proof']['frames']:
                obs=[e for e in ev if e['kind']=='note' and f['start']<=e['t']<f['end']];h=check_candidates(obs,f['start']+.064,f['end']);assert h==f['candidates'];local+=1
                if len(h)==1:nodes.append(h[0][:2])
            if res['proof']['reason'] in ('admitted','grammar'):
                assert parse(nodes)==res['meaning'];grammar+=1
    assert counts==r['summary'];assert replayed==r['decisions'];assert hashes==r['cases']
    n=0
    if repeat:
        q=Path(repeat);assert {x.name for x in p.iterdir()}=={x.name for x in q.iterdir()}
        for f in p.iterdir():assert f.read_bytes()==(q/f.name).read_bytes();n+=1
    print(json.dumps(dict(pcm_hashes=hashes,decision_replays=replayed,scalar_candidate_checks=local,reverse_parser_checks=grammar,summary_groups=len(counts)*len(S['MODES']),manifest_entries=len(manifest),wav_headers=len(wavs),byte_identical_exports=n),sort_keys=True))
if __name__=='__main__':main(*sys.argv[1:])
