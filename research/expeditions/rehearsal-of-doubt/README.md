# The Rehearsal of Doubt
## An ensemble can achieve perfect unison without sharing a guarantee of unison

Original MHAC exploratory essay and finite research toy; 2026-11-23. [Issue #214](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/214). Base 495a98ca12bae467a507031f04931aa4254b1866. AI-authored, internally checked; no external review, human observations, Track E/G admission or product requirements. [Sources](SOURCES.md) · [Lab](lab.mjs) · [Afterword](AFTERWORD.md) · [Execution](EVIDENCE.md).

## 1. A duet with two incompatible biographies

Two musicians receive invitations to play at a previously agreed beat. The first learns that the invitation exists; she sends a message to her colleague. He acknowledges it. She acknowledges the acknowledgement. Eventually they play, precisely together. Elsewhere two musicians have a public, perfectly observed invitation. Their performance is identical to the first.

The first performance establishes that the two musicians actually entered together, not that their local evidence made every alternative history impossible. The second ensemble enjoys a different epistemic architecture by stipulation. An audience with the recording alone cannot identify which architecture was used. Conversely, a failed entrance does not identify the architecture either.

This distinction is related to, but not equivalent to, Alfred Schutz's inquiry into musical sociality. The introductory passage of his 1951 essay uses music among several interdependent practices to investigate precommunicative social relations. The short primary excerpt is not evidence for an epistemic-logic interpretation of his phenomenology. Later work by Segre highlights both Schutz's interpersonal emphasis and Becker's conventions; Costelloe argues against reifying talk about inner temporality into a private mental mechanism. This is a productive disagreement, not a consensus to extract.

Our formal exercise does not model lived duration, bodily anticipation, musicians' expertise or musical meaning. It models one sharp question about local observations: does a fact hold in all histories compatible with what an observer sees? Halpern and Moses already distinguish levels of knowledge and discuss unreliable acknowledgement chains. The research contribution here is the bounded score construction and exact finite local-policy comparison, not a new distributed-computing impossibility theorem.

## 2. Finite model and proof

Let N be a known finite bound on deliveries and worlds W = {-1,0,1,...,N}. World -1 has no invitation; at 0 A knows the invitation but no message reached B. At k >= 1 exactly k messages in an alternating sequence reached their recipients, starting A to B. The next attempted delivery may fail; the model contains every shorter prefix. At a common evaluation beat, neither hears the other's output before choosing. No other observation disambiguates worlds.

A's local observation cells are {-1}, {0,1}, {2,3}, ...; B's are {-1,0}, {1,2}, {3,4}, ... . Truncate at N. Singleton terminal cells are permitted; this is a fully specified finite model, not a general network protocol. The proposition P is invitation exists, true exactly at 0,...,N. K_i(S) is the union of i's observation cells wholly contained in S. E(S) = K_A(S) intersect K_B(S). Define E^0(P)=P and E^(d+1)(P)=E(E^d(P)). Common knowledge is the intersection of all positive iterates.

**Proposition.** For d >= 0, E^d(P) = {k in W: k >= d}. Proof: base d=0 is the valuation. In the union of the two reflexive equivalence relations the underlying graph is a path, each consecutive pair connected by exactly one agent's nontrivial observation edge. A world belongs to E(S) precisely when it and all its immediate neighbors belong to S. Starting at the interval [0,N], each iteration deletes the left endpoint and leaves the remainder (or empty). Thus depth at k is exactly k, even at the terminal singleton. No positive world has common knowledge because the union path reaches -1. No asymptotic inference or infinite computation is required.

**Ideal public control.** Replace both agents' partitions by {-1} and {0,...,N}. The positive component cannot reach -1. E(P)=P, a fixed point, so all positive worlds have common knowledge. This is a model of perfectly public observation, not a claim about a speaker, room, broadcast or simultaneous human hearing.

**Independent decision result.** Let f_A and f_B be binary functions of their own observation cells, deciding to play or rest at the beat. Require jointness in *every* world, and silence in -1. If jointness holds, define g(w)=f_A(w)=f_B(w). The function g is constant across any edge of either observer, hence across each connected component. The private graph is connected, so silence at -1 forces silence throughout. The public graph has two components; g can be zero on the absent component and one on the positive component. This proves the exact policy counts: private two joint rules (both always silent / always play), one joint safe rule (silence), zero nontrivial joint safe rules; public four joint rules, two joint safe, one nontrivial joint safe. We count pairs of functions over realized observation cells, not arbitrary program texts.

The simple audition policy instead plays iff the individual knows P. In the private model, A plays from k=0 onward; B plays from k=1 onward. At every k>=1 the performance is perfectly coordinated, although jointness is not guaranteed at k=0. Thus observed success and a universal policy guarantee are strictly different.

## 3. Exact executable controls and score

Run Node 22+ (no npm or dependencies):

    node research/expeditions/rehearsal-of-doubt/lab.mjs out/rehearsal

The script checks all model bounds 0 through 32 and exhaustively enumerates all binary local policy pairs for N=0..10; it also synthesizes and verifies four 2-second stereo 16-bit PCM witnesses at 16 kHz. With N=8, private has 11 local bits and 2048 policy pairs; public has four bits and 16 pairs. The large assertion count includes sample-level waveform checks; not independent scientific trials.

| World/model | Each knows P? | Group depth | Score |
|---|---|---|---|
| Private -1 | Neither | P false | silence |
| Private 0 | Only A | 0 | left alone |
| Private 1 | Both | 1 | unison |
| Private 8 | Both | 8 | unison |
| Ideal public 8 | Both | Common | same unison |

The generated private-unison.wav and public-unison.wav are byte-identical. They consist of four enveloped 400 Hz square-wave pulses, left and right channels assigned to A and B. The solo and absent files are controls. The waveform is an original deliberately simple synthetic score, not a reconstruction of any source composition. Rendering is deterministic, exact integer samples; a centrally rendered score does not demonstrate real distributed synchronization.

## 4. Aesthetic interpretation: composing the unseen possibility of failure

Suppose a conductor is not a tempo-giver but an architect of knowledge. The conductor distributes permission, indication of receipt, evidence that receipt is visible, or an explicit public cue. An ensemble might play the same material using these different rules. Its score would therefore have a second, epistemic layer describing the relationship between performer and contingency.

A musical rest can become a deliberate declaration of insufficient knowledge, but it could also be aesthetic silence or the product of a failed channel. Sound is not an unambiguous record of the reason for sound. The interesting creative space is to expose these distinctions with an accompanying visual score rather than encode an allegedly universal language of hesitation.

A proposed rehearsal instrument, **The Doubt Conductor**, gives two performers private invitation panels, a public cue, and a policy selection (individual knowledge, always play, silence, ideal public cue). It enumerates the counterfactual histories with the same local observation. The display distinguishes the actual run from guaranteed outcomes across all modeled worlds. The composer may intentionally choose weakly coordinated rules and treat solitary notes as part of the composition. With uncertain physical timing, the timing tolerance must be specified separately. The engine currently supplies the exact symbolic and audio core, not a networked collaborative instrument.

A more radical artistic possibility: a concert where the public learns the score only after the performance, and hears an identical recording again under another account of who was permitted to know what. The second listening is not another auditory stimulus but another interpretation of the same trace. Whether a listener actually experiences it differently is a human research question, not a conclusion of this piece.

## 5. Adversarial boundaries and transfer

- Coordination can succeed without common knowledge in one history, and weaker coordination requirements can be satisfied without exact simultaneous agreement. Halpern/Moses explicitly address weaker variants. Our proof requires jointness in *every modeled world*, local deterministic policies, no extra observations, and silence when no invitation exists.
- Shared clocks do not tell participants that an uncertain invitation exists. Conversely an ideal public cue changes the equivalence relations; this is not merely a longer chain.
- Common knowledge of a false assertion's broadcast does not make the assertion true. Here P is factive by construction; authenticity and truth are assumptions, not repaired by sound.
- Confidence probabilities, approximate synchronization, randomness, adaptation and hearing the other player are not included. Correlated randomization cannot save a deterministic support rule required to be safe in every possible draw, but probabilistic or expected-payoff coordination is an explicitly different goal; no general randomization result is asserted.
- Neither phenomenology nor cognitive science can be reduced to a partition graph merely because both discuss coordination. Conversely philosophical critiques of inner time do not invalidate the finite proof.
- #33 studies repair lifecycle, #193 evidence independence, #205 choice menus, #183 partial order, #211 finite signal prefixes, #212 relational grounding. This toy concerns *higher-order knowledge and all-world local policy jointness*, not any of those constructions. It leaves their branches and canonical registries untouched.

Potential MHAC exaptation: in an interface rehearsal, display separate badges for a cue emitted, locally received, acknowledged, and jointly guaranteed under named assumptions. Do not collapse them into a single green 'everyone ready' indicator. A future human-gated experiment might compare explicit feedback with a single shared status; no performance prediction is claimed. The synthetic score is a falsifier of the inference from identical successful output to identical guarantees, not evidence for interface effectiveness.
