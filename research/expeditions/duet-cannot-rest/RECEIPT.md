# Native execution receipt — 2026-11-25

Executed in local container with Python 3, standard library only; single-agent self-qualification. Command: python laboratory.py audio

- 12,854 marked cyclic words across a,b=1..7; 33,102 bounded interval/r configurations. All assertions passed (direct word enumeration vs composition DP and feasibility inequalities).
- 12 original mono 16-bit 16 kHz WAVs: four allocation patterns, each with two stems and a sum. Each 9 seconds, 144,000 frames. Repeated PCM generation, bounds and WAV payload readback passed. Mixes byte-identical.
- Exact local source Git blob SHA: 928a2c3d8a2b02870fe20d689be421bd9d452f10.
- SHA-256 of all four mix WAVs: 6b4e5f85a3cac5122f883d63b6654f3bc6724c45d26fb7e1ff55d08377202269.

| Pattern | A stem SHA-256 | B stem SHA-256 |
|---|---|---|
| alternating | 85986444769228f25ee4ed768481f5a52ad3830a7e1624bddf0175ba50950a8b | 450f9cd365df3834e0ece2f9fc89c22c59a6ab46ecd472442129c523c7519a39 |
| even_pairs | 6ab455e804d5fd0f734200f6bf8901e50c20e5d2eaa67c8eb0883592cedefcce | 8938b44cc76d73dd9c4dbce1e1e72b63630020cb4c22e875920aedd573d7ccfa |
| uneven_pairs | d86a3e2eb2bba5f11828d1eaee10493b7912b22cd2789a40445ba76a67d8a586 | 3ea196ed39a474aec6db48d26d67c2ac15c17f217657dee2f0bd4560b4905321 |
| blocks | d487e33ba07170d5d287511eb58a593e6d8d88de560387ec5df8dfe368a2b6c0 | 0a679618119f8edc8ddf53730abf8934514fc719c02865531305a2d8cbeb4475 |

Generated WAVs are delivered separately; repository stores reproducible source rather than binaries. Floating point oscillator results may differ on other math libraries; exact symbolic checks are portable. Not a listening study, performance assessment, independent review or full repository CI. No canonical evidence or human gate satisfied.
