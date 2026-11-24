# Predeclared policy comparison and scoring

**Four rivals** (fixed before reading synthetic evaluation results):

| Policy | Available information / behavior | Known weakness |
|---|---|---|
| A `value_only` | Report exact indicated value and unit; no conformity claim or no-action instruction. Assume separately inspectable text as a *prospective* accessibility option, not implemented. | Withholds valid concise classification; needs reader to resolve meaning |
| B `naive` | Treat displayed/rounded number <= nominal specification as “within tolerance” and “no action needed”; ignore rule, quality and authority. | Confounds reported value, world truth, authorized class and action |
| C `local_rule` | Classify only using a current, applicable, known-quality selected toy rule, without checking signed upstream approval. | A local inference can remain **unauthorized** as a speech act |
| D `upstream_warrant` | Report the upstream decision only if rule identity/version/quantity/unit, measurement, authorization, evidence and decision all agree. Never infer action. | More words than A; depends on upstream authority metadata being honest, and may suppress useful classes |

**Gold labels:** each of 32 cases has an authored `ground_truth.permitted_class` independent of the policy and a separate `world_conforming`. A candidate class is **unsupported** if it differs from permitted class, **false accept** if it says conforming while the fictional world is nonconforming, and **false reject** if vice versa. These categories can overlap but are reported separately. *Warranted yet world-wrong* decisions demonstrate a residual limit rather than an oracle bug.

Other indicators: omitted justified binary/indeterminate classifications; unsupported `no_action`; numeric value loss from deliberate rounding; use of unavailable rule; total word-token proxy. No probabilities are estimated, and neither word tokens nor synthetic results estimate listening time, trust, usability, safety or participant success.

**Adversarial falsification:** change only rule version (018), upstream authority (019), upstream freshness (020), measured validity (021), known uncertainty (022), quantity/unit (025–026), contradictory upstream claim (027–028), or selected rule for same measured value (029–030). The `naive` strategy should make unsupported safe-ish claims and infer action; `local_rule` should expose unauthorized but arithmetically consistent classes; D should refuse these. If A is equally low-error but shorter, that is a legitimate null hypothesis.

No decision threshold is inferred from risk labels. The acceptance and rejection thresholds themselves are predeclared fictional test parameters. Real JCGM conformance probabilities and guard bands require additional assumptions and are deliberately **not** computed here.
