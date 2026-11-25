# Native execution receipt — 2026-11-25

Node v22.16.0. Executed source Git blob e4f5ca71ad32a0c600a23ee02391269811465203, independently matched with git hash-object against GitHub contents metadata.
Command: node laboratory.cjs --wav. Exit 0, repeated with identical WAV SHA-256 hashes. 46,656 configurations, 839,817 checks, max incompatible pairs 12, 1,860 equal-row configurations. Nine files; each mono 16-bit 16 kHz 24,000 frames. Independent Python wave/struct checks verified both four-stem sums against common mix (48,000 sample comparisons), and differing stems. Peak absolute common mix 7676.

| WAV | SHA-256 |
|---|---|
| crossed-1 | 4bd4656da333dafcef076b4863aa6d3ddb5126dc3ae647f0dd1febad2d62a23e |
| crossed-2 | 5ff29fb78023e7604a3bec6ec254dc6bfbabd76d1da78b67c88e33095b2e5fe4 |
| crossed-3 | 2712733b449390033e3018daad26e08ed1fdadc68b2369584bef5c0daedc403c |
| crossed-4 | 0c0ba763e1f8825dce5beedd49f5b0db335980a8cb1b79ebd74287d3b94c5c0e |
| invariant-mix | e3160570fcb27521ba673667e006e7fe567346523b4ea9d817e55d5178a1503a |
| nested-1 | 4bd4656da333dafcef076b4863aa6d3ddb5126dc3ae647f0dd1febad2d62a23e |
| nested-2 | 4bd4656da333dafcef076b4863aa6d3ddb5126dc3ae647f0dd1febad2d62a23e |
| nested-3 | f74d768cd31f1a8510ce121b11490ecfc1376c28147c1fb71a5fc589e2cb7ce9 |
| nested-4 | f74d768cd31f1a8510ce121b11490ecfc1376c28147c1fb71a5fc589e2cb7ce9 |

These are checks of deterministic synthetic output in the executing environment, not a human listening study, independent review, or full repository integrity check. WAVs are reproducible with the checked-in source and need not be committed as binaries.
