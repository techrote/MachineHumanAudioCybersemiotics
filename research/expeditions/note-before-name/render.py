"""Original symbolic sonification, not a perceptual experiment."""
import math
import struct
import wave
from pathlib import Path

RATE = 22050
CELL = 3300

def render(left, right, path):
    frames = bytearray()
    for j in range(max(len(left), len(right))):
        for i in range(CELL):
            vals = []
            for bits in (left, right):
                if j >= len(bits):
                    vals.append(0)
                    continue
                f = 440 if bits[j] == '0' else 660
                env = min(1, i/160, (CELL-1-i)/160)
                vals.append(round(9000*env*math.sin(2*math.pi*f*i/RATE)))
            frames.extend(struct.pack('<hh', *vals))
    with wave.open(str(path), 'wb') as w:
        w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(frames)

if __name__ == '__main__':
    out = Path(__file__).parent
    render('0'+'11'*14, '01'+'11'*14, out/'end-of-message.wav')
    render('0'+'110'+'0', '01'+'110', out/'finite-delay.wav')
