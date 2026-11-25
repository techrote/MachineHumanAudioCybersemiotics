"""Exhaustive small multiset oracle, explicit erasures, variable stream and audio."""
import itertools as it
import json, math, random, struct, wave, hashlib, sys
from pathlib import Path
from bank import phases, run, erasure_bounds, exact_contract


def counts(M, p, a):
    # Direct membership oracle, independent of the virtual accumulator formula.
    return [sum((v+r)%M >= M-a for v in p) for r in range(M)]


def verify():
    layouts = bounds = explicit = contracts = windows = 0
    for M in range(2, 9):
        for n in range(1, 7):
            best = {(a,e): [0,n] for a in range(M) for e in range(n)}
            for p in it.combinations_with_replacement(range(M),n):
                layouts += 1
                for a in range(M):
                    c = counts(M,p,a)
                    for e in range(n):
                        lo,hi = max(0,min(c)-e),min(n-e,max(c))
                        b = best[a,e]
                        b[0],b[1] = max(b[0],lo),min(b[1],hi)
                        bounds += 1
                        if M <= 5 and n <= 4:
                            vals = [z for sub in it.combinations(p,n-e) for z in counts(M,sub,a)]
                            assert (min(vals),max(vals)) == (lo,hi)
                            explicit += 1
                    if min(c)==max(c):
                        assert n % exact_contract(M,[a]) == 0
                    contracts += 1
            for (a,e), b in best.items():
                c = counts(M,phases(M,n),a)
                observed = max(0,min(c)-e),min(n-e,max(c))
                assert observed == tuple(b) == erasure_bounds(M,n,a,e)
    rng = random.Random(450)
    for M in range(2,32):
        for n in range(1,14):
            A = [rng.randrange(M+1) for _ in range(32)]
            y = list(run(M, phases(M,n), A))
            C = [0]
            for a in A: C.append(C[-1]+a)
            assert [sum(row) for row in y] == [n*b//M-n*a//M for a,b in zip(C,C[1:])]
            for i in range(len(A)):
                for j in range(i+1,len(A)+1):
                    total = sum(sum(row) for row in y[i:j])
                    assert abs(M*total-n*(C[j]-C[i])) < M
                    windows += 1
    # Full aggregation can be exact while adaptive erasures destroy bounded debt.
    y=list(run(8,phases(8,4),[2]*16))
    assert all(sum(row)==1 for row in y)
    assert sum(sum(row)-max(row) for row in y)==0  # erase current carrier
    assert sum(sum(row)-min(row) for row in y)==16 # erase current noncarrier
    # Unequal inputs invalidate common rotation: phases 0,2,4,6; increments 8,0,0,0.
    # Stronger mismatch: same sum as [2,2,2,2], but all carry simultaneously
    # impossible at sum 8 for these phases; zero carries possible using [7,1,0,0].
    assert sum((s+a)//8 for s,a in zip(phases(8,4),[7,1,0,0]))==0
    for args in [(1,2),(8,0),(8,2.0)]:
        try: phases(*args)
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    return dict(layouts=layouts, layout_residue_erasure_cases=bounds, explicit_subset_cases=explicit, constant_contract_checks=contracts, variable_stream_windows=windows)


def render(out):
    out.mkdir(parents=True,exist_ok=True)
    M,n,fs=64,8,16000
    # Exact count 3 every tick in balanced bank, versus 0/8 for aligned phases.
    A=[24]*(fs*2)
    aligned=list(run(M,[0]*n,A)); balanced=list(run(M,phases(M,n),A))
    # Deliberately fixed, known missing lane; compare against 7-lane target.
    fixed=[sum(r[1:]) for r in balanced]
    dynamic=[sum(r)-max(r) for r in balanced]
    def write(name,left,right):
        path=out/name
        pcm=bytearray()
        for a,b in zip(left,right):
            pcm.extend(struct.pack('<hh',round(12000*a),round(12000*b)))
        with wave.open(str(path),'wb') as f:
            f.setparams((2,2,fs,0,'NONE','not compressed')); f.writeframes(pcm)
        return hashlib.sha256(path.read_bytes()).hexdigest()
    # Raw residual centered on target, at a common scale; no independent normalization.
    err=lambda rows:[(sum(r)-3)/8 for r in rows]
    h1=write('aligned-vs-staggered.wav',err(aligned),err(balanced))
    # Render fixed loss as a residual; adaptive loss creates DC, so sonify its
    # cumulative normalized debt via amplitude of a 440 Hz carrier instead.
    def debt_audio(rows):
        debt=0; out=[]
        for i,y in enumerate(rows):
            debt+=8*y-21
            out.append(min(1,abs(debt)/(8*fs))*math.sin(2*math.pi*440*i/fs))
        return out
    h2=write('fixed-vs-moving-loss.wav',debt_audio(fixed),debt_audio(dynamic))
    return dict(M=M,n=n,rate=fs,ticks=len(A),aligned_peak_count_error=max(abs(sum(r)-3) for r in aligned),staggered_peak_count_error=max(abs(sum(r)-3) for r in balanced),fixed_final_debt_numerator=sum(8*y-21 for y in fixed),moving_final_debt_numerator=sum(8*y-21 for y in dynamic),sha256={'aligned-vs-staggered.wav':h1,'fixed-vs-moving-loss.wav':h2})


if __name__=='__main__':
    print(json.dumps({'verification':verify(),'audio':render(Path(sys.argv[1] if len(sys.argv)>1 else 'run'))},indent=2,sort_keys=True))
