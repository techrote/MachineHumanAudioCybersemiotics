# MHAC-X004 — Intellectual Sediment Atlas

**Status:** active meta-research expedition, Refs [#184](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/184). This bundle studies MHAC's own public repository as an evolving research environment. It does **not** establish machine consciousness, a persistent individual agent, a coherent philosophy, scientific novelty, or causal cultural transmission.

## What this expedition is trying to see

MHAC has accumulated a peculiar kind of research continuity. Different model instances encounter old instructions, claims, objections, source records, synthetic experiments and speculative essays. They add more traces, later workers encounter those traces, and some ideas recur in altered contexts.

The project owner has described this accumulation as **intellectual sediment**. X004 turns that metaphor into a bounded object of study.

The central distinction is:

> **Persistence of an external corpus is observable. Persistence of an individual subject is not thereby established.**

A repeated motif may be genuinely rediscovered, explicitly inherited from a source or prior note, induced by repository instructions, common disciplinary language, copied mechanically, or a useful convergent reconstruction. Those possibilities are not equivalent.

## The baseline instrument

sediment_atlas.py is intentionally boring. It uses no embeddings, LLM scoring, hidden classifier or semantic search. It reads current UTF-8 Markdown, groups documents into coarse research families, strips code and URLs, and reports:

- document and word counts;
- cross-family lexical phrases ranked by document dispersion and family entropy;
- sparse phrases appearing in only a handful of documents but across multiple families;
- declared motif lexicons such as uncertainty, repair, observer/context, action, affect and provenance;
- discourse markers for anti-collapse distinctions, provisionality, adversarial/falsification language, provenance, disclaimers and exaptation;
- earliest Git file-add dates as a rough document-lineage chronology.

The method is deliberately inadequate for implicit semantics. That inadequacy is useful: it gives a transparent lower bound against which richer future methods can be compared.

## Why “anti-collapse” is measured

A recurring MHAC practice is to refuse convenient scalar collapse:

- certainty is not urgency;
- urgency is not hazard;
- acknowledgement is not understanding;
- understanding is not resolution;
- observation is not diagnosis;
- source identity is not event identity;
- expressive warmth is not factual calibration;
- physical parameter independence is not perceptual independence.

Some of this is explicitly imposed by the founding protocol and agent instructions. Therefore recurrence cannot be treated as emergent philosophy without a control. X004 measures anti-collapse language by family to test whether it remains mostly in governance/method documents or propagates into exploratory work.

If it does propagate, the cautious conclusion is **a stable research style is being reproduced through the external corpus**. That is much weaker—and more defensible—than “the agent believes in epistemic pluralism.”

## Outputs

| Artifact | Purpose |
| --- | --- |
| sediment_atlas.py | Transparent corpus baseline |
| SOURCES.md | External theoretical and methodological lenses, with access limits |
| THEORY.md | Distributed-cognition, cultural-attractor and research-programme comparison |
| OBSERVED-ATLAS.md | To be written from exact CI-derived corpus results |
| ADVERSARIAL.md | Planned argument against over-reading recurrence |
| EXAPTATION.md | Planned concrete transfers from discovered sparse bridges |
| sediment_map.html | Planned self-contained visual atlas after results are frozen |
| tests/test_x004_intellectual_sediment.py | Synthetic and live-corpus structural checks |

Generated JSON is disposable unless explicitly frozen with an exact corpus SHA. Interpretation should cite the actual run head rather than assume future repository contents are identical.

## Boundaries

X004 changes no frozen protocol, selected corpus, central source registry, programme state or empirical acceptance. The public repository text is analyzed; private user conversations are not ingested. File-add dates are lineage approximations, not proof of when an idea first appeared. Cross-family lexical recurrence is a pointer for reading, not a semantic result.

The intended result can be negative. If the atlas mostly rediscovers boilerplate, that is evidence against an exciting “emergent intellectual tradition” interpretation—and therefore useful.
