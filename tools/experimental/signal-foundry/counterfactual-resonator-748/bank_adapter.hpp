#pragma once
#include "bank_host.hpp"
namespace mhac::counterfactual::bankhost {
constexpr unsigned LegacyParamCount=38, ParamCount=45;
inline unsigned index(unsigned id) noexcept {return id>=FirstOptimal?LegacyParamCount+id-FirstOptimal:id<FirstBand?id-Wet:2+id-FirstBand;}
inline unsigned paramID(unsigned i) noexcept {return i>=LegacyParamCount?FirstOptimal+i-LegacyParamCount:i<2?Wet+i:FirstBand+i-2;}
inline double normalized(const MemoryConfig& c,unsigned id) noexcept {
    if(id==Wet)return c.wet/1000.;
    if(id==Bypass)return c.bypass?1.:0.;
    if(!known(id)||command(id))return 0;
    if(id==Budget)return c.budget/16.;
    if(id==Objective)return c.energyFirst?1.:0.;
    const auto& b=c.bands[(id-FirstBand)/Stride];
    switch((id-FirstBand)%Stride){
    case Frequency:return (b.hz-40)/5960.;case Gain:return b.gain/1000.;
    case Peak:return b.peakMix/1000.;case Selectivity:return b.selectivity/1000.;
    case Excite:return b.excite?1.:0.;case Erase:return b.erase?1.:0.;
    case DiscardOnClose:return b.discardOnClose?1.:0.;default:return 0;
    }
}
// Fixed storage, bounded heap sort; source queue ordering preserved at equal offsets.
class EventBatch {
    struct Entry {Event event{};unsigned ordinal=0;};
    std::array<Entry,MaxEvents> entries_{};
    std::array<Event,MaxEvents> sorted_{};
    std::array<bool,ParamCount> seen_{};
    unsigned count_=0,frames_=0,id_=0,previous_=0;
    bool first_=true,active_=false,ok_=true;
public:
    void clear(unsigned frames) noexcept {count_=0;frames_=frames;seen_={};active_=false;ok_=true;}
    bool queue(unsigned id) noexcept {
        if(!ok_||!known(id)||seen_[index(id)])return ok_=false;
        seen_[index(id)]=true;id_=id;first_=true;active_=true;return true;
    }
    bool point(unsigned offset,double value) noexcept {
        if(!ok_||!active_||count_==MaxEvents||!std::isfinite(value)||
           (frames_?offset>=frames_:offset!=0)||(!first_&&offset<previous_))return ok_=false;
        entries_[count_]={{offset,id_,value},count_};++count_;first_=false;previous_=offset;return true;
    }
    bool finish() noexcept {
        if(!ok_)return false;
        const auto less=[](const Entry& a,const Entry& b){return a.event.offset==b.event.offset?a.ordinal<b.ordinal:a.event.offset<b.event.offset;};
        std::make_heap(entries_.begin(),entries_.begin()+count_,less);
        std::sort_heap(entries_.begin(),entries_.begin()+count_,less);
        for(unsigned i=0;i<count_;++i)sorted_[i]=entries_[i].event;
        return true;
    }
    const Event* data() const noexcept {return sorted_.data();}
    unsigned size() const noexcept {return count_;}
};
}
