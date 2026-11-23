# MHAC-X001 evidence and execution ledger

**Document state:** contemporaneous author record, 23 November 2026. This is not a substitute for GitHub CI, external peer review or a human audio test.

## Source and derivation checks actually performed

- Read the University of Chicago HTML presentation of Quintilian, *Institutio Oratoria* Book I, chapter 5, §§34–38 and §§45–53; the text states that errors can arise in combinations of words and context. The interpretive use in the essay is the author's, not Quintilian's supposed anticipation of modern signal processing.
- Read University of Hamburg/Jan Louis lecture notes §17.1 printed p.64 and **visually inspected PDF screenshot page index 64**: periodic coordinate, scalar Fourier expansion, simple KK mass-squared n²/R².
- Independently evaluated the default sampling comparison with Python numeric expressions (not by running the complete repository test suite):
  - N=8, modes n=2 and n'=10.
  - Maximum absolute discrepancy at the eight unshifted probes: ~**3.490862358206545e-15** (rounding error).
  - Shift δ=π/16: maximum observed difference ~**1.3065629648763784**.
  - At shifted probe j=0: f₂≈0.9238795325112867, f₁₀≈−0.3826834323650897.
- The general equality at fixed sensors and the factorisation theorem are proven symbolically in [MATHEMATICS.md](MATHEMATICS.md).

## Code and expected verification

- [mode_alias_lab.py](mode_alias_lab.py) is a newly written standard-library Python file that should produce two CSVs, a PCM16 stereo WAV and a JSON receipt.
- [test_mode_alias_lab.py](test_mode_alias_lab.py) defines focused unit tests on aliasing, shifted distinguishing measurement, zero and cosine-symmetry cases, radius/eigenvalues, deterministic audio, WAV framing and invalid input rejection.
- A minimal repository unittest discovery adapter under tests/ allows the existing lightweight test command to exercise these tests, without adding new CI workflows.
- **Do not report a code test as executed merely because source files have been committed.** Exact-commit CI outcome and any real local run must be appended separately below after observed results.
- The owner has not been asked to listen to the WAV or judge synthesizer quality; audio usefulness and perception remain speculative.

## Known limitations and falsifiers

- A fixed finite set of samples does not constrain a general continuous field.
- The shifted observer separates only the chosen pair under the specified offset. It does not uniquely reconstruct every unknown field.
- Rounding error in evaluating sinusoids can vary by runtime/architecture; numerical tests use tolerances.
- Discrete sample equality is instrumental indistinguishability, not a demonstrated shared semantic meaning or cognitive ambiguity.
- The audio generator's rotation-to-frequency transposition is a design choice, not a measurement of physical KK mass.
- No empirical listener data, no preregistered study and no proof of novel physics.

## Execution / review checkpoint

- **Issue:** [MHAC-X001 #178](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/178).
- **Parent work:** additive expedition source/essay/proof and independent tests; frozen MHAC protocol and canonical registries untouched.
- **Exact PR head and checks:** pending PR creation and inspection.
- **Review boundary:** synthetic and literary work is permissible as standalone research sediment; downstream integration into MHAC science requires evidence/protocol decisions.
