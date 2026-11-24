# The Resonator That Cannot Hear Its Neighbours

**Scope:** exploratory synthetic mathematics and an original sonification, issue [#388](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/388), 2026-11-24. GPT-6.2 assisted derivation, source reading, implementation and self-check; no independent reviewer or human listener. No priority claim. Not a frozen-protocol empirical result or production TTS implementation.

## Abstract

Two sixteen-node coupled instruments have identical spectra, all-time one-port return kernels, and identical distributions of all pair transfer kernels. Nevertheless, one contains eight four-way cliques and the other none. The difference survives arbitrarily sophisticated homogeneous nonlinear processing when only one fixed node is externally addressable. Two adjacent anchors suffice once the instrument permits a nonlinear intervention at every node and three rounds of propagation. If only linear propagation and anonymous memoryless readout are permitted, two anchors remain insufficient; three anchors forming a triangle suffice. These are distinct access models, not a single universal complexity bound.

## Graph construction and the linear obstruction

Take the vertex set Z4 × Z4. R (rook) joins different vertices that share a coordinate. S (Shrikhande) joins vertices whose difference belongs to {±(1,0), ±(0,1), ±(1,1)} modulo four. Both have 16 vertices and degree 6. In R, adjacent pairs share the other two vertices on their line and nonadjacent pairs share the two opposite corners of a rectangle. In S, the intersection of the six-element generator set with each of its 15 nonzero translates has size two (direct enumeration by the supplied lab). Thus both satisfy

A² = 4I + 2J, AJ = JA = 6J.

Every polynomial in A is therefore a linear combination of I, A and J. This extends to matrix exponentials and resolvents wherever defined, via convergence or spectral interpolation. Eigenvalues are 6 (multiplicity 1), 2 (6), −2 (9): the all-ones vector has eigenvalue 6; on its orthogonal complement A²=4I; trace zero fixes the remaining multiplicities.

A linear wave or diffusion model whose propagator is an analytic function of A has three classes of transfer functions: same vertex, adjacent and nonadjacent. Both graphs have 16 diagonal entries, 96 ordered adjacent entries and 144 ordered nonadjacent entries. Hence their individual return responses, global spectral summaries and anonymous pair-transfer multisets coincide at all orders. This is not a claim of identical physical room acoustics.

A port set P with its ordered induced adjacency matrix fixed has identical restricted kernels E_P^T f(A) E_P. Arbitrary causal linear driving at those ports cannot separate the candidates. Even nonlinear, adaptive feedback *confined to the ports* cannot break equivalence from the same initial zero state: identical impulse kernels imply identical responses to each identical sequence of inputs, so any deterministic controller receives the same history (or couple its random coins). A feedback instability does not create new graph information. The statement excludes graph-specific interior forcing, arbitrary hidden initial states and vertex labels as side information.

For up to three distinct ports every possible induced graph pattern occurs in both candidates, with identical unlabelled multiplicities (0,1,2,3 edges on triples: 96,288,144,32). Thus a matching three-port pattern is always ambiguous. Four ports forming a clique separate; this is an existence witness, not a guarantee that a blind four-port selection will distinguish. If all labelled pair responses are available, the adjacency matrix itself is revealed by the first step; the ambiguity concerns restricted or anonymous access.

## One-anchor nonlinear impossibility

Fix a root u. The partition into {u}, its six neighbours and its nine non-neighbours is equitable: the numbers of neighbours in each class of a node of a given class are the rows of

Q = [[0,6,0],[1,2,3],[0,2,4]].

For states constant within classes, propagation x -> Ax acts exactly as Q on the three class values. Any homogeneous pointwise function (possibly time dependent, with arbitrary vector-valued local memory and root-specific forcing), preserves that property; uniform initial state and a root-only input belong to the class-constant space. Induction gives identical quotient trajectories for R and S at every step, for arbitrary such nonlinear functions. The root readout, and even any permutation-invariant readout of the population of node states, agree because class sizes agree. This includes arbitrary repeated resets and adaptive root driving, as long as no other node becomes distinguished and the dynamics are deterministic or share only global randomness. Independent local stochastic forcing, edge-specific operations, access to edges between neighbours or a different initial state are not covered.

No amount of temporal depth over this access model recovers the missing adjacency among neighbours. This is an exact obstruction, not a convergence failure.

## Two-anchor constructive repair

Choose an adjacent pair u,v. Start with x=e_u+e_v and apply the following three propagation rounds with homogeneous nonlinearities:

```text
z = A x
c = z(z-1)/2        # pointwise: select common neighbours from z in {0,1,2}
w = c * (A c)       # pointwise product; retain c as a local state channel
y = A w
return y[u]
```

There are exactly two common neighbours. Both are neighbours of u, so the final scalar is y[u] = c^T A c, twice the number of edges among the common neighbours. In the rook graph the two are on the same line and adjacent; output is 2. In S the neighbours of any root induce a six-cycle (the generator set ordered as (1,0),(1,1),(0,1),(3,0),(3,3),(0,3)). There is no triangle in this induced cycle and therefore no K4 in S. Adjacent u,v cannot have adjacent common neighbours; output is 0.

This is an explicit arithmetic realization of a distinguishing experiment with two simultaneously addressable adjacent ports, root-only final readout, homogeneous internal operations, no direct interior sensor and finite local memory. The previous result makes two anchors optimal for this particular model, given a known adjacent pair. Locating such a pair is separate acquisition work. The 0/2 certificate is also exactly twice the number of four-cliques containing the edge, on any simple graph: a useful local motif counter even outside the pair studied here. Summing it over all undirected edges and dividing by 12 gives the total K4 count. This yields 8 versus 0.

For a nonadjacent pair the same output does not count cliques. In R all 72 nonedges yield 0; in S 24 yield 0 and 48 yield 2. Selecting an arbitrary pair is not a guaranteed separator. With unstructured labels, the first-root adjacency scan may itself require up to ten candidate probes to find a neighbour among the 15 other vertices (nine non-neighbours); concurrent anchor budget is not the total number of locations ever addressed.

Robustness in a limited noise model: replacing the polynomial selector by a threshold z>1.5 produces the exact same mask under additive first-round error strictly less than 0.5 per coordinate. With all remaining stages exact, bounded additive final readout error strictly below 1 separates the two outputs at threshold 1. This does not qualify arbitrary analog errors or physical hardware.

## Three anchors and anonymous readout

Another access model permits linear fields from selected ports, arbitrary pointwise functions of those fields at each vertex, and a permutation-invariant aggregate of resulting node trajectories, but forbids propagation after any pointwise nonlinear operation. With two ports, every linear field at vertex i is determined by (i=u,i=v,A_ui,A_vi). The multiplicity of every such joint category is fixed by adjacency of the pair and the SRG parameters. For an adjacent pair, outside the anchors, the categories (neither, only u, only v, both) contain (6,3,3,2); for a nonadjacent pair (4,4,4,2). Thus no such anonymous readout can distinguish matching pair types, even with multiple times and input waveforms. This includes arbitrary polynomial statistics, not only means and powers.

For three anchors u,v,w forming a triangle, the one-step fields a=Ae_u, b=Ae_v, d=Ae_w have product sum T = sum_i a_i b_i d_i. This counts common neighbours of the triangle. In R it equals 1, in S 0. All 32 triangles in each graph give their respective answer. Equivalently drive all three simultaneously and count vertices receiving three pulses. The distinction is carried by a third-order joint moment. Under the stated anonymous one-pass model, three anchors are optimal for the existence of a separating experiment, again subject to finding a triangle. If labels are retained across many distinct interventions, the lower bound is inapplicable.

The two-anchor internal propagation and three-anchor anonymous-readout results are not contradictory. The former lets a nonlinear selection create a new source field and asks how it travels; the latter only summarizes a fixed linear response.

## Executed laboratory and provenance

Run with Python 3.11+ standard library:

```sh
python laboratory.py results > execution.json
```

Native Python 3.13.5 was used. All assertions passed twice; the full JSON receipts were byte-identical on that runtime. The Git blob of the executed laboratory matched the retrieved committed blob b74cb717730a3a7b598c329fa44e725329d53709. A compact measured receipt is provided separately; the full receipt is reproducible, and records the audio hashes, kernel traces and pair/triple classes. No timings or independent replication are claimed.

| Test | Count |
|---|---:|
| Ordered adjacency/common-neighbour checks | 512 |
| Root/time kernel comparisons (13 steps × 16 roots × 2 graphs) | 416 |
| Unordered pairs | 240 |
| Unordered triples | 1120 |
| Four-vertex subsets | 3640 |
| Signed three-class quotient test states | 4000 |

The exhaustive pair census exposes an additional negative result: the adjacency relation alone determines the linear transfer, but does not determine the nonlinear witness for all nonadjacent pairs in S.

The audio is a sonification of normalized closed-walk counts (A^t)_uu / 6^t, not an acoustic simulation. Each value controls the amplitude of a tapered 250 Hz sine over 0.12 seconds. The thirteen linear slots are byte-identical. Appending the normalized nonlinear witness produces an audible-in-principle final tone versus silence. No listening test or psychoacoustic inference was conducted. The code generates four WAV files and hashes them; no third-party audio is used. PCM hashes depend on numerical/runtime details.

## Sources and relationship to prior work

- Laura Mančinska, David E. Roberson, Antonios Varvitsiotis, *Graph isomorphism: physical resources, optimization models, and algebraic characterizations*, Mathematical Programming 205 (2024), 617–660, online 2023, [DOI](https://doi.org/10.1007/s10107-023-01989-7). Open HTML, read the complete example and proof of Theorem 8.2 in §8; establishes the shared SRG parameters and K4 distinction in the context of quantum versus DNN-isomorphism. Not a source for our audio claims.
- Edwin R. van Dam and Gholamreza R. Omidi, *Directed strongly walk-regular graphs*, Journal of Algebraic Combinatorics 47 (2018), 623–639, [DOI](https://doi.org/10.1007/s10801-017-0789-8). Open HTML §§2.1–2.3, passages on walk counts and matrix identity. General algebraic background, not a study of acoustic sensing.
- Pál András Papp and Roger Wattenhofer, *A Theoretical Comparison of Graph Neural Network Extensions*, ICML 2022, PMLR 162:17323–17345, [proceedings](https://proceedings.mlr.press/v162/papp22a.html). Read appendix D, proof of Theorem 6.5, PDF page index 17 (text and page image). Their marked-node GNN argument distinguishes this very graph pair by a closely related common-neighbour test. This is direct prior conceptual overlap, not mere background. Our scope is translating the motif into explicit scalar propagation and distinguishing port access/readout regimes; no claim of novel graph-isomorphism result.
- [Shrikhande graph catalogue entry](https://jaanos.github.io/tables/graphs/Shrikhande.html), viewed excerpt (secondary discovery). The original S. S. Shrikhande 1959 paper, DOI 10.1214/aoms/1177706207, was identified via secondary records but not read; it is not used as verified primary evidence.

Access date 2026-11-24; source checks by the same AI agent. The mathematical statements are derived in this document, not attributed to these papers unless stated. The source search was bounded, not a systematic novelty audit.

## Exaptation and contrary cases

A diagnostic instrument should distinguish passive measurement diversity from active intervention capability. A one-port measurement may retain a rich spectrum and still say nothing about whether neighbouring relations form a particular motif. Adding nonlinear computation only at an observation terminal cannot create the lost relationship. Moving nonlinear computation *into* a network can break the invariance, but the position and independent addressability of its driving signals matter.

A possible musical instrument would expose three controls: anchor count and placement, the pointwise selector, and whether a selected response can become a new excitation. A performer first plays a return-kernel score in which two different patch networks sound identical, then turns a response into a new source and auditions the emergent difference. This is a design hypothesis, not a claim about listeners or physical networks.

Negative boundaries: full labelled transfer reveals adjacency; unequal local dynamics, spatially distinct initial states or stochastic node-specific drives may break the quotient; ports cannot be assumed adjacent without evidence; the K4 witness is not a general graph-isomorphism algorithm; no physical realization or perceptual equivalence has been established. The scope of measurement access is part of the sign, not a footnote to it.

Fiction: two technicians were given instruments that returned every test pulse with the same echo. One added increasingly elaborate filters to the meter. The other routed the pulse back through the instrument, allowing only chambers that had heard both sources to speak again. One instrument answered twice; the other said nothing. The original echoes had all been accurate.

## Checkpoint

Base main SHA 495a98ca12bae467a507031f04931aa4254b1866. Reviewed AGENTS, RAG, programme, runbook, integrity and validation; 253 branch names, 100 recent open issues and 100 recent open PRs returned, and targeted cospectral/Shrikhande duplicate search returned none. Existing graph and signal expeditions are distinct; #381's exact head CI was successful. New scope only, not dependent on those draft branches; no canonical records or manifests edited. Full repository validation and independent mathematical critique remain pending. Draft is intentionally unmerged until exact-head CI and review; no human experiment requested.
