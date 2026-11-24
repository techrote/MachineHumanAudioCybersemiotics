# The Orchestra Behind the Veil
## Sound objects, source ownership and the price of asking who played

**Expedition #230 · 24 November 2026 · original formal/artistic exploration, not Track E/G evidence.**

### Contents

1. [The listener's two invitations](#1-the-listeners-two-invitations) — separate attentive listening from forensic attribution.
2. [The eight-event theatre](#2-the-eight-event-theatre) — construct identical signals with different ownership.
3. [The cost of revelation](#3-the-cost-of-revelation) — prove a sharp restricted interrogation bound.
4. [The veil has seams](#4-the-veil-has-seams) — controls, rival assumptions and claim limits.
5. [An instrument for alternative orchestrations](#5-an-instrument-for-alternative-orchestrations) — turn ambiguity into a mixer affordance.
6. [A research programme in miniature](#6-a-research-programme-in-miniature) — formulate discriminating next experiments.

## 1. The listener's two invitations

A composer invites a listener to ignore the instrument that caused a sound; an engineer invites the same listener to identify that instrument. The invitations are not contradictory unless we presume that there is one correct purpose for listening. A piece of musique concrète can be excellent precisely because its source refuses identification. A maintenance system may need the opposite: an independent account of where a sound came from, because the next action depends upon it.

Michel Chion's *Guide to Sound Objects*, entry 10 and entry 11 (printed pp. 28–31), presents phenomenological suspension as a change of listening intention rather than a refutation of ordinary causal listening. Entry 12 further distinguishes the sound object from its causal body, signal, recording medium and score. This matters more than the familiar anecdote about hearing a hidden instrument. Concealing a source is a condition of access, whereas reduced listening is a disposition. Neither is identical to the mathematical operation of erasing source labels. Chion's own account allows causal knowledge to help attend to a sound's qualities; the separation is a methodological redirection, not a universal prohibition.

Albert Bregman's archived laboratory introduction to auditory scene analysis describes a different investigation: the auditory system organizing mixed evidence into representations likely to belong to individual sound-producing events. If Chion asks what becomes available when causal curiosity is bracketed, Bregman asks how plausible causal groupings are established despite mixing. Neither supplies a proof that a particular inferred source partition is physically correct. Brian Kane's chapter abstract on Schaeffer adds a useful caution: a phenomenological theory is itself disputable. The abstract identifies historical and ontological objections; it does not give their complete arguments.

**Interpretation.** A fruitful audio system might offer both invitations without presenting them as competing truth claims. One listening mode asks what kind of sound this is, another asks what produced it, and a third asks what would change if a purported source were removed. The third adds an intervention to an observation. A beautiful answer to the first question cannot serve as a certificate for the last two. Conversely, source verification is not a prerequisite for aesthetic enjoyment.

The present construction deliberately works below the level of phenomenological description: one observed waveform, two explicitly stipulated generator labels, no listener, room acoustics, loudspeaker or psychoacoustic model. It is a finite source-attribution game, not an explanatory theory of hearing.

## 2. The eight-event theatre

Let n=2k distinct, nonzero, mutually disjoint time blocks constitute a mono signal y. Each block belongs in its entirety to one of two labelled tracks A and B; each track owns exactly k blocks. An independently authenticated anchor says the first block is A. All blocks have equal squared sample energy E. There is no extra constraint relating source identity to pitch, rhythm, spatial position or timbre.

For every admissible ownership set S, define A_S to be y on blocks in S and zero elsewhere; B_S is its complement. A_S+B_S=y sample by sample, and the energy of each track is kE. Hence all admissible allocations have the same mono waveform, source count, individual event counts and individual energies. Knowing those quantities cannot uniquely determine S except in the trivial n=2 case.

The count is binomial(n-1,k-1), because the anchor fixes one ownership label and k-1 of the remaining n-1 blocks must be A. This is also the number of balanced unlabelled bipartitions, since the anchor chooses a canonical label orientation. Without the anchor, labelled allocations number binomial(n,k), twice as many.

For eight events, there are 35 anchored allocations. Compare:

    Event:       1 2 3 4 5 6 7 8
    Grouped:     A A A A B B B B
    Alternating: A B A B A B A B

Both produce exactly the same mono performance, including the same sequence of pitches and inter-onset times. Yet soloing A yields different sounds. Among the 35 allocations, the first and second events belong to the same source in 15 and different sources in 20. This is a count, not a claim about an actual prior distribution or about human preferences. With a stipulated uniform prior the corresponding probabilities are 3/7 and 4/7.

This is a constrained special case of the familiar underdetermination in single-channel source separation. The novelty sought here is not the nonuniqueness of a sum, but the combination of an artistic same-mix witness, a specified source intervention, a sharp cost for one kind of extra observation and a distinction between the purposes of listening.

## 3. The cost of revelation

**Formal model.** An oracle truthfully reveals the owner of one chosen block per query. Queries are noiseless, non-destructive, equally costly, and can be chosen adaptively. Let a and b be the remaining numbers of unknown A and B blocks. If either is zero, the rest are implied and the exact remaining cost is zero.

Otherwise, every as-yet-unknown block is symmetric under the candidate set. Both answers are possible; the minimax recurrence is

    W(a,0)=W(0,b)=0
    W(a,b)=1+max(W(a-1,b),W(a,b-1)), a,b>0.

Induction on a+b gives W(a,b)=a+b-1 whenever both are positive: a=b=1 requires one query; for a+b>2 at least one branch retains two positive counts, whose cost is a+b-2 by induction, and neither branch exceeds that. This gives an upper bound by arbitrary sequential querying and a lower bound against an adversary retaining both labels for as long as possible. Adaptivity cannot improve the worst case under this symmetric query vocabulary.

For anchored balanced n=2k, a=k-1 and b=k. For n>=4 the bound is n-2; n=2 gives zero as well. The bound is about **membership queries**, not all physically possible interventions. One exact solo recording with a reliable A label reveals every block in this toy model; it is one richer observation, not a contradiction. If arbitrary binary subset-of-candidate questions are permitted, a balanced decision tree achieves ceil(log2 M) queries for M candidates. Those questions need not be physically implementable.

| n | Anchored allocations | Worst membership queries | Arbitrary binary queries |
|---:|---:|---:|---:|
| 2 | 1 | 0 | 0 |
| 4 | 3 | 2 | 2 |
| 6 | 10 | 4 | 4 |
| 8 | 35 | 6 | 6 |
| 10 | 126 | 8 | 7 |
| 12 | 462 | 10 | 9 |
| 14 | 1,716 | 12 | 11 |
| 16 | 6,435 | 14 | 13 |

The gap at n=10 is the beginning of a second rabbit hole: the number of bits necessary to distinguish worlds is not always the number of questions necessary in a given interface. A request for more information might be perfectly sensible in abstract information theory and still unavailable in the instrument's vocabulary. The question design space itself has an epistemic geometry.

**Artistic experiment.** The Node laboratory generates eight consecutive 200 ms slots with 150 ms signed, enveloped square-wave blocks and 50 ms silence. The half-periods are 32,28,24,20,16,14,12,10 samples at 16 kHz. Integer amplitude envelopes make squared energy exactly equal across blocks independently of pitch. The mono signals for grouped and alternating ownership are byte-identical; stereo split and solo tracks differ. The 35 candidate allocations are all checked. Neither split is represented as an actual recording of hidden musicians: both are constructed source histories.

## 4. The veil has seams

- **Known source law:** if a trusted assignment rule specifies the first four events belong to A and the rest B, no ambiguity remains. Such a rule is excluded from the baseline, not denied in actual music.
- **More informative measurement:** one authenticated, complete solo track identifies every nonzero disjoint block in this toy. In a noisy, overlapping, reverberant recording even that may fail to have the same implication.
- **Degenerate allocation:** a known all-A assignment has zero uncertainty. n=2 with the balance and anchor also has only one possible allocation.
- **Disjoint does not mean independent:** the blocks are independent only in their algebraic supports, not necessarily as causal events or perceptual streams. Our renderer is a single algorithm with two logical tracks.
- **Equal energy is not equal loudness:** different frequencies and temporal organization may change perceived salience. No claim of perceptual equivalence is needed beyond the identical digital mono data.
- **Labels do not confer physical authenticity:** a stem in a digital workstation may be a routing channel, a role, an editing layer or an estimated source. Physical authorship requires different evidence. Even a correctly inferred partition does not establish instrument identity or who operated it.
- **No universal impossibility:** practical separation can exploit learned priors, distinctive source models, multiple sensors, spatial cues or controlled interventions. Their performance is empirical and outside this toy.
- **Not a clinical or safety protocol:** do not mute a real alarm source just to obtain attribution; the solo operation here is performed only on a synthetic, safe offline render.

Siamantas's thesis abstract describes monaural separation as underdetermined and discusses priors; Gillis's article abstract describes conditions for better-posed nonnegative matrix factorization. Neither is evidence that arbitrary priors recover historical source truth. Their relevance is the explicit role of assumptions, not a purported validation of our model. The counterexample is also distinct from X001's general observation map: this one asks which extra source-specific query is available and how expensive complete attribution is. X008's provenance plurality concerns corroboration; here we know the count of logical sources but not the partition. #199 changes observations through spectral feature summaries; here the entire waveform is identical. #201 asks for decision-sufficient clarification; here we intentionally require full assignment. #222 fills missing content; here no PCM sample is missing.

## 5. An instrument for alternative orchestrations

**Design proposal — not an implemented production feature.** Construct a "veil mixer" whose fundamental editable object is not a single set of stems but a family of admissible partitions of an immutable mix.

- *Reduced audition:* listen to the unmodified waveform with track names hidden; choose which sonic qualities are interesting.
- *Attribution audition:* switch among candidate partitions, including their stereo splits or solo responses, with every conjectural stem visibly labelled.
- *Intervention mode:* ask a selected membership question, import authenticated provenance or acquire a controlled isolated measurement; record which candidates it excludes.
- *Composition mode:* use the changing partition as an expressive parameter. Keep the full mix invariant while moving ownership between performers, spatial positions or processing buses; when one bus is attenuated, the differences become audible.

For a finite candidate family, a UI can show the exact set of still-possible owners per event; marginal frequency is optional and explicitly conditional on a named prior. It can also display a guaranteed invariant (e.g. total mix) separately from disputed identities. A cautious interface distinguishes generated stem, observed channel, independently authenticated source and artist-chosen mapping. On this toy, a binary source query splits the family and the remaining balance determines a stopping condition.

The musical idea is unusual: compose two scores whose difference is entirely latent until the listener acts. The performer can change a routing graph without changing the master output, then a mixer gesture reveals a concealed counterpoint. A sound can be constant while its potential responses to an interface change. This is an aesthetic construction, not a claim that the latent layer is perceived prior to intervention.

**Practical MHAC transfer:** a notification can be faithfully received as a waveform but still have an unverified originating subsystem. Source attribution should be independently linked to trusted metadata if an action depends on it; a source-separated audio estimate should not be mistaken for that metadata. The distinction is analogous to, but not a replacement for, existing T008 and T015 work on actor/source claims.

## 6. A research programme in miniature

A richer follow-up would compare blockwise membership questions against interval-count queries, group tests and source-isolation operations with different costs; allow inconsistent or unavailable answers; replace hard balance with a prior; and optimize for a specific decision such as which source may be safely soloed rather than reconstructing the complete partition. Each extension changes the hypothesis space or objective and must not be described as a stronger result of the present proof.

A future human experiment, only under the actual MHAC authorization gates, could compare source identification, freely reported sonic qualities, and intervention prediction under exactly matched mono recordings with different disclosed metadata. Controls should include genuine source-distinguishing cues and false but clearly fictional attribution in a consenting study design. We have no such results. An artwork, on the other hand, can stage the listening invitations without pretending to measure them.

The philosophical conclusion remains intentionally open: sometimes not knowing the source enlarges the domain of art, and sometimes it diminishes the domain of justified action. The desirable interface is one that lets its users see the difference.

## Reproduction

From this directory run Node 18+ with `node veil_lab.cjs /tmp/veil-output`. It emits the six WAV files plus results.json and executes the assertions first. See [SOURCES.md](SOURCES.md), [EVIDENCE.md](EVIDENCE.md), [AFTERWORD.md](AFTERWORD.md). No external libraries, downloaded recordings or human data.