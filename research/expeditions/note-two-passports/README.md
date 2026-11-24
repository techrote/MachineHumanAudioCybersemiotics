# The Note That Has Two Passports

Exploratory expedition, 24 November 2026 — Refs #350. Original interpretation, elementary mathematics and score design; not selected empirical evidence, production TTS, or an assertion of theoretical novelty.

## Two offices of musical citizenship

Imagine two conservatories that use the same continuously tunable oscillator. The first issues a passport to every pitch and all its octave transpositions. The second recognizes triple-frequency transpositions. Each has a perfectly usable internal definition of sameness. A cultural exchange programme decrees that the passports are interchangeable, and that the administrative relation of sameness is transitive.

The surprising result is not simply that the two systems disagree. If all allowed substitutions are made and the resulting classification is continuous, no nonconstant pitch classification survives at all.

This is a formal consequence of stipulated operations, not a claim that musical cultures are mutually unintelligible. The institutional failure is not plurality; it is the suppression of the reason for a particular equivalence. Instead of asking whether two notes are the same, ask: for which purpose, under which transformation, and with what remainder?

A note could be a frequency, a named scale degree, a class modulo a register convention, a physical act, a remembered event or the beginning of an instruction. A machine can preserve one while discarding another. A single note ID should not impersonate all of them.

## Source encounters and limits

- C. S. Peirce, “Prolegomena to an Apology for Pragmaticism” (1906), pp. 505–506, CP 4.537, [transcription](https://www.jfsowa.com/exgraphs/peirceoneg/prolegomena.htm); type/token/Tone paragraph consulted in imperfect OCR transcription; cross-checked against David Liebesman, [Types and Tokens](https://plato.stanford.edu/entries/types-tokens/), §1 (2026 revision). Peirce distinguishes repeatable significant form from a particular instance and adds a category of indefinite significant quality. Here the proposed pitch passport is a rule for grouping tokens; it is not a reconstruction of Peirce's entire sign theory. Two identical frequencies may still be distinct token events.
- Jacoby, Undurraga, McPherson, Valdés, Ossandón and McDermott, “Universal and non-universal features of musical pitch perception revealed by singing,” Current Biology 29 (2019), 3229–3243.e12, [DOI](https://doi.org/10.1016/j.cub.2019.08.020), [open manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC9907018/). Consulted Summary, Results subsection “Octave equivalence – chroma matching” and Discussion. The authors report different octave-specific sung reproduction patterns between their US and Tsimane' groups despite relative interval reproduction in both. Their Discussion explicitly retains production/perception coordination and developmental alternatives. This does not show absence of all octave perception in any population, nor that physical octave cues are invented, nor that tritave equivalence is universal. No numeric effect extraction or appraisal attempted.
- “The Bohlen-Pierce Clarinet: Exploring a New Tonality,” The Clarinet 46/3 (June 2019), [ICA article](https://clarinet.org/the-bohlen-pierce-clarinet-exploring-a-new-tonality/), historical account and “Creation of the BP Clarinet” section. The 3:1 repetition interval and clarinet's twelfth overblowing make a material counterexample to the presumption that every useful scale must be octave-periodic. This is a secondary practitioner history, not a primary priority adjudication. No acoustic measurement or claim that a clarinet has exclusively odd harmonics.
- Loui, Wessel and Hudson Kam, “Humans Rapidly Learn Grammatical Structure in a New Musical Scale,” Music Perception 27 (2010), 377–388, [DOI](https://doi.org/10.1525/mp.2010.27.5.377), [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/20740059/). Abstract-level only; attempted PMC opening met a browser challenge. The abstract reports recognition, generalization and preference effects following exposure to artificial Bohlen–Pierce melodies. Not evidence that an arbitrary equivalence convention can be learned, or that learning entails liking. Compare Loui and Wessel (2008), [abstract](https://doi.org/10.1177/102986490801200202), which describes different outcomes for grammar generalization and item preference under different exposure sets. A new musical language is not automatically an accessible operational code.

All passages consulted 24 November 2026 by one AI-assisted author. These are exploratory reading notes, not protocol-controlled extraction or independent review. The 2026 SEP revision is contextual reading, not an amendment to the programme cutoff or corpus.

## Exact model: when the two passports are merged

Define f ~2 g iff g/f is an integer power of 2, and f ~3 g iff g/f is an integer power of 3, for positive real frequencies. These are two distinct equivalence relations. Their intersection is equality, since 2^a = 3^b for integer a,b requires both zero by unique factorization. Their union is generally not transitive: f ~2 2f and 2f ~3 6f but f is related to 6f by neither rule individually. The smallest equivalence relation containing both relates f to f*2^a*3^b. This is the join, not the union or intersection.

Put x = log2(f/f0). The join identifies translations by the additive group Z + log2(3) Z. The number log2(3) is irrational by the same unique-factorization argument. For completeness: partition the unit interval into M equal bins and consider M+1 fractional parts of multiples of log2(3). Two lie in a common bin, so a nonzero group member has magnitude less than or equal to 1/M. For any target real displacement, integer multiples of that group member approximate the target within 1/M. Since M is arbitrary, the group is dense. Therefore every equivalence class is dense in log-frequency space.

If a continuous real-valued label L is invariant under both rules, L is constant along each dense orbit and hence constant everywhere by continuity. A continuous map to any Hausdorff label space obeys the same conclusion. Even a finite label map not assumed continuous must be constant if every label is locally constant; more generally if a finite partition has at least one class with nonempty interior, that class must be the entire space because every orbit intersects that interior. Arbitrary discontinuous labels can distinguish exact orbits; they are not prohibited. A physical finite-range instrument need not have every exact intermediate transformation available. Within [f0,6f0), however, the step f -> 3f -> octave-fold(f) is available for f in [f0,2f0). Its positive iterates form an irrational rotation on the octave circle. The dense forward orbit follows from the same small-step argument (a positive iterate approximates either direction around the circle, and its positive multiples form an arbitrarily fine net).

The earlier [comma expedition](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/287) studied drift from incompatible just intervals and the scheduling of reanchoring; here the object is the identification relation itself, not frequency correction. This is standard irrational-rotation arithmetic applied to a synthetic semiotic contract, not a new theorem about auditory perception.

### Finite temperaments are a different contract

On an N-step octave grid, round the tritave to the nearest integer step, then reduce modulo N to obtain s = round(N log2(3)) mod N. The generated relation has gcd(N,s) components: multiples of s modulo N form exactly the subgroup of multiples of gcd(N,s), by Bézout's identity. Each component has N/gcd(N,s) notes. Thus a grid can appear to preserve distinct categories solely because of quantization.

| N | Rounded tritave step mod N | Classes after merging |
|---:|---:|---:|
| 12 | 7 | 1 |
| 19 | 11 | 1 |
| 24 | 14 | 2 |
| 31 | 18 | 1 |
| 53 | 31 | 1 |
| 72 | 42 | 6 |
| 96 | 56 | 8 |
| 120 | 70 | 10 |

The 24/72/96-step survivors are residue classes, not evidence of stable perceptual categories. Adding finer resolution need not monotonically increase the number of classes. An actual 13-step equal division of the tritave is a different tuning construction; the octave grids here approximate the tritave for the purpose of a controlled comparison.

The [oracle](oracle.cjs) enumerated all 7,259 combinations of N=2..120 and s=0..N-1; breadth-first graph components matched the gcd formula at every one of 583,219 vertex visits. For 128 exact tritave-fold steps, numerator and denominator identities, range and pairwise uniqueness were checked with BigInt. 599,118 assertions passed in V8. Cents are illustrative floating calculations, not exact assertions about gaps.

| Steps | Distinct visited pitches | Final displacement from root (cents) | Largest circular gap (cents) |
|---:|---:|---:|---:|
| 1 | 2 | 701.955 | 701.955 |
| 2 | 3 | 203.910 | 498.045 |
| 5 | 6 | 1109.775 | 294.135 |
| 12 | 13 | 23.460 | 113.685 |
| 24 | 25 | 46.920 | 90.225 |
| 53 | 54 | 3.615 | 23.460 |
| 128 | 129 | 1050.240 | 19.845 |

Notice 12-step equal temperament closes exactly after twelve transpositions by seven steps. The rational itinerary does not. In the finite 12-grid all pitches are formally equivalent under the merged passport despite their frequencies being different. More directly, an approximate-neighbour relation need not be transitive; do not compute its equivalence closure unless that loss of distinction is intended.

## Original artistic research: customs counterpoint

Perform the same oscillator under two authorities. Register is not simply pitch height but a field of permission. A 3:1 transposition is a change of octave-family membership but a preservation of tritave-family membership. The two authorities can each report a different answer without contradicting themselves.

See the [text score](SCORE.md). The illustrative audio renderer, if present, is a synthetic sonic witness, not a perceptual trial. Make the institutional decision audible separately from the oscillator; never conflate a category announcement with acoustic sameness. The performer is free to prefer the equal-tempered closure, the small rational residual, or the disappearance of the institutional voice.

## Exaptation: the Passport Oscillator

Keep an immutable event ID, physical frequency, tuning version, equivalence-rule ID, class coordinate and transformation history. Let the performer patch a symbolic relation independently of the oscillator. Four modes: octave only, tritave only, BOTH (intersection), EITHER WITH CLOSURE (join). The latter is an experimental diagnostic and compositional effect, not an ordinary pitch encoder. Add a fifth mode TAGGED, which returns both coordinates without identifying them. The pair of exact coordinates determines frequency on the whole positive domain, by the intersection proof; in finite precision it may be ill-conditioned for near-returns. Avoid pretending that rounded phase pairs decode uniquely in an unlimited frequency range.

A multi-register FM instrument could assign the carrier to one convention, modulation operators to another, and the patch browser to a third. The patch could display the transformation that preserved the name and any changed frequency or operator ratio. In an experimental “customs” mode, a component census modulates a separate accompaniment, so the audible consequence of administrative homogenization is distinct from the original pitch.

For MHAC, a machine saying “same state” should declare the relation that matters: same physical reading, same hazard band, same action obligation, same lifecycle stage, or same entity? Treating all as one transitive relation could merge states requiring different action. This is a conceptual design risk, not an observed incident. A suitable synthetic falsification test would compare tagged and untagged descriptions on carefully constructed pairwise chains where local equalities differ in meaning; measure correct action identification, time, comprehension and cost of metadata. A simple fixed-reference control is essential. No human recruitment or empirical validation here.

Counterargument: a real listener need not be a continuous invariant classifier; a contextual interpretation can switch rules without computing any transitive closure. Indeed the proposed instrument is intended to enable such switching. The theorem criticizes one precise merging operation, not ambiguity, mixed traditions, or the practice of borrowing another system's categories. If the relation tag is distracting and does not improve recognition, discard the interface proposal. Do not infer universal psychoacoustic distances from frequency ratios.

## Speculative afterword — A common passport

The negotiators abolished the requirement that the stamp identify the issuing conservatory. At first it was an immense success. A student from the western office could present a note in the east and be recognized.

One morning a clerk issued a passport to every key on a piano. His successor issued one to the space between the keys. A third discovered that the number of citizens was growing without the number of passports changing.

The musicians kept performing. The ministry's report was perfectly accurate: there was only one musical citizen.

At the next conference the conservatories did not agree to withdraw recognition. They agreed to print, on the reverse of each passport, the name of the office which had issued it.

The blank reverse had been the entire problem.

---

Reconciliation: main base 495a98ca12bae467a507031f04931aa4254b1866. Read live AGENTS, README, research index, RAG, programme, runbook, integrity, validation, human gates, protocol index/freeze route; reviewed 100 recent PR titles and 60 open issue titles; inspected earlier comma essay. Target #350 created and comments empty on inspection. No exhaustive novelty claim. Fresh disjoint branch, no shared manifests, frozen methods, records or production control changed. ChatGPT/GPT-6.2 with V8 and Python tools; no external reviewers, participant data, purchase or contact. Exact-head repository qualification and integrator review pending; do not infer acceptance from the dedicated oracle. 
