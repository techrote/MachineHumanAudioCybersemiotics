#pragma once
#include "control.hpp"
#include <atomic>
#include <mutex>
#include <thread>

namespace restbus::control {
// One serialized writer per mailbox. All participating words are atomic and
// sequentially consistent: an equal even sequence brackets one coherent read.
// A reader makes exactly one attempt; it never waits for a preempted writer.
class StateMailbox {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
                  "Rest Bus state handoff requires lock-free 64-bit atomics");
    std::atomic<std::uint64_t> sequence_{0}, acknowledgement_{0};
    std::array<std::atomic<std::uint64_t>,defaults.size()> words_{};
public:
    struct Snapshot { Params params=defaults; std::uint64_t sequence=0, ack=0; };
    explicit StateMailbox(std::uint64_t ack=0) noexcept { publish(defaults,ack); }
    void publish(const Params& p,std::uint64_t ack=0) noexcept {
        const auto seq=sequence_.load();
        sequence_.store(seq+1);
        for(unsigned i=0;i<defaults.size();++i){std::uint64_t bits;std::memcpy(&bits,&p[i],8);words_[i].store(bits);}
        acknowledgement_.store(ack);
        sequence_.store(seq+2);
    }
    std::uint64_t acknowledged() const noexcept { return acknowledgement_.load(); }
    bool read(Snapshot& out) const noexcept {
        Snapshot s; s.sequence=sequence_.load();
        if(s.sequence&1u)return false;
        for(unsigned i=0;i<defaults.size();++i){const auto bits=words_[i].load();std::memcpy(&s.params[i],&bits,8);}
        s.ack=acknowledgement_.load();
        if(sequence_.load()!=s.sequence)return false;
        out=s;return true;
    }
};

// Audio owns Live. Non-audio state callers serialize only with one another.
// Requests coalesce (latest wins) until the next process-block boundary.
// Save observes either a coherent published block or the newest pending patch.
class StateBridge {
    StateMailbox requested_, published_{2};
    std::mutex stateMutex_;
    std::uint64_t applied_=2, lastAck_=2;
    Params last_=defaults;
public:
    bool request(const Params& p) {
        if(!std::all_of(p.begin(),p.end(),[](double v){return valid(v);}))return false;
        const std::lock_guard<std::mutex> guard(stateMutex_);
        requested_.publish(p);return true;
    }
    bool save(Params& p) {
        const std::lock_guard<std::mutex> guard(stateMutex_);
        StateMailbox::Snapshot request, audio;
        if(!requested_.read(request))return false;
        // The latest request is authoritative until audio publishes its ack.
        // A pending save does not have to contend for the audio snapshot.
        if(request.sequence!=published_.acknowledged()){p=request.params;return true;}
        // Bounded even on the non-audio side; fail rather than save torn data.
        for(unsigned i=0;i<64;++i){
            if(published_.read(audio)){p=audio.params;return true;}
            std::this_thread::yield();
        }
        return false;
    }
    bool begin(Live& engine) noexcept {
        StateMailbox::Snapshot s;
        if(!requested_.read(s)||s.sequence==applied_)return false;
        if(!engine.applyPatch(s.params))return false;
        applied_=s.sequence;return true;
    }
    void end(const Live& engine) noexcept {
        const auto& p=engine.parameters();
        if(applied_!=lastAck_||p!=last_){published_.publish(p,applied_);last_=p;lastAck_=applied_;}
    }
};
}
