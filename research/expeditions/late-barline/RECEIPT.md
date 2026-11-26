# Native execution receipt — 2026-11-26

Run: python laboratory.py, Python 3.13.5, Linux execution environment. Exit 0; standard library only. Source SHA-256 e9a0ccf49f5852e3210b87e962cd8fcdef8375109f01c7ccb39630d5f4aea315, Git blob e9067cc63509fb03a6533e22057a96856b2536b5 (local and returned GitHub update blob agree).

- PASS: 1,936 period/phase pairs, 29,524 ternary assignments, separate 24-pulse witness (10 contested labels).
- PASS: four deterministic repeated PCM renders, amplitude bound, stereo 16-bit 16 kHz WAV header and full payload readback, 192,000 frames each (12 s).
- PASS: all first 96,000 frames equal across four files; complete left channel identical, four distinct full PCM payloads; all 16-bit right samples of unresolved are zero. Invalid mode rejected.
- The silent-channel check was strengthened during self-review to examine both bytes of each sample; final code rerun.

| Generated file | SHA-256 |
|---|---|
| three.wav | 6b5c49d419b67dc7c4cdca23bfe1af1bcc8af8f680e240e2f2759c0186117ba0 |
| four.wav | 384b6855fbeaab70ba7082a988144bda6db7877a54f82715fde8812296aed1c2 |
| unresolved.wav | 24d1b60a11b8152151950d5fe1e22b3e490f0d3d9fb9d66f1c8bc9e666e650f3 |
| double.wav | 40a576bdfafdf891b9322fcbc74cee9dde0e4af7211a8cd59ee657a677935a9a |

WAV files are generated locally; not stored as repository blobs. Rerendering uses platform math functions, so cross-platform byte identity is not guaranteed. No real-time DSP, human audition, participant evidence, empirical source appraisal, full repository validator, or independent review was performed. This receipt records bounded local software checks, not research acceptance or CI.
