# The Choir That Mistakes Stillness for Agreement
## Exact alternating-partition stopping debt and the arithmetic of a vanished dissent

**Refs #276 · 24 November 2026 · exploratory formal mathematics, synthetic computation, interpretation, original sound art and fiction.** No Track E/G advancement, human findings, production consensus protocol, or theorem-priority claim.

### Excavation and scope

Two committees repeatedly replace every member's report by the mean of their current committee. The membership changes between two fixed partitions of the same roster. Each committee's operation is exact, preserves the overall mean, and produces perfect within-committee agreement. If the aggregate report hardly changes from one full round to the next, are the members nearly unanimous?

Not necessarily. A single shared bridge member can make a strongly divided roster technically connected but extremely slow to reach consensus. A more unexpected result appears when reports are binary: **the existence of one-pass, order-sensitive complete erasure of disagreement is equivalent to the roster size being composite**, under this particular two-binary-partition model. The arithmetic of the sample size can determine whether this particular failure mode even exists.

Reconciled live main at 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation and project foundations read. Recent open issues and PRs (61 returned open PRs) and two pages of branch listings (197 branch names returned) inspected; no existing alternating-partition expedition identified. Related [#220](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/220), [PR #221](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/221) actual report concerns one-shot calibration and pooling; [#240](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/240) actual draft report concerns stochastic state lumping and temporal laws. Both issues and their comments read; no mutation or dependency on their drafts. This expedition concerns dynamics of repeated report replacement, explicit geometric contraction, stopping certificates and binary order-sensitive erasure. It neither asserts that disagreement is always valuable nor that agreement is evidence of truth. No accepted registry or canonical manifest is touched.

### Model and exact dynamics — proof

Let N>=2 uniformly weighted individuals be classified by two nonconstant binary partitions A and B. The four membership counts, in row-major order, are (a,b,c,d). Rows describe A, columns describe B. Let P and Q respectively replace a real-valued report by its A-cell or B-cell mean. These are orthogonal projections on the finite real Hilbert space with inner product sum(x_i y_i)/N. They preserve the common mean mu. A full round T=QP first applies P then Q. Reports are overwritten; original observations do not recur. No new evidence, noise, quantization, rounding, changing roster or strategic behavior is modeled.

Let u and v be centered, unit-norm indicators of the nonconstant categories of A and B. Each centered projection has rank one: P x=u<u,x> and Q x=v<v,x> on the centered subspace. Their inner product rho is the signed binary correlation (up to choice of indicator orientation). Explicitly,

    rho = (ad-bc)/sqrt((a+b)(c+d)(a+c)(b+d)),
    r = rho^2.

For arbitrary centered x and integer k>=1,

    T^k x = rho^(2k-1) v <u,x>.

This follows by applying QP once, then using T v=r v. Consequently the worst-case norm contraction after k rounds, for arbitrary initial centered inputs, is |rho|^(2k-1), attained by x=u. Once a state is in the range of Q (as after every full round), its centered component is a multiple of v and contracts by exactly r per full round.

The row/column membership graph has four group vertices and an edge for each occupied cell. With nonempty margins it is connected iff at least three cells are occupied; two occupied cells with nonempty margins must describe the same binary partition up to relabeling. In the connected case |rho|<1 (equality in Cauchy–Schwarz would make the two binary indicators identical or complementary). Hence the unique limiting report is the global initial mean. In the disconnected case r=1, P=Q, and arbitrary nonzero between-group differences persist forever. The orthogonal case r=0, e.g. (1,1,1,1), reaches the global mean in a single round in either order. This is an elementary finite specialization of alternating projection theory, not a new general convergence theorem.

### Sharp bridge budget — proof

Relabel one partition if needed so ad-bc>=0. For a connected table a,d>0 and s=b+c>=1; set s as the off-diagonal mass in this orientation, not as an independent claim about physical network edges. In particular s<=N-2.

Using (a+b)(a+c)>=a(a+s), (d+b)(d+c)>=d(d+s), and (ad-bc)^2<=(ad)^2 gives

    r <= ad / ((a+s)(d+s)) = ad/(ad+sN).

For fixed N,s the last expression increases with ad. Since a+d=N-s, the largest integer product is h=floor((N-s)^2/4). Therefore

    r <= h/(h+sN).

This is sharp for every N>=3 and 1<=s<=N-2: take (a,b,c,d)=(floor((N-s)/2),s,0,ceil((N-s)/2)). The product is maximized and both preceding inequalities are equalities. All margins are positive, and three cells are occupied. The maximum decreases with s because h decreases and sN increases. In particular the sharp global connected bound is

    r_max(N) = floor((N-1)^2/4) / (floor((N-1)^2/4)+N).

A single overlap observation thus permits r approaching one as N grows, even though each averaging pass exposes only two group values. For odd N=2m+1, the maximizer is (m,1,0,m) and r=m^2/(m+1)^2. This bridge formula and its proof are original reconstruction in this report; no priority search adequate to establish novelty has been conducted.

### Stopping debt and observation cadence — proof and limits

After at least one full round, write E=||x-mu|| for the pre-round RMS deviation from global consensus and D=||Tx-x|| for the movement over the next full round. Since the centered part of x is in the range of Q,

    D=(1-r)E,    E_after=r E.

The exact multiplier converting movement to *pre-round* error is 1/(1-r), and the multiplier for post-round error is r/(1-r). For all connected N-member rosters, the sharp uniform pre-round multiplier is

    1 + floor((N-1)^2/4)/N.

A rule demanding D<=epsilon does not imply E_after<=epsilon. A sufficient uniform stopping condition for a requested pre-round error tolerance tau is D<=(1-r_max)tau. If the actual membership counts are known, use the actual r. This is an algebraic error certificate, not a probabilistic uncertainty interval. If the graph is disconnected, no finite multiplier can bound global disagreement by motion; D can be exactly zero with E>0. Under connectedness and exact arithmetic, D=0 *does* prove consensus after a full round, so the stronger claim that stillness always misleads is false.

With N=101 and (50,1,0,50), r=2500/2601. A full round retains 96.117% of the pre-round deviation and moves only 3.883%. The pre-round amplification factor is 2601/101≈25.7525. With N=1001 and (500,1,0,500), r=250000/251001; the multiplier is 251001/1001≈250.75025. It is possible to make apparent movement arbitrarily small relative to actual remaining disagreement by increasing the roster.

A different observation cadence produces a different apparent activity signal. For x in the range of Q, the orthogonal-projection identity gives

    ||Px-x||^2=(1-r)E^2.

The intermediate half-step changes by sqrt(1-r)E, whereas the full-round net movement is (1-r)E. The second half-step cancels part of the first. For 101 members, the first movement is about 19.7% of E but the full round only 3.883%. A report on whether the system is 'quiet' therefore needs an explicit sampling cadence. This does not make the whole-round certificate incorrect; it makes unnormalized comparisons across cadences misleading. The first arbitrary round is excluded from the exact end-of-round stopping identity.

### An arithmetic anomaly — one-pass order erasure

Noncommuting projections have an additional asymmetry. For 0<r<1, choose centered x=(I-P)v. Then P x=0, hence QP x=0; Q x=(1-r)v and PQ x=(1-r)rho u!=0. The forward order erases disagreement immediately, whereas reversing the order preserves a nonzero distinction. Thus slow worst-case convergence does not imply that every input converges slowly.

Can this happen if every initial report is restricted to 0 or 1? The exhaustive small-roster census exposed an intriguing pattern: 4,6,8 permit it; 2,3,5,7 do not. The pattern is not a parity law. It is a compositeness law.

**Theorem.** For N>=2, there exist two nonconstant binary partitions and a binary report vector for which QP gives a constant vector but PQ gives a nonconstant vector iff N is composite.

Proof of necessity. When rho=0 both orders give a constant; when |rho|=1 both projections coincide. Otherwise QP x constant iff the two original row means coincide (the Q projection cannot annihilate a nonzero centered row contrast). If row sizes are R0,R1 and the respective positive counts are k0,k1, equality means k0 R1=k1 R0. If N is prime, gcd(R0,R1)=1, since their sum is N and both are positive and smaller than N. Then R0 divides k0, so k0 is zero or R0; equality forces every initial report to be the same. Reversal cannot preserve a nonconstant vector.

Proof of sufficiency. Write N=pq with p,q>=2. Choose table (0,p,1,N-p-1). All margins are nonempty, support has three cells, and determinant -p is nonzero. Put exactly one 1 in the first row and exactly q-1 ones in the second row, including the singleton first column. Both row means equal 1/p, so QP outputs that constant. Column 0 has mean 1 and column 1 has mean (q-1)/(N-1)<1; because rho!=0, PQ is nonconstant. Thus every composite N has a witness. No inference about prime-sized real groups, real-valued or multilevel reports, more than two partitions, or strategic voting follows.

Smallest binary witness, N=4: table (0,2,1,1), with roster in row-major cell order and initial reports (1,0,1,0). Forward QP yields (1/2,1/2,1/2,1/2), while reverse PQ yields (1/3,1/3,2/3,2/3). Both preserve the overall mean. The order changes what remains observable, without changing the evidence that was initially supplied. A prime-sized roster can still have slow convergence or order-dependent output on other inputs; it only rules out this specific exact one-direction binary annihilation.

**Exact counting extension.** For a fixed table with nonzero determinant, write R0=a+b, R1=c+d, C0=a+c and g=gcd(R0,R1). Row-balanced binary inputs have common row fraction k/g, 0<=k<=g. Put U=k R0/g, V=k R1/g, W=k C0/g. Count row-balanced inputs by summing binom(R0,U)binom(R1,V) over k. Subtract those also column-balanced: for each integral W, sum over i=0..a the product

    binom(a,i) binom(b,U-i) binom(c,W-i) binom(d,V-W+i).

Use zero for out-of-range binomial arguments. The four factors select the ones in each cell; row and column sums uniquely specify the other three cell counts given i. This subtraction is exactly the number of binary vectors erased by QP but not PQ, by the rank-one criterion above. If the determinant is zero, both orders always give the constant and the count is zero instead. For disconnected tables the subtraction is zero because the partitions coincide up to relabeling. The count retains labelled members within each fixed table, but does not multiply by the number of ways to assign a given table to a different labelled roster.

### Executed experiments and reproducibility

Three implementations were actually run in the V8 environment, then serialized as source and committed. The core was subsequently fetched and re-executed after adding the intermediate-step and order-erasure assertions; its numerical receipt matched byte-for-byte in JSON representation. The expanded-roster BigInt implementation and the binomial counting implementation were executed separately and compared on every population size 2–8. These are separate implementations by one AI agent, not independent scholarly review.

| Experiment | Exact scope/result |
|---|---:|
| All nonnegative integer 2x2 tables, N=2–60 | 635,371 |
| Nonconstant row and column margins | 628,055 |
| Connected tables tested against global and bridge-specific bounds | 624,515 |
| Disconnected controls | 3,540 |
| Orthogonal connected controls | 2,395 |
| Exact global-bound-attaining tables (ordered cell counts) | 348 |
| Full cell-basis, half-step and order checks, N<=30 | 44,515 tables |
| Expanded-roster binary vectors, N<=8 | 51,192 across 350 tables |
| One-direction erasure vectors in expanded census | 2,420 |
| Exact binomial counts, N<=30 | 44,515 tables, 17,050 with positive count |
| Explicit composite witnesses through N=200 | 153 |

No assertion failure in completed runs; four malformed/constant-partition test cases rejected. The core uses exact integer Number operations over the bounded census, and the expanded-roster and binomial checks use BigInt. The exact count is not the number of empirically observed failures or a representative sampling distribution. Larger input sizes are outside the census qualification. The table-basis proof check uses scaled integer group means, not the correlation formula to generate the trajectory. The expanded census includes all binary micro-inputs for each ordered table (one canonical labelled roster per table), including variability inside cells.

| N | Valid tables | Tables admitting erasure | Binary vectors erased forward only (sum over tables) |
|---:|---:|---:|---:|
| 4 | 19 | 4 | 16 |
| 5 | 36 | 0 | 0 |
| 6 | 60 | 30 | 344 |
| 7 | 92 | 0 | 0 |
| 8 | 133 | 50 | 2,060 |
| 9 | 184 | 44 | 3,544 |
| 10 | 246 | 132 | 16,584 |
| 11 | 320 | 0 | 0 |
| 12 | 407 | 240 | 121,032 |
| 30 | 5,336 | 3,746 | 213,298,843,760 |

Run from this directory: `node verify.mjs` (Node 20+ suggested); optionally `node verify.mjs --audio-dir ./generated-audio` creates fresh WAVs, refusing to overwrite an existing WAV. See [core](laboratory.mjs), [core receipt](execution.json), [expanded cross-check](microcheck.mjs), [expanded receipt](micro-execution.json), [counting extension](arithmetic.mjs), and [counting receipt](arithmetic-execution.json). The actual Node filesystem wrapper and full repository test suite are not yet locally qualified: direct Git checkout was attempted but DNS resolution for github.com failed in the local container. Connector access worked. Repository exact-head CI is a separate gate. No validation claim for arbitrary library inputs, floating-point or asynchronous implementations.

### Original audio — The Stillness Organ

The synthetic stereo score has 32 rounds at 8 kHz, 400 frames per round. Each channel uses the same 400 Hz integer triangle waveform, with fades. Left amplitude is proportional to normalized movement (1-r)r^k; right amplitude is proportional to residual disagreement r^(k+1). Integer amplitude truncation is only a rendering choice, not part of the proof. Four 51,244-byte WAV arrays were generated in memory and compared; FNV-1a fingerprints are reproducibility aids, not cryptographic evidence.

| Case | Left: movement | Right: residual | FNV-1a |
|---|---|---|---|
| Orthogonal | Single pulse | Silent | 6ee8f077 |
| One bridge, N=101 | Small decaying pulses | Larger decaying pulses | 105103b3 |
| Disconnected | Silent | Sustained pulsed tone | 47f63d6d |
| Already constant | Silent | Silent | dc908c6d |

The disconnected and already-constant left channels are identically zero sample-by-sample, while their right channels differ. This is an exact acoustic alias at the sample level, not evidence that listeners will infer the intended semantics. In the orthogonal case the right channel is silent after the first round; the left correctly reports a substantial final move. The full waveform is original, generated from the declared equations; no recordings or third-party samples are used.

**Speculative instrument.** A two-layer sequencer could let performers place notes into intersecting rehearsal groups, with the grouping rather than pitch or tempo acting as the principal modulation control. A motion-only voice can appear to settle while a residual voice exposes remaining separation. Another control could swap the order of the two group-averaging operations: a binary input score would occasionally lose its entire nonconstant component in one order but retain it in the other. A composer could deliberately vary a roster's divisibility as an abstract constraint on this score grammar. This is art and a design conjecture, not a claim that prime-numbered ensembles behave differently in human music.

### Interpretation, contrary cases and practical transfer

In a distributed computation, stable output, equality of current reports and agreement with the original evidence are three different predicates. The present model has deliberately thrown away original reports after each averaging stage; consensus cannot restore them. The arithmetic mean is the consensus because the model preserves that mean, not because the mean is epistemically privileged. It could be wrong for all members. Conversely an average may be precisely the required output, and rapid loss of detail is then beneficial.

A provisional *consensus receipt* should preserve the roster, grouping schedule, fixed or changing inputs, source-data identity, exact update rule, observation cadence, connectivity certificate, contraction rate or verified error bound, and target of convergence. Distinguish current disagreement from movement and both from ground-truth accuracy. For an actual agent network with nonlinear updates, irregular weights, asynchronous messages, retained observations, stochastic or strategic behaviour, this proof does not apply without separate justification. A robust real stopping rule would need independently derived assumptions and performance evidence, not merely the visual impression that a dashboard stopped changing.

For a communication analogy, the two groupings are different ways to partition a vocabulary or a population; successive re-descriptions can suppress distinctions without adding facts. This is an interpretation, not a theory that human linguistic conventions are conditional averages or that deliberation literally follows this linear algorithm. A falsification condition for any proposed interface benefit is that a movement-plus-residual cue fails to improve discrimination of stable-but-divided versus genuinely converged states under the relevant task, training and accessibility conditions. No human testing has taken place.

### Source custody

Consulted 24 November 2026 by one ChatGPT agent via public web retrieval:

- C. Badea, S. Grivaux, V. Muller, *The rate of convergence in the method of alternating projections*, [arXiv:1006.2047](https://arxiv.org/abs/1006.2047), preprint dated 10 June 2010. Body-level reading of Introduction §§1A–1B: von Neumann's two-projection limit, Friedrichs angle, geometric rate and attribution to Aronszajn/Kayalar–Weinert. §§1C–1E also inspected for the boundary between two and more than two projections. Not a full-paper reading. The elementary rank-one proof here independently establishes the finite result and does not generalize it to more than two partitions.
- S. Kayalar and H. L. Weinert, *Error bounds for the method of alternating projections*, Math. Control Signals Systems 1, 43–59 (1988), [DOI 10.1007/BF02551235](https://doi.org/10.1007/BF02551235). Publisher DOI access failed; visible author/article search extraction at [public listing](https://www.academia.edu/62612942/Error_bounds_for_the_method_of_alternating_projections) included abstract, opening and Example 2. The two-space exact norm formula is established antecedent, also attributed in Badea et al. §1B. No claim to have inspected the entire paper or its original theorem page.
- M. H. DeGroot, *Reaching a Consensus*, JASA 69(345), 118–121 (1974), [DOI 10.1080/01621459.1974.10480137](https://doi.org/10.1080/01621459.1974.10480137). Publisher search result abstract inspected; direct publisher page access returned 403. The abstract describes pooling individual opinions to reach a common distribution or point estimate. Contextual analogy only, not an assertion that our specific matrices reproduce every DeGroot result.
- D. J. Evans and C. Li, *New Stopping Criteria for Some Iterative Methods for a Class of Unsymmetric Linear Systems* (1991), [DOI 10.1137/0612040](https://doi.org/10.1137/0612040). Publisher search result abstract explicitly distinguishes small iteration pseudoresidual from small error. Bounded abstract-level contrary precedent; its theorem uses a different matrix class and is not applied here.
- A. Olshevsky and J. N. Tsitsiklis, *Convergence Speed in Distributed Consensus and Averaging*, SIAM Review 53(4), 747–772 (2011), [DOI 10.1137/110837462](https://doi.org/10.1137/110837462). Publisher search result abstract inspected for established study of convergence-time limits and fixed/time-varying topologies. No detailed theorem transfer from unread body.

These sources delimit existing ideas; the bridge optimization, stopping multiplier, divisibility theorem and counting formula are justified by the proofs above, not by invented source attribution. Priority is unestablished. Source snippets are not canonical MHAC evidence. No third-party full text is redistributed; no license or external authorization has been selected.

### Afterword — fiction

The conductor had divided the choir by range on Mondays and by rehearsal room on Tuesdays. Each division replaced every voice with the mean pitch of its group. The hall grew quieter at the end of each week, so the conductor announced that disagreement had almost disappeared.

An apprentice recorded the difference between the beginning and end of the week on one wire, and the difference between the voices on another. The first wire eventually carried a note so faint it seemed polite not to mention it. The second wire carried a long, unresolved chord.

The conductor pointed at the first meter. The apprentice pointed at the second.

There was agreement about the needle. There was not agreement about the choir.

### Disposition

AI-assisted synthetic exploration; original proofs, source-bounded contextual interpretation, executable bounded checks and score generator. No external reviewers, participants, production policy or core research acceptance. Independent critique, clean-checkout wrapper execution and exact-head CI remain required before landing. All files are additive within this expedition. Do not merge another worker's branch or amend shared indexes as part of this scope.
