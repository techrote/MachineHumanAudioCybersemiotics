# The Rhythm That Cannot Stay Apart

Synthetic mathematical expedition, issue #400, 2026-11-24. Base: `495a98ca12bae467a507031f04931aa4254b1866`. This is not a live research record, human study, production scheduler or priority claim. AI-authored implementation and self-review; the separate Python oracle is algorithmically independent, not independent human review.

## Model

A voice with integer period p and offset o fires exactly when t = o (mod p), for integer ticks t >= 0. Events occupy one tick and have unit resource demand; no jitter, preemption, queuing, variable duration, dropping or reassignment is allowed. Duplicate periods are distinct voices. Minimize the maximum number of simultaneous events over the entire infinite schedule. This is not pinwheel scheduling (which permits unequal inter-event gaps).

## Exact constant-pairwise-GCD theorem

Group identical periods p_i with multiplicity m_i. Suppose gcd(p_i,p_j)=g for all distinct groups; for one group set g=p_1. Write a_i=p_i/g. The a_i are pairwise coprime. Then the optimal peak is

    K* = ceil( sum_i ceil(m_i/a_i) / g ).

Proof: Each group distributes its voices among g residue buckets modulo g. In bucket r, let m_ir be its count and b_ir the maximum number of voices sharing an exact offset modulo p_i. There are a_i possible offsets in that bucket, so b_ir >= ceil(m_ir/a_i). For each nonempty group in that bucket, choose an offset realizing its maximum b_ir. Their congruences are jointly compatible (all chosen offsets agree mod g, and the reduced periods are pairwise coprime). The generalized CRT yields a nonnegative integer tick attaining sum_i b_ir. No tick in that bucket can exceed that sum. Thus the peak is max_r sum_i b_ir. Summing across buckets, sum_r b_ir >= ceil(m_i/a_i), proving the lower bound on K.

Construction: partition each group's voices into chunks of at most a_i voices; assign consecutive chunks to residue buckets round-robin across all groups. Within a chunk assigned bucket r, assign offsets r+g*j for j=0,...,chunk_size-1. Every chunk contributes at most one event per tick. The maximum number of chunks assigned to any bucket is ceil(total chunks/g), attaining the lower bound. The one-group case follows with a_1=1. No array of size g or hyperperiod is allocated. BigInt arithmetic preserves exact integers; group pairing takes quadratic gcd comparisons and phase construction is linear in number of voices after grouping/sorting.

The compiler additionally certifies the peak of any supplied offset arrangement in this family, by taking per-group/per-bucket maximum multiplicities and merging the corresponding congruences, yielding an actual simultaneous-event tick and full hyperperiod. It returns active voice indices. Empty inputs, nonpositive/noninteger periods, more than 256 voices, malformed offsets and nonconstant pairwise gcd are refused; refusal of the last class is **not** an infeasibility certificate. General unequal-gcd optimization is outside this compiler.

## Counterexamples and transfer

* Periods 6,10,14: each pair permits collision-free offsets, but all three cannot fit on a one-event resource. Every pair has gcd 2, and three offsets must share a parity pair. Optimal peak 2 with offsets 0,1,0. Aligned peak 3. Average load 71/210. By taking g=2 and arbitrarily many sufficiently large distinct primes as reduced periods, average load can be made arbitrarily small while optimal peak ceil(n/2) grows without bound.
* Periods 6,10,15: global gcd 1, yet offsets 0,1,2 are collision-free (pair gcds 2,3,5). Applying the constant-pairwise formula using only the global gcd would be false. The specialized compiler refuses this input; the separate timeline oracle finds peak 1.
* Periods 101,103 with offsets 0,1: the first coincidence occurs at tick 5151, then repeats every 10403 ticks. A long clean prefix is not a lifetime certificate.
* Multiplicities five at period 4 and four at period 6: a_i=2,3; total chunks 3+2=5; peak 3. Average load 23/12; its ceiling 2 is insufficient.
* Scaling all periods by a common integer changes g and can change the optimum; simply stretching time is not a theorem about the phase search space.
* Fixed-event concurrency is not acoustic peak amplitude, perceived masking, CPU deadline feasibility with arbitrary jobs or a claim about people. Allowing phase jitter can remove obstructions and changes the problem.

Potential exaptation: rigid polyrhythm generator with peak-onset budget; allocate shared procedural event triggers or exact periodic telemetry phases; adversarial tests for event queues that assume low mean load implies low peak. The same phase compiler can deliberately concentrate or distribute simultaneous pulses. Event-count objective does not optimize groove, spectral energy, clipping or listening preferences.

## Provenance and novelty boundary

Michael J. Short, *Exact and Heuristic Algorithms for Thrift Cyclic Scheduling*, Algorithms 2(4), 1449–1472 (2009), https://doi.org/10.3390/a2041449. Publisher HTML inspected, introduction (offset assignment / simultaneous actions) and §3.2 eqs. 11–13 (congruence and joint compatibility). Established broader problem and CRT verification, not new here.

Eun-Seok Kim and Celia A. Glass, *Perfect periodic scheduling for three basic cycles*, Journal of Scheduling 17, 47–65 (2014; online 2013), https://doi.org/10.1007/s10951-013-0331-3. Publisher HTML inspected, abstract, introduction, §3 Lemmas 3–4 and Theorem 1: two distinct periodicities have a one-resource ceiling-sum condition. Our derivation specializes peak concurrency for a restricted constant-pairwise-gcd family with arbitrary multiplicities and multiple simultaneous events. No priority or comprehensive literature search claimed. No citations from these sources are added to frozen registers.

## Reproduction and results

Run `node verify.cjs` from this directory; compare stdout with results.synthetic.json (a deterministic receipt from executing the same functions in a JS isolate). Run `python independent.py` for the separately formulated bitset timeline oracle, negative cases and two original PCM16 stereo WAVs. Both implementations remove global translation symmetry by setting the first offset to zero in exhaustive search. The JS census covers every multiset of one through five periods from 1..7: 497 in-family, 294 outside-family, 146998 phase assignments examined, 497 compiled CRT witnesses. Histogram for peak 1..5: 42,154,178,95,28. Python reproduces all 497 optima and histogram. Large-period CRT example exceeds 10^36 ticks without enumerating a timeline. These are exact constructed populations, not measured real-world rates.

Audio: 50 ms ticks, 16 kHz stereo, each voice mapped to a raised-cosine-windowed sinusoidal pulse (300/400/500 Hz). Common scaling, no automatic normalization. Left aligned, right offsets optimized or independently supplied. rigid-voices.wav spans 210 ticks (10.5s), identical 71 events/channel, peak concurrency 3 vs 2. gcd-geometry.wav spans 60 ticks (3s), identical 20 events/channel, peak concurrency 3 vs 1. This is artistic pulse mapping, not human perception data. Files generated locally, not binary repository assets; source regenerates them. Python receipt records hashes and PCM peaks.

Repository-wide CI and independent review are separate gates. Keep Draft; no change to main or central records.
