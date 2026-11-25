"""Independent triangle-based enumeration and equal-energy audio witness.
Python 3 standard library; no dependencies. Output written beside source.
"""
from itertools import combinations, product
from collections import Counter
from pathlib import Path
import json, math, wave, struct, hashlib
ROOT = Path(__file__).resolve().parent

def enumerate_matrices(n):
    edges = list(combinations(range(n), 2))
    idx = {e:i for i,e in enumerate(edges)}
    triples = [tuple(idx[e] for e in combinations(t, 2)) for t in combinations(range(n),3)]
    # Strictly binary, distinct merges: each triple has exactly two equal
    # largest distances; and all n-1 heights occur.
    def rec(v):
        if len(v)==len(edges):
            if set(v)==set(range(1,n)): yield tuple(v)
            return
        for k in range(1,n):
            a=v+[k]
            if all(sorted(a[i] for i in t)[0]<sorted(a[i] for i in t)[1]==sorted(a[i] for i in t)[2] for t in triples if max(t)==len(v)):
                yield from rec(a)
    # A set of heights of size n-1 guarantees exactly one binary merge at each.
    return list(rec([]))

def census():
    results=[]
    for n in range(3,6):
        H=enumerate_matrices(n); m=n*(n-1)//2
        assert len(H)==math.factorial(n)*math.factorial(n-1)//2**(n-1)
        diffs=Counter(tuple(i for i,(x,y) in enumerate(zip(a,b)) if x!=y) for a,b in combinations(H,2))
        assert min(map(len,diffs))==2
        assert all((i,j) in diffs for i,j in combinations(range(m),2))
        # Verify nearest decoder for one flagged erasure with no substitution.
        for i in range(m): assert len({a[:i]+a[i+1:] for a in H})==len(H)
        results.append(dict(n=n,histories=len(H),literal_matrix_pairs=len(H)*(len(H)-1)//2,exact_two_coordinate_supports=sum(len(k)==2 for k in diffs)))
    return results

def model(groups):
    # Leaf node = (0, leaf index); internal = (height, left, right).
    cherries=[(i+1,(0,2*i),(0,2*i+1)) for i in range(4)]
    return (7,(5,cherries[groups[0]],cherries[groups[1]]),(6,cherries[groups[2]],cherries[groups[3]]))

def vectors(tree):
    # Orthogonal edge coordinate squared norm = (parent_height^2-child_height^2)/2.
    paths={}; edges=[]
    def visit(node,path):
        if not node[0]: paths[node[1]]=path; return
        for child in node[1:]:
            j=len(edges); edges.append(math.sqrt((node[0]**2-child[0]**2)/2)); visit(child,path+[j])
    visit(tree,[])
    return [[edges[j] if j in paths[i] else 0. for j in range(len(edges))] for i in range(8)]

def expected(groups):
    order={j:i//2 for i,j in enumerate(groups)}
    return tuple(i//2+1 if i//2==j//2 else 5+order[i//2] if order[i//2]==order[j//2] else 7 for i,j in combinations(range(8),2))

def write_bank(name,groups):
    v=vectors(model(groups)); target=expected(groups)
    for a in v: assert abs(sum(x*x for x in a)-24.5)<1e-10
    for (i,j),h in zip(combinations(range(8),2),target): assert abs(sum((a-b)**2 for a,b in zip(v[i],v[j]))-h*h)<1e-10
    sr=8000; N=2000; gain=1000; freqs=[200+40*j for j in range(len(v[0]))]
    basis=[[math.sin(2*math.pi*f*t/sr) for t in range(N)] for f in freqs]
    data=[[round(gain*sum(a*b[t] for a,b in zip(row,basis))) for t in range(N)] for row in v]
    assert max(abs(x) for row in data for x in row)<32767
    p=ROOT/'audio'/f'{name}.wav';p.parent.mkdir(exist_ok=True)
    with wave.open(str(p),'wb') as w: w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes(struct.pack('<'+'h'*(8*N),*(x for row in data for x in row)))
    with wave.open(str(p),'rb') as w: raw=struct.unpack('<'+'h'*(8*N),w.readframes(8*N))
    decoded=[raw[i*N:(i+1)*N] for i in range(8)]
    # Direct time-domain squared distances, normalized by basis energy and gain.
    err=max(abs(sum((a-b)**2 for a,b in zip(decoded[i],decoded[j]))/(gain*gain*N/2)-h*h) for (i,j),h in zip(combinations(range(8),2),target))
    energy_err=max(abs(sum(x*x for x in row)/(gain*gain*N/2)-24.5) for row in decoded)
    assert err<.01 and energy_err<.01
    nearest=[min(target[k] for k,e in enumerate(combinations(range(8),2)) if i in e) for i in range(8)]
    return dict(name=name,distances=target,histogram=dict(Counter(target)),nearest=nearest,max_squared_distance_error=err,max_energy_error=energy_err,sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
    A=write_bank('families-a',(0,1,2,3)); B=write_bank('families-b',(0,2,1,3))
    assert A['histogram']==B['histogram'] and A['nearest']==B['nearest'] and A['distances']!=B['distances']
    result=dict(status='PASS',native_census=census(),audio=[A,B],changed_pairs=sum(a!=b for a,b in zip(A['distances'],B['distances'])))
    (ROOT/'native-execution.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
