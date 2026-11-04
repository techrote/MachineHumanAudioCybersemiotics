# MHAC-T005 — Conditional decision and handoff

**Status:** implementation-ready *exploratory symbolic prepass*, not experimental evidence or an accepted sound design. Assessment 2026-11-04 UTC, against 25 authored fictional traces and four logical policies. An earlier issue-scoped commit already supplied replay/tests; this tranche adds provenance, policy and future-protocol documentation, with negative tests.

## What this tranche does and does not show

The fixture ledger enumerates 25 cases × 4 policies = **100 policy-case evaluations** when the replay suite passes. There are positive recovery cases, silencing/failure without recovery, source unknown/stale, mismatched replay, concurrent sources and a separate urgent event. The predicted logical restriction is **no approved clear without a fresh, known inactive source and matching closed event**, under hypothetical trusted snapshots and a separately encoded fictional recovery binding (no cross-domain revision ordering). Those are *oracle rules by construction*, not independently observed false-clear rates. Symbolic event offerings and ducking are not human hearing or task outcomes; no benefit ranking or safety claim is justified.

| Candidate | Possible gain | Specific failure / reason to reject or narrow |
|---|---|---|
| Discrete warning + conventional visual state | Lower continuous sound burden, explicit event timing and accessible inspection | Trend/status may require visual attention; no human action comparison has been done |
| Persistent state only (conceptual comparison; not implemented in replay) | May make trend peripheral | Cannot guarantee source/event identity or a discrete urgent request from unchanging sound; tests would need a new defined information contract |
| Persistent status + discrete event | Peripheral trend and independent event | Potential masking of other events; directly challenged by Donmez et al. (2009), not resolved by this oracle |
| Persistent + explicit transition/clear | Could reduce ambiguity of sound cessation | Extra events and interpretation burden; only valid if source recovery confirmed independently of playback |
| Ducked hybrid | Prioritizes event offer over persistent status in the script | Abrupt suspension can itself look like recovery; no audibility, detection or latency result |

**Symbolic revision-causality repair, still not a live proof:** The old `source.version >= event.version` and cross-event numeric supersession assumptions are removed. Fresh inactive snapshots require a fictional binding to a complete closed-event set. The positive source-revision-0/event-revision-1 case and missing/partial-binding negative controls expose the earlier flaw. The binding is *not* verified source authority, authentic time ordering or protection against a TOCTOU race. The idealized visual channel remains unvalidated. The scientific and oracle review gate remains open; no schema or production audio policy is adopted.

## Decision consequences

- **Positive human performance in a properly authorized trial:** consider a *conditional* persistent+event design, separately evaluating masking, comprehension, accessibility, exposure and correct action.
- **State monitoring better but separate event action worse:** narrow/reject persistent sound for that workload; do not average the injury to correct action away.
- **Discrete+visual equal/better or lower burden:** retain simpler baseline; a null effect without adequate precision is inconclusive, not noninferiority.
- **Symbolically false clear on active/stale/unknown source:** reject the proposed policy/state binding before acoustic testing.
- **Conflicting tasks/groups:** stratify by task, training, hearing context, multi-source load and alert urgency, or decline a universal mapping.
- **No accepted need for persistent state and separate event:** stop; no new sound-policy requirement.

## Follow-up routes and acceptance boundary

- **R008 (#8):** critically compare predictive/attentional and semiotic theories; S30/S31 contradict a one-direction superiority narrative.
- **R005/R006 (#5/#6), then R009 (#9):** if protocol-eligible, reconcile report/study/sample overlap, legally access full reports and extract/appraise outcomes. This note **does not perform screening**.
- **R012 (#12):** possible source/event/playback/acknowledgment lifecycle distinctions *after* #11; specify credible causal epochs before adopting an oracle.
- **R013 (#13):** only after R012, define acoustic and visual policy hypotheses, including a viable discrete alternative.
- **R014 (#14):** preregistration-ready controlled sound study proposal, not participant execution. See [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md).
- **R017 (#17):** adversarial false-clear, masking, version-causality and source-identity checks.
- **R020 (#20):** remains a human gate; nothing in this package satisfies it.

This bounded issue work is not R013 implementation, not a live registry update, not a frozen protocol amendment and not production TTS/sonification. Source audit: [SOURCES.md](SOURCES.md). Exact positive/negative fixture contract: [POLICIES.md](POLICIES.md). AI-assisted preparation; no independent human review, physical audio generation or listener measurement.
