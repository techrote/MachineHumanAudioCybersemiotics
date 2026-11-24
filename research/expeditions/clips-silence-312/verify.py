"""Independent direct-tree oracle, exhaustive corner census and audio rendering."""
import hashlib
import itertools
import json
import math
import struct
import wave
from collections import Counter
from functools import lru_cache
from pathlib import Path
from mixer import optimal, endpoints, evaluate, balanced_family, BudgetExceeded


@lru_cache(None)
def trees(labels):
    if len(labels) == 1:
        return labels
    # Independent enumeration by combinations rather than bitmask submasks.
    out = []
    for k in range(len(labels)-1):
        for extra in itertools.combinations(labels[1:], k):
            left = (labels[0],) + extra
            right = tuple(j for j in labels if j not in left)
            out.extend((a, b) for a in trees(left) for b in trees(right))
    return tuple(out)


def direct(v, t, cap=None):
    if isinstance(t, int):
        return v[t], max(abs(x) for x in v[t])
    a, pa = direct(v, t[0], cap); b, pb = direct(v, t[1], cap)
    z = tuple(x+y for x, y in zip(a, b))
    peak = max(pa, pb, *(abs(x) for x in z))
    if cap is not None:
        z = tuple(min(cap, max(-cap, x)) for x in z)
    return z, peak


def verify():
    corners = list(itertools.product((-1, 1), repeat=3))
    census = []
    for n in range(2, 7):
        counts = Counter()
        examples = {}
        for ids in itertools.combinations_with_replacement(range(8), n):
            v = tuple(corners[i] for i in ids)
            target = tuple(map(sum, zip(*v)))
            if max(map(abs, target)) > 1:
                continue
            counts['final_fits'] += 1
            p, t = optimal(v); s, order = optimal(v, True)
            assert evaluate(v, t)[:2] == (target, p)
            assert evaluate(v, order)[:2] == (target, s)
            h = endpoints(v, 1)
            assert sum(h.values()) == math.prod(range(1, 2*n-2, 2))
            # Oracle deliberately enumerates every tree for the entire selected population.
            all_t = trees(tuple(range(n)))
            hh = Counter(); pp = math.inf
            for tt in all_t:
                pp = min(pp, direct(v, tt)[1])
                hh[direct(v, tt, 1)[0]] += 1
            assert h == hh and p == pp
            brute_seq = math.inf
            for perm in itertools.permutations(range(n)):
                prefix = [0]*3; peak = 0
                for i in perm:
                    prefix = [x+y for x,y in zip(prefix, v[i])]
                    peak = max(peak, *map(abs, prefix))
                brute_seq = min(brute_seq, peak)
            assert s == brute_seq
            counts['tree_oracle_replays'] += len(all_t)
            counts['sequence_oracle_replays'] += math.factorial(n)
            counts['clip_free_exists'] += p <= 1
            counts['some_correct_endpoint'] += target in h
            counts['all_correct_endpoints'] += len(h) == 1 and target in h
            counts['hidden_clip_possible'] += p > 1 and target in h
            counts['tree_beats_sequence'] += p < s
            if p > 1 and target in h and len(h) > 1:
                examples.setdefault('hidden_clip', {'vectors': v, 'target': target, 'peak': p, 'endpoints': sorted(h.items())})
            if target not in h:
                examples.setdefault('irreparable', {'vectors': v, 'target': target, 'peak': p, 'endpoints': sorted(h.items())})
        census.append({'n': n, **counts, 'examples': examples})
    family = []
    for n in range(2, 13, 2):
        v = balanced_family(n)
        p, t = optimal(v); s, order = optimal(v, True)
        assert p == (n+2)//3 and s == n//2
        assert evaluate(v, t)[1] == p and evaluate(v, order)[1] == s
        family.append({'n':n, 'coordinates':len(v[0]), 'tree_peak':p, 'sequential_peak':s})
    # Falsifiers and refusals.
    v = ((1,1,-1),(1,-1,1),(-1,1,1))
    assert optimal(v)[0] == 2 and (1,1,1) not in endpoints(v,1)
    assert all(optimal(tuple((row[j],) for row in v))[0] == 1 for j in range(3))
    v = balanced_family(4)
    assert evaluate(v, ((0,1),(2,3)), 1) == ((0,0,0),2,2)
    assert evaluate(v, (((0,1),2),3), 1)[0] != (0,0,0)
    assert optimal(((1,),(-1,),(1,),(-1,)))[0] == 1
    try:
        endpoints(v,1,pair_budget=1)
    except BudgetExceeded:
        pass
    else:
        raise AssertionError('budget refusal missing')
    for fn in (lambda: optimal(((1.0,),)), lambda: evaluate(v, ((0,1),(1,3))), lambda: endpoints(v,0)):
        try:
            fn()
        except ValueError:
            pass
        else:
            raise AssertionError('input refusal missing')
    return {'classification':'synthetic exact finite population', 'census':census, 'balanced_family':family, 'negative_controls':'passed'}


def render(out):
    rate, cap, block = 16000, 12000, 6400
    def make(name, v, left, right):
        data = bytearray(); peaks = [0,0]; nonzero = [0,0]; differences = 0
        def sample(vals, tree, saturate):
            if isinstance(tree,int): return vals[tree]
            x = sample(vals,tree[0],saturate)+sample(vals,tree[1],saturate)
            return max(-cap,min(cap,x)) if saturate else x
        for j in range(len(v[0])):
            for t in range(block):
                env = min(1,t/160,(block-1-t)/160)
                carrier = round(cap*env*math.sin(2*math.pi*(220+110*j)*t/rate))
                vals = [carrier*row[j] for row in v]
                l = sample(vals,left[0],left[1]); r = sample(vals,right[0],right[1])
                assert -32768 <= l <= 32767 and -32768 <= r <= 32767
                peaks = [max(peaks[0],abs(l)),max(peaks[1],abs(r))]
                nonzero = [nonzero[0]+int(l!=0),nonzero[1]+int(r!=0)]
                differences += l != r
                data.extend(struct.pack('<hh',l,r))
        path = out / name
        with wave.open(str(path),'wb') as w:
            w.setparams((2,2,rate,0,'NONE','not compressed')); w.writeframes(data)
        return {'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rate':rate,'frames':len(data)//4,'peak_pcm':peaks,'nonzero_samples':nonzero,'different_samples':differences,'vectors':v,'left':left,'right':right,'cap':cap}
    a = make('three-voices.wav',((1,1,-1),(1,-1,1),(-1,1,1)),(((0,1),2),False),(((0,1),2),True))
    b = make('silence-that-clips.wav',balanced_family(4),(((0,1),(2,3)),True),((((0,1),2),3),True))
    assert a['different_samples'] > 0 and b['nonzero_samples'][0] == 0 and b['nonzero_samples'][1] > 0
    return [a,b]


if __name__ == '__main__':
    out = Path(__file__).parent/'run'; out.mkdir(exist_ok=True)
    result = verify(); result['audio'] = render(out)
    (out/'results.synthetic.txt').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
