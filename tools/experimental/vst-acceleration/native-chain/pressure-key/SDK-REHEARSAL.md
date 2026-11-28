# Pressure / Key direct SDK rehearsal (ACCEL-051)

Refs #632, #738, #748. This is a separate candidate rehearsal, not independent
qualification, not a new plugin and not a replacement for the previous host evidence.

The three archive identities in preflight.py are the original Windows deliveries:
Orbit 0.5.0 (15268476929), Bank 0.4.0 (15268772488), Shuttle 0.2.0 (15248002499).
The Shuttle binary source is b5f509eb5c857dc6e411a7718bdc40dfa09bb0ad, not the
later native header dependency ref. Each archive, its PE, SDK root and seven
gitlinks, source receipt, factory CID and version are checked before extraction.

The direct SDK probe restores OL04/HM02/PS02 state, sends sample-offset note-on,
note-off and poly-pressure events to Orbit, passes its actual output to Bank's
main audio bus, delivers an independent stereo pulse train to Bank's activated
auxiliary bus, and routes Bank output into Shuttle. The rendered mix retains
the dry path. Stages execute serially offline, not concurrently or in a DAW.
Three rates, four modes and two block sizes yield 24 renders; six more compare
automatic key admission with a manual parameter-queue reference. Requires
pressure contrast, dry-path invariance, key contrast, full erasure, release,
state readback and partition/manual agreement. Four WAVs at 48 kHz.

Existing Trace Bell CMake SDK verification and Windows audition job are reused.
The SDK-specific probe has NOT been compiled locally (DNS-blocked SDK checkout);
the host execution gate is pending. Local package preflight and native
pressure-key CTest were executed, including an altered archive rejection.
No subjective listening or physical hardware claim.
