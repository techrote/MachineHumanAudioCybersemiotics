# Execution receipt — 2026-11-25

Native Python 3 standard-library execution, single AI assistant; no human listening or independent verification.

- 83,521 four-sample input tuples, 6,561 clipped output tuples, maximum preimage 625. All reconstruction, sign/support, output count and individual fiber-size assertions passed.
- Six original mono 16-bit WAVs, 16,000 Hz, 64,000 frames each; peaks: input 16,000, principal and residual 8,000. Same-environment repeat identical. PCM readback, header, sample bounds and exact recombination passed. The principal file hash is identical across conditions; residual hashes differ.
- Executed source Git blob: 1b3a985f75bd75997b0d0ff43c2157e1219feece. Retrieved repository laboratory.py blob matched.

| File | SHA-256 |
|---|---|
| slow-input.wav | f3d7a7e3e821cc62fd5fb5f26f60c790b853f6a39f808a0ef1ec0346d2df78bb |
| slow-primary.wav | 985a727b8f11cb7d7821a286c8a4ab030499874d645cde53e5897304a1169736 |
| slow-offcut.wav | 3d875b5741d3d4ee806d697c98a372e06f9a56e7f3f3f55176e2682c11042c2b |
| fast-input.wav | 07da879b97ef64ab842682b0c439f0d5da38a94f961a378d02429e2021642f9e |
| fast-primary.wav | 985a727b8f11cb7d7821a286c8a4ab030499874d645cde53e5897304a1169736 |
| fast-offcut.wav | 257a275671bed787b33a169abae7b95d4c8601929e7ee1ee1d5db34294517f1c |

Generated WAVs and JSON receipt are not committed; regenerate using python3 laboratory.py. No third-party audio. Hashes establish same-environment output only (platform math differences are possible). Repository-wide offline checks and exact-head CI not yet verified. No claim of scientific acceptance.
