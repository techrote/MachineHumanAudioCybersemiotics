"""Synthetic cache counterpoint. Counts are tile constructions, not CPU time."""
import hashlib
import itertools
import json
import math
import struct
import sys
import wave
from collections import Counter
from functools import lru_cache
from pathlib import Path

RATE, FRAMES = 16000, 4000
SCORE = "ABCABCABCABC"


def trace(score, policy, build=lambda key: key):
    cache, events, tiles = {}, [], []
    for i, key in enumerate(score):
        hit = key in cache
        if not hit:
            if len(cache) == 2:
                if policy == "future":
                    def next_use(k):
                        return score.find(k, i + 1) if k in score[i + 1:] else len(score)
                    victim = max(cache, key=next_use)
                else:
                    victim = next(iter(cache))
                del cache[victim]
            cache[key] = build(key)
        elif policy == "lru":
            cache[key] = cache.pop(key)
        tiles.append(cache[key])
        events.append(not hit)
    return events, tiles


def optimum(score):
    @lru_cache(None)
    def solve(i, held):
        if i == len(score):
            return 0
        key = score[i]
        if key in held:
            return solve(i + 1, held)
        choices = [held] if len(held) < 2 else [held - {v} for v in held]
        return 1 + min(solve(i + 1, frozenset(s | {key})) for s in choices)
    return solve(0, frozenset())


def census():
    counts = Counter()
    for n in range(1, 8):
        for seq in itertools.product("ABC", repeat=n):
            score = "".join(seq)
            lru = sum(trace(score, "lru")[0])
            future = sum(trace(score, "future")[0])
            assert future == optimum(score) <= lru
            counts["scores"] += 1
            counts["lru_builds"] += lru
            counts["future_builds"] += future
            counts["strict_gap_scores"] += lru > future
            counts["maximum_gap"] = max(counts["maximum_gap"], lru - future)
    for score in ("ABCA", "ABCB"):
        assert optimum(score) == 3
    assert sum(trace("ABCA", "lru")[0]) == 4
    return dict(counts)


def tone(freq, amp, n=FRAMES):
    return tuple(round(amp * math.sin(2 * math.pi * freq * i / RATE) *
                       math.sin(math.pi * i / (n - 1)) ** 2) for i in range(n))


def render(out, policy, theatre=False):
    calls = []
    def build(key):
        calls.append(key)
        return tone(dict(A=220, B=277, C=330)[key], 8000)
    misses, tiles = trace(SCORE, policy, build)
    assert calls == [k for k, m in zip(SCORE, misses) if m]
    markers = [theatre or m for m in misses]
    pulse = tone(880, 4500, 1200) + (0,) * (FRAMES - 1200)
    left = tuple(itertools.chain.from_iterable(tiles))
    right = tuple(itertools.chain.from_iterable(pulse if m else (0,) * FRAMES for m in markers))
    payload = b"".join(struct.pack("<hh", a, b) for a, b in zip(left, right))
    name = "theatre" if theatre else policy
    path = out / (name + ".wav")
    with wave.open(str(path), "wb") as f:
        f.setparams((2, 2, RATE, 0, "NONE", "not compressed"))
        f.writeframes(payload)
    with wave.open(str(path), "rb") as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (2, 2, RATE, len(left))
        assert f.readframes(len(left)) == payload
    assert max(map(abs, left + right)) <= 8000
    return left, {"builds": len(calls), "misses": misses, "markers": markers,
                  "false_markers": sum(m and not h for m, h in zip(markers, misses)),
                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    left, a = render(out, "lru")
    other, b = render(out, "future")
    fake, c = render(out, "future", theatre=True)
    assert left == other == fake
    assert a["false_markers"] == b["false_markers"] == 0 < c["false_markers"]
    assert a["sha256"] == c["sha256"] != b["sha256"]
    receipt = {"score": SCORE, "census": census(), "lru": a, "future": b, "theatre": c}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("audio"))
