"""Original integer PCM sonification for MHAC #232; no dependencies."""
import hashlib
import json
import struct
import wave
from pathlib import Path

RATE = 16000
CELL = 2400
PERIODS = (80, 64, 50, 40)


def trajectory(word, omitted=(), initial=0):
    state = initial
    out = [state]
    for i, command in enumerate(word):
        if i not in omitted:
            state = (state + 1) % 4 if command == 'a' else (0 if state == 3 else state)
        out.append(state)
    return out


def sample(state, i):
    p = PERIODS[state]
    # Integer triangle, with independent cell envelopes to avoid clicks.
    tri = 4 * abs((i % p) - p // 2) - p
    env = min(i, CELL - 1 - i, 120)
    return tri * 7000 * env // (p * 120)


def render(outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, word, omitted in (
        ('ordinary-one-loss', 'baaabaaab', (1,)),
        ('robust-one-loss', 'baaababaababaaab', (1,)),
        ('robust-two-loss', 'baaababaababaaab', (13, 14)),
    ):
        left, right = trajectory(word), trajectory(word, omitted)
        path = outdir / (name + '.wav')
        pcm = bytearray()
        for a, b in zip(left + [left[-1]] * 3, right + [right[-1]] * 3):
            for i in range(CELL):
                pcm.extend(struct.pack('<hh', sample(a, i), sample(b, i)))
        with wave.open(str(path), 'wb') as f:
            f.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            f.writeframes(pcm)
        rows.append(dict(file=path.name, word=word, omitted_zero_based=omitted,
                         left=left, right=right, frames=len(pcm)//4,
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (outdir / 'audio-manifest.json').write_text(json.dumps(rows, indent=2) + '\n')
    return rows


if __name__ == '__main__':
    import sys
    print(json.dumps(render(Path(sys.argv[1] if len(sys.argv) > 1 else 'run')), indent=2))
