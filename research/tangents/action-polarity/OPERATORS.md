# Fictional authority, speech acts and non-equivalence

`truth = (source, event, version, issued_at, expires_at, state, actions)` is a *supplied fixture*, not a real device. `state ∈ {active,inactive,unknown}`; independently each action is `required, prohibited, permitted` or `unknown`. Unknown hazard state cannot be silently inferred as inactivity or clearance; acknowledgment is neither correct action nor resolution.

| Message | Provisional asserted semantics | Required token sequence (symbolic; **not audio**) |
|---|---|---|
| `require(A)` | A is obligatory; authoritative action A must be required | `DO A` |
| `prohibit(A)` | A is forbidden; authoritative action A must be prohibited | `DO NOT A` |
| `correction(B,A)` | Both B required **and** A prohibited; distinct roles | `DO B NOT A` |
| `status(active/inactive/unknown)` | Factual state, not action authorization | `HAZARD ACTIVE/CLEARED/UNKNOWN` |
| `status(not_cleared)` | Known active, **not** unknown | `HAZARD NOT CLEARED` |
| `status(clearance_unconfirmed)` | Cannot be proved: clearance-record evidence is not modeled | `CLEARANCE NOT CONFIRMED` → unresolved |
| `all_clear` | Explicit known inactive state, never silence | `ALL CLEAR` |
| `ack` | Mere receipt, not condition resolution | `ACKNOWLEDGED` → reject as hazard assertion |

Tokens have a type-level scope `action, factual, clearance` or `acknowledgement`. Scope swaps, missing negators or moved tokens reject a *formal string*, not an acoustic signal. A direct command must be truth-bound to source, event and current event version; expired or pre-authority commands are rejected. Unknown action identity/authorization yields **unresolved**, not automatic permission.

## Why NOT A does not logically imply DO B

A prohibition `¬permitted(A)` does not entail `obligatory(B)`. With permitted choices B and C, a forbidden A can coexist with **no requirement** to perform either. Even if A and B were the only listed actions, exclusivity/exhaustivity and a duty-to-act premise would still need independent authoritative proof. The fixture `unsupported-affirmative-paraphrase` holds A prohibited while B is merely permitted: its putative positive requirement is therefore rejected.

Factual negation (“hazard not cleared”) does not mean “do not act”. Unknown hazard state cannot support asserting active hazard, and `clearance_unconfirmed` requires a separate clearance-record truth field this intentionally small model lacks, so it always remains unresolved. Silence and acknowledgment cannot substitute for a new, versioned all-clear proposition.

## Invariants and limitations

1. Current source **and** event identity, exact version, issue and expiry bounds; integer clocks, non-booleans; `issued ≤ now < expiry`. Old or future versions never bind to current truth.
2. A present complete token list must exactly match a legal typed operator template. Dropping NOT produces structural rejection. **It does not estimate the chance a listener misses NOT.**
3. `accept` = invented text consistent with invented current authority; `reject` = malformed or known contradiction; `unresolved` = cannot warrant claim from supplied truth. No accepted status implies comprehension.
4. Single-snapshot checking cannot prove authentication, parallel concurrency, actual network ordering or acoustic intelligibility. The project needs separate controls for these.
5. All token mappings, legal statuses and model choices are provisional *conventions*, not primary-source findings or a Brier-derived design claim.
