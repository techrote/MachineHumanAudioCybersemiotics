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

## Observed exact research-head qualification

GitHub Research integrity workflow **#45247604203** executed commit
`d3870cc5255611ccb74460e78cba7abfc13c8cac` after the full research/code
bundle was assembled.

Observed job evidence:

- **30 X005-specific tests passed** (28 `SoundOfNothingTests` plus 2 artifact/offline checks).
- **1,205 repository tests passed in 39.090 s**.
- `tools/validate.py` reported **`structural_result: pass`** and retained
  **`research_state: in_progress`**.
- the repository's deterministic synthetic v1 fixtures reproduced
  **byte-for-byte**.
- no legacy commit status was treated as a substitute for the Actions run.

The shared silence interval is 1.5 s × 24,000 mono frames/s × 2 bytes/frame =
**72,000 zero bytes**. Its deterministic SHA-256 is
`36438cefa7206dac9ef150b613418d5912c3eb69ed4e0084798602985b43470d`.
The program independently records this same shared-window digest in its
generated receipt; the CI tests assert that every scene's extracted window is
identical and all-zero.

The code/test qualification establishes software invariants only. It does not
validate listener interpretation, metaphysics, production safety, or the
usefulness of any proposed auditory rendering.

## Final-head qualification rule

This evidence update itself creates a newer **evidence-only** commit. The PR
must therefore obtain one additional successful Research integrity run on that
actual final head before merge. The final run result should be recorded in the
PR/issue metadata without editing this file again, so qualification does not
create an infinite self-referential commit loop.

## Still intentionally unvalidated

- external human listening/visual review;
- real-system failure-detector performance;
- participant comprehension or action;
- programme-level adoption into R012/R013;
- any claim that the philosophical/artistic comparisons are scientifically
  established.

Green CI validates software/repository integrity only.

## Nonclaims

X005 does not establish:
- that human silence is always meaningful;
- that silence never carries information;
- that a timeout can never be useful;
- that FLP is an auditory theorem;
- that absences are or are not metaphysical causes;
- that UNKNOWN is always the best user-facing label;
- that the silence quartet has any measured aesthetic or perceptual effect.
