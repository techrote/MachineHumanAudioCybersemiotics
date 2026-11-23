# MHAC-X005 — The Sound of Nothing

**Status:** independent exploratory research epic, Refs #187. This bundle studies silence, erasure, delay, omission and explicit resolution across distributed systems, information theory, pragmatics, auditory design and philosophy.

The central proposition is deliberately modest:

> A receiver's lack of a message is an observation. It is not, by itself, a uniquely identified world state.

That proposition is formalized for a tiny asynchronous trace model, rendered as an original four-scene audio experiment, and then carried through a cross-disciplinary comparison.

## Contents

| Artifact | Purpose |
| --- | --- |
| silence_oracle.py | Deterministic trace oracle, lease/heartbeat examples and PCM silence quartet |
| test_silence_oracle.py | Focused mathematical/audio tests |
| FORMAL.md | Finite-prefix indistinguishability theorem and assumption table |
| SOURCES.md | Source ledger with actual reading/access limits |
| SYNTHESIS.md | Cross-domain analysis without collapsing the source disciplines |
| NEGATIVE-INFORMATION.md | Liveness, open/closed-world and Bayesian non-detection distinctions |
| INFORMATION.md | Exact mutual-information result for the constructed silence quartet |
| TOMBSTONES.md | Replicated-deletion exaptation: explicit negative state prevents stale resurrection |
| NETWORK-AUDIO.md | RTP silence suppression, sequence/timestamp evidence and comfort-noise precedent |
| ADVERSARIAL.md | Twelve objections and counterexamples against overbroad silence claims |
| NEGATIVE-SPACE-PROTOCOL.md | Candidate lease/status design extracted from the research |
| TYPE-SYSTEM.md | Reusable distinction discipline for NO_DELIVERY, ERASURE, STALE, UNKNOWN, suspicion and resolution |
| EXAPTATION.md | Exact reuse of X001's observation-fibre theorem inside X005 |
| AFTERWORD.md | Original speculative essay; explicitly not scientific evidence |
| EVIDENCE.md | Execution receipts, CI state and nonclaims |
| silence_observatory.html | Optional self-contained interactive visual/audio artwork |

## Reproduce

Python 3.11+, standard library only:

    python research/expeditions/sound-of-nothing/silence_oracle.py --out build/mhac-x005
    python -m unittest discover -s research/expeditions/sound-of-nothing -p 'test_*.py' -v

The generator writes four mono PCM16 WAVs, one receipt and one formal counterexample record. Each WAV contains the exact same digital-zero interval from 1.0 s through 2.5 s:

- explicit_resolved.wav — explicit all-clear before the interval;
- channel_failed.wav — no all-clear; a later diagnostic tone reveals failure;
- alert_delayed.wav — an alert arrives only after the interval;
- intentional_rest.wav — a musical pulse resumes after an intentional rest.

The silent samples are byte-identical. Their hidden histories are not.

## Why this is not “silence always means unknown”

Silence can be meaningful when the protocol supplies enough structure. A known bounded-delivery model can make a timeout informative about a declared earlier interval. A deliberate human silence can be a communicative act. A binary erasure channel can emit an explicit erasure symbol. A signed lease can expire into an UNKNOWN state. An authenticated all-clear can explicitly say RESOLVED.

The point is narrower: **meaning comes from the contract and context, not from zero acoustic amplitude alone.**

## Non-duplication

MHAC-T005 #36 already studies persistent-state sonification, discrete events, all-clear transitions and erroneous inference from sound cessation. X005 does not replace its listening questions or replay harness. It generalizes the epistemic problem across asynchronous systems, channel models, pragmatics and absence philosophy.

MHAC-X003 #183 studies order among observed events; X005 studies missing observations. T010 #47 owns delivery deferral/deadlines. T003 #33 owns recipient repair. The frozen programme, empirical corpus and source registries remain untouched.

## Claim discipline

- The finite-prefix theorem is an elementary result of the stated toy model.
- FLP and failure-detector literature are historical/theoretical comparators, not proofs of auditory-interface behaviour.
- The binary erasure channel is useful precisely because erasure is a distinct received symbol; literal silence is not that symbol.
- Pragmatic silence can be intentional communication, but a failed network link is not thereby a speech act.
- Philosophy of absence is contested; this bundle does not resolve the metaphysics.
- The WAVs are original synthetic art/illustration, not participant data or safe alarm designs.

**AI disclosure:** one GPT-6 assistant authored the expedition, consulted public sources, implemented the code and self-reviewed it. Automated tests and same-agent review are not independent scholarly or human validation.
