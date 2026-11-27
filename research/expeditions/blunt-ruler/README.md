# The Clock That Survives a Blunt Ruler

Refs #796, #792/#793. Exploratory mathematics and synthetic signal processing, 27 November 2026. One ChatGPT agent; no independent review, human data, physical-channel qualification or scientific-priority claim. Outside frozen Track E/G; no canonical evidence records changed.

## Observation contract

The equality-clock expedition established that deliberately repeated signal levels can improve exact synchronization under an arbitrary strictly monotone calibration. But a real quantizer can manufacture equality between distinct transmitted symbols. How much of the advantage survives?

Let the transmitter have a known ordered grid of q levels, indexed 0,...,q-1, including levels that are not used in a particular pilot. Let F be unknown, fixed over a window, nondecreasing or nonincreasing. Its maximal constant intervals on the complete grid may contain at most B levels, 1<=B<=q. Distinct plateaus may have any strictly ordered real outputs. In particular, F need not use a known output alphabet, gain, zero point, or threshold placement. Two alternative explanations may have different F. We do not assume independent quantization at each tick. B is a stipulated bound on the effective composite input-to-output map, not an ADC specification inferred from bit depth.

A pilot x of length N+K-1 yields candidate phase words x_s(t)=x_(t+s), t=0,...,N-1, s=0,...,K-1 (K>=2). Allow up to e arbitrary replacements and f flagged missing observations; original indices remain known. There is no dense noise in the exact decoder. Unknown deletions, time-varying gain, arbitrary pre-quantizer compression and receiver clipping beyond B are different contracts.

## Exact minimax alphabet reduction (proof)

For two words define L_B(a,b) to be the maximum cardinality of an indexed subset on which two legal channel maps can produce identical outputs. For a pilot define L_B(x)=max over distinct phase pairs. Its exact minimum inter-phase Hamming distance is N-L_B(x). For given N,K let L*(q,B) be the minimum over all q-grid pilots; lower is better.

**Theorem.** Put m=ceil(q/B). Then L*(q,B)=L*(m,1).

Upper bound on attainable distance / lower bound on L*: for ANY q-grid pilot, apply the permitted map c(i)=floor(i/B). It has m contiguous plateaus of lengths at most B. Subsequent arbitrary strictly monotone relabelings of these m outputs are still legal B-bounded channel maps. Thus every common subset under strict monotone calibration of the coarsened pilot c(x) is also a common subset of the original pilot under legal plateau-limited calibration. L_B(x)>=L_1(c(x))>=L*(m,1).

Achievability: take any m-level strict-model pilot z and transmit x=B*z. The maximum grid index B*(m-1) is at most q-1. Two distinct occupied levels differ by at least B, so they cannot lie in one interval of at most B grid levels. Every legal map therefore preserves their strict ordering up to global reversal, and preserves equality. Conversely every strictly monotone assignment on the occupied levels extends to a strictly monotone assignment on the finite complete grid by interpolation and extrapolation. Hence L_B(B*z)=L_1(z). Choose a minimizer z (finite alphabet, finite pilot length). This gives the reverse inequality.

This proves exact equivalence, not an approximation, for every N and K and all legal q,B. The same argument works for an arbitrary finite codebook of indexed words, not only shifted windows. B=1 recovers the predecessor; B=q permits complete collapse and L*=N.

Interpretation: the number of robust ordered symbols is m, not q. Empty guard levels have operational value, and simply transmitting a larger number of closely spaced distinct values cannot beat a deliberately spaced alphabet under this minimax contract. This is a theorem about exact worst-case Hamming discrimination, not Shannon capacity or a rate-distortion theorem.

## Exact fault contract and block-alignment decoder (proof)

The hypothesis sets consist of all transformed phase words. Two distinct such sets have minimum Hamming distance N-L_B(a,b). If received words agree off the union of two error supports and a shared erasure support, their clean explanations agree on at least N-2e-f indices. Conversely, take two clean transformed words agreeing on L_B indices and erase up to f differing positions, then split the other differing positions between two replacement supports of size at most e. This constructs a common received word whenever N-L_B<=2e+f. Hence universal phase recovery holds exactly when 2e+f<N-L_B(x). There is no probability or independent-error assumption.

Computing L_B need not enumerate the possible calibrations. For a pair of grids of sizes q,r and plateau bounds B,C, form the integer contingency matrix W[i,j] counting indexed observations of cell (i,j). Reverse the column axis for the opposite relative polarity. With equal orientation, common output levels correspond to a sequence of disjoint ordered pairs of input intervals, each row interval of length <=B, each column interval of length <=C. The full rectangle mass of each matched pair can be included: all rows and columns in its rectangle share the same output. Different matched pairs must be strictly ordered in both axes. Unmatched grid levels can be partitioned into singleton intervals with strictly ordered values between matched outputs, or before/after them. Thus such an interval matching is both necessary and sufficient. In particular, absent grid levels still count toward plateau width.

Let T(i,j) be the maximum mass using the first i rows and j columns. Start T(0,j)=T(i,0)=0. Then

    T(i,j)=max(
        T(i-1,j),
        T(i,j-1),
        max_{1<=u<=min(B,i),1<=v<=min(C,j)}
           [T(i-u,j-v)+mass([i-u,i),[j-v,j))]
    ).

If the last row or column is unused, one of the first two cases suffices. Otherwise the last matched intervals end at i,j and contribute exactly the rectangle mass; the preceding match is confined to the preceding prefixes. This proves the recurrence by induction. A summed-area table supplies rectangle masses in O(1). Compute both orientations and take their maximum. Time O(N+qrBC), space O(qr). For B=C=1 the recurrence is the strict weighted chain from #792 expressed on a dense grid.

For actual received values, delete flagged positions, sort distinct observed values and replace them by their ranks. The received side is not a second unknown quantizer; it has C=1. A matched input block must map to one observed value, and distinct matched blocks must map to distinct ordered values. Unmatched input levels can be assigned by interpolation without altering any observed clean value. The maximum mass is therefore the exact number of observations that can be fitted by some legal fixed channel. Keep each phase with mass >= number of nonerased samples - e. This produces the entire feasible candidate list, including empty and ambiguous results. Rank construction in the retained simple implementation uses indexOf; a map can reduce that preprocessing to O(N log N).

The source is a standalone synthetic oracle rather than a production streaming API. It assumes valid finite integer input-grid indices, finite received values or null, and valid bounds.

## A blunt ruler breaks the previous witness

The previous four-level pilot was (1,3,0,0,1,0,3,2,3,3), N=8,K=3. With strict calibration L=2, so any three retained effective observations suffice. With q=4,B=2 its exact L rises to 6. Now seven effective observations are needed; even one arbitrary substitution can cause ambiguity.

The retained counterexample uses the SAME legal partition (0,0,1,1) in both hypotheses, scaled by 100:

    phase 1: 100 0 0 0   0 100 100 100
    phase 2:   0 0 0 0 100 100 100 100
    received:  0 0 0 0   0 100 100 100

Either hypothesis uses exactly one replacement, at different indices. The decoder returns [1,2]. This failure does not depend on permitting different calibrations in competing explanations. It is a constructive negative result, not a numerical conditioning issue.

If the grid is fixed at q=4,B=2, m=2. Any two binary words have at least ceil(N/2) agreement under identical or reversed binary labeling (the two Hamming agreement counts sum to N). Therefore L*>=4 at N=8. A spaced binary pilot (0,0,0,0,2,0,0,2,0,0) attains L=4 for every phase pair and both relative polarities, so the exact optimum is five required survivors. Redesign alone helps, but cannot recover the old three-survivor guarantee on this grid.

## New optimal three-level motif and exact grid threshold

A finite search discovered a smaller strict-model alphabet than the old four-level witness. On N=8,K=3, the ternary pilot

    z=(0,0,1,0,2,2,1,2,0,0)

has L=2 for every phase pair in both orientations. Its three phase words are 00102212, 01022120, 10221200. Exhaustive enumeration of all 3^10=59049 pilots found exactly 16 with L=2. The absolute two-survivor obstruction from #792 (on two observations there are only equal or unequal classes up to reversal, with three phases) proves global sharpness regardless of alphabet size.

By the reduction theorem, the spaced pilot B*z works on q=2B+1 levels for every B>=1. All adjacent occupied levels are separated by B. The grid threshold q>=2B+1 is also necessary: with q<=2B, the effective alphabet is at most two, and the binary obstruction gives L>=4 at N=8 (or complete collapse if m=1).

In particular q=5,B=2 is sufficient, not q=7 as naively spacing the four-level witness would suggest:

    0 0 2 0 4 4 2 4 0 0

Any 2e+f<=5 is universally correctable. This theorem counts grid levels including unused guards, not the number of distinct transmitted values (three). It does not assume a minimum output amplitude separation.

| Grid q | Plateau B | Pilot | Exact L | Required effective survivors |
|---:|---:|---|---:|---:|
| 4 | 1 | old four-level | 2 | 3 |
| 4 | 2 | old four-level | 6 | 7 |
| 4 | 2 | redesigned binary | 4 | 5 |
| 5 | 2 | new spaced ternary | 2 | 3 |
| 7 | 2 | old spaced four-level | 2 | 3 |
| 10 | 3 | old spaced four-level | 2 | 3 |

The exact grid threshold holds for the fixed 8-observation, three-consecutive-offset contract. For larger windows the minimum effective alphabet remains an interesting separate combinatorial problem. The general reduction removes the plateau nuisance from that optimization without solving all strict-alphabet instances.

Additional finite minima (three candidate phases, strict calibration):

| N | Binary optimum L | Ternary optimum L |
|---:|---:|---:|
| 3 | 2 | 2 |
| 4 | 2 | 2 |
| 5 | 3 | 2 |
| 6 | 4 | 2 |
| 7 | 4 | 2 |
| 8 | 4 | 2 |

These are exhaustive finite minima, not an asymptotic formula. In particular N=6 binary does not attain the pairwise ceil(N/2) bound simultaneously for all three overlapping phases.

## Qualification, source ledger and limits

Run node laboratory.cjs from this directory; no external dependencies. The laboratory executes 674,728 complete finite pilots across strict binary/ternary N=3..8 and plateau profiles (q,B)=(3,2),(4,2),(5,2), N=3..6. Histograms count all pilots with no symmetry pruning. All 12 plateau profile minima agree with the reduction theorem. It also executes 400 seeded block-DP versus independent exhaustive partition-and-mask checks; 800 seeded pairwise reduction checks (both lower bound and spaced equality); 600 candidate-list decodes with two arbitrary replacements and one erasure, all recovering the injected phase and agreeing with the independent mask oracle. It verifies eight minimal-grid ternary profiles B=1..8, the old-pilot failure, and explicit shared-output ambiguity. Finite tests supplement the proofs; they are not independent review. The seeded draws use a 32-bit deterministic LCG, scaled using its full state, not a claim about physical fault probabilities. The final receipt records all exact combinatorial profiles. The particular ambiguity construction uses integer outputs; its general helper interpolates with JS numbers, not a general rational-arithmetic certificate.

Primary source context (all read by this same agent on 27 November 2026):
- Tim Gutjahr and Karsten Keller, *Generalized Ordinal Patterns and the KS-Entropy*, Entropy 23(8), 1097 (2021), https://doi.org/10.3390/e23081097 . Publisher HTML abstract and section 1 through equations (1)-(4), Definition 1 and the ensuing discussion of symbolization and partitions read at https://www.mdpi.com/1099-4300/23/8/1097 . Not whole-paper reading; PMC route returned a browser challenge. The authors generalize ordinal representations by changing the relation used to discriminate pairs. This is a conceptual connection: which distinctions survive an observer's partition? Their entropy problem differs from the finite adversarial decoding problem here. No entropy equivalence is inferred from the present result.
- Anxiao Jiang, Robert Mateescu, Moshe Schwartz and Jehoshua Bruck, *Rank Modulation for Flash Memories*, IEEE Transactions on Information Theory 55(6), 2659–2673 (2009), https://doi.org/10.1109/TIT.2009.2018336 . Institutional metadata and abstract read at https://authors.library.caltech.edu/records/9zr6t-5rz21 ; full article not read. The paper uses relative charge order to represent information rather than fixed cell levels. This supports the contextual link to rank-coded information but not a priority claim about plateau-bounded minimax codes.
- Repository predecessor #792/#793, complete report read, issue/comments and exact-head workflow 45994358142 checked (completed success). Its strict-model results are input to the present exploratory derivation, not accepted canonical human evidence.

Negative sediment: unrestricted nonstrict monotone maps permit complete collapse. Even B=1 permits arbitrarily close output levels, so without a positive output-gap bound there is zero uniform positive dense-noise tolerance: scale two legal clean words by an arbitrarily small positive constant and take their midpoint. Ties that were intentional cannot be distinguished from channel-created ties solely by observing equal outputs. A physical quantizer with arbitrary upstream compression, clipping, per-tick drift, or unknown grid does not automatically meet the bounded-plateau contract. Larger input grid resolution alone is not sufficient if B scales with q. The decoder assumes exact equality of received outputs and does not establish a robust analog tie detector. No acoustic, VST, device or listening trial was performed.

Design hypothesis: an MHAC calibration inspector can offer a grid/plateau contract, synthesize guard-spaced timing motifs and report all compatible interpretations. Test against actual bounded level collapses, not just arbitrary gain; separately measure output gaps and physical error mechanisms before claiming acoustic validity. Interpretation: unused positions can preserve a distinction, but this is not an empirical statement about the semiotics of human silence. Conventional finite coding theory, ordered partitions and dynamic programming explain every demonstrated result; no extra cybersemiotic mechanism established (Brier subtraction). Scientific priority unassessed.

Checkpoint: main base 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-796/blunt-ruler. Read AGENTS, RAG, programme, runbook, integrity, validation, experiments and human gates; no research/AGENTS or research/expeditions/AGENTS found. Reconciled 461 branch entries and 30 recent issues/PRs, targeted ordinal/coarsening searches, predecessor report, issue, PR and checks; fresh #796 body/comments read. Scope only this new directory. Draft/HOLD pending integrator critique and exact-final-head repository checks; full native repository validation not performed. No human gate for synthetic research.

Fiction: The apprentice learns that a blunt ruler may turn two different marks into one. Instead of marking more finely she leaves unused notches between the three marks she needs. The unused notches become part of her alphabet.
