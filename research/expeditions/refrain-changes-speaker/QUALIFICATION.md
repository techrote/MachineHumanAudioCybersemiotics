# Qualification receipt — 2026-11-24

Agent: ChatGPT, single agent. No independent human review. All files additive, based on main 495a98ca12bae467a507031f04931aa4254b1866.

Fetched exact branch source, lab.js blob fcf69c2d0860585aa579289d40c4af0e8c3d8914 and instrument.html blob c7fa1ba892973241cc257061f3d1c900376912c5, executed lab in the JavaScript tool environment via Function constructor; 25,777 checks, 8,191 masks, 1,093 paths. Separately generated masks recursively through length ten, sorted direct boundary lists lexicographically and compared rank/unrank: 4,094 checks. Same agent, distinct algorithm, not independent reviewer.

Executed fetched instrument inline script against a minimal simulated DOM and Web Audio schedule recorder: 16 checks covering initial state, nested scope, early/late equal raw oscillator schedule (8 events), audit schedule (10 events, correct two low accompaniment offsets), all/none, toggling, late footer and stop. Actual browser layout, acoustic output, audio-device timing and human comprehension not evaluated. This test is a handler/schedule check, not PCM equality or browser certification.

Total observed dedicated assertions: 29,887 (25,777 + 4,094 + 16). The retained lab.js self-test is rerunnable with Node. The additional cross-check and handler tests were executed via the tool environment, not retained as a separate test file. Full repository tests and CI are not claimed passed by this receipt; inspect the PR workflow. No human experiment, real machinery, verified authority or production security evaluation.
