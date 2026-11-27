# Epoch-checked direct semantic rank — Measurement Run 069

Refs #442/#443, #448/#449. Draft/HOLD; AI-assisted synthetic computational experiment, not independent acceptance. Base main 495a98ca12bae467a507031f04931aa4254b1866. Parent 2dab493e14107adb2fefce097aba59a13026d2a4. Adversarial witness 9a8e4edc3c7607c37cda8381e57b707e70d66225 (pilot-decoys.py). Both exact-head integrity CI runs 46045264940 and 46052625898 succeeded before this work. No human, physical, protocol or shared registry changes.

## Apparatus and replay

Run `OPENBLAS_NUM_THREADS=1 python epoch-rank.py acquisition-rank.py selective-transport.py NEW_OUTPUT` from this directory with Python 3.13.5 / NumPy 2.3.5 (tested). Comparator bytes checked against SHA-256 pins in source. Seed 4426901; all 108 fixed-depth ranks once per condition, expected frame ID 0–53, expected one-byte epoch supplied independently by harness. Original header is frame/rank/CRC-8 plus three pilot symbols (180 ms); extended header adds epoch (220 ms). Direct semantic rank is the decoded meaning, not a supplementary body checksum. Four acquisition candidates using predecessor 357-hypothesis grid and 2 ms / 20 Hz suppression, threshold 600 PCM counts; accept only one distinct valid remaining rank. Epoch ignored and epoch guard use the exact same capture. Continuous 1000-count RMS white noise, 1600-count nominal tone amplitude, randomized phase, off-grid sample and carrier offsets. Stale frames have a different rank and either previous epoch or deliberately reused epoch (wrap). No sequential session state or authentication implemented. Capture length and expected frame ID are known. Different packet lengths mean energy/duration not matched; paired noise, target amplitude, and phase draws are matched, with signal energy in traces.

## Results (correct / wrong / withheld, each out of 108)

| Condition | Rank | Epoch ignored | Epoch guard |
|---|---|---|---|
| Target | 108/0/0 | 108/0/0 | 108/0/0 |
| Previous epoch only | 0/108/0 | 0/108/0 | 0/0/108 |
| Reused epoch only | 0/108/0 | 0/108/0 | 0/108/0 |
| Target + previous | 10/9/89 | 11/9/88 | 69/0/39 |
| Target + reused | 10/9/89 | 15/6/87 | 15/6/87 |
| Target + pilot | 103/0/5 | 103/0/5 | 103/0/5 |
| Noise only | 0/0/108 | 0/0/108 | 0/0/108 |

Same-waveform guard improves current-rank recovery in target+previous, but does not protect reused epochs; old-epoch-only and wrapped-epoch-only controls are deliberately valid codewords, not a natural channel error estimate. Reused epoch models a frame from 256 increments ago, not a sequential execution of 256 transactions. CRC is unkeyed, not authentication. Direct rank is specific to the 108 fixed-depth meanings; not a proof of broader grammar compression or human comprehension. Adding a byte costs 40 ms (22.2% of rank-only duration). These experiments don't include feedback or retry transport.

## Verification and continuation

1512 rendered captures (some controls identical across formats), 2268 decisions, 756 matched noise groups, 21 aggregate recounts. Independently recomputed policy outcomes from exported decoded symbols via the pinned CRC decoder; matching epoch-policy PCM hashes and all group noise hashes checked. Two complete executions produced byte-identical output directories. Node syntax checked for inline inspector JS; browser runtime not tested. Fourteen original WAV examples at common 0.25 PCM scale, maximum sample magnitude 1585; default player gain 0.2; no autoplay. Source SHA-256 b2fe2e6468acd283c03d3766edc9036df1f7dd8b0933c9d6641fee6b61b8e13a. Whole repository native validation and independent Mergedown review outstanding.

Next Measurement: compare explicit non-reuse session scope and persistent receiver replay state, plus integrity-triggered full retransmission of fresh grammatical body; distinguish direct-rank baseline from recursive grammar. Next consolidated run Adversarial: resume Run064 bounded suspension/reacquisition and preserve these freshness witnesses. No merge or self-certification.
