# The Unchosen Note
## A score for instruments with identical repertoires and unequal moments of choice

**Claim class:** original finite formal construction, philosophical interpretation, experimental artwork and interface hypothesis. Not an empirical MHAC finding, not a reconstruction of Brier, and not a production interface specification.

The traditional score is an unusual kind of object. It describes something that may not yet exist, and a performance describes something that no longer exists. Between them lies a short-lived arrangement of possibilities: what the performer can do now. The arrangement is neither the printed score nor the recording. This expedition asks whether a recording can tell us anything about the disappearance of that arrangement.

Imagine three instruments. All start with the same note A. All are capable, over their performances, of ending in B, C or D. On the first instrument, the player chooses the ending after hearing A. On the second, an internal mechanism selects a single allowable ending before the player hears A. On the third, the mechanism permits two endings at a time, but its pair changes. An archive of performances may contain exactly AB, AC and AD for each instrument. The archive alone does not specify whether any performer had all three choices at the time of the second note.

The analogy to freedom is tempting. Resist its most expansive form. An instrument with many buttons can still be oppressive to use; an instrument with one well-understood button can be profoundly enabling. The formal question is not whether choice is good, but **where and when a particular modeled action is available**.

## 1. Three intellectual lenses

Gibson's ecological account treats possibilities for action as relational to the environment and the animal (1979, *The Theory of Affordances*, opening excerpt; see [source ledger](SOURCES.md)). Gaver's 1991 design account explicitly distinguishes an affordance from information about it, including cases in which information is absent or suggests a nonexistent action. His account of sequential affordances and auditory information is especially relevant. A sound may disclose a further action, not simply announce a state that has already happened. This motivates a distinction between a menu that exists, a representation of that menu, and the agent who knows it.

Music offers a second, independent motivation. In Carmen Pardo's IRCAM essay, Cage's use of chance and performance indeterminacy are discussed as distinct compositional approaches; Pardo also discusses performers' latitude within time brackets and whether they choose to be conducted in *Etcetera*. The examples suggest that the distribution of decisions across composer, mechanism and performer can be a compositional variable. The present experiment is not an account of all of Cage's practice, nor an attempt to recreate one of his works.

Finally, van Glabbeek's 1990 extended abstract distinguishes multiple behavioral semantics for finitely branching sequential processes, using testing scenarios as motivation. In the toy below, trace equality is deliberately weaker than the immediate menu observations. The classical process-theory distinction is not our invention. The original contribution here is the explicit tiny enumeration, musical interpretation, and proposed score/interface device, not a claim of a new general theorem about process algebra.

These three sources do not share an ontology. A graph transition is not an animal-environment affordance; an afforded action is not automatically an artistic choice; and indeterminacy is not equivalent to nondeterminism in a labeled transition system. The comparison is useful precisely because it leaves these gaps open.

## 2. The finite instrument

Let the continuation alphabet be U = {B,C,D}. A design F is a nonempty family of distinct nonempty subsets M of U. Each trial starts with audible A and a selected menu M in F. The selection is made by the mechanism; it is not controlled by the player in the base model. One permitted continuation is then played and the trial ends. An unavailable button has no sound and no state effect in the interactive toy. No probabilities or timing costs are assigned. Complete **successful** audible traces are just {Ax : x belongs to the union of F}. The prefix language adds the empty trace and A, equally for all nonempty F.

The guarantee of a precommitted action before the actual menu is known is the intersection of F. It is not the same as the set of actions a player can choose *after* the menu is disclosed. Even with no fixed guaranteed note, observing a nonempty menu always allows some successful selection under this model. The browser offers both disclosure modes and cycles menus deterministically: this makes experiments repeatable but potentially predictable. It does not instantiate a mathematically unknowable state or random choice.

| Design | Possible actual menus after A | Complete traces | Fixed guaranteed endings |
|---|---|---|---|
| Open | BCD | AB, AC, AD | B,C,D |
| Committed | B / C / D | AB, AC, AD | none |
| Overlapping | BC / BD / CD | AB, AC, AD | none |
| Anchored | BC / BD | AB, AC, AD | B |

The overlapping case defeats another shortcut: every realized menu has two options, every pair of menus intersects, but their total intersection is empty. Counting options, testing pairwise compatibility, and proving one common action are three different tasks.

The sound function maps each successful note to a fixed oscillator pitch; it does not encode the menu, selection mechanism, ownership or refused attempts. Thus the complete successful trace language is identical across these four designs. A live button probe or explicit menu disclosure introduces observations excluded from that language. We are not claiming equality under every observational protocol, nor equality of audio files captured with arbitrary human timing.

## 3. Exhaustive combinatorial experiment

Three notes yield 2^3 - 1 = 7 nonempty menus. A family is a nonempty subset of those seven, so the exhaustive population is 2^7 - 1 = 127 designs. Distinct designs have no probabilities in this enumeration; counts are combinatorial, not frequencies of real instruments.

A fixed singleton union admits one family. A fixed two-note union admits five: the seven nonempty families over its three menus, minus the two singleton-union families. Consequently a full three-note union admits 127 - 3(1) - 3(5) = 109 families. All 109 share exactly the same complete successful trace language. The experiment independently enumerates each family, computes union and intersection, checks those against per-note quantification, and reports the histogram.

| Intersection | Number of designs among the full-union class |
|---|---:|
| empty | 84 |
| B only | 7 |
| C only | 7 |
| D only | 7 |
| BC | 1 |
| BD | 1 |
| CD | 1 |
| BCD | 1 |

For a specified singleton intersection, the four eligible menus all contain that note and vary in the two remaining coordinates. Of the 15 nonempty families over those four menus, remove the families in which either free coordinate is constant; inclusion-exclusion gives 15 - 4(3) + 4(1) = 7. For a specified two-note intersection there is exactly one family containing both its two-note menu and the full menu. For full intersection only the full-menu singleton family works. The empty-intersection remainder is 109 - 3(7) - 3(1) - 1 = 84. This matches the executed enumeration.

Therefore any decoder which receives only the successful trace set and purports to recover the guarantee uniquely must fail on this class: identical input would require eight distinct answers. This is a narrow information-loss proof, not an empirical claim about listeners or a discovery that all recordings are informationally deficient.

## 4. The politics of a score (interpretation)

A score is sometimes treated as a distribution of responsibilities rather than a linear representation of sound. The distinction matters because there can be at least three different times at which a note is determined: when the composer writes the rules, when the machine realizes them, and when the player acts. Chance can shift a decision upstream without leaving any extra decision to the performer; an open menu can shift it downstream without changing the archive of possible sounds.

The recorded performance is consequently a peculiar witness. It records the exercise of a possibility while leaving most competing possibilities unexercised. The neglected object is the **counterfactual score**, a notation of the momentary menus, their owners and their expiry. Consider an improvised duet whose two participants are never allowed to improvise at the same time; its recorded phrases may be individually indistinguishable from a duet whose musicians could both intervene at any moment. A score for the second object could be concerned more with intervals of agency than with pitch.

An aesthetically interesting constraint is to make the option set shrink whenever a note is played, then reopen it at a musically meaningful boundary. The composition becomes a negotiation between the sound being produced and the future sound being withdrawn. A player may deliberately preserve an unattractive option because retaining it is part of the performance. This is artistic speculation, not a proposed objective measure of agency.

The danger in the metaphor is equally interesting. A collection of formal menus does not capture skill, embodiment, resources, contractual authority, social consequences, preferences, fatigue or the ability to refuse altogether. A person may have a real-world possibility that the model excludes, or a modeled button may be unusable. A fully disclosed list is also not equivalent to comprehension. In Gaver's terms, information about an affordance needs to be distinguished from the actual affordance and its perception. A count of edges is not a count of freedoms.

## 5. Exaptation: a counterfactual score editor

The original browser [instrument](instrument.html) realizes the four designs with the same three ending tones. Download the HTML and open locally. The player chooses whether the actual menu is disclosed; the machine cycles its masks across trials. The text exposes the possible and guaranteed sets and the realized trace. In disclosure-off mode the buttons are intentionally available as probes; refusal is reported visibly. This makes it a demonstration of the distinction, not a fair comparison of auditory displays. No network, recorded music or external library is needed.

A future synthesizer could give each step an independent **choice envelope**. A patch or sequencer would contain not just target parameters but a constraint over which future edits remain available. A preset could advertise the union (what can happen on some execution), intersection (what the engine can guarantee without a state query), actual menu (what the current engine knows), and provenance (who or what selected it). An operator could rehearse alternate branches before committing, with refusal rendered as a distinct event rather than silently interpreted as absence. A score editor could draw a second, ghost layer of never-played alternatives.

A practical software test follows without invoking aesthetics: two systems that pass an identical trace-corpus regression test may differ under a readiness probe. To preserve the distinction, snapshot actual menu, timestamp, scope of the observation, and authority separately from the emitted trace. A future benchmark should include a deterministic system as a negative control, a state that is disclosed but unusable by a particular actor, a stale menu, and a refusal whose side effects differ. None are implemented by this bounded oracle, and no safety or production requirement is claimed here.

Research question for later work: does a learned auditory cue encoding an option set aid exploration or merely create a new arbitrary code to memorize? Test against text/visual baselines and a no-cue control, separate detection from comprehension, and measure both false availability beliefs and missed available actions. Any real participant study needs the existing MHAC gates; this expedition has none.

## Reproduction and boundaries

Run Node 18+ with no dependencies: `node research/expeditions/unchosen-note/run.mjs`. [RESULTS.json](RESULTS.json) is the deterministic report generated from the same function body by the JavaScript execution tool (396 assertions passed); no Node invocation or browser playback was observed in that tool. The HTML embeds that same function body; DOM and Web Audio behavior still need browser qualification. The function rejects empty/invalid menus by design; it does not model deadlock, infinite traces, silent transitions, stochastic policy or general bisimulation. See [source ledger](SOURCES.md), [speculative score](AFTERWORD.md) and [checkpoint](CHECKPOINT.md).

Refs #205. The independent expedition complements, rather than supersedes, #197 (identity across successive changes), #199 (feature-level rhythm collision), #201 (selective clarification), #203 (destructive observation), and #183 (partial order). No canonical records or frozen protocol edits. No claim about human perception, preference, learning or agency is validated. AI-generated work; no independent human review.
