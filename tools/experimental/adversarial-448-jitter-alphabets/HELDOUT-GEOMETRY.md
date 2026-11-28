# Held-out competing pilot geometry — Run 072

Refs #448/#449, Adversarial lane, Draft/HOLD. Synthetic exploratory falsification only. No independent acceptance. Run070 comparator 56272fdf8c81661a37b92cc1488baacf8f68e373 (SHA256 386a2e3b1e88369748e2a7641614d7c12616cf4f7bbd0ba9c29c8b09da33d43d), Measurement cf8ed0b6dea0cfc4865ad10a57fbcebd3339fe36. Accepted main at intake 495a98ca12bae467a507031f04931aa4254b1866. Source pins checked against mounted comparator bytes and remote Git blobs. No new threshold or policy tuning.

## Method

Two new fixed seeds 4480721/4480722, each enumerating 108 meanings. 16 kHz, 20 ms symbol, 1,600 PCM count target, continuous white noise RMS 1,000, independently drawn carrier shifts in [-75,75] Hz, integer arrival samples [-151,151]. 2,400 count pilots: coincident arrival, near (offset 24 or 40 samples in either direction, clipped), far (>=96 samples apart), independently sampled arrival, and two near/far pilots. Previous/reused epoch controls use equal nominal 1,600 count full stale header with independent arrival. Target and noise controls. Phases and noise matched across conditions within a fixture; identical PCM for every policy. Same 357 pilot scores, unchanged Local4, Diverse4 and Local8. Known capture, frame and expected epoch; no stateful suspension or longer grammar body.

## Executed totals (216 per condition)

| Condition | Local4 correct | Diverse4 correct | Local8 correct |
|---|---:|---:|---:|
| Target | 216 | 216 | 216 |
| Coincident | 167 | 143 | 204 |
| Near | 160 | 145 | 199 |
| Far | 44 | 175 | 164 |
| Independent | 103 | 164 | 170 |
| Two | 127 | 132 | 158 |
| Previous epoch | 123 | 127 | 133 |
| Reused epoch | 23 | 18 | 18 |
| Noise | 0 | 0 | 0 |

Wrong counts are zero except reused epoch: 18/13/15; remaining outcomes withheld. Far: 133 rescues, 2 losses for Diverse4 versus Local4; calls 863/851/1699. Coincident: 1 rescue, 25 losses. Near: 5 rescues, 20 losses. The earlier benefit is geometry dependent, not a general dominance claim. Both seeds show the same direction for far, coincident and near. Do not infer general rates from this constructed factorial. Real CPU and energy parity not measured; decodes are a work proxy. No authentication, physical or human claims.

## Reproduction and qualification

`OPENBLAS_NUM_THREADS=1 python heldout-geometry.py bounded-reacquisition.py acquisition-rank.py selective-transport.py epoch-rank.py NEW_OUT`

Python 3.13.5, NumPy 2.3.5; 1,944 matched PCM captures, 5,832 decision recounts, 54 aggregate and 18 paired-transition recounts. Two output directories byte-identical. Nine original WAV specimens common quarter scale, max 1406 PCM counts, no autoplay, default gain .2. Offline HTML selector, JSONL candidate traces, receipt, SHA256 manifest generated. Node syntax check passed; browser and full repo native qualification not executed. Source SHA256 9315975fdb5cf505a7fc6296e81e959b3a962e1bc104ab719a1333cd3e91ca3d. Direct Git DNS failed; guarded connector publication only. No canonical records, merge, protocol or gate changes. AI-assisted implementation and self-check, not independent acceptance.

Next: stateful bounded suspension on longer bodies from Run064; compare a geometry-adaptive allocation on a separate future seed set, not these holdouts. Measurement remains on fresh grammatical PCM and integrity-triggered escalation.
