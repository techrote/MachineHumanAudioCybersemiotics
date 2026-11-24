"""Synthetic original alias twins. No listener data. Python 3.11+ stdlib."""
import hashlib
import json
import math
import struct
import wave
from pathlib import Path


def render(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rate, frames, period, stride = 16000, 32000, 320, 40
    # Frequencies 3*rate/period=150 and 11*rate/period=550 Hz.
    # The phase lookup index is integer, so anchors match before PCM rounding.
    table = [math.sin(2 * math.pi * j / period) for j in range(period)]
    samples = bytearray()
    equal_anchors = equal_midpoints = equal_all = 0
    for i in range(frames):
        envelope = min(1, i / 320, (frames - 1 - i) / 320)
        a = round(12000 * envelope * table[(3 * i) % period])
        b = round(12000 * envelope * table[(11 * i) % period])
        if i % stride == 0:
            assert (3 * i) % period == (11 * i) % period
            assert a == b
            equal_anchors += 1
        if i % stride == stride // 2:
            assert ((11 * i) - (3 * i)) % period == period // 2
            equal_midpoints += int(a == b)
        equal_all += int(a == b)
        samples.extend(struct.pack('<hh', a, b))
    path = out / 'alias-twins.wav'
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(samples)
    result = {
        'synthetic': True, 'rate_hz': rate, 'frames': frames,
        'channels_hz': [150, 550], 'anchor_rate_hz': rate // stride,
        'equal_anchor_pcm_pairs': equal_anchors,
        'total_anchor_pairs': frames // stride,
        'equal_midpoint_pcm_pairs': equal_midpoints,
        'total_midpoint_pairs': frames // stride,
        'equal_all_pcm_pairs': equal_all,
        'different_all_pcm_pairs': frames - equal_all,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    (out / 'audio-manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    import sys
    print(json.dumps(render(sys.argv[1] if len(sys.argv) > 1 else 'run'), indent=2))
