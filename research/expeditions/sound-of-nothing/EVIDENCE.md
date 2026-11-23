# MHAC-X005 — execution and evidence ledger

**Date:** 23 November 2026.

## Actually completed before PR qualification

- Reconciled live MHAC issues and identified T005 #36 as the closest internal overlap.
- Inspected public source records for FLP, Chandra–Toueg failure detectors, heartbeat/accrual detectors, binary erasure channels, pragmatics of silence and philosophy of absence.
- Implemented silence_oracle.py using Python standard library only.
- Added focused tests and repository discovery bridge.
- Authored formal proof, synthesis, candidate protocol and speculative essay.
- No private conversations were ingested as research data; no user psychological state is inferred.

## Synthetic experiment contract

Default audio:
- sample rate: 24,000 Hz;
- mono PCM16;
- duration: 4.0 s;
- shared digital silence: 1.0–2.5 s;
- four scenes with distinct histories.

The tests require:
- all four silence-window byte sequences are identical;
- every silence-window PCM byte is zero;
- complete WAV files are mutually different;
- generated receipt hashes match the actual files.

## Formal checks represented in tests

- no-emission and emitted-but-delayed worlds have equal finite traces;
- the same pair becomes distinguishable after delayed delivery;
- no finite timeout is called sound when no delivery bound is supplied;
- known delay bound permits only the specifically bounded past conclusion;
- erasure marker E remains distinct from valid 0 and 1;
- ACTIVE lease expires to UNKNOWN, not RESOLVED;
- explicit RESOLVED remains explicit;
- heartbeat timeout is a suspicion policy and can be reversed by a later arrival.

## Pending at this document's initial creation

- exact final-head GitHub Actions;
- full repository validator;
- deterministic fixture check;
- external human listening/visual review;
- any programme-level adoption.

Green CI, when obtained, will validate software/repository invariants only. It will not validate human interpretation, metaphysics, or production safety.

## Nonclaims

X005 does not establish:
- that human silence is always meaningful;
- that silence never carries information;
- that a timeout can never be useful;
- that FLP is an auditory theorem;
- that absences are or are not metaphysical causes;
- that UNKNOWN is always the best user-facing label;
- that the silence quartet has any measured aesthetic or perceptual effect.
