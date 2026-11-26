# Native execution receipt — 26 November 2026

ChatGPT executed the exact renderer in a native Python 3.13.5 environment. No external reviewer or listener. Command: `python laboratory.py` with default audio output directory. Source SHA-256: `80499b129282888ef44dfa7bd20299a7052825e8a0d12e84bc35e0a21251e10d`; locally computed Git blob `20fffbcf04874deba9077ac71aa10c1295366fdd` matches GitHub fetch on the issue branch. Exit 0. Standard library only; assertions enabled.

- 9,009 model parameter comparisons (3 gestures × 1,001 times × 3 bodies), coordinate inversion tolerance 1e-12, normalized nonnegative weights, positive instantaneous partials below Nyquist during rendering.
- Nine different cell PCM payloads; repeat render equality for each. Edges zero; signed 16-bit PCM peak bound. Invalid normalized time rejected.
- Unfurl first-partial endpoint ratios Reed 2, Plate 1.6817928305074294, Inverse 0.5. These are model parameters, not measurements from recorded audio.
- All 13 WAV headers and full payloads read back; 24 kHz, mono, PCM16. Maximum observed absolute sample 20726. Hashes refer to generated WAV bytes, not committed binary files. Renderer regenerates them; platform floating-point differences may affect hashes. No loudness or spectral aliasing qualification.

| File | Frames | SHA-256 |
|---|---:|---|
| unfurl-reed.wav | 28800 | 20888f1d88f7f95750567d557b88d667fe26375f673726c1734dad840fa582a6 |
| unfurl-plate.wav | 28800 | bb55c794bc0cc0edaf4f457d484694e1ba52cea9b7afb6b9c73d3af69d88506c |
| unfurl-inverse.wav | 28800 | 2ad451e051bba5d7819517b515a4fee29da10a86c84a191c427f9f3928996806 |
| knuckle-reed.wav | 28800 | 41bdc104cb123a063e2b3fb97ea61fed6ec6ef3ee24d693cb51cd5437a1b9381 |
| knuckle-plate.wav | 28800 | deb8e13ed5700492f65ddb388db52666f957de961462b3ad41622b60fd42efb4 |
| knuckle-inverse.wav | 28800 | 49cebfd33f39c4bfe75eb5eeea8e306a19e169b3a4ae0fe14f4c25bd8acfb37a |
| coil-reed.wav | 28800 | 12897e15d8766dac47438c016d508d6e33369c8198aba08d5e0ccd07fbf3e4b3 |
| coil-plate.wav | 28800 | 355c1a9fd167d9625e5257a97cdb33b9fc179cde81a226a1c2b275c419085fb3 |
| coil-inverse.wav | 28800 | 8b219d912e1c4e3fbc29143c2d9ce8a77319f3e279b45dbe0cec278f23811cf2 |
| lexicon-reed.wav | 96000 | a4122bdcfaf65188317e6f63401b9240b47b86cea1a9e1a94246d1cfa97b4458 |
| lexicon-plate.wav | 96000 | 864779a197a17b2225c1111a61f708da916dc36582f17199fdf343032bacf00c |
| lexicon-inverse.wav | 96000 | bba0279526bba3c77709dc07cd8211f2dd3f2ee412c7972f2efebd4b7e8d2cfe |
| three-mouths.wav | 96000 | e550a39bff2c6a273d26018c8b25dc541767ded4162b403de8167ddccb61fca3 |

No full repo tests, peer review, listening study, firmware, VST implementation or scientific validation. Synthetic additive trajectories only.
