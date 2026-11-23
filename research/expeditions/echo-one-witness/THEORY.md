# The Echo of One Witness: epistemic multiplication by repetition

**MHAC-X008 / [#193](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/193) — 23 November 2026.** Original philosophical synthesis and finite synthetic calculation, not MHAC listener evidence, an accepted Track E/G finding, a new probability theorem, or a production audio requirement.

## The four distinct pluralities

Consider eight machine utterances, eight research-agent reports, or eight articles referring to the same claim. Such a collection may have eight **renderings**, eight **documents**, eight **propositions** and only one **original observation**. The counts are not exchangeable. Sometimes one document contains several genuine observations; sometimes many documents are derivative descriptions of one study. A source may be quoted in criticism, not endorsed.

This is not just “duplicate data,” and is not the claim that repetition is useless. Repeated warnings might help reach a listener or overcome masking; repeated arguments can introduce new interpretations. The narrower error is to assign them **new evidential independence** without accounting for their source relations.

The [Cochrane Handbook, Chapter 5 §5.2.1 and MECIR C42](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-05) explicitly makes the **study rather than its reports** the primary unit for systematic review. It warns that multiple reports of a study must be collated and that a report can itself describe more than one study. That is a methodological analogy for claim ancestry here, not a permission to replace MHAC-R006's study/sample identity ledger. The publisher abstract of [Hurlbert (1984)](https://doi.org/10.2307/1942661) defines *pseudoreplication* narrowly in experimental inferential statistics when suitable replication or independence is absent. Applying it to copied AI reports is an **analogy**, not a finding that prose is an experimental replicate.

The [1977 publisher abstract of Hasher, Goldstein and Toppino](https://doi.org/10.1016/S0022-5371(77)80012-1) reports increased perceived validity for repeatedly presented plausible statements in their experiment. This does **not** establish that humans interpret MHAC alarm repetition as independent corroboration, or that an AI agent necessarily accepts its own previous work. Repetition's psychological consequences and its logical accounting are distinct research questions.

## Two incompatible origins, one outward sequence

Let a receiver observe only eight positive messages: (+,+,+,+,+,+,+,+). Construct two different possible histories:

**Echo world E:** one original observation S1 is copied into eight separate downstream reports M1 ... M8.

**Independent-by-stipulation world I:** eight different observations S1 ... S8 are made, and in an explicitly stated artificial model their errors are conditionally independent under both hypothesis H and its negation. Each is reported once.

The observation function from complete ancestry history to emitted message sequence maps both worlds to exactly the same output. No deterministic decoder receiving *only* that sequence can correctly identify the number of original observations in both worlds: it must return 1 in E and 8 in I for identical input. This is a finite elementary observation non-injectivity proof; it is not a novel theorem attributed to Brier, Shannon or another scholar.

The construction is intentionally disprovable when its assumptions change. Authenticated provenance metadata can distinguish histories; a verified source-independent sampling protocol can license additional evidence counting; an observer with access to such a contract is not confined to the eight-message sequence. The impossibility is restricted to **unannotated output-only interpretation**.

The original PCM instrument in echo_lab.py makes the first 5.5 seconds of both constructed worlds byte-identical. Each file presents eight pulses. A subsequent invented one-pulse or eight-pulse legend is an additional root-count code. The result shows that sonic rendering alone cannot encode genealogical structure it was never instructed to convey; it does not show that human listeners can reliably learn the legend.

## The Bayesian multiplication trap

Let H have prior probability 0.5. A fictional primary positive observation has P(+|H)=0.8 and P(+|not H)=0.2, a likelihood ratio of 4. For one such observation, Bayes's theorem yields posterior 0.8.

For n conditionally independent observations, with **factorization both under H and under not-H**, posterior odds equal prior odds multiplied by each observation's likelihood ratio. For eight independent positive *draws*, odds are 4^8 = 65,536, hence posterior 65,536 / 65,537 = **0.9999847414437646**.

If the eight reports are copies of **one** original draw, there was only one probabilistic event. Copying an observed value does not generate seven additional independent likelihood factors. The same eight rendered messages then correspond to a toy posterior of **0.8**. This is not an empirical estimate: the numbers and sampling assumptions are authored expressly to make the structural difference inspectable.

| Fictional ancestry case | Messages | Unique declared roots | Defective message-count posterior | Root-level posterior, assuming conditional independence |
| --- | ---: | ---: | ---: | ---: |
| Eight echoes of one positive root | 8 | 1 | 0.9999847414 | 0.8 |
| Eight independently stipulated positive roots | 8 | 8 | 0.9999847414 | 0.9999847414 |
| Seven copies from source 1 and one from source 2 | 8 | 2 | 0.9999847414 | 0.9411764706 |
| Seven positive claims, one untraced ancestry | 8 | at least 1 identified; remainder unknown | 0.9999847414 | **refuse** |
| Seven copies of a positive source and one independent negative source | 8 | 2 | 0.9997559190 | 0.5 |

The defective comparator always counts each **outward claim** as new evidence; it preserves the opposing message's negative polarity in the last row. The root-aware comparator counts one positive and one opposing source there, whose specified likelihood factors cancel. Untraced ancestry does not prove a claim false; the simple source-count toy refuses the numeric inference because the model has insufficient information. Another properly specified probabilistic model could estimate it.

The figures do not measure human belief, source correctness, calibrated trust, causal independence, or how any production sensor behaves.

## Why even a perfect source ID is insufficient

Suppose eight sensors carry distinct IDs and have different attached “source records,” yet all measure one unmodelled upstream variable X. If the eight measurements are exact copies of X, their one-dimensional marginal sensitivity and false-positive rates can match the independent toy's 0.8 and 0.2, but their **joint likelihood** for all-positive reports is 0.8 under H and 0.2 under not-H, not 0.8^8 and 0.2^8. The likelihood ratio is 4, not 4^8.

Thus *different root IDs* do **not** imply conditional independence. Actual factorization requires a justified dependence model, which may be physical, statistical or experimental. Inversely, one sensor might take genuinely independent measurements over time; using its hardware ID as a fixed one-observation surrogate would undercount. The event root here is a **declared observation event**, not a particular device label.

This refutes two opposed overclaims: “distinct sources are necessarily independent” and “shared equipment means all observations are exactly redundant.” Neither follows from identifier equality.

## What a provenance DAG can and cannot establish

The executable oracle has three typed fictional nodes: an **observation** with source polarity, a **derivative** with one or more declared parent links, and an **untraced** node whose source ancestry is unknown. It computes reachable unique source roots and untraced roots for each emitted message. It rejects malformed IDs, dangling parents, duplicate IDs/links and dependency cycles. Its reference-closure method is exercised against a separately written exhaustive set-union comparator on 64 forward-edge four-node DAGs and each of their 15 nonempty output subsets: **960 ancestry cases**, plus 19 targeted unit test methods overall.

This is useful *accounting*, not authentication. A malicious or careless report could invent its roots; a citation can criticize its source; a high-quality derivation can add new knowledge without adding a new observation; an observed measurement can be wrong. In this model parent edges mean declared derivation, not empirical verification, endorsement or logical entailment.

The refusal to handle cycles is a scope boundary of the stipulated genealogy **DAG**, not a philosophical judgment that scientific discourse must be acyclic. A scholarly criticism may refer back to a response; that reciprocal discourse requires different semantics, not silent conversion into a DAG.

## The intellectual archaeology hypothesis

The repo's many AI-generated notes may carry recurring phrases: distinctions between state and action, data and interpretation, sound and meaning, accepted evidence and synthetic examples. Some repetitions come from explicit agent instructions and shared problem vocabulary; some may be copied; some may arise independently from primary sources. [MHAC-X004](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/184) is the separate lexical-migration atlas. **Identical wording does not prove shared provenance**, just as changed wording does not prove independent observation.

A later audit could choose one concrete proposition and trace the actual documents claiming it: What source did each read? At what extent? Were claims checked against primary material or a predecessor's paraphrase? Did a contradiction survive, or did several restatements acquire the appearance of consensus? Without that trace, saying MHAC has already self-laundered a false claim would be an allegation without evidence. The present finite oracle is **not** a corpus-wide accusation.

This distinction matters especially for claims of “independent review.” Several AI passes may catch different mistakes but share training, prompts, sources, code and assumptions. Mechanically agreeing outputs are not independent scientific validation. Conversely, adversarial review can still be useful; it should describe what was independently checked, not turn headcount into epistemic authority.

## An exaptation that might actually survive

A research claim could carry a minimal **lineage envelope**: claim ID, proposition type, original source IDs and reading extent, derivation links, stance toward a cited source, verification extent, unknown ancestry and *independence not established* unless checked by a separate model. A future auditor could then ask for unique ancestors rather than number of reports. [TRANSFER.md](TRANSFER.md) proposes the envelope without editing shared programme schemas.

The more economical solution may be no new machinery at all: **avoid advertising independent corroboration without warrant**. This respects [T015's synthetic null result](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/59): the simple separately presented-message baseline avoided its fictional failures at lower word cost than lineage narration. A lineage graph could remain a behind-the-scenes audit, revealed only when helpful. Making every audible alarm explain its graph risks needless complexity, especially under a deadline.

The *remove-Brier* test yields a negative result here. All mathematical observations follow from elementary probability, functions and typed provenance. No incremental formal predictive contribution from cybersemiotics is demonstrated. A richer account of interpretants might still motivate worthwhile questions about how people assign credibility, but a genuinely discriminating hypothesis and authorized empirical study would be necessary.

## Evidence classes and refusals

**Proved only in the constructed system:** outward-sequence alias; source-root closure under the declared graph; toy Bayesian values under explicit likelihood assumptions; exact PCM-prefix equality and code/test invariants.

**Source-reported, not independently replicated:** Cochrane's methodological study/report distinction; Hurlbert's pseudoreplication definition; Hasher et al.'s repetition-related judgment results. See [SOURCES.md](SOURCES.md) for exact access and reading limits.

**Untested:** effects on real listener confidence, message recognition, calibration, action correctness, agentic self-endorsement, actual MHAC source graph or accessibility of the musical legend.

**Rejected overclaims:** eight roots automatically means eight independent observations; eight voices automatically means eight witnesses; citation means endorsement; copying necessarily removes all value; distinct agent identities equal independent review; audio can certify physical ancestry; a theorem about one synthetic output map establishes a general human cognitive bias; Brier uniquely explains the probability calculation.

The most useful surviving conclusion is therefore limited and actionable: **before treating repeated assertions as multiple independent pieces of evidence, specify what counts as an observation, trace its provenance, and justify the statistical/causal independence model.** If those are unavailable, report the distinction instead of manufacturing confidence.

For exact run evidence, see [EVIDENCE.md](EVIDENCE.md); for adversarial objections, [ADVERSARIAL.md](ADVERSARIAL.md); for speculative fiction, [AFTERWORD.md](AFTERWORD.md). All actual research programme gates remain intact.
