# The Reset That Can Be Forgotten

**MHAC expedition #232 — 2026-11-24.** Original finite-model derivation and synthetic experiments, AI-assisted. No Track E/G evidence, participant data, production control system, or mathematical-priority claim.

## Question and scope

A reset sequence may be independent of the starting state yet depend absolutely on every command arriving. Can one open-loop command word absorb unknown silent omissions, without observing the device, the omitted position, or the starting state? This differs from #207 (order dependence of reversible operations), #203 (destructive measurement), #224 (stream decoding), #187 (missing message interpretation), #230 (source attribution): here the output is a common terminal state, not knowledge of the trajectory. No changes to frozen records or core programmes.

A complete deterministic instrument has finite states Q and an alphabet of total maps. An issued word is executed in order, with any zero through k individual command positions silently omitted (the state remains unchanged at those positions). The goal is **one shared terminal state for all initial states and all permitted omission histories**, not merely a rank-one map for each history individually. There is no feedback, substitution, insertion, time variation, external state transition, or probabilistic assumption.

## Exact search and certificates

Let S_j(w) contain all states reachable after w with at most j omissions, starting anywhere. S_j(empty)=Q. For an appended map f,

    S_0(wf) = f(S_0(w))
    S_j(wf) = f(S_j(w)) union S_(j-1)(w), j>0.

Proof: the final command was either executed (first term) or omitted (second term); these cases exhaust the possibilities. The sets are nonempty and nested. A word is k-robust exactly when S_k is a singleton. BFS over nested tuples, with unit command cost, is exact because future successors depend solely on the tuple and BFS processes increasing word length. An exhausted finite search proves impossibility; a budget exit does not. A certificate is any closed collection containing the initial tuple and no accepting tuple; every map successor must be inside it. The verifier checks this independently of parent pointers. The nested tuple universe has at most (k+2)^n elements (each original state has a first membership level or is absent); this is exponential, not a scalable universal compiler. Code deliberately limits n to 12, k to 2, and visited tuples to two million by default.

Direct replay independently branches over omission choices and all initial states. A control shows that repeating an ordinary reset word need not give a robust reset: corruption of its final block can leave a different terminal state. A constant map repeated k+1 times does give a robust reset. For n=1 the empty word suffices. Permutation-only alphabets cannot reset n>1 even without loss.

## A constructive family and a hard ceiling

Use the familiar Cerny-style maps on Q={0,...,n-1}: a rotates by +1 modulo n; b maps n-1 to 0 and fixes every other state. Our convention swaps the letter names relative to Volkov's example. The usual word b(a^(n-1)b)^(n-2) has length (n-1)^2 and resets to 0 (the nominal set shrinks by one at each b after a^(n-1)). For n>=3 an explicit one-omission robust word is

    b a^(n-1) b (a b a^(n-2) b)^(n-3) a b a^(n-1) b

of length n^2. Here powers denote repetitions, not exponentiation of numerical states. For n=2, b is constant and bb suffices.

**Construction proof.** Write I_m={0,...,m}. After the initial b a^(n-1) b, the nominal set is I_(n-3) and the at-most-one-loss set is Q: omitting the last b allows n-1 and omitting an appropriate rotation allows n-2, while the nominal states cover the others. More explicitly, after the first b the sets are I_(n-2), Q; the rotation leaves the second set Q, and the final b maps Q to I_(n-2), while the omit-last term adds n-1. Thus S_1=I_(n-3) union {n-2,n-1}. For 1<=m<=n-3, starting with S_0=I_m and S_1=I_m union {n-2,n-1}, applying ab yields S_0={1,...,m+1}, S_1=I_(m+1). Rotating n-2 times gives S_0={n-1} union I_(m-1), S_1={n-2,n-1} union I_(m-1); omitting a rotation produces a subset of that S_1. Final b gives S_0=I_(m-1), S_1=I_(m-1) union {n-2,n-1}. Induction reaches m=0. The final ab yields S_0={1}, S_1={0,1}. The final a^(n-1) yields S_0={0}, S_1={0,n-1}, including all one-rotation omissions; final b collapses both sets to {0}. The length is (n+1)+(n-3)(n+1)+(n+2)=n^2.

**Two-omission impossibility theorem for this same family, n>=3.** Suppose a robust word exists. It must contain a (b alone has at least two fixed states) and must end in b (omitting a final rotation changes every state). Let the last a be followed by a nonempty run of b's, whose map is b by idempotence. For a fixed initial state, call the nominal state immediately before that last a x. Comparing the intact word to the one omitting the last a requires b(x+1 mod n)=b(x), which for n>=3 is possible only when x=n-1. This last a cannot be first, because then x ranges across all Q; it cannot be immediately preceded by b, because b never outputs n-1. Therefore it is immediately preceded by a. Fix an initial state; immediately before these last two rotations the nominal state is y. Comparing zero, one and two omissions of these rotations forces b(y), b(y+1), b(y+2) to coincide. Their arguments are three distinct states, but b has no fibre of size three. Contradiction. Thus **no word of any length** can tolerate two omissions in this model for n>=3, and neither can any larger budget. This is a model-specific impossibility, not a general impossibility of fault-tolerant control.

The one-loss n^2 upper construction is proved for all n>=3; its optimality is established by BFS only for n=3..10. Do not extrapolate a universal sharp lower bound from eight data points. The impossibility proof does not depend on BFS.

## Results and adversarial interpretation

All ordered pairs of total maps on labelled states (including repeated maps) were enumerated. They are not quotient classes, random samples, or observed device populations.

| n | All pairs | Ordinary reset exists | One-loss reset exists | Ordinary but no one-loss reset |
|---:|---:|---:|---:|---:|
| 2 | 16 | 12 | 12 | 0 |
| 3 | 729 | 549 | 495 | 54 |
| 4 | 65536 | 51520 | 41584 | 9936 |

For the 4-state population, 9936/51520 (19.29%) of the ordinary-synchronizing automata fail one-loss robustness. Some ordinary length-2 cases require 8 commands when one loss is permitted. The Cerny family has lengths 1,4,9,16,25,36,49,64,81 for k=0 at n=2..10; for k=1 these are 2,9,16,25,36,49,64,81,100. The k=2 solver certifies no solution for n=3..10 (17 to 64302 reached tuples). For n=2, bbb works. A one-loss impossible three-state example uses maps [1,0,0] and [2,1,0] with ordinary reset aba. Exhausted searches are closure-checked; successful one-loss census words are explicitly replayed. Direct trace comparison covers 3024 cases (all two-state map pairs, all binary words of length 0..5, budgets 0..2); construction verified for n=3..64 using sets, plus direct replay for n=2..10. Results include every histogram and a representative per populated bin, not a complete listing of all labelled automata.

## Source notes and transfer

- M. V. Volkov, *Synchronization of finite automata*, Russian Mathematical Surveys 77(5), 819–891 (2022), DOI 10.4213/rm10005, https://www.mathnet.ru/eng/rm10005 . Agent inspected HTML excerpts of sections 1.2 (definition, C4 example) and 2.3 (subset automaton shortest-path computation), not entire survey. These support ordinary synchronization and subset BFS, not our deletion extension.
- A. Kisielewicz, J. Kowalski and M. Szykuła, *Computing the shortest reset words of synchronizing automata*, Journal of Combinatorial Optimization 29, 88–124 (2015), DOI 10.1007/s10878-013-9682-0, https://link.springer.com/article/10.1007/s10878-013-9682-0 . Agent inspected abstract and HTML section 2.4 correctness discussion. Their ordinary reset algorithm is a more sophisticated baseline; not implemented here.
- V. Vorel, *Subset Synchronization and Careful Synchronization of Binary Finite Automata*, https://arxiv.org/abs/1403.3972 , abstract (2014 preprint; publication metadata also inspected at https://nomos.is.cuni.cz/publication/559768, 2016). Partial automata careful synchronization and subset synchronization have their own definitions and complexity. Our model is total maps with omitted actions, not an assertion that their bounds carry over.
- Targeted search for fault-tolerant/deletion reset words was inconclusive; no priority/novelty claim. No source files copied, no license assigned.

Exaptation: open-loop macro compilation for quantized synth presets, symbolic agents with dropped action events, and test generation for stateful procedural tools. A solver that refuses to certify a reset is as useful as one that constructs it. A command log is an intention trace, not evidence of execution; agreement at the endpoint does not establish identical histories. Actual systems require a specified fault model, deadlines and state verification; this is not safety guidance. The score uses arbitrary triangle pitches mapped to state indices; it is an artistic witness, not a tested perceptual language.

## Reproduction and acceptance

Run `node reset.mjs > actual.json` and compare with `results.synthetic.txt`; original source run executed in the available V8 runtime, not a clean Node checkout. Run `python3 render.py run` to generate three stereo WAVs and a hash manifest. All data synthetic, no human participants. Audio local repeat was byte-identical. See QUALIFICATION.md for runtime evidence. Draft PR deliberately pending review and final-head CI, no core programme acceptance or merge.
