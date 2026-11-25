# The Reset That Leaves a Score
## Shortest balanced saturation programs across capacities

Refs #424 · 25 November 2026 · isolated formal/synthetic/artistic expedition. Not Track E/G evidence, participant research, a production control, or an accepted auditory requirement.

## Model and result

One broadcast symbol changes every integer register by +1 or -1, clipping to [0,m] for capacity m. Registers have arbitrary unknown initial states. A balanced program has exactly as many plus as minus symbols (net input zero). We require every register of capacity 1 through R to forget its initial state and attain a specified endpoint f(m).

The complete feasible family is f(0)=0 and f(m)-f(m-1) in {0,1}. There are exactly 2^R different full target profiles. For a fixed profile, put d_m=+ if the increment is 1 and - otherwise. Let c=f(R) if d_R=+, and c=R-f(R) otherwise. The exact shortest balanced program length is

    L = R + sum_{2 <= m <= R, d_m != d_(m-1)} (m-1) + c.

This includes a quadratic worst-case programming cost even though an unconstrained balanced reset of all capacities takes only 2R operations. The compiler also accepts partial target profiles (null = unspecified) and minimizes length over all feasible completions.

## Proof: reverse records are the endpoint score

Let S_t be the ordinary prefix sum of a word, including S_0=0. While its range max(S)-min(S) is at most m, the image of the entire starting interval [0,m] is the integer interval with endpoints S_t-min(S) and m+S_t-max(S). Induction: a + step translates both endpoints and clips the upper endpoint at m, exactly updating the maximum; the - case updates the minimum. Equality of the range and m collapses the image to a singleton. Subsequent updates cannot recover initial-state dependence. Therefore a word resets capacity m exactly when its prefix-sum range is at least m. Unit increments ensure the first crossing is equality.

Read the word backwards, without negating symbols, forming reverse prefix sums Q_j with Q_0=0. For a suffix of the forward word, the maximum reverse prefix sum equals the suffix's total minus its minimum ordinary prefix sum; likewise for the minimum. At the first reverse time the range reaches m, the corresponding forward suffix has range exactly m. The interval formula yields the singleton max(Q_j) at that time, regardless of state when the suffix began. Every earlier part of the forward word is thus irrelevant to the endpoint. Each new reverse range record increases width by one; extending the upper extreme increments the endpoint by one, extending the lower extreme leaves it unchanged. This proves necessity of the profile condition. If the full range is smaller than m, the image is instead [max(Q), m+min(Q)] and has positive width.

For sufficiency, construct a reverse walk from zero with successive range extensions on exactly the prescribed sides. After the R-th record, return directly to zero. Reversing the resulting symbol sequence gives a balanced forward word with the requested profile. The return to zero introduces no new range record.

## Proof: minimum cost

At the m-th range extension the walk is at the new extreme. From the preceding record, a same-side extension requires at least one step; an opposite-side extension requires at least m steps, since the preceding width was m-1. At the last record the coordinate is f(R) or -(R-f(R)), so a return to zero requires at least c steps. These lower bounds hold for *any* word realizing the full profile, even one that subsequently extends beyond R. Walking directly between the prescribed record positions and then to zero attains every lower bound. This proves the length formula.

The least possible length across profiles is 2R: any closed walk spanning R must traverse at least R steps in each direction, and a single out-and-back excursion attains the bound. An alternating record direction profile takes R+R(R-1)/2+ceil(R/2) operations. This is also a global maximum of shortest profile lengths: hold the last direction fixed and compare any profile with the alternating one having that last direction. At each missing switch between positions i and i+1, flip the first i directions, creating that switch without changing any other adjacency or the final direction. Such a flip increases the switch cost by i and can reduce the final-side population c by at most i. The cost cannot decrease on the way to the alternating profile. Both alternating profiles have c=ceil(R/2).

For partial anchors, dynamic programming over (m, number of positive record directions so far, last direction) is sufficient. The transition adds 1 for same-side or first extension and m for an opposite-side extension; an anchor rejects incompatible counts. At termination add c. Every feasible profile is a path in this DAG, and future costs depend only on these state variables. The implementation retains a deterministic lexicographic tie-break string. The state count is O(R^2); retained strings add copying/storage overhead. Capacity limit 256 is an implementation choice, not a theorem.

## Executable witnesses and falsifiers

- At R=8 the all-upper profile [1,2,3,4,5,6,7,8] costs 16 operations; [1,1,2,2,3,3,4,4] costs 40. Both reset all initial states and have net zero.
- If only capacities 2,4,6,8 need final values 1,2,3,4, the optimal cost falls to 28; a completion is [1,1,1,2,3,3,3,4]. Do not infer that its unanchored capacities meet the original full contract.
- Targets [1,0] and [0,2] are impossible for capacities 1 and 2. Independently attainable targets are not necessarily jointly attainable.
- The balanced word '+-' fails to reset any capacity m>1. Zero net input is not a reset certificate.
- A capacity exceeding the reverse range retains an interval of possible states; no finite program resets unbounded unknown capacities.
- Without clipping, a balanced word is the identity. Leaky, wrapped, continuous-time or independently weighted increments change the model. Nonunit steps can skip the one-at-a-time record geometry used for optimality.
- This is a reset of explicitly modeled numeric states, not a claim about cognition, forgetting, emotion, or a listener's interpretation.

## Reproduction and qualification

From this directory: run `node reset.cjs` for the exact integer compiler census and `python independent.py` for a separate full-transition-image BFS and two WAV renders. The JS source was executed in the tool's V8 JavaScript runtime, then fetched back and re-executed to reproduce the committed receipt exactly; native Node CLI execution was not established. Python 3.13.5 executed the independently formulated oracle and audio generator. The full-state BFS explicitly propagates every possible initial value instead of relying on the interval formula; it verifies all 254 target profiles through R=7. The JS test suite additionally checks 65,528 direct image comparisons across 8,191 words through length 12, 6,527 feasible partial-anchor optimality comparisons against exhaustive full-profile minimization, and six invalid inputs. Both BFS implementations visit 7,101 states (including net input). Neither is an independent human review.

Original WAVs are generated locally by the Python source, not committed as binary files. The receipt records sample counts, peak PCM and SHA-256 on this runtime; cross-platform libm byte identity is not guaranteed. Both renders repeated byte-identically here.

- same-input-different-score.wav: two balanced 40-symbol programs with identical plus/minus counts; the ascending score uses a 16-step reset preceded by 24 alternating filler steps for duration matching. Both start from the same midpoint state vector. Their final normalized oscillator-gain profiles differ.
- forgetting-in-stereo.wav: both channels use the same 40-step alternating-record word, starting at opposite extremes. They converge at tick 12 and remain equal. Eight sinusoidal carriers at 180+73m Hz have gain x_m/m; linear 10 ms ramps, shared phase, 16 kHz stereo PCM16, 3.8 seconds. Carrier selection and gain mapping are artistic conventions. The arithmetic state trajectories, not the waveform's perceptual quality, are the test object.

## Exaptation

A broadcast reset can double as a programmable parameter bank, encoding a monotone discrete score in the saturation limits of several otherwise identical registers. The programming interface is a pair of signed unit commands, not individually addressed writes. This suggests constrained embedded parameter initialization, reproducible fault injection in clipped accumulators, reset protocols for explicitly modeled agent-state registers, and a synthesis instrument whose voice amplitudes encode reverse-record history. The exact DP can trade unneeded control commitments for a shorter programming sequence. Hardware timing, saturation semantics, noise, transport costs and actual listening remain untested.

## Provenance and integration boundary

Background only: Mikhail V. Volkov, *Synchronization of finite automata*, Russian Mathematical Surveys 77:5 (2022), 819–891, https://www.mathnet.ru/eng/rm10005 , §1.2 definition 1.1 (visible passage checked 2026-11-25 by ChatGPT; not a full reading). Its reset-word terminology is used here for a simple family of finite automata. The balanced shared-word theorem and construction above are self-contained derivations; no mathematical priority or comprehensive literature search is claimed. Adjacent repo issue #364 investigates Preisach relay ensembles and first reversals, not these bounded additive registers; no inheritance of its results is needed. Live issue searches for saturation, accumulator, synchronizing/reset word, clipping and hysteresis, plus recent PR reconciliation, were performed before selecting the scope. The search is not proof of absence of overlap.

Reconciled main: 495a98ca12bae467a507031f04931aa4254b1866. New issue #424 and branch mhac-expedition/reset-score-424 only. Agent instructions, RAG, programme, runbook, research integrity and validation documents inspected. No frozen records, central manifests, or production sources changed. Native Git remote access failed with DNS resolution, so repository-wide local validation remains unexecuted. This exploratory work remains Draft pending exact-head checks and integrator review. No external human action or participant work was undertaken. AI-assisted derivation, implementation, source lookup, and computational checking by ChatGPT; no independent human reviewer or external endorsement.
