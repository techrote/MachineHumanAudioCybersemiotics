# The Command That Crosses Another

*Research expedition #332, 24 November 2026. Formal derivations, synthetic computation, interpretive exaptation and original fiction; no human or production validation.*

## The anomaly

A four-component sound has three stipulated meanings, A=0000, B=1111 and C=0011. A transition from A to B can be made by turning on each component once. If the two low-order components change first, the instantaneous word is exactly C. No noise or incorrect static encoding occurred. The receiver has encountered a perfectly valid third message that the sender did not select.

A different update order avoids C: 0000 → 0100 → 1100 → 1101 → 1111. There are 24 possible orders, four of which pass through C. The problem is not confined to a fragile code. Repeating each coordinate m times gives three words 0^(4m), 0^(2m)1^(2m), 1^(4m), with minimum Hamming distance 2m. The static correction radius grows without bound, yet a monotone transition between the outer words can still pass exactly through the middle one. Increasing static error protection alone does not repair asynchronous semantics.

## Model and established connections

Let C be a subset of the n-dimensional binary cube, with M >= 3 distinct codewords. The receiver observes a discrete snapshot after any individual coordinate changes. A transition from a to b flips exactly the differing coordinates once, in any order. Coordinates not differing never change. There is no interpolation overshoot, clock error, analog mixing, persistence requirement or knowledge of intended endpoints at the decoder. A third word c is an unintended activation. Old and new meanings are allowed; an application requiring exactly-once action needs additional state.

The reachable snapshots I(a,b) form the Boolean subcube of all mixtures of endpoint coordinates. Every snapshot is reached by some monotone shortest path. Therefore no third codeword occurs under **any** order iff C is a 2-frameproof code, equivalently a general-position set in the hypercube. A code with **some** safe order for each pair is instead a mutual-visibility set. These are existing mathematical objects, not new names for new coding-theory discoveries. See Fernandez et al., Definition 1; Korže and Vesel, section 4; Axenovich and Liu, Definition 1.1.

The latter authors' 2026 Theorem 1.2 gives a mutual-visibility set of size strictly greater than (14/75)2^n for each n. For comparison, the following elementary universal-safety bound needs no asymptotic coding-theory result. Split the coordinates into two parts L,R of sizes floor(n/2),ceil(n/2). For every codeword c, at least one projection must be unique among codewords: otherwise there are distinct a,b, one agreeing with c on L, the other on R. They must be different from each other, since agreeing on both would equal c. Then c belongs to I(a,b), forbidden. Counting unique projections gives M <= 2^floor(n/2)+2^ceil(n/2). This is not claimed to be the best bound.

Even without the 2026 theorem, take all words of one fixed Hamming weight floor(n/2). For any distinct pair, remove the old-only ones first, then add the new-only ones. Every internal word has strictly smaller weight, so no third codeword is encountered. This gives binomial(n,floor(n/2)) scheduled words, at least 2^n/(n+1) by the binomial theorem. Thus controlling the transition order permits an exponentially larger alphabet than universally safe unordered transitions in this ideal model. This is an operational reading of the established distinction, not a claim about actual human auditory perception or the cost of coordinating the order.

## Exact isolation margin

For distinct a,b,c define

    g(a,b;c) = number of coordinates i where a_i=b_i != c_i
             = (d(a,c)+d(b,c)-d(a,b))/2.

The minimum distance from c to I(a,b) is exactly g. Proof: on fixed coordinates, disagreements are unavoidable; on free coordinates choose c's value independently. The second expression follows by summing the coordinate contributions to the three Hamming distances. In particular g=0 is the known frameproof obstruction.

Let t be the radius of the receiver's acceptance balls and e the maximum number of adversarial observation bit errors per snapshot. An unintended activation of c is possible during the transition iff g <= e+t. Necessity: if x in I and observed y satisfy d(x,y)<=e and d(y,c)<=t, triangle inequality gives g<=e+t. Sufficiency: take x attaining g and move from x towards c by min(e,g) coordinates. The resulting y belongs to both balls. This proves possibility of membership in the third acceptance ball; to infer a unique decoded label, require disjoint radius-t balls or state the tie policy. If stable endpoint correction is required, impose t>=e and minimum pair distance >2t separately. Including endpoints in I is intentional; with those static conditions they cannot trigger a third ball.

Consequently define lambda(C)=min g over all distinct triples with a,b unordered. Universal transient third-label exclusion holds exactly when lambda>e+t. With equal error and decoding radii e=t, it requires lambda>=2e+1.

Static minimum distance is a different observable. In the binary simplex code of length seven and eight messages, pair distance is four, so any one-bit error on a stable word can be corrected. Yet lambda=2. Concrete integer words (LSB first as in the executable): a=0, b=85, c=102. The intermediate v=68 is on I(a,b); it differs from c in two bits. One bit error yields y=70, within one bit of c and uniquely decoded as c. Thus even a perfectly frameproof noiseless code with optimal static geometry can fail when its ordinary error correction is activated mid-transition.

A conservative decoder that simply refuses every non-codeword avoids this particular one-bit acceptance expansion, but also loses the promised static correction capability. The right solution is not determined by distance alone.

## Sharp fixed-alphabet margin

For M>=3, n coordinates, write z_i and o_i for the number of zeros and ones in column i. Sum g over every unordered endpoint pair and distinct target (3 binomial(M,3) instances). Each column contributes

    binomial(z_i,2)o_i + binomial(o_i,2)z_i
      = z_i o_i (M-2)/2
      <= floor(M^2/4)(M-2)/2.

A minimum cannot exceed the mean. Therefore

    lambda(C) <= floor(n floor(M^2/4)/(M(M-1))).

This bound is sharp at an explicit infinite sequence of lengths for every M. Construct a code with one column for every subset of floor(M/2) of the M message labels; a label's bit is its membership in that subset. Put w=floor(M/2), n0=binomial(M,w). For a fixed distinct triple, separation counts binomial(M-3,w-1) + binomial(M-3,w-2) = binomial(M-2,w-1), using the convention that out-of-range binomial coefficients vanish. Thus all g are equal to n0 w(M-w)/(M(M-1)), exactly attaining the average bound. Repetition attains every positive multiple of n0. All pairs are distinct and equidistant. No assertion of attainability at every other length is made.

For M=2^k, k>=2, a far shorter optimum is the binary simplex code: columns are indexed by all nonzero v in F2^k and message x has bit x dot v. Length M-1, pair distance M/2. Given three distinct labels a,b,c, a+c and b+c are distinct nonzero vectors, hence independent over F2. Exactly M/4 choices of v give both dot products 1; none is zero. Therefore lambda=M/4 and the bound is attained, also under repetition. This is a familiar code used here for a distinct transition qualification question. No mathematical priority is claimed for the averaging argument or designs.

Equality in the unrounded mean bound requires every column maximally balanced and every triple gap equal; otherwise some term in the two inequalities is strict. For any triple, d(a,b)=g(b,c;a)+g(a,c;b). Equal gaps therefore imply equidistant words with pair distance 2 lambda. For these optimal constructions a static correction radius is lambda-1 but a same-radius transient guarantee only floor((lambda-1)/2). Roughly half the correctable errors disappear from the transition guarantee.

| Messages | Simplex length | Static radius | Equal-radius transient guarantee |
|---:|---:|---:|---:|
| 4 | 3 | 0 | 0 |
| 8 | 7 | 1 | 0 |
| 16 | 15 | 3 | 1 |
| 32 | 31 | 7 | 3 |

For arbitrary M, the upper bound implies no unordered transition can guarantee e=t if 2e+1 exceeds it. At the specified lengths the balanced-column construction attains that guarantee. This is a sharp statement for the toy, not a general noisy-channel capacity theorem.

## Path control, chance and the guard coordinate

Let D be the set of differing coordinates, and represent each intermediate word by the subset S of D already flipped. Mark a subset forbidden if its word is within e+t of some third command. Let F(S)=0 for forbidden S, F(D)=1 if allowed, and otherwise F(S)=sum_{i in D minus S} F(S union {i}). Backward evaluation gives the exact number of safe orders, with F(empty)/|D|! the probability of a safe order under a uniform random permutation of coordinate changes. The model assumes all orders are equally likely only for this probability, not for the worst-case theorem.

A single third word c in I(a,b) at distance k from a is visited by exactly k!(|D|-k)! orders. Its visit probability is 1/binomial(|D|,k). For multiple forbidden words, summing visit probabilities gives the expected number of visits, NOT the probability of any false activation; paths can visit several. The recurrence supplies the latter without independence assumptions.

Full even parity in four coordinates has eight valid words, all statically separated by at least two bits, but no safe shortest path from 0000 to 1111: every path reaches another even word at its second step. Conversely the three-word initial example allows 20 of 24 orders. A scheduler can be sufficient, but not for every code.

A different repair is a staged guard. Append g guard coordinates, enabled 1^g, disabled 0^g. Require an acknowledged barrier between disabling all guards, changing payload, and enabling all guards. During payload changes any disabled snapshot is at distance at least g from every enabled word. Thus g>e+t suffices to exclude all enabled acceptance balls, even for arbitrary payload changes. It is necessary for uniform exclusion in this specific guard architecture when a payload may coincide with a valid word: the two balls can meet if g<=e+t. In the outer stages the payload is fixed at one endpoint; other labels remain excluded if their payload distance exceeds e+t. Old/new activation is allowed, and the guard does not itself prove exactly-once semantics.

For exact noiseless snapshots one extra bit suffices, independent of alphabet size, **but only with the phase barrier**. An unsequenced guard can arrive late and leave the third command enabled. With e=t=1, three guard coordinates suffice under the same assumptions. This exchanges spatial redundancy for sequencing and confirmation, not an unconditional free capacity improvement. A lost acknowledgement, simultaneous changes, correlated errors beyond the bound, or a receiver interpreting the guard as a payload channel invalidates the contract.

## Computational and acoustic record

The committed CommonJS laboratory was executed in a JS isolate before committing. It checks the distance formula against explicit intervals, the noise condition against explicit pairs of snapshots, and safe-order DP against every explicit shortest path for all >=3-word codebooks of dimensions 2–4. The receipt is deterministic. Counts refer to exact enumerations, not observations of human listeners.

| Quantity | Count |
|---|---:|
| Endpoint-pair/third-label interval comparisons, n=2–6 | 141,732 |
| Explicit noise-ball comparisons, n=2–3 | 2,796 |
| Codebooks, n=2–4, M>=3 | 65,623 |
| Path enumeration vs DP comparisons | 1,967,742 |
| Balanced-design triple checks | 990 |
| Simplex-design triple checks | 16,740 |
| Guard noise comparisons | 2,304 |

No assertion failed. Exhaustive maxima (for n=2, no universal set of size at least three, but any pair works):

| n | Universal-safe max | Scheduled-safe max | Scheduled-only codebooks of size >=3 |
|---:|---:|---:|---:|
| 2 | 2 | 3 | 4 |
| 3 | 4 | 5 | 134 |
| 4 | 5 | 9 | 19,572 |

These are independent small finite re-enumerations of existing graph parameters. They are not claimed as previously unknown optima. The full 4-cube witness for scheduled size nine is in the receipt. Large-n optimal margins at arbitrary lengths, probability-constrained alphabet design, stochastic delays, robust scheduling and constrained hardware barriers remain open here.

The original **Threshold Organ** renders one 100 ms slot per word, five independent integer square-wave oscillators at 8 kHz sampling, amplitude 1000 per active component, phase reset per slot. Four payload oscillators and a fifth guard tone are used. No recording of a real room or listener is involved.

| Score | FNV-1a | Bytes |
|---|---|---:|
| Unsafe transition | b037a809 | 8044 |
| Controlled safe transition | 0e37eab9 | 8044 |
| Staged guard transition | b84ae0e9 | 11244 |
| Intended C | a3c7518d | 1644 |
| Transient C | a3c7518d | 1644 |
| Enabled C | 54f1720d | 1644 |
| Disabled C | a3c7518d | 1644 |

The intended and transient single slots are byte-identical; enabled and disabled C differ. FNV-1a is a reproducibility fingerprint, not authentication; bytewise equality was asserted. Run with Node using `node laboratory.cjs`; optional argument is a directory for WAV outputs. The filesystem wrapper and full repository CI were not executed in the initial isolate. No auditory recognition or perceptual equivalence beyond the identical digital bytes is inferred.

A speculative performance design separates the players responsible for a sound's endpoints, the order of changes, and the permission for the intermediate sound to count as an utterance. The timbre can traverse a forbidden sign while the authority channel disclaims it. A listener might hear an unintended sign regardless; this design needs perceptual tests and is not a safety implementation.

## Source ledger, interpretation and project boundary

- Marcel Fernandez, John Livieratos, Sebastià Martín, *Frameproof codes, separable codes and B2 codes: Bounds and constructions*, Cryptography and Communications 16, 481–506 (2024; online 2023), [DOI](https://doi.org/10.1007/s12095-023-00682-y). Read HTML introduction and section 2 through Definition 1 and Lemma 2 on 24 November 2026. Their fingerprinting setting provides the descendant formalism, not evidence about acoustic interfaces.
- Danilo Korže, Aleksander Vesel, *General Position Sets in Two Families of Cartesian Product Graphs*, Mediterr. J. Math. 20, 203 (2023), [DOI](https://doi.org/10.1007/s00009-023-02416-z). Read HTML introduction and section 4 (definition, Proposition 4.1, SAT formulation and qualification of exact small cases). The hypercube relation to (2,1)-separation is explicit. Did not use the uninspected numeric table as evidence.
- Maria Axenovich, Dingyuan Liu, *Visibility in Hypercubes*, Graphs and Combinatorics 42, 38 (2026), [DOI](https://doi.org/10.1007/s00373-026-03025-9). Read HTML abstract, section 1 including Definition 1.1 and Theorem 1.2. Used the theorem as an attributed source claim; its hypergraph proof was not reconstructed.
- Additional discovery lead: *Mutual and total mutual visibility in hypercube-like graphs*, [DOI](https://doi.org/10.1016/j.amc.2024.129216). The full-text redirect failed; not used as decisive evidence. The small optimum table here comes from exhaustive computation.

Interpretation: the intended sign is not necessarily the sign instantiated during a change. A component-level process may manufacture a valid sign with no corresponding act of selection. This is an analogy to semiotic uptake, not a claim that human interpretation is a memoryless Hamming decoder. The evidence a recipient needs might include a transaction boundary, endpoint intention, an authority channel, or a sequence rather than a snapshot. The repository's #246 protected distinctions concern static class distance, and #224 concerns variable-length live decoding; this expedition instead isolates the within-transition geometry of a fixed-length parallel alphabet. No production interface or normative policy follows automatically.

Suggested receipt fields: codebook/version, intended endpoint IDs, coordinate-update model, allowed schedule family, third-label isolation, decoder policy/radius, error budget, exact safe-order count or refusal witness, barrier evidence, and separate acknowledgement of any requested action. Negative result: a guard changes the observational contract and cannot erase an action that already occurred.

Reconciliation: read live AGENTS, RAG, programme, runbook, integrity and validation; inspected open issues/PRs and paginated branch inventory, and #246 issue/comments and report passage. Main observed at 495a98ca12bae467a507031f04931aa4254b1866. Prior #325 is draft with successful observed exact-head CI. New issue #332 read back with no comments. Only this expedition directory is edited; no changes to frozen tracks or shared manifests. One ChatGPT agent conducted derivation, source reading, coding, tests and self-review; no independent reviewer or participant. Refs #332; keep open for exact-head repository qualification and independent critique.

## Fiction: the silent conductor

The conductor requested that four shutters be opened. Each shutter had its own attendant. Two attendants obeyed more quickly than the others.

The instrument announced that the room was closed.

The repairman inspected its notes and pronounced them perfectly formed. The conductor inspected the score and found no such instruction. Neither was mistaken.

The next day the conductor installed a fifth shutter. Its sound did not tell the room what to do. It told the room when the other shutters had finished telling it.

The musicians complained that it ruined the silence between instructions. The clerk replied that the silence had never been empty. It had been an instruction the conductor had not written.
