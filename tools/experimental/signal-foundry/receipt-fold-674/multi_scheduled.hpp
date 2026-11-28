#pragma once
#include "multi_receipt.hpp"
namespace mhac::receipt::multi {
// Audio-thread-owned, last-value-wins control transaction. No cross-thread mailbox.
class Scheduled {
    Live live_{};
    Config requested_{};
    unsigned period_=48, remaining_=0;
public:
    const Config& requested() const noexcept {return requested_;}
    const Config& active() const noexcept {return live_.config();}
    unsigned period() const noexcept {return period_;}
    unsigned until_boundary() const noexcept {return remaining_;}
    bool request(const Config& p) noexcept {
        if(!valid(p))return false;
        requested_=p;return true;
    }
    bool prepare(double rate) noexcept {
        if(!live_.prepare(rate))return false;
        period_=std::max(32u,static_cast<unsigned>(std::ceil(rate*.001)));
        reset();return true;
    }
    // Lifecycle only: promote the latest request, reset receipt clock and ramps.
    void reset() noexcept {
        live_.apply(requested_);live_.reset();remaining_=0;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(!remaining_){live_.apply(requested_);remaining_=period_;}
        else if(active().wet!=requested_.wet||active().bypass!=requested_.bypass){
            Config cheap=active();cheap.wet=requested_.wet;cheap.bypass=requested_.bypass;
            live_.apply(cheap);
        }
        --remaining_;live_.frame(l,r);
    }
};
}
