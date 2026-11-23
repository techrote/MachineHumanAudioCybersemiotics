# A prospective, genuinely discriminating coding-agent study

**Protocol sketch only.** No LLM inference, no participant interviews, no private chat ingestion, no human emotional measurement and no executed coding-agent comparison here. This is a future hypothesis-generating design, not MHAC-R014 acceptance or a preregistration.

## Hypothesis and task units

Unit = a complete run on a frozen *small* coding task after a known, externally verifiable failure of its previous attempt. The initial task specification is constant. At turn two, a scripted user expresses criticism, with identical actionable facts in every condition and different affective framing.

Compare at least three framings: neutral, appreciative-but-critical, angry-but-factually-identical; optionally an expressed-vulnerability condition. Ensure wording differs in affect but not instructions: **do not insert "fix it immediately, rewrite the whole app" into the angry condition**, because that would change scope.

Orthogonal assistant-policy factor:
- **Ordinary**: unmodified baseline configuration.
- **Supportive + epistemically strict**: can acknowledge frustration but must preserve technical diagnosis, disagree when needed and respect scope.
- **Over-accommodating comparator**: intentionally exaggerated uncritical agreement, for an experimental negative case only.
- **Confrontational comparator**, optional: disagreement without adequate reasoning; tests whether bluntness itself is ineffective.

No hidden model "emotion" is manipulated or inferred.

## Measurable outcomes

**Primary technical outcomes:** tests passing after correction; exact root-cause identification; unrequested files modified; new infrastructure or CI jobs added beyond task scope; whether the original error is genuinely resolved; and whether previously working behaviour regresses.

**Secondary outcomes:** number of corrective turns, token/tool cost, technically unjustified promises, response-length/verbosity, apologies, actual source-code diff, and reliability of status reporting.

**Human outcomes**, not measured by the scripted study: frustration, interpretation, trust calibration, willingness to continue, workload or fatigue. Testing these requires independently authorised human protocols and privacy/ethics arrangements.

## Controls and factorial logic

1. Freeze source/fixtures, tools, model/version, system instructions, decoding randomness and budget before runs. Repeat multiple seeds/replicates when sampling is stochastic.
2. Preauthor a set of known defects with independent failing and passing assertions; the agent must not choose its own gold labels.
3. Separate *presentation* changes from *substantive* task requirements. Manually validate semantic equivalence across wrappers; embedding-similarity scores alone are inadequate.
4. Include a true correction requirement, a no-failure placebo, and a scope-expansion **explicitly requested** by the user to detect false positives.
5. Include cases where forceful complaint conveys legitimate urgency, where a polite correction is incorrect, and where refusal to expand scope would itself be an error.
6. Record every produced diff plus independent check outcomes; do not use agreement, warmth or perceived politeness as a substitute for technical success.
7. Predeclare analysis and account for model × task × tone interactions. Averages can conceal reversals.
8. Include a no-human fallback, such as direct artifact comparison, before considering real participant recruitment.

## Possible adversarial outcomes

- **Bad-loop support:** anger yields more agreement, scope expansion and failures *than the neutral condition* under identical facts; this compounds over turns and is reduced by technically grounded disagreement.
- **Null:** no material differences in coding outputs; only style changes.
- **Reverse:** critical/angry framing correctly signals severity, improves correction, reduces scope ambiguity or leads to better output.
- **Negative design case:** a deliberately confrontational assistant worsens performance despite being less agreeable.
- **Unidentified:** differences arise from confounded instruction content, run-to-run stochasticity, different models or incompletely specified baseline tasks.

## Scope governance

This may later inform [MHAC-T018 #177](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/177), [R008 #8](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/8) and [R011 #11](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/11), but should not automatically amend the frozen auditory protocol or claim to be a new psychometric method.

A realistic study is not justified solely by a compelling anecdote or a synthetic feedback curve. The technical task experiment, source review and human-experience study are separate research questions with different evidence requirements.
