# Measurement Run 073 — Bounded escalation
Refs #442/#443. Synthetic exploratory apparatus; Draft/HOLD. No human/physical evidence or independent acceptance.

Parent 56383207d8d5d8d4b2fb6db1802688ae826679e0; main 495a98ca12bae467a507031f04931aa4254b1866. Adversarial #449 1ffd17fe7d1efa7511fea606cf54256f02cd53ce unchanged. Both predecessor CI passed (46073635641, 46078980765). Nine runtime dependency blobs compared to parent and match native inputs. Immediate comparator SHA256 pins in source, inherited dependencies enforce their own pins. Initial grammatical body newly rendered from Dual3 model, not replayed. Full 108-meaning fixed-depth domain, seed 4427301; 8 conditions, same initial/header PCM per policy and same stage noise, 16kHz, 1600 counts nominal peak, 240ms initial body plus 120ms CRC8-protected rank header; request/reply 120ms each, 10ms turnaround each, 20ms per field. Initial header provides trusted intended rank, which is itself a full finite-domain representation, so this is a redundant-body recovery experiment, not an argument that body improves upon direct rank. Known boundaries and frame ID. No authentication/session negotiation, ideal request equality guard at sender, no retransmission on invalid controls or modeled additional timeout; durations not wall time. Persistent fault repeats corrupted fields, transient fault removed on reply. No matched total energy across conditions.

Run from this directory with Python 3.13.5, NumPy 2.3.5: OPENBLAS_NUM_THREADS=1 python escalation-lab.py NEW_OUT. Generates receipt, candidate traces, SHA256 manifest, offline inspector and eight original WAVs (quarter-scale, opt-in playback). 864 initial body/header pairs; 3456 decisions, 32 aggregates, replay cost/status verification, two runs byte-identical. Inherited symbolic tests passed (3). Source SHA256 af56d9128c861211e52255078788d34834253687cf7b255535cbfed06f890cc4.

Correct /108 and total scheduled milliseconds (full1, selective1, escalate2, full2):
- white: 108/80480, 108/70320, 108/70320, 108/80480.
- colored: 108/50080, 108/46720, 108/46720, 108/50080.
- offgrid: 108/77280, 107/66920, 107/66920, 108/77280.
- transient: 108/82080, 1/72580, 108/115380, 108/82080.
- persistent: all zero; 82080, 72580, 115780, 125280.
- weak_control: all 1; 41230, 41130, 41130, 41230.
- clean: all 108; 38880 each. absent: all zero; 38880 each. Zero incorrect admissions in this finite factorial (not a bound on operational error).

Escalation repairs transient retained wrong fields at material cost: 107 second requests, 40.57% longer than full1 for identical recovery. Under control errors a bounded second body attempt does not help because the policies abort on invalid control. Next: explicitly budget control retry/timeout, compare direct rank with equal airtime/energy and independent held-out conditions; adversarial lane resume longer-body hypothesis suspension as promised. No shared manifest/frozen protocol changes.
