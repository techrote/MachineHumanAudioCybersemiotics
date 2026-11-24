"""Original stereo score of exact three-symbol probability mass (not a sample)."""
import argparse
import hashlib
import json
import struct
import wave
from pathlib import Path

RATE = 16000
CELL = 1280
GAP = 640
COUNTS = [(8, 9), (4, 3), (2, 1), (2, 3), (4, 3), (0, 1), (2, 3), (10, 9)]


def note(bit, t):
    period = 64 if bit == "0" else 40
    x = t % period
    tri = period - 4 * abs(x - period // 2)
    env = min(80, t, CELL - 1 - t)
    return (7000 * tri * env) // (period * 80)


def render(path):
    data = bytearray()
    groups = []
    frame = 0
    for i, (left, right) in enumerate(COUNTS):
        word = format(i, "03b")
        start = frame
        for rep in range(max(left, right)):
            for bit in word:
                for t in range(CELL):
                    v = note(bit, t)
                    data.extend(struct.pack("<hh", v if rep < left else 0, v if rep < right else 0))
            data.extend(b"\0" * (GAP * 4))
            frame += 3 * CELL + GAP
        groups.append(dict(word=word, left=left, right=right, start_frame=start, end_frame=frame))
    with wave.open(str(path), "wb") as out:
        out.setparams((2, 2, RATE, 0, "NONE", "not compressed"))
        out.writeframes(data)
    return dict(rate=RATE, frames=frame, left_motifs=sum(x for x, _ in COUNTS),
                right_motifs=sum(y for _, y in COUNTS), groups=groups,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                interpretation="Probability-mass score, not a simulated trajectory or listener experiment")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("borrowed-memory.wav"))
    args = parser.parse_args()
    print(json.dumps(render(args.out), indent=2))
