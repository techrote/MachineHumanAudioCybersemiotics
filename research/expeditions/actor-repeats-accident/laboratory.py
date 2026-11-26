"""Synthetic theatrical timing oracle and original stereo score; Python 3.10+."""
from itertools import product
from pathlib import Path
import hashlib, json, math, struct, sys, wave

CUES = (4, 12, 20, 28)
DELAY = 3
DOMAIN = (None, -2, -1, 0, 1, 2)
POLICIES = ('clock', 0, 1, 2)
RATE, TICK, FRAMES = 16000, 2000, 72000


def schedule(shifts, policy):
    if len(shifts) != len(CUES) or any(d not in DOMAIN for d in shifts):
        raise ValueError('outside the declared cue contract')
    if policy not in POLICIES:
        raise ValueError('unknown policy')
    return tuple(t + DELAY if policy == 'clock' else
                 None if d is None else t + DELAY + max(-policy, min(policy, d))
                 for t, d in zip(CUES, shifts))


def costs(shifts, replies):
    absolute = relational = phantom = omitted = 0
    for t, d, r in zip(CUES, shifts, replies):
        if d is None:
            phantom += r is not None
        elif r is None:
            omitted += 1
        else:
            absolute += abs(r - t - DELAY)
            relational += abs(r - t - d - DELAY)
    return absolute, relational, phantom, omitted


def census():
    totals = {str(p): [0] * 4 for p in POLICIES}
    histories = 0
    for ds in product(DOMAIN, repeat=4):
        histories += 1
        expected = sum(abs(d) for d in ds if d is not None)
        for p in POLICIES:
            rs = schedule(ds, p)
            a, r, f, o = costs(ds, rs)
            assert a + r == expected and o == 0
            assert f == (ds.count(None) if p == 'clock' else 0)
            for t, d, q in zip(CUES, ds, rs):
                if d is not None:
                    assert q >= t + d + 1
                    assert min(t + DELAY, t + d + DELAY) <= q <= max(t + DELAY, t + d + DELAY)
                elif p != 'clock':
                    assert q is None
            totals[str(p)] = [x + y for x, y in zip(totals[str(p)], (a, r, f, o))]
    assert histories == 1296
    assert totals == {'clock': [0, 5184, 864, 0], '0': [0, 5184, 0, 0],
                      '1': [3456, 1728, 0, 0], '2': [5184, 0, 0, 0]}
    try:
        schedule((4, 0, 0, 0), 2)
    except ValueError:
        pass
    else:
        raise AssertionError('out-of-contract cue accepted')
    return {'histories': histories, 'policy_evaluations': histories * 4,
            'cost_order': ['absolute_ticks', 'relational_ticks', 'phantom', 'omitted'],
            'totals': totals}


def render(ds, policy):
    channels = [[0] * FRAMES for _ in range(2)]
    for ch, times in enumerate((tuple(None if d is None else t+d for t,d in zip(CUES,ds)), schedule(ds,policy))):
        for i, t in enumerate(times):
            if t is None:
                continue
            f = ((220, 247, 294, 330), (440, 370, 494, 392))[ch][i]
            for j in range(1600):
                channels[ch][t*TICK+j] += round(8500 * math.sin(2*math.pi*f*j/RATE) * math.sin(math.pi*j/1599)**2)
    assert max(abs(v) for c in channels for v in c) <= 8500
    return b''.join(struct.pack('<hh', l, r) for l,r in zip(*channels))


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    result = census()
    nominal = (0,)*4
    altered = (2, None, -2, 1)
    assert len({render(nominal,p) for p in POLICIES}) == 1
    scores = [('rehearsal', nominal, 'clock')] + [(name,altered,p) for name,p in zip(('clock','gated','compromise','responsive'),POLICIES)]
    receipts = {}
    for name, ds, p in scores:
        raw = render(ds,p)
        path = out / (name+'.wav')
        with wave.open(str(path),'wb') as w:
            w.setparams((2,2,RATE,FRAMES,'NONE','not compressed'))
            w.writeframes(raw)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (2,2,RATE,FRAMES)
            assert w.readframes(FRAMES) == raw
        receipts[name] = {'shifts': ds, 'policy': p, 'replies': schedule(ds,p),
                          'costs': costs(ds,schedule(ds,p)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    altered_pcm = [render(altered,p) for p in POLICIES]
    assert len(set(altered_pcm)) == 4
    assert len({b''.join(raw[i:i+2] for i in range(0,len(raw),4)) for raw in altered_pcm}) == 1
    result.update({'python': sys.version.split()[0], 'frames': FRAMES, 'rate': RATE, 'recordings': receipts})
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))
