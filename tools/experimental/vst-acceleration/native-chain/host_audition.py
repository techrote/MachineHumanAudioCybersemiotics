"""Windows x64 host audition of exact foundry archives; not official SDK validator."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import stat
import struct
import unittest
import wave
import zipfile

import numpy as np
import pedalboard as pb
import preset_bank as bank

PINS = (
    ("MHACGoldenReceipt", "299400212aff8213b99131474d8092be5a396658197727621245ca4a7a94e9c3", bank.G),
    ("MHACFreezeSocket", "e3791e9129d6344d18b63fe64018437a4f1a60ca6d978e713cc3c9f9e1c34d9a", bank.F),
)
SDK = "9fad9770f2ae8542ab1a548a68c1ad1ac690abe0"
RATE = 48000
DURATION = 4.5
NOTES = [(0,48,102),(137,55,95),(503,60,83),(1299,67,95),(1701,52,102),(2101,57,89)]
MIDI = [(bytes((0x90,p,v)), t/1000) for t,p,v in NOTES] + [
    (bytes((0x80,p,0)), 2.401) for _,p,_ in NOTES]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unpack(path, dest, pin):
    name, digest, cid = pin
    raw = path.read_bytes()
    require(sha(raw) == digest, "wrong outer artifact SHA256")
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        require(outer.testzip() is None, "outer CRC")
        candidates = [i for i in outer.namelist() if i.endswith(".zip")]
        require(len(candidates) == 1, "expected one inner archive")
        inner = outer.read(candidates[0])
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        require(z.testzip() is None, "inner CRC")
        receipt = z.read("BUILD-SOURCE.txt").decode("utf-8-sig").splitlines()
        require("sdk="+SDK in receipt and "source="+bank.PINS[cid][1] in receipt, "source receipt")
        seen = set()
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            require(not p.is_absolute() and ".." not in p.parts and "\\" not in item.filename
                    and ":" not in item.filename and all(x.rstrip(" .") == x for x in p.parts)
                    and not stat.S_ISLNK(item.external_attr >> 16), "unsafe archive path")
            key = str(p).casefold()
            require(key not in seen, "duplicate archive path")
            seen.add(key)
            target = dest.joinpath(*p.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(item))
    bundle = (dest / (name+".vst3")).resolve(strict=True)
    binary = bundle / "Contents" / "x86_64-win" / (name+".vst3")
    require(binary.is_file(), "missing Windows x64 binary")
    return bundle, dict(outer_sha256=digest, inner_sha256=sha(inner), binary_sha256=sha(binary.read_bytes()),
                        source=bank.PINS[cid][1], sdk=SDK)


def checked(audio, frames):
    require(audio.shape == (2, frames), "unexpected stereo frame shape")
    require(np.isfinite(audio).all(), "nonfinite output")
    require(float(np.max(np.abs(audio))) <= 1.0, "out-of-range output")
    return audio


def metrics(audio):
    x = audio.astype(np.float64)
    return dict(peak=float(np.max(np.abs(x))), rms=float(np.sqrt(np.mean(x*x))),
                float32_sha256=sha(np.asarray(audio, dtype="<f4").tobytes()))


def compare(dry, wet):
    require(metrics(dry)["rms"] > 1e-5, "silent instrument")
    require(float(np.max(np.abs(dry[:,-480:]))) < 1e-5, "instrument did not release")
    require(np.max(np.abs(wet-dry)) > 1e-4, "effect did not alter audio")
    require(np.max(np.abs(wet)-np.abs(dry)) < 2e-6, "unexpected effect gain")
    return dict(dry=metrics(dry), wet=metrics(wet))


def wav(path, audio):
    # Fixed common gain, no normalization or playback.
    with wave.open(str(path), "wb") as w:
        w.setparams((2,2,RATE,0,"NONE","not compressed"))
        w.writeframes(np.rint(audio.T*8192).astype("<i2").tobytes())


def open_plugin(bundle):
    # JUCE file scanning expects absolute native paths. Record an inner-module
    # fallback separately: success there would not establish bundle scanning.
    bundle = bundle.resolve(strict=True)
    binary = bundle / "Contents" / "x86_64-win" / bundle.name
    errors = []
    for path in (bundle, binary):
        try:
            plugin = pb.load_plugin(str(path))
            print("HOST LOAD:", path, plugin.name, flush=True)
            return plugin
        except (ImportError, RuntimeError) as e:
            errors.append(str(path)+": "+str(e))
    # Diagnostic only, in a separate process to avoid contaminating host state.
    import subprocess
    import sys
    diagnostic = subprocess.run(
        [sys.executable, "-c", "import ctypes,sys; d=ctypes.WinDLL(sys.argv[1]); print(bool(d.GetPluginFactory))", str(binary)],
        capture_output=True, text=True, timeout=20)
    raise RuntimeError("\n".join(errors)+f"\nWinDLL probe exit={diagnostic.returncode}: {diagnostic.stdout} {diagnostic.stderr}")


def prepare_instrument(p, rate, block):
    # Pedalboard 0.9.23's cold/reset instrument path overwrote restored
    # component state with defaults. Prepare a silent stream first, then
    # restore the requested preset and continue with reset=False.
    silence = p([], duration=.05, sample_rate=rate, num_channels=2, buffer_size=block)
    require(np.isfinite(silence).all() and np.max(np.abs(silence)) < 1e-7,
            "instrument preparation not silent")


def component(raw):
    sig, version, cid, offset = bank.HEADER.unpack_from(raw)
    require(sig == b"VST3" and version == 1, "host preset header")
    tag, count = bank.LIST.unpack_from(raw,offset)
    require(tag == b"List" and 0 <= count <= 32, "host preset list")
    chunks = {}
    for i in range(count):
        name, start, size = bank.ENTRY.unpack_from(raw,offset+bank.LIST.size+i*bank.ENTRY.size)
        require(start >= bank.HEADER.size and size >= 0 and start+size <= offset, "host chunk extent")
        chunks[name.decode("ascii")] = raw[start:start+size].hex()
    return dict(class_id=cid.decode("ascii"),chunks=chunks)


def verify_component(p, cid, expected):
    state = component(p.preset_data)
    require(state["class_id"] == cid, "host-export class mismatch")
    require(state["chunks"].get("Comp") == expected.hex(), "host component parameters differ from request")


def load(bundle, cid, index, rate=RATE, block=257):
    p = open_plugin(bundle)
    _, _, values = bank.BANK[index]
    require(bank.BANK[index][0] == cid, "preset class mismatch")
    if cid == bank.G:
        prepare_instrument(p,rate,block)
    p.preset_data = bank.preset(cid, values)
    verify_component(p,cid,bank.state(cid,values))
    return p


def diagnose_golden_state(bundle, out, report):
    """Locate whether imported instrument state is lost before or during process."""
    report["golden_state_diagnostic"] = []
    for method in ("cold_preset", "prepared_preset", "controller_gain"):
        p = open_plugin(bundle)
        case = dict(method=method, before=component(p.preset_data))
        report["golden_state_diagnostic"].append(case)
        try:
            if method == "prepared_preset":
                p([],duration=.05,sample_rate=RATE,num_channels=2,buffer_size=257)
            if method == "controller_gain":
                case["parameter_names"] = list(p.parameters)
                p.parameters["gain"].raw_value = .1
                case["controller_gain_readback"] = p.parameters["gain"].raw_value
            else:
                _, _, values = bank.BANK[4]
                raw = bank.preset(bank.G,values)
                case["requested"] = component(raw)
                p.preset_data = raw
            case["before_process"] = component(p.preset_data)
            signal = checked(p(MIDI,duration=DURATION,sample_rate=RATE,num_channels=2,
                               buffer_size=257,reset=(method != "prepared_preset")), int(RATE*DURATION))
            case["after_process"] = component(p.preset_data)
            case["signal"] = metrics(signal)
        except Exception as e:
            case["error"] = repr(e)
        finally:
            (out/"host-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
            print("GOLDEN STATE DIAGNOSTIC:",json.dumps(case),flush=True)


def run_preset_matrix(gpath, fpath, out, report):
    """Exercise every delivered preset in fresh real host instances, at three rates."""
    report["preset_matrix"] = []
    report["preset_matrix_scope"] = (
        "Static preset import and host-exported preset restoration; Hold is off. "
        "Freeze contract differentiation during active Hold is NOT tested.")
    def persist():
        (out/"host-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    persist()
    for rate in (44100, 48000, 96000):
        n = int(rate*DURATION)
        source = None
        gold_hashes = []
        for index, (cid, name, values) in enumerate(bank.BANK):
            instrument = cid == bank.G
            bundle = gpath if instrument else fpath
            case = dict(rate=rate, block=257, index=index, preset=name,
                        class_id=cid, input_preset_sha256=sha(bank.preset(cid,values)),
                        status="started")
            report["preset_matrix"].append(case)
            persist()
            try:
                p = load(bundle, cid, index, rate, 257)
                require(p.is_instrument if instrument else p.is_effect, "category mismatch")
                def render(plugin):
                    return checked(plugin(MIDI, duration=DURATION, sample_rate=rate,
                                          num_channels=2, buffer_size=257, reset=False) if instrument else
                                   plugin(source.copy(), rate, buffer_size=257), n)
                signal = render(p)
                case["output"] = metrics(signal)
                verify_component(p,cid,bank.state(cid,values))
                case["requested_component_retained"] = True
                case["tail_peak"] = float(np.max(np.abs(signal[:,-480:])))
                require(case["output"]["rms"] > 1e-5, "silent preset")
                if instrument:
                    gold_hashes.append(case["output"]["float32_sha256"])
                    if index == 0:
                        source = signal.copy()
                    require(case["tail_peak"] < 1e-5, "instrument did not release")
                else:
                    case["max_dry_difference"] = float(np.max(np.abs(signal-source)))
                    if index == 11:
                        require(case["max_dry_difference"] < 2e-6, "bypass not transparent")
                    else:
                        require(case["max_dry_difference"] > 1e-4, "effect did not alter audio")
                        require(np.max(np.abs(signal)-np.abs(source)) < 2e-6, "unexpected effect gain")
                saved = p.preset_data
                case["host_export_sha256"] = sha(saved)
                fresh = open_plugin(bundle)
                if instrument:
                    prepare_instrument(fresh,rate,257)
                fresh.preset_data = saved
                verify_component(fresh,cid,bank.state(cid,values))
                restored = render(fresh)
                verify_component(fresh,cid,bank.state(cid,values))
                case["restore_max_error"] = float(np.max(np.abs(restored-signal)))
                require(case["restore_max_error"] < 2e-5, "fresh-instance preset audio mismatch")
                case["status"] = "pass"
            except Exception as e:
                case["status"] = "fail"
                case["error"] = str(e)
                raise
            finally:
                persist()
                print("PRESET MATRIX:", json.dumps(case), flush=True)
        require(len(set(gold_hashes)) == 5, "unexpected instrument preset equivalence classes")
        require(gold_hashes[1] == gold_hashes[2], "designed affine deletion collision absent")
    report["preset_matrix_complete"] = True
    persist()


# Explicit controller edits BETWEEN streaming calls, not sample-offset host queues.
# Expected steady-state gain derived from the pinned Freeze Socket clock:
# rate=.5 -> 2 slots/s; hold at .75 s in slot B; mutate B,C at 1 s;
# release at 1.75 s. The paused clock resumes from its fractional position.
HOLD_WINDOWS = (.60, .85, 1.15, 1.65, 1.85, 2.10)
HOLD_EXPECTED = (
    (.25, .25, .25, .25, .10, 1.),
    (.25, .25, .90, .90, .90, .05),
    (.25, .25, .75, .10, .10, 1.),
)


def hold_witness(signal, rate, mode):
    checked(signal, int(2.25*rate))
    measured = []
    for start, expected in zip(HOLD_WINDOWS, HOLD_EXPECTED[mode]):
        # Stay far from events and the 5 ms maximum full-scale slew.
        window = signal[:, int(start*rate):int((start+.02)*rate)]
        require(np.max(np.abs(window[0]/.125-window[1]/(-.25))) < 2e-6,
                "Hold test stereo gain mismatch")
        gain = window[0]/.125
        require(np.max(np.abs(gain-expected)) < 2e-4,
                f"Hold mode {mode} at {start}s: expected {expected}, got {float(np.mean(gain))}")
        measured.append(float(np.mean(gain)))
    return measured


def run_hold_matrix(bundle, out, report):
    report["hold_matrix"] = []
    report["hold_scope"] = "Host controller edits between contiguous processing calls; not sample-offset queue automation."
    def persist():
        (out/"host-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    for rate in (44100,48000,96000):
        for mode in range(3):
            p = open_plugin(bundle)
            values = [.5,1.,1.,mode/2,0.,1.,.25,.75,.1,0.]
            p.preset_data = bank.preset(bank.F, values)
            verify_component(p,bank.F,bank.state(bank.F,values))
            case = dict(rate=rate, mode=mode, status="started", parameters=list(p.parameters))
            report["hold_matrix"].append(case)
            persist()
            pieces = []
            def render(seconds):
                frames = round(seconds*rate)
                x = np.empty((2,frames),dtype=np.float32)
                x[0] = .125
                x[1] = -.25
                pieces.append(checked(p(x,rate,buffer_size=257,reset=not pieces),frames))
            def edit(name,index,value):
                require(name in p.parameters, "missing controller parameter: "+name)
                p.parameters[name].raw_value = value
                require(abs(p.parameters[name].raw_value-value) < 1e-6, "controller readback mismatch")
                values[index] = value
            try:
                render(.75)
                edit("hold",4,1.)
                render(.25)
                edit("step_b",6,.90)
                edit("step_c",7,.05)
                render(.75)
                edit("hold",4,0.)
                render(.50)
                signal = np.concatenate(pieces,axis=1)
                case["gain_windows"] = hold_witness(signal,rate,mode)
                verify_component(p,bank.F,bank.state(bank.F,values))
                case["final_component_retained"] = True
                case["output"] = metrics(signal)
                case["status"] = "pass"
            except Exception as exc:
                case["status"] = "fail"
                case["error"] = str(exc)
                raise
            finally:
                persist()
                print("HOLD MATRIX:",json.dumps(case),flush=True)
    report["hold_matrix_complete"] = True
    persist()


def run(gold, freeze, out):
    require(platform.system() == "Windows" and platform.machine().lower() in ("amd64","x86_64"),
            "exact packages require native Windows x64")
    out.mkdir()
    gpath, gpin = unpack(gold, out/"gold", PINS[0])
    fpath, fpin = unpack(freeze, out/"freeze", PINS[1])
    report = dict(host="Pedalboard "+pb.__version__, numpy=np.__version__,
                  platform=platform.platform(), packages=[gpin,fpin], cases=[])
    (out/"host-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    n = int(RATE*DURATION)
    for block in (64, 257, 1024):
        g = load(gpath, bank.G, 0, RATE, block)
        f = load(fpath, bank.F, 6)
        require(g.is_instrument and f.is_effect, "wrong plugin category")
        dry = checked(g(MIDI, duration=DURATION, sample_rate=RATE, num_channels=2, buffer_size=block, reset=False), n)
        wet = checked(f(dry.copy(), RATE, buffer_size=block), n)
        case = compare(dry, wet)
        verify_component(g,bank.G,bank.state(bank.G,bank.BANK[0][2]))
        verify_component(f,bank.F,bank.state(bank.F,bank.BANK[6][2]))
        bypass = load(fpath, bank.F, 11)
        reference = checked(bypass(dry.copy(), RATE, buffer_size=block), n)
        require(np.max(np.abs(reference-dry)) < 2e-6, "bypass not transparent")
        # Host-produced state, restored to a new instance, not our offline decoder.
        for p, bundle, signal, instrument in ((g,gpath,dry,True),(f,fpath,wet,False)):
            saved = p.preset_data
            new = open_plugin(bundle)
            if instrument:
                prepare_instrument(new,RATE,block)
            new.preset_data = saved
            again = (new(MIDI, duration=DURATION, sample_rate=RATE, num_channels=2, buffer_size=block, reset=False)
                     if instrument else new(dry.copy(), RATE, buffer_size=block))
            checked(again,n)
            error = float(np.max(np.abs(again-signal)))
            case["instrument_restore_error" if instrument else "effect_restore_error"] = error
            require(error < 2e-5, "fresh-instance host state audio mismatch")
        case["block"] = block
        report["cases"].append(case)
        (out/"host-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(case), flush=True)
        if block == 257:
            wav(out/"dry.wav", dry)
            wav(out/"wet.wav", wet)
    diagnose_golden_state(gpath, out, report)
    run_preset_matrix(gpath, fpath, out, report)
    run_hold_matrix(fpath, out, report)


class Tests(unittest.TestCase):
    def test_real_builtin_effect_and_negative_controls(self):
        x = np.zeros((2, RATE), dtype=np.float32)
        x[:,:1000] = .25
        wet = pb.Gain(gain_db=-6)(x.copy(), RATE, buffer_size=257)
        checked(wet, RATE)
        self.assertGreater(compare(x,wet)["wet"]["rms"],0)
        for bad in (x[:1], x[:,:-1], x+np.nan, x+2):
            with self.assertRaises(ValueError):
                checked(bad,RATE)
        for dry, processed in ((x,x),(x,x*2),(x*0,x*0),(x+.1,x)):
            with self.assertRaises(ValueError):
                compare(dry,processed)

    def test_hold_witness_and_negative_controls(self):
        rate = 48000
        for mode, expected in enumerate(HOLD_EXPECTED):
            signal = np.zeros((2,int(2.25*rate)),dtype=np.float32)
            for start,gain in zip(HOLD_WINDOWS,expected):
                a,b = int(start*rate),int((start+.02)*rate)
                signal[0,a:b] = .125*gain
                signal[1,a:b] = -.25*gain
            np.testing.assert_allclose(hold_witness(signal,rate,mode),expected,atol=1e-6)
            for other in range(3):
                if other != mode:
                    with self.assertRaises(ValueError):
                        hold_witness(signal,rate,other)
            broken = signal.copy()
            broken[1] = 0
            with self.assertRaises(ValueError):
                hold_witness(broken,rate,mode)

    def test_wav(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"x.wav"
            x = np.array([[1.,-1.],[.5,-.5]],dtype=np.float32)
            wav(p,x)
            with wave.open(str(p),"rb") as w:
                self.assertEqual((w.getnchannels(),w.getframerate(),w.getnframes()),(2,RATE,2))
                self.assertEqual(struct.unpack("<4h",w.readframes(2)),(8192,4096,-8192,-4096))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold",type=Path)
    parser.add_argument("--freeze",type=Path)
    parser.add_argument("--out",type=Path)
    args = parser.parse_args()
    require(pb.__version__ == "0.9.23" and np.__version__ == "2.3.5","wrong host dependency version")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if any((args.gold,args.freeze,args.out)):
        require(all((args.gold,args.freeze,args.out)),"supply all three host arguments")
        run(args.gold,args.freeze,args.out)
    else:
        print("SELF-TEST ONLY; no external VST3 loaded")
