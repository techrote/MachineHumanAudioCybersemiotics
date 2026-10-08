# MachineHumanAudioCybersemiotics — R001 prepass packet

Start with [HANDOFF](HANDOFF.md). The full architecture and dictionary are in [R001_PREPASS](proposal/docs/R001_PREPASS.md); [worked example](assessment/WORKED_EXAMPLE.md); [file-by-file implementation order](assessment/IMPLEMENTATION_ORDER.md); [actual test summary](results/SUMMARY.json).

The proposal contains executable scripts, all frozen positive/negative fixtures, authored synthetic source bytes, and additive tests. `proposed.patch` is an optional additive proposal, locally apply-checked; do not install it without reconciling live main. It does not complete issue #1.

Verify integrity with `python verify_packet.py`. Then run `python run_prepass.py --output rerun-results` to recreate the offline overlay tests and CLI reports. Run the verifier before creating rerun output inside this directory, or use an output directory outside it. No network or secrets are required. The manifest covers all payload files except itself. The external ZIP SHA-256 covers the entire archive, including the manifest. Checksums prove file identity only.

`baseline/` holds only the two original executable files whose Git blob IDs were checked. It is not a checkout and cannot run full repository validation on its own. Repository/authority retrieval provenance, limitations and intended paths are in `assessment/` and HANDOFF.md. This is synthetic infrastructure rehearsal, not real research evidence or independent review.
