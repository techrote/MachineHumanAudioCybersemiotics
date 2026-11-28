# FX-011L — exact undriven escape planner (Refs #748)

Direct finite-graph realization of the lexicographic objective in draft #265 at 56c107f8f4147316a588484c47be28bc8f840fbb, specialized to the actual q=9 quarter-turn bounded single-channel lattice in resonator.hpp. Not human evidence.

Offline synchronous Bellman relaxation uses the 1089 states and costs N=1, T=1091 (weight=1090). Positive costs imply a simple optimal route of at most 1088 edges, so the scalar ordering implements minimum truncations then minimum elapsed ticks. Lookup is constant-time, with no allocation. Construct outside the audio callback. Do not use the planner for nonzero drive, pending input, arbitrary coefficients or a stereo pair sharing a single intervention command; those require separate integration and verification. No VST3 parameter, state, audio path or binary changes in this increment.

Independent forward budget-augmented BFS checks both the minimum intervention budget and shortest feasible path at that budget for every state, then replays the chosen policy and compares pure truncation. GCC 14.2 Release CTest 12/12 PASS; standalone GCC and Clang 17 ASan/UBSan planner PASS, 1089 states, max 4 interventions, max 14 ticks, 1008 states use fewer interventions than pure truncation. These are model-state counts, not frequencies of musical input or perceptual outcomes. Prior negative timing and spectral separation evidence retained.

Reproduce: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build; ctest --test-dir build --output-on-failure. SDK not consumed by this test; existing exact 3.8.0 pin unchanged. Windows and actual host testing of this new increment outstanding. Draft/HOLD.
