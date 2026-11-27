#pragma once
#include "harmonic_bank.hpp"
#include <atomic>

namespace mhac::counterfactual::bankhost {
// State is configuration only, not the live resonator lattice.
using State = std::array<std::uint8_t,43>;
inline bool valid(const MemoryConfig& c) noexcept {
    if(c.wet>1000) return false;
    for(const auto& b:c.bands)
        if(b.hz<40||b.hz>6000||b.gain>1000||b.peakMix>1000||b.selectivity>1000) return false;
    return true;
}
inline State encode(const MemoryConfig& c) noexcept {
    State s{{'H','M','0','1'}};
    unsigned i=4;
    const auto put=[&](unsigned v){s[i++]=static_cast<std::uint8_t>(v);s[i++]=static_cast<std::uint8_t>(v>>8);};
    put(c.wet);s[i++]=static_cast<std::uint8_t>(c.bypass);
    for(const auto& b:c.bands){put(b.hz);put(b.gain);put(b.peakMix);put(b.selectivity);
        s[i++]=static_cast<std::uint8_t>(unsigned(b.excite)|(unsigned(b.erase)<<1)|(unsigned(b.discardOnClose)<<2));}
    return s;
}
inline bool decode(const State& s,MemoryConfig& out) noexcept {
    if(s[0]!='H'||s[1]!='M'||s[2]!='0'||s[3]!='1'||s[6]>1) return false;
    MemoryConfig c{};unsigned i=4;
    const auto get=[&](){const unsigned lo=s[i++];return static_cast<std::uint16_t>(lo|(unsigned(s[i++])<<8));};
    c.wet=get();c.bypass=s[i++]!=0;
    for(auto& b:c.bands){b.hz=get();b.gain=get();b.peakMix=get();b.selectivity=get();
        const unsigned f=s[i++];if(f>7)return false;b.excite=(f&1)!=0;b.erase=(f&2)!=0;b.discardOnClose=(f&4)!=0;}
    if(!valid(c))return false;
    out=c;return true;
}
// Single producer, single consumer. Each owns one slot; the atomic middle
// index exchanges exclusive ownership. No retry loop, no concurrent slot access.
template<class Payload> class MailboxOf {
    std::array<Payload,3> slots_{};
    std::atomic<unsigned> middle_{1};
    unsigned back_=2,front_=0;
public:
    void publish(const Payload& c) noexcept {
        slots_[back_]=c;back_=middle_.exchange(back_|4,std::memory_order_acq_rel)&3;
    }
    bool consume(Payload& c) noexcept {
        if(!(middle_.load(std::memory_order_acquire)&4))return false;
        front_=middle_.exchange(front_,std::memory_order_acq_rel)&3;
        c=slots_[front_];return true;
    }
};
using Mailbox=MailboxOf<MemoryConfig>;
static_assert(std::atomic<unsigned>::is_always_lock_free,"requires lock-free mailbox index");
// Stable candidate parameter IDs: global 2000/2001, four consecutive groups
// of nine beginning at 2010. Pulse/discard are rising-edge, nonpersistent.
constexpr unsigned Wet=2000,Bypass=2001,FirstBand=2010,Stride=9;
enum Field : unsigned { Frequency,Gain,Peak,Selectivity,Excite,Erase,DiscardOnClose,Pulse,Discard };
constexpr unsigned FirstOptimal=2050; // four new momentary controls, legacy IDs unchanged
constexpr unsigned MaxEvents=4096;
inline bool optimalCommand(unsigned id) noexcept {return id>=FirstOptimal&&id<FirstOptimal+4;}
struct Event {unsigned offset,id;double value;};
inline bool known(unsigned id) noexcept {return id==Wet||id==Bypass||(id>=FirstBand&&id<FirstBand+4*Stride)||optimalCommand(id);}
inline bool command(unsigned id) noexcept {return optimalCommand(id)||(id>=FirstBand&&id<FirstBand+4*Stride&&(id-FirstBand)%Stride>=Pulse);}
inline void change(MemoryConfig& c,unsigned id,double value) noexcept {
    if(!known(id)||command(id)||!std::isfinite(value))return;
    const double v=std::clamp(value,0.0,1.0);
    const auto q=static_cast<std::uint16_t>(std::lround(v*1000));
    if(id==Wet){c.wet=q;return;}if(id==Bypass){c.bypass=v>=0.5;return;}
    auto& b=c.bands[(id-FirstBand)/Stride];
    switch((id-FirstBand)%Stride){
    case Frequency:b.hz=static_cast<std::uint16_t>(40+std::lround(v*5960));break;
    case Gain:b.gain=q;break;case Peak:b.peakMix=q;break;case Selectivity:b.selectivity=q;break;
    case Excite:b.excite=v>=0.5;break;case Erase:b.erase=v>=0.5;break;
    case DiscardOnClose:b.discardOnClose=v>=0.5;break;default:break;}
}
class Host {
    HarmonicBank dsp_{};
    struct Ticket {MemoryConfig config{}; std::uint64_t generation=0;};
    MemoryConfig current_{};
    Ticket requested_{},lastPublished_{};
    std::uint64_t admitted_=0;
    MailboxOf<Ticket> requests_,completed_;
    std::array<std::array<bool,3>,4> edges_{};
    void trigger(const Event& e) noexcept {
        const bool optimal=optimalCommand(e.id);
        const unsigned band=optimal?e.id-FirstOptimal:(e.id-FirstBand)/Stride;
        const unsigned f=optimal?2:(e.id-FirstBand)%Stride-Pulse;
        const bool high=e.value>=0.5;
        if(high&&!edges_[band][f]){if(f==0)dsp_.pulse(band);else if(f==1)dsp_.discardPendingInput(band);else dsp_.beginOptimalEscape(band);}
        edges_[band][f]=high;
    }
    void admit() noexcept {Ticket t;if(requests_.consume(t)){current_=t.config;admitted_=t.generation;dsp_.set(current_);}}
    void complete() noexcept {completed_.publish({current_,admitted_});}
public:
    // Control thread only: request and snapshot. Snapshot means last completed
    // audio block, not a pending request. One control thread is required.
    bool request(const MemoryConfig& c) noexcept {if(!valid(c))return false;requested_={c,requested_.generation+1};requests_.publish(requested_);return true;}
    bool request(const State& s) noexcept {MemoryConfig c{};return decode(s,c)&&request(c);}
    State snapshot() noexcept {completed_.consume(lastPublished_);return encode(lastPublished_.config);}
    // For state saves: a pending control request wins until the audio thread acknowledges it.
    State save() noexcept {completed_.consume(lastPublished_);return encode(lastPublished_.generation==requested_.generation?lastPublished_.config:requested_.config);}
    // Audio lifecycle only, stopped processing required for prepare/reset.
    bool prepare(double rate) noexcept {if(!dsp_.prepare(rate))return false;reset();return true;}
    void reset() noexcept {admit();dsp_.reset();edges_={};complete();}
    // Planar stereo; exact in-place supported. Event list sorted by offset;
    // validate entire list before changing state or touching output.
    template<class Sample> bool process(const Sample* l,const Sample* r,Sample* ol,Sample* oright,
                                       unsigned n,const Event* events=nullptr,unsigned count=0) noexcept {
        if(n&&(!l||!r||!ol||!oright))return false;
        return processOptional(l,r,ol,oright,n,events,count);
    }
    // Null input channels mean silence; null output channels are discarded.
    // A zero-frame block accepts offset-zero events for host parameter flush.
    template<class Sample> bool processOptional(const Sample* l,const Sample* r,Sample* ol,Sample* oright,
                                       unsigned n,const Event* events=nullptr,unsigned count=0) noexcept {
        if(count>MaxEvents||(count&&!events))return false;
        for(unsigned i=0;i<count;++i){const auto& e=events[i];
            if((n?e.offset>=n:e.offset!=0)||!known(e.id)||!std::isfinite(e.value)||(i&&e.offset<events[i-1].offset))return false;}
        admit();unsigned j=0;
        for(unsigned i=0;i<(n?n:1);++i){
            const unsigned start=j;bool changed=false;
            while(j<count&&events[j].offset==i){if(!command(events[j].id)){change(current_,events[j].id,events[j].value);changed=true;}++j;}
            if(changed)dsp_.set(current_);
            for(unsigned k=start;k<j;++k)if(command(events[k].id)&&!optimalCommand(events[k].id))trigger(events[k]);
            // Existing manual commands take priority regardless of host queue order.
            for(unsigned k=start;k<j;++k)if(optimalCommand(events[k].id))trigger(events[k]);
            if(n){const auto s=dsp_.process(l?l[i]:0,r?r[i]:0);if(ol)ol[i]=static_cast<Sample>(s.left);if(oright)oright[i]=static_cast<Sample>(s.right);}
        }
        complete();return true;
    }
};
} // namespace mhac::counterfactual::bankhost
