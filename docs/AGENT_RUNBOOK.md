# End-to-end execution and merge runbook

[Programme](PROGRAMME.md) · [Integrity](RESEARCH_INTEGRITY.md) · [Validation](VALIDATION.md)

## Reconcile before editing

Fetch the current default branch, exact issue body and all comments, linked PRs, active branches and CI. Verify upstream acceptance artifacts, not only issue closure. Read required authorities and freeze/amendment records. Check the worktree for existing user or worker changes; preserve them. Resume an active suitable branch rather than duplicate its work. Record the base SHA and issue ID in the task checkpoint.

## Scope and plan

Confirm the issue's owned paths, outputs, exclusions and dependencies. Use branch names such as `mhac-r007/brier-reconstruction`. If an essential decision cannot be resolved from evidence or current instructions, record the ambiguity and a minimal human gate. Ordinary implementation decisions, source retrieval attempts, testing and PR work do not need repeated approval. A running task does not imply permission to begin every later issue; multi-issue continuation needs the user's scope authorization.

## Execute with records

Work in bounded source or feature batches. Preserve raw discovery provenance and separate fixtures from real evidence. Run the relevant validation command after each coherent change. Add negative tests when adding a structural rule. For new statistics or library behavior, verify primary documentation and record versions. Do not weaken a checker simply to permit invalid research status.

Use additional workers for disjoint batches or read-only critique; record their actual role, tools/models and verification limits. Do not represent agent agreement as independent human review. Keep shared manifest/aggregate edits serialized. Only this repository is mutable.

## Review before PR

Review the complete diff for scope, source fidelity, unsupported claims, citation locators, bias, rights/privacy, dependency changes and misleading completion labels. Check positive and negative cases. Verify any render produced for human reading. Rebase or merge current main safely and rerun tests when the base changes. No force update to main and no destruction of another worker's work.

## PR contract

Open a PR to the actual default branch with scope, issue reference, artifact inventory, source/analysis provenance, tests and exact outcomes, limitations, human gates, AI assistance and a completed acceptance checklist. Use `Closes #N` only when the entire issue is met; otherwise use `Refs #N` and leave it open. Include protocol amendments and their downstream impact. Resolve review findings with evidence rather than mechanically dismissing them.

## Check and merge

Run local tests and obtain successful automated checks on the exact final PR head. Inspect both check-runs/Actions and legacy commit statuses where applicable: an empty status list is not green CI. All required checks and approvals must be satisfied, the PR must be mergeable, and material review findings must be resolved. An ordinary merge method must not bypass branch protections. Prefer squash merge and pass the expected head SHA when the tool supports it; if the head moved, re-read and revalidate.

Auto-merge is optional and repository-dependent. If unavailable, wait for checks within the active task and merge normally when allowed. If CI or required approval is unavailable, leave the PR unmerged with exact blocker evidence; do not change protections or falsely mark checks passed. Do not poll tightly or promise background completion. The bootstrap's single initial README commit is the documented empty-repository exception; substantive bootstrap docs are reviewed in a PR.

## Post-merge verification

Fetch main and verify the merge commit, intended files and issue state. Check the push-triggered CI run for that merged main SHA; PR-only workflow endpoints may omit it. Re-run local validation on the landed tree where possible. If post-merge checks fail, create a scoped correction/PR or reopen the affected issue, not a false completed status. Record actual PR URL, head and merge SHA, checks, artifact paths, acceptance/remaining limitations and next dependency-ready issue. Distinguish implementation landed, post-merge verification pending and research accepted.

## Checkpoint and blocker format

```text
Issue and scope:
Base/head SHA and branch/PR:
Completed artifacts and source batches:
Tests/checks actually run:
Remaining acceptance items:
Blocker, evidence and attempted remedies:
Exact next action and completion signal:
Files that must be preserved:
Human action genuinely required, or none:
```

A blocked scientific claim may be removed or narrowed with a justified amendment; unavailable foundational evidence must not be replaced by inference. Partial useful artifacts can land while the issue remains open. Continue only independent work authorized by the user. Do not create an unattended schedule, send messages, purchase access or mutate a second repo as an implicit workaround.
