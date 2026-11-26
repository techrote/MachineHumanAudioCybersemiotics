# The Song That Acquires an Ancestor

**Status:** exploratory humanities interpretation, mathematical construction and original synthetic sound art; not a finding of the frozen review. 2026-11-26. Refs #684. AI-assisted authored expedition, no human review or participants.

## The editor's invention

Three singers arrive in an archive with three versions of a song. A fourth singer is built out of their agreements. The archivist discovers that every syllable of its song is endorsed by two of the visitors. Not one visitor endorses the song.

The archivist calls it the original. The instrument maker calls it a new instrument.

This is not the claim that textual editors merely take votes. It is a deliberate caricature of one aggregation procedure. Its value is to make visible a choice of the unit over which agreement is asserted. A local majority can be perfectly well defined without there being a whole-object witness. The new song is a legitimate composition and a potentially illegitimate historical attribution.

Consider the archive as a musical instrument. It has two keyboards: one plays historical performances, another plays relations among them. Neither keyboard is inherently superior. The problem begins when a note from the second is catalogued as a note from the first.

## Source encounters and disagreements

All encounters below are selective, not systematic screening; original source texts are not reproduced.

* Albert B. Lord, *The Singer of Tales*, 3rd ed. (2019), [Center for Hellenic Studies publisher description](https://www-current.chs.harvard.edu/book/the-singer-of-tales-3rd-edition/), paragraphs 1–3 under the title: composition in performance and comparative study of oral epic. The Indiana University Press online chapter [The Theory of Oral Composition](https://publish.iupress.indiana.edu/read/the-theory-of-oral-composition/section/459fbd6a-b9f4-4d63-a364-39f423820cee), paragraph beginning “In chapter 5”, reports Lord's account of theme-level stability and variability of actual words (cites Lord pp. 99, 101, 123). This is a mediated reading, not direct verification of those pages; the full book was not read. The philosophical consequence proposed here is that a performance can be a realization of a tradition without being a defective copy of a single master recording. Do not model actual oral performers as bit-copying machines.
* Casey Dué and Mary Ebbott, [The Homer Multitext and the System of Homeric Epic](https://classics-at.chs.harvard.edu/classics14-due-ebbott/), opening paragraphs in indexed article text; direct fetch timed out. The editors explain their alternative to recovering a single authorial text in a composition-in-performance tradition, while distinguishing surviving written artifacts from unavailable ancient performances. The [project's About page](https://www.homermultitext.org/about/), first paragraph, describes presenting multiform witnesses in historical context. This is a particularly important design precedent for keeping individual recordings alongside an editorial composite.
* Barbara Bordalejo and Peter Robinson, [Manuscripts with Few Significant Introduced Variants](https://doi.org/10.7385/99280), Ecdotica 1/2018, pp. 37–65, publisher abstract only (full text gated). They distinguish coincident agreement and contamination (readings drawn from multiple manuscripts), then identify an additional difficulty involving manuscripts that lack consistent shared introduced variants. This motivates retaining provenance edges rather than presuming a tree. Their analysis is much richer than the synthetic vote below. A shared bit is not evidence of descent.
* Simon Kirby, Hannah Cornish and Kenny Smith, [Cumulative cultural evolution in the laboratory](https://doi.org/10.1073/pnas.0707835105), PNAS 105 (2008), 10681–10686, abstract and Iterated Learning section from indexed text; publisher header also identifies a 2017 supplementary-information correction, not independently examined. Artificial languages transmitted between participants became more learnable and structured in their experiments. No numerical result is imported. The artistic interpretation is that changing the transmission contract may itself change the music. This is not evidence that majority voting models cultural learning.
* Nori Jacoby and Josh H. McDermott, [Integer Ratio Priors on Musical Rhythm Revealed Cross-culturally by Iterated Reproduction](https://doi.org/10.1016/j.cub.2016.12.031), Current Biology 27 (2017), 359–370. Indexed Summary, Experiment 1, Controlling for Productive Biases and Discussion consulted; direct fetch denied. The authors report different reproduction distributions in the two sampled populations, both with some simple-ratio peaks; they use controls for modality, memory and discrimination. No general cultural claim or numerical replication is made here. The important contrast is between the stochastic human reproduction protocol and this deliberately aligned, noiseless discrete apparatus.

The first two encounters resist the assumption that an original is the only worthwhile editorial object. The last two study how transmission changes material. The manuscript encounter warns that the resulting agreements do not uniquely identify a transmission graph. These are different intellectual tasks. None endorses the toy algorithm.

## The finite apparatus

Let three complete, aligned binary scores be a,b,c of length n. At every position two or more agree. Their coordinate majority m is the unique minimizer of total Hamming loss L(x)=sum_i d(x,w_i) over all binary words. This follows independently at every position: choosing the minority costs two disagreements rather than one, and departing from unanimous agreement costs three instead of zero.

Let d_i=d(w_i,m). The minority masks are disjoint because at most one witness dissents in each column. For a witness, all deviations from m occur at nonunanimous positions. Hence L(w_i)=L(m)+d_i. If the output must be a complete witnessed performance, the best attainable loss is L(m)+min_i d_i. This is the precise price of the witness constraint under this loss. It is not a price of authenticity in any broader aesthetic sense.

The majority word is absent from all three witnesses exactly when each of the three minority labels occurs at least once. For three independently uniformly chosen n-bit words, the four column types (unanimous, A minority, B minority, C minority) each have probability 1/4. Inclusion–exclusion therefore gives

P(absent) = 1 - 3(3/4)^n + 3(1/2)^n - (1/4)^n.

There are 2^n choices of majority word, so the exact absent count is 2^n(4^n - 3*3^n + 3*2^n - 1). The probability tends to one in this stipulated independent model; correlated or duplicate witnesses change it. An absent majority is impossible below length three. Conversely, three distinct witnesses 001,010,100 already exhibit the phenomenon.

Now change the unit of agreement. At a k-bit block there are M=2^k possible readings. Exact block majority requires at least two whole block values to coincide. The number of ordered triples with no majority is M(M-1)(M-2), giving probability (M-1)(M-2)/M^2 under independent uniform witnesses. For k=1 this is zero; for k=2 it is 3/8; for k=4 it is 210/256. This is a different procedure from majority on each bit of a block. Whole-block equality can fail even when every note has majority support.

Neither independence nor Hamming distance is a model of historical descent, semantic truth, rhythmic perception or aesthetic quality. The formulas are elementary; no priority claim.

## Four depositions of a song

Original score, fixed 200 ms cells; 0 = 220 Hz, 1 = 330 Hz. Each cell has a squared sine envelope. The three complete witnesses are equally distant from the editorial word:

| Role | Score | Total loss |
|---|---|---:|
| A | 00 11 00 01 | 8 |
| B | 11 01 01 01 | 8 |
| C | 10 10 11 01 | 8 |
| Editorial majority | 10 11 01 01 | 6 |

The first three two-note blocks have three different readings; only the final block is unanimous. The edition appears in none of the original witnesses. Each note has at least two supporters. The optimum witness loss is 8, not 6. This means the edit has gained something in the explicitly specified distance and lost something in its witness status.

Performance directions: play the three witnesses in turn, then the edition. In a fifth movement (unrendered), play only block-majority material, leaving three two-note silences and a final 01. A sixth movement (unrendered) plays the edition while exposing the minority notes on independent voices. The fifth is a deliberately incomplete publication, not an assertion that silence has a universal meaning. The sixth makes dissent available as musical counterpoint.

## Rehearsal and qualification

Run python laboratory.py. It writes four mono 16-bit 16 kHz WAVs (25,600 frames each) and a JSON receipt beside the script. Native Python execution passed on 2026-11-26: 299,592 ordered witness triples, 69,904 exhaustive candidate losses at n<=4, 4,680 block-triples at k<=4. Every enumerated triple verifies the disjoint minority masks, medoid premium and absent equivalence; the exhaustive candidate check verifies uniqueness of the optimum. The absent census at n=1..6 is 0, 0, 48, 960, 12,480, 134,400. The two explicit majority controls, example block counts, deterministic rerender, bounds, complete WAV payload verification and distinct recording hashes passed. No listening test, real lineage inference, external reviewer or repository-wide CI result is asserted by this run.

## Instrument exaptation and the second rabbit hole

**Ancestral Choir** is a proposed playable sequencer, not an implemented VST or firmware. Record three or more quantized performances on independent witness lanes. Give the performer a movable editorial window: note, cell, motif, bar or whole phrase. Provide independently routed witness audition, coordinate consensus, medoid selection, exact block agreement and unresolved alternatives. Store source lane IDs and alignment maps. Display whether a complete generated phrase exists among supplied witnesses. A new phrase must not be automatically added as an independent historical witness: repeated publication could otherwise manufacture numerical support without new observations.

For a CYD touch surface, render witnesses as horizontal strips and the edition beneath; a pinch-like scale control or buttons change block width. Tap a disputed block to reveal complete alternatives. Keep a bounded event buffer and use a precomputed selection map outside the audio callback. For VSTi, add a MIDI witness recorder and performance clock; for VSTfx, use explicitly segmented grain IDs rather than arbitrary spectral bins. A grain composite is not necessarily musically continuous at the splice, so any crossfade is a declared new rendering operation.

The more interesting next instrument permits several traditions to coexist. One conserves contours, another conserves attack order, another has no fixed alignment. Instead of inventing a universal similarity metric, let composers perform the change of alignment and the change of loss. A song may survive one of these editors and disappear under another.

This extends the earlier MHAC investigation into the *Urn* (#668): not merely who is represented as speaking, but what units of their actual records support a newly edited statement. Distinct from #220 (calibrated forecast pooling), #392 (in-place binary smoothing) and #310 (retrospective genre framing). Searches on oral tradition, transmission chains, iterated learning, stemma, consensus and recombination returned no identified equivalent scoped construction; this is not an exhaustive novelty audit.

For operational MHAC, never turn independent field majorities into a supposedly observed joint state. Suppose three valid device records each contain different exceptions to a default. A fieldwise summary may erase every exception and produce a state no device reported. Store joint witness IDs, field support and completeness separately. Compare exact text records, aggregate-only summaries and linked witness inspection in a future synthetic reconstruction study. A reliable structured log may be sufficient; no acoustic advantage established. Keep access, warning and action authorization outside the musical editorial machinery.

Counterargument: an editorial median can be the right estimator under an explicit statistical model with independent errors and a true common template. It can also be a valuable new composition. The error is not combining material but forgetting that a combination was made. Whole witnesses themselves can be unreliable, correlated or fictitious. Agreement does not establish truth; disagreement does not establish error.

*The fourth singer was invited to the archive. When asked who had taught it the song, it played the first two notes of three different visitors. The archivist prepared a label for the original. The singer asked for a label for the operation.*

## Repository reconciliation

Read live main AGENTS, README, RAG, research README, programme, runbook and research integrity. Inspected 45 recent PR-title results and 35 open-issue search results (the latter returned overlapping PR titles; not a complete open issue census), and fetched #220, #392 and #607. Main records retain frozen protocol and in-progress corpus; mergedown #607 reserves promotion for owner-approved exact candidates. This independently scoped exploratory branch is additive and held for that review; no central manifests, frozen records, production software, other branches or registry statuses changed. No external outreach, recruitment or source redistribution. Local renderer blob verified c68ca8045a39a1a21f786f68037d7b4ae4c6cdd4. No subagent or independent human review claimed.
