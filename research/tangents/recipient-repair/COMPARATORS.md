# T003 — four competing mechanisms and scope guard

**Not a recommendation or source-derived human performance ranking.** The question is whether structured recipient repair adds useful correct interpretation/action after accounting for delays, compared with simpler interface strategies.

| Arm | Available behavior | Proposed benefit | Costs / reasons to reject |
|---|---|---|---|
| **A: One-way plus acknowledgement** | Fixed alert, optional delivery/ack report; no reply | Minimal interruption and state | Acknowledgement cannot establish source/event interpretation or action. Might dominate when deadline short. |
| **B: Bounded repeat-only** | A + replay of the same identified version | Possible recovery from hearing/attention lapse; lower training cost | May repeat stale/ambiguous information; replays may interfere with tasks. |
| **C: Recipient-initiated structured repair** | Named clarification of source, event, action or why, strict request/response correlation and cannot_answer | May target a specific ambiguity and expose missing knowledge | More states/turns, motor/ASR burden, deadline loss, fluent but ungrounded answer. Only a hypothesis from adjacent studies S26/S27. |
| **D: Accessible non-audio status fallback** | Text/button/current-state confirmation independent of always-on ASR | Potential access route for noise/hearing variation and persistent inspection | Eyes-busy or motor constraints may make visual/text worse; no global modality advantage. |

Primary **decision** is correct consequential action by the task-defined deadline, **including omissions**, not how many repairs were answered. Keep separate detection, source identification, event interpretation, action correctness, action lateness, evidence of resolution, repair count and task disruption. A richer interface only matters if it improves an important endpoint relative to a fair B/D baseline.

**Fairness requirements:** equal semantic payload and version, comparable lexical content/clarification options where possible, matched training and information access, controlled delivery latency, controlled acoustics/output level, workload, language/hearing/visual/motor accessibility, counterbalanced source/event mappings and order. Never contrast a polished C against deliberately ambiguous A.

**Opposing evidence:** the SAGE abstracts of Helleberg/Wickens (2001) and Wickens/Gosney (2003) report task-dependent disadvantages of auditory/redundant interfaces and sensitivity to training; neither examines C directly. The IBM abstracts of Moore et al. (2024) and Do et al. (2024) motivate investigating repair/grounding but do not validate warning deadlines. See [source provenance](SOURCES.md).

**Negative/null value:** If B or D matches C's correct-action/interpretation performance with lower cost, reject the complex repair default for that context. If C increases delayed or wrong actions, restrict or abandon it. A successful Python trace is not evidence for any comparative ordering.
