# MHAC-X004 — exaptation ledger and reusable machinery

The purpose of this note is not to generate another infrastructure programme. It records concrete things X004 has already made useful and bounded opportunities that future work may pick up.

## Distinction miner: a reusable result already produced

The strongest recurring MHAC posture is “do not collapse X into Y.”

X004 therefore implements distinction_miner.py, which scans narrative Markdown for candidate statements such as:
- distinguish A from B;
- separate A from B;
- A is not the same as B;
- does not establish / prove / imply;
- do not conflate;
- keep distinct.

Every candidate retains file and line provenance.

The CI corpus pass found **206 boundary candidates**, including **40 syntactically parsed left/right pairs**.

This is not an ontology generator. Regex spans can be ugly, incomplete or context-dependent. Its value is retrieval:

> Before a future agent simplifies a complicated model, retrieve nearby distinction statements and ask whether the simplification silently merges quantities earlier work kept apart.

That can be reused in MHAC without changing any scientific claim.

## A possible “distinction deck” for agent handoffs

A future tool could transform reviewed distinction records into a small task-local deck:
- terms involved;
- source path/line;
- reason the distinction mattered;
- conditions where it can be safely collapsed;
- counterexample demonstrating failure.

That is more useful than a global prohibition.

For example, certainty and urgency should sometimes remain separate, but a specific interface could map them together under a deliberately restricted operational policy if the consequences are understood and tested.

The deck should therefore store **revision conditions**, not dogma.

## Shadow sediment as negative RAG

Open and abandoned branches are normally treated as clutter.

X004's shadow_sediment.py deliberately treats them as a second archive:
- ideas that did not land;
- duplicate approaches;
- overextended hypotheses;
- synthetic falsifiers;
- paths awaiting integration.

A future research agent could query this archive before claiming novelty:

> “Has something like this already been attempted and rejected?”

That is a different function from ordinary RAG over accepted main. It is closer to organizational memory for failure.

Crucially, branch material must remain labelled noncanonical.

## Stigmergic metamarks: useful idea, wrong time to standardize

The stigmergy comparison suggests explicit marks such as:
- reusable mechanism;
- failed analogy;
- unresolved contradiction;
- exaptation candidate;
- negative result;
- needs human/domain specialist.

Such marks could guide later work through the environment.

But making a schema now would be classic MHAC yak shedding: X004 has not demonstrated that workers fail to recover these categories with ordinary search and prose.

Therefore **no new mandatory metadata system is proposed**.

The concept belongs in the ledger until a real retrieval failure justifies it.

## Cross-project methodological transfer

Without modifying any other repository, X004's tools could later audit:
- radiCADSAC for narrow proof/classification machinery that migrates into implementation;
- CyberSand for concepts transferred from research prototypes into pixel-engine mechanics;
- Xenovection for visual motifs that turn into general renderer abstractions.

That would test whether “intellectual sediment” is peculiar to MHAC or a broader property of the owner's agentic development ecology.

Such work must be separately commissioned because cross-repository writes are outside X004.

## A musical exaptation

The distinction ledger itself can become a compositional object.

Imagine two synthesis voices assigned to a pair that a research note says must remain distinct. Their spectra begin separated. A control gradually collapses them onto one parameter while an audible error/resonance layer grows according to the downstream consequences recorded in a synthetic model.

Pairs such as:
- certainty / urgency;
- acknowledgement / resolution;
- sample / field;
- social repair / technical repair;
- coordinate token / reference frame

could become movements in a “Do Not Conflate” instrument.

That would be artistic translation, not sonified empirical truth.

The unusual compositional constraint comes directly from the research corpus: **music built from distinctions rather than values**.

## A software-design exaptation

The factorisation theorem from X001 and the distinction ledger suggest a generic diagnostic:

If two full states collapse to the same observable representation but require different actions, the interface lacks a decision-relevant observable.

The distinction miner can supply candidate variables; X001 supplies the mathematical condition.

A future tool could use explicit synthetic state tables to test whether a proposed UI/API/event schema is action-sufficient.

This would be a real exaptation from grammatical/philosophical research into interface validation.

It remains a proposal until implemented on a concrete schema.

## What X004 refuses to build

X004 will not:
- create a heavyweight knowledge graph because words recur;
- require every project to adopt an epistemic taxonomy;
- add embeddings/vector databases merely to improve the aesthetics of the atlas;
- automatically promote branch notes into accepted knowledge;
- infer model beliefs or user psychology;
- touch other repositories to prove transfer.

The result should remain small enough to be useful.

The far-horizon opportunity is not “more infrastructure.”

It is **better retrieval of the surprising thing that was already there**.
