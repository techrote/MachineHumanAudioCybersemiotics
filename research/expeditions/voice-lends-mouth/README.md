# The Voice That Lends Its Mouth
## Footing, audible quotation, and the adoption of someone else's musical rule

**25 November 2026 · Refs #460 · exploratory humanities, artistic and synthetic research.** Not selected Track E/G evidence, a frozen-protocol amendment, or an implemented operational interface.

A sound travels from a recording to a sampler, then from a sampler to a synthesizer. The synthesizer can repeat it accurately. But is it speaking, citing, lending a mouth to the absent performer, or allowing the borrowed sound to organize its own subsequent activity? The question cannot be settled by obtaining a better recording.

The expedition proposes separating *rendering a pattern* from *adopting that pattern as a local compositional rule*. The separation permits a rather peculiar instrument: a sampler that borrows a sound without borrowing its power to organize the future.

## The philosophical encounters

**Quotation.** The Stanford Encyclopedia of Philosophy entry [Quotation](https://plato.stanford.edu/entries/quotation/) (revision 19 April 2023), §2.2, examples D1–D3, gives the familiar distinction between using a word to speak about something and mentioning the word itself, and then shows why simple definitions of that distinction are inadequate. Its §4, example 12 and subsequent discussion of mixed quotation, recognizes that a quotation can contribute to what is said while also attributing a particular expression. These are secondary expository passages, not a reading of all cited theories. The distinction is therefore a starting point, not a claim that linguistic activity has two mutually exclusive modes.

**Footing.** Manning and Gershon, [Animating interaction](https://www.journals.uchicago.edu/doi/full/10.14318/hau3.3.006), HAU 3(3), 2013, DOI 10.14318/hau3.3.006, paragraphs beginning "Goffman's innovation" and "Goffman suggests three primary roles", discuss the separation of physical utterance production, formulation and the party whose position is represented (citing Goffman 1981, pp. 144–145). Their subsequent paragraphs introduce the animated figure from Goffman's 1974 work and compare animation and performance. We consulted these passages in the authors' article, not the original Goffman books. A loudspeaker can be the physical vehicle of words without being the party responsible for their position. The transfer to a synthesizer is our interpretation.

**Counterposition.** Luke Fleming, [Undecontextualizable: Performativity and the Conditions of Possibility of Linguistic Symbolism](https://www.cambridge.org/core/journals/signs-and-society/article/undecontextualizable-performativity-and-the-conditions-of-possibility-of-linguistic-symbolism/573BC3A23B3A7046FC3253FF0B579B5E), published online 1 January 2025, abstract and Participant Roles section (paragraph beginning "Two scholars who grapple"), contrasts Levinson's finer-grained analysis of participation with Irvine's attention to culturally situated fragmentation of roles. Fleming's abstract also emphasizes utterances whose performative effects resist cancellation. Irvine is read indirectly here. This prevents the engineering diagram from becoming a universal anthropology: quotation labels cannot guarantee the absence of social effects. The most interesting art may deliberately destabilize the very roles that the software records.

**Berio.** Luciano Berio, [Sinfonia (author's note)](https://www.lucianoberio.org/en/program-note-work/sinfonia-authors-note/), work dated 1968–69, introductory paragraph and the paragraphs describing the third movement and Mahler's scherzo, primary composer commentary in the hosted English version. Berio treats varying intelligibility as part of the work, and describes the pre-existing Mahler movement as a generative framework within which other materials interact. He offers the image of a river intermittently visible in a changing landscape. Thus a borrowed structure can be more than an object exhibited in a new composition: it can be the place in which composition happens. This is his account of the work, not an independently performed score analysis.

**Oswald.** John Oswald, [Plunderphonics, or Audio Piracy as a Compositional Prerogative](https://www.econtact.ca/16_4/oswald_plunderphonics.html), 1985 conference paper, eContact! 16.4 web republication; opening paragraphs and passage immediately before "Chimeras of Sound" beginning "Musical language has". Oswald treats the sampler as simultaneously a documentary and creative instrument and raises the absence of a conventional musical equivalent to literary quotation punctuation. This is a primary artistic polemic, not current legal advice or evidence of universal musical practice. His question is valuable precisely because a borrowed sound can be recognizably quoted without a standardized acoustic punctuation system. Attribution, contractual permission, artistic transformation and payment remain different concerns.

All five items accessed on 25 November 2026 by one AI research agent using web text retrieval. The stated sections/paragraphs were inspected; no full-book reading, independent human appraisal, or legal verification. No source audio or copyrighted score was copied. The juxtaposition is an interpretation, not evidence that these writers share one theory.

## A sound can be a specimen and a rule

Consider a four-note fragment that occurs in an archive. We can listen to it as an example of the archive, or use its pitches as the parameters of an unrelated harmonic system. We can do both at once. The second operation has consequences outside the time interval in which the fragment sounded.

This suggests several distinct relations to borrowed material:

| Relation | Narrow question |
|---|---|
| Rendering | What signal is being produced now? |
| Lineage | From which stored object was the material derived? |
| Declared citation | Is this occurrence presented as referring to that object? |
| Local adoption | Does this occurrence explicitly supply a rule for later synthesis? |
| Authorization | Who can permit the use, transformation or delegation of the material? |

The last relation is deliberately NOT implemented as a license system. No one gains a legal permission merely because a sound is reproducible, its parent is known, or an artist adopts it. A citation declaration is not cryptographic authenticity. Even correct lineage does not decide the meaning of the citation.

An example of mixed artistic use: quote an oscillator's recorded four tones while adopting their reversed, octave-transposed frequencies to tune a subsequent countervoice. The citation and the compositional consequence can coexist. Conversely one could leave the original completely inaudible, using a derived envelope only. That latter possibility is outside our miniature, which always renders the opening phrase.

An artist could preserve the original in a dedicated monitor while allowing the borrowed pattern to make unfamiliar things. This may be more interesting than endlessly manipulating the original audio: the source has become a guest organizer.

## Executed miniature: a relay whose rules do not travel automatically

The included [laboratory](laboratory.cjs) uses four explicitly chosen local modes. Every node keeps a parent reference and an invariant four-frequency motif. The citation bit C and adoption bit A are independent; C is an additional explicit declaration, not whether provenance exists. The local rule A=1 produces a reversed, octave-doubled countervoice in the second half of the score. The rule A=0 produces no such countervoice. Both keep the base voice.

The deliberately bad comparison policy inherits adoption by logical OR from all ancestors. Once an ancestor has chosen adoption, every subsequent replay is interpreted as adoption. The scoped policy instead uses only the current node's explicit bit. This is a design choice for this instrument; inheritance may be desirable in other explicitly authored instruments.

At chain depth d there are 4^d distinct mode histories. The number ending in non-adoption while having at least one earlier adoption is 2*(4^(d-1)-2^(d-1)): two terminal non-adopting modes, and any preceding sequence except one in which all modes have A=0. Summing depths 1 through 6 yields 2,604 disagreeing endpoints in 5,460 histories. The count is not a probability of misuse. Its value is to expose exactly what the comparison policy conflates.

The executed JavaScript core enumerated those histories and rendered four stereo 16-bit PCM recordings at 16 kHz, two seconds each. It checked parent retention, all local mode bits, identical motif values, repeated rendering, byte lengths, sample bounds, invariant first-half PCM, identical left-hand continuation, and exact equality of the two citation-bit variants for each adoption setting. It counted 293,861 successful assertions (including individual PCM sample bounds). Two different sounds are produced, not four. No Node wrapper or actual speaker was used in the qualification: the pure core ran in the available JS runtime, and the Node wrapper is provided for subsequent offline export. No listener data.

Run with Node 18+ from this directory:

    node laboratory.cjs output

The files are original generated tones, not renderings of Berio or Oswald. See [SCORE.md](SCORE.md) for the performance and blind comparison. No separate output files are necessary in the repository.

## Exaptation: the Footing Sampler

Propose a modular instrument with separate material and rule buses. A sample reference has a stable ID and retains its lineage; a local event independently controls audio playback, citation annotation, and explicit adoption into synthesis. Adopting a pattern instantiates a bounded new transformation under the local performer's control. That operation is not inherited by copying the sample. Explicitly routing or copying the transformation is another operation.

Example: one performer contributes a four-frequency pattern. A second renders it without adoption. A third uses its ratios to reorganize a set of FM carriers. A fourth chooses to quote the third performer's new rule rather than the first performer's notes. The audience might hear the same motif moving through the ensemble while its downstream relationships continually change. The score becomes a genealogy of changing relations rather than a genealogy of note sequences.

An implementation could retain origin, transformation chain, citation status, adoption target, scope and release. Keep sample playback independent of the bounded local modulation graph; no executable code in imported media. Distinguish copied parameter values from ongoing links, and expose a snapshot when severing a link. Parameter ranges and scheduling need separate DSP qualification. Optional annotation could become a musical voice of its own; never assume an arbitrary earcon universally signifies quotation.

An artistic instrument can permit unresolved footing: maybe the source is credited on one layer and imitated on another. An operational system has a different obligation. In a purely fictional console, a machine replaying an archived instruction for inspection must not present it as a current request. Correct source ID, destination ID, and payload integrity are insufficient if the current utterance's role is unclear. Compare literal archival labels, explicit current/quoted role labels and a visual transcript; measure source/role/action prediction, unauthorized actions in simulation, missed genuine requests and burden. A label might not prevent misinterpretation. Prior work #43 covers actor binding, #56 retraction, #58 shared evidence dependence, #366 abandoned syntax, #452 scoped clauses. This proposal changes neither those protocols nor their results; it concerns the difference between displaying a historical utterance and adopting its content locally, not the correctness of its recipient, cancellation, or scope.

**Counterarguments.** Citation can be genuinely consequential: an insulting remark can still offend when repeated, and a musical quotation can confer prestige even when its note pattern drives no subsequent synthesis. Our A bit controls only one defined musical transformation; it does not measure actual influence, consent, endorsement or social power. An unchanged waveform can have a new function, but the reverse is also possible: different sounds may enact the same role. If a standard DAW with explicit audio and modulation routing already suffices, the engineering contribution may be nothing beyond an authoring vocabulary and comparison score. That is an acceptable outcome.

## Checkpoint

Base main inspected at 495a98ca12bae467a507031f04931aa4254b1866. Reconciled AGENTS, README, RAG, programme, runbook, integrity and validation documents; inspected recent PR/open issue search results and targeted quotation/role overlap results, new issue #460 and its empty comment list. The owner explicitly requested a fresh additive expedition; no frozen or shared records modified, no dependent canonical work advanced. One AI agent performed reading, composition, implementation and self-check. Draft for integration; repository integrity CI and mergeability are separate from the local core qualification. No participant recruitment, physical listening, independent review or production deployment.
