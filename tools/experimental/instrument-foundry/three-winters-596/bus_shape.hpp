#pragma once

namespace winters::compat {
// A narrow host compatibility exception: an explicitly inactive mono auxiliary
// may be represented by zero channels and a null channel-array pointer.
// Negotiated arrangements and bus indices do not change.
constexpr bool accepts(int bus, bool active, int expected, int supplied,
                       bool nullArray) noexcept {
    if (bus < 0 || bus > 3 || expected < 1 || expected > (bus == 0 ? 2 : 1) ||
        supplied < 0 || supplied > (bus == 0 ? 2 : 1)) return false;
    if (supplied == expected) return true;
    return bus > 0 && !active && expected == 1 && supplied == 0 && nullArray;
}
}
