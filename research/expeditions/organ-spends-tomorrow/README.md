# The Organ That Spends Tomorrow to Sound Like Yesterday

**2026-11-26 · Refs #678 · Exploratory humanities, artistic research and synthetic engineering.** Outside the frozen Track E/G programme. AI-assisted writing, source inspection, mathematical derivation and software self-qualification by one ChatGPT GPT-6.2 session; no independent human review or participant study.

## A commission for an impossible conservator

The museum buys a small organ with four registers. When the old components grow inefficient the conservator can compensate with stronger excitation or install replacements. At the opening concert all three candidates sound exactly like the archived reference. The director declares the work restored.

At the second concert the score demands twice the amplitude. One instrument can perform it, the second changes colour, and the third compromises the sound less but still cannot perform the request exactly. The first concert was not a fraudulent measurement. It was an incomplete definition of success.

The proposed artwork makes **reserve** compositional: a resource available for future actions, not an audible property of the present output. Restoration can preserve the present sound at the expense of the range of future sounds. Conversely, replacement may recover a range of responses while sacrificing continuity of active original components. This is not a claim that real instruments should be driven harder. The mathematical apparatus is invented and deliberately safe, an abstract per-event resource allocation model.

The curator can also commission a replica instead of repairing the original; this changes what it means to preserve the object. An externally supplied voice that supplements the original while leaving it intact changes the allocation boundary, rather than proving the original regained capability.

## Source encounters and objections

- John Ruskin, *The Seven Lamps of Architecture* (1849), ch. VI, “The Lamp of Memory,” §XVIII. [Project Gutenberg Boston Dana Estes edition](https://www.gutenberg.org/cache/epub/35898/pg35898-images.html). Search-indexed substantial paragraph consulted; direct retrieval returned 503. Ruskin objects to restoration as destructive replacement accompanied by misleading description. He is concerned with architectural fabric and work, not synthesizer performance; his anti-restoration argument supplies a counterweight to automatic optimization, not a rule for all preservation.
- Patricia Andrew (revised ed.), *Standards in the Museum Curation of Musical Instruments* (MLA, 2005), [PDF](https://collectionstrust.org.uk/wp-content/uploads/2017/02/Museums-Libraries-Archives-Council-Standards-in-the-Museum-Curation-of-Musical-Instruments-2005.pdf), foreword pp. 1–2 and §§6.1–6.16, printed PDF pp. 23–25 (page image p. 24 inspected). Section 6.11 explicitly distinguishes historical sound from an aged artifact's current sound, making a good copy potentially a better approximation of the former. §§6.14 and 6.16 require attention to retained removed parts and documentation. This historical guidance is not a substitute for the applicable present museum policy or specialist conservation judgement. No physical treatment is proposed.
- Guggenheim, [The Variable Media Initiative](https://www.guggenheim.org/conservation/the-variable-media-initiative), second and third substantive paragraphs. Search-indexed text consulted; direct retrieval produced a JavaScript gate. Describing behaviors alongside constituent media permits strategies including emulation and migration. Our extension is to record the *domain of possible future responses*, not merely demonstrate one playback.
- Claudia Fritz, Marguerite Jossic et al., [3D Printing in the Museum: Perceptual Discrimination between a Hotteterre Traverso Facsimile and its Printed Copies](https://doi.org/10.1177/20592043251387546), *Music & Science* 8 (online 11 Nov 2025), introduction, playing-test discussion, listening-test methodology and conclusion as exposed on the publisher's indexed page. The authors report a comparison involving nine professional flutists and 69 listeners; playing-test judgments varied, including between repeated presentations of the same instrument, while the recorded wooden facsimile and selected printed copy were not discriminated above chance under their listening protocol. Their conclusion calls for further work on playing characteristics and bias. Not a full independent appraisal; no equivalence claim beyond that study, and the comparator is itself a facsimile rather than the historical original. The result makes the distinction between played interaction and recorded appearance especially relevant.
- Lior Arbel and Itai Weissman, [Digital Revival: Acoustic Documentation and Digital Reactivation of Historical Woodwind Instruments](https://arxiv.org/abs/2606.24216), arXiv preprint dated 23 June 2026, abstract and §1E; HTML rendering consulted. Their project describes playable digital descendants and expressly does not aim at exact replication. This is a pertinent contemporary artistic practice, not evidence that the present apparatus describes historic flutes.

**Interpretation:** sound is sometimes the thing that needs to be preserved, sometimes the way an object is investigated, and sometimes the very activity that jeopardizes the thing. These are not identical relationships. A document recording a sound can be evidence of an event without constituting a restoration of the instrument. A playable descendant can preserve certain relations without acquiring the provenance of the source object. No source is claimed to endorse this expedition or the project's operational communication preference.

The philosophical danger of the model below is that it makes restoration an optimization, then invites the artist to mistake the optimal point for the right decision. Its numerical costs are chosen, not discovered. Historical significance is not a count of parts. Real intervention risks are not linear or fungible, and playability can be irrelevant to a collection's purpose. The appropriate role of the model is to stage a disagreement between explicit goals.

## A finite organ with a common resource

Four oscillators at 220, 440, 660 and 880 Hz have invented integer efficiencies e=(1,2,3,4). Each fresh replacement sets its efficiency to 4. All are virtual, not physical models. Nonnegative integer settings u_i share an instantaneous budget B, with sum(u_i)<=B. The audible coefficients are a_i=e_i*u_i. No cumulative aging or damage law exists. 'Spending tomorrow' means exhausting present headroom for stronger subsequent requests, not consuming a stored quantity of future time or energy.

The target is a_i=T for all four partials. Minimize E=sum((a_i-T)^2). For ties minimize total drive, then use lexicographic control order. When comparing repair masks in the table, minimize E, then drive, then numeric mask, then settings. Replacement count is an upper bound, not the objective within that feasible set. Neither E nor the abstract drive is a psychoacoustic measure, watts, current, wear or safety limit.

Exact feasibility requires divisibility of T by every e_i and sufficient total drive. The exact required drive, when divisibility holds, is T*sum(1/e_i). At T=12 the aged instrument requires 25 units and the all-fresh instrument 12. Replacing the weakest partial alone reduces demand to 16; replacing the two weakest reduces it to 13; replacing all three degraded partials reduces it to 12. These points are the optimal exact-restoration frontier for this example, because the drive saving of replacing each part is independent: T*(1/e_i-1/4), and picking the largest savings first minimizes required drive at a fixed replacement count. This rule need not hold for coupled instruments or heterogeneous intervention costs.

For approximate fidelity at a bounded drive, the dynamic program starts with D_0(0)=0 and infinite cost elsewhere. With exact spent drive b, D_i(b)=min over integer 0<=u<=b of D_(i-1)(b-u)+(e_i*u-T)^2. Take the minimum over b<=B. Settings above ceil(T/e_i) cannot improve the coefficient error or feasibility; this justifies pruning. The enumerator does not apply that pruning, checking every feasible tuple through cap 25. No new mathematical technique is claimed.

| Maximum replacements | B=12 | B=16 | B=20 | B=25 |
|---:|---:|---:|---:|---:|
| 0 | 122 | 61 | 20 | 0 |
| 1 | 41 | 0 | 0 | 0 |
| 2 | 9 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 |

Entries are minimum squared coefficient errors for T=12. At B=25 every policy can be exact. Their reserves differ.

| Policy | T=12 drive | T=12 unused budget | T=24 optimum error | T=24 output coefficients |
|---|---:|---:|---:|---|
| All fresh reference | 12 | 13 | 0 | 24,24,24,24 |
| Retain all | 25 | 0 | 440 | 6,16,18,20 |
| Replace weakest only | 16 | 9 | 104 | 20,18,18,20 |

At higher demand, the objective chooses to change spectral balance rather than merely reducing level. A timbre-lock policy would select a different optimum. A safety contract could instead refuse the impossible request. Neither alternative is implemented. Note that spare integer drive does not automatically translate into a usable exact amplitude increment, since divisibility still matters.

**Counterexample:** the same reference waveform at T=12 does not imply the same attainable set at T=24. This result is exact only for the defined finite apparatus. A second negative witness is the unadjusted aged instrument, which already differs at T=12. A no-loss reference and zero-target cases were also verified. The test does not establish perceptual differences or validate real calibration, and the choice of higher demand is deliberately adversarial, not a statistical model of musical performance.

## Original score: the two concerts

Each movement contains two one-second notes, each constructed by summing the four sinusoids with a squared-sine envelope, common gain and fixed initial phase. The first requests coefficient 12, the second 24. There is no hidden limiter or per-file normalization.

- I: The archive — all-fresh reference, both requests exact.
- II: The original fabric — retain the aged components and choose the minimum coefficient error. Opening exact; the second note is constrained.
- III: The disputed replacement — restore only the least efficient component, opening exact; second note still constrained.
- IV: The witness without correction — perform original settings 3 and 6 on each aged component, exposing the discrepancy even in the first note. This control uses 12 and 24 drive respectively.

Three opening PCM segments are identical (16,000 frames). All complete signals differ. The recording is an authored miniature, not an acoustic reconstruction of a real historical organ. A performer could extend it by making the higher demand optional, leaving the apparent restoration unchallenged. The piece then includes the decision whether to spend an opportunity to discover a difference.

The [laboratory](laboratory.py) regenerates all four WAVs and a machine-readable receipt. Run `python laboratory.py audio` (standard library only). Native Python 3.13.5: 1,520,064 feasible candidate-vector visits across 16 masks and four targets (repeated vectors across configurations), 1,664 exact comparisons including tie outcomes, three invalid-control refusals, deterministic PCM rerender, amplitude/format/full readback and equal-prefix checks passed. Git blob of executed source: 4212f1d2141d43f4c406e0abf9e45aba643ab089, matched repository readback. Local execution is not whole-repository CI or scientific qualification.

WAV SHA-256 (on this execution environment):
- reference: 2253675d7f16c7fae52401415375beda673417d1a3b9cc34e142f6e03e250f7e
- retained: 39aa3590ded465fa29863604ad72c8d8311cb58fe45f6180d5f12c471a1066cc
- one-replacement: df85aea7c718c92dcc90522a243bfb9a80ad5d29e7c91935d611f5633a2020d9
- unadjusted: 2ef78a09eef8e95b6d895e06dda3c6c307006767d7df3d6d05be2d14530fb81f

## Exaptation and a second expedition

A **Reserve Organ** VSTi could let a musician design oscillator banks with individual response curves, explicit shared control budgets, spare capacity and virtual replacements. The player can switch from coefficient matching to spectral-shape preservation, or perform failures deliberately. The visual interface should expose predicted attainable responses rather than a single green calibration indicator. A **Reserve Auditor** VSTfx could act as a bounded synthetic bank or constrained resynthesis effect with independent dry and compensated channels; it should not claim to diagnose arbitrary hardware. A CYD interface could map X to requested amplitude, Y to the intervention or reserve policy, with a four-partial spectrum and visible resource ledger; no firmware or real-time plugin has been implemented here.

The conceptual extension is not simply a repair simulator. Imagine a duet between the musician who performs on an instrument and a curator who manages the conditions under which it can continue to perform. One writes the sounding score, the other the score of allowable interventions. They share a resource but need not share a musical intention. Their conflicts become musical events. A third player may operate a substitute instrument whose output is indistinguishable at the current target but whose origin is separately documented.

The extension must avoid conflating *instantaneous reserve* with *durability*. A subsequent model could give each component a dynamic stress history, define a bounded future demand sequence, and compare a greedy present-fidelity controller against a policy minimizing maximum future regret. Such a model would require explicit degradation assumptions and falsification; it is not warranted to infer a real lifespan from abstract budgets. A second possibility is interval-valued efficiency estimates: the most important replacement could be the one that decreases uncertainty about future feasibility rather than the one that reduces nominal demand.

For MHAC the design hypothesis is narrow: when a synthetic machine is currently satisfying a request but near its specified capacity, explicitly exposing reserve and the scope of the current success may improve predictions of the next request's feasibility. Compare current-success-only, current-success plus numerical reserve, explicit feasible-demand range, and optional sonification. Hold present carrier identical and include matched reserve with different feasible ranges (discrete constraints) as a negative control. Measure future feasibility judgement, mistaken certainty about provenance and correct action separately. A conventional text/numeric panel may suffice. No human trial, participant contact or operational recommendation; any future experiment must pass the actual programme's human and methodological gates.

## Speculative afterword — The director's third concert

The director heard the organ restored. The conservator showed him the four numbers on the receipt.

He asked the organ to become twice as loud. Three registers obeyed partially and one scarcely moved.

The conservator proposed replacing the weakest register. The director asked whether it would remain the same organ.

The apprentice brought in a second organ, which performed both notes without difficulty. The director asked her to put the original name on it.

She wrote the original name on the score instead.

## Reconciliation and handoff

Read live main AGENTS, RAG, programme, runbook, integrity and validation; sampled 40 updated PR titles and 30 open issue titles, plus targeted overlap searches. Inspected issue #222 (completion after lost archival material), #374 (invisible calibration labour and different histories), #606 (wear and ambiguous history) and #471 (same repertoire but differing cue bindings). Here the primary distinction is a bounded current-versus-future demand frontier under independently constrained active replacement and drive. The earlier work supplies precedent, not a novelty claim. New issue #678 body and comments read (no comments at creation). Base 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-678/restoration-reserve. No shared files, canonical registries, frozen protocol, evidence declarations or production code touched. Draft/HOLD until independent integrator review and exact-head checks. No external review, real intervention, or human evaluation. No rights or licensing decision made.
