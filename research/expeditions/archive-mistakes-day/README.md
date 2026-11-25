# The Archive That Mistakes a Day for an Event
## Infra-ordinary listening and the politics of sampling units

**2026-11-25 · exploratory humanities and artistic research · Refs #612 · proposed, not selected Track E/G evidence.**

### An essay about the clerk who divides the world

An archive receives twenty seconds from a room. Twelve are occupied by a hum. Three little taps interrupt three gaps, and a chime occupies the final two seconds. One archivist files the hum as a single object; another files one object per second. Both retain precisely the same signal. A curator then commissions a miniature made from three randomly selected catalogue entries. The archivists now produce different music.

A choice has entered the work before the random number generator starts. It is not a choice of seed, filter or probability distribution over an agreed population. It is a choice of what the population consists of.

In the first archive the hum can be one object among eight. In the second it can be twelve objects among nineteen. The catalogue's apparent neutrality conceals a decision about whether duration is an attribute of an event or an opportunity to encounter it. A person who spends most of the day doing one thing may almost disappear from an event-count summary. A person whose work is continually interrupted may occupy a disproportionate number of its entries. This is an analogy, not data about people or work.

An artist might choose either register intentionally. An evening devoted to the hum would be as legitimate as an anthology of brief happenings. The problem begins when one of those works declares itself to be the complete biography of the room.

There is a peculiar inversion of the ordinary here. The hum is not silent; the clerk has merely given it fewer chances to appear. The gaps are not meaningless; they have been classified as intervals during which no named activity happens. In another edition the gaps might be the central character. The model should not represent unobserved material as silence, however. A gap in the supplied synthetic scene is an observed category. A missing recording is a different state.

### Source encounters (access and reading explicitly bounded)

- Georges Perec, *Tentative d'épuisement d'un lieu parisien*. [Christian Bourgois catalogue](https://bourgoisediteur.fr/catalogue/tentative-depuisement-dun-lieu-parisien-nouvelle-edition/), description immediately below author name (web lines 43–45 in retrieved view), consulted in French on 2026-11-25. The publisher describes three days of noting ordinary activity at Place Saint-Sulpice in October 1974. The catalogue reproduces a sentence from the work; this is **publisher description plus short primary quotation**, not close reading of the book. The book's procedure is a precedent for intentionally attending to what conventional descriptions neglect. The interpretation that cataloguing units can be a compositional parameter is ours, not an attribution to Perec.
- Alecia Beymer, [“The Infra-Ordinary: All That Goes Unnoticed”](https://www.poetryfoundation.org/articles/1353927/the-infra-ordinary-all-that-goes-unnoticed), Poetry Foundation, 24 June 2024, opening quotation and paragraph in indexed text; direct open returned 403. A secondary creative-writing prompt puts recurrence at the centre of ordinary observation. It is a discovery encounter, not a reading of Perec's original essay.
- University of Sussex Library, [Day Surveys 1937–38](https://www.sussex.ac.uk/library/special-collections/mass-obs-search/day-surveys), sections “About the Day Surveys” and “Directive replies” (retrieved lines 184–190). The archive describes an instruction to volunteers to account for the 12th day of successive months in 1937, followed by increased emphasis on special days and topics. This is institutional documentation of the collection procedure, not individual diary evidence. A recurrent calendar rule and an occasion-based rule generate different documentary corpora. The volunteer panel was not a demonstrated probability sample of Britain; no representativeness claim is made. Nor is a special-day survey inferior merely because its aim is different.
- Max Neuhaus, [LISTEN, artist's retrospective text (1988/1990)](https://www.max-neuhaus.estate/en/bibliography/publications/max-neuhaus-listen-1990), paragraphs beginning “It was my first independent work” through “After a while” (retrieved lines 40–75). The artist describes moving the audience out of the concert hall, marking their hands with a listening instruction and leading walks through ordinary sound environments. His reported impressions of audiences are testimony rather than controlled observations. The relevant distinction here is between changing a sound and changing the conditions under which it becomes an object of attention. The proposed archive instrument changes selection rather than claiming to reproduce Neuhaus's practice.
- Jeffrey S. Vitter, [“Random sampling with a reservoir”](https://doi.org/10.1145/3147.3165), ACM TOMS 11(1), 1985, pp. 37–57, indexed publisher abstract consulted; direct DOI retrieval returned 403. The abstract describes uniform sampling without replacement from a stream of initially unknown length and faster one-pass algorithms. It supplies an engineering precedent, not the philosophical argument. The present laboratory uses exhaustive subsets of a known finite population; it does not implement or benchmark Algorithm Z.

**Critical synthesis:** Perec's literary attention, the archive's collection rules, the soundwalk and the algorithm have different objects and purposes. Their productive conjunction is not a claim of equivalence. The shared question is which occurrences are available to be selected, and who declares them to be occurrences. A selection algorithm can be impeccably fair to its input records while being unsuitable for the question its user thinks they asked.

### A finite construction: three legitimate archives

The synthetic carrier is a nonoverlapping twenty-slot stream: hum x12, tap, gap, tap, gap, tap, gap, chime x2. The labels are stipulated, not extracted by a detector. Its eight initial episode records have positive lengths. Three distinct items are selected uniformly without replacement, in each of three separate populations:

| Archive | Item | Population | Intended question |
|---|---|---:|---|
| Clock | one duration slot | 20 | what occupies the time? |
| Diary | one annotated episode | 8 | what appears among recorded episodes? |
| Cabinet | one present category | 4 | what kinds occur? |

For a population of N items containing d items of type X and a uniform k-subset, the probability of encountering X at least once is 1 - C(N-d,k)/C(N,k). The expected number of X draws is kd/N. These are distinct quantities. For the hum with k=3, the clock yields 1084/1140 = 95.09% inclusion and 1.8 expected draws; the diary yields 21/56 = 37.5% inclusion and 0.375 expected draws; the cabinet yields 3/4 inclusion and 0.75 expected draws.

The cabinet does not estimate temporal prevalence. The diary does not estimate duration. A cabinet can offer one rare sound an equal opportunity to appear beside an overwhelmingly common one. This may be precisely the right artistic policy. It is the wrong policy if the stated purpose is to sample the duration distribution.

#### Refinement sensitivity, not evidence of human bias

Keep the carrier and all existing boundaries fixed. Allow optional cuts at each internal boundary of the hum and chime (eleven plus one, twelve independent binary decisions). This produces 4096 alternative annotated episode inventories with identical frame streams. The clock and cabinet have unchanged populations. The diary does not.

The minimum hum inclusion across the family is 1/3, when the hum is left as one episode and the chime is split into two. The maximum is 1-C(7,3)/C(19,3) = 934/969, about 96.39%, when the hum is fully split but the chime is not. Fully splitting all episodes makes diary and clock populations identical, so the distinction vanishes in this limiting case. Refinements are not necessarily meaningful event segmentations; the point is that an annotation system allowing those refinements changes its own sampling law. The laboratory independently enumerates all three-item subsets and checks inclusion and expected count formulas, reconstructs the unchanged carrier, and checks the all-unit limit. See laboratory.cjs and RECEIPT.md.

A second distinction follows: the sampler can preserve duration weighting under splitting by choosing an episode proportional to its duration, then a uniform slot within it. This is exact for a single independent draw; multiple draws without replacement must remove the chosen slot rather than the entire episode. Uniform episodes followed by uniform slots cannot generally produce the uniform clock. Do not conflate the two constructions.

### The instrument proposal: The Ordinary Register

An artist supplies a carrier recording or procedural sound field and editable annotations. The instrument retains the carrier independently of its archive. It offers three sampling registers: clock, episode and cabinet. A fourth register, deliberate selection, makes editorial choice explicit rather than disguising it as a probability model.

The musician chooses three grains or equal-duration excerpts, not three variable-duration passages by default. Variable-duration audition is a separate mode, because a clock sample followed by replay of its entire episode would introduce another duration preference. Every output includes a sidecar with original source position, duration, label, population and sampling policy; the listener can inspect or discard it. A gap can be an explicit silent grain. Unavailable source samples are visibly unavailable, not synthesized as silence by default.

A useful compositional control is **segmentation morphing**: while the carrier plays without change, split and join its editorial regions. In diary mode this transforms the distribution of future grains. In clock mode it leaves the sampling law alone. Cabinet mode can be changed only by altering the category vocabulary or the within-category sampler. The artist can crossfade between the three interpretations, but the mixture weights should be inspectable.

A VSTi could use a bank of procedural sound generators and trigger excerpt-sized grains under this policy. A VSTfx could provide bounded, user-enabled capture of its input into a local ring buffer; never silently record a microphone, conversation or other private audio. The capture domain, retention interval and clear operation need explicit controls. Implementation would require real-time-safe buffering, host automation, reproducible seed handling, independent per-voice state, dropout markers and fixed latency reporting. This is a proposal, not a delivered plugin.

### Counterarguments, limits and next inquiry

There is no objectively right population without a specified objective. A time-weighted archive may preserve the dominance of a boring machine while neglecting a rare consequential transient. Event selection may be exactly right for fault investigation. Category balancing depends on a taxonomy: arbitrarily splitting the category “hum” into twelve names would alter the cabinet just as episode splitting alters the diary. The current invariance claim applies only to cuts preserving labels and carrier.

The construction assumes a finite, nonoverlapping, completely observed stream and externally specified categories. Real sound fields overlap, have uncertain boundaries, contain partial observations and may resist identification. Duration and event frequency are separate statistics, not moral quantities; nobody's dignity can be inferred from their fraction of an archive.

MHAC can use the distinction as a **design hypothesis** about diagnostic history browsers: compare a duration-sampled state history, an event-sampled history, a categorical coverage index and an ordinary complete log under an explicit retrieval task. Independently measure time occupancy error, event incidence error, missing-category rate and task completion. Keep safety-critical incidents in a dedicated complete log, never rely on a sample to convey consequential events. No human tests or auditory benefits are asserted. A conventional filterable timeline might be better than any musical archive. 

The next intellectual rabbit hole is a corpus with overlapping categories, such as a motor hum and a quiet voice in the same frame. A choice of atom (frame, label occurrence, source stream, or human-authored encounter) then changes the meaning of coverage. Do not extend the nonoverlapping theorem without defining that new population.

### Scope reconciliation and handoff

Live AGENTS, RAG, PROGRAMME, AGENT_RUNBOOK, integrity and validation guidance read on 2026-11-25; main inspected at 495a98ca12bae467a507031f04931aa4254b1866. Sixty recent PR search titles and forty open issue search titles examined; targeted terms Perec, infra-ordinary, soundwalk, reservoir sampling, archive sampling, Neuhaus, habituation and salience searched. Existing #342 addresses acoustic withdrawal; #430 addresses estrangement and change-budget counterpoint. This expedition retains the sound and changes the selection population; it claims no priority and the title search is not an exhaustive novelty audit. Issue #607 indicates mergedown activity, so do not modify shared manifests or other branches. New issue #612 body read and comments endpoint returned an empty list. No dependencies on accepted empirical outputs. Draft/HOLD for integrator; no change to frozen method, canonical claims or human gates. The only deliverables are this essay, SCORE.md, laboratory.cjs and RECEIPT.md. ChatGPT GPT-6.2 performed the source encounters, interpretation, software checks and self-review; no independent human review. No real recordings or human data.
