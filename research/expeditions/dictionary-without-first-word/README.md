# The Dictionary Without a First Word

**23 November 2026 · Refs #212 · Original bounded mathematical, computational and artistic expedition.** No new human data, no formal promotion to the MHAC evidence registry, no claim to have solved symbol grounding. Base: `495a98ca12bae467a507031f04931aa4254b1866`. AI-assisted research, implementation and self-check by ChatGPT; no independent human or external review.

## The anomaly: a dictionary with perfect relationships and missing names

A machine and a technician each possess a complete map of five channels arranged in a ring. The machine calls them a,b,c,d,e; the technician uses physical socket numbers 0–4. Every pairwise adjacency is known without noise. The machine can specify a uniquely distinguishable tone for each *symbol*; every received tone can be decoded perfectly back to that symbol. But the parties have never agreed which socket corresponds to which symbol.

There are ten equally structurally admissible alignments (five rotations and two orientations). A trusted statement “a is socket 0” leaves two. “Select b” still admits sockets 1 and 4. This is not acoustic confusion, an ambiguous phoneme, an unobserved event chronology, or a version migration. Both dictionaries are perfectly known; the missing datum is the correspondence between their domains.

A contrary case matters as much. For an asymmetric relation graph with exactly one isomorphism to the known physical graph, no *additional* explicit pairing is needed to recover the correspondence. That does not make abstract symbols intrinsically meaningful: the physical graph already provides a grounded observational scaffold. A false shared graph assumption or a wrong physical measurement can produce a uniquely wrong answer.

The productive question is not “how much meaning does sound possess?” but “what external identifications are indispensable, given a particular relational model and a particular intended operation?”

## Mathematical account: admissible maps, stabilizers and exact questions

Let G and H be finite simple undirected graphs on n vertices, respectively abstract symbols and known physical ports. Both are exact, complete and assumed to be isomorphic. A candidate binding is a bijective edge/nonedge-preserving map f:G→H. Given trusted anchors (s,f(s)) for symbols s in S, retain only consistent bindings.

Pick one consistent binding f. All unanchored alternatives have the form f∘g where g is an automorphism of G: f inverse composed with another binding is an automorphism, and the converse follows by composition. The remaining alternatives after anchors are precisely f composed with the pointwise stabilizer Aut(G)_(S). The mapping is unique exactly when that stabilizer contains only the identity. Nonisomorphic inputs or inconsistent anchors have no candidates; this is contradiction, not a success with an empty action set.

A set S is determining precisely if it intersects the moved support of each nonidentity automorphism. The smallest such set is the established graph determining number (also called a base size for this action). Exhaustively testing subsets in increasing cardinality gives a finite exact algorithm. The paper by Boutin identified below defines this concept; this report claims neither discovery of determining sets nor new general graph theory.

**Exact adaptive-query theorem in this model.** Suppose a query names an abstract vertex s and an oracle returns its physical identity f(s), at unit cost, exactly and without affecting the world. Any successful decision-tree leaf has queried a determining set: otherwise a nontrivial stabilizer element yields a second consistent binding following the same path, contradicting guaranteed identification. Consequently every successful branch requires at least the determining number of distinct queries. Querying any known minimum determining set in advance achieves that lower bound on every branch. Adaptivity therefore cannot reduce even the best-case count for a policy required to identify every admissible binding. It may help outside this restricted query model, e.g. variable costs, noisy observations, restricted query access, arbitrary subset questions, nonuniform plausible candidates, or a narrower success criterion. The theorem is not a statement about all learning or repair.

**Task quotient.** For an intended symbol v and declared physical action function A, collect {A(h(v)): h is a consistent binding}. A nonempty singleton warrants the same action in all admissible worlds; multiple values require further information or abstention in the guarantee model. An empty set is inconsistent evidence. Full dictionary identification is sufficient but not always necessary. For a five-vertex path P5, reversal moves the ends but fixes the centre. The centre is uniquely actionable before any pairing. Pairing the centre with itself supplies no new discrimination; pairing an end resolves the entire dictionary. In contrast every single vertex pairing in the five-cycle C5 leaves a reflection, and any two distinct vertex pairings suffice. No single transposition is an automorphism of C5: this is a counterexample to detecting ambiguity merely by finding twin vertices.

**More relations do not always mean less ambiguity.** P5 has two automorphisms; connecting its two ends to make C5 gives ten. This does not contradict monotone evidence accumulation. Replacing one untyped edge relation with a new one changes the structure, rather than retaining the original as a separate constraint. If two independently typed relations are retained and both must be preserved, the allowable group is their intersection and cannot grow. Proposed engineering analogy: maintain typed relation layers and evidence versions rather than flattening them into an untyped connectivity graph. A more connected summary can be less identifying.

## Enumeration and adversarial checks

[oracle.py](oracle.py) constructs all vertex permutations through n=6 and evaluates their action on edge bitmasks. It chooses the least remaining labelled graph, removes its entire isomorphism orbit, and weights the representative by the orbit size. The orbit-stabilizer identity and disjointness are asserted for each class. Every labelled mask is accounted for, not independently evaluated as a new representative. The six-vertex census is:

| Minimum exact anchors | Labelled graphs | Isomorphism classes | Labelled graphs with no twin transposition |
| ---: | ---: | ---: | ---: |
| 0 | 5,760 | 8 | 5,760 |
| 1 | 16,920 | 48 | 7,560 |
| 2 | 8,244 | 56 | 504 |
| 3 | 1,680 | 30 | 0 |
| 4 | 162 | 12 | 0 |
| 5 | 2 | 2 | 0 |
| Total | 32,768 | 156 | 13,824 |

Across n=1..6 the program covers 33,867 labelled masks and 208 isomorphism classes. The eight rigid six-vertex classes contrast with none at sizes 2–5. In the six-vertex labelled population 8,064 graphs have no twin transposition yet still require anchors. The 12 labelled five-cycles are included in the twinless, two-anchor five-vertex cell. Neither the total nor the frequencies estimate natural language, industrial networks or audio-interface populations. Equal weighting over labelled edge masks is a combinatorial design choice; uniform weighting over isomorphism classes gives different frequencies.

[test_oracle.py](test_oracle.py) includes a separate explicit minimax decision-tree search for all 52 isomorphism classes through n=5. It does not call the determining-set routine when calculating its policy cost. Costs agree with the base size, and relabelled graph cosets and single-anchor filtering are verified. Other tests cover the wrong-anchor example, task-invariant centre, C5, contradictory anchors, nonisomorphic inputs, invalid indices, repeated undirected edge input and PCM witnesses. This is an implementation cross-check, not independent human peer review.

The implementation is intentionally brute force and limited to n≤6. The single-action helper returns a set; callers must separately refuse empty and nonsingleton sets. It does not solve noisy graph alignment, discover the physical graph, or authenticate the anchor provider.

## Experimental instrument: The Unnamed Patchbay

Imagine an instrument whose score consists solely of relational statements between oscillators. The first score emits motifs for the edges in abstract-label order. The second emits a tone representing the intended physical port of a selected symbol. In the anchored pentagon example, the two remaining bindings give the same relational score but different physical-target scores.

The standard-library generator writes four deterministic 8 kHz, signed 16-bit, mono PCM WAVs. Two complete relation files are byte-identical; the two target files differ. This is a designed digital witness, not a perceptual experiment. The relation score deliberately omits the physical binding; the target score deliberately accesses it. It makes the missing information tangible but cannot establish listener discrimination, musical quality or the usability of a real port-mapping scheme.

Reproduce from this directory:

    python -m unittest -v
    python oracle.py --wav-dir /tmp/mhac212-wav

Execution receipt: Python 3.13.5, all six test methods passed, 0.238 s observed in the local container; full census and WAV generation succeeded. Exact local source Git blob IDs, checked against fetched repository blobs:

- oracle.py: 8633e15dbb7e6f610f7e055af779ab1e13614714
- test_oracle.py: 212d8cbd22de28685bebec3de86ac5cb32c82acb

Generated WAV SHA-256 (not committed; regenerate with the script):

- relations-a.wav and relations-b.wav: a1aa08253c561a47b7fcbc9ad698f6383a5f613cf6e3b93370e70500c05c63ed
- target-a.wav: 8979cecac994679acca59035211508160f2ae489950daa729b07c2ac65eb1979
- target-b.wav: ea7772cb660c684a914817bb04435cb3806ed9456fe285cb970995903de25e04

Candidate instrument extensions: an oscillator network with a mutable physical patch map; a score whose events are orbit-invariant until a performer supplies a physical anchor; and a composition in which each newly identified channel breaks a symmetry, making formerly equivalent motifs diverge. These are artistic proposals, not measured findings.

## Source discipline, exaptation and the first word

Primary sources consulted on 23 November 2026 via web:

- Stevan Harnad (1990), *The Symbol Grounding Problem*, Physica D 42, 335–346, [DOI](https://doi.org/10.1016/0167-2789%2890%2990087-6). Read the [author-hosted HTML](https://www.southampton.ac.uk/~harnad/Papers/Harnad/harnad90.sgproblem.html) abstract and sections 1.2, 2.2–2.3, 3.1–3.3 (the retrieved passage through the zebra example); publisher DOI direct fetch returned 403, so no claim of verified publisher full-text access or reading of its tables/figures. Harnad distinguishes discrimination, category identification and compositional symbolic representation. The dictionary argument targets intrinsic grounding, not merely graph isomorphism. A unique correspondence between two graphs is a narrower engineering result, conditional on an already identified physical structure. The earlier [R008 preparatory Harnad note](../../analysis/comparisons/R008-HARNAD-SYMBOL-GROUNDING-PREP-20261110.md) likewise separates intrinsic and communicative grounding. This expedition neither duplicates its broader reconstruction nor promotes it.
- Debra L. Boutin (2006), *Identifying Graph Automorphisms Using Determining Sets*, Electronic Journal of Combinatorics 13(1), R78. [Journal abstract and metadata](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v13i1r78), [DOI](https://doi.org/10.37236/1104). Read abstract only; it defines determining sets and identifies the associated minimization problem. No claim to have read its full proofs or to improve its bounds.
- Boutin, *Determining Sets, Resolving Sets, and the Exchange Property*, Graphs and Combinatorics 25, 789–806 (issue date 2009; publisher records online publication 10 February 2010), [DOI](https://doi.org/10.1007/S00373-010-0880-6). Read publisher abstract only; its explicit distinction between determining sets and distance-resolving sets matters here. A distance signature is a different measurement protocol from obtaining a trusted name pairing. No new theorem about metric dimension is asserted.

No source PDF or third-party audio is reproduced. Source access and interpretation are limited to the locations above; no source registry, manuscript, frozen protocol or claim stage changes. Graph theory here is established mathematics with an original illustrative application and self-derived finite checks. The earlier X002 frame ambiguity, T012 mixed dictionary versions, #197 identity drift, #201 selective clarification and #209 late-context coding are adjacent but distinct: this expedition assumes unchanged exact graphs and no channel error, with uncertainty only about their cross-domain binding.

**Candidate engineering transfer.** Consider an agent rebuilding a device topology or a software dependency graph after a migration. A structurally correct inferred mapping may preserve every observed relationship while swapping two physical ports or service identities. Report the candidate orbit or mapping set; use trusted identity checks chosen for symmetry-breaking power; distinguish “mapping unique under current assumptions” from “mapping independently physically verified”; and inspect only the uncertainty that actually affects the requested operation. If physical identifiers are already present, this additional process may be redundant. If the assumed physical graph is wrong, this process is insufficient. The smallest determining set under exact complete data is not necessarily the cheapest or safest real procedure.

**Fictional afterword: The unnamed patchbay.** There was a synthesizer in a room whose sockets had been worn smooth. Its manual listed every connection, every adjacency and every interval, but not a single inscription could be found on the instrument. The apprentice learned the complete score. The master asked for the voice immediately clockwise from the first. The apprentice asked which direction the manual faced. Neither had made an error reading the notes. They had simply arrived at the place where the dictionary needed its first word. The master touched a second socket; the music acquired a direction. This passage is fiction, not an account of a historical instrument or a cognitive result.
