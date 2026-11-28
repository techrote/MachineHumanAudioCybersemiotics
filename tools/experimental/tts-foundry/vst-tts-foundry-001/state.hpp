#pragma once
#include "logos.hpp"
#include "articulum.hpp"
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstring>

namespace mhac::tts {

template<std::size_t N>
using Patch = std::array<float,N>;
using LogosPatch = Patch<7>;
using ArticulumPatch = Patch<7>;

inline constexpr LogosPatch logosDefaults{{.5f,(1.f-.35f)/(3.f-.35f),0.f,.5f,.65f,0.f,.75f}};
inline constexpr ArticulumPatch articulumDefaults{{.5f,.5f,.25f,.08f,.05f,.5f,.8f}};

inline float unit(float x) noexcept { return std::clamp(x,0.f,1.f); }
inline unsigned phrase_index(float x) noexcept { return static_cast<unsigned>(std::lround(unit(x)*7.f)); }

inline LogosParameters logos_parameters(const LogosPatch& q) noexcept {
    LogosParameters p{};
    p.pitchSemitones=-24.f+48.f*unit(q[0]);
    p.rate=.35f+2.65f*unit(q[1]);
    p.whisper=unit(q[2]);
    p.formantShiftSemitones=-18.f+36.f*unit(q[3]);
    p.articulation=unit(q[4]);
    p.gain=unit(q[6]);
    return p;
}
inline ArticulumParameters articulum_parameters(const ArticulumPatch& q) noexcept {
    ArticulumParameters p{};
    p.tongueFront=unit(q[0]);p.tongueHeight=unit(q[1]);p.lipRound=unit(q[2]);
    p.aspiration=unit(q[3]);p.nasal=unit(q[4]);p.pitchSemitones=-24.f+48.f*unit(q[5]);p.gain=unit(q[6]);
    return p;
}

template<std::size_t N>
using StateBytes=std::array<std::uint8_t,4+4*N>;

template<std::size_t N>
inline StateBytes<N> encode_patch(const Patch<N>& p, const std::array<std::uint8_t,4>& magic) noexcept {
    StateBytes<N> b{}; for(unsigned i=0;i<4;++i)b[i]=magic[i];
    for(std::size_t i=0;i<N;++i){
        float x=unit(p[i]);std::uint32_t u=0;std::memcpy(&u,&x,4);
        for(unsigned j=0;j<4;++j)b[4+i*4+j]=static_cast<std::uint8_t>((u>>(8*j))&255u);
    }
    return b;
}
template<std::size_t N>
inline bool decode_patch(const StateBytes<N>& b, Patch<N>& p, const std::array<std::uint8_t,4>& magic) noexcept {
    for(unsigned i=0;i<4;++i)if(b[i]!=magic[i])return false;
    Patch<N> q{};
    for(std::size_t i=0;i<N;++i){
        std::uint32_t u=0;for(unsigned j=0;j<4;++j)u|=std::uint32_t(b[4+i*4+j])<<(8*j);
        float x=0;std::memcpy(&x,&u,4);if(!std::isfinite(x)||x<0.f||x>1.f)return false;q[i]=x;
    }
    p=q;return true;
}
inline auto encode_logos(const LogosPatch& p) noexcept { return encode_patch(p,{{'L','G','0','1'}}); }
inline auto encode_articulum(const ArticulumPatch& p) noexcept { return encode_patch(p,{{'A','R','0','1'}}); }
inline bool decode_logos(const StateBytes<7>& b,LogosPatch& p) noexcept {return decode_patch(b,p,{{'L','G','0','1'}});}
inline bool decode_articulum(const StateBytes<7>& b,ArticulumPatch& p) noexcept {return decode_patch(b,p,{{'A','R','0','1'}});}

} // namespace mhac::tts
