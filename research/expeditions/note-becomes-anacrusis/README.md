# The Note That Becomes an Anacrusis

**Exploratory humanities/art research — 24 November 2026 — issue #382.** Original conceptual work, an exact synthetic theorem, and original acoustic illustrations. Not a Track E finding, completed Track G synthesis, or evidence of human perception.

[Score and fiction](SCORE.md) · [Exact oracle](oracle.cjs) · [Audio renderer](render.py)

## A note whose occupation is not yet decided

A performer strikes a key. It sounds unremarkable. A second performer, who has not yet chosen when to enter, will eventually make that first sound into a pickup, a continuation, or something less easily named. In the meantime, what is the first sound?

The distinction is not between existence and nonexistence. The sound was made. The question is whether a relational role has already been constituted, and whether an observer could know that role. There are at least three clocks: when a sound occurred, when an interpretation became available, and when someone chose to commit to that interpretation. A recording contains the first but not necessarily the second or third.

A particularly fertile musical operation would be to assign the production of sounds to one performer and the production of their temporal roles to another. The second performer is not given permission to overwrite the recording. Instead they compose the events that make previous sounds intelligible in a new way. We call this **prospective role composition**: producing the subsequent context in which an earlier event takes a different function.

## Encounters with theory (source-located notes)

1. Christopher Hasty, *Meter as Rhythm*, 20th anniversary edition (2020), chapter 7, pp. 113–126, publisher abstract, [DOI 10.1093/oso/9780190886912.003.0007](https://doi.org/10.1093/oso/9780190886912.003.0007). Hasty characterizes projection as the capacity of a completed duration to condition the durational possibilities of a successor. The successor is not guaranteed. Access: publisher abstract returned in search; direct chapter retrieval failed; no full chapter reading or claim about an uninspected example. The term projection here is a theory of musical becoming, not the prediction function of a statistical model.
2. Chris Stover, "Christopher Hasty's Meter as Rhythm", English version of commissioned 2015 reference essay, [author website](https://www.chrisstovermusic.com/hastys-meter-as-rhythm). Read main text, particularly paragraphs beginning "Once beginning and continuation are understood" and "After a detailed engagement with Beethoven's Symphony no. 1". Stover describes Hasty's contrast between continuation relating to an earlier beginning and anacrusis relating to a succeeding beginning; his discussion of Monteverdi describes a potential beginning reinterpreted as deferral. This is secondary exposition, not an independent analysis of Monteverdi or a direct reading of the Hasty score.
3. Matthew W. Butterfield, "The Power of Anacrusis: Engendered Feeling in Groove-Based Musics", *Music Theory Online* 12(4), December 2006, [publisher text](https://www.mtosmt.org/issues/mto.06.12.4/mto.06.12.4.butterfield.php), paragraphs [10]–[16], [18]–[23], [31]–[32]. Read these passages in HTML; audio examples not auditioned. Butterfield argues that rhythmic patterns and expressive microtiming interact to create anticipatory force. He treats the distinction between continuation and anacrusis partly as a matter of orientation of attention; brevity, accent, articulation and timing may affect it. His analyses concern specific groove practices, not a universal mapping of one pitch or click to a pickup.
4. Justin London, *Hearing in Time*, 2nd ed. (2012), chapter 1, "Meter as a Kind of Attentional Behavior", pp. 9–24, [DOI 10.1093/acprof:oso/9780199744374.003.0001](https://doi.org/10.1093/acprof:oso/9780199744374.003.0001). Publisher abstract visible in search; direct chapter retrieval failed. London treats meter as a kind of synchronization of attention and behaviour with environmental rhythms and distinguishes the sounding durations from the organization of expectations. Stover's closing paragraphs also identify London's critique of Hasty as a useful point of tension. Neither theory should be described as having been adjudicated by this expedition.
5. *Stanford Encyclopedia of Philosophy*, "Temporal Consciousness", [§4.2](https://plato.stanford.edu/entries/consciousness-temporal/#RetAppHus), paragraphs beginning "At the heart of Husserl's account" and "For Husserl, retentions", and §4.3 on temporal illusions. Read the HTML passages; no Husserl primary edition consulted. The exposition distinguishes the present impression, retention of the just-past and protention toward the future. It also describes alternative interpretations of later information influencing reports of an earlier percept. A role assigned by software after a delay is not a model of Husserlian retention or a demonstration of retrocausality.
6. Hannon, Snyder, Eerola and Krumhansl (2004), "The role of melodic and temporal cues in perceiving musical meter", *Journal of Experimental Psychology: Human Perception and Performance* 30(5), 956–974, [PMID 15462633](https://pubmed.ncbi.nlm.nih.gov/15462633/). Abstract returned by search; direct open returned only a disclosure link. The authors report that multiple melodic and temporal features inform judgments of meter in their stimuli. No effect size or generalization to the present audio is extracted.

Read by one AI assistant, GPT-6.2, on the date above. Reading extent is limited as stated; no independent reviewer or participant. These encounters are research leads, not formal extraction records. No quotation, source reproduction, or licensing grant.

## The toy theorem: the last possible shared accent

Let time be indexed by nonnegative integers, and let hypothesis (m,p) predict a binary accent stream a(t)=1 exactly when t mod m=p, with period m at least 2 and phase p between 0 and m-1. A 0 is observed absence of the added accent, not silence or a missing observation. A hypothesis is globally fixed; no missing accents, noise, changing meter, microtiming or competing cues.

For distinct periods m<n, the maximum length of a common contiguous observation prefix (over all initial phases) is exactly 2m-1. Proof: any matching run cannot contain two ones, since consecutive shared ones would require both periods to equal their separation. A zero-only run has length at most m-1. A run containing a single shared one can contain at most m-1 zeros on each side, hence at most 2m-1 total symbols. Sharpness: set both phases to m-1. The run 0^(m-1) 1 0^(m-1) agrees; at the next position the shorter period accents and the longer does not. Same period m and distinct phases cannot share any ones; the longest common prefix is m-2 zeros, achieved by phases m-2 and m-1. These are elementary periodic-word facts; no mathematical priority asserted.

For the entire candidate family with periods 2 through M, exact phase and period are guaranteed identifiable from the first 2M-2 observations when M>=3. The pair M-1 and M witnesses sharpness. For M=2 the horizon is one observation. This is a zero-error identification horizon in a fully observed fixed model, not a psychophysical threshold. In particular, increasing M can increase both the number of candidate meters and the observation time required to rule them out. If accents become unobservable for arbitrary lengths, no finite horizon of this kind holds.

Concrete case (positions numbered one through twelve):

| Model | Accent sequence |
|---|---|
| Period 4, phase 3 (zero-based) | 000100010001 |
| Period 5, phase 3 | 000100001000 |

The first seven symbols coincide. At the eighth, the first adds an accent; the second does not. If we define "pickup" solely as the pulse immediately before the next designated accent, pulse seven has that role in the first score but not the second. This narrow definition is an invented annotation rule, not Hasty's anacrusis. No causal classifier can know the role of pulse seven from that shared history alone. An artist who elects to let the role remain provisional is doing something different from an algorithm which guesses and later conceals the guess.

### Executed checks

The standard-library JavaScript oracle enumerates phase pairs for every unordered period pair (including same-period cases) from 2 through 16. It measures common prefixes directly, up to the least common multiple. It checks the upper bound and its attainment, and independently checks whole-family prefix injectivity immediately before and at the predicted global horizon.

| Maximum period | Candidate hypotheses | Guaranteed observations |
|---:|---:|---:|
| 2 | 2 | 1 |
| 3 | 5 | 4 |
| 4 | 9 | 6 |
| 5 | 14 | 8 |
| 8 | 35 | 14 |
| 12 | 77 | 22 |
| 16 | 135 | 30 |

Executed: 120 period-pair classes, 9,725 phase-pair comparisons, 19,600 passing assertions. Run with Node: node oracle.cjs. The proof and exhaustive checks are distinct; the latter cover finite sizes only. The result concerns an idealized accent symbol, not its audibility. A common prefix of PCM does not require listeners to have identical prior experiences.

## A second rabbit hole: the ethics of reassigning a beginning

A court may distinguish the beginning of an incident from the time at which it can be recognized as such. A machine operator may distinguish the initial indication of a problem from the moment at which enough information exists to declare the problem. A historian may give an earlier event a new place in a sequence. None of these changes the timestamp of occurrence. In the artistic case there can be pleasure in leaving an earlier event open to several futures. In an operational setting, such ambiguity may be harmful.

A past event with a revisable role need not be a past event with a revisable fact. This distinction might deserve first-class representation in a sequencer: immutable occurrence, mutable interpretation, separately timestamped commitment. If one deletes the intermediate role assignments, one loses the difference between an interpretation that was always supported and one made plausible by later material. If one forces all provisional interpretations into the mix, one may make the music intolerably explanatory.

The counterargument is that Hasty's approach is not asking us to identify a pre-existing hidden periodic parameter in the first place. It questions the reduction of meter to a temporal grid. Our theorem begins precisely by making such a reduction, and can only show what is unknowable *even in that restrictive case*. There is no reason to claim that a long enough observation will uniquely identify the meter of an actual musical performance. A composition with no intended periodic meter is not a failed instance of the toy model. The term anacrusis is used artistically in the title, not as the name of the theorem.

## The proposed instrument: the Future-Role Sequencer

Separate the sounding lane from an accent lane, a candidate-role lane, and an annotation-history lane. The first plays immutable notes; the second chooses subsequent accent events; the third shows compatible descriptions; the fourth can be optionally sonified. A musician might be allowed to change the next accent until its onset. A causal rendering engine never changes emitted samples. A playback mode may show later interpretations on the historical timeline, but labels them with their actual assignment time.

Controls:
- Role commitment: choose provisional, confirmed, or deliberately unclassified.
- Accent horizon: limit permissible future intervals; do not treat this control as a measure of human attention.
- Interpretation counterpoint: a second voice plays changes in the candidate set or annotations, not predictions disguised as facts.
- Deferred pickup: a performer delays an accent, changing which earlier pulse is its immediate predecessor.
- Unresolved ending: stop without automatically selecting a best-fitting meter.
- Perspective routing: independent role lanes for multiple interpreters; disagreement need not be resolved.

A richer artistic version would use the same underlying sound event as a rhythmic continuation in one live arrangement and as an anticipatory gesture in another. Different interpreters might route their annotation to unrelated parameters (filter motion, grain density, harmonic suspension) rather than just different barlines. This is proposed, not implemented DSP. It complements earlier MHAC studies of framing, silence, tempo transfer, reversible edits and retrospective category selection, while concentrating on evidence arriving *after* an event and a role whose definition depends upon future events.

## MHAC question and a possible falsification

Design hypothesis: interfaces should distinguish occurrence time, time of detection and time of classification when a later event supplies decisive evidence about an earlier signal. A machine's retrospectively assigned label must not be presented as an already-known actionable instruction at the earlier timestamp. A comparison could present artificial noncritical sequences with (A) a backdated label alone, (B) a label with explicit time of assignment, and (C) no retrospective label, with identical underlying timelines. Measure correct identification of what was knowable when, response time, false action attribution and additional burden. If explicit assignment information yields no better comprehension or worsens task performance, revise or abandon the design. Preserve required action, certainty and safety messages outside the artistic layer. No recruitment or operational deployment authorized.

A separate artistic listening question: present the shared prefix and either continuation, counterbalance order, distinguish judgments of the immediate predecessor from judgments of meter, and permit no-meter and uncertain responses. Include an irregular continuation and a no-accent control. The current recordings are only stimulus sketches, not a validated protocol or evidence of any effect. Later information, memory, entrainment, preference, and task demand are alternative mechanisms.

## Reproduction and repository checkpoint

AI-assisted original work. Base main commit 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, integrity, validation, research workspace and frozen protocol index; reviewed 100 recent PR titles, 70 open issue titles, and targeted issue search (anacrusis OR downbeat OR metrical, no hits). This is a bounded overlap scan, not a claim of novelty or exhaustive repository archaeology. Created #382 and read its body and empty comment history. Four additive files only; no canonical registry, protocol, manifests, prior branches or production implementation altered. Generated WAVs delivered separately; local renderer passed prefix, divergence, PCM, repeated-render and bounds checks. Repo CI and independent integration review remain pending at submission; no scientific or human gate claimed. Scope deliberately remains an exploratory draft per issue, with no authority to promote these notes into the formal evidence pipeline.
