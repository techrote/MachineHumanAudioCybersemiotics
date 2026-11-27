# Integration Regression Corpus 003 — authenticated session and rollback (Draft/HOLD)

Refs #607, #512, #513. Frozen source: 32eca4f1e1fe16d53422971c7663ae7fd73cca34; accepted base 495a98ca12bae467a507031f04931aa4254b1866. Upstream source report: https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/512#issuecomment-7204899903; upstream structural workflow 45906241473 passed. This candidate is not a scientific acceptance or production security audit.

The source directory contains only the 23 literal relative CommonJS dependency-closure files of session-v40.cjs and test-session-v40.cjs, archived by existing exact Git blob identity; no source rewrite. relay.cjs and bound-v2.cjs are the same Git blobs already in #736, retained at this separate archival path so this batch is independently runnable (Git deduplicates identical blobs). All other v1–v40 experiments, UI, source reports and generated upstream artifacts are excluded from this bounded batch, as are v41+ experiments. The source report remains the original evidence; regenerated outputs are new evidence, not a replacement of canonical records. Attribution: MHAC Integration laboratory, techrote repository, frozen #513. No new licensing grant; repository root license not established. All stimuli are deterministic synthetic fixtures. No recruitment, external publication, physical device, or human evidence.

Independent Python checker reconstructs frame parity and grammar, recomputes HMAC vectors, and recounts final results, authorized false assertions, time bounds and selected metrics from original traces. It does not independently decode PCM or replay the complete semantic reducer. Existing Node generator rescans its own exported PCM. Local Python 3.13.5 / Node 22.16.0 self-test passed six independent frame comparisons against exact relay blob and RFC 4231 known-answer HMAC check; full v40 runtime not locally executed (Git DNS failure). Targeted Linux CI will execute the actual archived modules, both seeds and role controls. Full audit results are not claimed until execution. Windows may require separate treatment of directory fsync, and no portability adaptation or weakened persistence semantics is introduced.

Reproduce from staged evidence directory (Python standard library and native Node, no npm):
```sh
python -B audit_session.py --self-test source/relay.cjs
SEED=71 node source/session-v40.cjs seed71
SEED=113 node source/session-v40.cjs seed113
node source/test-session-v40.cjs controls.json
python -B audit_session.py --seed71 seed71 --seed113 seed113 --controls controls.json
```
Use fresh output directories. Verify sources.json against exact Git blob bytes before running. Source bytes are staged directly from candidate Git objects by CI to avoid CRLF conversion. No ordinary browser/audition/Windows qualification at intake. No separate proof of authenticity, safe physical effects, power-loss durability, or semantic truth. The fixture uses public deterministic keys and nonces; valid same-session replay and an authorized false execution claim are intentionally retained. Restoring an old valid semantic snapshot is a trust-boundary failure even if its digest is internally correct. This is not evidence that MACs are broken. Promotion remains HOLD; no merge or approval.
