# FX-011J — harmonic-memory host bridge (Refs #748)

Creative DSP extension of #264 / draft #265 at 56c107f8f4147316a588484c47be28bc8f840fbb; not a direct general escape solver or human evidence. The existing single-resonator VST3 is unchanged. This is a native adapter foundation, not an installable four-band plugin.

## State and control contract

HM01 is exactly 43 bytes: ASCII magic, little-endian uint16 wet (0..1000), bypass byte (0/1), then four nine-byte records (little-endian uint16 frequency Hz 40..6000, gain, peak mix, selectivity, followed by flags excite=1, erase=2, discard-on-close=4). Other flag bits are invalid. Decode validates before replacing destination. Live lattice, filter histories, clocks and command edges are not serialized. No conversion from CR01/CR02 is implied; those belong to the existing effect. Future stream adapter must reject truncated/oversized states and preserve HM01 decoding.

Global IDs 2000 wet and 2001 bypass; band IDs 2010+9*b+field, b=0..3: frequency, gain, peak mix, selectivity, excite, erase, discard-on-close, pulse, discard in that order. Normalized controls clamp to [0,1], frequency rounds linearly to integer Hz, continuous levels round to permille, switches use >=0.5. Pulse/discard fire only on rising edges, persist edge history across blocks, and are not serialized. Prepare/reset clears edges. The entire sorted event list (maximum 4096 per block) is validated before touching audio or consuming a patch. Offsets must be inside the block; zero frames with zero events admits a pending patch. At an offset persistent edits are coalesced, then commands execute in input order, then that sample processes. Last value for a persistent field at the same offset wins. No interpolation between host points is promised. Direct change() requires a known non-command ID and a finite value.

One control thread publishes whole patches and consumes completed snapshots; one audio thread consumes patches and publishes snapshots. Each direction uses a three-slot single-producer/single-consumer mailbox with atomic ownership exchange, no allocation, waiting or retry. Intermediate unpublished-to-consumer configurations may be overwritten; latest available wins. Snapshot means last completed configuration, not unadmitted requests; immediately saving a pending patch requires additional adapter-side policy. The eventual VST3 adapter must serialize non-audio callers, establish lifecycle ownership and enforce the event cap without silently dropping events. Only planar stereo with separate or exact in-place channel buffers is supported here. Prepare/reset require stopped processing; cross-channel overlapping buffers are unsupported. No actual host or TSAN qualification claimed.

## Reproduce

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    c++ -std=c++17 -O2 bank_host_render.cpp -o bank_host_render
    mkdir -p HostAudio
    ./bank_host_render HostAudio

GCC Release CTest 10/10; Clang ASan/UBSan standalone host probe PASS. The render replays all four FX-011I treatments via HM01 requests and sample-offset automation in 127-frame blocks, producing four PCM16 WAVs byte-identical to their predecessors, including exact final silence. No new acoustic claim or listening assessment. Concurrent handoff witness is a stress test, not a formal memory-model proof or race-detector result. Native tests only; exact SDK pin retained, no SDK source consumed. Next: separate VST3 class identities, parameter/controller and stream adapters, official validator, exact Windows bundle and actual DAW qualification. Preserve negative prior timing and separation results. Draft/HOLD; no shared files or merge.
