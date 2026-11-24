# The Licensed Glitch
*An essay and finite sound experiment on the difference between protecting a distinction and protecting every detail.*

**Status:** exploratory MHAC expedition; original interpretation, bounded mathematical derivation, synthetic audio. Not Track E/G evidence, a validated human interface, or a new coding-theory theorem of general scope. Refs #246.

## 1. The grammarian and the broken machine

A grammarian encounters a sentence which violates the rule she has just taught. A poet encounters the same sentence and discovers a device. A repair algorithm encounters it and produces a third sentence: the one it thinks must have been intended.

The relation between these three occupations is not simply their attitude to error. They possess different warrants for intervention. The grammarian acts in a normative institution; the poet may exploit or change that institution; the repair algorithm operates under a specified objective. None automatically possesses an authenticated account of how a particular irregular sentence came into existence.

Quintilian's *Institutio Oratoria* supplies a remarkably old formulation of the difficulty. In I.5.5 and I.5.52–53 he differentiates grammatical faults from admissible figures, while IX.3.1–5 situates grammatical figures in changing usage, deliberate practice, authority and stylistic moderation. Deliberateness is important in his account, but not a sufficient condition for excellence. In IX.3.13, once an unusual construction becomes customary, its status as a figure is itself doubtful. This is not a modern theory of dialect equality: it is a rhetorical education formed within a particular hierarchy of usage and authority. Nor should a modern reader infer that every unconventional construction is an intentional literary gesture.

Rosa Menkman's *The Glitch Moment(um)* returns to a related tension in a very different technical and political setting. Her introduction (printed pp. 8–9) attends to both accidental and simulated disruptions, while her manifesto (p. 11, especially points 1, 3 and 5) challenges the pursuit of transparent media and warns that reproducible glitch effects may themselves become conventional commodities. These are positions in an artistic-critical programme; they are not evidence that unreliable alarms are desirable.

The comparison is not a claim of genealogy, influence, or equivalence. Quintilian and Menkman have different objects, social contexts, and evaluative commitments. Their juxtaposition suggests a question: what happens when an institution, instead of prohibiting every departure from its canonical form, explicitly protects some distinctions and leaves other departures available for play?

Shannon's opening definition of the communication engineering problem (1948, corrected reprint p. 1) concerns reproduction of a selected message and brackets its semantic content. It does not require that every application designate the entire waveform as the message. Masnick and Wolf's 1967 unequal error protection paper (abstract and introduction, p. 600) explicitly investigates protecting some digits more strongly than others. This is the technical antecedent, not an invention of this expedition. The following toy changes what counts as a message from a whole word to a stipulated class of words; aesthetic interpretation remains a separate act.

## 2. A finite contract for ornament

Let Q_n be the n-dimensional binary cube, with Hamming distance d. A sender may choose any member of either nonempty class A or B; that class is the stipulated message. Its selected word is an ornamented realization, not an independently protected payload. Assume an adversarial channel flips at most t bits, including no flip. Assume known boundaries, known codebook and perfect observation of the received word.

The exact condition for a class decoder that never fails on a permitted transmission is min d(a,b) >= 2t+1 over cross-class pairs. Sufficiency follows from the triangle inequality: overlapping radius-t balls would imply cross-distance at most 2t. For necessity, if a cross-pair differs in at most 2t coordinates, choose an intermediate word by changing at most t of those coordinates from either endpoint; that received word is compatible with both messages. This is ordinary distance geometry, not a theory of semantic understanding.

Notice that distances within a class are unrestricted. A class decoder need not restore the ornament; a full-word decoder must additionally separate all distinct words. If all source words are allowed and no transmission error occurs, an exact word readout is possible. Conversely, when errors are possible, a received member of the codebook is not by itself proof of intentional selection.

Define F(n,t,k) as the largest possible size of B when A has k members and both are nonempty. For a fixed A, B may include every word whose distance from every member of A exceeds 2t. The oracle enumerates this intersection. It reduces search without assuming linearity, antipodality or ball-shaped optimal sets: translate one member of A to zero, then permute coordinates to move some chosen member of B to a canonical word of its Hamming weight w. Since w ranges over 2t+1 through n, every admissible pair is represented up to an isometry. Enumerate every subset of the canonical B witness's far set containing zero, intersect all far sets, and retain the maximum for each k. No randomized sampling.

| n | t | Max equal class size | Enumerated symmetry-reduced cases |
|---:|---:|---:|---:|
| 3 | 0 | 4 | 192 |
| 3 | 1 | 1 | 1 |
| 4 | 1 | 2 | 32 |
| 5 | 1 | 6 | 98,304 |
| 5 | 2 | 1 | 1 |
| 6 | 2 | 2 | 128 |

In five bits with one allowed error, the complete nonempty frontier is:

| A size | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11–16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Max B size | 16 | 10 | 7 | 6 | 6 | 6 | 3 | 2 | 2 | 2 | 1 |

A size greater than 16 is infeasible if B is nonempty. A and B are labelled; the frontier is not a count of distinct designs. A witness for six each is A = {00000 and the five weight-one words}, B = {11111 and the five weight-four words}. The nearest cross-distance is three. The radius-one expansions cover the entire cube, exactly partitioned by weight <=2 versus >=3. Majority decoding therefore works for all 72 allowed combinations of source and error mask. A much simpler construction repeats the class in three bits and leaves two free bits, permitting four variants per class. The ball construction allows six, a 50% increase in variants under the same length and radius; this is a finite codebook comparison, not a throughput or perceptual improvement.

The comparison with full-word correction is striking. The maximum pairwise-distance-three code in Q_5 contains only four words, verified by clique search and direct five-subset exclusion; {0,7,25,30} attains four. Thus two equally sized classes with exact realization correction could contain at most two words apiece, versus six each for class-only correction. For completeness the trivial no-error case permits two disjoint half-cubes; the two-error case for n=5 permits only one word in each class. At n=6,t=1 the oracle refuses its expensive enumeration rather than silently extrapolating.

In the six-per-class example every received word has multiple possible origins: the two canonical all-equal words each have six, and every other received word has two. Under the explicit uniform distribution over the twelve selected words and six error masks, each of the 72 histories is equally probable. Exactly one history per received word can be guessed correctly by a full-word estimator, so the optimal exact-word success probability is 32/72 = 4/9, while class recovery is perfect. This probability changes with the source or channel distribution; the worst-case class guarantee does not. There is no unique ornament estimate anywhere in the cube under the allowed-history model, although a posterior probability may favour an origin under a different prior.

A negative control is essential: weight-one A word 00001, flipped at two additional positions, becomes 00111, which the decoder classifies as B. The guarantee is only one flip. A separate no-error control shows exact decoding can be warranted when the error model actually excludes corruption. None of these facts demonstrates that a listener could recognize the artificial five-note phrases, nor that real audio errors resemble independent bit flips.

## 3. Is an intentional glitch still a glitch?

The constructed codebook has a weakness as glitch art: each planned variation is already licensed. It belongs to the grammar. Calling every unusual member a glitch risks precisely the domestication problem Menkman raises. A software button labelled GLITCH might be less a rupture than a new conventional expressive control.

The score therefore has three histories to distinguish: a deliberately selected permitted ornament; an accidental channel change producing the same received word; and a decoder's rendering of a canonical representative. The first two may be digitally identical in their arrival waveform. A sound-only inspector cannot determine which history occurred. The third is not recovery of the selected ornament; it is a projection onto a class representative. It can be perfectly successful as a class interface and destructive as a compositional or archival interface.

This invites a distinction among four questions often compressed into one word, correction:

- Did a received signal satisfy the channel contract?
- Did it preserve the stipulated operational distinction?
- Did it preserve the selected realization?
- Did a deliberate expressive gesture, rather than an accident, cause the difference?

The fourth is not decidable from the stipulated waveform alone. A trusted side channel or independent evidence could resolve it; an untrusted sender's claim of intention need not. Aesthetic judgment can also change after the fact: an accidental sound might be adopted as a musical material. That adoption does not retroactively change its physical origin.

There is an anti-romantic consequence. A planned violation cannot emancipate a medium merely because a designer calls it an error. The codebook's protected classes are an imposed norm. Even the label "ornament" may conceal someone else's substantive concern. A composer might consider an exact microtiming inflection the central meaning, not expendable detail. The observer's intended task must be declared before claiming redundancy is well allocated. This is a design ethic, not a claim that any particular language or culture treats musical ornament in this way.

Another counterposition is that perfect restoration can be a prerequisite for meaningful artistic interruption: the performer may wish to hear the very glitch she deliberately produced, in which case this class-only code is inadequate. The appropriate response is not to promote an ambiguity-set decoder into a universal aesthetic principle, but to change protection levels, record the raw signal, or switch instruments.

## 4. The art object: a score with a protected spine

The synthetic score uses five pitches per phrase, 200 Hz for zero and 400 Hz for one, short integer envelopes and silence only between phrases. Its twelve licensed variants run through low-majority and high-majority families. Two six-phrase recordings are produced from distinct histories: deliberately selected ornaments versus an all-zero source with channel flips at matching positions. They are byte-identical at the received-score level. A third six-phrase recording replaces all arrivals with the canonical all-zero rendering; this suppresses intentional variation and channel changes alike. The fourth WAV is the full licensed-variant catalogue. Playback is artistic illustration, not an auditory transmission experiment.

Proposed instrument: a **protected-spine sequencer**. A patch contains (i) an explicit protected distinction; (ii) a set of allowed realizations per class; (iii) an error budget; (iv) a raw received stream; (v) a set of consistent source words; and (vi) independent output routing for raw, canonical, and uncertainty-aware audition. A composer can mutate a codebook and see the exact guaranteed separation change. A repair module can preserve the class while exposing the received ornament rather than claiming it is authentic. A curator may record an accidental event as a later adopted ornament without rewriting provenance.

An artist could write a piece in which ornaments gradually become indispensable. At the point the composer changes the protected partition, the old codebook must be evaluated against a new contract. This is a stronger musical idea than adding randomly distorted notes: the composition can change the distinction that the transmission is expected to preserve. A useful next experiment would use unequal error protection on a larger alphabet and measure where source reconstruction becomes impossible, while keeping a separate study of whether human performers learn or value the resulting constraints.

The MHAC application is only a hypothesis: a machine interface may need to protect operational class, source identity or action authority more strongly than stylistic variation. It should not use this toy as an assurance that machine speech is intelligible or that ornamental prosody is harmless. If any stylistic component carries urgency, status or accessibility information, it must be included in the relevant protected contract. An error channel for speech, noise, masking and attention must be independently specified and evaluated.

## 5. Evidence, limitations and reproducibility

The following source ledger is intentionally small and passage-bounded. All readings performed by a single GPT-6.2 assistant on 2026-11-24; no external peer review or participant work. No third-party source files redistributed.

| Source | Access / exact extent inspected | Use / refusal |
|---|---|---|
| Quintilian, *Institutio Oratoria*, Loeb English translation (1920), [I.5](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Quintilian/Institutio_Oratoria/1B*.html) §§5,52–53 and [IX.3](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Quintilian/Institutio_Oratoria/9C*.html) §§1–5,13 | public-domain English transcription; IX chapter host notes unproofread status. Selected passages only. | Historical argument about figures and usage; no claims about original Latin nuances or modern grammatical norms. |
| Rosa Menkman, *The Glitch Moment(um)* (INC, 2011, ISBN 978-90-816021-6-7), [publisher PDF](https://networkcultures.org/_uploads/NN%234_RosaMenkman.pdf) | printed pp. 8–9 and 11, visually inspected PDF pages 8,9,11 (zero-based); not whole book | Critical artistic argument and commodity tension; not an empirical psychology or engineering reliability finding. |
| Claude E. Shannon, *A Mathematical Theory of Communication* (1948), [corrected reprint](https://swh.princeton.edu/~wbialek/rome/refs/shannon_48.pdf) | introduction, printed reprint p. 1, PDF index 0 visually inspected | Scope of engineering problem; no claim Shannon endorses the aesthetic construction. |
| Burt Masnick and Jack K. Wolf, *On linear unequal error protection codes*, IEEE TIT 13(4), 600–607 (1967), [DOI](https://doi.org/10.1109/TIT.1967.1054054), [author-text transcription](https://www.academia.edu/51882006/On_linear_unequal_error_protection_codes) | abstract and introduction p. 600, text extraction only; original journal PDF not independently inspected | Established antecedent for different protection levels. No reliance on OCR of later equations or claims of new coding-theory novelty. |

Reproduce using Python 3.11+ standard library, from this directory:

    python -m unittest -v
    python glitch_lab.py audio

Executed locally before upload: five test methods, including independent direct subset enumeration on small cubes, 736,281 seven-word candidates containing zero for the five-bit upper bound, direct 201,376 five-word subsets for full-word exclusion (short-circuit per subset), all 72 permitted histories, a two-error negative control, and PCM verification. Source and test Git blob SHA-1s were verified against repository copies:

- glitch_lab.py: f9703fe58ef1c4113fd66bd29a23676e79353d5c
- test_glitch_lab.py: e481efc6ecd092656b6369da508091494b6bf68f

The generated files are not canonical research records. See generated results.json for all 32 ambiguity sets and score provenance. Expected WAV SHA-256:

| WAV | Hash |
|---|---|
| intentional / corrupted | 2ad2a5ee3fcbdafa0fb18f6d659587a61b365902e9e1dbe51b55d782fd8af0ec |
| canonicalized | b6dc8e91229fda2f283254978ea300c448693d77bacc2f47ce4bae7eb6566bbd |
| licensed_variants | b22b88a209c24033d8c0f5fb06bcb15fd164f4ec34b812d6a68de524a5139396 |

Base main 495a98ca12bae467a507031f04931aa4254b1866. Reviewed live AGENTS, RAG, Programme, Runbook, Integrity, Validation, current issue/PR titles, and issue scopes #209, #224, #222 and #234. Distinct from #209 unknown future decision context, #224 live variable-length parsing, #222 reconstructing incomplete historical evidence, and #199 feature collisions: here classes are fixed, intact framed words are received, and cross-class error balls enforce a declared protection hierarchy. The numerical oracle is bounded; the source comparison is selective; the artistic interpretation is original and revisable. No shared records or other branches changed. Repository-wide CI and independent review remain separate acceptance items.
