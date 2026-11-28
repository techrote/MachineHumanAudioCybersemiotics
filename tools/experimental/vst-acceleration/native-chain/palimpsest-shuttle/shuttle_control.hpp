#pragma once
#include "shuttle.hpp"
namespace mhac::accel {
inline double shuttleNormalized(const ShuttlePatch& p,unsigned id) noexcept {
    switch(id){case 0:return p.mix/1000.;case 1:return p.reverse/1000.;case 2:return p.feedback/1000.;case 3:return p.cross/1000.;case 4:return p.bypass?1.:0.;default:return 0.;}
}
inline bool applyShuttleNormalized(ShuttlePatch& p,unsigned id,double v) noexcept {
    if(id>=5||!std::isfinite(v)||v<0||v>1)return false;
    const auto n=static_cast<uint16_t>(std::floor(v*1000.+.5));
    switch(id){case 0:p.mix=n;break;case 1:p.reverse=n;break;case 2:p.feedback=n;break;case 3:p.cross=n;break;case 4:p.bypass=v>=.5;break;}
    return true;
}
}
