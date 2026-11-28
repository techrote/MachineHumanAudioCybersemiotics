#pragma once
namespace mhac::mainline {
// Match the qualified Three Winters inactive-aux exception, with a per-plugin bus limit.
template<int MaxAux>
constexpr bool acceptsOutputShape(int bus, bool active, int expected, int supplied,
                                  bool nullArray) noexcept {
    if (bus < 0 || bus > MaxAux || expected < 1 || expected > (bus == 0 ? 2 : 1) ||
        supplied < 0 || supplied > (bus == 0 ? 2 : 1)) return false;
    if (supplied == expected) return true;
    return bus > 0 && !active && expected == 1 && supplied == 0 && nullArray;
}
}
