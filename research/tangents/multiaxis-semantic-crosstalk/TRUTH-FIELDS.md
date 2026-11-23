# Predeclared fictional truth fields

No real alarm, human action or acoustically rendered waveform is represented. Source-state records are **truth-labelled independently of all candidate mapping functions** and are not empirical observations.

| Field | Values | Meaning within the toy model | Independence and exceptions |
|---|---|---|---|
| \`certainty\` | 0 low, 1 intermediate, 2 high, null unknown | Epistemic confidence placeholder only | Not event likelihood calibration; unknown must not become low. |
| \`hazard\` | 0 low, 1 moderate, 2 high, null unknown | Fictional consequence magnitude | High hazard can have a distant deadline; not urgency. |
| \`urgency\` | 0 long deadline, 1 medium, 2 short deadline, null unknown | Deadline proximity placeholder | High urgency can have low hazard; not certainty. |
| \`requested_action\` | \`inspect\` | Fixed control, **not** permission to act | Correctness/action authorization is untested. |
| \`addressee\` | \`operator-A\` | Fixed control | Does not bind real authorized actors (see #43). |

\`CASES.json\` contains exhaustive 3×3×3 = 27 valid fictional combinations (F01–F27), followed by three one-at-a-time unknowns (U28–U30). This includes high severity + long deadline, low certainty + high severity, and low severity + short deadline. All 27 are intentionally feasible **inside this abstract toy ontology**; physical domain-specific feasibility was not evaluated. Unknown is explicit rather than silently imputed.

Comparisons use the same state truth for four policies. A missing semantic field in a simultaneous component candidate receives an explicit \`UNKNOWN\` descriptor; the fused comparator loses which field is missing. Such engineering descriptors do not predict just-noticeable differences, perceptual selectivity, or semantic understanding.

Falsifier: F06 (0,1,2) and F20 (2,0,1) differ in **all three** state fields but collapse under the fused sum. Any proposed semantic mapping that collapses these is non-injective and fails faithful independent-field representation. A non-colliding mapping remains *unvalidated* as an auditory code.
