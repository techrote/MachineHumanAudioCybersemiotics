"""Exact finite marginal bounds and original integer PCM demonstration.

Mask bit i denotes satisfaction of constraint i by one candidate. Histogram
cells count candidates, not probabilities; candidate identity is omitted.
No external dependencies, no human or empirical data.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import wave

MAX_N = 12


def size(n):
    if type(n) is not int or not 1 <= n <= MAX_N:
        raise ValueError("n must be an integer in 1..12")
    return 1 << n


def check_counts(values, length):
    values = tuple(values)
    if len(values) != length or any(type(v) is not int or v < 0 for v in values):
        raise ValueError("expected exact nonnegative integer counts of declared length")
    return values


def moments(n, histogram):
    """All conjunction counts, including empty conjunction = population."""
    m = list(check_counts(histogram, size(n)))
    for i in range(n):
        bit = 1 << i
        for s in range(len(m)):
            if not s & bit:
                m[s] += m[s | bit]
    return tuple(m)


def invert(n, counts):
    """Boolean lattice inverse; signed intermediate cells allowed."""
    h = list(counts)
    for i in range(n):
        bit = 1 << i
        for s in range(len(h)):
            if not s & bit:
                h[s] -= h[s | bit]
    return tuple(h)


def bounds(n, proper):
    """Exact inclusive integer range of the omitted all-constraints count.

    proper[s] is the count satisfying every bit in s, for masks 0..2**n-2.
    Raises ValueError if no nonnegative integer histogram is compatible.
    """
    top = size(n) - 1
    proper = check_counts(proper, top)
    a = invert(n, proper + (0,))
    lo, hi = 0, proper[0]
    for s, v in enumerate(a):
        if (n - s.bit_count()) % 2 == 0:
            lo = max(lo, -v)
        else:
            hi = min(hi, v)
    if lo > hi:
        raise ValueError("inconsistent proper conjunction counts")
    return lo, hi


def reconstruct(n, proper, x):
    proper = tuple(proper)
    lo, hi = bounds(n, proper)
    if type(x) is not int or not lo <= x <= hi:
        raise ValueError("joint count outside feasible integer range")
    return invert(n, tuple(proper) + (x,))


def status(n, proper):
    lo, hi = bounds(n, proper)
    return "IMPOSSIBLE" if hi == 0 else "GUARANTEED_EXISTENCE" if lo > 0 else "UNDETERMINED"


def parity_hist(n, parity):
    if type(parity) is not int or parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    return tuple(int(s.bit_count() % 2 == parity) for s in range(size(n)))


def compositions(total, cells):
    """All weak compositions, for small exhaustive test domains only."""
    if cells == 1:
        yield (total,)
        return
    for x in range(total + 1):
        for tail in compositions(total - x, cells - 1):
            yield (x,) + tail


def exhaustive(n=3, max_total=5):
    """Independent enumeration of feasible counts, grouped by proper moments."""
    groups = {}
    examined = 0
    for total in range(max_total + 1):
        for h in compositions(total, size(n)):
            m = moments(n, h)
            groups.setdefault(m[:-1], set()).add(h[-1])
            examined += 1
    for proper, observed in groups.items():
        lo, hi = bounds(n, proper)
        assert observed == set(range(lo, hi + 1))
        for x in observed:
            h = reconstruct(n, proper, x)
            assert min(h) >= 0 and moments(n, h) == proper + (x,)
    return {"histograms": examined, "summary_groups": len(groups),
            "ambiguous_groups": sum(len(v) > 1 for v in groups.values())}


def render(counts):
    """One fixed-length tone per count. Integer triangle wave, PCM16 mono.

    Counts map to pitch periods; this is an authored mapping, not a listener
    test. Distinct input is not generally claimed to imply distinct audio.
    """
    frames = bytearray()
    for count in counts:
        if type(count) is not int or not 0 <= count <= 4095:
            raise ValueError("audio count outside demonstration range")
        period = 32 + count
        for t in range(1600):
            phase = t % period
            triangle = 4 * min(phase, period - phase) * 6000 // period - 6000
            envelope = min(t, 1599-t, 80)
            frames.extend(struct.pack("<h", triangle * envelope // 80))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(frames)
    return out.getvalue()


def experiment():
    even, odd = parity_hist(3, 0), parity_hist(3, 1)
    m0, m1 = moments(3, even), moments(3, odd)
    assert m0[:-1] == m1[:-1] and m0[-1] != m1[-1]
    audio = {"proper_even": render(m0[:-1]), "proper_odd": render(m1[:-1]),
             "full_even": render(m0), "full_odd": render(m1)}
    assert audio["proper_even"] == audio["proper_odd"]
    assert audio["full_even"] != audio["full_odd"]
    receipt = {"scope": "fictional finite counts; no participant data",
               "even": even, "odd": odd, "proper": m0[:-1],
               "full_intersections": [m0[-1], m1[-1]],
               "bounds": bounds(3, m0[:-1]), "status": status(3, m0[:-1]),
               "exhaustive": exhaustive(),
               "audio_sha256": {k: hashlib.sha256(v).hexdigest() for k,v in audio.items()}}
    return receipt, audio


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    receipt, audio = experiment()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for name, data in audio.items():
            (args.out / (name + ".wav")).write_bytes(data)
        (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
