# The Corrector That Manufactures Its Evidence

**Exploratory expedition #398 · 24 November 2026 · AI-assisted writing and formal construction.** Not frozen Track E/G evidence, medical theory validation, or production design.

## 1. A conservatory with a recording problem

Imagine two musicians who have agreed to a very simple dialect of pairs: in one, the second sound repeats the first; in the other it answers with the opposite sound. The two kinds of pair are perfectly systematic. An automatic accompanist has been trained to recognize only the first. It treats the second as a failed attempt at the first and repairs it.

A century later, a scholar studies the accompanist's recordings. No surviving pair contains an answering note. The scholar concludes that the musicians were incapable of answering one another.

The error has moved. It was first alleged to inhabit a musical phrase. It now inhabits the evidential relation between an archive and the world from which the archive was made.

This is an imagined example, not a historical case. Its central problem is not merely whether correction is accurate, but whether the correction apparatus produces the evidence by which its own authority is subsequently judged.

## 2. Encounters and limits

**Canguilhem.** Georges Canguilhem, “The Normal and the Pathological,” chapter 6 of *Knowledge of Life*, English edition (Fordham, 2008), printed pp. 121–126, especially 122 and 125–126: [public chapter excerpt](https://www.ias-research.net/wp-content/uploads/2018/02/Canguilhem_Normal_Pathological.pdf). Read the accessible opening passage and inspected page images 122 and 125. Canguilhem contrasts a statistical description of normality with an evaluative ideal. His discussion of variation refuses to define singularity solely as failure relative to an invariant type. This is a philosophy of life and medicine, not a warrant for declaring a synthesizer alive, treating disability as a coding defect, or redefining engineering safety as taste. The software analogy is mine: a learned frequency is not an authorization to repair.

**Linguistic Society of America.** “Resolution on the Oakland Ebonics Issue,” January 1997, clauses (a)–(d), [drafter's Stanford-hosted text](https://stanford.edu/~rickford/ebonics/LSAResolution.html). Read all four clauses. The resolution recognizes the systematicity of African American Vernacular English, explicitly rejects deficit characterizations, and recognizes the benefits of access to Standard English without requiring the denigration of another variety. This is a scholarly society's statement in a specific educational and political controversy, not an independent review of the studies it invokes. The present binary musical pairs do not model AAVE or any community. A crucial distinction survives the analogy: teaching an additional convention need not require treating a person's existing convention as defective.

**George E. Lewis.** “Improvised Music after 1950: Afrological and Eurological Perspectives,” *Black Music Research Journal* 16(1), 91–122 (1996), [DOI](https://doi.org/10.2307/779379), [accessible transcription](https://www.academia.edu/165349872/Improvised_Music_after_1950_Afrological_and_Eurological_Perspectives), opening pp. 91–95 and selected discussion of Cage, pp. 96–97. Lewis makes improvisative practices historically situated rather than ethnically essential and criticizes accounts that erase African-American influence. The historical asymmetries matter: a neutral-sounding repertoire of permissible events can hide decisions concerning which musical traditions have authority. A numerical controller cannot explain those histories. Nor should the two imaginary grammars be mapped onto Lewis's categories. His account also complicates our score: an arranger may have to learn a practice from its practitioners rather than merely admit another option to a menu.

**Perdomo, Zrnic, Mendler-Dünner, Hardt.** “Performative Prediction,” PMLR 119, 7599–7609 (2020), [publisher record](https://proceedings.mlr.press/v119/perdomo20a.html), abstract only. The authors formalize prediction-induced changes in the distribution that the predictor encounters. The present elementary recurrence is not their theorem; it makes a particular editorial mechanism explicit. A stable classifier may be describing a world altered by classification. That observation is not itself evidence of an injustice.

All sources checked 2026-11-24 by this AI-assisted expedition. No human verification, full-book reading, or corpus eligibility is asserted. The LSA text and Lewis's essay address lived social histories; these histories are not interchangeable with biological norms or machine feedback. The juxtaposition is interpretive.

## 3. Four distinctions and an objection

- Frequency: what occurs in an identified source population.
- Grammar: what counts as well formed under an identified practice.
- Purpose: whether a particular event fulfills a specified function.
- Authority: who may choose or amend the operative criterion.

These axes can disagree. A rare word can be grammatical; a familiar warning can be wrong; a deliberate musical rupture can be authorized; a popular repair can erase a valid minority practice. Conversely, an infrequent safety fault can really be dangerous, and an explicit interchange format can legitimately forbid certain messages. The answer is not to abandon norms. The answer is to locate the type of norm and its warrant.

Consider a second objection. Preserving all alternatives indefinitely could bury the musician under an archive of unusable proposals. Statistical regularization can genuinely support learning. The claim here is narrower: do not represent data *after a coercive or selective intervention* as an unmediated census of the data before it. A declared canonical output is a useful object, but a different object.

The corrective loop below models only frequency. A separately specified grammar remains authoritative for validation. It is possible to use frequency to select among already valid expressions without letting frequency decide validity.

## 4. Exact construction: two histories, one source

Let grammar A allow pairs 00 and 11, grammar B allow 01 and 10. In this toy score the label is the relation, not the first token. An editor converts B to A by replacing the second token with the first. Such an operation preserves the first token and destroys the distinction between the two relations. A single edited pair cannot reveal which relation was originally authored.

Let p be the share of B in a stable independent fresh source, q the share of B in the current archive, a the fraction of the next archive replenished by unedited fresh material, c the fraction of inherited B converted to A when q is below threshold t. All quantities are in [0,1]; assume 0<a<=1, 0<t<p<=1. The editor stops correcting when q>=t. The next archive is a mixture of fresh and inherited edited material, not a simulation of independent people.

q' = a p + (1-a)(1-c)q, if q<t.
q' = a p + (1-a)q, if q>=t.

The high branch converges to p and is invariant because p>t. On the low branch the contraction coefficient is r=(1-a)(1-c) and the fixed point is L=ap/[1-r]. Since a>0, r<1.

If L<t, every low start stays low and converges to L; every high start stays high and converges to p. Hence the same source and same correction policy have two basins. If L>t, a low start crosses t in finite time because the hypothetical low trajectory converges to L, and thereafter converges to p. At equality L=t, a low start approaches t from below forever when r>0; if r=0 it reaches t immediately. This boundary matters: seeing an improving metric does not guarantee a finite transition.

The critical replenishment fraction is a*=tc/(p-t+tc). Strictly above it recovery is guaranteed; below it a low basin survives. At the threshold use the equality rule above. If c=0 and a>0, correction is absent and recovery occurs; if a=1 the archive is exactly the fresh source after one step.

Example p=3/5, t=1/2, c=1/2: a*=5/7. With a=1/4, L=6/25=0.24 and p=0.60. A low-start archive settles at 24% B although the fresh source contains 60% B. A high-start archive settles at 60%. Raising a to 3/4 yields a low-branch fixed point 18/35>1/2 and, from zero, reaches 0.45 then 0.50625. No stochastic sampling or physical process is implied.

**Proof of the threshold:** the denominator is a+c-ac>0. L>t iff ap>t(a+c-ac), iff a(p-t+tc)>tc. This is algebra, not a new mathematical theorem.

**Tests actually executed:** oracle.cjs, 4,950 parameter configurations with t,p,a,c in tenths and p>t; 54,450 one-step grid transitions; 187,418 assertions. Integer mass accounting separately decomposes fresh, inherited, and overwritten B, checks range, basin invariance, fixed-point direction, recovery progress and degenerate equality. Three rational trajectories were evaluated for twelve steps with BigInt arithmetic. The grid is not a proof for real parameters; the preceding argument is. Neither establishes a human effect. To rerun: node oracle.cjs.

## 5. The score and the instrument

See [SCORE.md](SCORE.md): a four-movement work for a source player, editor, archive player and independent witness. Two distinct archive histories are played against a shared source. The object composed is the feedback routing, not a culturally imitative dialect.

The **Provenance Quantizer** is an instrument proposal, not an implementation. It has a raw-input lane, grammar validator, optional editorial transformer, output ledger, and separately routed training feed. A macro can route the edited output back into future motif selection. Another controls how much of an untouched source enters that selection. The musician can hear the source and edited archive in counterpoint, then decide whether to retain the editor at all.

Potential controls: grammar ID, correction scope, correction intensity, raw-source fraction, separate learning and playback taps, and explicit reset of learned preferences. Do not silently rewrite the source. Permit an intentional departure and a real format failure to coexist as distinguishable events. A novelty-preserving mode is not automatically more musical; audition the edited version as a legitimate aesthetic option.

For operational MHAC, use the weaker inference: a post-filter message distribution may not identify the pre-filter distribution. A future authorized synthetic comparison could hold the source stream fixed, vary the editorial rule, and compare provenance-aware reporting versus aggregate output counts. Outcomes: correctly distinguish source change from editorial change, actual protocol violations, false anomaly classifications, latency and burden. Required semantic fields and hazard reporting must not adapt away merely because an event is rare. If a simple raw/output counter suffices, reject a more elaborate cybersemiotic layer. No listener recruitment, no protocol amendment, no production code.

## Reconciliation and custody

Read live AGENTS, README, RAG, programme, runbook, research integrity, research workspace, and new issue/comments; recent 100 PR and 70 open issue title results plus targeted Canguilhem/dialect/normativity/markedness/anomaly search. Base commit 495a98ca12bae467a507031f04931aa4254b1866 (latest commit returned at intake; branch created from this exact SHA). The Migrating Timbre (#198) handles resemblance drift, #367 revision counterpoint handles discarded material, #351 equivalence merging, #391 invitation allocation, and the earlier performative warning addresses forecast-induced outcomes; these are adjacent, not claimed exhaustively disjoint after title triage. This expedition specifically studies retraining on edited musical distributions and the threshold for recovery with fresh input. No change to accepted research records, frozen protocol, shared index, dependencies or other branches. No independent review, external author contact, human data, or license grant. All text and score are original constructions; no source PDFs copied into the repository.
