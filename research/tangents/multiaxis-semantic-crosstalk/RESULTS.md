# Deterministic synthetic audit — 2026-11-04

Command: \`python research/tangents/multiaxis-semantic-crosstalk/analyze.py\`. Inputs are source-controlled \`CASES.json\` and \`MAPPINGS.json\`; zero stochastic sampling, waveform generation or external services.

| Policy | Truth cases | Distinct exact codes | Extra cases in collision groups | Collision groups | Field-addressable |
|---|---:|---:|---:|---:|---|
| A fused scalar | 30 | **8** | **22** | **6** | **No** |
| B naïve component | 30 | 30 | 0 | 0 | Yes (symbolic only) |
| C candidate component | 30 | 30 | 0 | 0 | Yes (symbolic only) |
| D serialized fields | 30 | 30 | 0 | 0 | Yes (symbolic only) |

The fused scalar compresses 27 fully specified truth tuples to 7 sums plus one common unknown code. F06 (certainty 0, hazard 1, urgency 2) and F20 (2,0,1) collide although **all three** source fields differ. Three explicitly unknown cases also collide in the fused comparator. The total *22 extra cases* is \`sum(group_size - 1)\`, **not** 22 human errors or 22 unordered colliding pairs.

**Positive null for component encoders:** no **exact symbolic code collisions** in the declared 30 fixtures; unaffected component descriptors remain fixed in single-field counterfactual comparisons. These are near-tautological results given injective per-field scales, not proof of separated percepts or stable meaning. The serial alternative is likewise not established superior under real timing/attention demands.

**Adversarial rejection:** a swapped/non-monotonic certainty scale and a saturated hazard scale raise validation failures. Explicit unknown is distinct from zero. This checks only declared ordinal direction and exact symbols; sign and slope expected by real listeners are **not** established.

**Interpretive decision:** Reject A as a lossless three-field representation for these states. Retain B, C and D only as unvalidated comparison candidates. If no consequential application needs simultaneous three-field communication, the null/no-vocabulary option remains appropriate. Future audibility/tolerability, learning and human semantic/action endpoints are separate and gated.

Local prepublication rehearsal: 7/7 Python regression tests passed on the identical implementation and fixture model in an isolated directory; repository-wide validation and exact-head CI must independently run on the published GitHub tree. No empirical or listener data have been created.
