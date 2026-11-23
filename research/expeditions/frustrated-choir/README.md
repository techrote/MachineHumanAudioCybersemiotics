# MHAC-X007 — The Frustrated Choir: a loop that refuses to close

**Status:** an original **synthetic, finite** mathematical/audio expedition; neither empirical auditory evidence nor a system that detects which speaker is truthful. See [issue #191](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/191).

An assertion says that two signs, flags, classifications, or symbolically encoded claims *agree* or *differ*. Put enough such relations into a network, and one can obtain an impossible demand: A equals B, B differs from C, and C equals A. Nothing in the sound or appearance of any individual edge reveals the collision. The collision belongs to the **closed path**.

Our small instrument exposes that property, supplies an auditable inconsistency certificate, and renders the result as a chord. It also asks a more unusual question: if every actor may locally invert the meanings of its two binary symbols, which properties survive the translation?

## 1. What is in the instrument

| Artifact | Purpose |
| --- | --- |
| [THEORY.md](THEORY.md) | Formal signed-graph translation, proof, switching symmetry, countercases and transfer |
| [SOURCES.md](SOURCES.md) | Consulted primary literature, metadata and exact reading limits |
| [choir_lab.html](choir_lab.html) | Open locally in a modern browser for edge toggles, local binary relabelling and user-initiated Web Audio; browser visual acceptance pending |
| [choir.py](choir.py) | Standard-library, finite graph analyser, certificate verifier, brute-force comparator, gauge switch, deterministic stereo PCM |
| [test_choir.py](test_choir.py) | Exhaustive 729-graph and 16-local-switch stress tests plus boundary controls |
| [AFTERWORD.md](AFTERWORD.md) | Deliberately speculative aesthetic essay |
| [EVIDENCE.md](EVIDENCE.md) | Execution/check identity and review boundaries; amend only on actual results |

Run from the repo root with Python 3.11+:

    python -m unittest discover -s research/expeditions/frustrated-choir -p 'test_*.py' -v
    python research/expeditions/frustrated-choir/choir.py --out build/mhac-x007

The command generates five original stereo WAVs plus a JSON receipt in disposable \`build/\`. A narrow bridge in \`tests/test_mhac_x007.py\` runs the exact local tests under the standard repository CI. Outputs are **not committed as fabricated baseline evidence**; anyone can reproduce them.

## 2. A worked four-edge collision

Start with these binary relations, all explicitly invented:

| Edge | Statement | Binary parity |
| --- | --- | ---: |
| e1 | A same as B | 0 |
| e2 | B different from C | 1 |
| e3 | C same as D | 0 |
| e4 | D different from A | 1 |

The closed path has XOR = 0 ⊕ 1 ⊕ 0 ⊕ 1 = **0**, and can be assigned consistently (for instance, A=B=0, C=D=1).

Flip only the last statement to **D same as A**. The XOR becomes **1**. No choice of labels for A, B, C, D satisfies all four edges. The first three form an accepted path, and the fourth receives an explicit path-based refusal certificate.

In the synthetic sonification, each closing loop yields one 0.60-second stereo event. A zero-parity loop uses matched 440 Hz tones; a one-parity loop uses 440 Hz in the left channel and 466.16 Hz in the right. The sound mapping is an **arbitrary artistic convention**, not a measured comprehension result.

## 3. A local label switch does not change the loop

Let a local convention flip be g(v) in {0,1}. Replace an edge parity p(u,v) by

    p'(u,v) = p(u,v) XOR g(u) XOR g(v).

Individual edge labels may now disagree with the previous recording, yet XOR around every closed loop remains the same: each vertex contributes its flip twice and cancels.

The two files \`frustrated.wav\` and \`switched_frustrated.wav\` must therefore be **byte-identical**: the renderer receives only the closed-loop parity, not the absolute labels. An actual assertion flip, however, changes the loop parity and the WAV bytes. These are mechanical invariance properties of the code and are tested; they are not proof of identical listening experience across rooms, people or devices.

## 4. Why the negative results matter

The program does **not** nominate an incorrect edge. An inconsistent four-cycle can be repaired by changing any one of its four constraints; without an external authority one cannot identify the culprit.

Its greedy accepted subset is not globally optimal. The six-edge counterexample in [THEORY.md](THEORY.md) requires rejecting **two** edges in stream order, although changing just **one** original relation would make the entire set consistent. Input order can also change which edge is refused.

A tree has no closed loops, and every binary parity assignment on its edges is jointly satisfiable. That includes arbitrarily many fictional and untrustworthy assertions. The absence of a warning tone therefore does **not** imply credible evidence, correctly described measurements or even that a message was received.

## 5. Potential exaptation, strictly conditional

A versioned multi-agent knowledge system, distributed game state, diagnostic rule graph, or synthesizer routing design could record typed pairwise **same/different claims** and run a tiny, source-local loop check before presenting mutually inconsistent claims as one coherent account. A witness is a **proof of incompatible stipulated relations**, and its path is useful for subsequent human inspection.

That design has not been deployed or evaluated. What is transferred is an algebraic consistency check plus a reproducible audio metaphor—not authority to reject a safety alarm, choose a fault culprit or decide that a machine is telling the truth. This expedition remains separate from MHAC's Track E experimental evidence and Track G/Brier reconstruction.

**Implementation provenance:** GPT-6 authored the original test program, mathematical exposition and synthetic audio renderer. Automated tests are mechanical checks, not independent expert peer review; no participants, permissions, external submissions or copyrighted audio were involved.
