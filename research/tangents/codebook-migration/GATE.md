# MHAC-T012 applicability, duplicate-ownership and scope gate

**2026-11-04; exploratory go, conditional only; base main `423649d18c54cbf90bf7bf79d49ba69b29f03848`; issue #51.** A fictional control-console cluster with locally cached sound/legend versions, a queued recorded warning and rollback is an *illustrative* scenario where a stable audio token can have incompatible longitudinal meanings. The repository has not established that MHAC will ship persistent trained cues, replayed spoken instructions or mixed-version devices. Thus this is a **testable possibility, not an accepted product requirement**. Stop before R012/R013 admission if actual scope excludes all such conditions or a trustworthy external legend fully eliminates ambiguity.

| Existing item | Checked currently proposed artifact | Overlap | Distinct remaining falsifier |
|---|---|---|---|
| #33 / PR #35 | Recipient repair state machine binds message/version/source/event and invalidates pending replies on update | high in lifecycle | Does not map an acoustic cue ID/hash through coexisting generation and receiver **codebook versions**, semantic aliases or a rollback legend |
| #34 / PR #37 | Compositional message grammar and stale message/version rejection | medium-high | Within-version source × event bindings; not same cue acquiring a new referent, priority or action across codebook migrations |
| #41 / PR #42 | Channel distortion and acoustic cue identification | medium | Does not test semantic remap while acoustic bytes are unchanged; waveform survival cannot certify acquired meaning |
| #45 / PR #46 | Per-field acoustic mapping independence, polarity, collisions | medium | Its collision test is simultaneous meaning within one mapping, not cross-version old/new dictionary incompatibility |
| #47 / PR #48 | Queue freshness versus durable action deadline | medium | Reuse its expiry distinction; does not resolve cue-dictionary mismatch after deferral |
| #49 / PR #50 | Mode-conditional action permissions with state attestation | medium | A valid action precondition can still be attached to the wrong learned sound identity |

Current-main accepted R012 and R013 specifications **do not exist**; their issue descriptions reserve downstream ownership. No current open PR listed above claims T012's exact longitudinal dictionary semantics. Read-only inspection of PR #35's STATE-MACHINE and protocol.py; PR #37's ABSTRACT-GRAMMAR; PR #46's COMPARATORS; PR #50's MODE-CONTRACT. These are non-merged exploratory branches, **not accepted MHAC design authority**.

**Go/no-go decision: LIMITED GO** for independently-labelled symbolic counterexamples only. A migrated acoustic cue can be syntactically valid and an action valid for the event yet be interpreted under an incompatible dictionary. The converse is equally important: extra version machinery is unjustified if identical mapping across all permitted versions or a sufficient external authority exists. The fixture includes those null controls.

**Owned paths:** this directory and `tests/test_t012_codebook.py`. Do not mutate schema, frozen protocol, registry, selected source records, shared aggregate, accepted main, other branches or issues. Partial implementation must use `Refs #51` and leave issue open. All future R008/R012/R013/R014/R017 changes require separate review and their own gates.