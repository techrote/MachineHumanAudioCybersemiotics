"""Original synthetic score: no audio input or external dependencies."""
from itertools import pairwise
from pathlib import Path
from math import sin, pi
import hashlib
import struct
import wave

FIELD = ((0, 2, 4, 7), (9, 7, 4, 2), (0, 5, 9, 12), (7, 5, 2, 0))
RATE = 16000
SLOT = 4000


def edge(a, b):
    return tuple(sorted((a, b)))


def grid_edges(n):
    return {edge((r, c), (r + dr, c + dc))
            for r in range(n) for c in range(n)
            for dr, dc in ((1, 0), (0, 1)) if r + dr < n and c + dc < n}


def scans(n):
    raster = [(r, c) for r in range(n) for c in range(n)]
    horizontal = [(r, c) for r in range(n)
                  for c in (range(n) if r % 2 == 0 else reversed(range(n)))]
    vertical = [(c, r) for r, c in horizontal]
    return {"raster": raster, "horizontal": horizontal, "vertical": vertical}


def transitions(path):
    return {edge(a, b) for a, b in pairwise(path)}


def census(n):
    vertices = [(r, c) for r in range(n) for c in range(n)]
    neighbors = {v: [u for u in vertices if sum(abs(a-b) for a,b in zip(v,u)) == 1]
                 for v in vertices}
    def visit(path, used):
        if len(path) == len(vertices):
            yield path
        else:
            for v in neighbors[path[-1]]:
                if v not in used:
                    yield from visit(path + [v], used | {v})
    return sum(1 for v in vertices for _ in visit([v], {v}))


def pcm(path):
    out = bytearray()
    for r, c in path:
        f = 220 * 2 ** (FIELD[r][c] / 12)
        for i in range(SLOT):
            t = i / RATE
            env = sin(pi * i / (SLOT - 1)) ** 2
            sample = round(7000 * env * (sin(2*pi*f*t) + .22*sin(4*pi*f*t)))
            out += struct.pack("<h", sample)
    return bytes(out)


def main():
    for n in range(2, 33):
        e = grid_edges(n)
        p = scans(n)
        h, v, r = (transitions(p[k]) for k in ("horizontal", "vertical", "raster"))
        assert len(e) == 2*n*(n-1)
        assert all(len(x) == len(set(x)) == n*n for x in p.values())
        assert len(h) == len(v) == n*n-1 and h <= e and v <= e
        assert h | v == e and len(h & v) == 2*(n-1)
        assert len(r & e) == n*(n-1) and len(r-e) == n-1
    print("Grid contracts passed for 31 sizes (2..32).")
    print("Directed Hamiltonian path counts:", {n: census(n) for n in (2,3,4)})
    folder = Path(__file__).parent / "audio"
    folder.mkdir(exist_ok=True)
    p = scans(4)
    p["two_pass"] = p["horizontal"] + p["vertical"]
    for name, path in p.items():
        payload = pcm(path)
        assert payload == pcm(path)
        assert max(abs(x[0]) for x in struct.iter_unpack("<h", payload)) <= 8540
        file = folder / (name + ".wav")
        with wave.open(str(file), "wb") as w:
            w.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            w.writeframes(payload)
        with wave.open(str(file), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, len(path)*SLOT)
            assert w.readframes(w.getnframes()) == payload
        print(name, len(path)*SLOT/RATE, "seconds", hashlib.sha256(file.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
