# MHAC-X005 — formal note: no-message prefixes and assumption debt

This note proves only elementary properties of the synthetic model in silence_oracle.py.

## 1. Receiver-local observation

A world contains an optional message emission time and an optional delivery time. The receiver's finite observation through time T is the list of messages **delivered** by T.

No access to sender state, hidden channel queues, future delivery or causal history is assumed.

## 2. Finite-prefix silence theorem

Let T > 0. Consider two worlds:

A. No message is emitted.

B. A message m is emitted at time T/2 and delivered at time 2T.

At receiver horizon T, both local traces are empty.

Therefore any deterministic classifier D that maps only the receiver's trace through T to one of the mutually exclusive claims

- NO_MESSAGE_WAS_EMITTED
- MESSAGE_WAS_EMITTED_BUT_NOT_YET_DELIVERED

must return the same answer in A and B and is therefore wrong in at least one world.

This is an indistinguishability result for the toy observation function, not a theorem about human cognition.

### Proof

The receiver trace in A is empty because there is no delivery.

The receiver trace in B is empty because the delivery time 2T is later than T.

Equal inputs to a deterministic classifier produce equal outputs. The two required ground-truth labels differ. Hence no such classifier can be correct on both.

QED.

## 3. What changes under a delay bound

Suppose instead that the channel contract states:

1. every relevant event up to time e is emitted immediately;
2. delivery is reliable;
3. every emitted message is delivered within known maximum delay Delta.

Then if the receiver observes no message by e + Delta, it may conclude that **no relevant event occurred on or before e**, under those assumptions.

This conclusion does not cover:
- events after e;
- violations of the delivery bound;
- sender failure before emission;
- receiver disconnection;
- messages excluded by the definition of “relevant.”

A timeout therefore spends **assumption debt**. It is not information created from nothing.

## 4. Permanent ambiguity under loss

If a model permits a message to be emitted and then lost forever, and exposes no erasure marker or independent side evidence, then the no-emission world and the lost-message world can remain receiver-indistinguishable forever.

This is stronger than temporary delay ambiguity but depends on allowing permanent loss.

## 5. Why an erasure marker changes the problem

The binary erasure channel deliberately produces a third observable output such as E.

Thus:

- output 0: a valid zero was received;
- output 1: a valid one was received;
- output E: the channel reports an erasure.

The receiver still does not know whether the erased input was 0 or 1, but it **does know an erasure occurred**. That knowledge exists because the model gives the receiver an explicit symbol.

Literal absence of output is not equivalent unless a surrounding protocol turns absence into an observable erasure event.

## 6. Leases and conservative state decay

X005 defines a toy status rule:

- explicit RESOLVED remains RESOLVED;
- ACTIVE is trusted only through a declared valid-until time;
- after the lease expires without a fresh status or resolution, interpretation becomes UNKNOWN;
- no status observed means UNKNOWN.

This is deliberately asymmetric:

    ACTIVE --silence past lease--> UNKNOWN
    RESOLVED --silence--> RESOLVED

There is no rule

    ACTIVE --silence--> RESOLVED.

That asymmetry is the proposed engineering exaptation.

## 7. Heartbeat suspicion is not failure truth

A simple heartbeat timeout can produce SUSPECT after sufficient silence. If a late heartbeat subsequently arrives, the earlier suspicion can have been false.

Accrual detectors make the same conceptual separation more explicit by returning a suspicion level rather than asserting metaphysical certainty.

X005 therefore uses the vocabulary:

- observed heartbeat;
- elapsed silence;
- suspicion under detector policy;
- verified/externally established failure.

Those are distinct fields.

## 8. Counterexamples to overbroad conclusions

1. **Intentional silence:** a trained human interlocutor can deliberately communicate through silence; the finite-prefix theorem does not deny this because the conversational contract is richer than the toy trace.
2. **Synchronous systems:** with reliable bounded delivery, timeouts can carry valid negative information about a past interval.
3. **Explicit all-clear:** a message saying RESOLVED removes the ambiguity by adding an observation.
4. **Explicit erasure:** E removes “did a symbol disappear?” ambiguity while leaving the erased value unknown.
5. **Side channel:** a second independent observation can distinguish worlds that the silent audio channel cannot.
6. **Statistical inference:** a receiver can estimate probabilities from prior distributions and timing histories; inability to know with certainty does not imply inability to make useful predictions.

## 9. Relationship to FLP

FLP's actual result concerns deterministic consensus in an asynchronous crash-failure model. Its opening discussion famously highlights that, without timing bounds/failure detection, a process cannot simply tell a crashed peer from a very slow one.

X005 borrows only the **modeling caution**: a missing message under unbounded delay does not uniquely identify hidden state.

The tiny theorem above is independently proved from our own two-world construction. Calling it “FLP for silence” would be rhetorically cute and technically misleading.
