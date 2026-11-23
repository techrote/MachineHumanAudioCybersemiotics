# MHAC-X002 — execution and negative-result ledger

**Recorded:** 2026-11-23 UTC. **Claim status:** original assistant-authored theoretical note and mechanically checked **fictional** enumeration. Nothing here constitutes participant evidence, scholarly peer review, real robotics qualification, or acceptance under the frozen Track E/G protocol.

## Exact source artifact verification

The two Python files were created on an issue-scoped GitHub branch and reproduced byte-exactly in a separate Python execution environment. The corresponding computed **Git blob SHA-1** values were compared against the source SHA reported by GitHub's file API:

| File | Size | Exact blob SHA-1 | Result |
| --- | ---: | --- | --- |
| [frame_oracle.py](frame_oracle.py) | 7,023 UTF-8 bytes | `7f36f762ead25225c23b727ca9acb734d426d914` | Match |
| [test_frame_oracle.py](test_frame_oracle.py) | 5,954 UTF-8 bytes | `a018531922efd5aa467add0c62a19d34260b6c3c` | Match |

The mirrored scripts were executed with **Python 3.13.5**, standard library only:

- `python -m unittest discover -s ... -p 'test_*.py' -v` → **9 tests, all passed**; all exhaustive rotations and anchor-isolation checks included.
- `python frame_oracle.py --check` → **exit 0**, 64 scenes / 192 scene-frame pairs and declared counts verified.
- `python frame_oracle.py --out ...` → **exit 0 twice**; output files census.json (22,115 bytes) and receipt.json (548 bytes), regenerated deterministically.
- Canonical census JSON SHA-256: `763b9ff6490f45d968261464e9c3d5dc04f8f6bae9341d8cf0fe7d296836383b`.
- Generated receipt JSON SHA-256: `59cbbddb69841ad4ad9bfae9b79b2e900c871739723a7a35947f5bb417f08d99`.

The execution environment also emitted an unrelated **spreadsheet-runtime warmup warning on interpreter startup**; it did not change the Python process's success exit code or unittest results. No spreadsheet tool was used for the experiment.

**Full repository validation:** not claimed by these isolated runs; those checks require a complete repository worktree/PR CI. Exact-head GitHub checks and required approvals must be assessed separately. Do not treat a successful local oracle as the integrator's approval.

## What the synthetic experiment establishes

- The recipient/emitter/panel triple `(north,east,south)` generates three distinct actions from one identical untagged "left": west, north, east.
- Exactly four of the 64 invented heading triples yield the **same world action under all three frame readings**.
- A blind recipient-relative policy is wrong for exactly 96 of the 192 **equally enumerated fictional** scene-frame pairs; this must not be described as a real-world 50% misunderstanding rate.
- The abstaining policy never commits the wrong world heading within this model, **because it refuses 180 of 192 pairs**. Hence "zero errors" is not enough to claim a useful interface.
- Explicit frame selection plus perfectly current transform produces 192/192 correct **by construction**, not because listeners can execute it.
- All relative action sets rotate equivariantly with the C4 scene rotation. When an *irrelevant* anchor alone rotates, an explicit other-frame action stays unchanged.

## Negative / scope-limiting results

1. **Mandatory tags are not mathematically necessary:** aligned headings have one possible action even with unspecified frame.
2. **Tags are not sufficient:** a stale / unknown transform is a separate failure; the toy abstains under an untrusted flag.
3. **Universal recipient-left convention remains a simpler alternative** under a shared, reliable protocol; the toy does not establish that people need frame metadata.
4. **No real acoustic channel was simulated:** utterance intelligibility, masking, sound localization, cognitive reference-frame selection and interactional repair are unmeasured.
5. **No full source close reading of Levinson or Clark & Wilkes-Gibbs was performed**; publisher/public abstract passages alone support bounded conceptual leads, not claims about those authors' complete arguments.
6. **No human or independent review**: the nine tests check internal consistency and hard-coded expected counts, not external scientific validity.

## Next bounded extensions

If adopted later, examine non-orthogonal orientation, probabilistic heading estimates, stale transforms indexed by timestamp, and feedback-based disambiguation; preregister competing interpretations before real evaluation. Adversarially test whether frame tags increase error by imposing longer speech, unfamiliar vocabulary or slower decision latency. Keep theoretical work separated from the R005/R006 selected evidence and from R020 participant authorization.

**Files that must remain untouched by this expedition:** canonical protocol/amendments, `programme.json`, source/screening records, generated registry aggregates, other worker branches, the accepted X001 files and all active T001–T018 tangents.