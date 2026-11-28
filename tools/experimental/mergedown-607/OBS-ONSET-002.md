# OBS-ONSET-002 — native independent computation audit

2026-11-25. Refs #607, #608, #442/#443. Frozen incremental source #443 at 92db2601aae859f0860eecb0acd03f44049688db, blob 198ce7fc4c350cd2ec1fc2fa3f85968dc8a7ac96. Separate from the earlier 5a1e3a85 freeze; no replacement or mutation of upstream. Parent consolidation integrity CI 45691276111 and source integrity CI 45699548702 succeeded. Base main 495a98ca12bae467a507031f04931aa4254b1866. One AI consolidation agent, separate Python/NumPy implementation, no human or scientific acceptance.

## Reproduce

From this directory: node onset-calibration.cjs NEW_OUTPUT_DIR (no dependencies beyond Node). For independent checks: python check_onset.py NEW_SCRATCH --browser /usr/bin/chromium (Python with NumPy and optional Playwright; omit browser argument for numeric checks). Output paths must not exist. Git retrieval failed with Could not resolve host: github.com; connector text was transferred and native git hash-object matched the upstream blob. Node 22.16.0, two byte-identical seven-file exports. All six manifest hashes and four original WAV PCM payloads checked with independent integer generator. Receipt SHA256 de8b1855af8dca6067ae83f898660ae5bf85a3efe5e29956251bc7934bac7d19. Separate oracle recreated 960 evaluation and 144 development waveforms, maximum template dot products and calibration, all evaluation decisions and 26 metric groups. Browser 144.0.7559.96 real DOM three rate selections, 24 rows matched, four controls/no autoplay, zero JS errors. file:// blocked by administrator; fallback in-memory HTML fixture, no media playback or ordinary file navigation claim.

## Finding requiring repair

In run(), devRows.push({rate,noise,seed,onset,...s,...e}) overwrites s.template (continuous projection score) with e.template (null estimate). The development trace cannot directly reconstruct the calibrated threshold from its per-row recorded values; 144/144 template fields null. This is a trace/export defect, not evidence of changed evaluation outcomes: independent reconstruction of all 144 development PCM inputs and integer correlation scores matches all three stored rate thresholds. Preserve original snapshot; upstream should use explicit templateScore and templateEstimate keys and add a regression checking max development score against calibration threshold. Do not edit upstream or rewrite receipt. Disposition REWORK for trace completeness, numeric reproduction PASS.

## Quantitative results

Threshold 624/768 detected, 118 within one sample, 0/192 false detections. Template 768/768 detected, 761 within one sample, 3/192 false detections. Six errors beyond two samples, all at gain .125 and peak noise 512, five at 8 kHz and one at 16 kHz. 8 kHz seed 211 deviates by -15 rather than exactly one carrier period; other five errors are ±one period. Export peak 805 PCM16 counts (2.46% FS); not acoustic SPL. Counts are finite shared-seed factorial cases, not iid human samples. Known phase/template/window; not streaming/unknown-phase qualification. Comparison not matched false-positive rate or computation. No owner authorization or new license. No native Windows or real DAW/human audition. The remaining workbench dependencies are still deferred; this standalone incremental measurement is not full workbench qualification.

## Source placement

Keep frozen copies only as temporary consolidation evidence until canonical path coordination with #443. No frozen protocol, shared record, manifest or other branch changed. Generated outputs reproduced rather than committed wholesale. New Python harness handwritten; pinned JS upstream, unchanged. Next repair trace export in Measurement lane, then qualify dependency-closed selective-transfer/legacy workbench; separately prepare the foundry collection.
