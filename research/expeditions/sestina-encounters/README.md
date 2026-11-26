# The Sestina That Cannot Introduce Everyone
*Poetic seams, balanced musical encounters and the difference between recurrence and encounter.*

2026-11-26 · Exploratory humanities/art research · #701 · AI-assisted writing, source encounter, mathematical derivation and software self-check by ChatGPT GPT-6.2. No human participants, independent reviewer or empirical result. Not part of frozen evidence synthesis.

## A room with six objects

A museum commissions six rooms, each containing a key, a glass, a wire, a bell, ash and a door. A visitor must encounter every object in every ordinal position across the rooms. The architect also insists that the last object in one room become the first object in the next. A statistician asks that every object immediately precede every other object exactly once *inside* the rooms.

These are different requests. A recurrence can sustain a relationship rather than distribute opportunities equally. The last object becoming the first is a hinge, not an introduction. It is a way of bringing something from one room into another without having to remember an explanation for it.

The sestina is a useful artistic opponent to the balanced experimental design. Neither is an incomplete version of the other. A poem may need exactly the repetitions an experiment would seek to counterbalance. The statistical designer wants to distinguish a stimulus from its immediate context; the poet may want to make the distinction impossible. An instrument can expose both ambitions as separate controls. Its score can determine not only what appears but what is allowed to meet.

## Source encounters (accessed 2026-11-26)

- Academy of American Poets, [Sestina](https://poets.org/glossary/sestina), sections Rules and History of the Sestina Form, including the six-row pattern and discussion of changing meanings of repeated endings. Full relevant web passage read. The institutional account attributes the form to Arnaut Daniel; no original Occitan text or historical performance was examined. The repeated endings are not necessarily acoustically identical in actual speech.
- Elizabeth Bishop, *Sestina*, as read in the transcript of Pádraig Ó Tuama's [Poetry Unbound episode, 12 November 2021](https://onbeing.org/programs/elizabeth-bishop-sestina/). Poem in transcript, six stanzas and envoi, read; selected commentary immediately following consulted. Audio not auditioned. My interpretation: recurrent domestic objects change their narrative occupations, rather than functioning as six interchangeable tokens. The poem's droplets, tears and illustrated figures make recurrence materially heterogeneous. The score below is newly written, not a reproduction or adaptation of Bishop's lines.
- Alan R. Champneys, Poul G. Hjorth, Harry Man, [The numbers lead a dance. Mathematics of the Sestina](https://ems.press/books/ecr/162/3078), 2018, DOI 10.4171/186-1/3, abstract only (subscription required). They investigate the spiral permutation, tent-map iteration and generalized sestina sizes. This is direct mathematical prior art for the permutation framing; the full chapter was not read, so no novelty assertion is made.
- E. J. Williams, [Experimental Designs Balanced for the Estimation of Residual Effects of Treatments](https://www.publish.csiro.au/ch/ch9490149), 1949, 2(2), 149–168, DOI 10.1071/CH9490149. Publisher metadata and [CiNii abstract, first paragraph and numbered description of single-predecessor balance](https://cir.nii.ac.jp/crid/1362544418714692224) read; publisher full text is paywalled. The abstract reports balanced designs with n sequences for even n and 2n for odd n. It concerns statistical residual effects, not musical aesthetics. The present mathematical fixture concerns only powers of one fixed permutation and does not reproduce the experimental analysis.

Interpretation: a score is a schedule of possible encounters, but a poem is not exhausted by that schedule. An identical token may play a completely different semantic role at the next occurrence. In Bishop's kitchen, the same material object can become an active participant in the narrative. Treating all its appearances as exchangeable would erase the artistic phenomenon. Conversely, a researcher cannot assume that an arbitrary motif has an intrinsic emotional or action meaning.

## Finite construction and exact result

Use n distinct labels 0..n-1, n rows, each starting from row zero (identity), with row t+1 at position j equal to row t at position p[j]. Restrict to one fixed permutation p, no envoi, no additional rows. Position completeness requires that each column contains every label once; equivalently p is a single n-cycle. Let encounter count D be the number of distinct ordered unequal consecutive pairs *within rows*. There are n(n-1) slots. Let S count equal last/first labels across the n-1 consecutive row seams. Boundary pairs are excluded from D. Do not confuse this with acoustic carryover or actual listening.

For the ordinary sestina p=(5,0,4,1,3,2), the six rows, in A..F notation, are:

    ABCDEF
    FAEBDC
    CFDABE
    ECBFAD
    DEACFB
    BDFECA

D=24, S=5. Six directed pairs occur twice and six never occur. Contrast p=(1,3,0,5,2,4):

    ABCDEF
    BDAFCE
    DFB EAC
    FEDCBA
    ECFADB
    CAEBFD

(The space in row 3 is visual only: DFBEAC.) D=30, S=0. Every directed unequal pair occurs exactly once. Both have complete positional coverage. Simple rotation p=(1,2,3,4,5,0) has D=6, S=0, another useful control. In the balanced form the fourth row reverses the first; a listener might hear something quite different from a sense of universal acquaintance.

Proof: assign each position j its phase c(j) in the cycle p, beginning at position zero. Then c(p(j))=c(j)+1 mod n. A row's consecutive pair at positions j,j+1 belongs to a cyclic orbit classified by the nonzero difference c(j+1)-c(j). Across the n rows that orbit visits exactly n ordered pairs. Hence D=n times the number of distinct consecutive phase differences. Full encounter coverage requires the n-1 differences to be all nonzero residues, with sum n(n-1)/2 mod n. This is zero for odd n (contradicting distinct endpoint phases), or n/2 for even n. Equal seams require p[0]=n-1, hence c(n-1)-c(0)=1. Thus for even n>2, full coverage and repeated seams are incompatible; for odd n>1 full coverage itself is impossible in this restricted n-row construction. n=2 is an exception. The result does not forbid arbitrary schedules, additional rows or other definitions of encounter.

A second rabbit hole: if the balanced n=6 rows may be reordered freely, their end-to-start equality graph consists of three disjoint reciprocal pairs, because the endpoint phase difference is 3. A linear ordering can join at most one directed seam per reciprocal pair, so at most three of five seams match, attained by row order 0,3,1,4,2,5. A separate native enumeration of all 720 row orders returned counts 240,288,144,48 for S=0,1,2,3. This extra check is not in laboratory.py. The relaxed rule sacrifices neither position nor encounter coverage but changes the fixed-permutation temporal grammar.

## Original poem — The locksmith's catalogue

Read as an original sestina using the six words key, glass, wire, bell, ash, door. This is artistic writing, not an account of a historical object.

The keeper entered carrying a key
that fitted nothing but the case of glass
in which a spider practised on a wire.
A note lay underneath a sleeping bell:
the factory was never made of ash,
although the inventory ended at a door.

There was no photograph beyond the door.
The clerk had made a drawing of the key,
and painted every shadow grey as ash.
The windows looked like instruments of glass;
the hour was a conjecture of the bell,
which had been disconnected from its wire.

A child returned the severed piece of wire
and asked what lay inside the painted door.
The keeper gave the child the smallest bell.
Its clapper could be lifted with a key.
They set it down beside the case of glass
and watched its shadow lengthen into ash.

The engineer proposed a model made of ash,
a plan to join the rooms with lengths of wire
and set their histories under sheets of glass.
A room would finish where began its door.
Each visit would supply a different key.
Each key would make acquaintance with a bell.

The statistician took apart the bell,
and numbered what had not been burnt to ash.
She set six chairs around a single key
and stretched between their legs a coloured wire.
No guest would twice arrive beside the door.
The invitations shimmered under glass.

The child drew a new window in the glass.
The keeper asked what could not meet the bell.
The child replied by pointing at the door.
There were two footprints in the model's ash,
both ending at the same discarded wire.
The keeper put them underneath the key.

Inside the glass the old machine preserved its ash;
the bell was drawn, but not attached to any wire;
the door was open, though the catalogue retained the key.

Reading proposal: the poem retains the seams by moving each end-word into the next stanza's first end-word. It does not assert that the same referent, action or sound recurs. The envoi is part of the poem but excluded from the finite oracle. A second performer may interrupt after each stanza with the corresponding missing ordered encounter, then discuss how the interruption changes the poem. That performance is proposed, not enacted.

## Audio laboratory and check record

Run: `python laboratory.py output` (stdlib Python 3.11+). Executed locally under Python 3.13.5. All 46,232 permutations for n=2..8 were tested, including 5,913 single-cycle/position-complete ones. The direct pair census agrees with the phase-offset oracle for every accepted candidate. Six-label histogram (D, S): (6,0):1; (6,5):1; (12,0):13; (12,5):5; (18,0):52; (18,5):8; (24,0):26; (24,5):10; (30,0):4. Exactly four of 120 six-cycles give all 30 directed encounters, none keeps repeated seams. Ten preserve all seams and achieve the maximum 24 under that constraint. Native checks passed, including n=2 exception and odd-n refusal.

Three 9-second original musical realizations (spiral, encounter, rotation) each consist of the same 36 quarter-second PCM tiles (six pitches each repeated six times, 220/247/294/330/370/440 Hz). Mono 16-bit PCM at 16 kHz, common gain, squared-sine envelope with two harmonics. The renderer verifies repeated render hashes, payload readback, frame count, amplitude bound and identical tile inventory by construction. No envoi, rests between stanzas, real listening or speech; the six musical objects are token analogues. The code writes receipt.json and WAVs locally. No binary outputs are committed. Source Git blob de3886ebb8deeb00d44355042abc42dc95a34768 matched the locally executed source upon readback.

## Instrument and research directions

The Encounter Loom is a proposed sequencer that separates three locks: equal ordinal positions, equal ordered encounters and repeated seams. It would retain each motif as a persistent sample or synthesis patch and allow the performer to alter only the transition grammar. On a 320x240 touch screen: six rows of six tiles, a 6x6 directed-pair matrix, and two counters for seam matches and absent transitions. In VSTi form, the pair matrix can additionally address a modulation lane: an encountered pair activates its corresponding FM index, resonator or filter envelope. Missing encounters become deliberately silent regions. In VSTfx form, record six source slices, replay in one of the qualified arrangements and route transitions to a separate voice. These are implementable directions, not qualified plugins or hardware.

Speculative duet: one musician maintains the poetic hinges; the other demands new meetings. Their disagreements trigger a third instrument whose only notes correspond to currently absent pair relations. If all pairs occur, it falls silent. The third musician can choose whether that silence is closure or an invitation to redefine the vocabulary.

For MHAC, a synthetic benchmark may expose the same message motifs in every position while undersampling certain predecessor contexts. A decoder that passes all positional tests might still fail after specific previous messages. Compare identical message inventories under spiral, rotation, balanced and independently randomized orders; evaluate per-directed-pair error, action correctness and latency separately, alongside conventional text. Reset/washout policies and genuine task dependencies must be explicit; pair coverage alone does not control higher-order context or fatigue. Do not infer actual carryover, musical preference or human decoding from the counting theorem. A plain transition coverage table may be sufficient.

Counterargument: balanced encounters can be dull, and recursive seams can be the essential characteristic of a composition. Neither invariant is an aesthetic metric. The purpose is to let an artist compose the disagreement, not to prescribe balance.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation and workspace read. Forty recent PR and forty open issue titles inspected; targeted searches for hocket, anamorphosis, gift, Oulipo, rhyme, sestina and related terms. #646 preserves local transition multisets; #494 studies collateral rule violations; #540 studies silent-window allocations. This work changes the transition census under fixed position coverage and studies seam constraints, not transition-preserving anagrams. Existing protocol/canonical manifests unchanged. Draft/HOLD for integrator review; no exact-head CI or merge asserted in this document. No human action necessary for this exploratory record.

*The archivist asked whether the bell had met every object. The locksmith answered that the bell had been in every room. The archivist corrected the catalogue; the locksmith retained the poem.*
