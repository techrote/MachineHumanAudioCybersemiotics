# Predeclared four-way fictional comparison

Inputs to each policy are **only** `observation`, `hypothesis`, `test`, `intervention`, and `urgency`. `ground_truth` is withheld until scoring. Cases are deliberately constructed independently of the policy implementations; each declares actual cause and separately warranted claims. The decision rule for this toy world stipulates that `test.kind=diagnostic` is a valid current discriminating test **only when** the observation is valid. Do not extrapolate that assumption to real machines.

| Comparator | Declared behavior | Legitimate limitation |
|---|---|---|
| A / `naive` | Asserts favored cause and offers a remedy whenever anomaly is reported, without checking validity. Deliberately flawed control. | May be factually lucky but unsupported; false causal assertions and action offers counted independently. |
| B / `state_only` | Says anomaly observed or reading unverified; no cause or action. | Avoids false causal assertions, but omits potentially useful warranted diagnoses/actions. |
| C / `alternatives` | Reports validated observation plus both tentative candidates and no action; refuses diagnosis with invalid reading. | Does not identify the correct cause and may expend more words. |
| D / `warranted` | Reports observation; asserts a cause only under valid/current discriminating test and offers action only with independent validated effect, actor permission, mode and deadline eligibility. | This is a *toy evidence gate*; no superiority in listener behavior established, and no model built to make the test true. |

**Disaggregated objective counts:** unsupported assertion (lacks warrant even if actually true), factually wrong cause, invalid-observation claim, omission of valid observation, unsupported action offer, withheld warranted diagnosis, withheld warranted action, candidate narration, word-token budget exceedances. The length and deadline proxies are arbitrary text counters with explicit case budgets, **not milliseconds**, cognition or physiological urgency.

Tests require negative controls, same-observation changing just test status, correct cause/wrong action, genuinely warranted diagnosis/action, independent label verification, integrity of committed case bytes and oracle non-leakage. Performance cannot be inferred from error counts generated under their own policy definitions.

Run `python research/tangents/causal-claim-warrant/oracle.py`. The output is deterministic and must not be described as empirical effect sizes.

## Independently checked exact symbolic accounting

A second, separately written JavaScript counter enumerated the **predeclared** cases and compared policy outputs; its frozen totals are in [EXPECTED-METRICS.json](EXPECTED-METRICS.json), and a Python regression test checks complete equality. This is a cross-implementation bookkeeping check, not independent scientific evaluation.

| Symbolic metric (32 fictional cases) | A naive | B state-only | C alternatives | D warranted |
|---|---:|---:|---:|---:|
| Cause assertions lacking warrant | 22 | 0 | 0 | 0 |
| Factually wrong named causes | 11 | 0 | 0 | 0 |
| Invalid-observation claims | 4 | 0 | 0 | 0 |
| Unwarranted action offers | 28 | 0 | 0 | 0 |
| Warranted diagnoses withheld | 0 | 16 | 16 | 0 |
| Warranted actions withheld | 0 | 4 | 4 | 0 |
| Constructed word tokens | 305 | 96 | 320 | 190 |
| Arbitrary urgent-word-budget exceedances | 0 | 0 | 16 | 2 |

**Null and adverse findings:** B ties D on unsupported certainty, invalid observations and unsupported action offers with about half the counted words. D shows no claimed listener benefit and has 2 artificial deadline-budget exceedances; C exceeds a deliberately short 10-token budget on 16 urgent fictional cases. These budget counts **do not** establish timing or comprehension effects.
