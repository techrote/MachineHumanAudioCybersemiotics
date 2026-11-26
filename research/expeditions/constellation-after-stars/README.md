# The Constellation That Arrives After the Stars

26 November 2026 — MHAC exploratory humanities/art expedition, issue #634. AI-authored interpretation, synthetic mathematics and original score; not selected evidence, peer review or a claim of listener behavior.

## An astronomy of listening

A room contains four sounds. A composer listens and finds three that seem to belong together. She draws a line through them and calls the figure a constellation. The fourth sound has not been erased; it has simply become a star outside this particular figure.

The next day a statistician arrives and asks whether the figure is surprising. The composer supplies its exact coordinates. The statistician calculates how unlikely those particular coordinates would be, then announces a discovery.

The error is not in the calculation of the fixed coordinates. It is in substituting a question conceived after the encounter for the procedure that actually found the figure. Aesthetic discovery is allowed to do this; a probabilistic claim about discovery must account for it.

There is a third participant, the instrument maker. She wants the lines to be playable. A line joining three sounds becomes a modulation trajectory; a second line creates another trajectory. A piece can then have a material layer, an atlas of possible relations, a history of selected relations, and a new sounding layer constructed out of those relations.

This is not an argument that chance lacks meaning or that art should be statistically corrected. The value of a found pattern is not its rarity under a null model.

## Source encounters (located, limited)

All accessed by a single AI assistant on 2026-11-26, public web. No complete book, formal empirical screening, human verification or independent appraisal.

- International Astronomical Union, [The Constellations](https://www.iau.org/IAU/Astronomy-FAQs/Constellations.aspx), sections "IAU and the 88 Constellations" and "Constellation Figures": the modern IAU definition is a bounded sky region, not an official stick figure; figures and asterisms can cut across boundaries. The boundary system approved in 1928 was published in 1930. Institutional explanatory account, selected paragraphs read. Interpretation: a partition, a pattern and a physical relationship are different objects. The many culturally distinct sky traditions are not interchangeable with this invented musical grid.
- John Cage, [Atlas Eclipticalis](https://www.wisemusicclassical.com/work/65356/Atlas-Eclipticalis--John-Cage/), publisher programme note, read; [John Bickerton, 2025 interview](https://johnbickerton.com/fanfare-magazine-interview-july-2025/), passage on the star atlas and remote performance, indexed excerpt read. Bickerton describes Cage's overlay of staves on Bečvář's star charts. The publisher permits many ensemble configurations and partial performances. Original score not inspected. A direct musical precedent for borrowing a sky and making it into a score, not evidence about this proposed instrument's usability.
- Garry L. Hagberg, [Wittgenstein's Aesthetics](https://plato.stanford.edu/entries/wittgenstein-aesthetics/), §4.2, paragraph beginning "However, calling it that": the author interprets context as changing the function of an otherwise structurally identical musical phrase. Selected paragraphs, secondary philosophical reading, not a complete reading of Wittgenstein. It cautions against equating an extracted motif with its role in the original material.
- Persi Diaconis and Frederick Mosteller (1989), [Methods for Studying Coincidences](https://doi.org/10.1080/01621459.1989.10478847), JASA 84(408), 853–861. [Accessible copy](https://gwern.net/doc/statistics/bias/1989-diaconis.pdf), printed p.853, abstract and §1, page image inspected. They discuss multiplicity of possible endpoints among several explanations of surprising coincidences. No claim that these principles explain every perceived pattern. This directly motivates separating preselected and searched rhythmic patterns.
- Diana Deutsch, Trevor Henthorn and Rachael Lapidis (2011), [Illusory transformation from speech to song](https://pubmed.ncbi.nlm.nih.gov/21476679/), JASA 129(4), 2245–2252, DOI 10.1121/1.3562174. Indexed abstract only (direct PubMed retrieval was blocked): authors report changes in classification after repeated identical spoken phrases, with disrupted effects under certain manipulations. Tamara Rathcke, Simone Falk and Simone Dalla Bella (2024), [Why Does Speech Sometimes Sound Like Song?](https://journals.sagepub.com/doi/abs/10.1177/20592043241266060), indexed abstract and introduction: authors report results challenging one attention-based account and propose a priors-based explanation. No full-text appraisal. This is a specific perceptual phenomenon, not proof that the following arbitrary rhythm motifs will emerge perceptually, or that listeners can recognize a hidden generator.

## The finite sky (exact construction)

Use twelve cyclic pulse positions 0 through 11. A carrier is a subset S of k positions, sampled uniformly without replacement for the null calculation. For a in 0..11 and spacing d in 1..D, define a triple T(a,d)={a,a+d,a+2d} modulo 12. D is restricted to 1..5, so every triple has three distinct points. Deduplicate the unordered triples; translations of d=4 produce only four distinct triples. These are deliberately narrow, equal-spacing definitions of a motif; no claim of perceptual salience.

The preselected test looks for T(0,1). The searched test looks for any member of F_D, the family of triples. For a fixed triple the probability is binomial(9,k-3)/binomial(12,k) (zero for k<3). The expected number H of distinct matching triples is |F_D| times that probability, by linearity, irrespective of dependence. The probability of at least one hit is not this expectation, nor is it obtained by treating overlapping triples as independent.

For k=4, there are 495 carriers; nine contain the preselected triple. Searching successively larger families gives the following exact counts, computed by laboratory.cjs:

| D | Family size | Carriers with any hit | Total hits across carriers |
|---:|---:|---:|---:|
| 1 | 12 | 96 | 108 |
| 2 | 24 | 168 | 216 |
| 3 | 36 | 267 | 324 |
| 4 | 40 | 291 | 360 |
| 5 | 52 | 351 | 468 |

The fixed-triple probability is 9/495, about 1.82%; the widest search probability is 351/495, about 70.91%. There is no contradiction. One calculation asks about a particular shape at a particular location; the other asks whether any eligible shape occurs. A third question, about the number of discoveries, has its own distribution: for D=5 the counts for H=0,1,2,4 are 144,240,108,3 respectively; H=3 never occurs in this stratum. Three carriers attain four hits; the result is combinatorial, not psychological.

The score witness {0,3,6,10} contains exactly one triple in F_5, {0,3,6}, and misses the fixed T(0,1). It is authored, not a random sample. The oracle enumerates all 4096 masks per ceiling, checks a separate position-triple enumeration against bitmask containment, checks rotational invariance and validates totals by combinatorics. See [receipt](RECEIPT.md).

### A stronger distinction: capture versus composition

A uniform null is a stipulated generator, not an adequate model of all rhythm. Meter, tempo, physical articulation, repeated patterns, musical training and selection over many bars all alter the relevant comparison. If a musician scans ten bars and chooses the one with the greatest number of matches, a one-bar probability is not a calibration of the ten-bar selection. Only under independent uniformly generated bars does the no-hit probability multiply. Likewise, a low null probability is not the posterior probability of conscious intent. Authorship, causation and artistic value require other evidence or judgment.

One can deliberately sample from a conditional ensemble: select only carriers with H=0, only those with H=1 or those with H=4. This is not a test of chance anymore; it is a compositional use of a known distribution. It produces a meaningful "constellation density" control without changing the onset count. A new extension would include motifs defined by intervals, cross-voice correspondences, timbral near-matches and phrase length. Each enlargement requires recomputing the declared null; the present counts do not transfer.

## An instrument that reads after it writes

The Constellation Loom is a proposed sequencer in which an immutable carrier and an editable relation graph coexist. In live mode a bounded event scanner discovers exact motifs, saves their original event IDs, and triggers a derived voice. It does not overwrite the carrier. The artist can retain, rename, reject, or combine discovered relationships. In retrospective mode previously selected lines become a new score. To hear the consequences rather than merely admire the graph, route every line to a resonator, an FM pair, or a three-event envelope.

The scan must remain comprehensible: a strict mode commits a single template before the next bar; a free mode allows all 52 triples; a curated mode permits explicitly authored lines not in the family. Different modes create different kinds of artistic relationships, not different grades of moral or aesthetic worth. A fixed onset count is not a guarantee of equal perceived complexity.

Proposed VSTi: a twelve-step percussion and modal synthesis grid, with locked carrier, pattern-family control, derived motif bus, deterministic seeded generation, and density-conditioned randomization. Proposed VSTfx: MIDI-driven (or explicit transient annotations) motif extractor with a dry path, separately audible generated accents, bounded one-bar lookahead and documented latency. The exact oracle concerns symbolic onsets; acoustic onset detection, jitter, polyphonic interpretation, real-time DSP, host compatibility and firmware are not implemented. A CYD touchscreen could show the ring, points and editable chords on a second layer, without interpreting the screen as verified telemetry.

## Critical and artistic consequences

A found motif may be aesthetically powerful precisely because it was not intended. A perfectly ordinary pattern may become important through rehearsal, naming or ritual. Conversely, a rare shape may be musically inert. The calculator should have an off switch: there is no reason to rank works by surprise.

The IAU analogy is also imperfect. Its regions have a coordination purpose and its figures have histories. Our grid is a fictional, culturally uncommitted construction, not a model of how people see the sky. Cage's work supplies precedent, not authorization to claim novelty or to copy his score.

MHAC hypothesis (unvalidated): an operational interface that announces a discovered correlation could distinguish the scan family, whether the query was predeclared or exploratory, and independent source evidence. Compare a conventional explicit text receipt against optional sonification; preserve ground truth, source lineage, actual action obligations and source dependencies. Measure false causal attribution and task correctness only in separately authorized future research. An ordinary query log and statistical correction may be sufficient; no special cybersemiotic mechanism is established. Do not map a pleasing coincidence to an alert severity or suppress independent warnings. This is different from #58's actual source-lineage question: even perfectly independent sources can generate a searched coincidence.

## Scope and reconciliation

Read live AGENTS, README, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY and VALIDATION. Checked 60 recent PR titles and 40 open issue titles, targeted issue searches for coincidence, constellation, pareidolia, apophenia, graphic scores and other concepts. #524 covers traversal of spatial scores; #612 covers changes in sampling units; #58 covers independence of evidence; this work holds the population fixed and changes a searched pattern family. Initial hysteresis, ordinal and phase-lift routes were abandoned after overlapping work was found. Search coverage is bounded, not a novelty proof. Issue #634 and comments read (no comments at intake). Base 495a98ca12bae467a507031f04931aa4254b1866. No shared manifests, registry records, protocol amendments, real listeners or production implementations. Draft for independent integration. No license grant.

## Fiction — A map that has learned to sing

The astronomer gave the composer a chart without lines. The composer found a swan in it. A second composer found a broken ladder.

The instrument maker fitted both figures with strings. When the swan sounded, nobody was asked to abandon the ladder.

A statistician calculated the frequency of swans in imaginary skies. The composer asked whether he could also calculate the price of a string.

He could not.

She bought a string anyway.
