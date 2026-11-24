"""Original synthetic stereo score; Python standard library only."""
import hashlib, math, struct, wave
from fractions import Fraction
from pathlib import Path

RATE = 16000
FRAMES = 4800
ROOT = 220


def exact(steps):
    x = Fraction(1)
    out = [x]
    for _ in range(steps):
        x *= 3
        while x >= 2:
            x /= 2
        out.append(x)
    return out


def render(ratios):
    pcm = bytearray()
    for ratio in ratios:
        for i in range(FRAMES):
            t = i / RATE
            env = min(1, i / 240, (FRAMES - 1 - i) / 240)
            left = round(6000 * env * math.sin(2 * math.pi * ROOT * float(ratio) * t))
            right = round(6000 * env * math.sin(2 * math.pi * ROOT * t))
            pcm.extend(struct.pack('<hh', left, right))
    return bytes(pcm)


def main():
    directory = Path(__file__).resolve().parent / 'audio'
    directory.mkdir(exist_ok=True)
    a, b = exact(12), exact(53)
    grid = [2 ** ((7 * k % 12) / 12) for k in range(13)]
    assert a[-1] == Fraction(3**12, 2**19)
    assert b[-1] == Fraction(3**53, 2**84)
    assert grid[-1] == 1 and len(set(grid[:-1])) == 12
    receipts = []
    for name, ratios in [('01-tempered', grid), ('02-rational', a), ('03-long-return', b)]:
        pcm = render(ratios)
        assert pcm == render(ratios)
        path = directory / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, len(ratios)*FRAMES)
            assert w.readframes(w.getnframes()) == pcm
        assert all(pcm[j+2:j+4] == pcm[j% (FRAMES*4)+2:j% (FRAMES*4)+4] for j in range(0,len(pcm),4))
        receipts.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  audio/{path.name}')
        print(name, len(ratios), float(ratios[-1])*ROOT, len(pcm)//4)
    (directory.parent / 'SHA256SUMS').write_text('\n'.join(receipts)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
