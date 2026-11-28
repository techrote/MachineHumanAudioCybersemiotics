"""ACCEL-018: independent spectral witness of Afterimage 0.2.0 memory depth."""
import argparse
import json
from pathlib import Path
import struct
import unittest
import numpy as np

RATES = (44100, 48000, 96000)
BLOCKS = (257, 1024)
HISTORIES = ((57, 59, 62), (60, 59, 62), (57, 61, 62))
NEW = ("MHACAfterimage", "c6cee2501acecf1873828cbe683b1763f39c6690",
       "607f0bd86c7d283b51c5333ee8b18721c080b51f9af8f6523e20d4c226f8da16",
       "BD0B8CB3B82E43EB9613F0C9A37FBA83", "0.2.0")


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def state(depth):
    require(depth in (1, 2, 3), "invalid depth")
    return (b"AC01" if depth == 1 else b"AC02") + struct.pack(
        "<I", 16 | (3 << 5) | (1000 << 18) | ((depth-1) << 28))


def events(history):
    result = []
    for i, pitch in enumerate((*history, 36)):
        result.extend(((bytes((0x90, pitch, 102)), i*.5),
                       (bytes((0x80, pitch, 0)), i*.5+.25)))
    return result


def frequencies(history, depth):
    newest, previous, oldest = (p % 8 for p in reversed(history))
    f = 440 * 2**((36-69)/12)
    return f * np.array([1, 2+newest/4, 3+(previous if depth >= 2 else newest)/2,
                         5+3*(oldest if depth >= 3 else newest)/4])


def basis(rate, history, depth):
    t = np.arange(round(1.6*rate), round(1.7*rate))/rate
    phase = 2*np.pi*t[:, None]*frequencies(history, depth)
    return np.column_stack((np.sin(phase), np.cos(phase), np.ones(len(t))))


def witness(x, rate, history, depth):
    design = basis(rate, history, depth)
    x = np.asarray(x, dtype=np.float64)
    require(x.shape == (len(design),) and np.isfinite(x).all(), "invalid witness")
    coef = np.linalg.lstsq(design, x, rcond=None)[0]
    amp = np.hypot(coef[:4], coef[4:8])
    require(amp[0] > .01, "silent/weak probe")
    expected = np.array([1, .5, .3, .2])
    error = float(np.max(np.abs(amp/amp[0]-expected)))
    residual = float(np.linalg.norm(x-design@coef)/np.linalg.norm(x))
    require(error < .003 and residual < .003, "unexpected harmonic structure")
    return dict(frequencies_hz=frequencies(history, depth).tolist(),
                amplitude_ratios=(amp/amp[0]).tolist(), ratio_error=error, relative_residual=residual)


def run(old, new, out):
    import host_audition as h
    import afterimage_receipt_host as chain
    out.mkdir(parents=True, exist_ok=True)
    report = dict(scope="AC01 migration and AC02 depth; continuous Windows host MIDI", cases=[])
    def persist():
        (out/"afterimage-depth.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    persist()
    try:
        ob, report["old_package"] = chain.package(old, out/"old", chain.A)
        nb, report["new_package"] = chain.package(new, out/"new", NEW)
        for rate in RATES:
            reference = {}
            for block in BLOCKS:
                for history in HISTORIES:
                    for depth in (1, 2, 3):
                        s = state(depth)
                        c = dict(rate=rate, block=block, history=history, depth=depth, status="started")
                        report["cases"].append(c); persist()
                        def render(bundle, pin, saved=None):
                            p = chain.prepare(bundle, pin, s, rate, block, True, saved)
                            x = h.checked(p(events(history), duration=2., sample_rate=rate,
                                num_channels=2, buffer_size=block, reset=False), 2*rate)
                            h.verify_component(p, pin[3], s)
                            require(np.max(np.abs(x[0]-x[1])) < 2e-5, "stereo")
                            require(np.max(np.abs(x[:, -rate//10:])) < 2e-5, "release")
                            return x, p.preset_data
                        x, saved = render(nb, NEW)
                        c.update(witness(x[0, round(1.6*rate):round(1.7*rate)], rate, history, depth))
                        c["restore_error"] = chain.error(x, render(nb, NEW, saved)[0])
                        require(c["restore_error"] < 2e-5, "fresh restore")
                        if depth == 1:
                            c["legacy_error"] = chain.error(x, render(ob, chain.A)[0])
                            require(c["legacy_error"] < 2e-5, "AC01 legacy render")
                        key = (history, depth)
                        if block == BLOCKS[0]: reference[key] = x
                        else:
                            c["partition_error"] = chain.error(x, reference[key])
                            require(c["partition_error"] < 2e-5, "partition")
                        c["output"] = h.metrics(x)
                        c["status"] = "pass"; persist()
        report["complete"] = True
    except Exception as exc:
        report["error"] = repr(exc)
        raise
    finally:
        persist()


class OracleTests(unittest.TestCase):
    def test_codec(self):
        for d in (1, 2, 3):
            self.assertEqual(state(d)[:4], b"AC01" if d == 1 else b"AC02")
            self.assertEqual(struct.unpack("<I", state(d)[4:])[0] >> 28, d-1)
        for d in (0, 4):
            with self.assertRaises(ValueError): state(d)

    def test_spectral(self):
        for rate in RATES:
            for history in HISTORIES:
                for depth in (1, 2, 3):
                    b = basis(rate, history, depth)
                    # Independent nonzero phases; scaled positive control.
                    x = b @ np.r_[.03*np.array([1, .5, .3, .2])*np.cos(.43),
                                  .03*np.array([1, .5, .3, .2])*np.sin(.43), 0.]
                    witness(x, rate, history, depth)
                    for bad in (np.zeros_like(x), x*np.nan, b[:, 0]*.03):
                        with self.assertRaises(ValueError): witness(bad, rate, history, depth)
                    for wrong in (1, 2, 3):
                        if wrong != depth:
                            with self.assertRaises(ValueError): witness(x, rate, history, wrong)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("old", "new", "out"): p.add_argument("--"+name, type=Path)
    a = p.parse_args()
    require(unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OracleTests)).wasSuccessful(), "oracle tests")
    if any((a.old, a.new, a.out)):
        require(all((a.old, a.new, a.out)), "all arguments required")
        run(a.old, a.new, a.out)
