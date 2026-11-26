# The Register That Forgets Only When It Travels
**Refs #662 · 26 November 2026 · synthetic mathematical expedition, agent self-review.**

## Observation contract

The earlier [#644](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/644) proves that a fixed nonuniform independent cyclic-addition channel cannot become uniform through finite repetition. That theorem is correct in its scope. Does it survive replacing translation-invariant addition by a state-dependent stochastic transition? No. The distinction matters for a semiotic interface that deliberately overwrites a previous context rather than merely adding random variation.

Let a state be a word of h symbols from an alphabet of size q >= 2. The forward operation F drops the leftmost symbol and appends a fresh independent uniform symbol on the right. The backward operation B drops the rightmost symbol and prepends a fresh independent uniform symbol on the left. Each operation consumes exactly log2(q) bits of Shannon entropy in its fresh symbol; the direction schedule is fixed independently of both original and fresh symbols unless explicitly stated otherwise. B is the stationary time reversal of F under the uniform law, not an inverse that restores the discarded symbol. The observer receives the final word, with the schedule treated as known when evaluating a conditional channel. No claim about security of actual data or human perception.

A four-slot binary register offers a miniature anomaly. Four forward steps forget every initial bit. Four alternating steps F B F B preserve three initial bits. Both schedules consume four fresh fair bits, but the second keeps replacing an edge that has already been refreshed. A freshly drawn symbol that is later discarded is not a persistent resource.

## Exact extinction and spectrum

For any n-state doubly stochastic matrix P let J have every entry 1/n. Put A=P-J. Then AJ=JA=0, and P^k=J+A^k for k>=1. Hence exact mixing in finite time is equivalent to nilpotence of A. Its restriction to the (n-1)-dimensional zero-sum space gives the universal upper bound n-1 for n>=2. If P is normal (including symmetric or circulant), A is normal, and nilpotence forces A=0. Thus only the already-uniform normal channel mixes exactly in finite time. The cyclic result in #644 is a special case. Ordinary eigenspectra do not determine the extinction horizon of a nonnormal channel.

Every integer horizon h in [1,n-1] is attainable even with strictly positive rational doubly stochastic matrices. In column-vector notation let u_i=e_i-e_n for 1<=i<=n-1, and v_j=n e_j-1 (the all-ones vector is denoted 1). Then v_j^T u_i=n delta_ij. Define A0=sum_{i=1}^{h-1}u_i v_{i+1}^T (empty sum when h=1). It annihilates 1, has image in the zero-sum subspace, and moves u_j to n u_{j-1} for 2<=j<=h, annihilating the other basis elements. Thus its nilpotency index is h. Choose M=1+max |A0_ij|. P=(M*11^T+A0)/(nM) is positive, rational and doubly stochastic, and its exact mixing horizon is h. This construction demonstrates an algebraic horizon, not a large detectable discrepancy at the final pre-extinction step. The integer laboratory tests every h for n=2..12.

A much more strongly separated sparse example is the de Bruijn shift: F^h=J on n=q^h states, but F^(h-1) retains one symbol, so its worst-row total variation from uniform is 1-1/q. All nontrivial eigenvalues of F are zero, yet the pre-extinction discrepancy can be substantial. If every row has at most q possible next states, k steps give at most q^k possible final states per input. For n=q^h, k>=h is necessary for exact uniformization. The shift attains that lower bound with fair q-way choices.

## The directional-range theorem

Write d_t=+1 for F and -1 for B. Let S_0=0 and S_t=sum_{i<=t}d_i. Define R=max_{0<=i<=k} S_i - min_{0<=i<=k} S_i. The exact number of surviving original symbols is

    m=max(0,h-R).

Proof: the original coordinate j (one-based) occupies position j-S_t if it survives. Survival requires 1<=j-S_t<=h at every time, hence 1+max S<=j<=h+min S. Counting the integer intersection gives m. Every other final coordinate is a distinct surviving fresh draw; because each draw is independent, those coordinates are jointly uniform independently of the surviving original block. There is no duplication. Conditional on the initial state and fixed schedule, the row law is uniform on q^(h-m) words with the survivor block prescribed. Rows with the same surviving block agree; rows with different blocks have disjoint supports.

Consequences (exact, for a fixed known direction schedule):
- Row support = q^(h-m); distinct rows and ordinary rank = q^m (disjoint nonzero row supports).
- Worst-row total variation from uniform = 1-q^(-m). Maximum distance between two conditional rows is 1 for m>0, zero otherwise.
- For an initially uniform word X and final Y, I(X;Y)=m log2(q), since Y is uniform and its conditional entropy is (h-m)log2(q).
- Final uniformization from every initial word occurs iff R>=h, regardless of the net displacement S_k.
- The schedule F^h B^h forgets everything despite net displacement zero. F B F B ... retains h-1 symbols forever for h>=2. Both matrices separately have finite mixing horizons, but their alternating product does not. Indeed B=F^T and FB is a symmetric matrix; its powers cannot become J unless FB=J.

For any finite fixed schedule the result depends on its excursion range, not its duration, total entropy consumed, or final direction. This supplies an explicit witness for noncommuting stochastic composition.

## Sharp reversal and omission budget

Suppose a nominally forward schedule of length k may have at most e steps reversed, at locations fixed independently of the symbol draws. For h>=2 the exact minimum universal length is

    k=h+2e.

Sufficiency: net displacement is at least k-2e=h; range dominates its absolute value. Necessity at k=h+2e-1: take (F B)^e followed by F^(h-1), whose range is h-1. All its prefixes remain unforgotten, so every shorter length also has a failing schedule within the reversal allowance. For h=1 either direction erases in one step, a necessary exception. If stages may instead be omitted (no replacement), each omission costs one step and the exact budget is h+e. With at most e reversals and f omissions, h+2e+f is sharp for h>=2 by inserting f no-ops into the same witness. This counts stages, not elapsed time or human responses.

The same proof works for a direction controller independent of draws and input, with its realized schedule revealed. Outcome-dependent choice is not covered: a one-slot fair symbol can be retained only when it has a desired value by adaptively selecting stopping times. Even fixed-direction extinction does not erase an earlier observed transcript.

## Random directions, a different stopping contract

Let directions be independent fair coins, independent of the inserted symbols and the initial word. Stop at T when the displacement range first reaches h. Conditional on every realized stopping schedule, the word is uniform independent of X, hence T and final word jointly reveal no information about X under the model. This is a strong stationary time. The mean is exactly h(h+1)/2: after range r is attained the walker lies at an endpoint of an interval of r+1 visited integers. The expected exit time starting at that endpoint is r+1 (solve the elementary gambler's-ruin difference equation f(i)=1+(f(i-1)+f(i+1))/2 with zero at the two outer boundaries). Sum from r=0 to h-1. This is established random-walk mathematics, not a discovery of the expectation formula.

By contrast, at a deterministic time k, the hidden-direction averaged channel K=(F+B)/2 is symmetric, not J for h>=2, so no power is exactly uniform. An alternative witness avoids eigenvalues: begin with the all-zero input, then every retained original symbol is zero while every other coordinate is uniform. There is positive probability of an alternating direction path at every finite k, retaining h-1 original symbols. Expected number of nonzero coordinates is therefore strictly below its uniform value h(1-1/q). The schedule need not be disclosed to detect that residual bias. For any fixed k the probability of T>k upper-bounds worst-row TV by coupling to a uniform initial word using identical random directions and replacements. This bound is not claimed sharp for the hidden-direction observer. With the schedule disclosed, the expected conditional TV and information can be calculated directly from the distribution of m. An adaptive stopping rule independent of content is a different contract from fixed-time inference or content-dependent postselection.

An exact counting DP uses state (r,x), where r is the current range and x is the position relative to the minimum (0<=x<=r<h). A step inside the interval changes x by +/-1. A step outside extends r by one and places x at the new endpoint. Discard states with r>=h. Integer counts divided by 2^k give P(T>k); O(h^2) states suffice. For h=8 the exact survival probabilities at k=8,16,32,64 are 254/256, 56322/65536, 2036810954/4294967296, and 1725759751758854938/18446744073709551616. The mean is 36 steps. Directional repetition requires only eight.

## Evidence, computation and prior art

- Brosh and Gerchak, *Markov Chains with finite convergence time*, Stochastic Processes and their Applications 7 (1978), 247–253, DOI https://doi.org/10.1016/0304-4149(78)90044-3 . Institutional abstract and metadata read at https://cris.tau.ac.il/en/publications/markov-chains-with-finite-convergence-time-2/ . Explicit prior overlap: minimal-polynomial characterization and finite convergence bounds; full article not inspected.
- Mehta and Schulman, *Edge Expansion and Spectral Gap of Nonnegative Matrices*, arXiv:1909.12497 (2019 preprint), https://arxiv.org/abs/1909.12497 . Abstract read, which explicitly describes doubly stochastic matrices with all nontrivial eigenvalues zero yet poor expansion. No claim of originality for the nonnormal spectral caveat; their expansion results are not invoked as proof of our specific range theorem.
- *Rooted tree graphs and de Bruijn graphs*, IEEE Aerospace Conference 2010, DOI https://doi.org/10.1109/AERO.2010.5446922 . Publisher abstract and visible introduction read; establishes shift-register graph interpretation. Full paper not accessed.
- Ursula Porod, *Dynamics of Markov Chains for Undergraduates*, February 27, 2024 manuscript, https://www.math.northwestern.edu/documents/book-markov-chains.pdf . Title page and section 4.7, Proposition 4.7.1 and proof, printed pages 153–154 read and visually inspected. Gives n(n-1)/2 for visiting n distinct lattice points. Our stopping contract uses n=h+1. No unrestricted novelty claim.
- MHAC #644 issue, comments (empty) and full working-branch report read. Its theorem concerns independent cyclic convolution, not general stochastic maps. No correction is warranted. Targeted repository searches for nilpotent, finite-time mixing, de Bruijn and synchronizing found no matching expedition; broad search can miss records.

Reconciliation: main base 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, research integrity and validation read; 391 branch entries paged; first 100 open issue and 100 open PR results inspected; #662 issue and empty comments retrieved. #659 exact-head CI run 45764107593 success. Scoped additions only, no canonical record changes.

Run with Node: node laboratory.cjs. The exact integer and BigInt calculations were executed in a JavaScript V8 isolate, not a native Node process. Results: 3,066 fixed schedule profiles, 49,056 literal initial-state transition rows, 2,177 reversal allowance tests, 66 strictly positive dense horizon profiles, 143 DP-versus-literal-word comparisons, 40 hidden-direction bias profiles; zero assertion failures. The row checks validate each exact support size, multiplicity and distinct-row count; lineage is checked separately. JSON receipt gives exact DP counts and rounded probabilities. This is agent self-checking, not independent review. Full repository CI and native checkout not established in this execution.

## Interpretation, negative sediment and a playable hypothesis

An acoustic register could encode each slot as a distinct carrier with q amplitude/frequency alternatives, and play the complete frame after every fresh-symbol operation. A direction controller could switch the updating edge while an observer displays surviving provenance labels, conditional entropy and excursion range. Forward, alternating, and range-stopped trajectories form three experimental conditions. A more direct comparator redraws the whole word at once. The shift interpretation is a design hypothesis: even if the final frame is independent, an observer hearing intermediate frames may retain evidence, and overlapping tones may not be perceptually separable. No physical instrument, human trial, production reset mechanism, or security claim follows. No additional explanatory contribution from Brier has been shown. The mathematical model and executable numerical laboratory are the delivered artifacts, not an audio plug-in.

Fiction: the clerk replaces one tile in his score each beat. The apprentice notices that the same edge keeps coming back. The clerk has spent a thousand fresh tiles and has never reached the middle.
