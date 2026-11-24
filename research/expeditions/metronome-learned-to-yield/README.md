# The Metronome That Learned to Yield

**Expedition #294, 24 November 2026. Exploratory humanities, mathematical construction and original sound art. Not a canonical evidence extraction or an empirical finding.**

## 1. The problem with a perfect rehearsal

Two percussionists play slightly out of time. One changes, the other stays put. Their next strike is more nearly simultaneous. The score of their improvement records only the difference between the two onsets, as if their contributions to the improvement were interchangeable.

Now reverse their obligations. The other percussionist changes, the first stays put. The difference is reduced by exactly the same amount, but their common future has moved in another direction.

The distinction is between the success of coordination and the distribution of adaptation. A click track normally seems like the least politically interesting member of an ensemble. But it is also the member whose timing is least negotiable. A machine that offers an adjustable rate of concession might be a very different instrument from one that offers only adjustable tempo.

This is not a moral condemnation of the click. An external reference is often useful, precisely because it does not yield. The interesting artistic question is whether the stability of the reference can itself become compositional material.

## 2. Intellectual collision: listening, correction, responsibility

**Source claims and bounded readings (agent-mediated web retrieval, 24 November; no source files retained):**

* Wing, Endo, Bradbury and Vorberg (2014), *Optimal feedback correction in string quartet synchronization*, J. R. Soc. Interface 11, 20131125, [DOI](https://doi.org/10.1098/rsif.2013.1125), [institutional abstract](https://research.birmingham.ac.uk/en/publications/optimal-feedback-correction-in-string-quartet-synchronization/), Abstract, sentences 1–7. The authors describe a phase-correction model and report different pairwise adjustment patterns in two professional quartets, despite near-optimal gains on average. This expedition only consulted the abstract, not the full article (PMC access returned a challenge). The authors' comparison of leadership styles is not a general political diagnosis.
* Wing, Endo, Yates and Bradbury (2014), *Perception of string quartet synchronization*, Front. Psychol. 5:1115, [full article](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.01115/full), Introduction final paragraphs, Materials and Methods opening, Discussion. The authors report listeners' discrimination of timing variability and sensitivity to its structure when correction gain was varied. The study used nine participants and virtual quartet excerpts; this is a bounded passage reading, not independent statistical appraisal. It cautions against claiming adaptation is inherently inaudible. Our narrower counterexample concerns a particular signed-difference observation, not every possible recording or listener.
* Heinz von Foerster, *Ethics and Second-Order Cybernetics*, SEHR 4(2), 1995 web version, [reproduced text](https://stream.syscoi.com/2018/10/21/ethics-and-second-order-cybernetics-heinz-von-foerster/), opening address, paragraphs beginning with the description of circular organization through the author's discussion of the cybernetician accounting for their own activity. A secondary-host reproduction of the author's text was read at passage level; edition fidelity not independently checked. Von Foerster includes the observer in the domain of cybernetic inquiry. It suggests an interpretive question about a measuring device which simultaneously participates in the phenomenon it measures. Our equations do not prove his epistemology.
* Pauline Oliveros, *Quantum Listening: From Practice to Theory (To Practice Practice)* (1999), excerpt attributed to Oliveros by the [Center for Deep Listening](https://www.deeplistening.rpi.edu/deep-listening/), section Pauline Oliveros on Deep Listening. Retrieved excerpt only; direct re-open timed out. Oliveros describes practices of widening awareness and focusing attention, including more than intended musical events. This is an important counterposition to treating listening as scalar timing-error extraction.
* Baker, Koivusalo, Troscheit and Zhang (2026), *On the Fourier transform of random Bernoulli convolutions*, J. London Math. Soc. 113(4), e70515, [article](https://londmathsoc.onlinelibrary.wiley.com/doi/full/10.1112/jlms.70515), §1 opening discussion of classical support versus measure regularity. Passage consulted; the Cantor/interval transition below is established mathematics, not a novelty claim. The random generalizations in that paper are not needed here.

**Interpretation:** There is something inadequate about calling a machine a listener solely because its next output depends upon a measured deviation. If it listens only for a phase error, then everything other than phase error becomes extraneous to its participation. Oliveros offers a productive tension: listening can enlarge the domain of attention rather than merely perfect correction in an already chosen domain. A machine may nevertheless be a valuable narrow listener; pretending it has a human's awareness would obscure its useful limits.

The phase-correction study offers an operational distinction between an ensemble's timing outcome and its adjustment relationships. Von Foerster supplies a different question: who chooses the observable by which the system judges its success? Neither makes the other true. A performer may willingly defer to a reference; asymmetry can be consensual, expressive, imposed, or irrelevant. No scalar correction coefficient can establish that social distinction.

## 3. Synthetic rendezvous geometry

Let A and B have onset offsets a and b with a < b, relative to an otherwise shared beat period. Start at a=0, b=D>0. Each correction round keeps fraction q of the previous difference, with 0<q<1. Exactly one player moves toward the other. If u=1, A moves by (1-q)(b-a); if u=0, B moves backwards by that amount. No noise, tempo adaptation, latency, missed beats, or unwrapped phase ambiguity occurs in this stipulated model.

After N rounds the signed difference is D q^N for every allocation history. The left endpoint is

    a_N = D (1-q) sum_{i=0}^{N-1} u_i q^i,
    b_N = a_N + D q^N.

Proof: each round removes exactly (1-q) of the current difference. Only A's moves accumulate in a_N. Both endpoints monotonically approach a common limit x. Every binary infinite history converges to such an x, and x lies in every nested interval [a_N,b_N].

Normalized by D, the reachable rendezvous set is the attractor of two maps f_0(x)=q x and f_1(x)=1-q+q x. The finite prefix cover is the union of 2^N intervals of length q^N. When q<1/2, siblings are separated by a gap (1-2q) times their parent's length; induction gives disjoint intervals. The cover length is (2q)^N, tending to zero. For q=1/3 this is the ordinary middle-thirds Cantor set. For q>=1/2, the two first-level images cover [0,1], and induction gives the entire interval at every depth. Every target has an infinite coding: recursively select a containing image and rescale. The nested intervals have lengths tending to zero, so the chosen code reaches the target.

Thus faster error contraction can remove attainable exact final rendezvous points. At q=1/3 and D=120 ms, the first decision leaves either [0,40] or [80,120] ms. No subsequent decisions can reach the 60 ms midpoint. At q=2/3 the first intervals overlap and any rendezvous remains reachable if the appropriate sequence is selected. Faster convergence remains faster; this is a distinct objective, not a paradox.

**Sharp finite comparison:** the fraction of the original interval not ruled out after N rounds when the entire prefix is unobserved is min(1,(2q)^N). This is geometric coverage, not probability of success or a uniform distribution on the limit set. If one allows simultaneous fractional sharing, a controller can reach the midpoint for any q by equal allocation each round. The obstruction therefore belongs to the combination of binary authority and strong contraction, not synchronization itself.

**Observation boundary:** the complete signed difference series identifies q if D>0, but contains no information about u. Absolute onset traces and known reference identify which side moved at each nonzero step in the ideal model. The four stereo scores deliberately preserve that richer evidence. They are not byte-identical and are not a proof of perceptual indistinguishability.

## 4. Executed laboratory and experimental score

Run `python lab.py` from this directory (Python 3.11+, standard library, assertions enabled). It enumerates 14,329 binary histories, for seven rational q values and depths 0 through 10; checks every trajectory against the direct finite-series expression, the exact residual at each step, disjointness below the transition, interval-union coverage for 77 parameter/depth combinations, and the continuous equal-allocation control. Four original stereo WAVs are rendered at 24 kHz, signed 16-bit; A is a 440 Hz pulse in the left channel and B a 660 Hz pulse in the right. Each beat has an 80 ms raised-sine-squared envelope; beat period 450 ms. The renderer records exact rational ideal offsets, rounded sample onsets and SHA-256, and reads back the written PCM. It is deterministic on the tested environment, not an assertion of cross-platform floating-point bit equivalence.

| Piece | q | Allocation | Ideal limit |
|---|---|---|---|
| yield-left | 1/3 | A always moves | 120 ms |
| yield-right | 1/3 | B always moves | 0 ms |
| alternating-fast | 1/3 | B,A repeated | 30 ms |
| alternating-slow | 2/3 | B,A repeated | 48 ms |

The first three share the same ideal difference trajectory. Each stops after eight correction rounds (nine strikes per channel); at the fast setting the final two ideal onsets are separated by approximately 0.0183 ms and round to the same sample in these particular clips. Absolute timing remains different. No human listening or hardware test was conducted.

**Score for two human players and one observer (original, optional interpretive performance):** 
Movement I: pick one player as reference, then swap. Do not change the nominal rhythm. 
Movement II: share the right to concede one correction at a time. The observer reports only how close the last two strikes were.
Movement III: the observer may also report how far each player travelled from the initial reference. Now make a collective target before playing; deliberately choose a contraction which makes the target impossible under the exclusive rule. 
Movement IV: abolish the exclusive rule and allow simultaneous, fractional concessions. Let players decide whether the restored reachability is worth the loss of the earlier rhythmic structure. Human performances need not realize the exact offsets; the computer score is a separate synthetic realization.

## 5. Exaptation: the Rendezvous Patch Bay

A sequencer may expose three lanes: nominal clock, error-contraction coefficient, and allocation of correction between voices. The last two are independent under the toy model. Let a user audition a target reference, visualize reachable intervals, and make correction allocation rhythmic rather than an invisible controller detail. An optional continuous sharing mode can restore any final target. A history lane should display both the actual correction and the distinction between an estimated and externally authenticated onset reference.

A hardware or DAW implementation would need to buffer future events so corrections cannot move already emitted notes; sample clocks, scheduler latency, phase wrapping, tempo changes and limits on inter-onset intervals are engineering constraints missing from this model. A sensible first prototype is an offline two-voice MIDI/audio generator, followed by a lookahead sequencer. A human-facing adaptive notification experiment would separately measure error, reference drift, predictability and perceived agency; do not equate any one with the others. A safety-critical clock must not silently enter adaptive mode.

A useful next mathematical direction is bounded stochastic correction and mixed allocation alphabets: the available interval maps may overlap unequally, and their attainable sets can differ from their probability densities. A useful artistic direction is to sonify the remaining *possible rendezvous intervals* as a branching filter bank, with silent spectral gaps corresponding to impossible targets. Neither is yet implemented.

### Speculative afterword — The clock that was excused

The colony had two clocks. One was bolted to the transit station; the other travelled with the workers. For a century the station published a single figure, the discrepancy, and celebrated every decline in it.

When the second clock finally learned to answer, the first declared that they had achieved mutual adjustment. The workers asked which clock had moved. The station's archive had no column for that.

They did not destroy the station clock. They placed a third clock in the square, with two controls marked *how quickly* and *who moves*. The controls were not mechanically coupled.

The first composition played on it was a duet in which neither performer ever struck the desired time. They came increasingly close to each other, however, and the municipal office reported a perfect rehearsal.

---

Checkpoint: based on main 495a98ca12bae467a507031f04931aa4254b1866 (repository-integrity success observed). Read AGENTS, RAG, programme, runbook, integrity, validation and workspace authorities; reconciled 60 recent PR summaries, 50 open issue/PR summaries and current expedition directory. New #294 body and empty comments retrieved. Neighboring #287 concerns comma-reset scheduling, #277 consensus stopping debt, #215 knowledge coordination; this expedition addresses geometric reachability under exclusive allocation. No claim of comprehensive novelty. One AI agent authored, source-checked and self-reviewed; no independent human review, canonical record promotion or scientific acceptance. No shared manifests or frozen records changed. PR review and exact-head CI pending at preparation.
