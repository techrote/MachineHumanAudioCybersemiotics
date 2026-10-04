# Human gates and minimal handoffs

[Runbook](AGENT_RUNBOOK.md) · [Integrity](RESEARCH_INTEGRITY.md) · [Experiments](EXPERIMENTS.md)

## Principle

Agents prepare evidence, analysis, artifacts and exact next steps. Humans are asked only for genuinely human-required access, decisions, permissions or actions. Do not ask the owner to reconstruct project context, manage routine tasks or approve every normal commit.

## Gate classes

| Gate | Required evidence / completion signal |
|---|---|
| Critical source access | Exact citation/edition and failed lawful routes; owner provides lawful access or authorizes a clearly bounded scope change. |
| Required GitHub approval/permissions | Exact PR/check and error; authorized approval or permission resolution, without bypassing protections. |
| Authorship, license or external submission | Proposed decision and consequences; explicit owner/contributor authorization. Repository creation is not a license grant or submission request. |
| External review (#19) | Approved outreach scope plus actual reviewer feedback and permission-safe provenance. A prepared invitation is not completed review. |
| Real participants (#20) | Explicit authorization, appropriate ethics/consent/privacy/listening arrangements, actual participants/data and verified readiness. Synthetic rehearsal does not satisfy this. |

## Handoff format

Use a short Markdown note with a descriptive heading, why the action is necessary, exact steps, links to prepared materials, expected completion signal, stop condition and what remains unblocked. Include what was already attempted. Avoid vague requests to review everything or procure unspecified resources. Do not expose private correspondence or personal data in this public repository.

## Queue and repository isolation

Stage the handoff within this repo's issue/checkpoint. The owner's canonical human-action queue, where used, is remote authority; do not rely on a persistent stale local clone. Writing another repo is outside this task's mutable scope. A separately authorized queue update requires a durable checkpoint, fresh remote instructions and a deliberate switch so exactly one repo is mutable. Lack of queue access must not prevent a useful local handoff.

## What remains allowed while a gate is blocked

Continue independent authorized source work, protocol preparation, coding/tests and analysis supported by available evidence. Land a truthful partial PR using `Refs #N`, leave unmet acceptance open, and state which downstream claims are blocked. Do not bypass paywalls, contact reviewers, purchase sources, register protocols, recruit participants or send external submissions as a workaround.

## No false completion

No real gate is satisfied by an agent changing a status field. Keep actual evidence and the actor/date/scope of authorization. Internal publication of a research draft is distinct from external journal submission. A GitHub merge is not human acceptance of a theory or the safety of an audio experiment.
