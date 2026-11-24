"""Exact finite averaging circuits and omitted-gate fingerprints (stdlib only)."""
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import hashlib, json, math, struct, wave


def matchings(vertices, edges):
    if not vertices:
        yield ()
        return
    a, *rest = vertices
    for b in rest:
        if (a, b) in edges:
            for tail in matchings([v for v in rest if v != b], edges):
                yield ((a, b),) + tail


def merge(supports, matching):
    out = list(supports)
    for a, b in matching:
        if supports[a] & supports[b]:
            return None
        out[a] = out[b] = supports[a] | supports[b]
    return tuple(out)


def compile_graph(n, edges):
    """Exact existence test for k=log2(n) perfect-matching rounds, n<=8.

    None means no minimum-round circuit, not no finite-time circuit.
    """
    if n not in (2, 4, 8):
        raise ValueError('graph search requires n=2,4,8')
    edges = {tuple(sorted(e)) for e in edges}
    if any(len(e) != 2 or not 0 <= e[0] < e[1] < n for e in edges):
        raise ValueError('invalid edge')
    ms = tuple(matchings(list(range(n)), edges))
    @lru_cache(None)
    def search(s):
        if all(v == (1 << n)-1 for v in s):
            return ()
        for m in ms:
            nxt = merge(s, m)
            if nxt is not None:
                tail = search(nxt)
                if tail is not None:
                    return (m,) + tail
        return None
    return search(tuple(1 << i for i in range(n)))


def butterfly(n):
    if n < 2 or n & (n-1):
        raise ValueError('power of two required')
    return tuple(tuple((i, i ^ (1 << l)) for i in range(n)
                       if not i & (1 << l)) for l in range(n.bit_length()-1))


def validate(n, rounds):
    if n < 2 or n & (n-1) or len(rounds) != n.bit_length()-1:
        raise ValueError('not minimum-round geometry')
    s = tuple(1 << i for i in range(n))
    for m in rounds:
        if any(len(e) != 2 for e in m) or sorted(v for e in m for v in e) != list(range(n)):
            raise ValueError('not a perfect matching')
        s = merge(s, m)
        if s is None:
            raise ValueError('overlapping information cones')
    if any(v != (1 << n)-1 for v in s):
        raise ValueError('not exact consensus')


def transfer(n, rounds, omitted=()):
    """Integer matrix equal to 2**len(rounds) times actual transfer."""
    omitted = set(omitted)
    if not omitted <= {(l,j) for l,m in enumerate(rounds) for j in range(len(m))}:
        raise ValueError('unknown gate')
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for l, m in enumerate(rounds):
        for j, (a,b) in enumerate(m):
            if (l,j) in omitted:
                rows[a] = [2*v for v in rows[a]]
                rows[b] = [2*v for v in rows[b]]
            else:
                rows[a] = rows[b] = [x+y for x,y in zip(rows[a],rows[b])]
    return rows


def signature(n, rounds, l, j):
    """Return input/output signed masks; outer product / n is exact error."""
    validate(n, rounds)
    if not 0 <= l < len(rounds) or not 0 <= j < len(rounds[l]):
        raise ValueError('unknown gate')
    a,b = rounds[l][j]
    before = transfer(n, rounds[:l])
    after = transfer(n, tuple(reversed(rounds[l+1:])))
    return ([x-y for x,y in zip(before[a],before[b])],
            [x-y for x,y in zip(after[a],after[b])])


def diagnostic_probe(n, rounds):
    """Bounded integer input distinguishing no-fault and every single fault."""
    signatures = [signature(n, rounds,l,j) for l,m in enumerate(rounds)
                  for j in range(len(m))]
    forms = {tuple(u) for u,v in signatures}
    for (u,v),(w,z) in combinations(signatures,2):
        if v == z or v == [-a for a in z]:
            sign = 1 if v == z else -1
            f = tuple(a-sign*b for a,b in zip(u,w))
            if not any(f):
                raise AssertionError('indistinguishable fault matrices')
            forms.add(f)
    buckets = [[] for _ in range(n)]
    for f in forms:
        buckets[max(i for i,a in enumerate(f) if a)].append(f)
    x = []
    for i,fs in enumerate(buckets):
        forbidden = { -sum(a*b for a,b in zip(f,x))//f[i]
                      for f in fs if sum(a*b for a,b in zip(f,x)) % f[i] == 0 }
        x.append(next(a for a in range(len(fs)+1) if a not in forbidden))
    residuals = {tuple([0]*n)}
    for u,v in signatures:
        y = tuple(a*sum(b*c for b,c in zip(u,x)) for a in v)
        assert y not in residuals
        residuals.add(y)
    return x


def audit(n, rounds):
    validate(n, rounds)
    assert transfer(n, rounds) == [[1]*n for _ in range(n)]
    count = 0
    for l,m in enumerate(rounds):
        for j in range(len(m)):
            u,v = signature(n, rounds, l,j)
            err = [[x-1 for x in row] for row in transfer(n,rounds,[(l,j)])]
            assert err == [[b*a for a in u] for b in v]
            assert sum(x*x for row in err for x in row) == 2*n
            assert sum(x != 0 for x in u) == 2**(l+1)
            assert sum(x != 0 for x in v) == 2**(len(rounds)-l)
            assert sum(u) == sum(v) == 0
            count += 1
    return count


def nonbipartite(edges, n):
    colors = {}
    for root in range(n):
        if root in colors: continue
        colors[root]=0; stack=[root]
        while stack:
            a=stack.pop()
            for e in edges:
                if a not in e: continue
                b=e[1] if a==e[0] else e[0]
                if b in colors:
                    if colors[b]==colors[a]: return True
                else:
                    colors[b]=1-colors[a]; stack.append(b)
    return False


def census():
    n=8
    all_edges=set(combinations(range(n),2))
    ms=tuple(matchings(list(range(n)), all_edges))
    first=butterfly(n)[0]
    s=merge(tuple(1 << i for i in range(n)), first)
    count=checks=odd_graphs=probe_max=0
    witness=None
    for second in ms:
        t=merge(s,second)
        if t is None: continue
        for third in ms:
            end=merge(t,third)
            if end is None: continue
            rounds=(first,second,third)
            checks+=audit(n,rounds)
            probe_max=max(probe_max,max(diagnostic_probe(n,rounds)))
            count+=1
            edges=set(e for m in rounds for e in m)
            if nonbipartite(edges,n):
                odd_graphs+=1
                if witness is None: witness=rounds
    assert witness is not None
    assert compile_graph(n,{e for m in witness for e in m}) is not None
    # Independent four-node graph oracle: a C4 is necessary and sufficient.
    e4=list(combinations(range(4),2)); yes=0
    for bits in range(1<<len(e4)):
        edges={e for j,e in enumerate(e4) if bits>>j&1}
        got=compile_graph(4,edges)
        expected=any(all(sum(v in e for e in cycle)==2 for v in range(4))
                     for cycle in combinations(edges,4))
        assert (got is not None)==expected
        if got is not None: yes+=1; audit(4,got)
    for n in (2,4,8,16,32,64): audit(n,butterfly(n))
    assert compile_graph(8,{(i,i+1) for i in range(7)}) is None
    # Cross-stage fault interaction: independent single fault matrices do not add.
    r=butterfly(4); a=(0,0); b=(1,0)
    A=transfer(4,r,[a]); B=transfer(4,r,[b]); AB=transfer(4,r,[a,b])
    cross=[[AB[i][j]-A[i][j]-B[i][j]+1 for j in range(4)] for i in range(4)]
    assert any(x for row in cross for x in row)
    return dict(fixed_first_schedules=count, labelled_schedules=count*len(ms),
                single_fault_checks=checks, nonbipartite_schedules=odd_graphs,
                nonbipartite_witness=witness, probe_max_coordinate=probe_max,
                butterfly16_probe=diagnostic_probe(16,butterfly(16)),
                four_node_graphs=64, four_node_feasible=yes,
                two_fault_interaction_numerator=cross,
                butterfly_sizes=[2,4,8,16,32,64])


def render(directory):
    """Stereo residual sonification. One carrier per input/output coordinate."""
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    n=16; r=butterfly(n); sr=16000; frames=sr*2
    # Probe using all basis vectors in turn; one output carrier per node.
    matrices=[transfer(n,r,[(l,0)]) for l in (0,3)]
    def sample(matrix,t):
        block=t//2000; i=block%n; pos=t%2000
        envelope=math.sin(math.pi*pos/2000)**2
        return envelope*sum((matrix[j][i]-1)*math.sin(2*math.pi*(220+70*j)*t/sr)
                            for j in range(n))/n/2
    pcm=bytearray()
    for t in range(frames):
        vals=[round(32767*sample(m,t)) for m in matrices]
        assert all(-32768<=v<=32767 for v in vals)
        pcm.extend(struct.pack('<hh',*vals))
    path=directory/'early-vs-late.wav'
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,sr,frames,'NONE','not compressed')); f.writeframes(pcm)
    return dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                frames=frames, sample_rate=sr, channels=2)


if __name__=='__main__':
    import sys
    dest=Path(sys.argv[1] if len(sys.argv)>1 else 'run')
    print(json.dumps(dict(census=census(),audio=render(dest)),indent=2))
