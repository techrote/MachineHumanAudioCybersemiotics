# The Surface That Forgets Its Scratches

*Patina, computational wear and the difference between a surface and a biography.*

Expedition #606 | 2026-11-25 | exploratory, AI-assisted, synthetic and artistic; not selected Track E/G evidence.

## A worn instrument and a new instrument with an old sound

Imagine a wooden organ whose most frequently used keys have become unusually smooth. A visitor mistakes the smoothest key for the newest. The conservator corrects the visitor: it is the oldest, or at least the most often touched. Then a second conservator corrects the first: that key was replaced and polished deliberately to resemble the others.

The same surface can have several plausible biographies. The point is not that surfaces tell us nothing. It is that the inference from a visible or audible trace to an event history is conditional on an account of how the trace was made.

The reverse problem interests the composer. Could we author the *conditions of aging* rather than simply selecting an aged sound? Could an instrument change while being played, remember some operations in its timbre, forget others, and permit a later musician to encounter what remains? Could an old patch be transplanted into a newly created instrument without asserting a fictitious history of performances?

This expedition proposes a Patina Organ: an optional stateful musical instrument whose surface is a compact, non-invertible consequence of explicitly chosen acts. The surface is not an audit trail. A separate, inspectable local score may retain exact history, or may be deliberately omitted. Wear is a compositional medium; provenance is an independent assertion.

## Source encounters (read 2026-11-25)

These are limited readings and original interpretations, not a comprehensive review. No external reviewer, participant, permissions decision or source endorsement is implied.

### Ruskin: the surface as witness

John Ruskin, *The Seven Lamps of Architecture*, chapter VI, "The Lamp of Memory", §10 (Aphorism 30) and opening of §11, Library Edition vol. 8 p. 234, [Lancaster electronic edition](https://www.lancaster.ac.uk/fass/ruskin/eSoV/texts/vol08/vol08p234.html). Read the page, including its editorial footnote 2. Ruskin makes a building's age and endurance central to its significance, famously invoking the "golden stain of time". He also asks a designer to make durable qualities survive loss of finer detail. The editorial note points to a later qualification that rough masonry need not be a sign of age. This is particularly interesting for digital sound: surface appearance may be deliberately constructed rather than accumulated. This is our inference, not Ruskin's account of audio.

The metaphor of a wall witnessing an event is powerful, but a wall does not supply an exhaustive log of everything that happened before it. The aesthetic significance of endurance need not depend upon being able to reconstruct the exact sequence of human gestures.

### Riegl reception: several incompatible values

Andreas Lehne, "The last words of Alois Riegl", *Conversaciones…* no. 5 (2018), translated by Valerie Magar, [HTML text](https://portal.amelica.org/ameli/journal/317/3174387012/html/). Read the consecutive paragraphs beginning "The theory on the values of the monument" through the discussion of novelty and relative artistic value; also the later discussion of nonhuman natural monuments. This is a secondary source, not a complete reading of Riegl's 1903 German text. Lehne distinguishes the aesthetic experience of age from documentary and instrumental values and describes conflicts among them. Preserving the legibility or usefulness of a work is not necessarily the same as letting decay continue.

Interpretation: a synthesizer need not choose between compulsory decay and permanent pristine operation. It can expose three different editing authorities: an aesthetic surface, a retained record, and a useful clean carrier. The desirable setting for each depends on the particular work.

### Marclay: circulation becomes part of a record

Christian Marclay, *Record Without a Cover* (1985), [MoMA object 854.2013.167](https://production-gcp.moma.org/collection/works/184035?artist_id=8478&page=1&sov_referrer=artist) (object metadata consulted: medium and publisher). [MoMA artist profile indexed passage](https://production-gcp.moma.org/artists/8478-christian-marclay) describes deliberate absence of a sleeve and the audible changes that follow; the direct page returned metadata without that prose. For the practice, also consult the indexed direct artist interview in [The Guardian, 14 February 2005](https://www.theguardian.com/music/2005/feb/14/popandrock), paragraph beginning "But Marclay's most notorious project". The artist describes relinquishing the stable document in favour of a changing record. No recording or image was copied.

Interpretation: a distribution system can become a compositional agent. A digital instrument whose copies develop independently would extend this direction, not reproduce the physical work. The artist could choose to exchange a clean design, a worn instance, or a trace of how it was worn. Identical starting files need not remain identical performances.

### Basinski: preservation captures disappearance

Drew Tewksbury, "Orchestra of Decay: William Basinski's Sonic Ruins and Vanishing Tape", PBS SoCal, 23 August 2012, [interview](https://www.pbssocal.org/shows/artbound/orchestra-of-decay-william-basinskis-sonic-ruins-and-vanishing-tape). Read the question about the tenth anniversary and the following five answer paragraphs, and the following exchange about conservation. Basinski describes noticing the tape's deterioration during digitization and recording the changing result. He also distinguishes accepting decay in his own work from the desirability of preservation elsewhere. This is an artist's account, not independent materials-science measurement.

Emilie Friedlander, "Interview: William Basinski", *The FADER*, 11 September 2012, [interview](https://www.thefader.com/2012/09/11/interview-william-basinski), indexed exchange on orchestral transcription. He discusses using rests and percussion to realize aspects of the tape's decay in another medium. A later enactment of decay can therefore be musically meaningful without undergoing the original chemical process. The transcription is not evidence of that process occurring again.

Interpretation: the Patina Organ should have a replay mode. A replay of the sound of wear must not automatically accrue additional wear in the instrument; an artist might explicitly elect to do so.

### Hill, Hollan, Wroblewski and McCandless: computational wear already exists

William C. Hill, James D. Hollan, Dave Wroblewski and Tim McCandless, "Edit Wear and Read Wear", CHI '92, pp. 3–9, DOI [10.1145/142750.142751](https://doi.org/10.1145/142750.142751), [author-hosted PDF](https://hci.ucsd.edu/220/readwear-editwear.pdf). Read abstract and introduction, printed p. 3 and opening p. 4; visually inspected PDF page 0. They propose displaying document-centred interaction histories in an editor, including graphical markings near scroll-bar navigation. Their system uses an abstraction of actual interaction history to support work.

This is direct HCI prior art, not just a resemblance. The proposed musical extension changes a synthesis state, not merely a graphical indicator. It does not automatically collect individual readership or performer histories. The practice of deliberately showing a trace also requires careful attention to whom that trace belongs and who is permitted to see it.

## The constructed material: scratch and polish

Define an initially zero, nonnegative scalar surface w. An abrasion event A adds one unit; a polish event P halves the existing surface:

    A(w) = w + 1
    P(w) = w / 2

These are exact rational toy operations, not a physical material model. Polish can make a surface smoother while both counters increase. The initial condition and operation law are known. Time between operations is not represented.

A then P gives 1/2; P then A gives 1. The event inventory is identical. Order matters.

A more interesting case uses exactly three A and two P events. AAPPA traverses 0,1,2,1,1/2,3/2. PAAAP traverses 0,0,1,2,3,3/2. The final surface is equal, and both event counts agree. Even a correct terminal measurement with exact operation counts does not uniquely recover the history.

The complete trace distinguishes these two examples. It is not guaranteed to identify every operation in a more general model (e.g. no-op polishing at zero, hidden operations, unknown initial state, concurrent or unobserved events).

### Exact reachable surface criterion

For a scratches and p polishes, each scratch contributes 2^(-j) where j is the number of subsequent polishes. Multiplying the final state by 2^p gives an integer n expressible as a sum of exactly a powers of two, each between 1 and 2^p.

Conversely, any such multiset of a powers specifies the number of scratches in each of the p+1 gaps around the ordered polishes. Thus it gives a valid operation word.

Let q,r = divmod(n,2^p). The minimum number of allowed powers required to express n is q + popcount(r): combine pairs of equal smaller powers until no further carries are possible below the maximum denomination. This produces the unique normalized minimum-coin representation; conversely any representation can be normalized by such merges, which only reduce its count.

A power greater than one may be split into two equal halves. Repeated splits increase the count by exactly one each, eventually reaching n ones. Consequently n is reachable if and only if

    a <= n <= a*2^p
    floor(n/2^p) + popcount(n mod 2^p) <= a.

The zero case a=0 gives n=0 only; p=0 yields n=a. The sharp extreme surfaces are a/2^p and a, achieved by putting all scratches respectively before or after all polishes. With sufficiently many scratches, different operation words can share a surface even when both counts are known. An exact criterion for existence is not a formula for multiplicity; the enumerator measures multiplicities independently.

The native Python laboratory enumerates all 12,869 marked operation words for a,p in 0..7, checks 6,980 candidate endpoint integers against the predicate, and rejects an invalid operation. It uses Fraction rather than approximate state updates. These are finite computational checks of a simple constructive proof, not a new mathematical priority claim. Floating-point sine rendering is downstream of the exact model.

## A score that keeps its wrinkles

The renderer uses an original six-note sequence (196,247,294,220,330,262 Hz), with fixed fundamental amplitude and two harmonic partials whose gains depend monotonically on w/(1+w). This arbitrary mapping makes the present state playable; it is not a model of vinyl, a real organ or material acoustics.

Render the entire six-state history for each of AAPPA and PAAAP. Then render the six notes using only the terminal state in each case. These last two files are byte-identical in the local run, whereas the history files differ. Render two more endpoint views for AAAPP and PPAAA. They have the same operation counts but different harmonic gains. See [SCORE.md](SCORE.md) and [receipt.json](receipt.json).

A recording can preserve a trace that the instrument itself no longer retains. Alternatively, an author can preserve the surface without recording its production. An instrument with exact gesture logging and an instrument with compressed state can sound the same in a subsequent performance. The distinction is not detectable by simply listening to identical endpoint renders.

### The instrument that has borrowed an age

A preset store could distribute an aged state as a creative object. A new instance loaded with that state has not lived through the original gestures. A maker can also deliberately generate a synthetic aged state. Label these independently: accrued in this instance, imported from a named snapshot, authored directly, or unknown. Identical sound is allowed; identical provenance labels are not required.

A reset is not historical innocence. In an audit mode the reset event remains in the separate history even when synthesis begins again from zero. In a privacy-preserving mode one can clear that history while retaining the sound; the interface must then report that past events are unavailable, rather than implying that none occurred. Do not retain personal usage data by default.

## Instrument exaptation and tests worth doing

The Patina Organ could be a VSTi with a clean carrier and a per-voice or per-region mutable relief field. A companion VSTfx could map bounded, explicitly opted-in processing events onto wear or polish operators. A score editor controls when such acts happen, independently of note onset. Allow a surface transplant, a simulated aging brush, a snapshot, and a clean audition. No arbitrary code execution or hidden external telemetry is needed.

A larger instrument could arrange thousands of oscillators into a 2-D surface. Gesture pressure writes into local relief; a polishing brush attenuates prior traces; optional diffusion introduces spatial borrowing. Distinct layers could modulate partial amplitude, resonance damping and local envelope character. These extensions need fresh bounds, determinism, state migration and real-time tests. Keep the one-scalar model as a reproducible unit, not a claim about the extensions.

Design a future comparison between a conventional static preset, an evolving surface, and an evolving surface with explicit history inspection. Separate sound preference, predictability of control, correct origin attribution and performance burden. Include a deliberately manufactured aged state and a clean state with many prior interactions. Counterhypothesis: wear makes sound less controllable and an ordinary undo history is more useful. No human experiment has been performed; no advantage established.

For MHAC proper, a weathered or hesitant status cue could misleadingly suggest a long-lived, much-used, or distressed system. Use explicit evidence-backed lifetime/maintenance counters when the information matters; never derive actual service history from a decorative filter. The artistic mode remains opt-in and separate from operational safety or factual state presentation. A conventional event log may be sufficient. The project preference for non-human audio does not remove affective interpretation by listeners.

## Original speculative miniature — the replacement key

The museum ordered a spare keyboard from the original maker. Each replacement key was smooth except for one, which a musician had asked him to roughen.

The registrar put it in the case marked Most Used.

The maker did not correct the surface. He corrected the label.

In the next gallery the worn keyboard played a recording made when it was new. The new keyboard performed a score written by its former owner. The archivist requested that each be allowed to finish.

A child asked whether the first instrument could forget.

The maker showed her the reset switch.

She asked whether this meant nobody had played it.

He showed her a separate book.

There was a second reset switch on the book.

## Repository checkpoint and limitations

Base 495a98ca12bae467a507031f04931aa4254b1866. Read live AGENTS, RAG, README, research README, programme, runbook and integrity instructions. Inspected 65 recent PR titles and 40 open issue titles, then searched patina, Ruskin, wear, restoration, conservation and related terms. Read #222 (rival conjectural restorations) and #374 (maintenance whose labour may be inaudible); our concern is visible/audible changes accumulated and partly erased through use, their deliberately simulated equivalents, and the ambiguity of the surviving surface. Also relevant are #207 hidden order dependence and #548 creative residuals. Overlap search is not proof of novelty.

The work is limited to this expedition directory. No frozen protocol, canonical registry, shared manifest or production code changes. No source files copied. AI-assisted source-located reading, interpretation and code; no independent reviewer. Locally executed Python source blob 42cb56c27662a712c7c344690fcfdbe2334aa3c5. Native tests cover the finite model and deterministic audio generation/readback. The source was retrieved from the branch and its blob SHA matched. Full repo tests, final-head CI and independent review are separate acceptance items. No listening trial or physical materials experiment. Draft/HOLD for integrator review.
