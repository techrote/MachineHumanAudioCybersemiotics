# MHAC-X003 — Causal Counterpoint

**Research status:** original finite mathematical/synthetic/audio expedition, **not** a user study, accepted empirical result, or adopted machine-voice policy. Refs [#183](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/183). Proposed for independent review as a Draft PR.

## Question

A queued audio system plays a succession of events. The ear hears a sequence; the logging graph may establish only a **partial** order. When is the phrase *A happened before B* actually warranted by system evidence, as opposed to being an artefact of the choice of playback order?

The key distinction is between **an event dependency** and **a chosen serialization**. One useful, but emphatically not universal, way to render a partial order into sound is to generate multiple counterfactual legal linearizations and let them disagree audibly. This is a compositional instrument, not a validated method of teaching causal inference.

## Exact finite result

Let `G=(V,E)` be a **finite DAG** of recorded, trustworthy event dependencies, and let `a` and `b` be distinct vertices. Write `a ≺ b` when there is a nonempty directed path from `a` to `b`.

**Linear-extension reversal lemma.** If neither `a ≺ b` nor `b ≺ a`, there exists a topological ordering placing `a` first and another placing `b` first. Proof: inserting `a → b` cannot create a directed cycle unless there was already a path `b ≺ a`. Likewise inserting `b → a` cannot create a cycle without a path `a ≺ b`. A finite DAG admits at least one topological order. The two augmented graphs produce the required witnesses. Conversely, if `a ≺ b`, every topological order must put `a` before `b`.

This does **not** establish that the real-world times of `a` and `b` were equal or reversed. It establishes only that their relative order is **not entailed by the declared dependency relation**. If the graph is incomplete, an absent path must never be rebranded as established Lamport concurrency or absence of real causal interaction.

## Fictional event world and exact oracle

There are two independent streams: `A.sense → A.emit`, `B.sense → B.emit`, both feeding `M.combine`. Both `A.emit` and `B.emit` are causal predecessors of `M.combine`, but there is no modelled causal relation between the two emits. The 5-event DAG admits **six** linear extensions, all enumerated without sampling.

The renderer takes two such legal sequences with opposite emit ordering, and plays them through the **left** and **right** PCM channels. Every event has a stable pitch; each note takes 0.22 s of a 0.32 s slot. The channels tell conflicting *serial stories* of the same dependency graph. These are arbitrary sound assignments. Different timbres/pitches/delays could yield very different perceptual effects; the demonstration makes no claim that listeners will decode the mapping correctly.

| Claim about events | Oracle verdict | Boundaries |
|---|---|---|
| `A.sense` causally precedes `M.combine` | `entailed` | A path exists |
| `M.combine` causally precedes `A.emit` | `contradicted` | A path exists in reverse |
| `A.emit` causally precedes `B.emit` | `not_entailed_either_way` | Both witness orders exist; this is not a claim of simultaneity |

**Different questions require different instruments.** Clock-time precedence needs reliable timestamp/uncertainty evidence; causal influence requires sufficient process/message evidence; a playback schedule establishes only the schedule of presentation. The program certifies none of those external measurement assumptions.

## Reproduction

Python 3.11+ and standard library only; from the repository root:

```sh
python -m unittest discover -s research/expeditions/causal-counterpoint -p 'test_*.py' -v
python research/expeditions/causal-counterpoint/causal_counterpoint.py --out build/mhac-x003
```

The generator creates disposable `linear-extensions.csv`, `two-legal-tellings.wav` (PCM16 stereo 22,050 Hz) and `receipt.json`. These are **synthetic examples**, not original field observations. The WAV is original and regenerated rather than committed as a binary corpus; its checksum appears in the receipt and [EVIDENCE.md](EVIDENCE.md).

## Critical and positive controls

- Positive: a total-order chain has exactly one linear extension and permits no reversal witness.
- Positive: a new dependency `A.emit → B.emit` removes the putative incomparability and reduces the number of legal serializations.
- Negative: two disconnected vertices admit two orders but that **does not** prove same-time occurrence.
- Negative: duplicate nodes/edges, unknown endpoints, self-loops, directed cycles and invalid causal claims fail closed.
- Negative: large factorial cases over eight events are refused, not misrepresented as exhaustively searched.
- Negative: even a formally valid alternate serialization does **not** demonstrate that human listeners spontaneously infer temporal or causal relationships.

## Non-duplication and transfer

This is intentionally distinct from [T010 #47](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/47) (freshness/deferral versus deadlines), [T014 #56](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/56) (retraction after emission), [T013 #54](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/54) (historical lexical presuppositions), [T004 #34](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/34) (field-binding grammar), [T007 #41](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/41) (received-waveform separability), and [X002 #181](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/181) (spatial coordinate-frame deixis). It tests **chronological claims implied by a chosen linearization** and their finite counterfactual witnesses, not task urgency, audio masking, message identities or actual chronology.

The reusable mechanism is a **causal-claim warrant oracle** paired with an optional **counterpoint score generator**. Possible later applications include log-playback interfaces, multi-agent incident reconstruction, a musical notation of partial-order ambiguity, and chronology-aware narration. Those are prospective design hypotheses, not validated findings. Read [SOURCE_NOTES.md](SOURCE_NOTES.md), [AFTERWORD.md](AFTERWORD.md) and [EVIDENCE.md](EVIDENCE.md) before citing or extending the experiment.

## Integrity declaration

One GPT-6 assistant wrote and tested the original code and material on 23 November 2026; primary-source consultation is bounded in `SOURCE_NOTES.md`. The finite tests certify code properties under declared inputs, not scientific novelty, model-independent review, listener behavior, authorized message semantics or safe product deployment. No empirical records, canonical registry, protocol, global manifests or other researchers' work were changed.
