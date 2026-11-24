# The Chord That Loses Its Reference
## Silent coordinates, sparse interference and the cost of retaining relational signs

**MHAC #372 · 24 November 2026 · synthetic mathematical expedition.** This is an original derivation and computational witness, not a Track E empirical result, a Track G conclusion, a claim of mathematical priority or a human listening study.

## Contents

1. [An absence that removes a relationship](#1-an-absence-that-removes-a-relationship) — distinguish a known zero from an available phase reference.
2. [Exact ambiguity and correction](#2-exact-ambiguity-and-correction) — component count and cut-distance theorems.
3. [The sharp price of a fixed probe plan](#3-the-sharp-price-of-a-fixed-probe-plan) — minimal simple-graph budgets with and without support information.
4. [The quiet voice sets the noise floor](#4-the-quiet-voice-sets-the-noise-floor) — exact mixed bounded-noise and arbitrary-error guarantee.
5. [A second cost of weak voices](#5-a-second-cost-of-weak-voices) — even the support-informed optimal count can be invalid at unequal amplitudes.
6. [A witness and an instrument](#6-a-witness-and-an-instrument) — original audio and conditional applications.
7. [Evidence and refusals](#7-evidence-and-refusals) — source locators, computational results and qualification limits.

## 1. An absence that removes a relationship

Imagine three phase-locked voices with real coefficients. A meter records their individual squared amplitudes and the powers of the first-plus-second and second-plus-third mixes. It is a connected chain of planned observations. But suppose the second voice is silent.

Two worlds are x=(1,0,1) and y=(1,0,-1). Their individual powers are (1,0,1); their two pair powers are (1,1). The meter knows that the second voice is absent. It nevertheless cannot learn whether the outer two reinforce or cancel. A single outer-pair probe returns 4 in the first world and 0 in the second.

A silent coordinate does not create a wrong sign. It removes the means of relating two signs. This distinction is particularly useful for interpreting a relational observation system. A gap should not be quietly translated into a positive or negative relation.

**Model.** There are n named real scalar coordinates x_i. The powers x_i^2 are obtained exactly and reveal amplitudes a_i=|x_i| and support S={i:a_i>0}. Only one additional kind of scalar probe is permitted: (x_i+x_j)^2 for distinct i,j. A simple graph G records the pair probes; no repeated edge, no arbitrary linear mixture, no external reference, and no query cost differences. The entire vector remains unchanged during all measurements. We recover the vector up to one simultaneous sign flip. Supports of size zero or one are trivial. Below k>=2 is the lower bound on support size. All counts exclude the n individual power measurements.

For an active pair, (x_i+x_j)^2-a_i^2-a_j^2=2x_i x_j; with known nonzero amplitudes its sign provides exactly one relative sign. An edge incident to a zero is independent of the nonzero endpoint's sign.

This mechanism is established in more general form in Alexeev, Bandeira, Fickus and Mixon's polarization approach. Their section 2 uses complex frame coefficients, obtains pair phase through three polarization measurements, describes the failure of phase propagation through zero coefficients, and exploits frame redundancy and expanders. Our coordinate basis has no such redundant spanning frame: every active coordinate must be accounted for. This is a restricted problem, not a new general phase-retrieval method.

## 2. Exact ambiguity and correction

**Theorem A (exact fiber).** For nonempty support S, let c be the number of connected components of G[S]. Each consistent noiseless observation has precisely 2^(c-1) distinct solutions modulo simultaneous global sign.

Proof. Choose one sign per component. The observed relative signs along a spanning tree uniquely determine the remaining signs in that component. Other edges are automatically satisfied for consistent observations. Conversely any solution must agree with the first solution up to a constant sign on each component, since every measured product agrees. Independent component flips are possible and the simultaneous global flip identifies pairs of choices. Thus there are exactly 2^(c-1) classes. A disconnected planned graph is not necessary for ambiguity: a connected graph can become disconnected when silent vertices are removed.

**Theorem B (exact edge distance).** For |S|>=2, define lambda(H)=min over nontrivial vertex bipartitions of the number of crossing edges in H=G[S]; lambda=0 for a disconnected graph. The minimum Hamming distance between distinct sign classes' pair-probe vectors is lambda(H). In particular unique recovery against up to t arbitrarily corrupted edge values and e known erased edge values is possible for every observation iff lambda(H)>2t+e.

Proof. Two sign assignments differ by flipping a nonempty proper subset A of S (global equivalence excludes the other possibilities). Pair intensities differ precisely on measured edges crossing (A,S-A). Every cut can arise by such a flip. Edges outside S have no sign dependence. This proves the distance formula, including zero. If two classes could explain a received vector, outside the e erased positions the two predictions could differ at most 2t positions, contradicting the strict inequality. Conversely take a minimum-cut pair; erase up to e differing coordinates, then split the remaining <=2t differences into two sets of at most t. Assign observations from opposite predictions on the two sets. Both worlds explain the same transcript. This proof does not rely on a particular decoder. Enumeration of sign classes is one exact but not generally efficient decoder.

This is an application of the cut code, not a priority claim. A tree is sufficient for noiseless full-support signs, but every tree has distance one. It cannot withstand even a single unknown edge error. Cycle consistency alone may detect a contradiction without uniquely locating the wrong edge, as in the earlier Frustrated Choir expedition (#191); the present question is the worst-case correction budget.

## 3. The sharp price of a fixed probe plan

Let d=2t+e+1 or, more generally, the target cut distance. Assume 1<=d<=k-1. A graph selected before support is revealed must satisfy lambda(G[S])>=d for every support of size at least k. A support-informed design selects a fixed graph after the exact individual powers arrive but before the pair measurements; it can restrict its edges to active coordinates. This is two-stage support adaptation, not unrestricted transcript-adaptive optimization with adversarial answers.

Define R=n-k+d. The minimum number of distinct pair probes in the fixed design is exactly

    F(n,k,d) = ceil(n R / 2), if R>=2;
               n-1,             if R=1.

Proof of lower bound. For each vertex v, choose k-1 other vertices preferentially from its non-neighbors. Its induced degree can be made max(0,deg(v)-(n-k)). The required cut distance forces deg(v)>=n-k+d. The handshake lemma gives ceil(nR/2). When R=1, necessarily k=n,d=1, so connectedness strengthens that degree bound to n-1.

Proof of attainability. Harary's maximum-connectivity theorem (1962, Theorem 1, pp. 1143–1144) supplies a simple graph on n vertices with exactly ceil(nR/2) edges and vertex connectivity at least R whenever 2<=R<=n-1. Deleting at most n-k vertices leaves a graph with vertex connectivity at least R-(n-k)=d: any further deletion of fewer than d vertices cannot disconnect the remaining graph. Vertex connectivity is at most edge connectivity, so the desired cut distance holds. The R=1 case is a tree. This construction uses only existing elementary graph theory. The exact minimum follows from matching lower and upper bounds.

For a known support of size j>=2, substitute n=k=j. Thus the sharp two-stage cost is j-1 for d=1, and ceil(jd/2) for 2<=d<=j-1. If d>=j no simple active-edge design can guarantee it, because no vertex has more than j-1 distinct neighbors. If the actual support size is unknown but has a minimum k, the cost is a function of the subsequently observed j, not a promise to always cost the minimum-size value.

A surprisingly expensive feature of the fixed problem is the small support regime. For n=64, k=4 and d=1, 1,952 of the 2,016 possible pairs are needed, whereas after learning that exactly four voices are active, three probes suffice. For d=3 (one arbitrary bad edge, no erasures), every pair is required in the fixed design, whereas the six edges of K4 suffice when the support is known. If the support is all 64 voices, both designs reduce to 63 or 96 probes for d=1 or d=3 respectively. These are counts of pair probes, not runtime or hardware estimates.

Negative result: the simple edge-count lower bound by itself is not sufficient. Two disjoint cliques have high minimum degree but cut distance zero. Harary's connectivity construction, rather than merely a degree target, is needed for the general attainability proof. The unrestricted worst-case guarantee is about all supports; a known distribution of support patterns could justify another objective entirely.

## 4. The quiet voice sets the noise floor

Add independently bounded additive power-measurement noise of absolute magnitude eta>=0 on each non-erased, non-arbitrarily-corrupted pair probe. Magnitudes remain exact. Errors and erasures are the same as Theorem B. The two possible uncorrupted values for edge ij are (a_i+a_j)^2 and (a_i-a_j)^2. Their gap is 4 a_i a_j. Their closed eta-neighborhoods are disjoint iff 2a_i a_j>eta (strict inequality is essential: equality allows a midpoint).

Let G_eta be the graph retaining only active edges satisfying this strict inequality.

**Theorem C (robust analog criterion).** Uniform exact sign identification is possible iff lambda(G_eta)>2t+e.

Proof. On edges retained in G_eta the two possible intervals do not overlap, so an honest bounded-noise value identifies its sign. A received value in neither interval can be treated as an arbitrary error; a corrupted value in an interval may identify a wrong sign. Decode using Theorem B on these strong edges, ignoring all weak ones. Conversely choose a minimum cut in G_eta. Flip one side of that cut. On all weak crossing edges choose a shared value from the two intersecting honest intervals. On strong crossing edges erase up to e, then split the remaining at most 2t differences between the two worlds' corruption budgets. Use the honest common values or shared intervals elsewhere. This yields one transcript compatible with both worlds. No stochastic independence or average-case noise assumption is used.

With complete pair availability, sort the j positive amplitudes as a_(1)<=...<=a_(j). The graph G_eta is a product-threshold graph. If any vertex has a neighbor, all such vertices have a neighbor at the largest amplitude (except that largest vertex itself); if the smallest is isolated, lambda=0. Otherwise the largest is universal. The minimum degree is the smallest-amplitude vertex's degree: for any other vertex, all neighbors of the smallest except possibly that vertex remain neighbors, and if they are adjacent the smallest replaces the excluded one. A graph with a universal vertex has edge connectivity equal to minimum degree D. To see this, take the side of a cut not containing the universal vertex, of size b. If b>=D, its edges to the universal vertex suffice. If 1<=b<D, each vertex has at least D-b+1 crossing edges, giving b(D-b+1)>=D. The singleton cut at a minimum-degree vertex achieves D.

It follows that even allowing all pairs, the exact noise threshold for distance d is

    eta < 2 a_(1) a_(j-d+1).

For d=1 the most powerful pair of the quietest voice with the loudest one controls the limit. The star centered at the loudest voice is sufficient and costs j-1, simultaneously attaining the noiseless count and the complete-graph bounded-noise threshold. For d>1, the d-th loudest voice must also be sufficiently loud. These are worst-case absolute power errors, not dB values or acoustic hearing thresholds.

If a_(1) tends to zero with a finite maximum amplitude, the complete graph itself cannot give a uniform strictly positive noise guarantee for sign of every active coefficient. Exact support identification and stable sign identification are distinct. A reliable external reference of amplitude A changes the question: with a known sign and independent reference probes, the threshold is eta<2 A a_i for each active coordinate. This is a different allowed-measurement architecture and does not contradict the graph count.

## 5. A second cost of weak voices

Even when complete availability passes the analog test, a minimal noiseless pair budget may be too small.

Take r loud coordinates of amplitude 3 and w>=r weak coordinates of amplitude 1; set eta=3 and target d=r. Weak-weak edges have overlapping intervals; weak-loud and loud-loud edges are strong. Every weak vertex must have all r possible strong edges or its singleton cut fails distance r. Thus at least rw distinct probes are necessary. Exactly rw suffice: use the complete bipartite graph K_(r,w), with no loud-loud edges. Any cut containing loud vertices on both sides has at least one crossing edge for every weak vertex, hence at least w>=r. A cut with all loud vertices on one side crosses r edges for each weak vertex on the opposite side. A weak singleton cut has size r.

Consequently the sharp robust support-informed count for this family is rw, versus ceil((r+w)r/2) without bounded noise for r>=2. For r=3,w=21, the counts are 63 and 36; as w grows with fixed r>=2, the ratio approaches two. For d=1 the tree exception still applies. The result refuses the tempting policy "once support is known, just deploy the sparsest optimally connected graph." Its edges may be too weak to transport phase reliably.

The mathematical mechanism is not limited to a detector algorithm. A relation's useful observability depends on both endpoints. In a semantic analogue, the loss of a shared reference may disrupt relationships between individually recognized signs. This is only an analogy; humans are not scalar phase graphs, and inference or contextual knowledge can supply independent information.

## 6. A witness and an instrument

The native Python generator creates four original 16-bit mono 8 kHz PCM recordings. It serializes individual powers followed by pair powers, using a 250 Hz square wave in each 100 ms slot, with amplitude 1200 times the integer power. There is no per-file normalization. This is a sonification of the meter's data, **not** a recording of simultaneous physical oscillators or a perceptual comparison.

| Case | Observation values | Bytes | SHA-256 prefix |
|---|---|---:|---|
| chain A | 1,0,1,1,1 | 8044 | 250ced8e783a |
| chain B | 1,0,1,1,1 | 8044 | 250ced8e783a |
| bridge A | 1,0,1,1,1,4 | 9644 | ef7d724ee028 |
| bridge B | 1,0,1,1,1,0 | 9644 | 3ecaeab484e9 |

The chain pair was additionally compared byte-for-byte using cmp. The bridge pair differs. Full hashes are retained in witness.json. WAV binaries are reproducible disposable outputs, not committed source material.

**Design hypothesis — the Reference Organ.** Treat signs as 0 or pi phase offsets of coherently locked voices. Provide an independent amplitude control and a patch graph describing the power probes. Play the measured powers as a score, and display connected components of the currently strong graph. A performer can lower one voice through the reliability threshold without changing the underlying sign vector. The interface should expose the newly ambiguous component orientation as an unresolved state, not invent a sign. The performer may patch a new bridge, boost a reliable reference or deliberately listen to several admissible orientations. A second mode would audition actual coherent mixes to reveal the missing relation. The score and physical mix serve different purposes.

An engineering receipt could retain the active-set measurement, exact/approximate magnitude assumption, pair graph and gains, declared noise/error budgets, a cut witness for refusal, and the sign class rather than a fabricated absolute polarity. No design has been tested with humans. Real acoustic sources have continuous phases, propagation delays, differing frequencies, microphone errors and nonstationarity; the scalar model is an intentionally small falsifier of claims about connectivity and reference, not a complete auditory scene model.

**Fiction.** The organist had three pipes and a meter between every neighboring pair. When the middle pipe failed, the two remaining pipes kept their notes. The meter registered the absence correctly. The organist was surprised only when the same score allowed the last two pipes either to reinforce each other or to cancel. The repairman ran one new wire across the empty socket. Nothing about the missing pipe had changed; the question had changed.

## 7. Evidence and refusals

### Source ledger

- Boris Alexeev, Afonso S. Bandeira, Matthew Fickus and Dustin G. Mixon, *Phase Retrieval with Polarization*, SIAM Journal on Imaging Sciences 7(1), 35–66 (2014), DOI [10.1137/12089939X](https://doi.org/10.1137/12089939X). Publisher abstract and [arXiv:1210.7752v2](https://arxiv.org/abs/1210.7752) (12 September 2013) checked 24 November 2026. Selected full-text reading: [preprint PDF](https://arxiv.org/pdf/1210.7752), section 2, printed pp. 3–6, eqs. (2.3)–(2.6), graph propagation discussion and Procedure A. Printed p. 4 was also inspected as a rendered page. The paper explicitly recognizes zero-coefficient vertex deletion and a signal-dependent cost of adaptive observations; its full-spark construction avoids requiring every coefficient to remain connected. We do not assert that our graph count is novel relative to the literature or that its broader claims apply to our model.
- Frank Harary, *The Maximum Connectivity of a Graph*, PNAS 48(7), 1142–1146 (1962), DOI [10.1073/pnas.48.7.1142](https://doi.org/10.1073/pnas.48.7.1142), [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC220921/). Read printed pages 1142–1144 as original page images (PDF endpoint required browser verification); section 2, Theorem 1, construction cases on pp. 1143–1144; also the connectivity inequalities and Theorem 2. This is the established attainability theorem used in section 3. No full-paper reading claim or reproduced source scans.
- Internal sediment: [Frustrated Choir #191](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/191) concerns parity inconsistency and convention switching, and [Orchestra Behind the Veil #230](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/230) concerns labelled ownership of a fixed mixture. Their draft-branch README texts were inspected read-only. They supply context rather than empirical support or proof of acceptance. This expedition concerns the probe graph on an unknown nonzero coordinate support, not source ownership or the repair of an inconsistent constraint loop.

### Reproduction and computational evidence

Run from repository root:

    node research/expeditions/chord-loses-reference/laboratory.cjs
    python research/expeditions/chord-loses-reference/witness.py build/mhac-372

The JS core was actually executed in a JS runtime through a function wrapper. Native Node filesystem/CLI qualification was not performed. Its exact receipt is execution.json. All simple labelled graphs on 2–6 vertices were evaluated: 33,866 graphs, 1,895,138 support cases, 9,956,978 cut evaluations, 35 optimal fixed-budget profiles. Direct square-intensity computations on the smaller subset independently compare 1,650 nontrivial sign flips against the cut-distance formula. Harary constructions were checked for n=2..13, 78 graphs and 81,936 surviving vertex subsets, including the odd-order/odd-connectivity construction and tree exception. This is a finite verification, not a substitute for the proof.

The analog oracle checks 1,360 positive amplitude vectors (entries 1..4), 44,880 vector/noise-threshold instances, 572,880 cut evaluations, 395,472 explicit interval comparisons and 2,187 direct decoder/erasure-mask/error-budget cases on four vertices. It also checks the weak/loud bipartite construction in 22 cases. It does not enumerate arbitrary real-valued noise: the theorem reduces that uncertainty to disjointness of intervals. All assertions passed.

Native Python 3.13.5 independently enumerated all 74 graphs of size 2..4 and 738 graph/support combinations, explicitly grouping the literal squared observations of every sign class and comparing every fiber size with the component formula. Four PCM files were produced and byte comparisons performed. All assertions passed; the retained witness.json is the actual output. Both methods were implemented by one GPT-6.2 agent, not independent peer review.

### Checkpoint

- Scope: issue #372, additive directory only; default branch main, base 495a98ca12bae467a507031f04931aa4254b1866.
- Reconciled: AGENTS, RAG, programme, runbook, research integrity, validation, root and research README; 245 returned branch names (all pages), 100 recent open issue and 100 open PR search snapshots (bounded, not entire inventories), targeted phase/polarization searches, prior expedition sources read-only. Issue #372 read back with zero comments at creation. Previous expedition #365 exact-head Actions success checked. Main programme still in progress; no canonical changes or upstream acceptance assertions.
- Artifacts: this report, laboratory.cjs, execution.json, witness.py, witness.json; no frozen manifests or other branches changed.
- Review boundary: report is original mathematics with source ancestry and self-checks. Independent critique, full repository checks and landing verification are outstanding at the point of authorship. The issue remains open. No human data, outreach, third-party redistribution or license decisions. Do not treat the synthetic results as scientific or human validation.
- Important refusals: no claim about arbitrary complex phase, noisy support/magnitudes, unequal measurement costs, repeated probes, fully transcript-adaptive corruption strategies, general frame measurement optimality, or empirical auditory comprehension. Exact sign of an arbitrarily small coefficient is not a robust target under a fixed absolute power-error tolerance. The explicit two-stage count is not the minimum number of general phase-retrieval measurements.

