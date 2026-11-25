# The Footnote That Refuses to Return

*Paratext, digression and addressable musical closure — exploratory humanities/art research, 2026-11-25.*

[Issue #532](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/532) · [Executable oracle](oracle.cjs) · [Performance score](SCORE.md)

## A note that does not know its place

A composer writes a footnote to the fourth bar. The footnote sounds so good that a second player continues it into the ninth bar. A third writes a footnote to that footnote. The fourth bar's author wants their first footnote to finish, but the third player has not finished theirs.

In a book the reader can hold two pages open. In a conventional sequential interpreter the most recently entered subordinate process is often the first to return. Neither convention is a law of musical meaning. The proposed instrument treats the attachment, the duration, the audibility and the right to terminate an excursion as distinct variables.

This is a compositional construction, not a definition of paratext or a theory of attention. It also differs from an ornament generator: the excursion can survive its parent, and its eventual closure can address a specific origin rather than the latest available voice.

## Source-located encounters

**S1 — Gérard Genette, Paratexts: Thresholds of Interpretation (1997), trans. Jane E. Lewin.** [Cambridge introduction excerpt](https://assets.cambridge.org/97805214/24066/excerpt/9780521424066_excerpt.pdf), printed pp. 1–4, especially pp. 2 and 4 (PDF indices 1 and 3 inspected visually as well as text). Genette positions surrounding productions between a text and its reception, with a pragmatic role and variable obligation to read them. His five descriptive questions concern location, time, form, communication situation and function. [Chapter 12, Notes](https://www.cambridge.org/core/books/abs/paratexts/notes/AFFC4676935E49CACD860C5EA595584B), opening subsection “Definition, place, time,” chapter pp. 319–343; publisher's opening excerpt only. A note is characterized by attachment to a local segment rather than to the text as a whole. **Interpretation:** the musical analogue is an explicit attachment, not necessarily a lower volume or a shorter duration. The status of the audible excursion as a paratext is debatable once it is performed as part of the composition; the analogy is deliberately incomplete.

**S2 — Laurence Sterne, The Life and Opinions of Tristram Shandy, Gentleman, vol. I, ch. XXII.** [English online transcription](https://www.ajhw.co.uk/books/book102.html), passage beginning with the narrator's account of his digressive skill, ending before ch. XXIII; pagination and edition not established. [Second online transcription](https://www.sparknotes.com/lit/tristram/full-text/chapter-1xxii/) used to cross-check the same chapter, not independent textual scholarship. The narrator claims his digressions advance the portrait of Uncle Toby rather than merely delaying it. He compares the movement to interlocking machinery. **Interpretation:** a digression may change the work without interrupting its apparent main sequence. It need not be a bracketed, reversible operation. Sterne's narrator is not offering an experimentally validated account of cognition.

**S3 — Music Encoding Initiative, Common Music Notation guidelines, development snapshot.** [Sections 4.3.7 Ossia, 4.3.8 Cue and 4.3.9.2 Rehearsal marks](https://ddmal.ca/guidelines/dev/content/cmn.html#cmn). Read text of these sections, not all embedded score images or examples. An ossia offers alternate realization; cue notes ordinarily indicate material played by others and support orientation; rehearsal marks establish resumption landmarks. These are different musical functions despite their proximity to the main notation. **Interpretation:** do not treat every small note as optional ornament. This is strong prior art for separately represented alternatives and re-entry; the new proposal concerns overlapping, explicitly addressed closures.

**S4 — LilyPond 2.24 notation reference, Creating footnotes.** [Section 3.3.4](https://lilypond.org/doc/v2.24/Documentation/notation/creating-footnotes), event-based and time-based footnotes subsections. The engraving system distinguishes anchoring to a musical event and anchoring to a contextual time point, including objects with no single event cause. **Interpretation:** an anchor ID and a timestamp are not interchangeable even before audio is produced. The proposal adds an audition/termination contract, not a new notation standard.

**S5 — Paulo Dias, Maria João Gomes and Ana Paula Correia (1999), Disorientation in Hypermedia Environments: Mechanisms to Support Navigation.** [Publisher abstract](https://journals.sagepub.com/doi/10.2190/G8C5-342V-DJX3-Q53F), Journal of Educational Computing Research 20(2). Abstract only; no effect sizes or detailed results extracted. The authors review navigation support and competing mechanisms for managing disorientation. **Counterargument:** allowing arbitrary excursions is not necessarily a benefit when the purpose is successful information retrieval. An explicit return marker may be valuable; that is a testable design hypothesis, not an established auditory result.

All access was public web reading on 2026-11-25 by one ChatGPT agent. No independent human review, full-book reading, participant data, or frozen corpus extraction. This is a bounded exploratory reading set, not an exhaustive prior-art or novelty search.

## The subordinate sound is not necessarily subordinate in time

Distinguish six functions: alternative (replace a passage); annotation (attach a comment); cue (orient a performer); excursion (introduce another process); return (resolve a previously selected attachment); orphan (continue a process after its original attachment is retired). A conventional score can do much of this already. The opportunity is to turn the relationships into live, editable synthesis parameters.

A score may have a main strand without requiring every excursion to respect a hierarchy of duration. Conversely an artist may make a very strict hierarchy, and turn its predictability into a rhythmic device. The crucial decision is whether subordination describes what a process is *about*, how strongly it sounds, how long it lives, or which other process is entitled to close it.

A literary note can also be ignored, read first, or revisited independently. The acoustic medium forces a decision about access that the printed page does not make in the same way. A listener could be offered an inspectable side stream rather than compelled to hear it; a composition could intentionally reverse the main and subsidiary buses. Neither choice grants an interface permission to conceal necessary operational facts.

## Exact construction: the address of a closing bracket

Model an event stream as a balanced word of n opens (+) and n closes (-), with no negative prefix depth. Opens have distinct IDs in arrival order. At every close, select any currently active ID and retire it exactly once. No simultaneous events, missing tokens, expiry, re-opening or resource limits other than the depth bound. The observer sees the signs but no address.

For example, ++-- admits A B / B A (nested) and A B / A B (crossing). Both have the same projected sign sequence. A stack makes the first interpretation compulsory; a queue makes the second compulsory. Neither recovers a free-choice sender's intention without additional information.

Let d_j be the active count immediately before close j. It depends only on the skeleton, never on the choices. Every partial valid choice has exactly d_j extensions at that close, so the number M of compatible full assignments is the product of the d_j. This is elementary finite matching enumeration, not a novel mathematical theorem.

An address can be represented as its zero-based index in the ordered active set. Those indices form mixed-radix digits of bases d_j. The full sequence can be encoded as a single integer in [0,M), using successive multiply-add, and recovered by successive reverse remainder/division. An offline fixed-width binary receipt requires ceil(log2 M) bits and suffices, with unused patterns rejected. This is a cardinality bound, not an acoustic rate or a claim of online latency optimality; the receiver needs the skeleton, and a real-time per-close message has a separate overhead/error budget. A sender that agrees to a single deterministic policy requires no address bits, because it has given up the choice.

**Peak concurrency as a composable parameter.** For exactly n opens, maximum depth h (1 <= h <= n), the greatest possible M is h! times h^(n-h). After the last visit to depth h there must be at least one close at every depth h,h-1,...,1 before returning to zero. The other n-h closes contribute factors at most h. The bound is attained by h opens, then n-h repetitions of close/open, then h closes. For n=7 the sharp maxima for h=1..7 are 1,64,486,1536,3000,4320,5040. Keeping the same number of musical events, a composer can alter how many attachment assignments are possible simply by relocating openings and closings.

For the fixed skeleton +++--- there are six possible close sequences. At depth one the closing sound alone is sufficient; at depth three it is not if arbitrary addressing is permitted. A repeated (+-) skeleton admits exactly one matching. These are negative controls against treating every closure as ambiguous.

Across all skeletons of size n, the total number of assignments equals (2n-1)!!: any perfect matching of 2n ordered positions determines the earlier endpoint as an open and the later as a close. The matched endpoints automatically satisfy the prefix condition. This independent count checks the enumeration.

## Executed qualification and boundaries

Run `node oracle.cjs`. The function body was executed in the JavaScript tool environment before committing, and the fetched file content matched the authored source. For n=0 through 7: 626 balanced skeletons, 146,600 valid matching assignments, 294,524 assertions. The oracle filters independently enumerated permutations by opening-position eligibility, compares counts, checks rank injection and inversion, validates the double-factorial total, checks every sharp depth maximum and its constructive witness, and rejects malformed skeletons, future/duplicate closure, noninteger/out-of-range ranks. Native Node and full repo validation not performed in this run. The exact finite computation does not model listener memory, timing errors, sound masking, message repair or human preference.

## Exaptation: the Marginalia Organ

Give every excursion a durable ID, parent anchor, local clock, render bus and close policy. A main-score conductor creates anchors; a second performer can audition annotations without making them audible to the audience; a third performer can promote an annotation into a voice or retire it. Keep parent-link and close-address independent. A voice can continue after a parent closes only if a declared orphan policy permits it; no automatic substitution of the newest active ID when a target is absent.

Suggested controls: anchor brush (event/time); optional replace or append; concurrent or paused main clock; address selector (stack/queue/free); maximum active excursions; per-voice decay; explicit orphan/promote/discard; separate principal, commentary, orientation and receipt buses. A repeated closing gesture may be the same sound in a deliberately ambiguous artistic mode, or may select an ID with an explicit visual or acoustic receipt. An address is not proof of understanding.

A minimal four-voice implementation can compare two scores sharing identical onset/close tokens but different matched endpoints, then introduce low-level address-specific resonators to make the relation audible. The related work could often be expressed through ordinary MIDI note-off IDs, polyphonic voice allocation, DAW sends and finite state machines. Do not claim a novel synthesis algorithm merely by naming these features. The experiment is whether independently authoring the attachment grammar is creatively productive.

For MHAC, a fictional inspection scenario could compare a single-thread restriction, unrestricted overlapping explanations with explicit topic IDs, and a direct text/visual list. Include queued/closed/stale targets, a skip and a resume, all within a non-consequential synthetic task. Measure intended-target identification, incorrect closures, lost place, latency and burden; compare equal event budgets or report differing exposure. No actual user study is authorized. Mandatory safety/state information must never depend on optional footnote access. If ordinary topic-labelled dialogue or existing #456 handles the problem, use it instead; no frozen protocol or operational integration is proposed.

## Speculative fragment: the reference librarian

The library had replaced its footnote numbers with bells. A low bell opened an inquiry and a high bell closed one. In a room with one reader this arrangement was faultless.

When three scholars arrived, the librarian ordered the high bell to close whichever inquiry had most recently begun. One scholar objected: his question had already been answered and another's was still alive.

The librarian installed three more bells. The composer hired the room at night, removed the labels and performed both histories.

At dawn the librarian asked which inquiry the concert had resolved. The composer said the concert had been about the difference between resolving a question and making the sound of resolution.

The librarian kept the labels. The composer kept the room.

## Reconciliation and scope

Base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, validation, research workspace and frozen-protocol index. The canonical evidence pipeline remains gated; this standalone expedition does not promote any finding. Reviewed 70 recent PR titles, 50 open issue titles and targeted searches for paratext, annotation, footnote, digression, margins, scope, interruption and related terms. Maintenance-art route abandoned due to #374; retrospective metric route overlaps #382. Read issue bodies #334 (perceptual framing), #382 (metric roles), #452 (scoped grammar), #456 (situated relay); this is about composing local attachment and close-order relations, not those existing mechanisms. Own new issue #532, no comments at intake. Search is bounded, not a global novelty guarantee. Three disjoint files only; no shared manifests, protocol, evidence registry, production software, participant work or merge. Draft/HOLD pending integration review and exact-head checks.
