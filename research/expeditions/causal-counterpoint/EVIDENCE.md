# MHAC-X003 — actual execution and review boundary

**Execution date:** 23 November 2026 UTC. **Input:** five-event original fictional DAG declared in `causal_counterpoint.py`. **Repository starting base:** `main` at `03934eac070deff438d11acf20a4bae97d99873f`, with X002 Draft PR #182 and earlier tangent Draft PRs open. Branch: `mhac-x003/causal-counterpoint-20261123`; issue: #183.

## Run actually performed

Local environment: Python **3.13.5**, standard library; command from the new expedition folder:

```text
python -m unittest discover -s . -p 'test_*.py' -v
Ran 13 tests in 0.062s
OK
python causal_counterpoint.py --out /mnt/data/mhac_x003/run
```

Results: **6** exhaustive linear extensions of a 5-event DAG; `A.emit` versus `B.emit` is `not_entailed_either_way`. The generated original `two-legal-tellings.wav` is PCM16 22,050 Hz, two channels, 42,336 frames, 1.92 s. Its SHA-256 in this environment was `4b85b819c1ccb1617345f3814e213e9329091a53aaf24d535553890c06ee2dd8`. The test suite generated the demo twice in independent temporary directories and asserted exact WAV and CSV byte identity, parsed the WAV header, checked required ordering, and verified negative cases for cycles, duplicates, invalid IDs and the eight-event enumeration bound.

The six orders were **computed** rather than invented human measurements; no controlled auditory test, browser UI inspection, CI result, full repository test suite or independent human verification is claimed by the local commands above. Later PR CI, if present, must be inspected separately on the final head before any merge.

## Falsification and limit ledger

1. **Reversal lemma fails** if there is a directed path between the target pair. The total-order chain and added-edge controls confirm that case.
2. **Concurrency is not simultaneity:** a pair of disconnected nodes has opposite linearizations but no measured physical timestamps.
3. **Missing data does not certify absence:** the oracle classifies relations *relative to the supplied dependency graph*. It does not infer real causal independence from incomplete telemetry.
4. **A total serialization can be useful:** it is allowed for playback and deterministic processing; the error is labeling arbitrary order as proven *causal* order.
5. **The audio score may mislead:** simultaneous stereo playback of alternative orders has no tested perceptual semantics; pitch mapping, headphone/crosstalk, hearing, attention and training are uncontrolled.
6. **Not a novel distributed-systems theorem:** Lamport's 1978 paper discusses the ordering gap and anomalous user-perceived order explicitly (p. 562). The expedition's original element is a compact musical exaptation and exact source-bounded oracle.

## Pending acceptance

Review original repo diff, exact PR head and checks; perform graphical/sound listening only with appropriate non-empirical label if desired; obtain an external review before any stronger intellectual or human claim. The issue and Draft PR are intentionally open. No shared manifests, empirical registry or canonical scientific gates were touched.
