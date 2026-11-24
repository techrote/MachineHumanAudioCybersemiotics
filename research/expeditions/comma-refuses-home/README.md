# The Comma That Refuses to Go Home

**Expedition 286 | 24 November 2026 | exploratory, synthetic, not a frozen-protocol finding**

A note can return to its name without returning to its frequency. This expedition asks whether an instrument could make the management of that difference a compositional practice, and whether a communication system might benefit from distinguishing local relational fidelity from persistent reference.

## Sources and disagreement

Nyhoff, Aarskog and Holm, “Geometric Construction of Pythagorean and Just Musical Scales and Commas,” Mathematical Intelligencer 46 (2024), 25–31, [DOI](https://doi.org/10.1007/s00283-022-10260-4), HTML introduction, Table 1 and equations (1)–(4), consulted 24 November 2026. Their equation (4) identifies the syntonic comma as the difference in ratio between the Pythagorean third 81/64 and the just third 5/4. This is sufficient for the mathematical premise; no claim about universal preferences follows.

William A. Sethares, “Adaptive Tunings for Musical Scales,” JASA (July 1994), [author's descriptive page](https://sethares.engr.wisc.edu/papers/adaptun.html), paragraphs 1–3, consulted on the same date. The page describes real-time pitch adjustment based on a consonance objective that can be sensitive to timbre. Only that description, not the complete paper or perceptual evidence, was read. This is an important corrective to treating one just-intonation ratio as the universal goal of all tuning.

Stange, Wick and Hinrichsen, “Playing Music in Just Intonation: A Dynamically Adaptive Tuning Scheme,” Computer Music Journal 42(3) (2018), 47–62, [DOI](https://doi.org/10.1162/comj_a_00478), [2017 preprint abstract](https://arxiv.org/abs/1706.04338). Abstract-level reading only; attempted HTML full-text access failed. Their method solves equations to obtain tempered compromises where all desired intervals cannot be satisfied. This is existing adaptive tuning work, not evidence of novelty for our toy scheduler.

Thomas S. Kuhn, “Commensurability, Comparability, Communicability,” PSA 1982, vol. 2, 668–688, [publisher extract](https://doi.org/10.1086/PSAPROCBIENMEETP.1982.2.192452), opening paragraph only. Kuhn discusses changes in scientific vocabulary such that not all terms are definable in the rival vocabulary. For context, see [SEP, The Incommensurability of Scientific Theories](https://plato.stanford.edu/entries/incommensurability/), introduction and §2, revision 7 May 2024. Its introduction distinguishes problems of comparison from failures of translation. We do not infer that incompatible vocabularies are numerically commensurable or that scientific paradigms obey a pitch-ratio model. A rational comma is not Euclidean irrational incommensurability. The analogy is a prompt to notice what is lost when local relations are identified with global labels, not a demonstration of Kuhn's position.

Robert Hasegawa, “Tone representation and just intervals in contemporary music,” Contemporary Music Review 25(3), 263–281, [DOI](https://doi.org/10.1080/07494460600726529), publisher abstract surfaced in search, direct opening refused (403). Reading is discovery/abstract only. Its account of approximate referential intervals and the gap between compositional technique and aural experience motivates a question, not an empirical conclusion here.

## A score whose names have itineraries

**Construction.** Begin at C = 264 Hz. Perform C–G–D–A–E–C using successive exact ratios 3/2, 3/4, 3/2, 3/4, 4/5. The two descending fourths are octave-reduced fifths. Their product is q = 81/80. The return C is 267.3 Hz, one syntonic comma (1200 log2(q), approximately 21.506 cents) above the initial C. Reverse the itinerary and invert every ratio to multiply by 80/81 instead. No single static frequency can be assigned to every occurrence of C while satisfying all these particular relations. This is familiar tuning arithmetic, not a new theorem.

**Interpretation.** The mistake would be to regard the name as an absolute frequency when the score actually specifies an itinerary. There are at least three honest readings of C: a fixed reference, a class of notes subject to some equivalence convention, and an instruction to realize a position relative to the note just heard. Neither the notation nor the acoustics alone specifies which reading an instrument implements.

This is not just a choice between accuracy and error. A fixed-reference instrument can preserve its coordinates by compromising its local intervals. A relation-following instrument can preserve its local intervals by shifting its reference. A third can maintain both representations and refuse to identify them. A fourth can periodically relinquish the continuity of its relation-following performance.

The latter suggests a different kind of ornament: an explicit seam in an otherwise internally consistent history. Rather than perform the correction as an embarrassing imperfection, let its timing be composed.

## A bounded itinerary and its reset budget

**Formal toy model.** The state x is an integer comma exponent; the boundary frequency is BASE times q^x. An entire phrase takes a step d in {-1,+1}. Before each phrase, the performer may reset x to zero at cost one; otherwise the existing state is preserved. After every phrase require |x| <= B, B a positive integer. The bound applies to the returning reference only, NOT to the intervening note frequencies. A reset is an independent break between phrases; all five ratios within each phrase remain exact. No fractional reset, gradual tempering, free reanchoring, final reset, or additional cost is allowed. The horizon may end after any phrase; an online policy sees the current step but not future steps or the stopping time.

A reactive policy resets only when the next step would violate the bound. Is this the least disruptive policy if disruption is counted by number of resets?

Counterexample at B=2: steps - - - + + + +.

| Policy | Boundary states | Reset before phrase (1-indexed) | Count |
|---|---|---|---|
| No resets (unconstrained) | -1,-2,-3,-2,-1,0,1 | — | 0 |
| Reactive | -1,-2,-1,0,1,2,1 | 3,7 | 2 |
| Anticipatory optimum | -1,-1,-2,-1,0,1,2 | 2 | 1 |

The anticipatory reset occurs before the existing state would violate the bound. It is a discontinuity introduced in order to avoid two later discontinuities. Its count is optimal because no-reset playback violates the bound at phrase 3.

**Exact dynamic programme.** Let V_i(x) be the minimum reset count among feasible prefixes ending in x after i phrases. Initialize V_0(0)=0 and all other costs infinity. For each reachable x and incoming d, offer two transitions: to x+d with cost V_i(x), if feasible, and to d with cost V_i(x)+1, resetting first. Retain the least cost at every destination; store a witness. Future feasibility and costs depend only on x and the future steps, so induction establishes optimality. Cost-only computation uses O(NB) time and O(B) memory; the implementation additionally copies witness lists, which increases costs. A zero-to-zero reset is dominated. Compare the dynamic programme against an independently implemented brute-force search over all reset masks, not another recurrence.

**Online impossibility, B >= 2.** Follow a stream of negative steps. Any proactive reset within the first B steps already loses against a zero-reset optimum if the stream ends there. If no reset occurs, the (B+1)th negative forces a reset. Then present B+2 positive steps. From state -1, that suffix forces at least one more reset (earlier voluntary resetting still costs one). Offline, a single reset just before the Bth negative leaves state -2 after the negatives, then the positive run reaches B exactly. Thus no deterministic online policy can always match the offline optimum on arbitrary unknown horizons. This does not establish the best competitive ratio, an impossibility with known full score, or the optimum of any perceptual metric. The two-versus-one witness extends to every B>=2; for B=1 the stated family is invalid. The finite B=1 census below is a negative control, not an all-horizons theorem.

**Executed census.** V8 ran the same function definitions used to generate oracle.cjs. All 2,047 binary step words of lengths 0–10 per B (four B values; 8,188 total configurations) were tested. The dynamic programme agreed with brute reset-mask enumeration, witnesses replayed within bounds, and greedy was never better than the optimum. 182,333 checks passed including the general family B=2..32.

| B | Cases where reactive costs more | Largest observed excess |
|---|---:|---:|
| 1 | 0 | 0 |
| 2 | 46 | 1 |
| 3 | 6 | 1 |
| 4 | 0 | 0 |

B=4 is an observation-window control: the general counterexample has length 11. The absence of a counterexample through length 10 does not imply greedy optimality.

## Musical research: two kinds of home

The score in render.py is an original stereo piece, using six 150-ms notes per phrase. The left channel carries the itinerant pitch; the right channel repeats the fixed 264 Hz reference at each event. Both voices are enveloped sine oscillators. The piece is not a perceptual trial, a listening threshold test or a calibrated dissonance stimulus.

Three performances share the seven phrase directions but differ in reset placement. Listen at the returning notes and the following beginnings, not only to the melodic contour. The unbounded version violates the reference envelope; the reactive one interrupts twice; the anticipatory one interrupts once at an earlier point. They do not end at identical frequencies. A reset count is not a ranking of artistic merit. The listener may prefer the late seam, the earlier seam, or no seam whatsoever.

Reproduce with node oracle.cjs and python3 render.py. The latter generates three local WAVs, deliberately not committed. Each is 100,800 stereo 16-bit PCM frames at 16 kHz (6.3 s). Local repeat renders returned identical hashes on this environment:

- unbounded.wav: 969dd5f750e0451c082bde10fbaeefd2fd83a3a230c8ae902ee26af1e1e72f73
- reactive.wav: 22960a81a6216c667e5d376d252979be827524575efc147e8a24f7c86ce135b3
- anticipatory.wav: 77b8dd07a453d24a1af58bf914f3d0d5840de0db8d07d412cf2391e3cfc84536

Exact fractions were checked at every phrase endpoint and both phrase products. PCM headers were inspected; floating sine rendering is not guaranteed byte-identical on unrelated math libraries. No actual listening or participant validation is asserted.

## Exaptation: the reference organ

**Design hypothesis, not validation.** Make the synthesizer's global reference state an instrument in its own right. An itinerant oscillator bank receives rational intervals, with an independent persistent root and an integer prime-exponent ledger. A second performer sets bounds, reset costs and admissible reset locations. A third can introduce a tempered interval gradually rather than force a root snap. The screen should retain both the fixed-reference and itinerant interpretations of a pitch name. Do not silently discard the residual comma when exporting a score.

A rehearsal mode could compute a Pareto frontier over reference deviation, local interval error, seam counts and seam magnitudes. These quantities are not interchangeable; a single objective would require a declared weighting and cannot be assumed to express auditory experience. The implemented reset-only scheduler is the smallest useful component, not a general adaptive tuner.

An interface analogy: a machine message “same state as before” might refer to the same named category or the same measured value. An adaptive baseline can make every local comparison correct under its stated reference while allowing the baseline itself to drift. Display baseline version, original anchor, accumulated change and reanchoring as distinct fields. Test whether operators can identify a reference change in randomized, counterbalanced synthetic traces; actual participants require prior authorization. The design should also be tested against a fixed-reference control, including workload and whether extra metadata is distracting.

A possible falsifier of the proposed music interface is that performers cannot meaningfully control seam placement or do not find it useful under any accessible mappings. A possible falsifier of the machine-interface hypothesis is that explicit anchor versions add confusion without improving reference identification. Mathematical scheduling results cannot answer either question.

## Speculative afterword — Cartographers of a Note

In the colony of Nacre, each town possessed a tuning fork inherited from its neighbour. A traveller could reproduce every interval of the journey with extraordinary fidelity. At the end of a circuit, the fork no longer agreed with the instrument at the departure gate.

The Ministry of Geography made two maps. One showed the distances between towns. The other showed their locations. Neither map was permitted to correct the other without a public ceremony.

A musician arrived who performed that ceremony ahead of schedule. The inspector objected: the discrepancy had not yet exceeded the permitted limit. She continued playing. Seven towns later the inspector discovered that her unsolicited correction had prevented two compulsory ones.

The inspector wanted the composition to become a regulation. The musician refused. She had been counting ceremonies, not measuring their importance. In the next performance she allowed the fork to wander until the two maps disagreed by an octave.

Nacre's eventual anthem consisted of one note, one reference note, and the silence during which a committee decided whether they were still the same.

---

**Reconciliation and limits.** Read live README, AGENTS, RAG, programme, runbook, protocol index, integrity and validation. Main at 495a98ca12bae467a507031f04931aa4254b1866 at start. Reviewed 60 recent PR titles and 40 open issue summaries. #228 concerns static cycle-fit error; #272 winding reconstruction; #232 deletion-resilient synchronization; this scope instead concerns prospective discrete reset placement and the aesthetics of musical reference. No exhaustive novelty search; no shared manifest, scientific record, frozen protocol or production control changed. One AI-assisted author, ChatGPT, with V8 and Python execution; no independent human reviewer. No external acquisition or contact. Draft pending exact-head repository checks and review.