"""Independent exact-rational oracle for frozen OBS selective transfer, synthetic only.
Run python check_selective_transfer.py; no third-party packages.
The reference fingerprints are from connector-retrieved V8 execution, not native JS CLI.
"""
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
import struct

PAIRS = [(1,1),(2,1),(3,2),(5,3),(8,5),(13,8),(21,13),(34,21),
         (55,34),(89,55),(144,89),(233,144),(377,233),(610,377),(987,610),(1597,987)]
UNIFORM = [F(1,4)]*4
BIASED = [F(1,10)]*3+[F(7,10)]
ONE = [(0,F(1))]
SYM = [(-1,F(1,4)),(0,F(1,2)),(1,F(1,4))]
MODELS = {
    'nominal': (UNIFORM, F(0), ONE),
    'middle-late-1': (UNIFORM, F(0), [(1,F(1))]),
    'middle-early-1': (UNIFORM, F(0), [(-1,F(1))]),
    'middle-symmetric-1': (UNIFORM, F(0), SYM),
    'middle-symmetric-2': (UNIFORM, F(0), [(-2,F(1,4)),(0,F(1,2)),(2,F(1,4))]),
    'late-phase': (UNIFORM, F(1,2), ONE),
    'biased-deletion': (BIASED, F(0), ONE),
    'combined': (BIASED, F(1,2), SYM),
}
REF = {
'receipt|nominal':'46739e3628ee98abc22d9637f32e65d45d5c776f7a98923df742f10529897bc4',
'receipt|middle-late-1':'2e07a7604e61bc0d254f97fa20c2db3144a66421134ae5ceb4ac820975993a1a',
'receipt|middle-early-1':'879f18d9cf04631abf6e9fce767cdc06a0d97265918c0dd4464e58aacc2334b7',
'receipt|middle-symmetric-1':'787934d0ff9478a7087bc902bf72c54bad10ce99df4f68e2867800c174550964',
'receipt|middle-symmetric-2':'ef605a22a1b68b106af2e808b5ae668f473440068be0292f0d3c24d533ee6e40',
'receipt|late-phase':'9e1458937642c17312071de1a3eb202b806156435ab603d9cf46502d4f4eae90',
'receipt|biased-deletion':'7a4d2abd6e94b948c6dc7382fcc036e029ead439294cebbcdd1f242a8e97798a',
'receipt|combined':'7903fa6d3b3c6e6f772a0577708ff85e924b1882706b3f86e5152f7aa4ba78b4',
'fixed|nominal':'f3ec089aa2e968e53b838237e8d1065ca66c0ce9afc220cdfd99ac83304ec5ac',
'fixed|middle-late-1':'e2ba4a4ac861404630489958d6cdf7d8e2a73d85e642d3d83e78b367cd448bea',
'fixed|middle-early-1':'d544376e999ee8b73bdf0ffd59806ab161c85cdc6073d3b20c550017f3de81e7',
'fixed|middle-symmetric-1':'66c2ba702a35889dd8040bac7c6af613176bc975247b65e2c41f0ad6f7bf27ca',
'fixed|middle-symmetric-2':'da86b74c23130b3c0312b3fd4f5f830bba5d3bf83cd5cecbac15fcab9c8c1f0a',
'fixed|late-phase':'34ff17b0e7c5e4ab821b4bf6a8a76ffbe84d94065a33989f99a1a06536c77189',
'fixed|biased-deletion':'afbbe636023899fe8561ab9fa8afd2a008b0c325e56df10c218f9ea0ae5d04b6',
'fixed|combined':'080c797ede9da6dfa42d7b6120a19a7c30d32731c2bcf2387458b8ffdc2c7118',
}
WAVS = [
    (48000,1600,(4800,52265,81600),'a604838ae761beab03b2f5046621a7b2ce5e8b27c839e2be42c7c63826a7afda'),
    (48000,1600,(4800,34135,81600),'71af806f0a1fe2b81d4af0b458dc5533b8a575178367ded3a53fa44b998b5b55'),
    (48000,1600,(4800,34135,81600),'71af806f0a1fe2b81d4af0b458dc5533b8a575178367ded3a53fa44b998b5b55'),
    (8000,800,(800,3245,7200),'6c826ba38b3efd2ab7e4cc33ec544214d82deeab52c4c0beff0d17c613446190'),
    (48000,200,(4800,10733,14400),'a598591f26a86a368e34de1e9e468e5b89bd0a19f23006ddc44e70183f28bab2'),
]


def mass_table(p,q,rate,ms,frame,model):
    prior, phase_start, shifts = model
    motif = [0,p,p+q,2*p+q]
    out = defaultdict(lambda: [F(0)]*4)
    # Integrate each deletion separately, without upstream shared segments.
    for deleted in range(4):
        survivors = motif[:deleted]+motif[deleted+1:]
        start = 0 if frame == 'fixed' else survivors[0]
        span = motif[-1] if frame == 'fixed' else survivors[-1]-start
        exact = [F((t-start)*rate*ms,1000*span)+rate//10 for t in survivors]
        bounds = sorted({phase_start,F(1)} | {1-(x%1) for x in exact if 1-(x%1)>phase_start})
        for lo,hi in zip(bounds,bounds[1:]):
            mid=(lo+hi)/2
            indices=[int(x+mid) for x in exact]
            for shift,weight in shifts:
                a,b,c=indices
                key=(a,b+shift,c)
                assert key[0]<key[1]<key[2]
                out[key][deleted] += (hi-lo)/(1-phase_start)*prior[deleted]*weight
    assert [sum(m[i] for m in out.values()) for i in range(4)]==prior
    return out


def quantize(x):
    return None if x is None else int(x*100_000_000+F(1,2))


def wave(rate,ms,onsets):
    n=rate*(ms+200)//1000
    pcm=[0]*n
    pulse,period=rate//50,rate//500
    for onset in onsets:
        for j in range(pulse):
            carrier=period-4*abs(j%period-period//2)
            a=3000*carrier*min(j,pulse-1-j)
            v=abs(a)//(period*(pulse//2))
            pcm[onset+j]+=v if a>=0 else -v
    payload=struct.pack('<'+'h'*n,*pcm)
    return b'RIFF'+struct.pack('<I',36+len(payload))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,rate,rate*2,2,16)+b'data'+struct.pack('<I',len(payload))+payload


def run():
    signs=defaultdict(list)
    summary=defaultdict(lambda: [F(0)]*5)
    cells=ties=0
    for (p,q),rate,ms,frame in product(PAIRS,[8000,16000,48000],[200,800,1600],['receipt','fixed']):
        nom=mass_table(p,q,rate,ms,frame,MODELS['nominal'])
        for model,spec in MODELS.items():
            k=frame+'|'+model
            observed=mass_table(p,q,rate,ms,frame,spec)
            entries=[]
            for idx,m in sorted(observed.items(),key=lambda z: ','.join(map(str,z[0]))):
                cells+=1
                mass=sum(m)
                oracle=max(m)
                prior=nom.get(idx)
                conf=max(prior)/sum(prior) if prior else None
                if prior and prior.count(max(prior))>1:
                    ties+=1
                entries.append([idx,[quantize(x) for x in m],quantize(conf),quantize(oracle)])
                agg=summary[k]
                agg[0]+=mass if prior is None else 0
                agg[1]+=oracle
                if conf==1:
                    agg[2]+=mass
                    agg[3]+=m[prior.index(max(prior))]
                    agg[4]+=mass-m[prior.index(max(prior))]
            signs[k].append([[p,q,rate,ms],entries])
    digests={k:sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest() for k,v in signs.items()}
    mismatches=[k for k in REF if digests.get(k)!=REF[k]]
    assert not mismatches,(mismatches,digests)
    assert cells==24467 and ties==54
    assert all(len(v)==144 for v in signs.values())
    wav_results=[]
    for rate,ms,onsets,expected in WAVS:
        wav=wave(rate,ms,onsets)
        actual=sha256(wav).hexdigest()
        assert actual==expected,(actual,expected)
        wav_results.append(actual)
    result={k:{'oov':float(v[0]/144),'oracle':float(v[1]/144),'certainty_coverage':float(v[2]/144),
               'certainty_correct':float(v[3]/144),'certainty_wrong':float(v[4]/144),
               'certainty_conditional_error':float(v[4]/v[2]) if v[2] else None} for k,v in summary.items()}
    return {'rows':sum(map(len,signs.values())),'cells':cells,'nominal_ties':ties,'fingerprints':digests,'wav_hashes':wav_results,'summary':result}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
