# The Score That Refuses Its Colours
## An expedition into relational notation and uncomposed refrains

24 November 2026 · exploratory humanities/art research · Refs #318

## Contents

- §1 — original thought experiment.
- §2 — bounded readings and locators.
- §3 — exact synthetic construction and proof.
- §4 — executed finite census.
- §5 — philosophical interpretation and objections.
- §6 — instrument proposal and transfer limits.
- §7 — reconciliation and next questions.

### 1. A composer writes only refusals

Two musicians bring instruments to an empty concert hall. The composer has written no pitches, but has drawn a line between two events and asks that they be different. Other lines follow. At first there is no sense in asking what the score sounds like; it does not yet possess a vocabulary. There is only a geometry of contrasts.

What if, after a performance, the composer hears a refrain that was never written? The musicians insist that it was compulsory. They can show why: their instruments supplied only three categories of sound and the written contrasts exhausted two of them.

This is not the familiar distinction between a determinate work and an improvisation. It is a narrower distinction between a *written constraint*, an *entailed constraint* and a *chosen realization*. An event may have been left unspecified without having been left free.

In ordinary software, a menu with three available items seems less expressive than one with four. But in this score the fourth item changes the meaning of a blank. With three items a blank can mean compulsory recurrence; with four it can mean a choice. No mark in the score has changed.

### 2. Source-located intellectual encounters

- Earle Brown, [Novara, 1962, composer program notes](https://earle-brown.org/work/novara/), paragraph defining open form. Brown explains that the material is fixed while its ordering and other performance decisions remain variable. Read the complete program-note passage, not the score. **Author claim:** the work retains its identity despite variability in form. **Interpretation:** a score can specify one dimension and delegate another; delegation need not imply an absence of identity. Our score reverses Brown's distribution of freedoms: temporal order is fixed, material labels are not. It is not an analysis or realization of Novara.
- David Cline, [Treatise and the Tractatus](https://doi.org/10.1017/rma.2020.5), Journal of the Royal Musical Association 145(1), 2020, pp. 119–166, abstract on Cambridge Core. Abstract only; no claim to have read the full article or Cardew's handbook. **Author claim:** Cline identifies affinities between early Cardew's approach to interpreting Treatise and Wittgenstein's account of propositions as pictures. **Interpretation:** the idea of preserving a relation across media makes a useful starting point, but our graph colouring is generally not an isomorphism: nonadjacent events may collapse onto one label.
- [Goodman's Aesthetics](https://plato.stanford.edu/entries/goodman-aesthetics/), Stanford Encyclopedia of Philosophy, revision 9 August 2017, §4.3, opening discussion and distinction between allographic/autographic works; secondary source, not direct reading of Languages of Art. **Source account:** Goodman connects notation, compliant realizations and the identity of artworks. **Interpretation:** our finite model has a decidable compliance predicate, but that does not establish an adequate criterion of identity for the artwork as experienced.
- William W. Gaver, Jacob Beaver and Steve Benford, [Ambiguity as a Resource for Design](https://doi.org/10.1145/642611.642653), CHI 2003, pp. 233–240. [Author-text PDF](https://studiolab.io.tudelft.nl/manila/gems/contextmapping/Gaver2003.pdf), printed p. 233 (PDF index 0), abstract and introduction; inspected text and page image. **Author claim:** ambiguity can promote interpretive engagement; the authors distinguish ambiguity in information, context and relationship, and explicitly limit this recommendation for clearly specified or safety-critical tasks. **Interpretation:** our exact finite underdetermination is only one possible resource for ambiguity, not a model of their full taxonomy.

Sources accessed 24 November 2026 by the executing ChatGPT agent. No independent human source verification, rights grant, whole-book reading, or empirical extraction is claimed. No source score or article reproduced. These notes are leads outside the frozen protocol, not additions to the selected evidence corpus.

### 3. A notation whose empty spaces have consequences

**Synthetic construction.** A graph has an event at each vertex and an inequality constraint on every edge. A performance assigns each vertex a categorical sound label from an available palette; adjacent vertices must receive different labels. No edge means no explicitly written restriction, not an instruction to use equal labels. Times and durations are separately fixed. Equality is exact label identity, not judged auditory similarity. A performance is valid exactly when it is a proper graph colouring.

Use two reference events A and B connected to each other, and four further events C,D,E,F, each connected to both references. Initially there are no other edges. The references occupy two different labels, so each further event must use one of the remaining q=k−2 labels, where k is total palette size.

The number of labelled realizations is k(k−1)(k−2)^4. For k=3, all four further events must share one label: a fourfold refrain is an implication of the palette and the graph, not an explicit repetition sign. For k=4, the four events can independently select one of two other labels. There are 16 such assignments for fixed anchors. If labels are considered interchangeable, these reduce to eight equality patterns: one all-equal partition plus seven partitions into two nonempty blocks.

This quotient is significant for compositional thinking but not a claim of auditory equivalence. Two patterns related by relabelling may use radically different sounds and possess different artistic effects. Conversely different labelled patterns can be perceptually indistinguishable.

Generalize to m further events with graph H of constraints between them. The count becomes k(k−1)P_H(k−2), where P_H is the ordinary chromatic polynomial (the number of proper labelled colourings). A partition of the m events into independent nonempty blocks represents a pattern of equality. If it has b blocks, it contributes the falling factorial (q)_b = q(q−1)...(q−b+1) labelled assignments for fixed anchors, or zero if b>q. Summing over admissible partitions gives an independent counting method.

A path C—D—E—F supplies a second witness. With four total labels there are only two available for these events; they must alternate. C and E must match; D and F must match; C and F must differ. The last inequality is as much an unwritten constraint as the first two equalities. With five total labels all three of these unwritten restrictions vanish individually.

**Spare-colour lemma.** Let a finite nonempty graph H have chromatic number χ and q≥χ+1. For any nonadjacent pair u,v, both equality and inequality are feasible (in possibly different colourings). Take a proper χ-colouring with a spare colour. To force equality, recolour both vertices with the unused colour; this preserves every edge because they are not adjacent. To force inequality, recolour u alone. In both cases all other assignments remain unchanged. This establishes the lemma. At q=χ it need not hold, as the path shows. The conclusion is pairwise: it does not say that arbitrary collections of independently feasible relations are jointly feasible.

The practical consequence is that a one-label surplus beyond the minimum guarantees local freedom for every unwritten pair. But it does not guarantee arbitrary global freedom. With four isolated events and two usable labels, every pair can be different in some realization, but all six pairs cannot be different together. To require global independence, one must specify an actual joint feasibility problem.

These are elementary graph-colouring constructions, not claims of mathematical novelty.

### 4. Executed census

Run `node lab.js` (no dependencies). The same lab function was executed in the ChatGPT JavaScript tool before being serialized as the committed source. It independently enumerates all labelled assignments to six vertices and all restricted-growth strings for partitions of four events; compares full pattern sets, labelled counts, pair classifications and the spare-colour lemma. It treats infeasibility separately from universal equality or inequality, avoiding vacuous truth masquerading as a performance instruction.

| Total labels k | Feasible spoke graphs (of 64) | Feasible graphs with at least one unwritten forced relation |
|---:|---:|---:|
| 3 | 1 | 1 |
| 4 | 41 | 31 |
| 5 | 63 | 6 |
| 6 | 64 | 0 |

Executed 4,294,784 candidate assignments across 256 configurations, with 2,396 assertions. These are computational checks, not observations of listeners.

| No internal edges | Labelled realizations | Equality patterns |
|---:|---:|---:|
| 3 labels | 6 | 1 |
| 4 labels | 192 | 8 |
| 5 labels | 1,620 | 14 |
| 6 labels | 7,680 | 15 |

| Path C—D—E—F | Labelled realizations | Equality patterns |
|---:|---:|---:|
| 3 labels | 0 | 0 |
| 4 labels | 24 | 1 |
| 5 labels | 480 | 4 |
| 6 labels | 3,240 | 5 |

The full set of six pair relations is audited, not just recurrence. The lab's numerical output is generated on demand rather than added as a registry JSON file.

### 5. Interpretation — The blank that changed its meaning

A musical score is not merely a message which passes from composer to performer. It may be an arrangement under which the performer and the instrument jointly determine what the message can mean. In the contrast score the composer supplies a graph, the instrument supplies a finite alphabet, and the performer supplies a colouring. Each participates in generating the refrain. None is independently sufficient.

This suggests an alternative to the familiar opposition between fidelity and interpretation. Sometimes interpretation is the work of discovering obligations implicit in the situation, rather than choosing among already announced freedoms. Conversely a performer can obtain real freedom by changing the material circumstances without revising the written score.

A useful objection is that the composer could have foreseen all of this. In that case the refrain is not uncomposed in an intentional sense. The phrase *uncomposed refrain* here denotes an absent explicit equality mark, not the absence of authorial intention. A second objection is that insisting on exact compliance may make the score sterile. That is possible. A performer who breaks the graph might produce a more compelling work. Compliance is not a ranking of artistic quality, and an improvising musician is not an optimization routine.

The conceptual experiment may also be inverted. Suppose the artist takes away a sound every time the musicians discover a new distinction. Eventually the instrument imposes a recurring shape, even though the written score keeps becoming more elaborate. An audience could hear restriction without knowing its cause. This is a score that becomes increasingly specific through the removal of resources.

### 6. Exaptation — The Contrast Loom

Proposed modular synthesizer/notation interface, not production implementation.

- Event layer: timed events, sound objects, spatial positions, optional gesture data.
- Constraint layer: editable equality/inequality, then optional directed relations (higher pitch, longer duration); the latter require a different solver and do not inherit the colouring theorem.
- Palette layer: live available sound-object IDs; capacity and audibility are separate. A performer can introduce or withdraw a timbre without rewriting the graph.
- Implication inspector: mark explicit constraints, derived forced relations, genuinely free pairs and infeasibility. When possible show two feasible assignments witnessing each free relation; for a forced relation provide an explainable proof or small unsatisfiable core.
- Audition layer: A/B two witness realizations, freeze the currently sounded prefix, solve only future events and never quietly rewrite the archive. The live palette change is transactional: proposed, previewed, committed or refused with reason.
- Aesthetic override: explicitly leave the score's rules; record the violation rather than masking it as compliance.

The interface should allow the player to compose both the constraint graph and the degree to which it can be fulfilled. A palette slider could become a structural modulation source rather than a filter knob. A contradiction can be staged as a silence, or as an explicitly labelled rule-breaking performance. Never equate solver failure with human failure.

**MHAC transfer hypothesis:** distinguish the semantic categories that must be discriminable from the acoustic resources used to realize them. A designer may accidentally make some unspecified mappings obligatory when available categories are insufficient. This is a design hypothesis for a discrete symbolic model, not evidence of discrimination by people. Test it with independently defined categories, controlled masking and actual confusion matrices only after the relevant gates. In an operational message, do not deliberately preserve ambiguity about action, target or hazard. In a gallery, deliberate ambiguity about interpretation can be the work.

**Revision criterion:** if listener studies show that equal IDs and different IDs do not predict the relevant discriminability, abandon the simplistic graph-to-palette model for that task. If performers find the inspector distracts from performance, keep the analytical view optional and compare against ordinary score rehearsal. No users have been recruited or tested.

### 7. Departure and checkpoint

Read live main AGENTS, RAG, README, research README, programme, runbook, integrity, validation and freeze record; reviewed 75 recent PR titles and 50 open issue titles before selecting this expedition. The neighbouring expeditions concern novelty, genre, attribution, context, timing and code ambiguity; this contribution instead concerns how a restricted palette entails absent score relations. The live programme is still in progress and its frozen authorities are unchanged. Issue #318 was opened specifically for this work; no prior comments existed at branch creation. Base: 495a98ca12bae467a507031f04931aa4254b1866. Additive branch mhac-318/score-refuses-colours. No shared manifests, production code, participant data or third-party source files changed. Single AI agent; no independent reviewer. Full repository qualification is separate from dedicated checks.

Next rabbit hole: allow the palette to be different for each event (list colouring). The common spare-colour argument then fails unless the unused label is available to both vertices. A score for incompatible instruments might reveal how the location of affordances changes the very meaning of unmarked relations. Another direction: replace categorical inequality by measured separation with uncertainty, but first decide what it means for two timbres to be distinguished rather than assuming a universal acoustic metric.

The original performance score and fictional afterword are in SCORE.md.
