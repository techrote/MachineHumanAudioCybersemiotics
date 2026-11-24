"""MHAC-T007 synthetic received-channel diagnostic; no psychoacoustic model.

Standard-library only. Linear amplitudes never represent physical SPL, listener
thresholds, source authority, verified event truth or communication accuracy.
"""
from __future__ import annotations
import hashlib
import json
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEMANTIC_FIELDS = ("source_id", "event_id", "state_version", "action_id", "truth_status")


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def _sine(freq: float, t: int, rate: int):
    return math.sin(2 * math.pi * freq * t / rate)


def synthesis(cue: dict, rate: int, duration_ms: int):
    """Return (L, R) with no IO. All stimuli are invented and uncalibrated."""
    assert 0 < rate <= 96000 and duration_ms > 0
    n = rate * duration_ms // 1000
    assert n > 0 and n < 1000000
    left, right = [], []
    pulse_starts = cue.get("pulse_starts_ms", [])
    for t in range(n):
        ms = 1000 * t / rate
        a = cue["amplitude"]
        if cue["kind"] == "pulsed":
            a = 0.0
            for i, start in enumerate(pulse_starts):
                if start <= ms < start + cue["pulse_width_ms"]:
                    a = cue.get("pulse_amplitudes", [cue["amplitude"]] * len(pulse_starts))[i]
                    break
        value = a * _sine(cue["frequency_hz"], t, rate)
        value += cue.get("background_amplitude", 0.0) * _sine(1100, t, rate)
        if "secondary_frequency_hz" in cue:
            value += cue["secondary_amplitude"] * _sine(cue["secondary_frequency_hz"], t, rate)
        if cue["kind"] == "spatial":
            left.append(value * cue["left_gain"])
            right.append(value * cue["right_gain"])
        else:
            left.append(value)
            right.append(value)
    assert max(max(map(abs, left)), max(map(abs, right))) < 1
    return left, right


def apply(signal, transform: dict, rate: int):
    """Independent toy processing on each channel; output contains spatial_defined flag."""
    left, right = signal
    kind = transform["kind"]
    spatial_defined = kind not in {"mono", "mute"}
    if kind == "mono":
        mix = [(l + r) / 2 for l, r in zip(left, right)]
        return (mix[:], mix[:]), False
    if kind == "identity":
        return (left[:], right[:]), spatial_defined
    if kind == "gain":
        return ([x * transform["gain_linear"] for x in left],
                [x * transform["gain_linear"] for x in right]), spatial_defined
    if kind == "mute":
        return ([0.0]*len(left), [0.0]*len(right)), False
    def one(xs):
        if kind == "moving_average_fir":
            taps = transform["taps"]
            # causal FIR, explicit zero-initial conditions and *fixed* DC normalization
            prefix = [0.0]
            for x in xs:
                prefix.append(prefix[-1] + x)
            return [(prefix[i+1] - prefix[max(0, i-taps+1)]) / taps for i in range(len(xs))]
        if kind == "reflection":
            d = transform["delay_samples"]
            g = transform["reflection_gain"]
            return [x + (g*xs[i-d] if i >= d else 0) for i, x in enumerate(xs)]
        if kind == "masker":
            return [x+transform["amplitude"]*_sine(transform["frequency_hz"], i, rate)
                    for i,x in enumerate(xs)]
        if kind == "gate":
            th = transform["threshold_linear"]
            return [x if abs(x) >= th else 0.0 for x in xs]
        if kind == "compressor":
            atk = math.exp(-1.0/(rate*transform["attack_ms"]/1000))
            rel = math.exp(-1.0/(rate*transform["release_ms"]/1000))
            env=0.0
            out=[]
            for x in xs:
                mag=abs(x)
                coeff=atk if mag>env else rel
                env=coeff*env + (1-coeff)*mag
                th=transform["threshold_linear"]
                gain=(th / env)**(1-1/transform["ratio"]) if env>th else 1.0
                out.append(x*gain*transform["makeup_linear"])
            return out
        raise ValueError("unknown transform: " + str(kind))
    return (one(left), one(right)), spatial_defined


def _rms(xs):
    return math.sqrt(sum(x*x for x in xs)/len(xs)) if xs else 0.0


def _freq_mag(xs, rate, freq):
    # Deterministic complex projection, not calibrated filterbank or spectrogram.
    re = sum(x*math.cos(2*math.pi*freq*i/rate) for i,x in enumerate(xs))
    im = sum(x*math.sin(2*math.pi*freq*i/rate) for i,x in enumerate(xs))
    return math.hypot(re, im)*2/len(xs)


def _pulse_frames(xs, rate):
    k = rate//100  # 10-ms window; exact integer only for declared fixture rate
    assert k > 0
    return [_rms(xs[i:i+k]) for i in range(0, len(xs), k)]


def features(signal, rate: int, spatial_defined=True):
    l, r = signal
    assert len(l) == len(r) and l
    mid = [(x+y)/2 for x,y in zip(l,r)]
    peak = max(max(map(abs, l)), max(map(abs, r)))
    rms_l, rms_r = _rms(l), _rms(r)
    overall = math.sqrt((rms_l*rms_l+rms_r*rms_r)/2)
    frames = _pulse_frames(mid,rate)
    frame_peak = max(frames)
    if frame_peak <= 1e-10:
        count = 0
        active_frac = None
        hi_lo = None
    else:
        on = [x >= max(0.08*frame_peak,1e-7) for x in frames]
        count = sum(1 for i,x in enumerate(on) if x and (i==0 or not on[i-1]))
        active_frac = sum(on)/len(on)
        e_lo = _freq_mag(mid,rate,500)
        e_hi = _freq_mag(mid,rate,1500)
        floor = 1e-6 * max(e_lo, e_hi)
        hi_lo = (20*math.log10((e_hi+floor)/(e_lo+floor))
                 if max(e_lo, e_hi) > 1e-9 else None)
    ild = (20*math.log10(rms_l/rms_r)
           if spatial_defined and rms_l > 1e-10 and rms_r > 1e-10 else None)
    # An end-window diagnostic, NOT an objective noise estimate for arbitrary cues.
    tail = _rms(mid[-rate//5:])
    return {"rms":round(overall,6),"peak":round(peak,6),
            "crest_factor":round(peak/overall,6) if overall>1e-10 else None,
            "pulse_groups_proxy":count, "active_frame_fraction":_round(active_frac),
            "high_low_projection_db":_round(hi_lo), "interaural_level_db":_round(ild),
            "tail_rms":round(tail,6), "clipped_sample_count":sum(abs(x)>1 for x in l+r)}


def _round(v):
    return round(v,6) if v is not None else None


def waveform_sha(signal):
    h=hashlib.sha256()
    # Signed integer PCM test-only; quantization format and byte order are fixed.
    for channel in signal:
        for x in channel:
            value=max(-32767,min(32767,round(x*32767)))
            h.update(struct.pack('<h',value))
    return h.hexdigest()


def pair_distance(a,b):
    """A vector, not a scalar 'robustness' score; undefined axes remain null."""
    axes={"pulse_groups_proxy":1,"active_frame_fraction":1,
          "high_low_projection_db":1,"interaural_level_db":1}
    return {k: _round(abs(a[k]-b[k])) if a[k] is not None and b[k] is not None else None
            for k in axes}


def run_all():
    cues = load("CUES.json")
    transforms = load("TRANSFORMS.json")
    assert cues["sample_rate_hz"] == 8000 and cues["duration_ms"] == 800
    rate=cues["sample_rate_hz"]
    assert len(set(c["id"] for c in cues["cues"]))==len(cues["cues"])
    assert len(set(t["id"] for t in transforms["transforms"]))==len(transforms["transforms"])
    for c in cues["cues"]:
        assert c["truth_status"] == "hypothetical" and all(x in c for x in SEMANTIC_FIELDS)
    result={"schema":"mhac-t007-proxy-results-v1","scope":"synthetic engineering diagnostic only",
            "sample_rate_hz":rate,"duration_ms":cues["duration_ms"],
            "inputs_sha256":{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ("CUES.json","TRANSFORMS.json","CASES.json")},
            "runs":{}, "pairwise":{}}
    from itertools import combinations
    for transform in transforms["transforms"]:
        tid=transform["id"]
        runs={}
        for cue in cues["cues"]:
            raw=synthesis(cue,rate,cues["duration_ms"])
            output, valid=apply(raw,transform,rate)
            runs[cue["id"]]={"metadata":{k:cue[k] for k in SEMANTIC_FIELDS},
                             "waveform_sha256":waveform_sha(output),
                             "features":features(output,rate,valid)}
        result["runs"][tid]=runs
        result["pairwise"][tid]={a["id"]+"|"+b["id"]:pair_distance(runs[a["id"]]["features"],runs[b["id"]]["features"])
                                 for a,b in combinations(cues["cues"],2)}
    return result

if __name__ == '__main__':
    print(json.dumps(run_all(),sort_keys=True,indent=2))
