# Research-to-project foundation specification

[Protocol](RESEARCH_PROTOCOL.md) · [Synthesis](SYNTHESIS_METHOD.md) · [Experiments](EXPERIMENTS.md)

**Status: proposed design questions and constraints. No encoding or interface benefit has yet been validated.** MHAC-R012 and MHAC-R013 derive the actual specification from accepted research.

## Purpose

An artificial auditory sign system for efficient machine-to-human communication, with human responses/acknowledgement available where useful. Speech is a candidate component, not the whole system. Preserve natural language intelligibility and grammatical clarity while avoiding dependence on emulated human emotional performance. Deliberately synthetic output must still be evaluated for comprehension, workload and retention.

Do not treat this preference as an empirical conclusion or a doctrine established by Brier. Competing conventional, speech-derived and affective-interface approaches remain legitimate research comparators. The system need not resolve philosophical questions about intrinsic meaning or consciousness to support an appropriately bounded interaction model.

## Proposed functional chain

```text
World state → observation → machine estimate → communicative purpose
→ semantic message → rendering policy → acoustic output
→ situated human interpretation → response/repair → updated interaction
```

Context, learning, hearing/acoustic conditions and attention affect interpretation. The world state may differ from the estimate. A sent signal is not proof of reception, an acknowledgement is not proof of understanding, and acknowledgement is not resolution. These distinctions are proposed modelling requirements to justify and test.

## Provisional dimensions

| Dimension | Question |
|---|---|
| Source/event identity | Which system and which incident does this concern? |
| Observation and diagnosis | What was observed versus inferred? |
| Epistemic status | How certain is the claim; what is unknown or conflicting? |
| Hazard severity | What safety consequence is supported by the evidence? |
| Task consequence | What non-safety loss or failure could occur? |
| Time-to-action/urgency | How soon would action matter? |
| Requested action | What is the listener being asked to do, and why? |
| Persistence/lifecycle | New, continuing, acknowledged, acted on, resolved or superseded? |
| Time validity/provenance | Is the estimate current and where did it originate? |

Hypothetical example only: a printer reports a suspected filament obstruction, low assessed hazard, likely print failure soon, and requests inspection of the filament path. Unknowns remain unknown. Do not convert suspicion to certainty or low hazard to low urgency merely to simplify the message.

## Candidate representations

Speech can express specific concepts and actions; motifs can encode learned categories; icons or sonification may represent relations or continuous state. These are research options, not approved mappings. The evidence should determine when each is useful, how much training it needs, and how it fails. Do not require every semantic field to occupy a simultaneous acoustic parameter.

Keep linguistic prosody, timing and intelligibility distinct from impersonated emotion. Evaluate perceived non-human identity rather than assuming a synthetic timbre achieves it. Do not assume no affect, universal symbols or effortless decoding. Prefer a minimal learnable inventory over arbitrary maximum information density only if supported by the research and tested conditions.

## Interaction and failure cases

Specify prioritization and arbitration between sources; interruption and resume; repeat/detail requests; changing confidence; stale, conflicting or superseded messages; missed cues; multiple unresolved conditions; acknowledgement without resolution; and correction after a wrong diagnosis. Include safe silent/text fallback and accessibility routes as design questions, not a claim that one modality suits everyone.

Avoid production integration, physical machine control and real safety-critical deployment in the foundational programme. Synthetic schema/logic tests are permitted. Acoustic implementations and real listening validation follow their specific gates.

## Traceability contract

Each requirement or hypothesis must state its class, basis/source/claim IDs, expected mechanism, conditions, alternatives/objections, test, rejection/revision rule and current validation status. Project constraints do not need a fabricated empirical citation; empirical recommendations do. Label arbitrary conventions explicitly.

The handoff must separate what is safe to prototype now, what the literature supports only under narrow conditions, what needs empirical work, and what requires a human decision. The research should inform implementation rather than freeze speculative choices into a permanent authority file.
