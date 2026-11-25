#pragma once
#include "freeze.hpp"
#include <atomic>
#include <cstring>
#include <limits>
namespace mhac {
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559,"IEEE binary64 required");
using State=std::array<uint8_t,4+8*Count>;
inline State encode(const Params& p) noexcept {
    State out{'M','S','F',1};
    for(unsigned i=0;i<Count;++i){double v=unit(p[i]);uint64_t bits;std::memcpy(&bits,&v,8);for(unsigned j=0;j<8;++j)out[4+8*i+j]=uint8_t(bits>>(8*j));}
    return out;
}
inline bool decode(const State& in,Params& p) noexcept {
    if(in[0]!='M'||in[1]!='S'||in[2]!='F'||in[3]!=1)return false;
    Params next{};
    for(unsigned i=0;i<Count;++i){uint64_t bits=0;for(unsigned j=0;j<8;++j)bits|=uint64_t(in[4+8*i+j])<<(8*j);std::memcpy(&next[i],&bits,8);if(!std::isfinite(next[i])||next[i]<0||next[i]>1)return false;}
    p=next;return true;
}
// Single writer per bank. Reader performs one bounded attempt; no audio-thread spin.
class AtomicBank {
    static_assert(std::atomic<double>::is_always_lock_free&&std::atomic<uint64_t>::is_always_lock_free,"lock-free x64/arm64 atomics required");
    std::atomic<uint64_t> seq{0};
    std::array<std::atomic<double>,Count> values{};
public:
    AtomicBank() noexcept {for(unsigned i=0;i<Count;++i)values[i].store(defaults[i]);}
    uint64_t write(const Params& p) noexcept {
        uint64_t s=seq.load();seq.store(s+1);for(unsigned i=0;i<Count;++i)values[i].store(p[i]);seq.store(s+2);return s+2;
    }
    bool tryRead(Params& p,uint64_t& version) const noexcept {
        uint64_t s=seq.load();if(s&1)return false;Params next{};for(unsigned i=0;i<Count;++i)next[i]=values[i].load();if(seq.load()!=s)return false;p=next;version=s;return true;
    }
};
}
