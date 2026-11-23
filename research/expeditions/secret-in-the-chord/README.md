# The Secret in the Chord
## A distinction which is absent from every part but present in their combination

**Refs #218 · 23 November 2026 · bounded mathematical, interpretive and artistic expedition.** No empirical participants, no production privacy/security claim, no Track E/G advancement and no mathematical priority claim.

## Contents

1. Archaeology — reverse the direction of the preservation argument.
2. A two-channel secret — exact finite probability and sharp coupling bound.
3. The third voice — arbitrary-order counterexample and negative controls.
4. Source-critical comparison — secrecy, synergy and differential privacy are not synonyms.
5. The acoustic instrument — a reproducible four-chord vocabulary and its limitations.
6. Exaptation — a joint-release contract, its costs and a deliberately declined architecture.
7. The censor of intervals — original fiction.
8. Reproducibility and disposition — exact executed checks and outstanding review.

## 1. Archaeology: the argument goes both ways

Base main inspected: 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, RAG, programme, runbook, research-integrity and validation documents were read; current open issues and PRs were surveyed. X004's main README and the #209 working-branch README were examined alongside the main Chiastic Trap and Migrating Timbre reports. The latter two are useful for their separation of symbolic properties from human perception and their refusal to treat similarity as identity.

The [X004 sediment atlas](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/README.md) makes a defensible case for retaining distinctions. [#201](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/201) challenges indiscriminate clarification. [#209](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/210) makes the counterargument that information irrelevant to today's question may be essential to tomorrow's. Its text explicitly recognizes privacy and retention costs. Rather than invent a disagreement, pursue the missing constructive half: **does removing a protected distinction from each outward view remove it from the combined record?**

A machine might expose a harmless-looking status cue in speech and a separately harmless-looking diagnostic cue in a visual panel. A test of each marginal output may pass. Yet their association, synchronization or joint conditional distribution might distinguish a protected state perfectly. This is not about a human actually having decoded a signal. It is a counterexample at the level of an explicitly declared receiver model.

Contrast other live work (issue/PR scopes inspected; full technical review of each not claimed):

- #193/#194 concerns inflated belief from shared evidence ancestry. Here the observations may individually contain no information about the protected variable; the joint view can be informative.
- #195/#196 concerns intersection of admissible witnesses; our obstruction is equality of probability distributions, not the intersection of action sets.
- #199/#200 concerns homometric rhythms and inadequate features. Here two individual views can have exactly equal probability laws, not merely equal selected acoustic descriptors.
- #209/#210 seeks sufficiency for future decoder queries. Our protected variable must instead be *insufficiently inferable* by a declared observer.
- #214/#215 concerns higher-order knowledge among agents. We make no claims about what another observer knows about knowledge.
- #43/#44 concerns addressee and actor authority. Authorized disclosure and statistical distinguishability remain separate. No policy decision follows automatically from either.

The emerging methodological tension is real: preserving capacity for future interpretation and denying capacity for unauthorized inference can be incompatible. Neither policy dominates without a specified audience, purpose and time horizon.

## 2. A two-channel secret

Let S be a binary protected state; assume both values have positive probability. Let A and B be binary released symbols. Stipulate the *same* conditional marginal probabilities p=P(A=1|S=s), q=P(B=1|S=s) for s=0 and s=1. Each symbol separately is independent of S. Set t_s=P(A=1,B=1|S=s).

The joint table, in order 00,01,10,11, is

    (1-p-q+t_s, q-t_s, p-t_s, t_s).

Nonnegativity is equivalent to

    max(0,p+q-1) <= t_s <= min(p,q).

This is the elementary fixed-marginal coupling interval (a binary instance of classical Fréchet-type bounds). The derivation here is from four nonnegativity inequalities; we make no claim to have discovered that interval.

Define the total variation distance between the two conditional joint laws as half the sum of absolute cell differences. The difference vector is (d,-d,-d,d), d=t_0-t_1. Therefore TV=2|d|, and the sharp maximum over all permitted couplings is

    TV_max = 2[min(p,q)-max(0,p+q-1)]
           = 2 min(p,1-p,q,1-q).

For the last identity, if p+q<=1 the width is min(p,q), and both complementary probabilities are at least that minimum. If p+q>=1 the width is 1-max(p,q), the smaller complement. Opposite interval endpoints attain the bound, so it is not merely an upper estimate.

The individual TV values are both zero by construction. The joint TV can take any value between zero and the maximum; choose t_0 at the lower endpoint and vary t_1 continuously. This is a spectrum, not a binary claim that every coupled output leaks.

For equal prior probabilities of S and a receiver who knows both conditional laws, optimal single-observation classification success is (1+TV)/2: choose the more probable conditional cell and sum its contribution weighted by 1/2. With unequal priors this formula does not hold in general; use the prior-weighted likelihoods. TV is distinguishability of distributions, not an empirical human success rate.

| p | q | Maximum joint TV | Optimal equal-prior success at maximum |
| ---: | ---: | ---: | ---: |
| 1/2 | 1/2 | 1 | 1 |
| 1/4 | 1/2 | 1/2 | 3/4 |
| 0 | 1/2 | 0 | 1/2 |

At p=q=1/2 choose opposite couplings: given S=0 the pair is 00 or 11 with equal probability; given S=1 it is 01 or 10 with equal probability. Each marginal is a fair bit. Jointly, S=A XOR B, exactly. No additional lexical sign is needed; the distinction resides in the relation.

**Necessary caveat.** These are probability statements about repeated realizations of the stipulated conditional law or a single draw from it, not assertions that every finite recording has perfectly balanced histograms. They are not a general security guarantee against side information, partial access to a random seed, adaptation or repeated releases.

## 3. The third voice

For any integer n>=2 let X be uniform on n-bit strings satisfying XOR(X)=S. For any proper subset J of k<n coordinates, any fixed pattern of those coordinates has exactly 2^(n-k-1) completions of either parity. There are 2^(n-1) total strings for each S. Hence P(X_J=x_J|S=s)=2^(-k), independent of s. The entire tuple has disjoint conditional supports and recovers S.

No universal testing rule that stops at a fixed order r can establish non-disclosure of an unrestricted number of jointly observable views: choose n=r+1. This is a known type of parity/secret-sharing construction, not a new theorem in cryptography. Its use here is to refute an *interface audit shortcut*. Pairwise testing is stronger than marginal testing but still inadequate in the stated unrestricted class.

Negative controls and boundary conditions:

| Control | Result / significance |
| --- | --- |
| Same complete joint law under both secrets | Zero joint TV, even when A and B are strongly correlated. Correlation alone is not leakage. |
| Conditional independence of A and B given S, with fixed marginals | Product law fixed for both secrets; joint TV zero. Independence is sufficient, not necessary. |
| Conditional independence only pairwise | Not enough for the n>=3 parity family; every proper subset of coordinates is uniform. |
| Degenerate marginal p=0 or 1 | No remaining two-bit coupling freedom; the sharp bound is zero. |
| A different audience sees only one coordinate of the parity example | No information about S in that specified view, absent additional side information. |
| Unspecified side channel | The theorem says nothing about it; do not add it to the audit's accepted boundary by assumption. |
| Unknown or biased protected-state prior | Equal conditional laws still imply independence for any prior; classification accuracy under nonzero TV is prior-dependent. |
| Deterministic encoders of S alone | A nonconstant bit leaks immediately when both states have positive probability. The examples require variation from a latent variable or randomized model. |

A dangerous rhetorical reversal would be to declare every relationship among sounds a secret. A joint distribution must differ *with respect to a specified protected variable*. Neither apparent musical order nor complexity establishes that condition.

## 4. Source-critical comparison

**S1.** C. E. Shannon, 1949, *Communication Theory of Secrecy Systems*, Bell System Technical Journal 28(4), 656–715, DOI [10.1002/j.1538-7305.1949.tb00928.x](https://doi.org/10.1002/j.1538-7305.1949.tb00928.x). Publisher bibliographic record and IEEE abstract inspected. This is the foundational secrecy reference. Full text not inspected for this expedition; the proof in §2 is self-contained rather than a paraphrase of a particular Shannon theorem.

**S2.** Adi Shamir, May 1979, *How to Share a Secret*, MIT-LCS-TM-134, [MIT repository metadata and abstract](https://dspace.mit.edu/entities/publication/91c51bfc-5678-409c-80c5-44ce8fcdbadf). The abstract specifies reconstructability from a threshold number of pieces and non-disclosure below that threshold. Only metadata and abstract were read. Our XOR parity family is an elementary all-shares construction, not a reimplementation or attribution of Shamir's polynomial method. The intended reconstruction in secret sharing is precisely what is unintended in the interface counterexample.

**S3.** Paul L. Williams and Randall D. Beer, 2010, *Nonnegative Decomposition of Multivariate Information*, [arXiv:1004.2515](https://arxiv.org/abs/1004.2515), abstract inspected. The paper proposes information atoms separating redundancy and synergy. This motivates distinguishing information available individually from information available only in groups. We do not compute the paper's proposed partial information decomposition or resolve its axiomatic disputes. Our metric is conditional-law total variation. In the fair XOR example, elementary entropy also yields I(S;A)=I(S;B)=0 and I(S;A,B)=1 bit under a uniform prior; the TV argument does not require choosing a general PID measure.

**S4.** J. Near, D. Darais, N. Lefkovitz and G. Howarth, March 2025, *Guidelines for Evaluating Differential Privacy Guarantees*, [NIST SP 800-226, final publication page and abstract](https://csrc.nist.gov/pubs/sp/800/226/final), DOI [10.6028/NIST.SP.800-226](https://doi.org/10.6028/NIST.SP.800-226). The abstract describes a mathematical framework and practical hazards. The full standard was not read here. Do not equate our two-state statistical test with a DP certification. Under a stipulated adjacency relation making the two inputs neighbors, the parity example's individual mechanisms have identical laws while the joint mechanism has disjoint support. This does not contradict standard DP composition theorems: conditional behavior of the later release given previous outputs matters when shared randomness is used. A marginal guarantee by itself does not establish that conditional guarantee. No claim is made about the privacy parameters of real mechanisms.

All sources accessed as public publisher/repository metadata or abstracts on 23 November 2026 by the executing AI. No source full text, copyrighted page images, participant data or private records were copied. Source-level review remains intentionally bounded. The algebraic proof is original to this report in presentation, elementary in substance. Scientific novelty is not asserted.

## 5. The acoustic instrument

The laboratory generates four original one-second stereo PCM chords. Left channel uses 220 or 330 Hz; right uses 440 or 660 Hz; each is a separate fixed-envelope oscillator. Symbol indices 0 and 1 are merely chosen conventions, not natural semantics. The law is:

| Fictional state | Possible paired chords | Weight per chord |
| --- | --- | --- |
| 0 | 00, 11 | 1/2 |
| 1 | 01, 10 | 1/2 |

One isolated channel has the same distribution of complete digital sample arrays under either state. This follows because the renderer for that channel depends only on its own bit. The laboratory checks equality of corresponding channel PCM sample sequences across all four chords. The joint digital waveform distinguishes all four pairs under an ideal decoder with access to the exact generated arrays. No human pitch-recognition test, acoustic room model, downmix guarantee, hearing protection test or listener accuracy is claimed.

The score deliberately juxtaposes four files as a museum of possible realizations, not as four independent sampled trials. File labels, playback order, selection metadata, alignment, auxiliary recordings and knowledge of a randomizer are all possible extra observations. Treating the four-file directory as a privacy-preserving deployed mechanism would be a category mistake. A deterministic replay of an enumerated score is not a randomly selected secret-sharing trial.

The two-channel rendering is a minimal artistic demonstration rather than a recommendation that sensitive machine states should be encoded acoustically. Do not deploy it to conceal real information. Its purpose is to make a formal counterexample inspectable.

## 6. Exaptation: audit the view, not the widget

Candidate transfer: a test-only **joint-release contract** for toy telemetry schemas. Specify the protected distinction, allowed audiences, all streams each audience can associate, the model of association (simultaneous, session-linked, persistent, sequential), conditional joint laws or trace support, and the allowed inference tolerance. A test should operate on the resulting composite view, not merely on each component's documentation.

Use an exact oracle for small finite models. Compare complete conditional distributions, or explicitly bounded approximations with justified error. Negative controls must include harmless correlation and individually private-but-jointly-disclosing parity. Unknown observations are not certified absent. If a model does not enumerate the relevant receiver's observations, the result is a statement about an incomplete model rather than an acceptance certificate.

This connects to the earlier sediment atlas's quotient guard: in deterministic functional adequacy, a desired distinction must survive the representation fibre. For privacy, depending on the declared observer and distribution, a protected distinction must *not* survive as distinguishable output laws. The same act of representation is evaluated against opposed objectives. A single global maxim such as preserve every distinction or erase all distinctions is inadequate.

The cost of auditing every subset grows exponentially. Moreover, if an actual audience has the whole joint view, auditing the complete law is sufficient for its deterministic projections (projection cannot increase TV: apply the triangle inequality to sums within each fibre). Subset analysis becomes valuable when different audiences have different views or when locating minimal failing combinations matters. This saves us from proposing universal subset enumeration where a complete-view test already settles the question.

**Declined architecture:** no generic privacy middleware, obfuscation system, cryptographic API, or auditory security protocol is implemented. The model is too narrow for any such claim. The intended reusable artifact is the bounded test pattern and executable counterexample.

## 7. The censor of intervals

*Original fiction; no historical or empirical claim.*

In the municipal orchestra each player received a permit for two notes. Neither note was prohibited. The censor examined the clarinet's part and found it blameless. He examined the cello's part and found it equally innocent.

At the concert a particular relationship between two pitches caused an old mechanical lock in the concert hall to open. The censor demanded the forbidden note. There was none. He demanded the offending player. Each could repeat either sound without opening anything.

A young copyist proposed censoring the intervals. The orchestra objected that every consonance and dissonance would then require permission. Another proposed destroying the scores. The curator objected that a century of music would vanish.

The copyist eventually wrote a narrower instruction: inspect the score available to the lock.

The next morning the censor had a different problem. Someone had moved the lock into the public gallery.

## 8. Reproducibility and disposition

Artifacts: lab.js (dependency-free JavaScript finite oracle and WAV generator), crosscheck.py (separate standard-library Fraction enumeration), this report. Execute from this directory:

    node lab.js
    node lab.js --wav-dir ./generated
    python3 crosscheck.py

The JavaScript functions were executed in an ECMAScript isolate before their source was committed. The separate Python calculation ran in a local Python runtime. Both were constructed by the same AI, so the implementation separation is not independent authorship or peer review.

Actual executed outcomes:
- 818 margin groups, 5,403 ordered within-group table pairs, denominators 1 through 12.
- 508 subset-projection checks for n=2 through 8, including empty and full subsets.
- 5,911 combined comparisons in each implementation, all passed.
- JavaScript additional checks: 818 product-law margin controls, five invalid-input refusals, stereo PCM exact sample-isolation checks and WAV size check passed. The product-law zero-distance control compares the identical constructed distribution to itself, so it is a sanity check, not a separate empirical test of conditional independence.
- PCM buffers were synthesized and checked in memory; actual WAV-file CLI writing and human listening were not separately exercised. Reproducibility of samples across differing math libraries is not guaranteed byte-for-byte.
- The Python cross-check does not validate PCM, only the finite mathematical comparisons.
- Repository CI and exact final-head review are pending at report creation. No scientific or integration acceptance is asserted.

The grid enumeration confirms sharpness at every rational margin on the enumerated finite denominators, not a substitute for the all-real-margins proof. The JS integers are exact within the deliberately small executed ranges; the exposed helpers are not a hardened arbitrary-size numeric API.

Falsification/extension criteria: a valid binary table violating the exact bound would refute §2; a proper-subset conditional probability differing by parity would refute §3. Real receiver behavior, unmodeled side information or correlation from additional releases can invalidate the transfer hypothesis without refuting either proof. An audit of a different protected distinction requires new inputs. Review should specifically challenge the conditional-law assumptions and avoid confusing the four-file artistic score with an operational security mechanism.

No core claim records, frozen protocol, source/screening registry, programme metadata, or other workers' branches have been modified. This is an additive exploratory issue-scoped checkpoint, not a substitute for accepted MHAC empirical work.
