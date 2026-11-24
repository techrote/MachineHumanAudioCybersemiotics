"""Original synthetic score; no dependencies or human data. Python 3.11+."""
import hashlib
import json
import math
import struct
import wave
from pathlib import Path

RATE = 24000
TICK = 7200
ATTACK = 4800
FREQ = (220, 247, 294, 330, 392)
SCORES = {
    "concentrated": ((12, 0, 0, 0), True, (2, 2, 2, 2)),
    "distributed": ((3, 3, 3, 3), True, (3, 1, 4, 2)),
    "deferred": ((0, 4, 4, 4), True, (0, 4, 3, 2)),
    "frozen": ((3, 3, 3, 3), False, (0, 0, 0, 0)),
}


def synth(gaps, advance):
    state = 0
    notes = []
    samples = bytearray()
    for gap in gaps:
        samples.extend(bytes(2 * gap * TICK))
        if advance:
            state = (state + gap) % len(FREQ)
        notes.append(state)
        for i in range(ATTACK):
            envelope = min(1, i / 240, (ATTACK - 1 - i) / 480)
            x = math.sin(2 * math.pi * FREQ[state] * i / RATE)
            samples.extend(struct.pack("<h", round(8000 * envelope * x)))
    return bytes(samples), tuple(notes)


def main():
    out = Path(__file__).resolve().parent
    receipts = []
    for name, (gaps, advance, expected) in SCORES.items():
        pcm, notes = synth(gaps, advance)
        assert (pcm, notes) == synth(gaps, advance)
        assert notes == expected and sum(gaps) == 12
        frames = 12 * TICK + 4 * ATTACK
        assert len(pcm) == frames * 2
        target = out / (name + ".wav")
        with wave.open(str(target), "wb") as f:
            f.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            f.writeframes(pcm)
        with wave.open(str(target), "rb") as f:
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (1, 2, RATE, frames)
            assert f.readframes(frames) == pcm
        pos = 0
        for gap, note in zip(gaps, notes):
            end = pos + 2 * gap * TICK
            assert pcm[pos:end] == bytes(end - pos)
            segment = pcm[end:end + 2 * ATTACK]
            values = struct.unpack("<" + "h" * ATTACK, segment)
            assert max(map(abs, values)) <= 8000 and max(values) > 0
            crossings = sum(a <= 0 < b for a, b in zip(values, values[1:]))
            assert abs(crossings - FREQ[note] * ATTACK / RATE) <= 2
            pos = end + 2 * ATTACK
        receipts.append(dict(name=name, gaps=gaps, advance=advance, notes=notes,
                             frames=frames, seconds=frames / RATE,
                             sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (out / "render-receipts.json").write_text(json.dumps(receipts, indent=2) + "\n")
    print(json.dumps(receipts, indent=2))


if __name__ == "__main__":
    main()
