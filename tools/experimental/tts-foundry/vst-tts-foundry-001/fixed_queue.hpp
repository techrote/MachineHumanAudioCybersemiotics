#pragma once
#include <array>
#include <atomic>
#include <cstddef>

namespace mhac::tts {

template<class T, std::size_t Capacity>
class SpscQueue {
    static_assert(Capacity >= 2, "queue capacity");
    std::array<T, Capacity> slots_{};
    std::atomic<std::size_t> write_{0};
    std::atomic<std::size_t> read_{0};
public:
    bool push(const T& value) noexcept {
        const auto w = write_.load(std::memory_order_relaxed);
        const auto next = (w + 1) % Capacity;
        if (next == read_.load(std::memory_order_acquire)) return false;
        slots_[w] = value;
        write_.store(next, std::memory_order_release);
        return true;
    }
    bool pop(T& value) noexcept {
        const auto r = read_.load(std::memory_order_relaxed);
        if (r == write_.load(std::memory_order_acquire)) return false;
        value = slots_[r];
        read_.store((r + 1) % Capacity, std::memory_order_release);
        return true;
    }
};

} // namespace mhac::tts
