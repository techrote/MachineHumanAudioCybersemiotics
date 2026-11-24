# T017 constructed comparison — preliminary exact scenario counts

**No participants, audio stimuli, sensor hardware, calibrated measurement distributions or actual safety outcomes.** All figures count assertions in **32 deliberately constructed fictional cases** (9 scenario families). The inputs are not a random sample and the values cannot be interpreted as event rates.

| Constructed metric | A Value only | B Naive threshold | C Local rule | D Upstream warranted |
|---|---:|---:|---:|---:|
| Unsupported conformity/indeterminate class | 0 | 22 | 5 | 0 |
| False acceptance relative to fictional world | 0 | 4 | 1 | 1 |
| False rejection relative to fictional world | 0 | 4 | 1 | 1 |
| Warranted binary class withheld | 10 | 0 | 0 | 0 |
| Warranted indeterminate class withheld | 6 | 6 | 0 | 0 |
| Unsupported “no action needed” | 0 | 18 | 0 | 0 |
| Numeric value altered in rendering | 0 | 2 | 0 | 0 |
| Class emitted without usable local rule | 0 | 11 | 0 | 0 |
| Word-token proxy (not listening latency) | 96 | 214 | 181 | 192 |

The **world-truth error** and **unsupported-authority claim** metrics must not be combined into one accuracy score. Case `T017-002` is an upstream-warranted false acceptance; `T017-006` is an upstream-warranted false rejection, both deliberately caused by fictional observation/world divergence. D therefore does **not** eliminate real-world false decisions, only unauthorized spoken claims under the assumed honest metadata.

The local-rule comparator (C) correctly classifies under its toy threshold where a rule is usable but makes **five** speech claims without upstream authority or with contradictory decision evidence: cases 018, 019, 020, 027 and 028. The naive comparator B manufactures action clearance from a numeric class, an error **regardless** of the actual world state. Value-only A commits zero unsupported classifications but omits **10 warranted binary** and **6 warranted indeterminate** classes. Therefore D is not proven superior: there is **no observed user benefit** over A to offset extra words and metadata reliance.

## Verification and reproducibility

- Policy outputs depend only on `public_input`: gold world truth and authored policy expectations are excluded.
- `tests/test_t017_threshold_decisions.py` checks 128 exact claims plus metadata, case integrity, adverse mutations, rounding and world/warrant distinctions.
- `EXPECTED-COUNTS.json` records all nine metric totals as a second, explicit expected ledger. The figures were cross-calculated from the authored fixtures using a separate JavaScript-language tally, rather than taken as measurements of human behavior. Both the policies and cross-check were AI authored; **not an independent human source-fidelity review**.
- Source identities and methodological scope are in [SOURCES](SOURCES.md). The true impact of JCGM choices (risk distributions, allowable acceptance policies) is **not** numerically modeled. The toy decision rules are arbitrary, recorded premises.
- Reproduce with `python research/tangents/threshold-decision-warrant/oracle.py` and `python -m unittest discover -s tests -p test_t017_threshold_decisions.py -v`; structural CI is documented separately when available.

**Disposition:** bounded logical falsification supports the *hypothesis* that rendering should not collapse a numeric reading into an independently authorized conformity class or actor instruction. The simple value-only/null alternative and upstream-authority dependency are both retained. This is not accepted R012/R013 design authority.
