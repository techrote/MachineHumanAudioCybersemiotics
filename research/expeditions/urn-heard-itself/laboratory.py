"""Synthetic role-binding witness and original music; no real authority or evidence."""
import hashlib
import itertools
import json
import math
import struct
import wave
from pathlib import Path

RATE = 16000
EVENT = "bell@noon"
ISSUER = "gallery"
EVIDENCE = {"sensor-1": EVENT, "sensor-2": "bell@dusk"}
QUOTES = {"archive-1": EVENT, "archive-2": "bell@dusk"}
MANDATES = {"mandate-1": (ISSUER, "curator", EVENT),
            "mandate-2": (ISSUER, "curator", "bell@dusk"),
            "mandate-3": ("other-gallery", "curator", EVENT)}
MODES = ("fiction", "quotation", "report", "delegated")


def admissible(mode, principal, evidence, mandate, quote):
    """Declared fixture contract, not a general truth or authorization checker."""
    if mode == "fiction":
        return (principal, evidence, mandate, quote) == (None, None, None, None)
    if mode == "quotation":
        return (principal is None and evidence is None and mandate is None
                and QUOTES.get(quote) == EVENT)
    if mode == "report":
        return (principal == ISSUER and EVIDENCE.get(evidence) == EVENT
                and mandate is None and quote is None)
    if mode == "delegated":
        return (principal == "curator" and EVIDENCE.get(evidence) == EVENT
                and MANDATES.get(mandate) == (ISSUER, principal, EVENT)
                and quote is None)
    return False


def note(freq, seconds):
    n = round(RATE * seconds)
    return b"".join(struct.pack("<h", round(10000 * math.sin(math.pi * i / (n - 1))**2
                                          * math.sin(2 * math.pi * freq * i / RATE)))
                    for i in range(n))


def main():
    root = Path(__file__).resolve().parent
    audio = root / "audio"
    audio.mkdir(exist_ok=True)
    expected = {(None, None, None, None), (None, None, None, "archive-1"),
                (ISSUER, "sensor-1", None, None), ("curator", "sensor-1", "mandate-1", None)}
    per_mode = dict(zip(MODES, [(None, None, None, None), (None, None, None, "archive-1"),
                              (ISSUER, "sensor-1", None, None), ("curator", "sensor-1", "mandate-1", None)]))
    candidates = list(itertools.product((None, ISSUER, "curator"), (None, *EVIDENCE),
                                        (None, *MANDATES), (None, *QUOTES)))
    admitted = []
    for mode in MODES:
        actual = {t for t in candidates if admissible(mode, *t)}
        assert actual == {per_mode[mode]}
        admitted.extend(actual)
    assert set(admitted) == expected
    assert not admissible("unknown", None, None, None, None)
    motif = b"".join(note(f, .3) for f in (220, 330, 275, 440))
    assert motif == b"".join(note(f, .3) for f in (220, 330, 275, 440))
    files = {}
    records = []
    for i, mode in enumerate(MODES):
        p, e, m, q = per_mode[mode]
        records.append(dict(mode=mode, animator="oscillator-1", author="score-writer",
                            figure="urn", issuer=ISSUER, principal=p, evidence=e,
                            mandate=m, quote=q, proposition=EVENT))
        files[mode] = note((550, 660, 770, 880)[i], .2) + b"\0" * (RATE // 10 * 2) + motif
    files["unframed"] = motif
    hashes = {}
    for name, pcm in files.items():
        path = audio / (name + ".wav")
        with wave.open(str(path), "wb") as f:
            f.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            f.writeframes(pcm)
        with wave.open(str(path), "rb") as f:
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (1, 2, RATE)
            actual = f.readframes(f.getnframes())
        assert actual == pcm and actual.endswith(motif)
        assert max(abs(x[0]) for x in struct.iter_unpack("<h", actual)) <= 10000
        hashes[name] = hashlib.sha256(actual).hexdigest()
    assert len(set(hashes.values())) == 5
    receipt = dict(candidate_assignments=len(candidates)*len(MODES), admitted=len(admitted),
                   rejected=len(candidates)*len(MODES)-len(admitted), motif_frames=len(motif)//2,
                   motif_sha256=hashlib.sha256(motif).hexdigest(), pcm_sha256=hashes, records=records)
    (root / "receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
