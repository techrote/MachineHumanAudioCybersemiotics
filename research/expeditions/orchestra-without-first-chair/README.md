# The Orchestra Without a First Chair

*Exploratory humanities/art research, 2026-11-26. Refs #664. Not a canonical research finding.*

## 1. A theatre with no privileged doorway

Imagine an orchestra installed around a perfectly circular room. The conductor is absent. Every chair receives the same invitation to play alone. No chair is numbered, no doorway is designated as front, and no prior soloist is remembered. The task is to select exactly one musician without making any distinction among them.

One curator says that the orchestra should remain silent. Another offers a die. A third paints a door on the wall. A fourth changes the commission: the orchestra may play a duet instead. These are four different ways of authoring the apparatus, not four interchangeable solutions to the original commission.

The artistic object of this expedition is the *origin of an asymmetry*. A solo is usually the product one hears; here the way a solo became possible is itself the score. The sound of an unanswered invitation can be a legitimate movement, rather than a defect that the engine must repair.

There is a trap here. A physical stage always has accidental differences: a temperature gradient, an audience member, clock skew, player skill. The thought experiment stipulates a mathematical symmetry, not a claim that a real orchestra has no distinguishing properties. What should count as an admissible difference is itself an authored decision.

## 2. Reading notebook: four encounters and a disagreement

- Elena Castellani and Katherine Brading's Stanford Encyclopedia entry [Symmetry and Symmetry Breaking](https://plato.stanford.edu/entries/symmetry-breaking/), substantive revision 2023-08-01, §1 (discussion of transformation groups and equivalence classes), §3 (paragraphs beginning “More precisely” through the modern deterministic-law reading of Curie's principle), and §4 opening paragraphs. Read those passages via HTML on 2026-11-26; not the entire entry or Curie's 1894 original. Its account distinguishes historical proportion from modern invariance and notes that the modern temporal reading of Curie's principle differs from Curie's functional relations. It also documents objections. Interpretation: the curator who expects an asymmetric selection from symmetric inputs may have omitted an explanatory variable. The computational proof below is not a claim about physical symmetry breaking.
- Dana Angluin, [Local and global properties in networks of processors](https://doi.org/10.1145/800141.804655), STOC 1980, pp. 82–93. Publisher-indexed abstract consulted; direct full-text retrieval failed. Angluin asks what processors must know about their identities and network in order to perform network-wide functions. Prior art for anonymous computation; no claim to have checked the full theorem or its proof in this paper.
- Avery Miller, Andrzej Pelc and Ram Narayan Yadav, [Deterministic Leader Election in Anonymous Radio Networks](https://arxiv.org/abs/2002.02641), 2020 preprint, §1.1–1.3 and abstract. Read these portions of the HTML version, not the full proofs. The radio model makes different wake-up times a potential source of asymmetry; simultaneous identical starts cannot create useful message exchanges under its stipulated collision model. Their distributed problem is not identical to our centralized rotation-equivariant set-valued choice. The interesting artistic extension is to let the time at which a musician becomes available become a resource, independent of the pitch played.
- David Revill, [John Cage](https://pas.org/john-cage/), Percussive Arts Society, Hall of Fame essay, paragraphs beginning “By the mid-1940s” and “Beginning with works such as ‘Music of Changes’” through the next two paragraphs. Read these portions on 2026-11-26; no original Cage score or complete Cage interview read. Revill describes chance operations as a disciplined change in the composer's responsibility, and recounts Cage's dissatisfaction with the reliability of affective musical communication. Cage's artistic response is not a recommendation to avoid explicit operational communication. Interpretation: choosing what to randomize is an exercise of authorship, not its disappearance.

All notes above are AI-assisted source encounters, not independently reviewed extractions; no external reader or participant was involved. No full source text is redistributed. These sources do not establish any listening outcome.

The disagreement: the physicist asks which changes are compatible with a law, the computer scientist which choices can be implemented, and the composer which constraints make a work interesting. The three questions are not equivalent. It would be a category mistake to infer equal moral worth from exchangeability, or to infer a musical virtue from a mathematical obstruction.

## 3. The exact finite construction

Let x be a binary ornament pattern on n equally spaced chairs. Rotation by s, denoted R_s, permutes their positions. The selection y is a binary mask of sounding chairs. A deterministic policy f is rotation-equivariant when f(R_s x) = R_s f(x) for all rotations.

Define H = {s : R_s x = x}. If h = |H|, then h divides n; the least positive cyclic period is p = n/h (take p=n if only the identity fixes x). Every H-orbit has h chairs because rotations act freely on chair positions. By equivariance, f(x) must be fixed by every element of H, hence its selected chairs must form a union of entire H-orbits.

Consequently the number of eligible invariant masks with exactly k chairs is binomial(p,k/h) if h divides k and 0 otherwise. This is also sufficient at this particular input: a fixed mask can be transported to all rotations of x, consistently because the stabilizer fixes it; define empty masks on other input orbits. This is an existence result for a centralized equivariant map, not an efficient local election algorithm. A nontrivial stabilizer prohibits a single-chair output.

Example: x=1010 on four chairs has h=2; exactly two nonempty proper invariant selections exist, 1010 and 0101. An asymmetric ornament can make h=1 and allow a unique chair. Ornament bits are visual input labels, not a constraint requiring only ornamented chairs to play. Selecting a lexicographically canonical rotation and mapping a fixed mask back works only when the result is independent of all tied rotations.

The apparently neutral fallback “pick the first array element” secretly introduces an origin. A memory of yesterday's chair similarly creates an asymmetric state. Neither is wrong if openly authored. Neither can be described as selecting from the original symmetric input alone.

### The finite lottery

A different contract permits each of m eligible chairs to draw an independent uniform integer in 0..q-1. If the maximum is unique it wins; otherwise the whole round is discarded. For a particular chair to win with value j, every other value must be strictly smaller. The exact success probability is

P = m * sum(j^(m-1), j=0..q-1) / q^m, m>=2, q>=2.

All chairs have identical probabilities, including conditional on success. This is ensemble symmetry, not invariance of each realized winner. With r independent fresh full rounds the chance of no decision is (1-P)^r. Unbounded retries terminate almost surely, not with a finite guaranteed deadline. This model uses a central view of all draws; it is not an implemented distributed protocol. A tie-only retry is another policy and is not covered by the full-redraw formula.

For four chairs and a two-value draw, P=1/4. After three rounds the unresolved probability is 27/64. With four draw values, P=9/16; after three rounds it is 343/4096. With six draw values, P=25/36; after three it is 1331/46656.

The composer can now choose how frequently an invitation goes unanswered without changing the candidates or introducing a fixed preferred chair. There is no suggestion that randomness repairs unequal real-world power.

## 4. An original performance score: Five Invitations to the Centre

Four performers sit in a ring. Use quiet sustained tones or noise; any pitches may be chosen, but the allocation apparatus must not use pitch or timbre to resolve a tie. All movements have six four-second slots. Silence is a scored outcome, not a pause that must be filled.

I. **The empty rostrum.** With all ornaments identical, request a singleton six times. Apply the equivariant refusal rule. Nobody is selected. Ambient sound is not part of the allocator.

II. **Two pairs.** Place identical cards on opposite chairs, leaving the others bare. In odd slots the marked pair sounds; in even slots the unmarked pair sounds. Each selection is invariant under the remaining half-turn. Do not split the pair. The order is authored by the score and not inferred from an unnamed chair.

III. **The door.** Place a single new card at one chair. It is the designated origin; select that chair in each slot. Rotate the whole scene including the card once midway, preserving the relationship rather than the array index.

IV. **The finite republic.** Remove all cards. In each slot every chair draws one bit, independently. A unique maximum earns that slot's solo. On a tie, try a fresh set of bits, up to three total rounds. If still unresolved, retain silence and show the tie status. Draws can be prepared offline. Do not rig draws to avoid empty slots.

V. **The archivist's forgery.** Repeat the selected chair sequence of IV exactly, but make the sequence a fixed score rather than a live draw. Preserve the different provenance labels. The same allocation can be produced by distinct mechanisms. If the performers improvise, the sound need not be identical; to make an exact audio comparison use the same stored stems and deterministic gain envelopes.

Optional ending: reverse the score's priorities. Rather than requesting a solo, request the smallest nonempty invariant choir. On a fully uniform n-chair ring that choir has n members; on a periodic ring its size is h. The aesthetic point is the changing size of a collective, not a moral claim about collectives.

The score is original and unperformed; no sound recording or listening trial is asserted.

## 5. Exaptation and adversarial questions

The proposed **First Chair Loom** is a bounded voice allocator with independently editable transformations, ornament patterns, target voice count and resolution policy. A CYD touch interface could use a rotating ring of cells; long press paints an anchor, ordinary touch changes an ornament, and a separate explicit command requests a solo. The status strip distinguishes INVARIANT CHOIR / NO UNIQUE SELECTION / ANCHORED / DRAWN / DRAW EXHAUSTED. The touch coordinates themselves are an anchor only when deliberately admitted by policy. Rotation of the UI must not silently change the selection.

A VSTi could generate polyphonic chord fragments whose voice-count constraints are resolved by orbit unions or an explicitly seeded lottery. A VSTfx could allocate equal-status grains to a single accent channel, retaining dry input and bounded output levels. Use fixed-capacity arrays and precompute orbit masks and bounded draw schedules away from the real-time callback; no unbounded retry in audio processing. A large spatial oscillator field could assign different local symmetry groups to neighbouring territories; adjoining regions might have incompatible admissible choir sizes.

Research proposition: compare visually or acoustically encoded refusal, explicit textual tie status, and apparently decisive fixed-index fallback in a synthetic resource allocation task. Measure correct attribution of selection policy, understanding of unresolved outcomes, latency and actual task correctness separately. Test whether a conventional status indicator is sufficient. No empirical advantage is claimed.

Counterexample: real candidates may have different eligibility or stakes. Equal probability of winning is not equality of outcome, and symmetry with respect to the wrong transformation can be actively misleading. The instrument must expose which attributes it ignores. Another counterexample: a fixed origin may be the simplest, most comprehensible musical control. Do not fetishize equivariance.

Operational MHAC must distinguish “no unique preference”, “cannot decide with the current policy”, “randomly selected” and “authorized action”. A refusal to select a solo is an aesthetic option here, not a substitute for an operational fallback, a required warning, or a safety procedure.

*Speculative afterword:* The orchestra requested a first chair. The architect drew a door. The musicians walked around the room until they found it. At the next concert the architect removed the door but left its reflection in the mirror. The orchestra chose the mirror. The architect wrote down what had become an input.

## Repository and execution receipt

Live AGENTS, README, RAG, programme, runbook, integrity and validation authorities were read; 40 recent PR titles and 30 open issue titles plus targeted issue searches (symmetry, tie-breaking, Buridan, equivariance, canonical representative, leader election) inspected. #212 issue body and comments were fetched: its name-alignment and anchor problem is closely related but distinct from allocation cardinality under a known cyclic symmetry. This is not a comprehensive novelty search.

Base main at intake: 495a98ca12bae467a507031f04931aa4254b1866. Fresh branch mhac-664/orchestra-first-chair. Only files under this expedition are changed. Draft/HOLD for mergedown; no protocol, manifests or canonical evidence touched. AI-assisted by GPT-6.2; no independent human review, no participant recruitment, no production implementation.

Run `node laboratory.cjs`. Native Node v22.16.0 execution exited successfully using source whose Git blob is 5b0ef70f572a581ea4ffaa6e1d92aaee0b6a6bec, matching branch retrieval. Exhaustive binary patterns n=2..10: 2,044 inputs, 1,398,096 candidate mask checks, 20,476 histogram-bin comparisons. Lottery m,q=2..6: 25 cases, 82,174 tuples, equal per-chair win counts and exact tie counts checked. Three explicit symmetry counter-controls passed. These are finite software checks, not independent experiments. Full repository suite and exact-head CI not yet qualified at writing. No merge or issue closure asserted.
