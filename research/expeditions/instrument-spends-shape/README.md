# The Instrument That Spends Its Own Shape

**Expedition X794 — 27 November 2026 — exploratory humanities, artistic research and synthetic mathematics. Draft/HOLD.** [Issue #794](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/794). Not a frozen-protocol extraction, reviewed empirical finding, production instrument or claim of mathematical priority.

## The organ maker's mistake (original fiction)

A musician asks an organ maker for a keyboard whose keys change whenever they are played. The maker supplies a different sound after every note. The musician objects: she does not want a keyboard with an immense number of sounds. She wants a keyboard with an exhaustible number of gestures.

The maker supplies a single resonating strip, marked with seven potential cuts. A cut destroys one resonator and gives birth to two. Neither child can restore the parent within the performance. A second performer listens only to the moment of division; a third listens to the surviving pieces. At the end every piece is a unit of the same size. Three performers arrive at the same instrument by three different routes.

A conservator acquires the eight pieces, places them in a case, and declares that she has acquired all three performances. The musician asks whether she has also acquired the act of cutting.

## Reading Clark: the object as a condition rather than the work

**Source claim.** Lygia Clark, [Caminhando (1964), archive ID 6275, transcription 061.3.8.1](https://www.portal.lygiaclark.org.br/acervo/6275/caminhando), Portuguese typescript transcription, read in full on 2026-11-27; not checked against the manuscript image. In the opening three paragraphs, Clark describes an ordinary paper strip joined with a half twist, the participant cutting lengthwise, and the choice of which side of the previous cut to continue on. The shrinking width eventually prevents continuation. In the paragraphs beginning Cada Caminhando and À relação dualista she explicitly contrasts the act with her earlier object–participant relationship. The later passages on the landscape seen from a train and her architectural attempts widen the question from manipulation to lived time and shared space. She writes, “A obra é o seu ato” (my working translation: the work is your act). This is a philosophical and artistic proposition, not a measured psychological outcome. MoMA's [Caminhando audio guide](https://www.moma.org/audio/playlist/181/2419), dated artwork 1963, confirms the basic procedure; distinguish artwork date from the 1964 text.

**Source claim.** [MoMA, Bichos (as a group)](https://www.moma.org/audio/playlist/181/2403), full short transcript, read 2026-11-27. Curators Connie Butler and Luis Perez-Oramas describe hinged metal forms, their instability and absence of a single ideal orientation. Their account establishes the intended audience manipulation, not an exhaustive mechanical configuration space. In contrast, Clark's cutting proposition materially alters the conditions of the next action. A hinge can usually be moved back; a severed sheet is not made whole simply by reversing a gesture.

**Source claim with metadata caveat.** [A propósito da magia do objeto (1965), archive ID 10170](https://portal.lygiaclark.org.br/en/archive/10170/a-proposito-da-magia-do-objeto), Portuguese transcription, read in full 2026-11-27. Archive description attributes the text to Clark, while the author field is marked unknown; attribution is therefore provisional at document-catalogue level. Opening paragraphs contrast the poetic charge of an ordinary object with the poetic act itself. The paragraph beginning Na primeira vez asks the participant not to calculate prior and subsequent cuts during the experience. The later paragraph beginning Talvez o homem argues that manipulation or participation alone is insufficient. Clark's claims about freedom, transformation and direct communication are philosophical assertions rather than demonstrated effects.

**Interpretation.** An interactive synthesizer is not necessarily a participatory artwork in Clark's stronger sense. An enormous parameter space can still reduce the performer to selecting finished objects from a menu. Conversely, a small repertoire may permit a gesture to create a new condition for subsequent gestures. The difference is not a number of choices; it is what a choice changes. The cutting instrument below is an intentionally artificial proposal for making the expenditure of a possibility audible.

A difficulty arises: displaying a remaining-possibility count makes this instrument a little game of optimization, precisely the kind of anticipatory calculation the 1965 text resists. This is not a defect to be hidden. The proposal should offer a blind mode in which no count, genealogy or suggested optimum is displayed. The analyst may record its structural history independently, if the performer agrees. An interface can be valuable as an inspector without being suitable as a performance surface.

## A collection of future occasions

**Source claim.** Martha Joseph, [Collecting Alvin Lucier's I Am Sitting in a Room](https://www.moma.org/explore/inside_out/2015/01/20/collecting-alvin-luciers-i-am-sitting-in-a-room/), MoMA, 20 January 2015. Read the complete essay on 2026-11-27. Opening paragraphs recount iterative room playback and rerecording; the acquisition discussion beginning How does a museum acquire distinguishes an archival recording from the ability to enact the work in the future. Closing paragraphs distinguish particular recordings from that ongoing capacity. The score and recordings were not examined in this expedition. Lucier also appears in MHAC #414 (reciprocal environmental coupling); this investigation instead concerns what an archive can establish about a sequence of structural edits.

**Interpretation.** The museum may preserve an invitation, an occasion, or a process rather than merely a terminal object. A digital instrument offers a further disjunction: the designer can preserve the rules of a performance, its particular action history, or its terminal state. None is necessarily an adequate substitute for the others. There is a temptation to describe a perfectly replayable trace as the performance itself. Clark's emphasis on the present act provides a reason to resist that equivalence: it does not follow that another person's replay has reproduced the experience of deciding. Nor does one recording exhaust Lucier's performance proposition.

## The Cut Organ — declared synthetic construction

Use n ordered unit cells occupying the half-open interval [0,n). Initially one live interval covers all cells. A cut at an integer interior boundary k replaces its unique live parent [a,b) with [a,k) and [k,b). Repeated or exterior cuts fail closed. No joining operation is permitted during a performance; reset is an explicit new performance, not a physical assertion of irreversibility. The construction models a LINEAR interval, not a Möbius strip, textile stress, fracture mechanics or bodily perception.

Three independently meaningful records:

* The current partition: live intervals only. Determines available future cuts in this particular model.
* The genealogy: each cut boundary and its parent interval. Determines which splits must precede which others but forgets the interleaving of independent branches.
* The chronology: ordered accepted cuts, sufficient to replay the symbolic session from its declared initial state. Does not establish actor identity, actual sound hardware output, perception, consent or authorization.

For eight cells, compare:
- L: 4,2,6,1,3,5,7.
- R: 4,6,2,7,5,3,1.
- C: 1,2,3,4,5,6,7.

All terminate in the same eight unit intervals. L and R have the same genealogy, but different intermediate partitions. C has a different genealogy. Thus neither terminal partition nor genealogy is sufficient to identify the chronological performance. Conversely, different histories need not imply different future affordances: after all cuts, none of the three has a further legal cut. This is an explicit negative case against making provenance and operational state interchangeable.

### Mathematical derivation (elementary, no priority claim)

There are (n-1)! complete histories, because every interior boundary can be used in any order and belongs to exactly one live interval until cut. The first cut determines the root of a plane full binary tree with n ordered leaves. Recursively the left and right subintervals determine its children. The count T(n) obeys T(1)=1 and T(n)=sum over k=1..n-1 of T(k)T(n-k). The Catalan solution is T(n)=binomial(2n-2,n-1)/n. One way to derive it is to let F(z)=sum over n>=1 of T(n)z^n; F=z+F², with the zero-constant solution (1-sqrt(1-4z))/2. Expanding gives the stated coefficients.

For a particular tree with first cut k, left subtree with k leaves, right with n-k leaves, let H(T) count compatible chronological histories. After the first cut, the two subsequences can be interleaved while preserving their own order. Therefore H(T)=binomial(n-2,k-1)H(L)H(R), with H(leaf)=1. Iterating gives the rooted-tree hook-length form: H(T)=(n-1)!/product over internal nodes v of s(v), where s(v) counts internal nodes in that subtree (including v). This follows from cancelling factorials at each recursion, not from an empirical result.

A genealogy determines a unique chronology exactly when it has no internal node with two nontrivial subtrees. For n>=2 there are 2^(n-2) such comb trees: each of the n-2 choices above the final pair selects which side contains the continuing subtree. A maximally balanced eight-leaf tree has 80 compatible chronologies (root interleaving 20, two child interleavings 2 each). This is the L/R example. The C genealogy has exactly one.

An important qualification: counting histories is not measuring the psychological freedom of a participant. A set of equally valid future operations need not have equal meaning, accessibility or value. A physical cut involves resistance and cannot simply be equated with a discrete transition.

### Executed finite qualification

Run with Python 3.11+ standard library:
```sh
python laboratory.py audio
```
Executed twice in native Python 3.13.5 on 2026-11-27. Both runs produced identical audio and receipt bytes. The test enumerates all 46,233 complete cut histories for n=2..9, uses a dynamic interval simulator and a separate recursive first-cut oracle, verifies partition coverage at every stage, compares per-tree multiplicity with the interleaving formula, and checks Catalan counts. Three illegal cut sequences rejected. It is a same-agent computational cross-check, not independent peer review.

| Cells | Histories | Genealogies | Largest observed history class | Unique-history genealogies |
|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 1 | 1 |
| 3 | 2 | 2 | 1 | 2 |
| 4 | 6 | 5 | 2 | 4 |
| 5 | 24 | 14 | 3 | 8 |
| 6 | 120 | 42 | 8 | 16 |
| 7 | 720 | 132 | 20 | 32 |
| 8 | 5040 | 429 | 80 | 64 |
| 9 | 40320 | 1430 | 210 | 128 |

Largest class sizes are finite observations, not a proposed general maximum formula. The renderer is deliberately limited to eight cells, and no real-time callback claim is made.

## Three Studies for an Exhausted Instrument (original score)

Three four-second stereo recordings, L, R and C, with eight half-second blocks including the original uncut strip. Left: every current interval sounds a sine voice with frequency 100+21*(b-a)+7*(a+b) Hz. Right: a decaying pulse with frequency 170+53*(b-a) Hz for the parent interval of the just-accepted cut. Stage boundaries use 10 ms ramps; phase resets at each block by design. The mapping is arbitrary artistic material, not an auditory code proven to reveal parentage.

Listen to L and R. Their genealogy is shared; their histories are not. Listen to C. Its successive cuts create a different series of parent lengths. The final half-second is sample-identical in all three editions, including the last pulse because all last parents have length two. The three full recordings are distinct. No listening experiment occurred.

For a live fourth study, draw an eight-cell strip on paper. At each cut, hum a sound for the disappearing parent, then choose independent sounds for its two children. Stop when you wish, even if cuts remain. Do not consult a target arrangement. If you wish to repeat the work, use a new strip. A participant who does not want to cut can choose boundaries verbally or with a switch. This is an original score inspired by Clark, not instructions for reconstructing her artwork.

For a fifth study, let the surviving children remain silent until a different person discovers them. The cut belongs to one performer, the recognition of a new instrument to another. Keep the two clocks separate.

## The second rabbit hole: an instrument that can retire

The usual software design demand is that every action be reversible. The artistic premise here deliberately limits reversal inside a disposable sandbox. The player can stop, discard or reset the session; the interface should never delete their files or compromise real data. Expenditure is an explicit compositional convention, not a claim about digital materiality.

A more ambitious instrument would offer different inheritance laws: split a resonator into two children with conserved total oscillator amplitude, conserve energy instead, or allocate energy asymmetrically; keep the dying parent's residual tail in a separate channel; let children inherit filter histories or acquire new ones. Amplitude and energy are not interchangeable, and such DSP would need actual stability and headroom tests. These are proposals, not functionality in the renderer.

The potential for CYD is unusually direct: an eight-cell touch strip with live intervals as colored bars; tap an interior boundary to cut. Use the XY pad to set the two children's resonant parameters, not to silently alter their genealogy. At the final cut, the instrument retires into a sustained chord. A new patch explicitly creates a fresh strip. For an accessible performance, buttons and MIDI note equivalents should duplicate touch gestures. A VSTi could maintain a preallocated voice pool, bounded event queue, crossfades and session-scope undo rules; a VSTfx could operate on explicit multistem segments, not infer arbitrary source identities. FM-1 could prototype split gestures through a fixed finite pool of carrier/modulator templates. None is implemented or qualified here.

## MHAC implication and opposing view

The narrow engineering lesson is that equality of state, ancestry and chronological history are distinct predicates. A state hash cannot prove a particular ordered history; a genealogy can preserve dependencies yet omit interleaving. Conversely, a complete symbolic trace cannot establish execution outside that model. Use a plain ordered event ledger as the baseline for any future interface experiment; compare a typed split-event receipt and optional acoustic accompaniment while deliberately varying duplicate, missing and reordered receipts. Include a negative case where two legal orders commute to the same final state. Distinguish event association, state reconstruction, false historical claims, task latency, workload and artistic preference. No acoustic communication advantage is established. No human trial is authorized or performed.

The mathematical argument is nearly the opposite of Clark's project: it renders each gesture countable, serializable and reproducible, eliminating bodily materiality and contingency. The artistic value may lie in that tension rather than in an allegedly faithful translation. There is no reason to require the performer to become an archivist. The inspector can be optional, and the archival copy need not be the principal work. A safety-critical operational interface, by contrast, cannot hide relevant execution evidence under the pretext of artistic freedom.

## Checkpoint

Base 495a98ca12bae467a507031f04931aa4254b1866. Reviewed live AGENTS, RAG, README, research README, programme, runbook, integrity and validation; 45 recent PR titles, 30 active issue results, targeted issue searches for Clark, Oiticica, Bichos, clinamen, cut order, partition history, irreversible operations, binary trees and adjacent themes. Earlier normativity and estrangement directions were set aside because of #398 and #430. #414 issue read, overlaps distinguished above; #786 concerns stopping frontiers rather than complete destructive partition histories. Issue #794 created and comments checked (none at creation). Branch owns only this directory. No evidence registry, manifest, protocol, shared index, other worker's branch, participant data or source corpus modified.

One AI assistant (GPT-6.2) read the identified online textual passages, wrote the original interpretation/score and implemented/executed the synthetic laboratory. No external review. Exact-head repository CI and integration acceptance are separate from local laboratory tests. Draft/HOLD for mergedown.

*The instrument maker asked which of the eight pieces was the work. The musician asked for a new strip.*
