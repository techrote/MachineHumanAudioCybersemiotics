# The Note That Advertises Its Prohibition

**Status:** exploratory humanities / artistic research, proposed, not a canonical MHAC finding.  
**Date:** 2026-11-26. **Issue:** [#650](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/650).  
**Branch base:** 495a98ca12bae467a507031f04931aa4254b1866.

## The two mouths of a prohibition

Imagine a concert in which the organ never plays two consecutive A notes. In the first version nobody announces the rule. In the second a miniature loudspeaker plays two consecutive A notes before the organ begins. Its purpose is to demonstrate what the organ will not play. A third version replaces the miniature speaker with a sign: NO AA. A fourth organ has no restriction at all but happens to play the same phrase.

Which concert contains the prohibition? The first contains it as a production rule; the second also performs its forbidden object; the third offers a description; the fourth has merely produced an instance consistent with the rule. These are fictional scenarios, not observations of listeners.

A negative score is a specification of excluded performances. A declaration of that score is a second performance. Neither determines the first performance's probability law.

This difference offers a new musical material: the distribution of permitted events, plus a potentially audible account of what was excluded. The two should be independently editable. A musician might wish to hear a denied note in a separate margin, or never hear it. The margin is not a privileged channel of truth: it may contain an illustrative example, an actual rejected proposal, an invented alternative, or a misleading caption. These should be tagged separately.

## Source encounters and boundaries

The following are selected, AI-read passages, not systematic searches or accepted Track G extractions. All accessed 2026-11-26. No external human review.

- A. Francisca Snoeck Henkemans, “Manoeuvring Strategically with Praeteritio,” Argumentation 23 (2009), 339–350, DOI [10.1007/s10503-009-9153-z](https://link.springer.com/article/10.1007/s10503-009-9153-z). Publisher HTML, abstract, selected introduction, example (13)–(15) and §4 read. The author distinguishes genuine omission from formulations that advertise an omission while communicating the ostensibly withheld material, and argues that the latter can combine concealment and emphasis. The classical description in Rhetorica ad Herennium IV.27.37 was encountered **through her quotation**, not independently checked against a Latin edition. Her account concerns argumentation; it is not an auditory effect study. Counterpoint: the same syntactic construction may genuinely withhold information. A compositional declaration is not necessarily deceptive.
- Oulipo, [Lipogramme](https://oulipo.net/fr/contraintes/lipogramme), French definition and example paragraph read (web text). The restriction excludes letters and consequently words containing them; the page names Perec's La Disparition as an example of omitting e. No complete reading of the novel. This is direct artistic precedent for productive exclusion, not evidence that an audience discovers a rule unaided.
- Sarah Meller, [The Writing Is On The Wall](https://whitney.org/education/blog/john-baldessari-i-will-not-make-any-more-boring-art), Whitney Museum, 9 July 2010, paragraphs following the work caption, including the discussion of the initial punishment piece and pedagogical conflict. The 1971 Baldessari work directs participants to repeatedly inscribe a pledge against making boring art; Meller identifies a tension between the pledge and the repetitive work. Institutional interpretation, not a measurement of boredom. The pledge is an object of the work, rather than a guarantee of its aesthetic quality. No original artist correspondence consulted.
- Alexandre Papadopoulos, François Pachet, Pierre Roy, Jason Sakellariou, “Exact Sampling for Regular and Markov Constraints with Belief Propagation,” CP 2015, pp. 341–350. [Author-hosted publication page](https://www.francoispachet.fr/publications/exact-sampling-for-regular-and-markov-constraints-with-belief-propagation/), bibliographic metadata, About and Abstract summary read, not the proceedings paper. Describes exact conditional sampling combining Markov models and finite automata. This is direct engineering prior art for the construction below; no novelty in exact constrained sampling is claimed.
- François Pachet and Pierre Roy, “Markov constraints: steerable generation of Markov sequences,” Constraints 16 (2011), 148–172, [DOI](https://link.springer.com/article/10.1007/s10601-010-9101-4), publisher abstract and metadata read. They formulate constrained generation to avoid limitations of greedy left-to-right methods. The present binary example is much narrower. No comparative algorithmic performance claim.

## Critical essay: a ban can be a productive force, but it cannot explain itself

The rhetorical and lipogrammatic gestures conflict. A lipogram can withhold its forbidden letter from the surface. Praeteritio can convey the very thing it says it will omit. In an exhibition these could become two pieces using the same score. The first hides its rule; the second stages a demonstration of the restriction. In neither case is a rule logically recoverable from a single successful performance.

Baldessari offers a further complication. The content of a pledge is not a criterion sufficient to establish its fulfilment. A score which announces “no boredom” has not made boredom formally decidable. By contrast, the prohibition AA below is syntactic and testable. We should not pretend the latter establishes a method for avoiding the former.

There are at least four mechanisms commonly blurred by the word 'negative': a hard production constraint, a probabilistic aversion, editing a completed work, and a performed account of restraint. Only the first is implemented in the combinatorial example. The stereo rendering is a deliberate theatrical instance of the fourth. The other mechanisms remain proposals.

Even a perfectly enforced ban does not specify how the remaining possibilities are treated. Suppose a musician's choices are A and B. A local rule permits a fair choice at each step unless A has just occurred, in which case B is compulsory. A second performer chooses a complete legal phrase uniformly. The two produce exactly the same language of possible phrases, yet assign different weights to its members. To call either performer fair without naming the unit of fairness is an editorial decision, not a mathematical result.

The philosophical risk is to mistake this mechanical distinction for a claim about human agency or meaning. A score is not a legislature; a sound is not a proposition without a suitable interpretative relation. We can make different selection processes audible in an installation without arguing that the machine has a conscience or that a listener can infer its rule.

## Exact finite construction

Alphabet A, B; phrase length n; no adjacent AA; initial previous symbol is B (equivalently no restriction on first symbol). Let C(n,p) count legal completions after p. Boundary C(0,A)=C(0,B)=1. Recurrence:

- C(n,A)=C(n-1,B).
- C(n,B)=C(n-1,A)+C(n-1,B).

Thus total C(n,B)=F(n+2), with F(0)=0, F(1)=1. This is the standard Fibonacci word count, not new mathematics.

For the local policy every choice is equiprobable among currently admissible symbols. For any valid word w, let k(w) be the number of A symbols in its first n-1 positions. Exactly k steps are forced. Its probability is 2^(k-n). The global policy instead gives each word probability 1/C(n,B). At length two the complete outcome list is AB, BA, BB; local probabilities 1/2, 1/4, 1/4, global probabilities 1/3 each. Both reject AA exactly.

The global policy can be realized without rejection by choosing a uniform integer rank in [0,C(n,B)-1] and lexicographically unranking with completion counts. Branches partition the rank interval into consecutive subintervals of sizes equal to the respective legal completion counts. This establishes bijectivity by induction. The probability of an initial A under global sampling is F(n)/F(n+2), approaching 1/phi^2; under the local policy it is 1/2 for every n>=1.

Total variation is half the sum of the absolute probability differences over the valid words. It measures distributional difference, not perceptual distance. For n=16, there are 2,584 valid words and TV=0.3180781975619195. All-B has probability 1/65,536 locally and 1/2,584 globally. Neither outcome is prohibited.

The lab enumerates all binary candidates for n=1..16 and tests the completion count against a separate literal substring rejection, local mass normalization in integer units of 2^-n, first-symbol counts, and all unranked words against the enumerated lexicographic list. Negative ranks, fractional ranks and the empty boundary are checked. Integer intermediates are exact within these tested bounds; do not extrapolate the Number implementation to arbitrary n without using BigInt and reviewing overflow. Executed in the JavaScript tool environment, not yet native Node. No timing benchmark.

## Artistic score: The Margin of the Organ

A and B are original oscillator pitches at 220 and 330 Hz. Each cell is a quarter-second, with short fades. A dash is a rest. The two channels represent separate fictional stages. The rule excludes AA within a phrase on the left stage only, not across phrase boundaries or in the right margin.

I. Silent rule: left --ABABBABBA-, right twelve rests. Do not present the prohibition.
II. Declared rule: identical left part; right AA followed by ten rests. The opening margin intentionally demonstrates the excluded phrase. This is an example, not a log of actual rejected notes.
III. Local quota: repeat the list AB, BA, AB, BB three times with one rest between phrases. Right silent. This exhibits the exact two-cell local proportions by deliberate construction, not random sampling.
IV. Global quota: repeat AB, BA, BB four times, same rests and durations. Right silent. These are quotas, not samples or listening results.
V. Unperformed law (live optional): remove the prohibition without altering the first movement. Permit an audience member to ask which policy produced the performance. Answer with the score and its provenance, not with an inference about what they must have heard. This movement is written only, not rendered.

A possible staging: the right margin is a smaller speaker near an explanatory placard. Replace its cue with a picture or silence for further versions. Do not imply any response is compulsory. The artistic purpose is to produce different relations between performance, declaration and expectation.

The first two audio renderings have identical left PCM sequences and distinct right sequences. The quota movements have the same length but differing authored proportions. These are deliberately selected demonstrations of a finite model; none is a statistically drawn performance. The renderer is an offline Python 3.13.5 standard-library script with deterministic rerender, bounds, WAV readback, channel identity and quota assertions. No human listening or physical apparatus.

## Exaptation: the Negative Score Loom

An instrument could retain four explicitly distinct panels: (1) a symbolic phrase grammar; (2) hard constraints as a finite automaton; (3) probability policy; (4) optional annotation/margin routing. Controls: draw a forbidden word; show the state reached by each prefix; choose local choice, uniform complete words, or a base model conditioned on success; preview completion counts; audition a rejected example separately from an actual rejection; change or clear the rule between phrases; preserve the clean primary output.

A useful VSTi prototype would use a small fixed alphabet and bounded lookahead with precomputed completion counts off the audio thread. For embedded CYD, begin with a 2–4 symbol touch sequencer, length up to 16, forbidden-word state and a tiny probability panel. The negative score is explicitly displayed. The operator can elect a decorative annotation bus. A VSTfx version would reorder authored grain IDs under a finite grammar, not attempt to identify or remove forbidden semantic content in arbitrary audio.

Potential extensions: multiple forbidden motifs using a prefix automaton; weighted completion masses to preserve a nonuniform prior conditional on a constraint; horizon-independent finite-state generation; a separate counterfactual composer who writes hypothetical rejected phrases without fabricating audit events. If no legal completions exist, return a distinct unsatisfiable score status rather than playing a misleading empty success. The present lab handles only no-AA and a nonempty language.

Counterargument: the declaration bus may spoil the expressive indeterminacy of the work, or may become an unwanted secondary composition. An audience may not recognize the ban from either channel. Offer an unannotated mode. A trivial sequencer with a rule label may be more usable than a new synth. No advantage has been demonstrated.

## Operational MHAC boundary and falsification

A valid output cannot by itself establish that a policy was enforced; a prohibited outcome may simply not have occurred. In a synthetic test compare rule labels, sample trajectories and actual execution traces with policy-version identifiers. Distinguish correctly identifying the policy, correctly predicting a future transition, and correctly choosing an action. Include an unrestricted process that happens to generate a legal phrase and a truthful explicit-text baseline. A label is also not proof that a policy was applied.

A separate “rejected proposal” audio stream must not be treated as an operational command and must not disclose otherwise protected material. The art's demonstration of the forbidden object would be inappropriate in a real confidentiality or safety setting. Do not route consequential cues through the experimental exclusion grammar. The operational question may be entirely answered by conventional structured logs and explicit rules; retain that negative possibility.

## Speculative coda — The exhibition of a forbidden note

The organ played the same tune for forty nights. A clerk finally wrote a sign declaring that the organ was forbidden to repeat its lowest note. On the forty-first night the clerk installed a small loudspeaker which repeated the note twice. The organ was not connected to the loudspeaker.

A visitor asked why the sign was necessary. The clerk said the organ had been obedient before the sign was written.

The curator asked to see the instrument's rule.

The clerk returned with forty programmes. The curator asked again.

## Reconciliation and receipt

Before editing: live AGENTS, README, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY, VALIDATION and research README consulted. No nested AGENTS files found at research/ or research/expeditions/. 45 recent PR titles and 40 open issue titles reviewed, plus targeted issue searches for apophasis, praeteritio, preterition, negative capability, cadence, anticipation, reticence, lipogram, forbidden motif, constrained sampling, negative score and rejected proposals. No direct rhetoric/negative-score match surfaced. Related #494 (collateral exceptions), #211 (finite prefix and recurrence), #636 (reachable state combinations), #646 (conserved transition inventories) are not replaced: this excursion asks how the same legal set can be weighted differently and how a prohibition can itself become performed material. Search is bounded, not a novelty audit.

The branch was created from main and compared before editing. Issue #650 newly created, no comments at intake. No shared manifest, protocol, registry, production implementation, or other worker branch modified.

JavaScript environment run: 131,070 binary candidates; 6,762 valid words across lengths; 6,831 assertions passed. Local Python 3.13.5 render: four original stereo WAVs, 16 kHz 16-bit PCM, 48,000 frames each for I/II and 140,000 each for III/IV. Source Git blob expected 0bb76311356c6de5f4871cc3dfc84246b9b8bbbb; see readback in PR. Audio files are generated locally by the renderer, not committed. No independent reviewer, participant, external approval or full repository CI result asserted.

Reproduce: node laboratory.cjs; python3 render.py. No external packages. The Python script writes audio/ and receipt.json alongside itself. The score, code and interpretations are AI-assisted original exploratory work; source encounters by the same assistant, not independent verification.

Disposition: Draft/HOLD for mergedown review. No promotion to canonical evidence.
