"""Original synthetic parallel score; standard library, no hardware or participants."""
import argparse
import hashlib
import itertools
import json
import math
import struct
import wave
from collections import Counter
from pathlib import Path

RATE = 16000
CELL = 8000
CORE = ("ENTER", "WAIT", "TURN", "EXIT")
FREQ = (180, 240, 300, 360)
VERSE = (
    ("A room acquires a hinge.", "The threshold lends its name."),
    ("A chair keeps an appointment.", "The clock declines its invitation."),
    ("The corridor changes grammar.", "The window rehearses a corner."),
    ("The key leaves its shadow.", "An address outlives its occupant."),
)
SCORE = (0, 1, 2, 1, 3, 0, 2, 3)
A = (0, 1, 0, 1, 1, 0, 1, 0)
B = (0, 0, 1, 0, 1, 1, 0, 1)


def symbols(event):
    c, a, t = event
    return (c, a), (c, t)


def reconcile(audio, text):
    """Symbolic core agreement, not provenance or real-world authorization."""
    if audio is None and text is None:
        return "ABSENT"
    if audio is None:
        return CORE[text[0]]
    if text is None:
        return CORE[audio[0]]
    return CORE[audio[0]] if audio[0] == text[0] else "CONFLICT"


def census():
    events = list(itertools.product(range(4), range(2), range(2)))
    channels = [Counter(), Counter()]
    core_pairs = set()
    for e in events:
        a, t = symbols(e)
        channels[0][a] += 1
        channels[1][t] += 1
        core_pairs.add((a, t))
        assert reconcile(a, None) == reconcile(None, t) == CORE[e[0]]
    assert len(core_pairs) == 16
    assert all(len(c) == 8 and set(c.values()) == {2} for c in channels)
    counts = Counter()
    for a, t in itertools.product(*channels):
        counts["agree" if a[0] == t[0] else "conflict"] += 1
        assert (reconcile(a, t) == "CONFLICT") == (a[0] != t[0])
    assert counts == {"agree": 16, "conflict": 48}
    # Shared wrong core is not caught by agreement.
    assert reconcile((1, 0), (1, 1)) == "WAIT"
    assert reconcile((1, 0), (1, 1)) != CORE[0]
    assert reconcile(None, None) == "ABSENT"
    # Exhaust all length-three scores and compare joint and one-channel fibers.
    sa, st, joint = Counter(), Counter(), set()
    for seq in itertools.product(events, repeat=3):
        pairs = tuple(map(symbols, seq))
        av, tv = tuple(p[0] for p in pairs), tuple(p[1] for p in pairs)
        sa[av] += 1
        st[tv] += 1
        joint.add((av, tv))
        assert tuple(reconcile(x, None) for x in av) == tuple(CORE[e[0]] for e in seq)
        assert tuple(reconcile(None, x) for x in tv) == tuple(CORE[e[0]] for e in seq)
    assert len(joint) == 4096
    assert all(len(c) == 512 and set(c.values()) == {8} for c in (sa, st))
    return {"event_count": len(events), "cross_channel_pairs": dict(counts),
            "length_three_scores": len(joint), "single_view_fiber": 8}


def tile(c, a):
    # Deliberate timbre variation; common fundamental and event duration.
    f = FREQ[c]
    out = []
    for i in range(CELL):
        p = 2 * math.pi * f * i / RATE
        env = math.sin(math.pi * i / (CELL - 1)) ** 2
        v = 0.24 * math.sin(p) + (0.12 * math.sin(3 * p) if a else 0)
        out.append(round(32767 * env * v))
    return tuple(out)


def read_core(pcm):
    # Known frame grid, fixed codebook, clean PCM only; not human decoding.
    def power(f):
        re = sum(v * math.cos(2 * math.pi * f * i / RATE) for i, v in enumerate(pcm))
        im = sum(v * math.sin(2 * math.pi * f * i / RATE) for i, v in enumerate(pcm))
        return re * re + im * im
    return max(range(4), key=lambda c: power(FREQ[c]))


def stamp(i):
    ms = i * 500
    return f"00:00:{ms // 1000:02d}.{ms % 1000:03d}"


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    tiles = {(c, a): tile(c, a) for c in range(4) for a in range(2)}
    for (c, a), pcm in tiles.items():
        assert read_core(pcm) == c
        assert max(map(abs, pcm)) < 12000
    receipt = census()
    receipt["clean_pcm_tiles_decoded"] = len(tiles)
    receipt["files"] = {}
    for name, av, tv in (("room", A, A), ("other-caption", A, B),
                         ("other-timbre", B, A), ("other-both", B, B)):
        samples = tuple(v for c, a in zip(SCORE, av) for v in tiles[c, a])
        pcm = struct.pack("<" + "h" * len(samples), *samples)
        path = out / (name + ".wav")
        with wave.open(str(path), "wb") as w:
            w.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            w.writeframes(pcm)
        with wave.open(str(path), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, CELL * len(SCORE))
            assert w.readframes(w.getnframes()) == pcm
        # Faithful description is separate from original artistic text.
        rows = ["WEBVTT", ""]
        access = ["WEBVTT", ""]
        for i, (c, a, t) in enumerate(zip(SCORE, av, tv)):
            timing = f"{stamp(i)} --> {stamp(i+1)}"
            rows += [timing, CORE[c] + " | " + VERSE[c][t], ""]
            access += [timing, f"{CORE[c]} | {FREQ[c]} Hz; " + ("fundamental + third harmonic" if a else "fundamental only"), ""]
        for suffix, lines in ((".art.vtt", rows), (".description.vtt", access)):
            (out / (name + suffix)).write_text("\n".join(lines) + "\n", encoding="utf-8")
        receipt["files"][name] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (path, out / (name + ".art.vtt"), out / (name + ".description.vtt"))}
    def digest(name, suffix):
        return receipt["files"][name][name + suffix]
    assert digest("room", ".wav") == digest("other-caption", ".wav")
    assert digest("room", ".wav") != digest("other-timbre", ".wav")
    assert digest("room", ".art.vtt") == digest("other-timbre", ".art.vtt")
    assert digest("room", ".description.vtt") == digest("other-caption", ".description.vtt")
    assert digest("room", ".description.vtt") != digest("other-timbre", ".description.vtt")
    assert digest("room", ".art.vtt") != digest("other-caption", ".art.vtt")
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    print(json.dumps(render(parser.parse_args().out), indent=2, sort_keys=True))
