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
