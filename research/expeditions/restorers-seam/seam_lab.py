"""The Restorer's Seam: synthetic, discrete restoration and original PCM."""
from itertools import product
from pathlib import Path
from hashlib import sha256
import argparse
import json
import struct
import wave

ALPHABET = (0, 1, 2)
RATE = 16000
FRAMES = 4000
OBS = (1, None, None, None, 1)


def compatible(observed, step_cap=None):
    """All completions of the stated grammar; None is missing, never zero."""
    if any(x is not None and x not in ALPHABET for x in observed):
        raise ValueError('symbol outside alphabet')
    if step_cap is not None and step_cap < 0:
        raise ValueError('negative step cap')
    return [s for s in product(*(ALPHABET if x is None else (x,) for x in observed))
            if step_cap is None or all(abs(a-b) <= step_cap for a,b in zip(s,s[1:]))]


def energy(s):
    return sum((a-b)**2 for a,b in zip(s,s[1:]))


def distance(a,b,loss):
    if len(a) != len(b):
        raise ValueError('length mismatch')
    if loss == 'hamming':
        return sum(x != y for x,y in zip(a,b))
    if loss == 'squared':
        return sum((x-y)**2 for x,y in zip(a,b))
    raise ValueError('unknown loss')


def analyze(observed,step_cap=None):
    c = compatible(observed,step_cap)
    if not c:
        return {'count':0,'status':'inconsistent','smooth':[], 'minimax':{}}
    e = min(map(energy,c))
    m = {}
    for loss in ('hamming','squared'):
        risk = [(max(distance(x,y,loss) for y in c),x) for x in c]
        best = min(r for r,x in risk)
        m[loss] = {'risk':best,'winners':[x for r,x in risk if r==best]}
    return {'count':len(c),'status':'identified' if len(c)==1 else 'ambiguous',
            'smooth_energy':e,'smooth':[s for s in c if energy(s)==e], 'minimax':m}


def sidecar(observed, candidate, step_cap=None):
    if tuple(candidate) not in compatible(observed,step_cap):
        raise ValueError('incompatible completion')
    return [{'event':i,'symbol':v,'provenance':'conjectural' if x is None else 'observed'}
            for i,(x,v) in enumerate(zip(observed,candidate))]


def tone(symbol, i):
    period = (100,80,64)[symbol]
    phase = i % period
    triangle = 4*min(phase,period-phase)-period
    env = min(i, FRAMES-1-i, 240)
    return triangle*6500*env//(period*240)


def noise(i, event):
    # Fixed arithmetic pseudo-noise, not a calibrated perceptual masker.
    v = ((i+1+event*FRAMES)*1103515245+12345) & 0x7fffffff
    return ((v >> 12)%12001-6000)*min(i,FRAMES-1-i,240)//240


def pcm(seq, mode='normal'):
    data = bytearray()
    for e,s in enumerate(seq):
        for i in range(FRAMES):
            x = (noise(i,e) if mode=='noise' else 0) if s is None else tone(s,i)
            y = x if mode!='audit' else (x if OBS[e] is None else 0)
            data.extend(struct.pack('<hh',x,y))
    return bytes(data)


def render(out):
    out.mkdir(parents=True,exist_ok=True)
    a=(1,1,1,1,1); b=(1,0,2,0,1)
    files={ '01_gap':pcm(OBS), '02_noise_placeholder':pcm(OBS,'noise'),
            '03_smooth_conjecture':pcm(a), '04_rival_conjecture':pcm(b),
            '05_audit_insert_only_right':pcm(a,'audit') }
    receipt={'observed':OBS,'rate':RATE,'frames_per_event':FRAMES,
             'cases':{'unrestricted':analyze(OBS),'unique_under_cap':analyze((0,None,2),1),
                      'no_loss':analyze((0,1,2)),'inconsistent':analyze((0,None,2),0)},
             'sidecars':{'smooth':sidecar(OBS,a),'rival':sidecar(OBS,b)},'audio':{}}
    for name,data in files.items():
        p=out/(name+'.wav')
        with wave.open(str(p),'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(data)
        receipt['audio'][p.name]={'sha256':sha256(p.read_bytes()).hexdigest(),'frames':len(data)//4}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    render(p.parse_args().out)
