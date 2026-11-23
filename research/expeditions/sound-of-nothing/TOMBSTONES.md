# MHAC-X005 — tombstones: when “nothing” is not enough to remember a deletion

Distributed storage provides an unusually concrete version of X005's negative-space problem.

## The deletion paradox

Suppose three replicas contain the same record A.

One replica goes offline.

A delete reaches the other two.

If “delete” is represented only by physically removing A, the cluster can become:

    replica 1: absent
    replica 2: absent
    replica 3: A, version 1

When the stale replica rejoins, there is no durable fact on replicas 1 and 2 saying that A was intentionally deleted. A naive repair policy can treat the surviving copy as the only positive record and restore it elsewhere.

Absence forgot the deletion.

## Tombstone as explicit negative state

Apache Cassandra's documentation describes a different strategy: a deletion is written as a time-stamped **tombstone**, which propagates through the normal write/repair machinery and suppresses older live values.

In the same cartoon:

    replica 1: TOMBSTONE(A), version 2
    replica 2: TOMBSTONE(A), version 2
    replica 3: A, version 1

Version-aware reconciliation preserves the newer deletion marker and carries it to the stale replica.

The tombstone is eventually eligible for garbage collection only after a grace period intended to give lagging replicas time to learn the deletion.

The exact Cassandra implementation is more complex than the toy below. The structural lesson is enough:

> A replicated system may need to preserve an explicit trace of *what is no longer there* so that absence cannot be mistaken for ignorance.

## X005 synthetic counterexample

silence_oracle.py contains a deliberately tiny three-replica last-version-wins demonstration.

Initial state:

    [LIVE@1, LIVE@1, LIVE@1]

Replica 3 becomes unavailable during deletion.

### Delete by absence

Reachable replicas physically remove their values:

    [None, None, LIVE@1]

Toy repair chooses the highest-version explicit value that exists:

    [LIVE@1, LIVE@1, LIVE@1]

The record has been resurrected.

### Delete by tombstone

Reachable replicas write an explicit newer deletion:

    [TOMBSTONE@2, TOMBSTONE@2, LIVE@1]

Toy repair chooses the higher version:

    [TOMBSTONE@2, TOMBSTONE@2, TOMBSTONE@2]

The deletion survives.

This demonstration is not Cassandra's storage engine, anti-entropy protocol or compaction algorithm. It is a finite counterexample showing why “missing value” and “known deleted value” are different information states.

## Auditory exaptation

The analogy to auditory state is unusually tight.

Imagine a persistent alarm/state tone representing an unresolved event.

If “resolved” is encoded only by removing the tone, a receiver with stale state or a failed channel can be left with no durable evidence that resolution actually occurred.

An explicit resolution event functions somewhat like a tombstone:

- it identifies what is being closed;
- it can be versioned/timestamped;
- it can propagate independently of the old positive state;
- it can suppress stale older interpretations;
- it can be retained long enough for lagging receivers to reconcile.

The comparison is structural, not literal. Human listeners are not Cassandra replicas and an audible all-clear is not a database mutation.

## Agentic exaptation

The same pattern appears in long-running agent work.

Bad protocol:

    RUNNING disappears -> assume COMPLETE

Tombstone-like protocol:

    RUNNING@v1
    COMPLETE@v2 with artifact/checkpoint identity

A late cache of RUNNING@v1 should not resurrect “still working,” and silence after RUNNING should not fabricate COMPLETE.

Similarly, explicit CANCELLED or SUPERSEDED records can outlive the work they negate.

## Cost of explicit negative state

Tombstones also provide a warning against naive enthusiasm for explicit markers.

They cost storage, read/compaction work and operational discipline. Cassandra eventually purges them, but doing so too early relative to unavailable replicas can allow deleted data to reappear.

The communication analogue is that keeping every all-clear, cancellation and stale-status marker forever is not free:

- listeners can be overloaded;
- state ledgers grow;
- rendering becomes noisy;
- old resolution messages themselves can become stale.

The real design question is therefore not “always use tombstones.”

It is:

> Which negative facts must persist long enough to defeat stale positive state, and what evidence makes them safe to forget?

## Relation to the negative-space type discipline

The tombstone analogy sharpens three X005 types:

- NO_DELIVERY: nothing arrived; no deletion fact is implied.
- RESOLVED: a semantic closure fact exists.
- STALE: old positive evidence exists but has expired.

A good protocol should not erase RESOLVED into NO_DELIVERY until it is certain that no receiver can legitimately revive the stale positive state.

That is the precise reusable result.
