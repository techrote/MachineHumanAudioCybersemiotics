"""Exact phase-blind rendezvous census and symbolic audio, stdlib only."""
import itertools as it
import hashlib
import json
import math
import pathlib
import struct
import wave

ROOT = pathlib.Path(__file__).resolve().parent


def rotations(mask, n):
    full = (1 << n) - 1
    return [((mask << t) | (mask >> (n-t))) & full for t in range(n)]


def literal(n, a, mask, emax):
    """All relative phases; maximum of e+1 consecutive inter-hit gaps."""
    minimum = a
    worst = [0] * (emax+1)
    for t in range(n):
        hit = [i for i in range(a) if (mask >> ((t+i) % n)) & 1]
        k = len(hit)
        minimum = min(minimum, k)
        doubled = hit + [x+n for x in hit]
        for e in range(emax+1):
            g = n+1 if k <= e else max(doubled[i+e+1]-hit[i] for i in range(k))
            worst[e] = max(worst[e], g)
    return minimum, worst


def shape_masks(a, s):
    return [((1 << u)-1) | (((1 << (s-u))-1) << (a-s+u)) for u in range(s+1)]


def certificate(n, a, mask, emax):
    """No explicit hit lists or time-gap evaluation."""
    rotated = rotations(mask, n)
    out = [n+1] * (emax+1)
    for s in range(1, a+1):
        count = min((m & shape).bit_count() for shape in shape_masks(a,s) for m in rotated)
        for e in range(emax+1):
            if out[e] == n+1 and count >= e+1:
                out[e] = n-a+s
    return out


def independent(n, a, s, mask):
    holes = ((1 << n)-1) ^ mask
    rot = rotations(holes, n)
    return all(not (holes & rot[d]) for d in set(range(1,s)) | set(range(a-s+1,a)))


def explicit_deletions(n,a,mask,e):
    worst=0
    for t in range(n):
        hit=[i for i in range(a) if (mask >> ((t+i)%n)) & 1]
        if len(hit)<=e: return n+1
        for erased in it.combinations(hit,e):
            remain=[i for i in hit if i not in erased]
            worst=max(worst,max(y-x for x,y in zip(remain,remain[1:]+[remain[0]+n])))
    return worst


def balanced(n,b):
    return sum(1<<i for i in range(n) if ((i+1)*b)//n != (i*b)//n)


def census():
    counts=dict(mask_window_profiles=0, fault_certificates=0, graph_certificates=0,
                explicit_deletion_profiles=0, duty_budget_profiles=0, balanced_latency_failures=0,
                divisible_density_checks=0, nondivisible_density_checks=0, special_density_checks=0,
                joint_optimum_failures=0)
    failures=[]
    for n in range(2,12):
        for a in range(1,n+1):
            emax=min(2,a-1)
            best_count=[-1]*(n+1)
            best_gap=[[n+1]*(emax+1) for _ in range(n+1)]
            jointly=[False]*(n+1)
            profiles=[]
            for mask in range(1<<n):
                b=mask.bit_count()
                m,g=literal(n,a,mask,emax)
                assert g==certificate(n,a,mask,emax), (n,a,mask,g)
                counts['mask_window_profiles']+=1
                counts['fault_certificates']+=emax+1
                assert m <= a*b//n
                for e in range(emax+1):
                    assert (g[e] == n+1) == (m <= e)
                    assert g[e] >= n-a+e+1
                    assert (g[e] == n-a+e+1) == (b==n)
                    if e+2<=a:
                        assert (g[e] <= n-a+e+2) == independent(n,a,e+2,mask)
                        counts['graph_certificates']+=1
                    if n<=7:
                        assert g[e]==explicit_deletions(n,a,mask,e)
                        counts['explicit_deletion_profiles']+=1
                    best_gap[b][e]=min(best_gap[b][e],g[e])
                best_count[b]=max(best_count[b],m)
                profiles.append((b,m,g[0]))
            for b,m,g in profiles:
                if m==best_count[b] and g==best_gap[b][0]: jointly[b]=True
            for b in range(n+1):
                m,g=literal(n,a,balanced(n,b),emax)
                assert m==best_count[b]==a*b//n
                counts['duty_budget_profiles']+=1
                if not jointly[b]: counts['joint_optimum_failures']+=1
                if g[0]>best_gap[b][0]:
                    counts['balanced_latency_failures']+=1
                    if len(failures)<12: failures.append([n,a,b,g[0],best_gap[b][0]])
            for e in range(emax+1):
                s=e+2
                if s>a: continue
                least=min(b for b in range(n+1) if best_gap[b][e]<=n-a+s)
                if n%s==0 and a%s==0:
                    assert least==n-n//s
                    counts['divisible_density_checks']+=1
                if n%s==0 and a%s!=0:
                    assert least>n-n//s
                    counts['nondivisible_density_checks']+=1
                if e==0 and a==3:
                    assert least==n-n//3
                    counts['special_density_checks']+=1
                if e==0 and a==4:
                    assert least==n-(n//2 if n%2==0 else (n-3)//2)
                    counts['special_density_checks']+=1
    return counts, failures


def audio(name, mask, phase):
    """Stereo: left requested pulses; right actual idealized receipts."""
    n,a=6,4
    hits=[i for i in range(a) if mask>>((phase+i)%n)&1]
    frames=bytearray(); rate=8000; slot=1000
    for t in range(n*4):
        for i in range(slot):
            env=math.sin(math.pi*i/(slot-1))**2
            left=round(9000*env*math.sin(2*math.pi*360*i/rate)) if t%n<a else 0
            right=round(9000*env*math.sin(2*math.pi*600*i/rate)) if t%n in hits else 0
            frames.extend(struct.pack('<hh',left,right))
    dest=ROOT/'audio'/f'{name}.wav';dest.parent.mkdir(exist_ok=True)
    with wave.open(str(dest),'wb') as f:
        f.setparams((2,2,rate,0,'NONE','not compressed'));f.writeframes(frames)
    with wave.open(str(dest),'rb') as f: assert f.readframes(f.getnframes())==frames
    return {'file':dest.name,'phase':phase,'hits':hits,'gap':max(y-x for x,y in zip(hits,hits[1:]+[hits[0]+n])),
            'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}


def main():
    counts, failures=census()
    # Rotation-equivalent to the mechanical word, versus unequal spacing.
    masks=[sum(1<<i for i in ids) for ids in [(0,1,3,4),(1,3,4,5)]]
    examples=[literal(6,4,m,1) for m in masks]
    assert examples==[(2,[5,6]),(2,[4,6])],examples
    receipts=[audio('balanced-phase-2',masks[0],2),audio('uneven-phase-2',masks[1],2),
              audio('balanced-phase-0',masks[0],0),audio('uneven-phase-0',masks[1],0)]
    print(json.dumps({'domain':'N=2..11, a=1..N, all masks, e=0..min(2,a-1)',
                      'counts':counts,'first_balanced_failures':failures,'six_slot_examples':examples,'audio':receipts},indent=2,sort_keys=True))

if __name__=='__main__': main()
