"""Independent exact first-passage and bounded-release witness; synthetic audio."""
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
import hashlib, json, math, struct, wave

OUT = Path(__file__).resolve().parent
H = 60

def counts(a, b, p):
    # Integer weighted path counts, not normalized transition recursion.
    u, d = p.numerator, p.denominator - p.numerator
    v = {0: 1}
    near, far = [F(0)], [F(0)]
    for t in range(1, H+1):
        nxt = Counter()
        for x, n in v.items():
            nxt[x+1] += n*u
            nxt[x-1] += n*d
        den = p.denominator**t
        near.append(F(nxt.pop(a, 0), den))
        far.append(F(nxt.pop(-b, 0), den))
        v = nxt
        assert sum(near)+sum(far)+F(sum(v.values()), den) == 1
    r = (1-p)/p
    h = F(b, a+b) if r == 1 else (1-r**b)/(1-r**(a+b))
    return h, [x/h for x in near], [x/(1-h) for x in far]

checks = 0
for j in range(1, 40):
    p = F(j, 40)
    _, near, far = counts(1, 3, p)
    w = p*(1-p)
    out = [F(0)]*(H+1)
    for t, mass in enumerate(near):
        prob2 = 1-w if t == 1 else 1-2*w
        if t+2 <= H:
            out[t+2] += mass*prob2
        if t+4 <= H:
            out[t+4] += mass*(1-prob2)
    assert out == far
    checks += H+1
    assert near[1] > sum(far[:5])
    checks += 1

# Deterministic quantile-score illustration, NOT independent statistical samples.
p = F(3,4)
_, near, far = counts(1,3,p)
def quantile(pmf, u):
    total = F(0)
    for t, mass in enumerate(pmf):
        total += mass
        if total >= u:
            return t
    raise ValueError('quantile outside retained prefix')
quantiles = [F(2*j+1,64) for j in range(32)]
A = [quantile(near,u) for u in quantiles]
B = [quantile(far,u) for u in quantiles]
assert all(0 <= t-s <= 4 for s,t in zip(A,B))
rate, tick, pulse = 8000, 320, 80
slot = (max(B)+2)*tick
shape = [int(12000*math.sin(2*math.pi*600*i/rate)*math.sin(math.pi*i/(pulse-1))**2) for i in range(pulse)]
def render(name, times):
    pcm = bytearray()
    for t in times:
        for i in range(slot):
            left = shape[i] if i < pulse else 0
            right = shape[i-t*tick] if 0 <= i-t*tick < pulse else 0
            pcm += struct.pack('<hh',left,right)
    path = OUT/name
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,rate,0,'NONE','not compressed'))
        f.writeframes(pcm)
    with wave.open(str(path),'rb') as f:
        samples = list(struct.iter_unpack('<hh',f.readframes(f.getnframes())))
    decoded=[]
    for k in range(len(times)):
        block = samples[k*slot:(k+1)*slot]
        assert next(i for i,(l,r) in enumerate(block) if l) < pulse
        onset = next(i for i,(l,r) in enumerate(block) if r)
        decoded.append(onset//tick)
    assert decoded == times
    return hashlib.sha256(path.read_bytes()).hexdigest()
files = {name:render(name,times) for name,times in [('near-raw.wav',A),('far-raw.wav',B),('near-padded.wav',B),('far-padded.wav',B)]}
assert files['near-padded.wav'] == files['far-padded.wav'] == files['far-raw.wav']
assert files['near-raw.wav'] != files['far-raw.wav']
receipt = {'status':'PASS','independent_formulation':'integer weighted path counts and explicit adaptive kernel','profiles':39,'kernel_and_cap_checks':checks,'horizon':H,'quantile_episodes_per_file':32,'decoded_episodes':128,'tick_ms':40,'slot_frames':slot,'near_times':A,'far_times':B,'max_score_delay':max(t-s for s,t in zip(A,B)),'sha256':files}
(OUT/'native-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
