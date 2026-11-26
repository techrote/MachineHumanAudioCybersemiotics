"""ACCEL-019: exact 0.2.0 instrument/effect chain; settled transfer oracle."""
import argparse
import json
from pathlib import Path
import unittest
import numpy as np
import afterimage_depth_host as ac
import receipt_fold_upgrade_host as rf


def states():
    for name, mode, bypass in (("collapse", 0, False), ("preview", 2, False),
                               ("full", 3, False), ("bypass", 0, True)):
        yield name, rf.rf03(bits=4, a=112, b=128, fine=True, mode=mode,
                            bypass=bypass, wet=.625)


def transfer_error(x, y, state):
    if x.shape != y.shape or not np.isfinite(y).all():
        raise ValueError("invalid chain output")
    error = float(np.max(np.abs(y - rf.oracle(x, state))))
    if error > 2e-6:
        raise ValueError(f"chain transfer error: {error}")
    return error


class Tests(unittest.TestCase):
    def test_transfer(self):
        x = rf.stimulus(48000)
        outputs = {}
        for name, state in states():
            y = rf.oracle(x, state)
            self.assertEqual(transfer_error(x, y, state), 0)
            outputs[name] = y
            with self.assertRaises(ValueError):
                transfer_error(x, y + .01, state)
        self.assertTrue(np.array_equal(outputs["preview"], outputs["full"]))
        self.assertTrue(np.array_equal(outputs["bypass"], x))
        self.assertGreater(np.max(np.abs(outputs["collapse"] - outputs["full"])), .01)


def run(instrument, effect, out):
    import afterimage_receipt_host as chain
    import host_audition as h
    out.mkdir(parents=True, exist_ok=True)
    report = dict(scope="exact 0.2.0 Windows binaries; settled RF03 on AC01/AC02 musical signal", cases=[])
    def persist():
        (out / "upgraded-chain.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    try:
        ab, report["instrument"] = chain.package(instrument, out/"instrument", ac.NEW)
        fb, report["effect"] = chain.package(effect, out/"effect", rf.NEW)
        for rate in ac.RATES:
            reference = {}
            for block in ac.BLOCKS:
                for depth in (1, 2, 3):
                    s = ac.state(depth)
                    p = chain.prepare(ab, ac.NEW, s, rate, block, True)
                    # Leading silence allows effect wet smoothing to settle.
                    events = [(msg, t+.1) for msg, t in ac.events(ac.HISTORIES[0])]
                    n = 2*rate + rate//5
                    x = h.checked(p(events, duration=n/rate, sample_rate=rate,
                                    num_channels=2, buffer_size=block, reset=False), n)
                    h.verify_component(p, ac.NEW[3], s)
                    h.require(np.max(np.abs(x)) > .01 and np.max(np.abs(x[:, :rate//20])) < 1e-7,
                              "dry activity or leading silence")
                    for name, state in states():
                        c = dict(rate=rate, block=block, depth=depth, mode=name, status="started")
                        report["cases"].append(c); persist()
                        def render(saved=None):
                            f = chain.prepare(fb, rf.NEW, state, rate, block, False, saved)
                            y = h.checked(f(x.copy(), rate, buffer_size=block, reset=False), n)
                            h.verify_component(f, rf.NEW[3], state)
                            return y, f.preset_data
                        y, saved = render()
                        c["oracle_error"] = transfer_error(x, y, state)
                        c["restore_error"] = chain.error(y, render(saved)[0])
                        h.require(c["restore_error"] < 2e-6, "effect restore")
                        key = (depth, name)
                        if block == ac.BLOCKS[0]: reference[key] = y
                        else:
                            c["partition_error"] = chain.error(y, reference[key])
                            h.require(c["partition_error"] < 2e-6, "partition")
                        c["output"] = h.metrics(y)
                        c["status"] = "pass"; persist()
        report["complete"] = True
    except Exception as exc:
        report["error"] = repr(exc)
        raise
    finally:
        persist()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("instrument", "effect", "out"):
        p.add_argument("--"+name, type=Path)
    a = p.parse_args()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests)).wasSuccessful():
        raise SystemExit(1)
    if any((a.instrument, a.effect, a.out)):
        if not all((a.instrument, a.effect, a.out)):
            p.error("all three arguments required")
        run(a.instrument, a.effect, a.out)
