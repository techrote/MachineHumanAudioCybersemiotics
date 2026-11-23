# MHAC-X001 — The Observer's Solecism

*An open-ended expedition through grammar, incomplete observation, a compact extra dimension, and two sounds that cannot be told apart by a fixed set of witnesses.*

**Status (23 November 2026):** original source-backed conceptual research and a deterministic **synthetic-only** mathematical/audio experiment. It does not assert any novel Kaluza–Klein theorem, empirical listener study, tested physical instrument, production alarm code or accepted Track E/Track G conclusion. Refs [#178](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/178).

## Short version

Quintilian's grammatical error is not necessarily a defect in an isolated word: the error can be in the relationship between a word and its context. Formalising that suggests a question: when can a verdict about a richer state be recovered from a partial observation?

The first result is a simple theorem: an unobserved distinction cannot be deterministically recovered from observations that collapse it. We demonstrate this using spatial samples of two different cosine harmonics on a circle, and we make the difference sound by replacing fixed probes with a moving one.

The Kaluza–Klein connection is **restricted to the well-established Fourier decomposition of fields on a compact circle**. This expedition adds a novel *observer-sampling operation* and a metaphor; it does not discover a new physical interaction, identify hidden spacetime dimensions or prove a gap in higher-dimensional gravitation.

## Contents

| Document / source | Purpose |
| --- | --- |
| [MATHEMATICS.md](MATHEMATICS.md) | Projection theorem, finite-circle alias proof, countercases and falsifiers |
| [SOURCES.md](SOURCES.md) | Primary-source/lexical access record with precise reading limits |
| [AFTERWORD.md](AFTERWORD.md) | Original speculative post-human essay; not a factual scientific paper |
| [TRANSFER.md](TRANSFER.md) | Synth design, semiotic/HCI crossover, negative conclusions and future trails |
| [mode_alias_lab.py](mode_alias_lab.py) | Dependency-free deterministic sensor and PCM-stereo generator |
| [observer_lab.html](observer_lab.html) | Self-contained interactive polar field, sensor offset and optional stereo synthesis; browser acceptance pending |
| [test_mode_alias_lab.py](test_mode_alias_lab.py) | Focused numerical, edge-case and WAV structural assertions |
| [EVIDENCE.md](EVIDENCE.md) | Execution receipts and boundaries; what was actually checked |

## Run

Python 3.11+, standard library only. From the repository root:

    python research/expeditions/observers-solecism/mode_alias_lab.py --out build/mhac-x001
    python -m unittest discover -s research/expeditions/observers-solecism -p 'test_*.py' -v

The generator creates four **disposable** files in the selected output directory:

- fixed-probes.csv — eight spatial positions, modes 2 and 10, their differences (almost zero).
- shifted-probes.csv — same sensors with a common non-grid angular offset; modes become separable.
- moving-witness-stereo.wav — original 3-second PCM16 stereo: low mode in left channel, higher in right.
- receipt.json — inputs, eigenvalues, maximum errors and WAV hash.

By default, the circle contains **N=8** sensors and compares **n=2** versus **n+N=10**. With a chosen rotating probe at 55 revolutions/second, the left and right channels are mathematically generated at **110 Hz** and **550 Hz**. Their audibility and artistic value are not validated by participant testing.

## Original interactive instrument

Open [observer_lab.html](observer_lab.html) in a modern browser directly from the filesystem. It shows both continuous harmonic curves, the limited fixed witnesses, a separate moving probe, and optional synthesized stereo tones. Change the observer offset to distinguish the otherwise aliased modes, or alter the number of witnesses. The visual moving-probe speed is deliberately reduced relative to the audio scan, so it remains inspectable.

**Status:** source built and manually reviewed for obvious structure; no independent graphical/browser acceptance performed yet. The polar drawing is not a physical Kaluza–Klein measurement or scientifically validated visual representation.

## Why the sound is interesting

The two wave patterns are **different everywhere in general**, and their Laplacian eigenvalues differ, yet they produce equal values at each of eight fixed sensors. If an observer moves around the circle continuously, the patterns produce different time signals.

The poetic leap: an apparent grammatical or sonic mistake can be a signature of a coordinate the receiver never got to observe. This is an invitation to explore, not a claim that natural-language misunderstandings are simply Fourier aliasing.

## Non-duplication and independence

- [T009 #45](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/45) already studies multi-feature sonification and perceptual/semantic interference. We do **not** recreate its cue-polarity oracle.
- [T004 #34](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/34) covers audio source/event compositional binding; this study does not design an alarm grammar.
- [T013 #54](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/54) covers historical linguistic presupposition; this is about **observational equivalence** and a fictional philosophical consequence.
- [T018 #177](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/177) addresses emotionally framed human/agent interactions; a useful future crossover, but its agent task-quality questions are not being solved here.
- Canonical empirical searches, screening, frozen protocol, model records, research registry and manuscripts are unchanged.

## Interpretation

A mathematical proof here warrants a mathematical claim **within its hypotheses**. A synthesizer output demonstrates deterministic signal construction **within this program**. The speculative essay is an artwork and a philosophical thought experiment. Neither may be silently promoted to listener efficacy, machine understanding or new fundamental physics.

**Method disclosure:** one GPT-6 assistant prepared the materials using public primary/lexical sources, GitHub tool access and mathematical calculations. Self-review and automated tests are not independent scholarly or human verification.
