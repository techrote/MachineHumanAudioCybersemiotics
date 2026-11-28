#pragma once
#include <array>
#include <atomic>
#include <cstdint>
#include <mutex>
#include <type_traits>

namespace mhac::accel {
// One producer, one consumer. Each owns a private slot; the middle slot is
// exchanged atomically. A producer may replace an unread publication.
// No shared payload is accessed concurrently, and neither side waits.
template<class T> class TraceLatest {
    static_assert(std::is_trivially_copyable<T>::value, "plain snapshot required");
    static_assert(std::atomic<unsigned>::is_always_lock_free, "lock-free index required");
    std::array<T,3> slots_{};
    std::atomic<unsigned> middle_{1};
    unsigned back_=2, front_=0;
    static constexpr unsigned dirty=4;
public:
    explicit TraceLatest(const T& initial) noexcept : slots_{{initial,initial,initial}} {}
    void publish(const T& v) noexcept {
        slots_[back_]=v;
        back_=middle_.exchange(back_|dirty,std::memory_order_acq_rel)&3u;
    }
    bool consume(T& v) noexcept {
        if(!(middle_.load(std::memory_order_acquire)&dirty))return false;
        front_=middle_.exchange(front_,std::memory_order_acq_rel)&3u;
        v=slots_[front_];return true;
    }
};

// Restore and save may run concurrently with audio. Only control calls use
// the mutex. The audio owner takes the latest complete restore at a block
// boundary, then publishes the final parameter snapshot (including automation).
// Lifecycle operations must still be serialized with audio by the host.
template<class Patch> class TraceStateBridge {
    struct Version { Patch patch; std::uint64_t generation; };
    TraceLatest<Version> toAudio_{Version{Patch{},0}};
    TraceLatest<Version> toControl_{Version{Patch{},0}};
    std::mutex control_;
    Version requested_{Patch{},0}, observed_{Patch{},0};
    std::uint64_t applied_=0;
public:
    void request(const Patch& p) {
        const std::lock_guard<std::mutex> lock(control_);
        requested_={p,requested_.generation+1};
        toAudio_.publish(requested_);
    }
    Patch snapshot() {
        const std::lock_guard<std::mutex> lock(control_);
        toControl_.consume(observed_);
        // Before the next block, save the newest requested restore rather
        // than a stale snapshot from the previous audio block.
        return observed_.generation==requested_.generation?observed_.patch:requested_.patch;
    }
    bool take(Patch& p) noexcept {
        Version v{};
        if(!toAudio_.consume(v))return false;
        p=v.patch;applied_=v.generation;return true;
    }
    void publish(const Patch& p) noexcept {toControl_.publish({p,applied_});}
};
} // namespace mhac::accel
