# The Choir That Invents a Word

Mondegreens, minimal boundary testimony and the art of an unauthorized lexicon.

**2026-11-26 | Exploratory humanities/art and synthetic mathematics | Refs #713 | Draft/HOLD.**
This is neither a frozen Track E/G extraction nor a validated acoustic communication design.

## 1. The error that refuses to die

Sylvia Wright's Lady Mondegreen is more than the consequence of a bad transcription. In her remembered childhood encounter with a ballad, Wright heard an additional person where the received text describes the disposition of the Earl. By the time the reader is told what the conventional reading is, the other woman has already acquired a costume, an attitude and a relationship. The correction arrives too late to prevent an act of fiction.

**Interpretation.** The essay's important operation is not the initial confusion but the subsequent refusal to let the recovered text cancel the new person. At its conclusion, Wright has made a whole imaginary geography from several mistakes. The correction is a legitimate answer to a question about the ballad's words; it is not a legitimate answer to every question about the fictional person who has since come into existence. The error has become a new work. The editor who removes it from the transcript need not remove it from the library.

This suggests an instrument whose performers have distinct occupations. The first plays acoustic material. The second proposes boundaries within it. The third invents the names of the newly constituted objects. The fourth may reject the proposed boundaries without deleting the names. A discarded reading can become an autonomous composition instead of an error to suppress.

We should be careful with the apparent analogy between the listener and a decoder. A word is not just a sequence of phonemes; its use can depend on history, genre, interlocutors and the activity in which it participates. The mathematical construction below deliberately omits those dimensions. It asks a narrow question about a world in which two kinds of units are licensed and exactly known. It does not explain why Wright heard a person.

## 2. Source encounters and disagreement

Accessed 2026-11-26 by the current AI assistant; no independent human reading, peer review, corpus screening or study appraisal. No source PDF or third-party audio redistributed.

- **Sylvia Wright (1954), The Death of Lady Mondegreen, Harper's Magazine, November, pp. 48–51.** [Scan](https://www.drapersguild.com/uploads/1/2/8/5/12854632/harpersmagazine-1954-11-0006768.pdf). Read opening anecdote, correction and aesthetic declaration on printed pp. 48–49 and closing narrative and warning on p. 51; visually inspected PDF pages 0, 1 and 3. The text explicitly privileges imaginative mishearings and constructs a shared world for them. My reading of correction as a late intervention in the ontology of fiction is an interpretation, not a claim about Wright's psychology. Source access is a third-party scan, not an inspected publisher archive.
- **Anne Cutler and Dennis Norris (1988), The role of strong syllables in segmentation for lexical access, JEP:HPP 14, 113–121.** [Institutional abstract](https://www.mpi.nl/publications/item68765/role-strong-syllables-segmentation-lexical-access), [DOI](https://doi.org/10.1037/0096-1523.14.1.113). Abstract and bibliographic metadata read, not the whole paper. Their model associates strong syllables with candidate segmentation points, and their reported word-spotting experiments distinguish different syllable contexts. This is source-reported evidence, not an independently assessed result.
- **Jessica Nieder and Kevin Tang (2023), Kriech nicht da rein! A new corpus of naturalistic misperception of German misheard sung speech.** [Author-text mirror](https://www.academia.edu/105621045/Kriech_nicht_da_rein_A_new_corpus_of_naturalistic_misperception_of_German_misheard_sung_speech). Read abstract, sections 2.1, 4.2 and 5, printed pp. 506–509, in HTML extraction; tables and raw data not independently inspected. Their collected German sung-lyric misperceptions include departures from predictions based on strong/weak syllable boundaries and newly invented word forms. Their discussion suggests genre expectations as one possible account; it is not established as the cause. The collection of reported mistakes is not a random sample of listening and does not estimate an error rate. Do not conflate German sung speech with English word-spotting.
- **Richard M. Warren (1961), Illusory changes of distinct speech upon repetition—the verbal transformation effect, British Journal of Psychology 52(3), 249–258.** [Bibliographic record and abstract](https://cir.nii.ac.jp/crid/1361137043760785408), [DOI](https://doi.org/10.1111/j.2044-8295.1961.tb00787.x). Abstract only: repeated speech can be reported as changing into alternative forms despite a repeating recording. This supplies a distinct experimental lead, not a demonstration that our tones induce the same experience.
- **Diana Deutsch, Trevor Henthorn and Rachael Lapidis (2011), Illusory transformation from speech to song, JASA 129, 2245–2252.** [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/21476679/), [DOI](https://doi.org/10.1121/1.3562174). Abstract only. The authors report shifts in judgments and vocal reproduction following repetition, with differing results when intervening presentations were altered. This concerns the speech/song distinction rather than identification of word boundaries.

The contrast between these accounts is more useful than a premature synthesis. Wright treats the unexpected reading as an achievement; laboratory speech research treats a changed report as an outcome requiring explanation. Neither implies that a machine has understood a phrase because its boundary detector succeeded. Neither authorizes a universal prosodic rule. An artist can privilege invention while an operational interface preserves source-authorized distinctions.

## 3. Exact construction: the cost of identifying a grouping

Let n >= 1 labelled acoustic cells have fixed durations and fixed PCM. Every single cell and every consecutive two-cell group is licensed. A complete parse tiles the line with singletons and dimers; no overlap or uncovered cell is allowed. All carriers are identical across parses. No semantic or pitch-dependent constraints exist.

Represent the parse by D, the set of gaps crossed by dimers. D is an independent set of the path of n-1 gaps. At each gap, the secondary channel can assert B (boundary), C (continuation/no boundary) or ? (unasserted). A truthful assertion constrains a gap to its target value. Silence denotes ? by convention; it never denotes C. Known cell grid, frame start/end, dictionary and reliable marker delivery are model assumptions, not free information in a physical implementation.

The number T(n) of possible parses without assertions satisfies T(0)=T(1)=1 and T(n)=T(n-1)+T(n-2) by the length of the first tile. Thus T(n)=F_(n+1), with F_0=0,F_1=1. Eight cells admit 34 readings.

**Proposition (elementary finite result):** the unique inclusion-minimal sufficient set of signed local assertions for a target D consists of:
1. C at every gap in D;
2. B at every gap outside D and outside the immediate-neighbour set of D.

Proof of necessity: remove any single dimer from D and replace it by two singletons. The alternate parse differs at precisely that gap, so that C is mandatory. For a gap outside D and not adjacent to D, the two cells are singletons, and merging them changes precisely that gap. Its B is mandatory. For sufficiency, every C forces the neighbouring gaps to be B because a cell cannot be in two dimers; every remaining gap is directly constrained. Hence all other assertions are redundant, and any sufficient set must contain exactly the mandatory set, possibly with additional assertions. This proves uniqueness of the minimum set.

Equivalently its size is the number of dimers plus the number of adjacent-singleton joins. The all-singleton parse requires n-1 B assertions; an even-length all-dimer parse requires n/2 C assertions. Different groupings of the same fixed carrier therefore have unequal local description costs.

Positive-only testimony has a sharper failure: if D is nonempty, asserting even every actual B still permits the all-singleton parse. A true list of boundaries is not necessarily a complete account of the boundaries. Absence of a marker must not be promoted to an assertion of continuity.

This is not an information-theoretic bit-optimum: a global index of a parse in an agreed enumeration needs at most ceil(log2(T(n))) bits, excluding framing and codebook costs. The proposition minimizes *the count of truthful local signed assertions*, not total communication cost. Arbitrary-length groups, cross-cell constraints, uncertain timing and noisy markers are outside the proof. No priority claimed.

Exemplar: eight cells, dimer crossings at gaps 2 and 5 (1-based). Target tiles have lengths 1,2,1,2,1,1. Seven gaps have target signs B C B B C B B. The minimum receipt is ? C ? ? C ? B. Positive-only B ? B B ? B B leaves four readings. Removing any one of the three required signed assertions produces an alternative. With all markers the target is unique, and all additional markers are redundant under the model.

## 4. Original score: Five Versions of a Word That Has No Name

Read the following eight notes as a tiny invented language: 220, 275, 330, 247, 294, 220, 330, 275 Hz; 250 ms per note. These frequencies are arbitrary, not symbols of real words. The left channel is fixed. The right channel performs a second score, with 990 Hz representing B and 330 Hz representing C; no marker means ?. All markers are 50 ms tapered pulses near the end of the preceding cell.

| Movement | Gap testimony | Admissible readings |
|---|---|---:|
| I: The nameless carrier | ? ? ? ? ? ? ? | 34 |
| II: The affirmative grammarian | B ? B B ? B B | 4 |
| III: The economical witness | ? C ? ? C ? B | 1 |
| IV: The pedant | B C B B C B B | 1 |
| V: The alternate lexicon | B B B B B B B | 1 (different target) |

Perform I with the right channel silent. Repeat it, but let a second musician group the notes into new phrases with their hands. Do not alter the carrier. Perform II with the affirmative grammarian attempting to make the intended grouping unmistakable. Perform III and IV consecutively. Their right channels sound different although the certified grouping is identical. V is not an error in its own score; it is a different score imposed on the same notes.

The final movement exists only as a performance instruction, not an additional WAV: give a name to each discarded grouping. Reuse those names in an unrelated song. Never correct the old names by changing the original recording.

### Executed laboratory

Run `python laboratory.py audio` using Python 3.11+. Native Python 3.13.5 returned PASS. The literal independent-set census covered 231 target tilings at lengths 1–10, testing 65,945 candidate assertion subsets, of which 2,697 were sufficient. The brute force checker computes disagreement masks against every alternate parse and tests all subsets; it confirms that the formula gives the unique minimum and that every sufficient subset contains it. The positive-only failure and Fibonacci recurrence were checked.

Five distinct 16 kHz, 16-bit stereo WAVs, each 32,000 frames (2 s), were rendered and read back, with amplitude bounds and identical left-channel PCM verified. Carrier-only/positive-only/minimal/full/alternate admissible counts are 34/4/1/1/1. Audio is original synthesized material, not speech or a demonstration of a perceptual illusion. No actual acoustic decoding, noisy channel, human participant or efficacy test. Receipt generated locally by the script; binary WAVs not committed.

## 5. Exaptation: the Mondegreen Choir

The instrument has a persistent carrier, a grouping canvas, a local testimony bus and a named-alternative archive. A singer controls the carrier; a second performer paints boundary/continuation markers; a third auditions a retained interpretation as independent modulation. Each group triggers an optional resonator whose parameters depend on its assigned name. Thus two musicians may agree on all frequencies and disagree on the resonator events. The additional music is a consequence of a declared reading rather than an intrinsic property of the carrier.

For CYD: a horizontal strip of eight cells; tap gaps to cycle ?/B/C. Under it display the number of viable parses and an auditionable selected reading. Refuse contradictory assignments; allow the artist to pin any viable reading, name it, and branch its history. A separate control toggles the minimum truthful certificate for the currently pinned reading. Use bounded dynamic programming for larger strips; do not materialize unbounded parse lists in the audio callback.

For VSTi: MIDI notes as cells, a grouping sequencer and independent marker/resonator buses. For VSTfx: externally supplied event segmentation, unchanged dry carrier and a separately modifiable grouping interpretation. Do not infer the original word boundaries from arbitrary incoming audio. For FM-1: a small finite gesture grouping grammar and independently routed modulation on group starts. Hardware feasibility and real-time implementation remain untested.

A richer score could let a group name remain active after its parse becomes invalid. The name then becomes a historical artistic adoption, not a decoded fact. This is an intentionally different operation from silently reinterpreting an authoritative message.

## 6. Research implications, dissent and handoff

A machine can explicitly report a boundary, explicitly report continuation, or report neither. A scope-sensitive decoder should not collapse these states. Test whether a straightforward visual boundary table, framed packets or explicit textual word boundaries solve the operational problem before adding sounds. A future authorized study could independently manipulate framing, true signed markers, ambiguity and exposure to previous readings. Report exact symbolic recovery separately from human boundary recognition, message interpretation, correct action, abstention, latency and false confidence. Include inconsistent markers, erased continuation markers, and a carrier-only negative control. No communication benefit is established. Any empirical inclusion or testing requires the established programme gates.

**Counterargument:** the model impoverishes Wright's error by insisting that new words be made from a fixed licensed inventory. The most interesting mondegreen may not be in the dictionary at all. Future artistic work should explicitly allow invented lexemes and changing grammars, while distinguishing invention from recovery. The mathematical oracle should continue to refuse out-of-contract strings.

**Speculative coda.** The machine sang eight notes. The grammarian found six words. The engineer found four possible sentences. The poet asked whether one of them could be a person. The machine played the same notes again. On a separate track, the poet began to answer.

**Repository reconciliation.** Base 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, research integrity and validation, recent 35 PR titles and 30 open issue results, targeted overlap searches. The initial Sardinas–Patterson/live-delay direction was abandoned after reading #224; #572 studies overlap between partitions, #366 interrupted syntax, #38 spoken polarity, #650 praeteritio. This expedition instead derives local signed certificates for a deliberately ambiguous finite carrier. Fresh issue #713 had no comments when read. No dependence on another draft's acceptance; no shared manifest, frozen protocol, canonical evidence or other-worker file changed. Single AI assistant performed source reading, derivation, implementation and checks; no independent reviewer. Full repository suite not executed locally. Hold for exact-head repository CI and independent integrator qualification; no merge or scientific promotion requested.
