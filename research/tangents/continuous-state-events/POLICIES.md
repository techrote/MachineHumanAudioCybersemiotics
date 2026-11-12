# MHAC-T005 — Candidate policies and independently encoded trace contracts

The [fixture ledger](STATE-TRACES.json) contains **25 deliberately fictional cases**. Each case gives `sources` and `events` as separate maps; one target source and optional target event; evaluation time in milliseconds; playback status; optional clear cue; and separately stored acknowledgment and action-completion lists. The optional, **fictional pretrusted** `recovery_binding` separately asserts an exact source observation and a complete set of closed same-source events. The fixtures store `expected.truth`, `expected.event_due`, and `expected.clear_allowed` as separate reference fields. Their authorship was **not blinded or independently adjudicated**; the expected labels and script were committed together. They are constructed test expectations, not independently measured physical truths.

## Candidate presentation policies

| Policy token | Persistent audio | Discrete event audio | Explicit clear cue | Idealized visual fallback |
|---|---|---|---|---|
| `discrete_visual` | No | Yes if playback is playing and event due | Visual clear only | Status and due event |
| `persistent_discrete` | Yes when fresh source state known and playback playing | Yes if due | Neither explicit clear channel | Status and due event |
| `persistent_transition` | Yes | Yes if due | Audio and visual if allowed | Status and due event |
| `ducked_hybrid` | Yes, suspended while a due event is given priority | Yes if due | Audio and visual if allowed | Status and due event |

These are **logical offers**. No waveform, energy, timbre, hearing, response time, attention or masking is represented. `event_visual` and `status_visual` assume an idealized inspection channel; absence of actual screen perception is not modeled. There is no measured superiority for any row. A persistent-only option is retained as an **external future listener comparator**, not spuriously counted as an implemented policy: an unchanging background cue alone cannot symbolically communicate every separately timed event under this trace vocabulary.

## Structural truth table

| Source / playback / event condition | Correct symbolic treatment |
|---|---|
| Fresh online active source; silence/failed playback | Active source stays active; sound absence cannot clear it |
| Fresh online inactive source, closed target event, exact revisions within their domains, all same-source events closed and covered by explicit fictional recovery binding | A logically permitted clear *may* be offered by explicit-clear policies |
| Unknown/offline/stale/future source observation | Never declare a clear; status truth is unknown/stale |
| Acknowledged or claimed action completed, without source recovery | Still active if measured source says active |
| An open, due event while status audio would play | Event offer remains due; `ducked_hybrid` suppresses simultaneous status offer |
| Old/misbound clear, open same-source event, or missing/incomplete synthetic recovery binding | Reject the clear |
| Due event with failed/silenced playback | Event remains due while audio offer fails; visual offer is idealized |
| Expired event deadline | Not a timely event offer under this oracle; unresolved/late obligations are outside this small model |

## Coverage and noncoverage

The cases exercise active/inactive/unknown/stale/offline, mismatched source/event versions, foreign/missing event identities, other-source concurrent events, supersession, playback failure, an urgent event during status sound, expiration and acknowledgment/action-completion separation. `replay.run_cases()` checks encoded labels for every one of the four policies plus unconditional invariants against unsupported clear/audio publication. The additional hardening tests mutate a valid trace to ensure state, revision, playback and event state cannot be accidentally equated.

**Correction (2026-11-04):** The earlier cross-domain `source.version >= event.version` and cross-event numeric supersession guard were removed. Revisions are compared for exact equality **within** identified source and event records, not ordered across unrelated streams. A `recovery_binding` must contain `authority: synthetic_fixture_only`, `source_id`, `source_version`, `source_observed_at_ms`, and exactly one `{event_id,event_version}` for **every closed event of that same source**. Any open same-source event blocks a clear. Other-source events do not. Independent clock counterexample: `source.version=0 < event.version=1` now permits clear *only if* explicitly bound. Closed-but-unattested events fail closed irrespective of numeric version.

**Unresolved causal/trust boundary:** This is a fictional optimistic input created with the fixture, not authenticated authority or independent evidence. It cannot prove event closure happened before source observation, rule out forged attestations, guarantee atomic snapshots, or prevent a new event between observation and audio publication (TOCTOU). An R012 contract would need external authority, ordering, current-state verification and bounded latency before adoption. The current test oracle is not such a contract.

Other absences: no masking transfer function, independent stream segregation, discriminability, trained operator, actual deadline-sensitive response, all-clear perception, sound-power normalization, source-independent verification, or ecological field context. These belong to future R013/R014 and possibly #30/#41, not to this symbolic package. All code/prose remains exploratory; do not change the frozen protocol or live registry on the strength of these tests.
