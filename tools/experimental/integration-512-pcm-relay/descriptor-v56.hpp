#pragma once
// Refs #512. Independent fixed-size local descriptor adapter; no authentication or PCM decoder.
#include <array>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <limits>
namespace mhac56 {
using Wire = std::array<std::uint8_t,20>;
struct Descriptor {
    std::uint8_t session,generation,source,event,sequence,value,status,revision;
    std::uint32_t challenge;
    double phase;
};
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559,"binary64 required");
inline bool valid(const Descriptor& d) noexcept {
    return d.session>0 && (d.source==1||d.source==2) && d.sequence>=1 && d.sequence<=16 && d.value<=3 &&
      ((d.event==6&&d.source==1)||(d.event==7&&d.source==1&&d.sequence<=4)||d.event==8) &&
      ((d.status==0&&d.revision==0)||(d.status>=1&&d.status<=8&&d.revision>=1&&d.revision<=4)) &&
      d.challenge>0 && std::isfinite(d.phase);
}
inline bool decode(const Wire& w, Descriptor& out) noexcept {
    Descriptor d{w[0],w[1],w[2],w[3],w[4],w[5],w[6],w[7],0,0.0};
    for(unsigned i=8;i<12;++i) d.challenge=(d.challenge<<8)|w[i];
    std::uint64_t bits=0;for(unsigned i=12;i<20;++i) bits=(bits<<8)|w[i];
    std::memcpy(&d.phase,&bits,8);
    if(!valid(d))return false;
    out=d;return true;
}
inline bool encode(const Descriptor& d, Wire& out) noexcept {
    if(!valid(d))return false;
    Wire w{d.session,d.generation,d.source,d.event,d.sequence,d.value,d.status,d.revision};
    for(unsigned i=0;i<4;++i)w[8+i]=static_cast<std::uint8_t>(d.challenge>>(24-8*i));
    std::uint64_t bits=0;std::memcpy(&bits,&d.phase,8);
    for(unsigned i=0;i<8;++i)w[12+i]=static_cast<std::uint8_t>(bits>>(56-8*i));
    out=w;return true;
}
} // namespace mhac56
