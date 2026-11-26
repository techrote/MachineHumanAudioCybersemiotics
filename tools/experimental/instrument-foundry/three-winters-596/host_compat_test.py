"""Windows Pedalboard compatibility witness; no DAW or callback timing claim."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import unittest
import numpy as np

CID = b"D1195E6E292C442CB550AE834977E4CD"
HEADER = struct.Struct("<4si32sq")
LIST = struct.Struct("<4si")
ENTRY = struct.Struct("<4sqq")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def preset(lane):
    v = [0., 0., 0., 0., 0., 0., 0., .25, 0., 0., 0., 0., .25, .75, 1., 0., 0., 0., .25]
    v[8 + lane] = 1.
    state = b"TW02" + struct.pack("<19f", *v)
    return HEADER.pack(b"VST3", 1, CID, HEADER.size + len(state)) + state + LIST.pack(b"List", 1) + ENTRY.pack(b"Comp", HEADER.size, len(state))


def component(raw):
    sig, version, cid, offset = HEADER.unpack_from(raw)
    require(sig == b"VST3" and version == 1 and cid == CID, "preset identity")
    require(HEADER.size <= offset <= len(raw) - LIST.size, "preset list offset")
    tag, count = LIST.unpack_from(raw, offset)
    require(tag == b"List" and 0 <= count <= 32 and offset + LIST.size + count * ENTRY.size <= len(raw), "preset list")
    found = []
    for i in range(count):
        name, start, size = ENTRY.unpack_from(raw, offset + LIST.size + i * ENTRY.size)
        require(HEADER.size <= start <= offset and 0 <= size <= offset - start, "chunk extent")
        if name == b"Comp":
            found.append(raw[start:start + size])
    require(len(found) == 1, "component chunk")
    return found[0]


def witness(x, rate, lane):
    require(x.shape == (2, int(.4 * rate)) and np.isfinite(x).all(), "render shape or finite")
    require(np.max(np.abs(x)) <= 1., "amplitude bound")
    require(np.max(np.abs(x[:, :rate // 50])) < 1e-6, "pre-note signal")
    require(np.max(np.abs(x[:, -rate // 10:])) < 1e-6, "release signal")
    settled = x[:, rate // 10:rate // 5].astype(np.float64)
    peak = float(np.max(np.abs(settled)))
    require(peak > 1e-4, "silent sustained note")
    fundamental = None
    if lane >= 0:
        if lane == 1:
            require(np.max(np.abs(x[0] - x[1])) < 2e-6, "pause channel mismatch")
        else:
            require(np.max(np.abs(x[1 if lane == 0 else 0])) < 2e-6, "inactive lane audible")
        tone = settled[1 if lane == 2 else 0]
        t = np.arange(len(tone)) / rate
        basis = np.exp(2j * np.pi * 440 * t)
        c = 2 * np.mean(tone * basis.conj())
        fundamental = float(abs(c))
        require(fundamental > 1e-4 and np.sqrt(np.mean((tone - np.real(c * basis)) ** 2)) < 2e-4, "wrong-pitch or nonstationary tone")
    return dict(peak=peak, fundamental=fundamental, float32_sha256=hashlib.sha256(np.asarray(x, dtype="<f4").tobytes()).hexdigest())


class Tests(unittest.TestCase):
    def test_preset(self):
        for lane in range(3):
            data = component(preset(lane))
            self.assertEqual(len(data), 80)
            self.assertEqual(struct.unpack("<19f", data[4:])[8:11], tuple(float(i == lane) for i in range(3)))
        with self.assertRaises(ValueError):
            component(preset(0)[:-1])

    def test_witness(self):
        for rate in (44100, 48000, 96000):
            for lane in range(3):
                x = np.zeros((2, int(.4 * rate)), dtype=np.float32)
                tone = .04 * np.sin(2 * np.pi * 440 * np.arange(rate // 5) / rate)
                i = rate // 50
                if lane != 2:
                    x[0, i:i + len(tone)] = tone
                if lane != 0:
                    x[1, i:i + len(tone)] = tone
                witness(x, rate, lane)
                with self.assertRaises(ValueError):
                    witness(x * 0, rate, lane)
                with self.assertRaises(ValueError):
                    witness(x[::-1] if lane != 1 else np.stack((x[0], x[1] * 0)), rate, lane)
                y = x.copy()
                y[:, -1] = .1
                with self.assertRaises(ValueError):
                    witness(y, rate, lane)


def run(bundle, out):
    import pedalboard as pb
    bundle = bundle.resolve(strict=True)
    binary = bundle / "Contents" / "x86_64-win" / bundle.name
    report = dict(scope=__doc__, pedalboard=pb.__version__, numpy=np.__version__, binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), cases=[])
    def persist():
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    def open_plugin():
        for path in (bundle, binary):
            try:
                p = pb.load_plugin(str(path))
            except (ImportError, RuntimeError):
                continue
            require(p.is_instrument and p.name == "MHAC Three Winters", "instrument identity")
            return p, str(path)
        raise RuntimeError("bundle and inner-module loading failed")
    persist()
    for rate in (44100, 48000, 96000):
        for lane in (-1, 0, 1, 2):
            reference = None
            for block in (257, 1024):
                case = dict(rate=rate, lane=lane, block=block, status="started")
                report["cases"].append(case)
                persist()
                try:
                    p, path = open_plugin()
                    case["load_path"] = path
                    if lane >= 0:
                        z = p([], duration=.05, sample_rate=rate, num_channels=2, buffer_size=block)
                        require(np.isfinite(z).all() and np.max(np.abs(z)) < 1e-7, "preparation not silent")
                        raw = preset(lane)
                        p.preset_data = raw
                        require(component(p.preset_data) == component(raw), "preset import mismatch")
                    x = p([(bytes((0x90, 69, 100)), .02), (bytes((0x80, 69, 0)), .25)], duration=.4, sample_rate=rate, num_channels=2, buffer_size=block, reset=lane < 0)
                    case.update(witness(x, rate, lane))
                    if lane >= 0:
                        require(component(p.preset_data) == component(raw), "state changed during render")
                    if reference is None:
                        reference = x.copy()
                    else:
                        error = float(np.max(np.abs(x - reference)))
                        case["partition_max_error"] = error
                        require(error < 2e-5, "block partition mismatch")
                    case["status"] = "pass"
                except Exception as e:
                    case.update(status="fail", error=repr(e))
                finally:
                    persist()
    report["complete"] = True
    persist()
    require(len(report["cases"]) == 24 and all(c["status"] == "pass" for c in report["cases"]), "host matrix failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    tests = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    require(tests.wasSuccessful(), "oracle self-tests")
    if args.bundle:
        require(args.out is not None, "missing receipt path")
        run(args.bundle, args.out)
