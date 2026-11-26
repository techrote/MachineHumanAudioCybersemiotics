"""Carrier Bag Organ: original synthetic music, not a human listening experiment."""
import hashlib
import json
import math
import platform
import random
import struct
import wave
from pathlib import Path

RATE = 16000
# Period, phase offset, duration (ms), frequencies, gain, stereo position.
VOICES = (
    (2300, 0, 1500, (110, 130.81, 146.83, 123.47), 3300, -0.65),
    (3700, 590, 2100, (196, 220, 174.61), 2800, 0.55),
    (5100, 1420, 800, (523.25, 659.25, 440, 587.33), 2100, -0.15),
    (7300, 2100, 3300, (82.41, 98, 73.42), 2300, 0.25),
)


def voice(n, spec):
    period, offset, duration, pitches, gain, pan = spec
    period, offset, duration = (x * RATE // 1000 for x in (period, offset, duration))
    event, age = divmod(n + offset, period)
    if age >= duration:
        return 0, 0, 0.0
    env = math.sin(math.pi * age / duration) ** 2
    phase = math.tau * pitches[event % len(pitches)] * age / RATE
    signal = gain * env * (0.75 * math.sin(phase) + 0.25 * math.sin(phase * 2.003))
    return round(signal * (1 - pan) / 2), round(signal * (1 + pan) / 2), env


def frame(n, encounter=True):
    parts = [voice(n, v) for v in VOICES]
    # An invented encounter voice, not a physical intermodulation model.
    guest = round(1200 * parts[1][2] * parts[2][2] * math.sin(math.tau * 311 * n / RATE)) if encounter else 0
    return sum(p[0] for p in parts) + guest, sum(p[1] for p in parts) + guest


def render(start, stop, encounter=True):
    if not 0 <= start <= stop:
        raise ValueError('invalid absolute sample range')
    return [frame(n, encounter) for n in range(start, stop)]


def editorial_end(samples, fade_frames=RATE * 2):
    """Presentation transform, deliberately dependent on the chosen ending."""
    if not 1 <= fade_frames <= len(samples):
        raise ValueError('invalid fade')
    begin = len(samples) - fade_frames
    return samples[:begin] + [tuple(round(x * (len(samples) - 1 - i) / max(1, fade_frames - 1)) for x in samples[i]) for i in range(begin, len(samples))]


def payload(samples):
    return b''.join(struct.pack('<hh', *p) for p in samples)


def write(out, name, samples):
    path = out / (name + '.wav')
    raw = payload(samples)
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        f.writeframes(raw)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (2, 2, RATE, len(samples))
        assert f.readframes(len(samples)) == raw
    return {'frames': len(samples), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'peak': max(abs(x) for pair in samples for x in pair)}


def main():
    out = Path(__file__).parent / 'audio'
    out.mkdir(exist_ok=True)
    long = render(0, 24 * RATE)
    short = render(0, 12 * RATE)
    excerpt = render(7 * RATE, 19 * RATE)
    assert short == long[:12 * RATE]
    assert excerpt == long[7 * RATE:19 * RATE]
    assert render(0, 0) == []
    try:
        render(10, 9)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid interval accepted')
    rng = random.Random(731)
    for _ in range(32):
        start = rng.randrange(len(long) - 256)
        end = start + rng.randrange(1, 257)
        assert render(start, end) == long[start:end]
    cut = editorial_end(short)
    assert cut[:10 * RATE] == short[:10 * RATE] and cut != short and cut[-1] == (0, 0)
    separate = render(0, 12 * RATE, False)
    assert separate != short
    for n, (a, b) in enumerate(zip(short, separate)):
        delta = (a[0] - b[0], a[1] - b[1])
        assert delta[0] == delta[1]
        if not (voice(n, VOICES[1])[2] and voice(n, VOICES[2])[2]):
            assert delta == (0, 0)
    variants = {'room-24': long, 'room-12': short, 'window-7-to-19': excerpt,
                'editorial-ending': cut, 'without-encounter': separate}
    receipt = {'python': platform.python_version(), 'rate': RATE, 'checks': {'prefix': True,
                'offset_crop': True, 'random_windows': 32, 'empty_invalid': True,
                'editorial_negative_control': True, 'encounter_ablation': True},
                'files': {name: write(out, name, s) for name, s in variants.items()}}
    assert all(v['peak'] <= 32767 for v in receipt['files'].values())
    assert len({v['sha256'] for v in receipt['files'].values()}) == len(variants)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
