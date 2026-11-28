#pragma once
// Derived from the existing MHAC TraceStateBridge/TraceLatest implementation.
// Fixed-size snapshots only. No allocation, waiting or mutex in audio paths.
#include <array>
#include <atomic>
#include <cstdint>
#include <mutex>
#include <type_traits>

namespace mhac::mainline {
template<class T> class Latest {
    static_assert(std::is_trivially_copyable<T>::value, "plain snapshot required");
    static_assert(std::atomic<unsigned>::is_always_lock_free, "lock-free index required");
    std::array<T,3> slots_;
    std::atomic<unsigned> middle_{1};
    unsigned back_=2, front_=0;
    static constexpr unsigned dirty=4;
public:
    explicit Latest(const T& initial) noexcept : slots_{{initial,initial,initial}} {}
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
// Host lifecycle operations must be serialized with audio. UI state callers
// may overlap audio and are serialized only with one another. Audio owns DSP.
// A restore is applied at the next valid audio/lifecycle boundary; before that
// a save returns the requested patch, not a stale audio observation.
template<class Patch> class StateBridge {
    struct Version { Patch patch; std::uint64_t generation; };
    Latest<Version> toAudio_,toControl_;
    std::mutex control_;
    Version requested_,observed_;
    std::uint64_t applied_=0;
public:
    explicit StateBridge(const Patch& initial) noexcept :
        toAudio_(Version{initial,0}),toControl_(Version{initial,0}),
        requested_{initial,0},observed_{initial,0} {}
    void request(const Patch& p) {
        const std::lock_guard<std::mutex> lock(control_);
        requested_={p,requested_.generation+1};
        toAudio_.publish(requested_);
    }
    Patch snapshot() {
        const std::lock_guard<std::mutex> lock(control_);
        toControl_.consume(observed_);
        return observed_.generation==requested_.generation?observed_.patch:requested_.patch;
    }
    bool take(Patch& p) noexcept {
        Version v{};if(!toAudio_.consume(v))return false;
        p=v.patch;applied_=v.generation;return true;
    }
    void publish(const Patch& p) noexcept {toControl_.publish({p,applied_});}
};
} // namespace mhac::mainline
