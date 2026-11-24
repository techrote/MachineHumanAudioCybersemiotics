"""Independent synthetic checks and original stereo preset sonifications."""
from collections import Counter
from itertools import permutations, combinations
from math import comb, sin, pi, cos
from pathlib import Path
import hashlib, json, struct, wave

W4 = [0,1,2,4,8,9,3,5,6,10,12,13,11,7,14,15]
W5 = [0,1,4,2,8,16,17,18,20,24,12,6,3,5,9,10,26,25,21,19,22,28,14,13,7,11,27,23,15,30,29,31]
W6 = [0,1,16,48,32,8,2,34,40,36,33,5,4,6,20,12,24,10,18,3,9,17,49,52,50,56,44,41,42,38,35,7,37,21,13,14,22,28,26,25,11,19,51,54,53,57,60,58,46,45,43,39,15,23,30,27,29,31,47,62,59,55,61,63]

def measure(p):
    assert sorted(p) == list(range(len(p)))
    jump = max((a^b).bit_count() for a,b in zip(p,p[1:]))
    # Independent pair-of-positions enumeration, not inverse-map edge iteration.
    span = max(j-i for i,j in combinations(range(len(p)),2) if (p[i]^p[j]).bit_count()==1)
    return jump,span

def gray_paths(n):
    def visit(p, remaining):
        if not remaining:
            yield p
        else:
            for v in sorted(remaining):
                if (p[-1]^v).bit_count()==1:
                    yield from visit(p+[v], remaining-{v})
    yield from visit([0],set(range(1,2**n)))

def reflected(n):
    return [i^(i>>1) for i in range(2**n)]

def shifted(n):
    g=reflected(n-1);m=len(g)
    return g+[m+v for v in g[-1:]+g[:-1]]

def checks():
    hist={n:dict(sorted(Counter(measure(p)[1] for p in gray_paths(n)).items())) for n in (2,3,4)}
    assert hist=={2:{3:2},3:{5:6,7:12},4:{9:48,11:552,13:2424,15:2688}}
    all3=Counter(measure(p) for p in permutations(range(8)))
    assert sum(all3.values())==40320
    frontier={j:min(b for (a,b) in all3 if a<=j) for j in (1,2,3)}
    assert frontier=={1:5,2:4,3:4}
    witnesses={n:measure(p) for n,p in [(4,W4),(5,W5),(6,W6)]}
    assert witnesses=={4:(2,7),5:(2,13),6:(2,23)}
    families={n:[measure(reflected(n)),measure(shifted(n))] for n in range(2,9)}
    assert all(a==(1,2**n-1) and b==(1,2**(n-1)+1) for n,(a,b) in families.items())
    return {'gray_histogram_start_zero':hist,'all_three_bit_layouts':sum(all3.values()),'all_three_bit_metrics_histogram':{f'{j},{b}':c for (j,b),c in sorted(all3.items())},'three_bit_frontier':frontier,'two_flip_witness_metrics':witnesses,'family_checks':families}

def render(path,left,right):
    assert len(left)==len(right)
    rate,cell=16000,3840
    freqs=[330,440,550,770]
    frames=bytearray(); prev=[left[0],right[0]]
    for k,(a,b) in enumerate(zip(left,right)):
        for i in range(cell):
            t=(k*cell+i)/rate
            blend=(1-cos(pi*min(1,i/160)))/2
            out=[]
            for c,v in enumerate((a,b)):
                y=.10*sin(2*pi*220*t)
                for bit,f in enumerate(freqs):
                    amp=(1-blend)*((prev[c]>>bit)&1)+blend*((v>>bit)&1)
                    y+=.13*amp*sin(2*pi*f*t)
                out.append(round(32767*y))
            frames.extend(struct.pack('<hh',*out))
        prev=[a,b]
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(frames)
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':len(left)*cell/rate,'left':left,'right':right}

def main():
    out=Path(__file__).resolve().parent/'run';out.mkdir(exist_ok=True)
    receipt=checks();g=reflected(4);s=shifted(4)
    a=render(out/'two-locality-objectives.wav',s,W4)
    # Same endpoints; hold after reaching target, rather than time-stretch.
    l=g[:g.index(8)+1];r=W4[:W4.index(8)+1];r+=[8]*(len(l)-len(r))
    b=render(out/'one-bit-neighbour-trip.wav',l,r)
    receipt['audio']=[a,b]
    (out/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
