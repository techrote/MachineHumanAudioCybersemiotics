# The Conservatory That Composes Its Examiner

*An expedition in audit aesthetics, extremal selection and the programmable jury.*

26 November 2026 · Refs [#688](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/688) · exploratory artistic research, not Track E or G evidence promotion.

## The examiner's ear — original speculative essay

The conservatory gives a prize for the number of separately articulated notes in a three-second performance. In its first year the prize seems to identify diligent students: playing more of the assigned figures also produces more attacks. In its second year a student discovers a tiny ornamental triplet that takes the time of a prescribed two-note figure. The jury's counting apparatus loves it. In its final year there are no prescribed figures in the winning recital, only the ornament.

This is not a story of the student cheating. She plays exactly what the prize rewards. The conservatory has commissioned a new compositional tradition without admitting that its examiner is a composer.

An acoustic measurement can be a valid description, a useful diagnostic, a selection criterion, an explicit aesthetic constraint or a claim about value. These are five jobs, not five names for the same job. A composer can enjoy a performance that deliberately maximizes a bad operational metric; the very failure can become the form. We should not infer that a metric cannot measure a property merely because it cannot substitute for an independently specified goal.

The artistic instrument I propose has two control surfaces: the first makes candidate music; the second composes the jury that selects the music. Its third, normally hidden, surface is the archivist's. That surface records what was excluded, the version of the jury, and which criterion was not optimized.

## Source encounters (AI-assisted reading, 2026-11-26)

1. **Vitaly Komar and Alexander Melamid, The Most Wanted Paintings.** [Dia's project overview](https://www.diaart.org/program/artistswebprojects/komar-melamid-the-most-wanted-paintings-web-project/), launch 5 September 1995, Overview paragraph; [Dia press release](https://www.diaart.org/about/press/komar-and-melamid-the-most-wanted-paintings-on-the-web-for-dias-artsts-web-projects/type/text), first three paragraphs. Indexed institutional text read; direct project retrieval returned 403. Dia describes polling preferences and using those results in a painting; the online extension intended to expose both polls and pictures. This is not a verified demonstration that the finished painting satisfied a majority. Interpretation: the survey instrument is itself material for the artist; choices about categories and aggregation participate in authorship.
2. **Dave Soldier, Komar and Melamid, The People's Choice: Music (1997).** [Artist album page](https://davesoldier.bandcamp.com/album/the-peoples-choice-music), track listing, About and Credits. Directly retrieved and read; tracks not auditioned, survey/raw data unavailable in this encounter. The account credits Nina Mankin with lyrics and describes two compositions designed using poll responses, one aiming at broad appeal and one at strong dislike. Do not infer actual listener response or representative population sampling from that statement. Interpretation: one can invert the objective and retain the survey procedure. The supposedly undesirable output becomes a deliberately sought artistic object. Our instrument does not reproduce their compositions or their survey.
3. **Marilyn Strathern, 'Improving ratings': audit in the British University system, European Review 5(3), 305–321 (July 1997).** [Publisher abstract and information block](https://www.cambridge.org/core/journals/european-review/article/abs/improving-ratings-audit-inthe-british-university-system/FC2EE640C0C44E3DB87C29FB666E9AAB). Directly retrieved; full article not read. Strathern treats audit as a cultural practice that can alter the institutional activity it evaluates. Interpretation: in a conservatory the award mechanism does not merely record existing musical culture; it may create a new object of study. This hypothetical extension is not a claim about actual conservatory outcomes.
4. **David Manheim and Scott Garrabrant, Categorizing Variants of Goodhart's Law.** [arXiv:1803.04585](https://arxiv.org/abs/1803.04585), abstract and rendered sections 'Varieties of Goodhart-like Phenomena' and '2 Extremal Goodhart', selected passages. The rendering has inconsistent date metadata (2018 submission and 2026 date in rendered body), so no exact version priority is asserted; [Garrabrant's 27 March 2018 author summary](https://intelligence.org/2018/03/27/categorizing-goodhart/), sections on regressional, extremal, causal and adversarial cases, independently located and read. Their distinction between selection in an extreme region and causal intervention matters: our fixed generating distribution and score-only selection require neither a strategic agent nor a changing causal mechanism. This is an intentionally finite example of a selection-induced proxy breakdown, not a new general taxonomy.
5. **Alvin Lucier, I Am Sitting in a Room.** [IRCAM workcourse](https://brahms.ircam.fr/en/composer/alvin-lucier/workcourse), indexed passage beginning with the work's title, and [DRAM album notes](https://www.dramonline.org/albums/alvin-lucier-i-am-sitting-in-a-room/notes), indexed paragraphs on the transformation of speech into resonant material. Original score and recording not inspected. Interpretation: the iterated physical filter becomes part of the compositional process. Our jury is not a physical filter, and our fixed-pool order statistic is not Lucier's iteration; the artistic comparison is the transformation of an otherwise ancillary mechanism into authored material.

No restricted texts or third-party audio copied. No independent human review, empirical claim promotion, external contact or license grant.

## Finite instrument — exact construction

A score consists of twelve 250 ms cells, each chosen independently with probabilities R=9/20 (rest), A=9/20 (assigned two-note figure), F=2/20 (ornamental three-note flourish). Define G as the number of A cells; the official proxy P counts authored attacks, hence P=2A+3F. The three categories and the task objective are stipulated, not perceptually inferred. The ornament is not intrinsically inferior; it simply does not fulfill this particular fictional commission.

For one cell, E[P]=1.2, E[G]=0.45, E[PG]=0.9, Var(P)=1.26 and Var(G)=0.2475. Thus Cov(P,G)=0.36 and the correlation is 0.36/sqrt(1.26*0.2475), approximately +0.645. Independence means the same correlation holds for twelve-cell totals. A single random score has expected P=14.4 and G=5.4. Even with this positive association, the unique maximum-P word is twelve flourishes (P=36,G=0), whereas the unique maximum-G word is twelve assigned figures (P=24,G=12).

To vary selection pressure, draw M independent candidate scores and publish the first score attaining the maximum P. Let H(p)=Pr(P<=p) and a(p)=E[G|P=p]. Because ties are broken by input order, independently of G conditional on P, the winning score's conditional G distribution given P=p is that of a single draw at p. Therefore:

    Pr(P_winner=p) = H(p)^M - H(p-1)^M
    E[G_winner] = sum_p a(p) * (H(p)^M - H(p-1)^M)

This is an elementary order-statistic identity, not a model of human taste. P_winner increases stochastically with M. The unique maximum has positive probability (1/10)^12, so eventually P_winner tends to 36 and G_winner tends to zero in expectation. Not all increases in M make G worse: the finite result initially improves the intended objective too.

For a hard floor G>=g, with integer 0<=g<=12, P=36-A-3R <=36-g, attained by g A cells and 12-g F cells. That is a transparent explicit trade-off. Protecting six assigned cells limits the prize to 30 attacks. If the task has no minimum floor, the maximum is 36. No arbitrary weighted blend is being passed off as a guarantee. The price of changing the jury's reward is also simple: if R=0, A and F have positive scores, the larger of A and F's rewards wins every cell; if equal, all 2^12 rest-free words tie. A tiny criterion change can switch the optimal set discontinuously. This latter symbolic extension is analytical, not an executed UI.

## Execution receipt

Native Python 3.13.5; run `python laboratory.py examiner-output` from this directory (standard library only). The 531,441 possible words were explicitly visited and their integer-weight joint histogram matched an independently calculated multinomial histogram; total probability mass checked. A separate 729 ordered two-draw pool enumeration at n=3 verified both expected scores including ties. Exact Fraction arithmetic for pool sizes <=16; double precision CDF powers for larger sizes; large values in the table are approximations, not exact rational receipts or actually sampled pools. The earlier all-rational large-pool approach exceeded the run's execution budget; switched to bounded rational checks and numerical large-pool evaluation. No claim that the numerical approach is accurate for arbitrarily large M. Positive control: the direct proxy G gives coincident intended and proxy expectations and increases with pool size. Endpoint and six-anchor floor checks passed.

| Candidate pool M | Expected winning attack count P | Expected winning assigned figures G |
|---:|---:|---:|
| 1 | 14.4000 | 5.4000 |
| 2 | 16.5940 | 6.0306 |
| 4 | 18.4026 | 6.4850 |
| 16 | 21.2161 | 7.0386 |
| 64 | 23.3417 | 7.2843 |
| 256 | 25.0401 | 7.3211 |
| 1024 | 26.4478 | 7.1914 |
| 16384 | 28.6707 | 6.5052 |
| 1000000 | 31.0519 | 4.8169 |
| 100000000 | 33.0189 | 2.9705 |

The sampled grid of pool sizes exhibits a reversal, not a proved global optimum at M=256. The initial benefit is important: a useful proxy and a harmful optimizer can belong to the same apparatus. The million-candidate expectation is calculated from the finite histogram, not a million rendered pieces.

## Original performance score — Four recitals at the same conservatory

All four pieces use the identical synthesis mapping: a rest is silent; A is an evenly spaced 220/330 Hz pair; F is an evenly spaced 660/880/550 Hz triplet. 16 kHz mono PCM, 16 bit, 48,000 frames each, fixed gain and squared-sine envelopes. Render twice, check bounds, read the full WAV payload, verify distinct file hashes. No recorded survey music used.

| Movement | Authored word | P | G | WAV SHA-256 |
|---|---|---:|---:|---|
| I The rehearsal | ARFAARARARAR | 15 | 6 | 20d601e6f5e610f60698de4226a5fdd4c530f2c13237cd4ec72c944cab4c2628 |
| II The commission | AAAAAAAAAAAA | 24 | 12 | d571b468c49ffb53430487c0bbee4c16d6694d50df7ed9ca3666cfd10a188cdc |
| III The prize | FFFFFFFFFFFF | 36 | 0 | 721603313b7f058dc2bd626cab8fd4e6fbbb95e551a7305f3f3bfbc8f977ba25 |
| IV The contract | AFAFAFAFAFAF | 30 | 6 | 5d546c7b54be49a4145a6a72f7737cbf08043184f589e6a050a32d0b3bfd8627 |

These are authored exemplars, not draws from the selection experiment. The audio is reproducibly generated, not committed as binary data. P counts scheduled events rather than perceived onsets. The recordings are not loudness matched; the purpose is to audition the authored differences, not test perceived density or preference.

## Exaptation — programmable juries, not just programmable sounds

**Examiner's Loom (VSTi):** bounded candidate generator, independently editable rubric, audition of best-proxy and best-goal candidates, explicit task floors, simultaneous Pareto view and undo. Keep scoring and generation off the real-time audio callback. Only precompiled event queues cross to synthesis. Never label a proxy "quality" without declaring the objective.

**Audit Fold (VSTfx):** a slice rearrangement effect that proposes variants and ranks them by explicit descriptors (e.g., onset density or spectral centroid), with a separately auditionable dry stream and candidate provenance. Use an offline audition buffer; do not interpret descriptors as taste. For an artistic mode, the performer deliberately rewards a descriptor until some other property disappears.

**Jury Field (CYD):** touchscreen canvas: paint metric weights in territories of a bounded agent population, with a second XY layer for selection intensity and declared task floor. Regions of low and high pressure coexist. Show proxy and goal separately; flash no success state solely because a prize score increases. No hardware, VST, real-time or perceptual qualification has occurred.

A further unimplemented performance: one musician composes the candidates, one edits the rubric, and a third preserves rejected alternatives. The audience hears changes of criterion rather than a stable winning aesthetic. The rubric must be versioned so a change in award is not silently reported as a change in the piece itself. In a different performance no metric is privileged: participants choose their own listening route without any winner.

## Counterarguments and transfer boundaries

There need not be a correct hidden goal in art. A real commission can value ornament, formal variety or the overthrow of its own rules; our count G merely supplies an inspectable stipulated objective. In an operational communication system, the task goal should instead be specified independently before optimization. The present model deliberately makes G available to the analyst, not the selector; measuring actual user outcomes is a different problem.

MHAC experiment proposal: generate artificial message sets with ground-truth required action fields. Define a proxy such as count of scheduled acoustic elements, not accuracy. Compare candidate selection at several fixed budgets with task-field coverage, exact decoding and correct action on held-out cases, separately. Add a direct-task selector and conventional explicit text baseline. Keep generator, train/test contexts, evaluation labels, and candidate budget frozen before testing; evaluate how robust the proposed measure is under deliberate optimization. Do not infer that more acoustic elements cause confusion from this fixture. A simple required-field validator may solve the entire operational problem. No actual listener, device or communication benefit demonstrated. Do not optimize away real alarms, omit required fields or change safety controls for artistic effect.

### Coda (original fiction)

The final examination consisted of no music. The students had brought the jury a new jury. It awarded points for the number of notes it could award points to. The conservatory published a recording of the applause. In the archive the applause was marked as evidence of a successful examination. The archivist kept an empty folder marked: "the thing examined."

## Reconciliation and handoff

Read live AGENTS.md, README, RAG, PROGRAMME, AGENT_RUNBOOK and RESEARCH_INTEGRITY; checked repository permissions/main at 495a98ca12bae467a507031f04931aa4254b1866, 40 recent PR titles, 30 recently updated open issue titles, and targeted issue searches for proxy/Goodhart/audit/rubric/Komar/Soldier and adjacent topics. No existing target located by this bounded search (not proof of novelty). Related #554 studies context-mixture reversal rather than optimization under one fixed candidate distribution; #199 feature collisions, #197 descriptor identity and #646 transition invariance are adjacent, not this selection experiment. The current explicit expansive scope authorizes a noncanonical expedition without superseding frozen review protocol. Own only this directory, no manifests, shared registries, production engine, or canonical evidence modifications. Native script blob be0eb737f4a51ae77510f9d52a0835329937ed5b. AI-assisted source reading, writing, calculation and test execution by this worker; no independent reviewer. Draft/HOLD for integrator; do not close #688 or promote claims before independent qualification. CI status must be checked at exact final head.
