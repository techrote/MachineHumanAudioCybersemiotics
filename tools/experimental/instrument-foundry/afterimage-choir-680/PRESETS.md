# Afterimage Choir — offline preset bank (INST-010D)

Refs #680, creative synthesis derived from #338/#339 at f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64. No new research claims.

The original Windows VST3 0.1.0 was qualified at 395bbda123255b8a9a0bc585aabd2c2e337a0393, run 45816239693, artifact 15115991707. This change adds an offline generator, not a change to the plugin binary, IDs, AC01 or synthesis law.

Build with CMake 3.25+ and a C++17 compiler; run:
```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
./build/afterimage_preset_bank presets
```
On multi-config Windows builds use build/Release/afterimage_preset_bank.exe.

Eight component-only VST3 preset containers, four previous patch designs and four new configurations. Format independently implemented from the pinned SDK public.sdk commit a3911a4615dabbfdfd9d181ee26b05c70c289a95, source/vst/vstpresetfile.cpp, writeHeader/writeChunkList/loadPreset. Header class ID from qualified moduleinfo; 8-byte AC01 Comp payload. No Cont chunk is needed by that SDK load path. Use a host's VST3 preset import (where supported); alternatively enter parameters manually. No live performance memory or cancellation gate is stored. Reset between comparisons if desired; patch restoration intentionally preserves performance memory.

Try holding D4 for at least 700 ms, releasing, then playing C4; compare Ambiguous Parity and Informed Memory from a fresh instance. Slow Commit ignores short gestures; Flicker Memory admits immediate releases. Pure Fundamental is the reference.

GCC 14.2 native CTest 3/3 and Clang 17 ASan/UBSan preset test passed locally; 1008 grid roundtrips, 640 deliberately corrupted structural bytes rejected, 806400 exact paired native audio frames. Strict reader is limited to the generated 84-byte format; not a general-purpose parser. No SDK-host preset import, DAW listening, fresh Windows build or independent review claimed for this addition. Keep the qualified 010C binary distinct from the subsequent source head. SDK pins unchanged. Draft/HOLD.
