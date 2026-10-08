# Minimal checkpoint-publication resume

## Ready state

Repository: `techrote/MachineHumanAudioCybersemiotics`.
Bundle: `MHAC_R002_chunk1C1_publication.bundle`.
Bundle SHA-256: `4bf56d8cad4157f902b48484b606dfad635ff304acd1be7eaab8251b678f28f6`.
Candidate commit: `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252`.
Parent: `796151a33ec7a1acc026b239fe5c883312ebf40b`.
Base tree: `40afaeebb1801fd8adf1417a8da7523bff014d9f`.
Candidate tree: `e58c33056e95365922f20fab377abe06bbe8fc1a`.
Branch: `checkpoint/mhac-r002-1c1-ca673613bb89885ec7e7`.
Directory: `checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/`.
Payload ID: `ca673613bb89885ec7e7`.
49 saved files; all 27 original source files retain their mode and blob identity.

## Exact next action

Act only as checkpoint publisher. Verify the outer ZIP against the separately supplied SHA-256, extract it and run `python verify_publication_package.py --git`. Read PUBLICATION-PLAN.json and SAVE-README.md. Use a new isolated workspace; do not touch other workers or apply archived files to active paths.

Reconcile the source commit, current instructions/workflows and exact destination. The bundle requires the existing base; fetch the real source repository or use a verified isolated copy containing that commit. Import the bundle ref and verify candidate parent/root, additive paths and all saved bytes. A matching saved payload is verify-only success. If the destination differs, stop without overwriting it. Never rebase this archival commit onto a newer main merely because main advanced.

If the destination is absent and checkpoint-only authorization is in force, create the intended non-default branch at the candidate commit without force. With a normal Git remote, the final write is `git push origin 3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252:refs/heads/checkpoint/mhac-r002-1c1-ca673613bb89885ec7e7` after the guards above. Do not push main or use mirror/all pushes. Read back the remote ref, exact commit and saved blob identities. Do not monitor CI or retry an ambiguous write before read-back. A clear write restriction is a stop condition, not a prompt for a model/retry loop.

No PR/review/comment, issue closure, merge, active registry/queue, workflow edit/dispatch, deployment, shared hardware, permissions or credential changes. No source-access retry, research continuation, regenerated evidence or accepted protocol freeze.

## Completion signal

`GIT_CHECKPOINT_VERIFIED` requires a reachable remote branch and verified payload bytes. Current package status is only `LOCAL_CHECKPOINT_READY`. Research remains `PARTIAL`. No earlier packet dependency is missing; lawful comparator full text is still required for later research, not for this save.
