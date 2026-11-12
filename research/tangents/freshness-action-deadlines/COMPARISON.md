# Synthetic comparison and conflicting outcomes

**30 fictional cases × five policy abstractions, 26 distinct truth-labelled required event IDs.** Reproduce values with `python research/tangents/freshness-action-deadlines/oracle.py --check`; all count values below concern the **model**, not hearing or safety.

| Policy | Timely+authorized / required | Missed required | Modeled dispatches | Stale statuses | Expired event dispatches | Wrong-actor dispatches | Discarded |
|---|---:|---:|---:|---:|---:|---:|---:|
| Immediate FIFO | 23 / 26 | 3 | 45 | 0 | 0 | 0 | 0 |
| Fixed deferral | 19 / 26 | 7 | 45 | 1 | 3 | 1 | 0 |
| Task-boundary with override | 22 / 26 | 4 | 45 | 1 | 0 | 1 | 0 |
| Protected status coalescing | 23 / 26 | 3 | 44 | 1 | 0 | 0 | 1 |
| Naive latest-wins by source | 12 / 26 | 14 | 32 | 1 | 3 | 1 | 13 |

`immediate_fifo` and protected coalescing each have three *deliberately unprovable* fictional cases (unknown deadline, actor or clock), not three observed human failures. All policies also encounter duplicate-delivery *risk* or obsolete dispatch in some invented traces. A lower notification count is **not** demonstrated reduced interruption harm; the naive comparator loses more obligations even while sending fewer notifications.

**Particular falsifiers:** T04 and T16 disprove unguarded deferral before short deadlines; T11 shows post-handover instructions sent to a former actor; T24 and T14 reject the assumption that newest status or newest same-source message subsumes unresolved events; T08/T09 show an explicitly resolved/revoked event cannot be represented by a pending action; T10 contrasts nonresolving acknowledgment; T18–T20 refuse to call unknown metadata successful. T02/T03/T27 preserve status-group and source boundaries. T22 is a simplifying counterexample: immediate-only can already be sufficient.

**Caveats:** The convenient 3-tick delay, every task boundary and every event deadline are arbitrary hypothetical fixtures. Fictional outcomes are *specification counterexamples*, not evidence for the real prevalence of any failure or superiority of any intervention. Our strict `timely_authorized` proxy labels a packet with unknown preconditions as not guaranteed; it is not an assertion of failure to receive. The task-boundary comparator uses a perfectly known future boundary and deadline, so its apparent control is optimistic. The source studies vary in task, modality, outcomes and rights/access; no pooled effect or auditory efficacy claim is attempted.
