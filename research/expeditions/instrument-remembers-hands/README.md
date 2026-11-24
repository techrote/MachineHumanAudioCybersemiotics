# The Instrument That Remembers Your Hands
*An essay on appropriation, resistance, access and the preservation of learned gestures.*

24 November 2026 · MHAC exploratory expedition, #270 · AI-assisted original research and artistic construction. No Track E/G inclusion, no participant data, no production recommendation.

## A replacement that is not a replacement

A musician has learned to play a box. The box contains a sensor, a little loudspeaker and an algorithm. Another box, sold under the same model number, is placed in front of her. It has the same range of sounds. It is nominally the same instrument. But her fingers have acquired a vocabulary that the substitute does not recognize.

One can preserve the entire catalogue of outputs and nevertheless destroy the relationship through which those outputs were obtained. Call this **skill incompatibility**: not the loss of an output but the loss of a previously practicable way of reaching it. This is a proposed design distinction, not a medical or psychological construct.

The encounter is not purely imaginary. In Zappi and McPherson's NIME 2014 paper, p. 460, three performers had to exchange instruments because of technical problems and reported preferring their own instruments' touch responses; some had marked or annotated their devices. The study's machines were nominally equivalent, not demonstrated to have physically identical response curves. We should not translate this observation into a claim that the performers could not play the replacements, or that calibration alone caused their reactions. It does offer a useful challenge to a specification consisting exclusively of sonic capability.

The question is not whether a designer can make a sufficiently sophisticated controller. It is whether the designer recognizes that some of the instrument's value has already been created by its player and cannot be reconstructed from the product's inventory.

## A friction, a barrier, a conversation

Dewey's *Art as Experience*, chapter III, pp. 35–36 (Perigee 1980 excerpt), situates experience in interaction with surroundings. He distinguishes a fulfilled episode from an interrupted succession, allowing resistance and pauses to participate in the formation of an experience. This is not the thesis that difficulty is intrinsically good. Resistance can take a coherent part in an unfolding activity, or merely terminate it.

Consider three situations: a bowed string that responds differently as pressure changes; a digital patch that unexpectedly discards every third input; a control that requires a bodily movement unavailable to its intended player. It is tempting to call all three 'resistance.' But the word obscures at least three separate design variables: a learnable relationship between action and response, interruption without useful control information, and exclusion from access. Their subjective character cannot be inferred from these descriptions alone. The same software delay could be a compositional resource in one practice and a destructive barrier in another.

Zappi and McPherson's ten-person study compared deliberately constrained instruments, one group having an additional control dimension. Their account suggests that the added dimension could dominate exploration, and that richer nominal controls need not produce richer actual appropriation (p. 455 abstract; p. 460 conclusion). The lesson for this expedition is not to remove controls mechanically, but to resist using parameter count as a substitute for an account of playing.

Frid and Ilsar's 2021 survey complicates this position. In their sections Background / Accessible Digital Musical Instruments and Discussion, they make access and player agency central; in Limitations and frustrations, a small number of respondents described constraints positively while others reported practical barriers. Only 12 of 118 respondents reported disability or access requirements, a limitation the authors explicitly discuss. This was not an experiment about the model below. There is no warrant to infer universal preferences from these respondents, still less to prescribe hardship as a route to musical legitimacy.

A provisional vocabulary:
- **Articulatory constraint:** a rule whose consequences can be learned and used to shape an intended performance.
- **Maintenance burden:** time or effort spent keeping the means of action available, without a necessary expressive payoff.
- **Access barrier:** a mismatch between a means of interaction and the needs of a particular player.
- **Instability:** a relationship between gesture and output that changes on a time scale incompatible with a given practice.
These are not disjoint categories. A performer may appropriate a maintenance burden as an articulatory constraint. A predictable constraint can remain inaccessible. A changing mapping can be artistically interesting when its change is deliberate and legible.

An instrument need not be difficult to be deep. A player need not earn the right to make sound by conforming to the designer's preferred physiology.

## Exact toy construction: rehearsal without embodiment

Let there be n distinguishable keys and n distinguishable pitches. A hidden bijection p maps keys to pitches; each possible permutation is equally likely. A rehearsal probe reveals one key's pitch. The player is an ideal observer with perfect memory and inference, not a person. Give the observer k distinct probes (0 <= k < n), then a uniformly chosen target pitch. The observer chooses one key without test feedback before scoring. A second test requests an ordered phrase using each pitch exactly once; the entire key sequence is committed before feedback.

Under a fixed mapping, (n-k)! permutations remain. For a probed target the key is known; for an unprobed target the best single-key success is 1/(n-k). Averaging gives (k+1)/n, including the case where the last unprobed association is inferred. For the complete phrase, the inverse permutation is uniquely required and every remaining candidate is equiprobable: best success 1/(n-k)!. These bounds are attained by any consistent completion for the phrase and an optimal single-key choice.

Now independently resample the entire bijection just before testing, keeping it fixed during the test phrase. Nothing about rehearsal identifies the fresh mapping. Single-pitch success is 1/n and full-phrase success is 1/n!, whatever k. A mapping resampled independently for each note would be a different model; its full phrase success would instead be n^-n. A displayed mapping, audible correction within the scored phrase, or correlated replacement would invalidate the stated bounds.

For n=4, stable single-target success progresses 25%, 50%, 75%, 100%; full-phrase success progresses 1/24, 1/6, 1/2, 1. With independent replacement they stay 25% and 1/24. Both instruments have exactly the same instantaneous pitch repertoire. Neither needs greater physical effort. The difference concerns the future utility of an observation.

This is elementary finite probability, not claimed novel mathematics or a model of bodily learning. It intentionally strips away expressive timing, error correction, motor memory, hearing differences and emotional experience. It establishes that there is a logically possible kind of practice value which cannot be recovered from an output catalogue. It does not establish that a stable mapping is invariably preferred or that random instruments cannot support skill (a player might learn distributions, timing or strategies rather than a bijection).

## The replacement contract

Suppose the old mapping is now fully known; relabel pitches so it is the identity. A new mapping q retains f of the n key associations exactly. The player reuses the old gestures without compensating. A phrase visits s distinct keys, possibly with repetition. Exact unchanged pitch playback occurs precisely when all s keys belong to the fixed-point set of q.

The number of possible updates with exactly f retained associations is C(n,f) D(n-f), where D(m) counts derangements, D(0)=1, D(1)=0, D(m)=(m-1)(D(m-1)+D(m-2)). Choose the fixed set; all other keys must be permuted without fixed points. A one-key change alone is impossible for a bijection. For a uniform update conditional on a feasible f, the fraction preserving a specified s-key phrase is C(n-s,f-s)/C(n,f), zero when s>f. This follows by counting fixed sets containing the phrase's keys; derangement factors cancel. It is not an estimate of real firmware update probabilities.

For a four-key instrument retaining two keys, six possible updates each swap the complementary pair. A one-key motif survives three of six updates, a two-key motif one of six, and a three-key motif none. Repeatedly playing a single unchanged key can be perfectly preserved even though two of four bindings are broken. A long phrase with few distinct keys can thus be more compatible than a short phrase covering the instrument's vocabulary. Repetition does not count as a new key. This is a deliberately narrow compatibility criterion: identical pitch sequence is not identical timing, sound, effort, feel, or artistic experience.

A known replacement permutation can be exactly compensated in software by remapping old gestures through the new inverse, under the model's assumptions. That is a crucial negative control: physical consistency is not always necessary for operational consistency; a transparent adapter can preserve learned routes. A new accessible controller can also intentionally use a different physical gesture to reach the same outcome. We should not freeze a single bodily norm in the name of compatibility.

The companion laboratory enumerates permutations for n=2..7 and every subset of keys, checks counts against the formula, and computes ideal posterior optimal single-target success by maximizing over keys. No sampled or participant results. Execute with `node laboratory.js`.

## Exaptation: a practice-preserving patch bay

A conventional preset receipt may retain oscillator parameters, routings and MIDI assignments. Extend it with a separately versioned **gesture contract**. It describes observable input events, calibration curves, units, response functions, temporal assumptions and accessibility adaptations. A replacement audit should use player-authored reference gestures, not a designer-selected motor ideal. Compare their pitch, onset, continuous response and reachable expression regions separately; report a vector of discrepancies rather than a universal skill score.

Three paths are useful: preserve the familiar mapping, intentionally fork it as an experimental instrument, or adapt it to an alternative means of access. Never update a learned mapping invisibly during a performance. If an adaptive instrument is meant to change continuously, disclose the adaptation policy, offer a frozen mode and make reversal possible. In an emergency interface, access and reliable actions take precedence over the aesthetics of resistance. These are design hypotheses or preferences, not evidence that specific implementation will improve performance.

A second, more speculative instrument could have a **rehearsal bus**. It records consensually selected gesture demonstrations, plays back their effects under alternative patches, and lets the performer decide which transformations survive. It would be like a DAW automation lane for the law of interaction itself. A player could compose a transition from reliable control to stochastic control and back again. Another player could independently manipulate that transition. The sound score becomes partly a score for what can be learned.

But logging gestures is not equivalent to acquiring a skill. A log cannot document pain, perceived effort, the felt arrival of a phrase, the social circumstances of learning, or an improviser's intent. No gesture recording is proposed without user control. To treat the receipt as an exhaustive model of the musician would repeat exactly the category mistake under investigation.

## Sources and challenge ledger

- John Dewey, *Art as Experience* (1934; Perigee 1980 edition), chapter III, “Having an Experience,” printed pp. 35–36. [Course excerpt](https://commons.princeton.edu/hum583-f21/wp-content/uploads/sites/283/2021/09/EXPERIENCE-readings.pdf), PDF indices 6–7 visually inspected; bounded passage, not full book. Philosophical argument, not measured causal evidence.
- Victor Zappi and Andrew McPherson, “Dimensionality and Appropriation in Digital Musical Instrument Design,” NIME 2014, pp. 455–460, DOI 10.5281/zenodo.1178993. [Proceedings PDF](https://nime.org/proceedings/2014/nime2014_409.pdf). Read abstract, introduction/section 1.1 and concluding discussion/section 5 on pp. 455 and 460, both page images inspected. Ten-player exploratory study; not independently appraised or included under frozen protocol. The report of replacement is observational, not a randomized calibration test.
- Emma Frid and Alon Ilsar, “Reimagining (Accessible) Digital Musical Instruments: A Survey on Electronic Music-Making Tools,” NIME 2021, DOI 10.21428/92fbeb44.c37a2370. [HTML](https://nime.pubpub.org/pub/reimaginingadmis/release/1). Read abstract, Background / Accessible Digital Musical Instruments, Methodology, Limitations and frustrations and Discussion (selected sections). Self-report survey, small access-requirement subgroup; not a basis for inferring a causal relationship between resistance and creativity. No underlying survey data retrieved.
- David Sudnow, *Ways of the Hand: A Rewritten Account* (MIT Press, 2001), [publisher description](https://mitpress.mit.edu/9780262194679/ways-of-the-hand/). Metadata and description only. A promising further reading lead about first-person learning, not used to assert details of the book.

All source access occurred 2026-11-24 by the same ChatGPT agent. No human or independent reviewer, no full-text claims beyond recorded passages, no source redistribution, no novelty claim. A contrary empirical result showing that a particular variable mapping supports transferable skill would not contradict the finite calculation; it would challenge an overgeneralized design inference. Seek NIME work on adaptation, control, haptics, access and musical appropriation before making such inferences.

## Reconciliation and status

Live main at 495a98ca12bae467a507031f04931aa4254b1866 at start. Read AGENTS, RAG, programme, runbook, integrity, validation and README; reviewed 35 recent PR summaries and targeted repair issue/branch search. Recent #254 investigates morph geometry; #268 context-dependent coding and #201 selective clarification; #33 recipient repair. The present question is learned route preservation under instrument replacement and appropriation, not those issues' completion. No mainline programme milestone claimed; frozen evidence and manifests unchanged. Dedicated issue #270, no comments at branch creation. Scope is original essay, synthetic oracle and artistic score only. Repository CI and independent review remain separate.
