# Bounded epoch-header reacquisition — exploratory, Refs #448

Pinned Measurement comparator cf8ed0b6dea0cfc4865ad10a57fbcebd3339fe36 (epoch-rank.py); acquisition-rank.py at 2dab493e14107adb2fefce097aba59a13026d2a4 and selective-transport.py at 8656394a04100f9dd6d835397cd2831f58356b36. Exact SHA-256 checks in executable. Adversarial parent 9a8e4edc3c7607c37cda8381e57b707e70d66225. Main 495a98ca12bae467a507031f04931aa4254b1866. Both preceding exact-head structural CI passed (46052625898 and 46059346422).

Run `OPENBLAS_NUM_THREADS=1 python bounded-reacquisition.py acquisition-rank.py selective-transport.py epoch-rank.py NEW_OUT` with Python 3.13.5 and NumPy 2.3.5. Seed 4480701. Fixed 357 pilot hypotheses, local4 is the pinned candidate selection; diverse4 reserves first three candidate positions for distinct timing neighborhoods (more than 48 samples separation), then returns to local ranking; local8 doubles the candidate ceiling. All use same CRC and supplied epoch guard, unique rank or withhold. Fresh 108 meanings per condition, continuous white noise RMS 1000 PCM counts, amplitude 1600, off-grid arrival and shift, matched captures. Candidate count is not runtime parity. No optimization dataset; exploratory parameters, not confirmatory. Timing selection diversity is not a full streaming suspension implementation.

| Condition | local4 C/W/H | diverse4 C/W/H | local8 C/W/H |
|---|---|---|---|
| Target | 108/0/0 | 108/0/0 | 108/0/0 |
| Equal pilot | 102/0/6 | 102/0/6 | 105/0/3 |
| Strong pilot | 30/0/78 | 83/0/25 | 83/0/25 |
| Two pilots | 43/0/65 | 52/0/56 | 60/0/48 |
| Previous epoch | 70/0/38 | 72/0/36 | 75/0/33 |
| Reused epoch | 8/10/90 | 9/14/85 | 7/14/87 |
| Stale only, reused | 0/108/0 | 0/108/0 | 0/108/0 |
| Noise | 0/0/108 | 0/0/108 | 0/0/108 |

Strong pilot actual decode calls 427/424/849, each 8 symbols. More search can increase wrong admissions under deliberate same-epoch replay. No natural channel error rate, human or physical evidence. No session negotiation, streaming, actual CPU parity or independent acceptance. 864 PCM captures, 2592 decision replays, 24 group recounts, 864 matched hashes, two byte-identical output sets. Eight original WAVs quarter-scaled, peak 1554 counts; browser runtime not tested. Next: held-out varied decoy geometry, stateful bounded suspension on longer Run064 bodies. Measurement next: stateful association and escalation. Draft/HOLD, no canonical or gate edits. AI-assisted implementation and software self-check, not independent review.
