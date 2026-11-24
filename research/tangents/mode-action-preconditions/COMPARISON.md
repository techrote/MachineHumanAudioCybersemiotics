# Deterministic comparison — 30 fictional scenarios

The independently authored cases give 13 `valid` actions, 5 wrong-mode, 1 wrong-actor, 1 expired, 1 unknown-mode, 2 unknown-actor, 2 unknown clock/deadline, 1 false-source, 1 unknown-source and 3 not-required scenarios. One `valid` row is a duplicate and excluded from missed-*nonduplicate* counts. The artificial mix is **not** a naturally sampled event distribution.

| Comparator | Offers | Wrong mode | Wrong actor | Expired | False known mode | Any invalid/unknown offer | Missed valid nonduplicate | Audible units | Visual units |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A unqualified | 30 | 5 | 1 | 1 | 6 | 17 | 0 | 30 | 0 |
| B narrate all | 30 | 5 | 1 | 1 | 6 | 17 | 0 | 36 | 0 |
| C conditional guard | 9 | 0 | 0 | 0 | 0 | 0 | 3 | 14 | 0 |
| D visual guard | 9 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 14 |
| E no action | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 |

**Counterexample:** M01/M02 have the same `resume_job` imperative but opposing action-time modes, so an otherwise well-addressed instruction can be inappropriate. M03–M05 place a mode transition at successive stages; M08–M10 have stale, conflicting or unknown observation. **Null/negative controls:** M11–M13 are mode-independent actions; B adds units but not better decisions. M23/M26/M30 need no extra action. **Adverse tradeoff:** C and D withhold three genuinely valid, nonduplicate actions (M08–M10) due to insufficient attestation; fail-closed output is not communication success. **Inconclusive:** B might help an actual listener detect change, but there is no listener; D's zero audio units assume an inspectable nonaudio channel and unmeasured accessibility.

These are reproducible symbolic *offers* under strong idealized external guard assumptions, not human error rates or system safety probabilities. Counts may overlap; no policy is endorsed for physical control. `oracle.py` produces the authoritative deterministic report, `MANIFEST.json` pins its bytes.
