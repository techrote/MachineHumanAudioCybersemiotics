# T015 bounded fictional policy comparison

**Predeclared case set:** 40 two-message traces, 20 negative/controls, 10 of each relation category. **Not listener outcomes, physical sensor validation, safety rates, observed source dependence, or accepted study data.** The authored truth oracle supplies event, authorization and deadline labels to *all* policies. Reproduce with `python research/tangents/alarm-evidence-independence/oracle.py --check`.

| Metric over constructed cases | A: proximity | B: device ID | C: lineage | D: separate |
|---|---:|---:|---:|---:|
| Unsupported independent-evidence assertions | 27 | 19 | 0 | 0 |
| Verified independence not reported | 1 | 5 | 0 | 10 |
| Required action keys entirely missed | 4 | 6 | 0 | 0 |
| Eligible independent observation messages lost | 3 | 4 | 0 | 0 |
| Eligible message offers suppressed | 12 | 9 | 4 | 0 |
| Unsupported/late action offers | 0 | 0 | 0 | 0 |
| Spoken message offers | 48 | 51 | 56 | 60 |
| Word-token proxy | 384 | 408 | 672 | 480 |
| Serial 0.1-second delay units proxy | 1536 | 1632 | 2688 | 1920 |

A/B are **intentionally defective models**; their failures reflect the constructed cases and code, not prevalence in real machines. The proximity rule conflates adjacent messages with independent evidence and can collapse two actions of a single event; the ID rule confuses device labels with evidence units and can collapse two independent events. Mutation tests isolate temporal proximity from declared lineage and retain negative authorization/expired-event controls. Zero late offers in *all* policies is a **design artifact** of the idealized common eligibility filter.

**Important null:** D avoids unsupported corroboration and missed action obligations without trusting source-lineage annotations. C uses presumed correct provenance and suppresses four exactly duplicated (observation, event, action) messages. C has **no advantage** in the basic obligation-coverage metric here and pays a hypothetical 192 extra word tokens over D. D abstains from declaring independent support even when author-labelled sources are independent: that is an information omission, not automatically a safety error. A tested benefit for explicit corroboration, compressed duplication or correct user judgments is currently **absent**.

**Independent-of-claims accounting:** `EXPECTED-METRICS.json` is a separate JS arithmetic cross-check over frozen authored cases, but is produced by the same AI worker. This detects many implementation errors, not author bias or mislabelled fictitious worlds. No blinded annotators, actual acoustic stimuli, reaction times, receiver hearing profiles or prospective study were collected.

**R008 comparison:** Parsimonious common-cause reasoning requires reliable upstream identities; auditory scene analysis describes how sound sequences may be grouped but cannot verify those identities; semiotic/pragmatic accounts may explain listener attribution but require an **additional falsifiable, differential prediction** to warrant theoretical preference. The fictional results alone give no incremental evidence for cybersemiotics relative to explicit typed message identity and conservative reporting. Formal R008 remains dependent on R006 evidence acceptance.