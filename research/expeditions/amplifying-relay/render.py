"""Original deterministic sonification of exact relay trajectories (not physical audio gain)."""
import hashlib
import json
import struct
import wave
from fractions import Fraction
from pathlib import Path

RATE = 16000
CELL = 3200
WEIGHTS = ((0, 4, 0), (0, 0, 4), (Fraction(1, 4), 0, 0))


def trajectory(word):
    x = (Fraction(1), Fraction(0), Fraction(0))
    result = [x]
    for mode in word:
        value = sum(x[i] * WEIGHTS[i][mode] for i in range(3))
        x = tuple(value if i == mode else Fraction(0) for i in range(3))
        result.append(x)
    return result


def cell(x):
    magnitude = sum(abs(v) for v in x)
    if not magnitude:
        return [0] * CELL
    coord = next(i for i, v in enumerate(x) if v)
    # Exact integer power-of-two compression, intentionally not linear gain.
    level = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    amplitude = max(500, min(12000, 1800 + 1300 * level))
    freq = (240, 320, 480)[coord]
    return [((4 * abs((i * freq) % RATE - RATE // 2) - RATE) * amplitude
             * min(i, CELL - 1 - i, 160)) // (RATE * 160)
            for i in range(CELL)]


def render(directory):
    directory.mkdir(parents=True, exist_ok=True)
    cases = {
        "unguarded-versus-guarded": ([1, 2, 0] * 4, [1, 1, 0] * 4),
        "equal-rate-different-peak": ([1, 2, 0, 0], [1, 1, 0, 0]),
    }
    manifest = {}
    for name, (left, right) in cases.items():
        a, b = trajectory(left), trajectory(right)
        l = [v for x in a for v in cell(x)]
        r = [v for x in b for v in cell(x)]
        path = directory / (name + ".wav")
        with wave.open(str(path), "wb") as f:
            f.setparams((2, 2, RATE, len(l), "NONE", "not compressed"))
            f.writeframes(b"".join(struct.pack("<hh", x, y) for x, y in zip(l, r)))
        manifest[name] = {"left_modes": left, "right_modes": right,
                          "left_norms": [str(sum(map(abs, x))) for x in a],
                          "right_norms": [str(sum(map(abs, x))) for x in b],
                          "frames": len(l), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (directory / "audio-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    import sys
    render(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("run"))
