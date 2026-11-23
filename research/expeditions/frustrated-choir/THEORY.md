# Signed relations, loop frustration and the portability of a contradiction

**Claim classes:** mathematical theorem for a stipulated finite model; executed synthetic result only when [EVIDENCE.md](EVIDENCE.md) records actual checks; interpretive cross-domain hypotheses; artistic convention. None is empirical evidence about human sound recognition or machine truthfulness.

## Contents

| Section | Contribution |
| --- | --- |
| [1. The graph in which every assertion is local](#1-the-graph-in-which-every-assertion-is-local) | Binary sign model and balance theorem proof |
| [2. Why an edge can sound innocent until it closes a walk](#2-why-an-edge-can-sound-innocent-until-it-closes-a-walk) | Streaming certificates and their limits |
| [3. The local-code gauge](#3-the-local-code-gauge-what-survives-when-every-node-renames-its-bits) | Switching invariance under local recoding |
| [4. The deliberately austere stereo score](#4-the-deliberately-austere-stereo-score) | Exact audio mapping and evidence boundary |
| [5. Counterexamples and failed inferences](#5-counterexamples-and-failed-inferences) | Failure cases for truth, blame, optimality and order |
| [6. Experimental and transfer boundary](#6-experimental-and-transfer-boundary) | Finite tests and conditional exaptations |

## 1. The graph in which every assertion is local

Let \`V\` be a finite set of named symbolic nodes. Each identified undirected edge \`e=(u,v,p)\` asserts that its endpoint labels, each in GF(2) = {0,1}, have XOR \`p\`. Thus

    x(u) XOR x(v) = p(e),       p(e) in {0,1}.

\`p=0\` means equal; \`p=1\` means unequal. This model permits parallel edges and loops. A loop with \`p=0\` is tautological; a loop with \`p=1\` is impossible. Two parallel edges can be consistent or contradictory. Each source assertion is merely represented, not endorsed.

The corresponding signed-graph convention is \`sigma(e)=(-1)^p(e)\`. An undirected closed walk \`C\` has sign \`prod(sigma(e)) = (-1)^(XOR of all p(e) over C)\`. The source of this well-established mathematical vocabulary is the signed-graph literature; see [SOURCES.md](SOURCES.md).

**Balance theorem (bounded formulation).** A finite undirected graph of such relations has a joint binary assignment if and only if every cycle has parity zero.

*Forward direction.* For any closed walk \`v0,v1,...,vk=v0\`, XOR all the edge equations. Each vertex variable appears an even number of times and therefore cancels. The XOR of all edge parities must be zero.

*Reverse direction.* In each connected component, choose a root label \`0\`. Propagate labels along a spanning tree via \`x(v)=x(u) XOR p(uv)\`. Every tree edge is satisfied. Any non-tree edge \`uv\` closes a cycle with its unique tree path; zero cycle parity means its parity equals \`x(u) XOR x(v)\`. Therefore all edges are satisfied. Self-loops are covered by a closed walk of length one and parallel edges by one of length two.

**Assignment multiplicity.** Every connected component has one unconstrained global inversion: switch all its labels from 0 to 1 or back. If the graph is consistent and contains \`c\` connected components (counting isolated vertices), there are exactly \`2^c\` solutions. Inconsistent graphs have none. None of the solutions proves which value corresponds to a real state without an external anchor.

The theorem is elementary graph algebra, not a newly discovered graph-theoretic theorem. Harary's structural balance result is an established predecessor, discussed explicitly by Zaslavsky (see Sources).

## 2. Why an edge can sound innocent until it closes a walk

The algorithm processes edges in a declared deterministic order. Before accepting the next edge, it finds the shortest path (fewest edges) connecting the endpoints through **previously accepted** relations. If no path exists, the edge joins components and is accepted. If a path exists, its XOR gives the already implied parity \`q\`.

- If \`q XOR p = 0\`, the edge is compatible; its complete cycle is recorded and the edge is accepted.
- If \`q XOR p = 1\`, the edge cannot join the existing accepted graph; the path plus edge is an explicit contradiction certificate and the edge is rejected.

At each step the accepted graph remains consistent, because connecting different components cannot introduce a cycle, and adding a same-parity edge cannot create an incompatible one. If the entire input is inconsistent, some edge must eventually be rejected: otherwise the final accepted graph would contain every edge and the theorem would guarantee satisfiability. Conversely, a rejected edge plus already accepted edges proves the full input inconsistent.

The certificate records the edge ID, ordered path vertices, path edge IDs, path XOR, declared XOR and cycle flux. \`verify_cycles\` checks edge sequence continuity, that each witness edge was previously accepted, and the actual XOR against the source edge table.

**This certificate is not necessarily the shortest negative cycle in the entire input.** It is shortest by edge count **in the accepted graph at the time of refusal**. It is not a unique explanation, an optimal repair, or a credibility ranking. A malicious first edge may become a privileged accepted premise and cause several later truthful edges to be refused.

## 3. The local-code gauge: what survives when every node renames its bits

Choose any binary function \`g:V->{0,1}\` and re-encode every vertex label by \`x'(v)=x(v) XOR g(v)\`. The corresponding assertion must be rewritten as

    p'(uv) = p(uv) XOR g(u) XOR g(v).

Along a closed walk the transformed flux is

    XOR_C p' = XOR_C p XOR XOR_C g(u) XOR g(v) = XOR_C p.

Every vertex touched by a closed walk contributes two endpoint appearances (counting multiplicity), and they cancel. Hence a closed-loop contradiction is invariant under local relabelling.

The transformation is also bijective on assignments: \`x\` satisfies the original constraints if and only if \`x'=x XOR g\` satisfies the switched constraints. Thus joint satisfiability and the number of complete assignments are unchanged.

This is the binary signed-graph operation often called **switching**, formally a local \`Z2\` coordinate change. It resembles gauge invariance, but there is no continuum field, no physical gauge potential, no new spin-glass result, and no asserted mental mechanism. The experiment uses a known combinatorial fact and a new, explicit sound mapping.

**Subtlety:** raw edge parities are *not* invariant. A recorder playing a note for each local edge sign could change its audible melody under harmless recoding. The choice to encode only closed-loop flux gives a sound that is invariant under these recodings by construction. This is the actual exaptation: audio can expose properties of relationships that do not depend on arbitrary local naming.

## 4. The deliberately austere stereo score

The renderer accepts an ordered list of cycle fluxes, never a free-form prose description. Each closed loop receives 0.60 seconds of PCM16 stereo at 22,050 samples/second with an original sine envelope. The left reference oscillator is 440 Hz. Right is 440 Hz for flux 0 (matched pair), and 466.16 Hz for flux 1 (a separated pair). Both use the same amplitude envelope \`sin(pi*(j+.5)/frames_per_note)^2\`.

A balanced square (parities 0,1,0,1) and frustrated square (0,1,0,0) have identical first three relations but different closure. Their recorded cycle-note lists are \`[0]\` and \`[1]\`, respectively. After switching the local convention at A, C and D, the frustrated graph has changed individual edge parities but its recorded notes remain \`[1]\`.

Therefore:

1. The frustrated and switched-frustrated WAVs are byte-identical under deterministic rendering.
2. The balanced and frustrated WAVs differ at the sample level.
3. The JSON witness identifies exactly which synthetic edge and path made the difference.

Byte-level uniqueness is not a proxy for human detection. Stereo reproduction, channel summation, headphones, masking, hearing, loudness, and context were not tested. The 440/466.16 Hz mapping is **not** a universal sign for error. There is no claim that listeners naturally hear a semitone as a contradiction, or even that the note is audible in a particular workplace.

The generator also renders `order_ab_first.wav` and `order_ab_last.wav` from the **same six-edge relation graph** in different assertion orders. Their loop-flux scores `[1,1,0]` and `[0,0,1]` are mechanically different, despite identical underlying constraints. This audible contrast is a deliberately adversarial demonstration that **the number of dissonant notes is not intrinsic contradiction severity**.

The renderer creates no musical quotation or reproduced recording. It is an authored procedural experiment.

## 5. Counterexamples and failed inferences

**No cycle is not true information.** Any tree of binary equal/different relations can be satisfied, regardless of who uttered those relations or whether the underlying phenomena exist. The instrument cannot determine whether the world's states match the symbolic nodes.

**A contradiction is not a liar locator.** In the frustrated four-cycle, changing any single one of the four edge relations restores consistency. The loop alone does not identify the defective statement.

**Greedy rejection is not a minimum edit set.** Consider ordered constraints:

    A-B different
    A-C same
    A-D same
    B-C same
    B-D same
    C-D same

The greedy stream rejects \`B-C same\` and \`B-D same\`, a total of **two** edges. An assignment making all four vertices equal violates only \`A-B different\`, so a globally optimal correction would change only **one** edge. No globally optimal graph-repair claim is made. Brute force validates this four-vertex counterexample.

**A subtle cycle-space warning.** For a graph with `m` edges, `n` vertices and `c` connected components, the number of emitted loop notes is always `m-n+c`—the GF(2) cycle-space dimension, even for self-loops and parallel edges. Each emitted cycle contains a newest edge that earlier emitted cycles cannot contain; this makes the emitted cycles linearly independent, and their count equals the dimension. They are therefore an **ordered, algorithm-selected basis**, not a unique canonical set of cycles.

The binary list of loop fluxes is the coordinate vector of the graph's cycle-sign functional in this chosen basis. A change of basis can alter the **number of ones** in that vector without altering whether it is the zero vector. For example, on the complete four-vertex graph with only `A-B different` and all other five relations `same`, reading `A-B` first gives flux notes `[1,1,0]` and two greedy rejections; reading it last gives `[0,0,1]` and one. Both input streams describe the same graph. **Do not score contradiction severity by the number or order of dissonant notes.** The only unconditional conclusion is the existence or absence of a nonzero loop flux under the declared binary model.

**Order matters.** Feeding the last frustrated-square edge first can move the rejected ID from \`e4\` to \`e3\`, even though the complete set is the same. Satisfiability is invariant to order; the streaming witness, acceptance decisions and resulting diagnostic narrative need not be.

**A loop does not create independent evidence.** If two relations copy one source or one sensor, the graph could have redundant edges; the analyzer has no provenance or statistical independence model. Redundancy does not confer warrant. T015 owns the independent-source alarm question, not X007.

**Unknown, weighted or asymmetric relations are not encoded.** Real beliefs are often graded, probabilistic, directed, time-indexed or context-conditional. Forcing these into same/different may create apparent contradictions by invalid modeling. A three-valued unknown cannot be silently recoded as zero.

**A consistent closed-loop checksum is not a cryptographic checksum.** An attacker can rewrite many parities to produce a consistent but false graph. This graph invariant provides no authentication, tamper evidence, origin assurance or inference of trust.

## 6. Experimental and transfer boundary

The independent oracle exhausts every possible assignment for at most sixteen vertices, while the main edge-stream algorithm does not enumerate assignments. The test suite checks all \`3^6=729\` simple four-vertex graphs (each edge absent/same/different) against the independent enumerator, then checks all \`2^4=16\` local switch masks for each of those graphs: 11,664 graph/mask combinations. Negative tests cover graph loops, conflicting parallel edges, forged certificates, input order, forest absence of cycles, invalid data and nonminimal greedy rejection. Actual execution status is recorded separately, not inferred from code being present.

Potential transfers worth investigating **only after a proper domain model exists**:

- **Multi-agent knowledge provenance:** relay a compact witness of mutually incompatible pairwise constraints rather than asking a language model to choose a winner by confidence.
- **Symbolic game systems:** detect impossible parity specifications from world-state flags whose local bit convention may vary by subsystem.
- **Patchable synth / modular network routing:** verify inversion-vs-preservation constraints around routing loops, making network inconsistencies playable without relying on exact module labels.
- **Research practice:** distinguish the state of an assembled, jointly inconsistent claim graph from the unsupported claim that one offending statement has been proven false.

The above are design hypotheses, not evaluated deployments. No corpus source was extracted, no accepted R006/R008 claim was amended, and no Track E/G inference is made. If a later prototype needs uncertain or temporal statements, this binary theory should be treated as a **lower-bound component** rather than stretched to explain the richer domain.

**Epistemic summary:** a loop can prove mutual incompatibility of stipulated binary constraints. It cannot tell who ought to be believed. The small synthesizer gives the contradiction a voice without pretending that voice is itself evidence.
