#!/usr/bin/env python3
"""MHAC-T018: deterministic synthetic *analogy* for multi-turn corrective feedback.

No LLM inference, user affect measurement, participant data, or empirical effect
sizes. Values are dimensionless invented bookkeeping signals, NOT probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import argparse
import csv
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class Coupling:
    name: str
    retention: float
    failure_to_pressure: float
    response_sensitivity: float
    response_to_failure: float
    background_pressure: float
    baseline_failure: float
    initial_pressure: float = 0.2

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if key == "name":
                continue
            if not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f"invalid nonfinite parameter: {key}")
        if not 0 <= self.retention < 1:
            raise ValueError("retention must be within [0,1)")
        if self.failure_to_pressure < 0 or self.response_sensitivity < 0:
            raise ValueError("couplings cannot be negative")
        # response_to_failure MAY be negative: useful counterexample.

    @property
    def gain(self) -> float:
        return (
            self.retention
            + self.failure_to_pressure
            * self.response_sensitivity
            * self.response_to_failure
        )

    @property
    def external_input(self) -> float:
        return self.background_pressure + self.failure_to_pressure * self.baseline_failure

    def classification(self) -> str:
        g = self.gain
        if abs(g) < 1 - 1e-12:
            return "asymptotically_stable"
        if abs(g) <= 1 + 1e-12:
            return "marginal_or_boundary"
        return "unstable_if_perturbed"

    def fixed_point(self) -> float | None:
        if abs(self.gain - 1.0) < 1e-12:
            return None
        return self.external_input / (1.0 - self.gain)


PRESETS = {
    "amplifying": Coupling(
        "amplifying", .72, .6, .9, .7, .025, .05, .2
    ),
    "bounded": Coupling(
        "bounded", .55, .45, .35, .3, .025, .05, .2
    ),
    "decoupled": Coupling(
        "decoupled", .55, .45, 0.0, .7, .025, .05, .2
    ),
    "helpful": Coupling(
        "helpful", .6, .4, .5, -.3, .025, .05, .2
    ),
}


def analytical_pressure(params: Coupling, tick: int) -> float:
    params.validate()
    if not isinstance(tick, int) or tick < 0:
        raise ValueError("tick must be a nonnegative integer")
    g = params.gain
    b = params.external_input
    if abs(g - 1.0) < 1e-12:
        return params.initial_pressure + tick * b
    return (g ** tick) * params.initial_pressure + b * (1 - g ** tick) / (1 - g)


def simulate(params: Coupling, steps: int = 18) -> list[dict]:
    params.validate()
    if not isinstance(steps, int) or not 1 <= steps <= 1000:
        raise ValueError("steps must be an integer from 1 to 1000")
    pressure = params.initial_pressure
    trace = []
    for tick in range(steps):
        response = params.response_sensitivity * pressure
        failure = params.baseline_failure + params.response_to_failure * response
        next_pressure = (
            params.background_pressure
            + params.retention * pressure
            + params.failure_to_pressure * failure
        )
        trace.append({
            "tick": tick,
            "pressure": pressure,
            "response_accommodation": response,
            "failure_cost_signal": failure,
            "next_pressure": next_pressure,
        })
        pressure = next_pressure
    return trace


def output_report(params: Coupling, steps: int) -> dict:
    rows = simulate(params, steps)
    return {
        "status": "synthetic_only",
        "schema": "mhac-t018-feedback-v1",
        "params": asdict(params),
        "gain": params.gain,
        "external_input": params.external_input,
        "linear_classification": params.classification(),
        "fixed_point_mathematical": params.fixed_point(),
        "trace": rows,
        "warning": (
            "No measurement of real frustration, panic, praise, agent intent, "
            "sycophancy, cognition, user preference or coding accuracy. "
            "Model coefficients are invented for controlled counterexamples."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/mhac-t018"))
    parser.add_argument("--steps", type=int, default=18)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = {name: output_report(preset, args.steps)
               for name, preset in sorted(PRESETS.items())}
    (args.out / "feedback-traces.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (args.out / "feedback-traces.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow((
            "condition", "tick", "pressure", "response_accommodation",
            "failure_cost_signal", "next_pressure", "gain"
        ))
        for name, result in sorted(results.items()):
            for row in result["trace"]:
                writer.writerow((
                    name, row["tick"], f'{row["pressure"]:.12g}',
                    f'{row["response_accommodation"]:.12g}',
                    f'{row["failure_cost_signal"]:.12g}',
                    f'{row["next_pressure"]:.12g}',
                    f'{result["gain"]:.12g}',
                ))
    print(json.dumps({
        "out": str(args.out),
        "classification": {k: v["linear_classification"] for k, v in results.items()},
        "gain": {k: v["gain"] for k, v in results.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
