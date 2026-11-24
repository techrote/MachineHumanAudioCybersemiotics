# The Choir That Cannot Choose Its Extremes

**Expedition #420 | 24 November 2026 | Original mathematics, synthetic experiment, compositional study.** Not an accepted Track E/G result, participant experiment, deployed alarm protocol or novelty-priority claim.

## Question and anomaly

Six voices each sound half the time. Every pair, even every triple, occupies each of its possible on/off patterns equally often. Does a full chorus therefore occur with probability 1/64? No. A law can assign probability 1/12 to the full chorus and 1/12 to complete silence, even after triple-wise independence is established. A different law can place probability 1/20 on the full chorus and zero on complete silence, with precisely the same individual, pair and triple marginals. The first law has more extreme events, but those events have no directional evidence when compared with its complement. The second has fewer extreme events but the extreme event identifies which of two complementary laws generated it.

The research target is not the already-known inadequacy of pairwise independence. It is the exact **joint feasible region** of two opposite extremes, and the distinction between a bound on total concurrence and the directional information of a concurrence.

## Model and reduction

Let X_i be fair binary voices, n >= 2, and k-wise independence mean every labelled subset of at most k voices is uniformly distributed. Let S=sum X_i and Y=2S-n; Y lies on the integer grid -n,-n+2,...,n. Let a=P(Y=-n), b=P(Y=n), q=a+b, d=b-a. Thus q is the probability of either unanimity, and d is its polarity imbalance. Always q>=|d|.

Permutation averaging does not change (a,b) or any symmetric objective, and preserves k-wise independence. Conversely, a law for S with the first k moments of Bin(n,1/2) lifts to a k-wise independent labelled law: conditional on S=s, choose a uniformly random s-element subset. The probability that a specified j-subset is all on is E[binom(S,j)]/binom(n,j)=2^-j. Inclusion-exclusion yields the other patterns. Consequently pairwise independence is equivalent for the purposes of these projections to E Y=0, E Y²=n, and triple-wise adds E Y³=0. The reduction is established prior art (source ledger below), not a new theorem.

## Exact pairwise endpoint region

Put C=1/(n+(n mod 2)). For n>=4:

- **Even n:** q>=|d| and n q+2|d|<=1.
- **Odd n:** q>=|d| and q<=C.

These inequalities completely characterize attainability, not just upper bounds. For n=2 the unique pair is q=1/2,d=0. For n=3, q=1/4 and |d|<=1/4.

Proof. Write m=n mod 2. From Y²>=m², n=E Y²>=n²q+m²(1-q), giving q<=C. For even n the interior grid obeys Y²>=2|Y|. Its first moment is -nd and its second n-n²q. Thus n-n²q>=2n|d|. For odd n no stronger inequality is required. For n=3 the interior is just ±1, giving q=1/4; for n=2 the interior is 0.

Attainment: for n>=4, the origin q=d=0 is feasible because a symmetric interior law can mix squared magnitudes m² and (n-2)² to attain n. The balanced apex (C,0) places equal mass C/2 at each endpoint and remaining mass symmetrically on magnitude m. For even n the one-sided corner q=d=1/(n+2) uses mass q at Y=n, n/(2(n+2)) at Y=-2, and 1/2 at Y=0. For odd n the corner q=d=C uses mass C at Y=n and 1-C at Y=-1. Reflection obtains the opposite corners. Convex mixing fills the polygons (for odd n the balanced apex is the midpoint of the two top corners). For n=3 the same odd one-sided construction and its reflection fill the segment. These explicit distributions also prove the known one-endpoint maxima.

## Exact triple-wise endpoint region

For n>=4, with C as above, define
\[
 \alpha_n = \begin{cases}
 n(n-4)/(n^2-2n+4), & n\text{ even},\\
 (n-2)/n, & n\text{ odd}.
 \end{cases}
\]
The sharp region is
\[
 0\le q\le C,\quad |d|\le\min\{q,\alpha_n(C-q)\}.
\]
For n=3, triple-wise independence is full independence, giving q=1/4,d=0. The formula covers n=4, where alpha=0: **all triple-wise independent fair four-voice laws have equal silence and tutti probabilities**, but their total extreme rate varies from 0 to 1/4.

Necessity, odd n. On the interior |Y|<=N=n-2, Y²>=1. Hence
\[
 n(n^2-1)|d|=|E_{\rm int}[Y(Y^2-1)]|
 \le N E_{\rm int}[Y^2-1]
 =N[(n-1)-(n^2-1)q].
\]
The equality on the left follows by subtracting the endpoint contributions from zero odd moments; E_int is an unnormalized expectation restricted to interior. Divide by n(n²-1).

Necessity, even n. By complement symmetry take d>=0. On the even interior grid the cubic Y(Y+N)(Y-2) is nonnegative: its roots are -N,0,2, and there is no grid point strictly between 0 and 2. Its restricted expectation gives
\[
 -n^3d+(N-2)(n-n^2q)+2Nnd\ge0.
\]
Rearrangement gives the stated bound. At n=4 this forces d=0.

Sufficiency. The origin and balanced apex constructions are symmetric, so automatically obey the third moment. For n=4 their segment is all that is needed. For n>=5 the two remaining corners are one-sided, q=d=c and its reflection, where
\[
 c=\frac{\alpha C}{1+\alpha}
 =\begin{cases}
 (n-4)/(2(n-1)(n-2)), & n\text{ even},\\
 (n-2)/(2(n-1)(n+1)), & n\text{ odd}.
 \end{cases}
\]

For even n>=6 put mass c at Y=n, t=(n+2)c/(n-4) at -N, u=2(n-1)c/(n-4) at +2, and 1-c-t-u at 0. These solve all three moments (the cubic is zero on the interior support). Nonnegativity of remaining mass follows from t+u+c=(4n-4)/(2(n-1)(n-2))<=1. For odd n>=5 put mass c at n, t=n(n+1)c/((n-2)(n-3)) at -N, with remaining mass 1-c-t divided across ±1 to give signed difference +Nt-nc. This difference is nonnegative; it is <= remaining mass because, after substitution, the inequality reduces to 2(n-1)(n-5)>=0. The cubic and first moment then vanish by construction and the second moment equals n. Explicit reflection and convex combinations fill all vertices and edges. Thus the projected regions are exact for all n, not a census extrapolation.

Consequence: the maximal q remains C after triple-wise qualification, although the extremal directional allocation shrinks. The maximal b alone becomes C/2, attained at the balanced apex. The established odd-k recursion for the single-endpoint problem (Peled et al., eq. 1.1, crediting BGP) agrees with this one-dimensional projection. Our two-endpoint region retains information discarded by that scalar maximum.

## The cost of reliable unanimity as evidence

Choose one of two laws with equal prior probability, P and its bitwise complement. Both obey the same k-wise fair marginals. For a decoder restricted to unanimity, abstain on every non-unanimous observation. Its coverage is q and its optimal conditional accuracy, for q>0, is (1+|d|/q)/2. Indeed each endpoint occurs with pooled probability q/2, and the corresponding posterior is b/q or a/q. This does not say that the non-unanimous observations are uninformative.

For desired conditional accuracy at least (1+r)/2, 0<=r<=1, and n>=4, the exact largest coverage is:

| Model | Coverage maximum |
|---|---|
| Pairwise, even n | 1/(n+2r) |
| Pairwise, odd n | C |
| Triple-wise, alpha>0 | alpha C/(alpha+r) |
| Triple-wise, alpha=0 | C when r=0; no positive coverage when r>0 |

Proof: set |d|=rq, optimize q in the polygons; if coverage is positive, every boundary is attained. The small-n cases follow from the explicit segment/point above. In particular, a perfect (zero false assertion) unanimity-only classifier has maximum coverage c. At n=6 this falls from 1/8 to 1/20; at n=7 from 1/8 to 5/96. For n tending to infinity the third-order condition roughly halves the best perfect-witness rate. By contrast, the rate of either extreme can still reach about 1/n. Under mutually independent fair voices, q=2^(1-n), d=0.

This is a semiotic interpretation of an exact statistical experiment: a sign's *frequency* and its *evidential orientation* are distinct quantities. It is not a privacy guarantee, universal decoding rule, or human-perception claim. Related #218 considers joint disclosure with fixed marginals and parity; #195 considers missing joint witnesses and all proper marginals; #400 addresses deterministic periodic scheduling. Here the distinctive objective is the joint opposite-tail frontier and its operational conditional-evidence tradeoff, under equal fair marginals.

## A general odd-order no-improvement theorem and sharp two-sided tails

For any complement-invariant real function f on the entire labelled bit cube (not just symmetric f), the attainable expectation range under 2r-wise fair independence equals the range under (2r+1)-wise fair independence, provided 2r+1<=n. Proof: average any feasible law with its complement. Every even centered sign product through order 2r remains zero, and every odd one vanishes by cancellation (including the new order). The centered-sign monomials characterize independence on each labelled subset by Walsh expansion. The expectation of f is preserved. The reverse inclusion is automatic. The statement also holds simultaneously for any collection of complement-even observables. It is about the feasible image, not the usefulness of a particular extra measurement conditional on other observed data.

Special case: take f=1{|Y|>=h}, where h>0 is an attainable magnitude, m=n mod 2. The exact upper bound under pairwise OR triple-wise independence is 1 if h²<=n, otherwise (n-m²)/(h²-m²). The exact lower bound is 1 if h=m, otherwise max(0,(n-(h-2)²)/(n²-(h-2)²)). Proof: let Z=Y²; E Z=n. On the event Z>=h² and elsewhere Z>=m²; for the lower bound use Z<=n² on the event and Z<=(h-2)² off the event. Each nontrivial bound is attained by mixing the two corresponding shells, with symmetric signs; for a clipped 0 or 1 mix two shells entirely on the appropriate side to attain the mean. Uniform subset lifting gives actual labelled triple-wise independent witnesses. h=m is the whole support. These bounds include the q maximum at h=n, and show that every symmetric overload statistic of this particular kind can retain exactly the same worst-case risk despite all triple checks passing.

## Executable qualification and original score

Run Node on laboratory.cjs for exact BigInt rational enumeration of the count-law moment polytope. A feasible vertex needs at most k+1 positive weights: otherwise a null vector of the moment matrix permits two-sided perturbation. For each k+1 distinct nodes, the unique solution is the expectation of the Lagrange basis polynomials under the known moments; degenerate supports are included by zero weights. The census checks every feasible vertex against inequalities, every actual claimed corner for attainability, and the exact lower/upper symmetric-tail optima. Odd pairwise balanced apex is a convex midpoint, not required as an enumerated vertex. No extrapolation substitutes for proof.

Actual JS core execution: 57 n/order profiles (n=2..30, k=2..3 with k<=n), 237,336 candidate supports, 25,654 feasible support instances (duplicates possible), 96,720 moment equations, 207 corner attainment checks, 477 tail profiles; zero failed assertions. Native Node CLI was not run. See execution.json.

A second calculation in witness.py uses SciPy HiGHS on the full labelled cube, with one constraint for every all-on subset of size <=k. It checks 24 nonzero objective directions per n/order profile (n=2..8), comparing the entire endpoint support function to the analytic corners. 312 numerical LPs; maximum absolute discrepancy 3.279765348196406e-12. Python 3.13.5, SciPy 1.17.0, executed twice, byte-identical JSON receipt. Independent computational methods, same AI agent, not independent review.

The six-voice score is an exact multiset, not a Monte Carlo sample. Every 120-frame composition has 60 active frames per voice and all four patterns 30 times per pair. The three triple-qualified scores additionally have every one of eight patterns 15 times per labelled triple (768 literal marginal cells checked across four scores). Seeded frame shuffling supplies a reproducible arrangement; it does not claim temporal independence. The complementary pair uses the same frame order, with bits inverted.

| Score | Silent frames | Full chorus | Other active-voice counts | Qualification |
|---|---:|---:|---|---|
| pairwise-tutti | 0 | 15 | 45 at 2; 60 at 3 | Pairwise |
| triple-tutti | 0 | 6 | 24 at 1; 60 at 3; 30 at 4 | Triple-wise |
| triple-silence | 6 | 0 | 30 at 2; 60 at 3; 24 at 5 | Triple-wise |
| triple-balanced | 10 | 10 | 100 at 3 | Triple-wise |

Run python witness.py (NumPy/SciPy required) to regenerate four original 9.6-second 8 kHz PCM16 mono WAVs and witness.json (redirect stdout). Six distinct tapered sinusoids, fixed per-voice gain, no normalization by frame count. These are synthetic artistic examples of exact score-level marginals, not measurements of acoustic perceptibility. SHA-256 values in witness.json; WAVs are generated rather than committed. Do not present as clinical alarm stimuli. Audio playback to participants, acoustic calibration, and listening tests were not performed.

## Evidence ledger and limits

- Ron Peled, Ariel Yadin, Amir Yehudayoff, *The Maximal Probability that k-wise Independent Bits are All 1*, Random Structures & Algorithms 38(4), 502–525 (2011), [DOI](https://doi.org/10.1002/rsa.20329), [arXiv v3](https://arxiv.org/abs/0801.0059v3). Agent read PDF introduction pp. 2–4 (printed; indices 1–3) and §2 pp. 8–9 (indices 7–8), with images inspected for pp. 2, 8, 9. §2 eqs. 2.1–2.5 and Lemma 2.1 directly establish the exchangeable reduction and polynomial LP dual. Eq. 1.1 states the known odd-order single-endpoint recursion; no claim to have read all its proof. The present proof uses two-endpoint projection, not a new moment reduction.
- Arjun Kodagehalli Ramachandra and Karthik Natarajan, *Tight Probability Bounds with Pairwise Independence*, SIAM J. Discrete Math. 37(2), 516–555 (2023), [DOI](https://doi.org/10.1137/21M1408294), [preprint PDF](https://arxiv.org/pdf/2006.00516). Agent read preprint §4.1 Theorem 4.1 and proof setup/first reduction, printed pp. 27–29 (PDF indices 26–28, image inspected index 26). Their sharp one-sided tail problem and binomial-moment reduction establish substantial overlap. We do not claim novelty for its single-endpoint special cases. Journal full text not read separately.
- Philippe Lacherez, Eunice Limin Seah, Penelope Sanderson, *Overlapping Melodic Alarms Are Almost Indiscriminable*, Human Factors 49(4), 637–645 (2007), [DOI](https://doi.org/10.1518/001872007X215719). Publisher abstract only (Objective/Method/Results/Conclusion; full article restricted). Authors report difficulty identifying overlapping melodic alarms in their nursing sample. This is a motivation and a contrary constraint on any polyphonic interpretation, not validation of this model or a screened Track E extraction.
- Daniel Berend et al., *Exact Expressions for the Maximal Probability that all k-wise Independent Bits are 1*, J. Theor. Probab. 39 article 58 (2026), [DOI](https://doi.org/10.1007/s10959-026-01487-4). Discovery-level publisher metadata/abstract fragment only; full open attempt failed. Further novelty audit should inspect it before asserting priority.

Other limitations: fair marginals are essential to complement averaging; unequal rates require a different moment system. Conditional independence given a fault cannot be inferred from unconditional pairwise independence. Real alarm occurrence may be nonstationary, semantically coupled, subject to common cause, or deliberately serialized. A third-order test on labelled events is not equivalent to a third-order acoustic feature. The proven bound is on probabilities under a stipulated law, not on the peak amplitude of a mixed waveform or human recognition. For actual machine design, candidate hypothesis only: a qualification record should retain both a joint concurrency-risk bound and the evidence polarity of a purported unanimous report, with a reliable clock/frame reference for interpreting silence. Test via synthetic replay first, then separate authorized human study. Reject any inference of causal independence or corroboration solely from marginal frequency matching. No general optimum for fourth-order asymmetric endpoint polygons is claimed.

## Compositional study and fiction

The instrument has six voices and a ledger which can be inspected through any one, two or three channels. A composer controls the two extreme probabilities within the proved polygon, not the volume. At the balanced apex there are more extraordinary moments but none can name a particular complementary world. At the one-sided corner the whole choir becomes a rare, decisive accent. The number of ordinary pair/triple coincidences never moves. This is a design sketch for a statistical composition instrument, not implemented interactive software.

*Fiction.* The clerk asked each singer how often they had sung; each answered half the time. Then the clerk interrogated pairs, and then triples. Every ledger was complete. The conductor changed the distribution of the pauses without changing a single answer. When the entire hall sounded at once, the clerk finally heard a distinction that had no place in his ledger. In a later arrangement the whole hall sounded even more often, but the conductor told him it no longer named anything. He drew two columns: how often the hall had agreed, and what that agreement could establish.

## Repository and acceptance checkpoint

Base 495a98ca12bae467a507031f04931aa4254b1866, branch mhac-420/choir-extremes. Reconciled AGENTS, README, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY, VALIDATION, PROJECT_FOUNDATIONS, EXPERIMENTS; no nested AGENTS found in research or research/expeditions. Inspected 100 recent open issue results, 100 recent open PR results, 269 branches; targeted duplicate searches and related issues #195, #218, #236, #240, #400. Prior expedition #413 exact head 896b6273b5d3b22a8672acac79ac12492668e02a: Actions result success (run 45504279017). New issue #420 read; no comments at intake. All additions scoped here. No canonical records, manifests, or other branches changed.

AI-authored, self-reviewed; no separate human or independent reviewer. Exact core and native witness qualification completed; witness source and receipt blobs matched the locally executed bytes. Native full repository checkout was attempted and failed DNS resolution of github.com, so full local validation and exact-head CI remain to be established. Draft for integration and substantive critique, using Refs #420. Do not merge on an empty check list; integrator owns shared acceptance. No human gate satisfied or required for this isolated synthetic work, except any actual repository review requirements. No priority or broader programme completion claim.
