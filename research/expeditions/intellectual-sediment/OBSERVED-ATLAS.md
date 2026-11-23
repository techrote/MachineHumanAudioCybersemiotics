# MHAC-X004 — observed atlas: what the transparent baseline actually found

This report interprets the machine-readable summary emitted by GitHub CI on the X004 branch after self-exclusion was added. The main-corpus analyzer completed successfully even in a run where the separate shadow-history helper still had an implementation error. The branch has since fixed that helper; exact final-head qualification remains a separate step.

## Corpus shape

The measured narrative corpus contained **128 current Markdown documents and 121,777 tokenized words**. X004's own directory was excluded so the measurement could not manufacture recurrence by counting its newly written theory.

Coarse document families:

| Family | Documents | Words |
| --- | ---: | ---: |
| evidence / retrieval | 69 | 63,912 |
| governance / foundations | 19 | 13,345 |
| exploratory research | 15 | 12,817 |
| method / novelty | 14 | 15,519 |
| theory / analysis | 8 | 14,206 |
| other | 3 | 1,978 |

The first caution follows immediately: **more than half the documents are evidence/retrieval records**. Raw term frequencies are structurally biased toward source custody, screening, access and provenance.

The current merged narrative corpus is also temporally lopsided. First-add dates cluster in:
- 4–8 October: foundational/governance documents;
- 13 October: method/novelty plus early evidence;
- 3–11 November: evidence retrieval and theory analysis;
- **23 November: all 15 exploratory-research documents measured in this run.**

Therefore the accepted-main corpus does **not yet support a months-long diachronic claim about exploratory concept evolution**. Much older exploratory material may exist on branches; that is why X004 separately analyzes shadow sediment.

## The lexical bridge baseline mostly failed interestingly

The first, deliberately naïve bridge ranking was dominated by procedural language: source, evidence, protocol, claim, review and access. That was a useful negative control. X004 then expanded its declared procedural stoplist rather than presenting repository bureaucracy as intellectual emergence.

After that correction, high-dispersion terms still remained broad:

- human — 115 documents;
- separate — 82;
- model — 49;
- design — 52;
- state — 51;
- bounded — 63;
- synthetic — 47;
- agent — 55;
- identity — 87.

This is not sufficient evidence of concept migration. It mostly describes the kinds of work MHAC does.

Sparse cross-family phrases were somewhat more informative, but still heavily methodological. Examples included:
- second-order cybernetics;
- common ground;
- human-computer interaction;
- non-human audio;
- **remain distinct**.

The last phrase is a better reading lead because it directly matches a recurring methodological operation and appeared across four coarse families. It still does not establish independent rediscovery.

**Conclusion:** lexical bridge scoring is useful primarily as a triage mechanism. It successfully demonstrates how easy it would be to manufacture a story of coherence from ordinary shared vocabulary.

## A stronger pattern: anti-collapse style

X004's declared style markers count language such as distinguish, separate, conflate, collapse, keep distinct and not the same. Rates per 1,000 tokenized words were:

| Family | Anti-collapse | Provenance | Adversarial / falsification | Boundary disclaimers |
| --- | ---: | ---: | ---: | ---: |
| governance / foundations | **4.646** | 6.444 | 1.349 | 10.266 |
| exploratory research | **3.667** | **0.780** | **1.873** | 7.022 |
| theory / analysis | **3.379** | 3.731 | 1.197 | 7.954 |
| evidence / retrieval | **3.129** | 6.102 | 0.767 | 6.227 |
| other | 2.528 | 13.650 | 3.539 | 10.111 |
| method / novelty | 1.998 | 4.188 | 0.193 | 4.833 |

The important comparison is not merely that exploratory work contains distinctions. It is that **exploratory work has high anti-collapse and adversarial marker rates while its provenance marker rate is extremely low relative to evidence/governance work**.

That weakens the simplest “all style markers are just the same provenance template” explanation. It does **not** eliminate instruction inheritance: the founding instructions explicitly demand distinction and critical practice.

The defensible claim is therefore:

> MHAC's exploratory layer reproduces an anti-collapse/adversarial research posture even when it is no longer reproducing the full provenance vocabulary at the same rate.

That is an externally observable corpus property, not a belief state.

## Manual lineage check: one motif really does change shape

A manual read of load-bearing files gives a more useful genealogy than the bag-of-words ranking.

### Founding formulation

PROJECT_FOUNDATIONS distinguishes:
- world state from machine estimate;
- reception from acknowledgement;
- acknowledgement from understanding;
- acknowledgement from resolution;
- suspicion from certainty;
- low hazard from low urgency.

CONCEPT_REGISTER formalizes:
- designed urgency vs perceived urgency vs time-to-action;
- identification vs correct action;
- message certainty vs evidence certainty vs listener confidence.

This makes typed distinction a **known inherited programme constraint**.

### Theory-analysis transformation

The Brier/Clark comparison then uses the posture to separate:
- machine truth;
- auditory delivery;
- listener interpretation;
- action validity;
- evidence of understanding.

It explicitly rejects equivalence between Brier's ontological project and Clark/Brennan grounding while allowing partial applied overlap.

This is already more than repeated wording: the distinction operation is applied to a new theoretical comparison.

### X001 transformation

The Observer's Solecism separates:
- discrete samples from the continuous field;
- instrumental indistinguishability from semantic identity;
- mathematical Fourier structure from physical Kaluza–Klein evidence;
- a synthetic pitch mapping from particle mass.

Its TRANSFER note proposes an interface distinction among contradicted, unknown, underdetermined and incompatible.

The inherited posture has become a mathematical design discipline.

### X002 transformation

Directional deixis separates:
- a well-formed audible word from an executable instruction;
- addressee identity from reference-frame identity;
- a frame label from a current trusted transform;
- equivariance from invariance.

Again the structure migrates into a different formal problem.

### T018 transformation

Affective-feedback work separates:
- emotional cue from technical specification;
- social repair success from task repair success;
- supportive presentation from epistemic/task judgement.

The same posture now constrains human–agent collaboration rather than auditory code design.

This is **conceptual migration with obvious inheritance pressure**. It is not independent convergence, but it is also not mere phrase copying: the local variables and falsifiers change.

## Motif lexicons: broad but pervasive

Declared motif lexicons appeared widely:

- provenance / identity / authority: 118 documents;
- action / urgency / consequence: 82;
- failure / ambiguity / conflict: 82;
- uncertainty / epistemics: 75;
- state / lifecycle / time: 74;
- repair / grounding: 63;
- composition / binding / mapping: 62;
- observer / context / frame: 60;
- meaning / semiosis: 54;
- affect / anthropomorphism: 47;
- exaptation / transfer: 40.

These lexicons are intentionally broad and overlapping. Their value is comparative, not ontological.

One interesting current-corpus fact is that observer/context/frame appears in **13 of 15 exploratory documents**, while composition/binding/mapping occurs in 11 and state/lifecycle/time in 12. This is compatible with the recent X001/X002 wave of observer/frame research, but because all exploratory documents are from one day, it could simply be a burst effect from shared prompts.

## The main finding is narrower than “agent philosophy”

The corpus supports three increasingly strong statements:

1. **Recurrence:** many concepts and methodological markers occur across research families. Proven.
2. **Transformation:** manual examples show one inherited anti-collapse operation being applied to materially different local problems. Supported by direct file comparison.
3. **Autonomous intellectual attractor or persistent philosophy:** not established.

The third would require excluding simpler causes: founding instructions, shared source literature, direct cross-links, similar model training, human selection and same-day prompt inheritance.

The atlas therefore treats **anti-collapse as a reproducible research posture**, not an agent's private philosophy.

## What the baseline could not see

The largest limitation turned into the next research target: accepted main contains only today's exploratory wave. Many T001–T017 tangents remain on open branches. Those rejected, provisional or unmerged paths are intellectually important precisely because they are not canonical.

The shadow-sediment analyzer was added to inspect them without pretending they are accepted findings.

That may be the more revealing archive: sediment includes not only what survives selection, but what nearly became rock.

## Shadow sediment changed the scale of the result

A later exact shadow pass (workflow #45246032759) found **155 branch/history-only Markdown paths**, of which **150 were unique text blobs** totaling **176,641 tokenized words** after exact-content deduplication.

The shadow family distribution was dominated by **108 exploratory paths**: 94 tangents and 14 expeditions. This is more exploratory material by path count than the entire current narrative corpus contains documents.

Three branch-only hourly scouting ledgers from 3–5 November contain **94,454 tokenized words** by themselves. Their repeated parallel/orthogonal/perpendicular lead structure and explicit endpoint distinctions provide a historical precursor to today's anti-collapse expeditions.

This changes the earlier same-day caveat:

- accepted-main exploratory work is indeed a 23 November burst;
- **MHAC's broader exploratory history is not**. It survives primarily off-main.

The shadow archive must remain noncanonical. Its value is archaeology and negative retrieval, not silent promotion into accepted findings.

See [SHADOW-SEDIMENT.md](SHADOW-SEDIMENT.md) and the frozen [BASELINE-20261123.json](BASELINE-20261123.json).
