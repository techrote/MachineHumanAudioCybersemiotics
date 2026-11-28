"""ACCEL-007: exact Windows standard/XL Erasure Loom host latency and state witness.
Run alongside host_audition.py; this is host output alignment, not a direct ABI
latency query or DAW PDC certification. No external input samples.
"""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import unittest
import zipfile

import numpy as np
import host_audition as h
import preset_bank as bank

SOURCE = "2951e946577e2090926a9ee081f636809dd96d33"
PINS = (
    ("MHACErasureLoom", "bd7a41aeca9789e1ab34a957074ec1586be155f07cce2b95d1001bdd624a860b",
     "DC4F4B718CA24A61A3B728C4C77342EE", b"EL02", 144),
    ("MHACErasureLoomXL", "e3f2493d09dc1cb5ab498d22a44e79e2b5a55286ec2834eea647ddacd066b1b4",
     "B74B3910A48B4F3985C3264918E4C6F1", b"EX01", 9216),
)

def extract(path, dest, pin):
    name, digest, cid, _, _ = pin
    raw = path.read_bytes()
    h.require(h.sha(raw) == digest, "outer digest")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        h.require(z.testzip() is None and len(z.namelist()) == 1, "outer archive")
        inner = z.read(name+"-Windows-x64.zip")
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        h.require(z.testzip() is None, "inner CRC")
        receipt = z.read("BUILD-SOURCE.txt").decode("utf-8-sig").splitlines()
        h.require("source="+SOURCE in receipt and "sdk="+h.SDK in receipt, "exact source/SDK")
        root = name+".vst3"
        info = z.read(root+"/Contents/Resources/moduleinfo.json").decode("utf-8-sig")
        # SDK emits trailing commas; normalize this known syntax, not arbitrary JSON5.
        info = json.loads(re.sub(r",(\s*[}\]])", r"\1", info))
        classes = [c for c in info["Classes"] if c["Category"] == "Audio Module Class"]
        h.require(len(classes) == 1 and classes[0]["CID"] == cid and
                  classes[0]["Version"] == ("0.1.0" if name.endswith("XL") else "0.2.0") and
                  classes[0]["SDKVersion"] == "VST 3.8.0", "module identity")
        seen = set()
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            h.require(not p.is_absolute() and ".." not in p.parts and
                      "\\" not in item.filename and ":" not in item.filename and
                      all(x.rstrip(" .") == x for x in p.parts) and
                      not stat.S_ISLNK(item.external_attr >> 16), "unsafe path")
            key = str(p).casefold()
            h.require(key not in seen, "duplicate path")
            seen.add(key)
            if p.parts[0] != root or item.is_dir():
                continue
            target = dest.joinpath(*p.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(item))
    bundle = (dest/root).resolve(strict=True)
    binary = bundle/"Contents"/"x86_64-win"/root
    return bundle, dict(source=SOURCE, sdk=h.SDK, outer_sha256=digest,
                        inner_sha256=h.sha(inner), binary_sha256=h.sha(binary.read_bytes()),
                        processor_cid=cid)

def state(pin, values):
    _, _, _, magic, _ = pin
    h.require(len(values) == (10 if magic == b"EX01" else 9), "parameter count")
    h.require(all(np.isfinite(x) and 0 <= x <= 1 for x in values), "parameter range")
    return magic + struct.pack("<"+"d"*len(values), *values)

def preset(pin, values):
    body = state(pin, values)
    return (bank.HEADER.pack(b"VST3", 1, pin[2].encode("ascii"), bank.HEADER.size+len(body))
            + body + bank.LIST.pack(b"List", 1) + bank.ENTRY.pack(b"Comp", bank.HEADER.size, len(body)))

def load(bundle, pin, values):
    p = h.open_plugin(bundle)
    h.require(p.is_effect, "not an effect")
    p.preset_data = preset(pin, values)
    h.verify_component(p, pin[2], state(pin, values))
    return p

def shifted(x, lag):
    if not lag:
        return x.copy()
    y = np.zeros_like(x)
    y[:, lag:] = x[:, :-lag]
    return y

def identify_delay(x, y, latency):
    errors = {d: float(np.max(np.abs(y-shifted(x,d)))) for d in (0, latency)}
    matches = [d for d, e in errors.items() if e < 2e-6]
    h.require(len(matches) == 1, "bypass neither uniquely compensated nor raw: "+repr(errors))
    return matches[0], errors

def align(y, lag):
    if not lag:
        return y.copy()
    x = np.zeros_like(y)
    x[:, :-lag] = y[:, lag:]
    return x

def stimulus(rate):
    # Deliberately asymmetric impulses plus independent two-channel chirp and
    # discontinuous pulses. Trailing silence exceeds both declared tails.
    n = rate*2
    x = np.zeros((2,n), dtype=np.float32)
    t = np.arange(rate, dtype=np.float64)/rate
    x[0, rate//4:rate//4+rate] = .095*np.sin(2*np.pi*(93*t+810*t*t))
    x[1, rate//4:rate//4+rate] = .065*np.cos(2*np.pi*(137*t+320*t*t))
    x[0, 67] = .25
    x[1, 113] = -.1875
    x[0, rate//2:rate//2+37] += .0625
    return x

def options(pin, mode):
    # Dyadic normalized values avoid host rounding ambiguity. Full wet,
    # deliberately erasure-heavy, bounded budget 2.875; no human claim.
    v = [1.,0.,.125,1.,1.,1.,0.,0.,0.]
    if mode == "bypass":
        v[6] = 1.
    elif mode == "dropout":
        v[3] = 0.
    elif mode == "soft":
        v[7:9] = [.5,.5]
    elif mode not in ("fine","medium","coarse"):
        raise ValueError("unknown mode")
    if pin[3] == b"EX01":
        v.append({"medium":.5,"coarse":1.}.get(mode,0.))
    return v

def run(archives, out):
    out.mkdir(parents=True, exist_ok=True)
    report = dict(scope="Windows host effect alignment/state; not raw ABI or sample-offset automation",
                  packages=[], cases=[])
    def persist():
        (out/"loom-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    persist()
    for path,pin in zip(archives,PINS):
        bundle, receipt = extract(path,out/pin[0],pin)
        report["packages"].append(receipt)
        persist()
        for rate in (44100,48000,96000):
            x = stimulus(rate)
            reference = {}
            for block in (257,1024):
                lag = None
                hashes = {}
                modes = ("bypass","fine","dropout","soft") + (("medium","coarse") if pin[3] == b"EX01" else ())
                for mode in modes:
                    case = dict(plugin=pin[0], rate=rate, block=block, mode=mode,
                                declared_latency=pin[4], status="started")
                    report["cases"].append(case)
                    persist()
                    try:
                        v = options(pin,mode)
                        p = load(bundle,pin,v)
                        y = h.checked(p(x.copy(),rate,buffer_size=block),x.shape[1])
                        h.verify_component(p,pin[2],state(pin,v))
                        case["component_retained"] = True
                        if mode == "bypass":
                            lag, errors = identify_delay(x,y,pin[4])
                            case["bypass_errors"] = errors
                        h.require(lag is not None, "no bypass alignment reference")
                        case["observed_lag"] = lag
                        a = align(y,lag)
                        case["output"] = h.metrics(a)
                        case["max_change"] = float(np.max(np.abs(a-x)))
                        if mode != "bypass":
                            h.require(case["max_change"] > 1e-4, "effect indistinguishable from bypass")
                            h.require(case["output"]["rms"] > 1e-5, "silent output")
                        tail_start = rate*5//4 + 2*pin[4]
                        h.require(float(np.max(np.abs(a[:,tail_start:]))) < 2e-6, "tail beyond contract")
                        saved = p.preset_data
                        fresh = h.open_plugin(bundle)
                        fresh.preset_data = saved
                        h.verify_component(fresh,pin[2],state(pin,v))
                        z = h.checked(fresh(x.copy(),rate,buffer_size=block),x.shape[1])
                        h.verify_component(fresh,pin[2],state(pin,v))
                        case["restore_max_error"] = float(np.max(np.abs(z-y)))
                        h.require(case["restore_max_error"] < 2e-6, "fresh state waveform mismatch")
                        if block == 257:
                            reference[mode] = a.copy()
                        else:
                            case["block_max_error"] = float(np.max(np.abs(a-reference[mode])))
                            h.require(case["block_max_error"] < 2e-6, "block-dependent aligned output")
                        hashes[mode] = case["output"]["float32_sha256"]
                        if rate == 48000 and block == 257:
                            h.wav(out/(pin[0]+"-"+mode+".wav"),a)
                        case["status"] = "pass"
                    except Exception as e:
                        case["status"] = "fail"
                        case["error"] = repr(e)
                        raise
                    finally:
                        persist()
                        print("LOOM HOST:", json.dumps(case), flush=True)
                h.require(len(set(hashes.values())) == len(hashes), "distinct settings collapsed")
    report["complete"] = True
    persist()

class Tests(unittest.TestCase):
    def test_delay_oracle(self):
        for rate in (44100,48000,96000):
            x = stimulus(rate)
            for pin in PINS:
                for d in (0,pin[4]):
                    y = shifted(x,d)
                    self.assertEqual(identify_delay(x,y,pin[4])[0],d)
                    np.testing.assert_array_equal(align(y,d),x)
                with self.assertRaises(ValueError):
                    identify_delay(x,shifted(x,1),pin[4])
                with self.assertRaises(ValueError):
                    identify_delay(x,np.zeros_like(x),pin[4])
    def test_state(self):
        for pin in PINS:
            v = options(pin,"soft")
            raw = preset(pin,v)
            s = h.component(raw)
            self.assertEqual(s["class_id"],pin[2])
            self.assertEqual(s["chunks"]["Comp"],state(pin,v).hex())
            self.assertEqual(len(state(pin,v)),84 if pin[3]==b"EX01" else 76)
            with self.assertRaises(ValueError):
                state(pin,[float("nan")]+v[1:])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--standard",type=Path,required=True)
    parser.add_argument("--xl",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    tests = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    h.require(tests.wasSuccessful(),"oracle self-tests")
    run((args.standard,args.xl),args.out)
