#!/usr/bin/env python3
"""MHAC-X005: absent-message oracle and deterministic "silence quartet".

Synthetic only. This module models receiver observations, not real users,
production failure detectors, human silence, or empirical auditory performance.
Python 3.11+, standard library only.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import wave

SAMPLE_RATE = 24000
SHARED_SILENCE_START = 1.0
SHARED_SILENCE_END = 2.5
DURATION = 4.0


@dataclass(frozen=True)
class World:
    name: str
    emitted_symbol: str | None
    emit_time: float | None
    deliver_time: float | None
    channel_outcome: str
    note: str

    def validate(self) -> None:
        if self.emitted_symbol is None:
            if self.emit_time is not None or self.deliver_time is not None:
                raise ValueError("no-emission world cannot have emission/delivery time")
        else:
            if self.emit_time is None or not math.isfinite(self.emit_time):
                raise ValueError("emitted symbol needs finite emit_time")
            if self.deliver_time is not None:
                if not math.isfinite(self.deliver_time) or self.deliver_time < self.emit_time:
                    raise ValueError("delivery must be finite and not precede emission")


@dataclass(frozen=True)
class LeaseState:
    status: str
    observed_at: float
    valid_until: float | None = None

    def validate(self) -> None:
        if self.status not in {"ACTIVE", "RESOLVED", "UNKNOWN"}:
            raise ValueError("unsupported lease status")
        if not math.isfinite(self.observed_at):
            raise ValueError("observed_at must be finite")
        if self.valid_until is not None and not math.isfinite(self.valid_until):
            raise ValueError("valid_until must be finite")
        if self.status == "ACTIVE" and self.valid_until is None:
            raise ValueError("ACTIVE lease needs valid_until")


def observed_prefix(world: World, horizon: float) -> tuple[tuple[float, str], ...]:
    """Receiver-local delivered symbols by a finite horizon."""
    world.validate()
    if not math.isfinite(horizon) or horizon < 0:
        raise ValueError("horizon must be finite and nonnegative")
    if world.deliver_time is None or world.deliver_time > horizon:
        return ()
    return ((world.deliver_time, world.emitted_symbol or ""),)


def indistinguishable_at(world_a: World, world_b: World, horizon: float) -> bool:
    return observed_prefix(world_a, horizon) == observed_prefix(world_b, horizon)


def partition_by_prefix(worlds: list[World], horizon: float) -> dict[tuple[tuple[float, str], ...], list[str]]:
    """Group finite hidden worlds into receiver-observation fibres."""
    result: dict[tuple[tuple[float, str], ...], list[str]] = {}
    for world in worlds:
        key = observed_prefix(world, horizon)
        result.setdefault(key, []).append(world.name)
    return result


def property_factors_through_prefix(
    worlds: list[World],
    horizon: float,
    labels: dict[str, str],
) -> bool:
    """Finite check of X001's observation-factorisation criterion.

    The property is recoverable from the receiver prefix iff every observation
    fibre contains only one property label.
    """
    fibres: dict[tuple[tuple[float, str], ...], set[str]] = {}
    for world in worlds:
        if world.name not in labels:
            raise ValueError("missing property label for " + world.name)
        key = observed_prefix(world, horizon)
        fibres.setdefault(key, set()).add(labels[world.name])
    return all(len(values) == 1 for values in fibres.values())


def async_counterexample(horizon: float = 5.0) -> tuple[World, World]:
    """Construct no-emission vs emitted-but-delayed worlds with same finite prefix."""
    if not math.isfinite(horizon) or horizon <= 0:
        raise ValueError("horizon must be finite and positive")
    no_emit = World(
        "no_event",
        None,
        None,
        None,
        "none",
        "The sender emits no event symbol.",
    )
    delayed = World(
        "delayed_event",
        "ALERT",
        horizon / 2,
        horizon * 2,
        "reliable_but_delayed",
        "The sender emitted ALERT before the horizon, but delivery occurs later.",
    )
    return no_emit, delayed


def timeout_claim_sound(
    *,
    last_possible_emit: float,
    max_delay: float | None,
    observation_time: float,
) -> bool:
    """Whether 'all emissions by last_possible_emit would have arrived' follows.

    A finite max_delay is an explicit synchrony/reliability assumption.
    This says nothing about events that may occur after last_possible_emit.
    """
    if not all(math.isfinite(x) for x in (last_possible_emit, observation_time)):
        raise ValueError("times must be finite")
    if max_delay is None:
        return False
    if not math.isfinite(max_delay) or max_delay < 0:
        raise ValueError("max_delay must be finite and nonnegative")
    return observation_time >= last_possible_emit + max_delay


def bec_output(bit: int, erased: bool) -> str:
    """Tiny deterministic representation of a binary erasure-channel outcome."""
    if bit not in (0, 1):
        raise ValueError("bit must be 0 or 1")
    return "E" if erased else str(bit)


def classify_lease(messages: list[LeaseState], now: float) -> str:
    """Conservative status interpretation.

    RESOLVED is explicit. Silence after an ACTIVE lease expires becomes UNKNOWN.
    """
    if not math.isfinite(now):
        raise ValueError("now must be finite")
    if not messages:
        return "UNKNOWN"
    ordered = sorted(messages, key=lambda x: x.observed_at)
    for msg in ordered:
        msg.validate()
    latest = ordered[-1]
    if latest.observed_at > now:
        return "UNKNOWN"
    if latest.status == "RESOLVED":
        return "RESOLVED"
    if latest.status == "UNKNOWN":
        return "UNKNOWN"
    assert latest.valid_until is not None
    return "ACTIVE" if now <= latest.valid_until else "UNKNOWN"


def finite_eventuality_verdict(
    delivery_times: list[float],
    horizon: float,
    deadline: float | None = None,
) -> str:
    """Three-valued finite monitor for 'a delivery eventually occurs'.

    Without a deadline, a quiet finite prefix is INCONCLUSIVE because a future
    delivery can still satisfy the property. A deadline converts the bounded
    requirement into a finitely refutable obligation.
    """
    if not math.isfinite(horizon) or horizon < 0:
        raise ValueError("horizon must be finite and nonnegative")
    if any((not math.isfinite(t) or t < 0) for t in delivery_times):
        raise ValueError("delivery times must be finite/nonnegative")
    if any(t <= horizon for t in delivery_times):
        return "SATISFIED"
    if deadline is None:
        return "INCONCLUSIVE"
    if not math.isfinite(deadline) or deadline < 0:
        raise ValueError("deadline must be finite and nonnegative")
    return "VIOLATED" if horizon >= deadline else "INCONCLUSIVE"


def open_world_query(
    positive_facts: set[str],
    negative_facts: set[str],
    proposition: str,
    *,
    closed_world: bool = False,
) -> str:
    """Tiny didactic open/closed-world contrast, not an OWL reasoner."""
    if not proposition:
        raise ValueError("proposition must be nonempty")
    if proposition in positive_facts and proposition in negative_facts:
        return "INCONSISTENT"
    if proposition in positive_facts:
        return "TRUE"
    if proposition in negative_facts:
        return "FALSE"
    return "FALSE" if closed_world else "UNKNOWN"


def entropy_bits(probabilities: list[float]) -> float:
    """Shannon entropy for a declared finite probability distribution."""
    if not probabilities:
        raise ValueError("probability distribution must be nonempty")
    if any((not math.isfinite(p) or p < 0) for p in probabilities):
        raise ValueError("probabilities must be finite and nonnegative")
    total = sum(probabilities)
    if abs(total - 1.0) > 1e-9:
        raise ValueError("probabilities must sum to 1")
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def mutual_information_bits(
    prior: dict[str, float],
    channel: dict[str, dict[str, float]],
) -> float:
    """Mutual information I(hidden; observation) for a finite channel."""
    if not prior or set(prior) != set(channel):
        raise ValueError("prior/channel hidden-state keys must match and be nonempty")
    entropy_bits(list(prior.values()))
    outputs: set[str] = set()
    for state, distribution in channel.items():
        if not distribution:
            raise ValueError("each state needs an observation distribution")
        entropy_bits(list(distribution.values()))
        outputs.update(distribution)
    p_y = {y: 0.0 for y in outputs}
    for x, px in prior.items():
        for y, py_x in channel[x].items():
            p_y[y] += px * py_x
    info = 0.0
    for x, px in prior.items():
        for y, py_x in channel[x].items():
            joint = px * py_x
            if joint > 0:
                info += joint * math.log2(joint / (px * p_y[y]))
    return info


def quartet_shared_silence_information_bits() -> float:
    """Uniform four-world prior + one identical silent-window observation."""
    states = (
        "explicit_resolved",
        "channel_failed",
        "alert_delayed",
        "intentional_rest",
    )
    prior = {state: 0.25 for state in states}
    channel = {state: {"SAME_DIGITAL_ZERO_WINDOW": 1.0} for state in states}
    return mutual_information_bits(prior, channel)


def posterior_event_probability_after_no_detections(
    prior_event_probability: float,
    detection_if_event: float,
    false_positive_if_no_event: float,
    opportunities: int,
) -> float:
    """Bayesian countercase: silence can be probabilistic evidence.

    Assumes conditionally independent opportunities and fixed per-opportunity
    detection/false-positive rates. These are modelling assumptions, not MHAC
    empirical estimates.
    """
    vals = (prior_event_probability, detection_if_event, false_positive_if_no_event)
    if any((not math.isfinite(x) or not 0 <= x <= 1) for x in vals):
        raise ValueError("probabilities must be finite within [0,1]")
    if not isinstance(opportunities, int) or opportunities < 0:
        raise ValueError("opportunities must be a nonnegative integer")
    likelihood_no_given_event = (1.0 - detection_if_event) ** opportunities
    likelihood_no_given_absent = (1.0 - false_positive_if_no_event) ** opportunities
    numerator = prior_event_probability * likelihood_no_given_event
    denominator = numerator + (1.0 - prior_event_probability) * likelihood_no_given_absent
    if denominator == 0:
        raise ValueError("conditioning event has zero probability under both hypotheses")
    return numerator / denominator


def heartbeat_suspicion(
    arrivals: list[float],
    now: float,
    expected_interval: float,
    timeout: float,
) -> bool:
    """Simple timeout implementation; returns suspicion, not truth of failure."""
    if expected_interval <= 0 or timeout < expected_interval:
        raise ValueError("timeout must be at least the positive heartbeat interval")
    if not math.isfinite(now):
        raise ValueError("now must be finite")
    if any((not math.isfinite(x) or x < 0) for x in arrivals):
        raise ValueError("heartbeat times must be finite/nonnegative")
    if not arrivals:
        return now > timeout
    return now - max(arrivals) > timeout


def _add_sine(samples: list[float], start: float, length: float, freq: float, amp: float) -> None:
    first = max(0, round(start * SAMPLE_RATE))
    count = max(0, round(length * SAMPLE_RATE))
    for k in range(count):
        i = first + k
        if i >= len(samples):
            break
        t = k / SAMPLE_RATE
        envelope = min(1.0, k / max(1, int(.008 * SAMPLE_RATE)),
                       (count - k) / max(1, int(.012 * SAMPLE_RATE)))
        samples[i] += amp * envelope * math.sin(2 * math.pi * freq * t)


def _base_heartbeats() -> list[float]:
    samples = [0.0] * round(DURATION * SAMPLE_RATE)
    for at in (0.12, 0.36, 0.60, 0.84):
        _add_sine(samples, at, .055, 880, .24)
    return samples


def scene_samples(scene: str) -> list[float]:
    """Four hidden situations sharing exact PCM zero from 1.0s to 2.5s."""
    s = _base_heartbeats()
    if scene == "explicit_resolved":
        # explicit all-clear BEFORE the common silent interval
        _add_sine(s, .91, .07, 1320, .20)
        _add_sine(s, .96, .03, 1760, .15)
        # intentionally remains quiet after silence
    elif scene == "channel_failed":
        # no resolution signal; later diagnostic side-channel reveals a fault
        _add_sine(s, 2.70, .45, 110, .18)
        _add_sine(s, 3.22, .20, 165, .14)
    elif scene == "alert_delayed":
        # alert was conceptually emitted earlier but arrives after silence
        for at, freq in ((2.70, 440), (2.84, 554.37), (2.98, 659.25)):
            _add_sine(s, at, .10, freq, .22)
    elif scene == "intentional_rest":
        # a musical rest framed by a deliberately resumed pulse pattern
        for at in (2.62, 2.86, 3.10, 3.34):
            _add_sine(s, at, .055, 880, .24)
    else:
        raise ValueError("unknown scene")
    # hard guarantee that the shared window is literal digital silence.
    a = round(SHARED_SILENCE_START * SAMPLE_RATE)
    b = round(SHARED_SILENCE_END * SAMPLE_RATE)
    for i in range(a, b):
        s[i] = 0.0
    return s


def pcm16_wav(samples: list[float]) -> bytes:
    pcm = bytearray()
    for value in samples:
        v = max(-.95, min(.95, value))
        pcm.extend(struct.pack("<h", round(v * 32767)))
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(bytes(pcm))
    return buf.getvalue()


def silence_window_pcm(wav_bytes: bytes) -> bytes:
    """Extract raw shared silent window from our mono PCM16 WAV."""
    import io
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2 or w.getframerate() != SAMPLE_RATE:
            raise ValueError("unexpected WAV contract")
        start = round(SHARED_SILENCE_START * SAMPLE_RATE)
        length = round((SHARED_SILENCE_END - SHARED_SILENCE_START) * SAMPLE_RATE)
        w.setpos(start)
        return w.readframes(length)


def build_quartet() -> dict[str, bytes]:
    return {
        name: pcm16_wav(scene_samples(name))
        for name in (
            "explicit_resolved",
            "channel_failed",
            "alert_delayed",
            "intentional_rest",
        )
    }


def receipt(quartet: dict[str, bytes]) -> dict:
    windows = {name: silence_window_pcm(data) for name, data in quartet.items()}
    unique_windows = {hashlib.sha256(x).hexdigest() for x in windows.values()}
    return {
        "schema": "mhac-x005-silence-quartet-v1",
        "sample_rate": SAMPLE_RATE,
        "duration_seconds": DURATION,
        "shared_silence": [SHARED_SILENCE_START, SHARED_SILENCE_END],
        "shared_window_sha256": next(iter(unique_windows)),
        "shared_window_identical": len(unique_windows) == 1,
        "shared_window_all_zero": all(set(x) <= {0} for x in windows.values()),
        "shared_window_hidden_world_information_bits":
            quartet_shared_silence_information_bits(),
        "files": {
            name + ".wav": {
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
            for name, data in quartet.items()
        },
        "warning": (
            "The files are synthetic demonstrations. Equal digital silence does "
            "not imply equal hidden state or human interpretation."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=Path("build/mhac-x005"))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    quartet = build_quartet()
    for name, data in quartet.items():
        (args.out / (name + ".wav")).write_bytes(data)
    rec = receipt(quartet)
    (args.out / "receipt.json").write_text(
        json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    no_emit, delayed = async_counterexample()
    proof = {
        "horizon": 5.0,
        "no_emit_prefix": observed_prefix(no_emit, 5.0),
        "delayed_prefix": observed_prefix(delayed, 5.0),
        "indistinguishable": indistinguishable_at(no_emit, delayed, 5.0),
        "later_distinguishable": not indistinguishable_at(no_emit, delayed, 11.0),
    }
    (args.out / "trace-counterexample.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"out": str(args.out), "quartet": rec, "proof": proof}, indent=2))


if __name__ == "__main__":
    main()
