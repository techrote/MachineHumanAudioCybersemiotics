"""Original synthetic score; stdlib only. Run: python render.py [output_dir]."""
import hashlib
import json
import math
import struct
import sys
import wave
from pathlib import Path

RATE, TICK = 24000, 7200
FINAL = (330, 392, 294, 220)
A, B = (220, 277), (440, 349)


def tone(freq, amp=0.22, partial=0.15):
    if not freq:
        return [0] * TICK
    return [round(32767 * amp * math.sin(math.pi * i / (TICK-1))**2 *
                  (math.sin(2*math.pi*freq*i/RATE) +
                   partial*math.sin(4*math.pi*freq*i/RATE)))
            for i in range(TICK)]


def lane(notes, amp=0.22, partial=0.15):
    return [sample for f in notes for sample in tone(f, amp, partial)]


def render():
    # Same time grid and canonical left-channel ending in every condition.
    # Mark is an arbitrary convention, not a perceptual claim.
    scenarios = {
        '01-clean': ((0, 0, 0, 0), (0,)*8),
        '02-interrupt': (A + (0, 0), (0,)*8),
        '03-repair': (A + (0, 0), (0, 0, 880, 0) + (0,)*4),
        '04-revision-A': (A + (0, 0), (0, 0, 880, 0) + A + A),
        '05-revision-B': (B + (0, 0), (0, 0, 880, 0) + B + B),
    }
    out = {}
    for name, (prefix, right) in scenarios.items():
        l = lane(prefix + FINAL)
        r = lane(right, 0.13, 0.35)
        assert len(l) == len(r) == 8*TICK
        assert max(map(abs, l+r)) < 32767
        out[name] = struct.pack('<'+'h'*(2*len(l)),
                                *(x for pair in zip(l,r) for x in pair))
    return out


def qualify(data):
    assert data == render()
    channels = {}
    for name, raw in data.items():
        samples = struct.unpack('<'+'h'*(len(raw)//2), raw)
        channels[name] = samples[::2], samples[1::2]
        assert len(samples) == 16*TICK
        assert all(v == 0 for v in samples[::2][2*TICK:4*TICK])
    canonical = tuple(lane(FINAL))
    assert all(l[4*TICK:] == canonical for l,r in channels.values())
    assert channels['02-interrupt'][0] == channels['03-repair'][0]
    assert channels['03-repair'][0] == channels['04-revision-A'][0]
    assert channels['04-revision-A'][1][:4*TICK] == channels['05-revision-B'][1][:4*TICK]
    assert channels['04-revision-A'][1][4*TICK:] != channels['05-revision-B'][1][4*TICK:]
    assert all(v == 0 for v in channels['01-clean'][0][:4*TICK])
    assert all(v == 0 for v in channels['02-interrupt'][1])
    assert any(channels['03-repair'][1][2*TICK:3*TICK])
    assert all(v == 0 for v in channels['03-repair'][1][4*TICK:])
    assert len(set(data.values())) == len(data) == 5


def main(outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    data = render()
    qualify(data)
    receipts = {}
    for name, raw in data.items():
        path = outdir / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, 8*TICK, 'NONE', 'not compressed'))
            w.writeframes(raw)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2,2,RATE,8*TICK)
            assert w.readframes(8*TICK) == raw
        receipts[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {'frames_per_recording': 8*TICK, 'invariant_left_suffix_frames': 4*TICK,
              'rate_hz': RATE, 'sha256': receipts,
              'qualification': 'PASS: repeated PCM render, header/payload roundtrip, canonical suffix and intervention controls'}
    (outdir/'receipts.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))
