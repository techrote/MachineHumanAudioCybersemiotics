"""Original synthetic score: python render.py [output-directory]."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import wave

RATE = 16000
CELL = 3200
GAP = CELL

def tone(freq, gain, i, length):
    return gain * math.sin(2 * math.pi * freq * i / RATE) * math.sin(math.pi * i / length) ** 2


def render(words, marked):
    left, right = [], []
    for k, word in enumerate(words):
        if k:
            left += [0] * GAP
            right += [0] * GAP
        notes = [220 if c == '0' else 330 for c in word] + [440]
        for j, freq in enumerate(notes):
            for i in range(CELL):
                left.append(round(tone(freq, 8500, i, CELL)))
                right.append(round(tone(660 if i < CELL//2 else 880, 6000, i % (CELL//2), CELL//2)) if k == marked and j == 5 else 0)
    return left, right


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    scenes = {
        'original': (('00000', '10000'), 0),
        'revised-exact': (('01000', '00000'), 1),
        'revised-joint': (('01000', '00000'), 0),
        'ambiguous-left': (('10000', '01000'), 0),
        'ambiguous-right': (('10000', '01000'), 1),
        'ambiguous-withheld': (('10000', '01000'), None),
    }
    rendered = {name: render(*scene) for name, scene in scenes.items()}
    assert rendered['revised-exact'][0] == rendered['revised-joint'][0]
    assert rendered['revised-exact'][1] != rendered['revised-joint'][1]
    assert rendered['ambiguous-left'][0] == rendered['ambiguous-right'][0] == rendered['ambiguous-withheld'][0]
    assert not any(rendered['ambiguous-withheld'][1])
    receipt = {}
    for name, (left, right) in rendered.items():
        assert (left, right) == render(*scenes[name])
        assert len(left) == len(right) == 13 * CELL
        assert max(map(abs, left + right)) <= 8500
        data = struct.pack('<' + 'hh' * len(left), *(v for pair in zip(left, right) for v in pair))
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, len(left), 'NONE', 'not compressed'))
            w.writeframes(data)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, len(left))
            assert w.readframes(len(left)) == data
        receipt[name] = {'context': scenes[name][0], 'marked_slot': scenes[name][1], 'frames': len(left), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert len({v['sha256'] for v in receipt.values()}) == len(receipt)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('PASS: six distinct WAVs, invariant left carriers, deterministic rendering and exact PCM readback')


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('audio'))
