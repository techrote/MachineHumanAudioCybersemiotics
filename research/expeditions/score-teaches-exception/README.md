# The Score That Teaches Its Own Exception

27 November 2026 | Humanities Drift | Refs #815 | Draft/HOLD. Original essay, finite proof and sound score by one GPT-6.2 assistant. No human participant data, independent review, publication submission or frozen Track E/G promotion.

## A school of perfectly obedient instruments (fiction)

The conservatory has two instruments and three bells for instruction. Each bell may sound high or low. A fourth answers. The pupils rehearse in a room where the second and third bells always agree. Both instruments answer correctly, even when the first bell changes. The teachers congratulate themselves on the success of their curriculum.

A pupil brings a fourth pattern from the courtyard: the second bell high and the third low. For the first time, the instruments disagree. Neither has malfunctioned. Each is still obedient to the rule with which it was built.

The conservatory issues a certificate for the first instrument. The pupil asks whether the certificate belongs to its responses, its rule, or the room. A clerk replies that the room was not a subject of examination.

## Projection, correctness and apprenticeship

The previous Humanities Drift expedition (#811/#812, pinned below) considered a fixed sound with changing interpretations. Here the interpretation is fixed in each instrument, but the rehearsal samples cannot determine which response rule is operative. The question is not whether the same sound may have two meters; it is whether the same successful training history licenses two contradictory continuations.

**Source encounter S1 (secondary):** Stanford Encyclopedia of Philosophy, [Nelson Goodman](https://plato.stanford.edu/entries/goodman/), substantive revision 8 February 2024, §§5.3–5.4, from the copper/third-son comparison through the grue/bleen definitions and the account of entrenchment. Read those passages, not all of Goodman's *Fact, Fiction, and Forecast*; the primary book was not retrieved. The entry locates the projectibility definitions at FFF p.108. Goodman's challenge is not simply that future events are unknown. It concerns which predicates support projection: equivalent past observations can support descriptions with incompatible implications for new cases. Changing the primitive vocabulary can exchange which predicate appears temporally exceptional. Entrenchment supplies a historically situated account of projection practice; it is not a universal proof of future success. Our example is a finite, deliberately restricted analogy rather than a resolution of the new riddle.

**Source encounter S2 (secondary):** SEP [Rule-Following and Intentionality](https://plato.stanford.edu/entries/rule-following/index.html), revision 23 November 2026, §2 opening and §2.1, plus the finitude and error discussion in §4. Read these passages, not Wittgenstein's complete *Philosophical Investigations* or Kripke's 1982 book. Kripke's sceptic distinguishes the ordinary addition rule from an alternative that agrees on familiar inputs. Crucially the philosophical challenge concerns what constitutes meaning and correctness, not just how to guess a black-box function. There are competing interpretations of that challenge. Our finite oracle presupposes a rule class and a correct response function; it cannot establish what makes those presuppositions normatively binding. Nor does it license calling an apprentice wrong when the convention was never specified.

An educational error is to assume that repetition is identical to variation. In the conservatory, hundreds of excellent performances can reinforce one habit while failing to expose a rival that agrees throughout the rehearsed region. But it would be equally mistaken to suppose that repetition has no value. Repetition can protect already observed distinctions from errors, allow skill acquisition, or develop preference. The new model separates those possible functions.

**Source encounter S3 (primary research, bounded reading):** Psyche Loui (2012), [Learning and Liking of Melody and Harmony: Further Studies in Artificial Grammar Learning](https://doi.org/10.1111/j.1756-8765.2012.01208.x), *Topics in Cognitive Science* 4(4), 554–567. Publisher HTML, abstract, §§2.1.2–2.1.3, 2.3, 3.1–3.3 and 4 opening read; figures and embedded formula images not inspected. In Experiment 1 the exposure repertoire omitted some legal pathways; the author reports unsuccessful recognition/generalization alongside increased preference for familiar items. Experiment 2 changed the harmonic relationships while retaining the grammar pathways; recognition/generalization succeeded without the reported preference effect. The author considers perceptual grouping and exposure duration as qualifications. This is evidence of a possible dissociation in these tasks, not a general theorem that repeated examples are useless or that listeners reason using binary affine functions. No full appraisal, extraction or reanalysis was conducted.

**Source encounter S4 (abstract only):** Loui, Wessel and Hudson Kam (2010), [Humans Rapidly Learn Grammatical Structure in a New Musical Scale](https://pubmed.ncbi.nlm.nih.gov/20740059/), *Music Perception* 27(5), 377–388, DOI 10.1525/mp.2010.27.5.377. Indexed abstract reports recognition/generalization after exposure to constructed finite-state grammars in an unfamiliar scale. PMC full text attempt met a CAPTCHA. No detailed methodological claims from that inaccessible text.

**Interpretation:** A pedagogical instrument might play the edge of its teaching vocabulary, not merely its most familiar motifs. In a creative setting the resulting disagreement can be composed, and in an operational setting it can identify an unqualified situation. The two uses need separate authority: there is no aesthetic obligation to reveal a hidden rule as early as possible, but an emergency cue should not rely on the audience guessing what was never taught.

## The finite conservatory

Let x=(x0,x1,x2) belong to the binary cube. A response rule has the form

    h(x) = b XOR a0*x0 XOR a1*x1 XOR a2*x2.

There are sixteen distinct affine Boolean functions. A row of rehearsal records an exact context and one binary response. The 3 cues are authored, not inferred from audio. The scope is known feature identities, no context-label error, fixed rule, arbitrary label substitutions and flagged missing responses. No claim about a human learner is built into the definition.

Take rules A=x0 and B=x0 XOR x1 XOR x2. The four contexts coded as integers 0,1,6,7 have x1=x2. Both rules agree on all these contexts. Repeating them indefinitely cannot distinguish the two rules. Among the sixteen stipulated rules these are exactly the two survivors (three independent augmented rows). The context 2, bits (0,1,0), yields response 0 under A and 1 under B. It is the exception that teaches the difference. It is not an exception to either rule.

**Theorem (noiseless coverage).** Write v(x)=(1,x0,x1,x2) over GF(2). For a consistent rehearsal let r be the rank of its augmented rows. Exactly 2^(4-r) rules remain. The response at a new context z is determined if and only if v(z) lies in the row span.

Proof: the observations are a consistent linear system with four unknown coefficients. Its solution set is a coset of the null space, of dimension 4-r. Evaluation at z is constant over the coset exactly when the row v(z) annihilates the null space, equivalently belongs to the row space. Otherwise half the surviving rules predict each label. Thus four affinely independent contexts are necessary and sufficient for unique identification. The same argument applies to d bits with d+1 coefficients. Repetition changes no row span. A novel but dependent context can be no more informative than a repeated example.

**Representation warning:** an unrestricted Boolean rule can agree with the affine rule on the four-context basis yet disagree on any unobserved context. For the full unrestricted class there are 2^(8-m) functions compatible with m distinct labelled contexts. A unique answer under the affine class is not a uniquely warranted answer outside that class. Even exhausting all eight contexts does not determine an extension to a new feature or future regime.

## When rehearsal must survive mistakes

For counts c_x of each context, N=sum c_x, the response code's exact minimum Hamming separation is

    D(c) = min over nonzero affine g of sum_x c_x*g(x).

Any two distinct hypotheses differ by a nonzero affine function; conversely each such difference is realized by two hypotheses. Thus universal identification under e arbitrary label flips and f flagged response erasures holds precisely when 2e+f < D(c). Necessity follows by erasing up to f differing positions and splitting the remaining disagreements between the two explanations. When D=0 even the noiseless contract fails. This is the familiar coding argument, not a new general coding theorem.

**Sharp optimal design at every length for three cues.** Write N=8k+r, 0<=r<8. The optimum is

    D*(N) = 4k + [0,0,0,0,1,1,2,3][r].

Proof of upper bound: for every nonzero linear part a, the two complementary affine rules with coefficients (0,a) and (1,a) have weights summing to N. Hence D<=floor(N/2). Let W_a=sum_x c_x*(-1)^(a dot x). Then their smaller weight is (N-|W_a|)/2. Equality with the half bound for even N requires W_a=0 for all nonzero a. Inverting the Walsh transform forces all eight counts equal, so 8 divides N. For r=2,4,6 this yields D<=floor(N/2)-1.

For odd N, achieving floor(N/2) requires every nonzero W_a to have absolute value 1, since each has odd parity. Orthogonality of the eight Walsh characters implies 8*sum c_x^2=N^2+7. But the least sum of squares of nonnegative integer counts with total N is achieved by distributing counts as evenly as possible, giving 8k^2+2kr+r. Substituting N=8k+r would require r*(8-r)<=7. This fails at r=3 and r=5, establishing the needed one-unit penalty. The same argument for M=2^d gives the necessary condition r*(M-r)<=M-1 (so r=1 or M-1 for odd r). This is a general necessary condition only; the complete residue optimum below is proved for three cues.

For lower bound take k complete cubes, then append a residual design of size r. Every nonconstant affine function has weight 4 per full cube; constant one has weight 8. For r<=3 append arbitrary distinct points, giving at least zero extra separation. For r=4 use the affine basis {0,1,2,4}; it has positive distance 1. For r=5 add 7 to that basis, maintaining distance at least 1. For r=6 use any six distinct cube points; a nonconstant affine function has at least two ones after deleting two cube points. For r=7 delete one point from a cube, retaining at least three ones. Together these meet the upper bounds for every N, including N<4 where the distance vanishes.

This is a proof of the exact best multiset of rehearsed contexts, not a claim of novel Reed–Muller coding theory. The full cube gives the first-order binary Reed–Muller code of length eight and dimension four. Its properties here follow directly from the displayed elementary argument. Scientific priority for this particular rehearsal-count formulation has not been assessed.

| N | Optimal D | One label flip guaranteed? |
|---:|---:|---|
| 4 | 1 | no |
| 5 | 1 | no |
| 6 | 2 | no |
| 7 | 3 | yes |
| 8 | 4 | yes |
| 9 | 4 | yes |
| 10 | 4 | yes |
| 11 | 4 | yes |
| 12 | 5 | yes |

A perfectly balanced eight-context rehearsal survives any one label flip and one erasure. At the boundary the actual received vector [0,1,null,null,0,1,1,1] admits rules x0 and x0 XOR x1, each with one label flip and two erasures. The oracle returns both. Adding three repetitions to the optimal eight observations cannot raise the optimal minimum distance at all; four well-selected additions can. That plateau is an arithmetic property, not a recommendation to shorten all teaching.

## An original score for the two conservatories

Each bar is four 200-ms slots: three cues followed by a reply. Cue bit 0 uses a 200 Hz triangle, bit 1 a 400 Hz triangle. Replies use 320 Hz and 500 Hz triangles for 0 and 1. The first 150 ms sounds with 10 ms fades, the last 50 ms rests. Mono PCM16, 16 kHz. These are arbitrary authored acoustic conventions. No acoustic discriminability, loudness equality, music-learning or semantic claim.

Movement I, *The room*: play contexts 0,1,6,7 twice, with their answers.

Movement II, *The courtyard*: play context 2; allow the two scores to disagree in their fourth note. The two complete editions lawA and lawB are each 7.2 seconds; their first 112000 PCM samples (7 seconds, including the three new cues) are byte-identical. The final answer distinguishes them. Do not claim that a listener heard the difference, inferred either law, or prefers either piece.

Movement III, *The catalogue of neglected questions*: the counterexamples edition plays all eight contexts once, with law A. Its length is 6.4 seconds. Invite an imagined teacher to select the four-context basis instead, or to repeat the confounded four contexts. These are equally long in the four-example case, but not equally informative within the declared class.

Movement IV, *An instrument that may refuse*: a performer may answer neither tone when two rules remain compatible. This silence is an added artistic convention, not an output of the binary model. If silence were an operational abstention signal it would need a separate, explicitly qualified code.

Render and reproduce with Node:

    node research/expeditions/score-teaches-exception/laboratory.cjs build/score-teaches-exception

The script writes three WAVs and prints the deterministic JSON receipt. The laboratory compares the common PCM prefix exactly and records noncryptographic FNV-1a fingerprints for the raw PCM; these fingerprints are not identity/authenticity evidence. Original tones only, no samples from third-party scores. No participant solicitation.

## Negative sediment and a proposed instrument

A teaching sequencer could show the span of prior contexts beside the complete surviving-rule list, offer a diagnostic example, and separately qualify label-error distance. In a speculative performance the composer could hide the rule vocabulary, allowing the score's exception to be heard as a dramatic rupture. In an interface the vocabulary, response roles and unseen region should be declared. A simple typed protocol can implement these ideas without any incremental cybersemiotic mechanism.

- More examples can add no distinction; the two-rule confounded witness remains forever unless the missing context is supplied.
- An affine basis identifies noiselessly but has distance one. One flipped label may select the wrong rule with apparently perfect confidence.
- A balanced curriculum over authored contexts is not necessarily balanced in perceived features. A listener may not distinguish 200 and 400 Hz as intended, and non-affine hypotheses remain possible.
- Correctness in a rehearsed task does not establish meaning, willingness, preference, successful physical action, consent or knowledge of the rule.
- If the context itself is corrupted, delayed or ambiguous, the fixed-input error guarantee is inapplicable. If the rule changes over time, no fixed-function estimate is adequate.
- A surprising artistic continuation is not necessarily a failure; a new rule can be part of the piece. A safety-relevant continuation must meet a separately authorized contract.

The follow-up empirical question would vary diversity and repetition independently while holding exposure length, marginal tone counts where feasible and presentation conditions constant. Measure recognition, novel-context generalization, confidence and liking separately; do not interpret preference as rule acquisition. A null result or better generalization in the confounded condition would challenge the usefulness of this particular pedagogical model, not the algebra. No participant protocol or empirical outcome is claimed.

## Verification and continuation

Repository reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; governing AGENTS, RAG, programme, runbook, integrity and validation read. Recent 30 issues/30 PRs and all 471 branch entries examined, targeted projectibility/grue/teaching searches, compared earlier #197, #205, #471 and #811 scope. No matching active candidate found. #815 is new scope, only this expedition path mutable. No inherited branches edited; no merge authority. Predecessors exact heads verified open Draft/HOLD with successful exact-head PR workflows: #812 at 066230908efee7a2840eb3ff80410027f6aac354, run 46037108137; #814 at 751be8060338b4caf4847797730b760d7831de02, run 46044283699. These do not validate this new work.

Executed V8 oracle: 4,096 rank checks, 32,768 prediction-span checks, exhaustive 125,969 context-count vectors at lengths 1–12, 512 construction checks at lengths 1–512 and 2,512 complete strict-budget binary fault-pattern decodes for the eight-context cube. All assertions passed. Exact boundary counterexample, audio fingerprints and full count witnesses in execution.json. No full native repository qualification or independent scientific review in this run. The source and execution receipt must be compared after commit.

Humanities Drift advanced: #815. Next possible humanities direction: the rhetoric of the exception, contextual learning vs institutional correctness, or another distinct source-led aesthetic tangent. Concept Excavation preserved: #813/#814, next unknown multiplicities or shared omissions affecting subsets of witnesses. Next run should rotate to technical research. Neither lane is displaced by the hybrid form of this record.

*Fictional coda.* The pupil returns with the note nobody rehearsed. The teacher first marks it wrong, then discovers that both instruments can cite every previous lesson. She adds a page to the score, not to declare one instrument virtuous, but to name the question that had been absent from the school.
