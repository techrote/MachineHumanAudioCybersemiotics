#!/usr/bin/env python3
"""MHAC-X001: circle-mode aliasing, shifted observer, and original stereo synthesis.

All observations and WAV data are synthetic. Not a Kaluza-Klein simulation,
an ML model, a psychophysical result, or an operational auditory code.
Python 3.11+, standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import wave

DEFAULT_SENSORS = 8
DEFAULT_MODE = 2
DEFAULT_RADIUS = 1.0
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_DURATION = 3.0
DEFAULT_REVOLUTIONS_PER_SECOND = 55.0


def mode_value(mode: int, theta: float) -> float:
    """Scalar cosine harmonic evaluated on a circle at angular position theta."""
    if not isinstance(mode, int) or mode < 0:
        raise ValueError("mode must be a nonnegative integer")
    if not math.isfinite(theta):
        raise ValueError("theta must be finite")
    return math.cos(mode * theta)


def sensor_values(mode: int, sensors: int, offset: float = 0.0) -> tuple[float, ...]:
    """N equally spaced probes with a common angular offset."""
    if not isinstance(sensors, int) or sensors < 3:
        raise ValueError("at least three sensors required")
    if not math.isfinite(offset):
        raise ValueError("offset must be finite")
    return tuple(
        mode_value(mode, 2 * math.pi * j / sensors + offset)
        for j in range(sensors)
    )


def max_abs_difference(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("nonempty equally sized observations required")
    return max(abs(a - b) for a, b in zip(left, right))


def make_stereo_wav(
    low_mode: int,
    high_mode: int,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    duration: float = DEFAULT_DURATION,
    revolutions_per_second: float = DEFAULT_REVOLUTIONS_PER_SECOND,
) -> bytes:
    """Make 16-bit PCM: left=f_low(theta(t)), right=f_high(theta(t)).

    theta(t)=2*pi*revolutions_per_second*t. The two mode frequencies are
    mode*revolutions_per_second Hz, a chosen *artistic* correspondence.
    """
    if min(low_mode, high_mode) < 0:
        raise ValueError("mode numbers must be nonnegative")
    if not (8000 <= sample_rate <= 192000):
        raise ValueError("sample rate out of supported range")
    if not (0.05 <= duration <= 30.0) or not math.isfinite(duration):
        raise ValueError("duration out of supported range")
    if not math.isfinite(revolutions_per_second) or revolutions_per_second <= 0:
        raise ValueError("revolutions per second must be finite and positive")
    if max(low_mode, high_mode) * revolutions_per_second >= sample_rate / 2:
        raise ValueError("the moving-probe tone exceeds the Nyquist frequency")
    count = round(sample_rate * duration)
    attack_release = min(0.035, duration / 4)
    pcm = bytearray()
    for i in range(count):
        t = i / sample_rate
        envelope = min(1.0, t / attack_release, (duration - t) / attack_release)
        theta = 2 * math.pi * revolutions_per_second * t
        left = 0.26 * envelope * mode_value(low_mode, theta)
        right = 0.26 * envelope * mode_value(high_mode, theta)
        pcm.extend(struct.pack(
            "<hh",
            int(max(-32767, min(32767, round(left * 32767)))),
            int(max(-32767, min(32767, round(right * 32767)))),
        ))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(pcm)
    return buf.getvalue()


def make_experiment(
    sensors: int = DEFAULT_SENSORS,
    low_mode: int = DEFAULT_MODE,
    radius: float = DEFAULT_RADIUS,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    duration: float = DEFAULT_DURATION,
    revolutions_per_second: float = DEFAULT_REVOLUTIONS_PER_SECOND,
) -> tuple[dict, list[tuple], list[tuple], bytes]:
    """Return deterministic receipt, exact/shifted probe rows, and generated WAV."""
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    if not isinstance(sensors, int) or sensors < 3:
        raise ValueError("at least three sensors required")
    if not isinstance(low_mode, int) or low_mode < 0:
        raise ValueError("low mode must be a nonnegative integer")
    high_mode = low_mode + sensors
    shift = math.pi / (2 * sensors)
    low = sensor_values(low_mode, sensors)
    high = sensor_values(high_mode, sensors)
    shifted_low = sensor_values(low_mode, sensors, shift)
    shifted_high = sensor_values(high_mode, sensors, shift)
    exact_error = max_abs_difference(low, high)
    shifted_error = max_abs_difference(shifted_low, shifted_high)
    if exact_error > 1e-10:
        raise AssertionError("sampling alias invariant failed")
    if shifted_error <= 1e-8:
        raise ValueError("chosen shifted observer does not distinguish this mode pair")
    wav = make_stereo_wav(
        low_mode, high_mode, sample_rate, duration, revolutions_per_second
    )
    rows = [
        (j, 2 * math.pi * j / sensors, low[j], high[j], abs(low[j] - high[j]))
        for j in range(sensors)
    ]
    shifted_rows = [
        (j, 2 * math.pi * j / sensors + shift,
         shifted_low[j], shifted_high[j], abs(shifted_low[j] - shifted_high[j]))
        for j in range(sensors)
    ]
    receipt = {
        "type": "MHAC-X001-original-synthetic-experiment",
        "schema": 1,
        "provenance": "analytic cosine values, deterministic PCM16; no participants",
        "radius_arbitrary_units": radius,
        "sensor_count": sensors,
        "mode_a": low_mode,
        "mode_b": high_mode,
        "equispaced_max_abs_error": exact_error,
        "shifted_max_abs_error": shifted_error,
        "shifted_offset_radians": shift,
        "eigenvalue_a_of_minus_d2_dy2": (low_mode / radius) ** 2,
        "eigenvalue_b_of_minus_d2_dy2": (high_mode / radius) ** 2,
        "wav_rate_hz": sample_rate,
        "wav_seconds": duration,
        "probe_revolutions_per_second": revolutions_per_second,
        "tone_a_hz": low_mode * revolutions_per_second,
        "tone_b_hz": high_mode * revolutions_per_second,
        "wav_frames": round(sample_rate * duration),
        "wav_sha256": hashlib.sha256(wav).hexdigest(),
        "validity": {
            "discrete_alias": exact_error < 1e-10,
            "shift_breaks_pair": shifted_error > 1e-8,
            "mode_eigenvalues_distinct": low_mode != high_mode,
        },
        "interpretation_limit": (
            "Equal discrete samples do not mean equal continuous fields; "
            "the acoustic timbres/pitches are synthetic and not a KK particle spectrum."
        ),
    }
    return receipt, rows, shifted_rows, wav


def write_csv(path: Path, rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(("probe_id", "theta_radians", "mode_a", "mode_b", "difference_abs"))
        for row in rows:
            writer.writerow((row[0],) + tuple(f"{v:.15f}" for v in row[1:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/mhac-x001"))
    parser.add_argument("--sensors", type=int, default=DEFAULT_SENSORS)
    parser.add_argument("--mode", type=int, default=DEFAULT_MODE)
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS)
    parser.add_argument("--rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--seconds", type=float, default=DEFAULT_DURATION)
    parser.add_argument("--revolutions", type=float, default=DEFAULT_REVOLUTIONS_PER_SECOND)
    args = parser.parse_args()
    receipt, rows, shifted_rows, wav = make_experiment(
        args.sensors, args.mode, args.radius, args.rate, args.seconds, args.revolutions
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "fixed-probes.csv", rows)
    write_csv(args.out / "shifted-probes.csv", shifted_rows)
    (args.out / "moving-witness-stereo.wav").write_bytes(wav)
    (args.out / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "alias_max_error": receipt["equispaced_max_abs_error"],
        "shifted_max_error": receipt["shifted_max_abs_error"],
        "wav_sha256": receipt["wav_sha256"],
        "output": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
