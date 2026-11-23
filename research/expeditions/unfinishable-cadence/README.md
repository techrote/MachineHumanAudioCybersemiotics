# The Unfinishable Cadence

Issue #211 · 2026-11-23 · Original bounded mathematical and artistic expedition, AI-assisted; no human participants or independent review.

## The anomaly: a song has not yet become a law

A machine repeats an audible pattern for ten beats. Does the next beat necessarily follow the apparent pattern? The question resembles a child's induction problem, but turns into an exact theorem once the admissible worlds are specified. With no bound on source complexity, any finite pattern has both repeating and nonrepeating continuations. With a genuine period promise, a finite observation can instead settle the entire future *symbolic stream*. Neither proposition implies the listener knows the source's mechanism, intentions or reliability.

This is not spectral homometry (#199), which discards order in a feature map, nor branching trace equivalence (#205), which concerns available choices. It concerns *how long* and *which samples* must be observed before two distinct, phase-aligned periodic streams can no longer masquerade as each other. #187 treats absence as an epistemic problem; here erasure locations are known and the data channel has an explicit error budget. #209 asks which distinctions a code must preserve for later questions; here the question and model class are specified already. No change to those expeditions or canonical research records.

## Formal model and proof

Let p,q be positive period promises (not necessarily minimal periods). A stream A is defined by symbols a[0..p-1], B by b[0..q-1]; index t starts at zero. T is a finite set of distinct nonnegative observation indices. All indices are available to the receiver; unknown clock drift, insertions, deletions and phase resets are outside the model. Unknown initial phase can be absorbed into the arbitrary words if the clock itself is shared.

Make a bipartite multigraph with p A-vertices and q B-vertices, adding an edge from A[t mod p] to B[t mod q] for each t in T. Different observation times may give parallel edges. Let g=gcd(p,q). The full graph over one lcm(p,q) cycle has g components: by the Chinese remainder theorem an A and B vertex are adjacent precisely when their indices agree modulo g. Each component is complete bipartite, with p/g and q/g vertices.

Define D(T;p,q) as the minimum Hamming distance on T between two streams with these periods that differ at *some* infinite-stream index. This exclusion of identical streams is essential; otherwise the minimum is trivially zero.

**Proposition (derived here; no priority claim):** D is the minimum nontrivial edge-cut size among the g full-graph components, counting parallel observed edges and permitting zero cuts in disconnected observed subgraphs.

Proof: Every assignment of symbols to the vertices defines a pair of streams. Two infinite streams differ iff at least one full component has a nonconstant assignment. Choose one symbol occurring in that component and take the proper nonempty subset of vertices bearing it. Every observed cut edge contributes a mismatch. Thus every distinct stream pair costs at least the minimum cut. Conversely assign binary 0/1 labels across a minimizing cut and label all other components uniformly zero. At least one full edge crosses the cut (the full component is connected), so the streams differ eventually; the observed cost is exactly the cut size. This proves the result even for any alphabet of size at least two. The binary witness requires no statistical independence assumptions.

A perfect-data receiver can distinguish every distinct cross-family stream pair exactly when D>0. With at most r adversarial substitutions per possible received history, the two Hamming balls intersect iff their centers differ at most 2r times: necessity is the triangle inequality; sufficiency follows by assigning roughly half the differing coordinates to each center. Therefore uniform separation of distinct cross-family streams is possible iff D>2r. This says nothing about distinguishing two candidates *inside* a single period family unless that family pair is also checked (use p=q, or examine all promised period pairs). It cannot distinguish identical output streams with different mechanisms or declared periods.

### Recovering the classical sharp prefix bound

Let p<=q. The first q observed edges connect each B vertex once to an A vertex. For the next p-g edges, each B vertex indexed i=0..p-g-1 receives another edge, effectively joining A[i] to A[(i+q) mod p]. The full permutation i -> (i+q) mod p consists of g cycles, one per residue. The omitted g consecutive indices p-g..p-1 remove one edge from each cycle (a loop for a singleton cycle), leaving each residue connected. Thus at n=p+q-g, the observed graph has exactly the g full components, each a tree: there are p+q vertices, n edges and g components. Removing its last edge disconnects one component, so D=0 at n-1 and D=1 at n. This proves the sharp Fine–Wilf prefix threshold independently of the cited historical theorem. It also handles p=q and divisibility.

For k complete cycles, the observed graph is k parallel copies of each full edge, yielding D=k min(p/g,q/g): the edge connectivity of a complete bipartite graph K(a,b) is min(a,b). To see this, a single minimum-degree vertex realizes the upper bound; for a cut taking x left and y right vertices, the cost x(b-y)+(a-x)y is at least min(a,b) for any nontrivial split (minimize the linear expression in y at its allowed endpoints). Partial cycles can be useful before that bound; the oracle computes them directly. D is nondecreasing under adding known observations, but elapsed time without samples has no guaranteed effect.

## Experiment and original score

[cadence.cjs](cadence.cjs) is a Node.js 18+ standard-library executable. From the expedition directory run:

    node cadence.cjs
    node cadence.cjs cadence.wav

It enumerates cuts with a fixed vertex label to remove complement duplicates; independent brute-force enumeration compares all binary periodic-word pairs across every mask of the classical threshold prefix for p,q in 1..5. This is deliberately an exponential small oracle (p+q<=24); a polynomial minimum-cut algorithm is a possible engineering replacement. It emits a 22-tick stereo 8 kHz, 16-bit PCM WAV using two original square-wave pitches and per-tick envelopes; no third-party music. Both channels have exactly equal samples through tick 9 and differ at zero-based tick 10. The renderer is a symbolic demonstration, not a study of listener discrimination. The file is generated locally, not committed as binary.

Actual execution on 2026-11-23: the exact JavaScript function bodies subsequently committed in 0467229b008fa7d3deecd99c4acc31f32180bbcb were executed in a V8 tool isolate; Node CLI/file-write wrapper not executed there. 1,270 masked cases matched brute force and witness validation; 100 ordered period pairs p,q in 1..10 matched the sharp prefix boundary; malformed duplicate-index input refused. Audio PCM compared sample by sample for first channel difference. Results:

| Substitution budget per candidate | Earliest contiguous observed ticks for p=5,q=7 | Minimum distance there |
|---:|---:|---:|
| 0 | 11 | 1 |
| 1 | 21 | 3 |
| 2 | 35 | 5 |
| 3 | 49 | 7 |

The noiseless witness is A=(0,1,0,1,0), B=(0,1,0,1,0,0,1). Their first ten symbols are equal; their eleventh differs. Even one arbitrary error per candidate almost doubles the necessary observation horizon for this pair of period promises. These are worst-case exact model results, not estimates of environmental noise or optimal auditory duration.

Negative results: the classical threshold alone cannot certify error-robust separation (distance just 1); having many observations all at the same residue pair can still leave a zero cut; no finite prefix can establish an unrestricted future law. A period bound cannot be inferred by merely observing a matching prefix. Conversely no additional evidence is needed to distinguish a pair whose observed histories already differ by more than 2r under these premises. Do not present a sufficient model-wide threshold as necessary for every individual received word.

## From cadence to machine testimony

A proposed diagnostic distinction: "observed recurrence" reports the prefix, "compatible with period p" states a model fit, "guaranteed continuation under contract C" invokes an independently warranted invariant, and "unresolved among C's candidates" identifies remaining ambiguity. These are different speech acts in practice even if they share the same rhythmic earcon. A repeated sound can report repeated evidence without asserting repeated law. A machine could expose the number of independently useful samples or the residual cut certificate rather than recite elapsed time as if it were evidential weight.

An analogous acceptance-reporting failure: ten successful runs do not prove the eleventh succeeds. A test harness that *actually* restricts the system to a verified finite model can sometimes settle the corresponding model property; those guarantees do not survive unspecified environment changes. For unrestricted infinite traces, eventual occurrence of an event cannot be refuted by a finite absence prefix; a stipulated finite deadline changes the property. This is a design hypothesis and a formal analogy, not an empirical claim about language use, user trust or TTS.

## Source ledger and adversarial limits

- N. J. Fine and H. S. Wilf (1965), *Uniqueness theorems for periodic functions*, Proc. AMS 16, 109–114, DOI [10.1090/S0002-9939-1965-0174934-9](https://doi.org/10.1090/S0002-9939-1965-0174934-9). Bibliographic metadata verified through discovery records; publisher page failed to open. **Original article not read.** Classical statement corroborated by Rankin, not attributed to a read primary passage.
- Stuart A. Rankin (2009), [Fine-Wilf graphs and the generalized Fine-Wilf theorem](https://arxiv.org/abs/0906.1780), arXiv:0906.1780. Read accessible rendered abstract and introduction (including graph setup), beginning of §2. Primary research for its generalized graph treatment; secondary exposition for the 1965 theorem. Our bipartite observation multigraph differs in construction from its finite-word distance graph; no exhaustive novelty search performed.
- Bowen Alpern and Fred B. Schneider, [Defining Liveness](https://www.cs.cornell.edu/fbs/publications/85-650.pdf), revised February 1985, Cornell TR 85-650. Read abstract and §§1–3 through the discussion of leads-to properties; visually inspected printed pp. 2–3 (PDF indices 3–4). Their definitions concern infinite execution sequences and finite prefixes, not auditory perception. The application here is a separate interpretation.

No claims of original discovery of Fine–Wilf, min-cut, error-correcting distance, induction or monitorability. The integration and executable score are expedition artifacts. The error model assumes equal indexed symbol reliability and arbitrary substitutions within a hard bound; real acoustics involves synchronization, continuous features, correlated noise and psychoacoustic variation. No human tests, effect size, device specification or validated alarm policy. No source redistribution beyond original summaries. Single GPT-6.2 research agent and V8 execution; no independent human verification.

Base at reconciliation: 495a98ca12bae467a507031f04931aa4254b1866. Reviewed repository instructions, RAG, programme, runbook, research integrity, validation, recent issues/PRs and active branch names. Additive expedition path only. Canonical records and human gates untouched.

## Fictional afterword: the clockmaker's apprentice

The apprentice heard the clock strike twice in the same manner and wrote down a law. The clockmaker asked how many different clocks could have made those sounds. She wrote down two clocks. He asked what would happen if a bell had been missed. She added a third, then a fourth. By evening she had drawn a map of wires between clocks that had never existed. It was a peculiar score: each line joining two bells was a claim of sameness, and each broken line was a place where the future could change.

At last she found the wire which, if cut, would permit two clocks to agree on every sound she had heard. She did not cut it. She played both clocks at once and waited for the first disagreement. The next morning she did not write down a law. She wrote down the conditions under which a law could be heard.
