"""Synthetic rendezvous model and original stereo pulse score. Python 3.11+ stdlib."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib, json, math, struct, wave


def trajectory(q, bits, distance=F(120)):
    a, b = F(0), distance
    states = [(a, b)]
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError('binary correction allocation required')
        step = (1-q)*(b-a)
        if bit:
            a += step
        else:
            b -= step
        states.append((a, b))
    return states


def union_length(intervals):
    left, right = sorted(intervals)[0]
    length = F(0)
    for lo, hi in sorted(intervals)[1:]:
        if lo > right:
            length += right-left
            left, right = lo, hi
        else:
            right = max(right, hi)
    return length+right-left


def verify():
    checked = 0
    coverage = []
    for q in (F(1,4), F(1,3), F(2,5), F(1,2), F(3,5), F(2,3), F(3,4)):
        for n in range(11):
            intervals = []
            for bits in product((0,1), repeat=n):
                states = trajectory(q, bits, F(1))
                a,b = states[-1]
                direct = (1-q)*sum((bit*q**i for i,bit in enumerate(bits)), F(0))
                assert a == direct and b-a == q**n and 0 <= a <= b <= 1
                assert all(y-x == q**i for i,(x,y) in enumerate(states))
                intervals.append((a,b))
                checked += 1
            width = union_length(intervals)
            assert width == min(F(1),(2*q)**n)
            if q < F(1,2):
                ordered = sorted(intervals)
                assert all(x[1] < y[0] for x,y in zip(ordered,ordered[1:]))
                assert len(set(intervals)) == 2**n
            coverage.append({'q':str(q),'depth':n,'coverage':str(width)})
    # Continuous equal allocation preserves midpoint; same difference sequence.
    for q in (F(1,3), F(1,2), F(2,3)):
        a,b = F(0),F(1)
        for n in range(1,21):
            step = (1-q)*(b-a)/2
            a,b = a+step,b-step
            assert a+b == 1 and b-a == q**n
        # First turn rules out exact midpoint for q<1/2.
        assert (q < F(1,2)) == (q < F(1,2) < 1-q)
    return {'binary_histories_checked':checked, 'coverage_cases':len(coverage), 'coverage':coverage}


def render(path, q, bits):
    rate, period, dur = 24000, 0.45, 0.08
    states = trajectory(q, bits)
    frames = [[0,0] for _ in range(round(rate*(period*len(states)+0.2)))]
    onsets = []
    for i,(a,b) in enumerate(states):
        starts = [round(rate*(i*period+float(x)/1000)) for x in (a,b)]
        onsets.append(starts)
        for ch,start in enumerate(starts):
            for k in range(round(rate*dur)):
                t=k/rate
                env=math.sin(math.pi*k/(round(rate*dur)-1))**2
                frames[start+k][ch]=round(9000*env*math.sin(2*math.pi*(440 if ch==0 else 660)*t))
    pcm=b''.join(struct.pack('<hh',*f) for f in frames)
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,rate,len(frames),'NONE','not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path),'rb') as w:
        assert w.getnchannels()==2 and w.getsampwidth()==2 and w.getframerate()==rate
        assert w.readframes(w.getnframes())==pcm
    return {'q':str(q),'bits':bits,'onsets_samples':onsets,'final_offsets_ms':[str(v) for v in states[-1]],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    out=Path(__file__).parent
    report=verify()
    cases=[('yield-left',F(1,3),[1]*8),('yield-right',F(1,3),[0]*8),('alternating-fast',F(1,3),[0,1]*4),('alternating-slow',F(2,3),[0,1]*4)]
    report['audio']=[render(out/(name+'.wav'),q,bits) for name,q,bits in cases]
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in report.items() if k!='coverage'})


if __name__=='__main__':
    main()
