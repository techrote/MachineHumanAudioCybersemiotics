#include "bus_shape.hpp"
#include <iostream>

int main() {
    unsigned cases = 0, accepted = 0, exceptions = 0;
    for (int bus = -1; bus <= 4; ++bus)
        for (bool active : {false, true})
            for (int expected = -1; expected <= 3; ++expected)
                for (int supplied = -1; supplied <= 3; ++supplied)
                    for (bool nullArray : {false, true}) {
                        const bool legalBus = bus >= 0 && bus <= 3;
                        const bool main = bus == 0;
                        const bool legalArrangement = main ? (expected == 1 || expected == 2) : expected == 1;
                        const bool standard = legalBus && legalArrangement && supplied == expected;
                        const bool compat = bus >= 1 && bus <= 3 && !active && expected == 1 && supplied == 0 && nullArray;
                        const bool actual = winters::compat::accepts(bus, active, expected, supplied, nullArray);
                        if (actual != (standard || compat)) {
                            std::cerr << "bus count contract mismatch\n";
                            return 1;
                        }
                        ++cases;
                        accepted += actual;
                        exceptions += compat;
                    }
    if (exceptions != 3 || accepted != 23 || cases != 600) return 2;
    std::cout << "PASS bus profiles=" << cases << " accepted=" << accepted
              << " compatibility_exceptions=" << exceptions << '\n';
}
