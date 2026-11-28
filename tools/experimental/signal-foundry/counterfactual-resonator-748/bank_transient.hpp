#pragma once
#include "bank_budget.hpp"

namespace mhac::counterfactual {
// Independent audio key, not a VST3 sidechain bus. A rising envelope crossing
// consumes its arm even during refractory time; a held key cannot retrigger.
class TransientGate {
    double peak_=0, decay_=0.99, high_=0.25, low_=0.10;
    unsigned cooldown_=0, hold_=4800;
    bool armed_=true;
    static double level(double x) noexcept {
        return std::isfinite(x)?std::min(1.0,std::abs(x)):0.0;
    }
public:
    bool prepare(double rate,double high=0.25,double low=0.10,double holdMs=100) noexcept {
        if(!validSampleRate(rate)||!std::isfinite(high)||!std::isfinite(low)||
           !std::isfinite(holdMs)||low<0.001||high<=low||high>1||holdMs<0||holdMs>1000)return false;
        high_=high;low_=low;hold_=static_cast<unsigned>(std::ceil(rate*holdMs/1000));
        decay_=std::exp(-1.0/(rate*0.005));reset();return true;
    }
    void reset() noexcept {peak_=0;cooldown_=0;armed_=true;}
    bool observe(double left,double right) noexcept {
        if(cooldown_)--cooldown_;
        peak_=std::max({peak_*decay_,level(left),level(right)});
        if(peak_<1e-20)peak_=0;
        if(peak_<=low_)armed_=true;
        if(armed_&&peak_>=high_){
            armed_=false;
            if(!cooldown_){cooldown_=hold_;return true;}
        }
        return false;
    }
};
// Audio owner calls before processing the corresponding program sample.
// A budget is per admitted onset, not a cumulative session allowance.
inline BudgetPlan transientErase(TransientGate& gate,HarmonicBank& bank,
                                  double keyL,double keyR,unsigned budget,
                                  BudgetObjective objective) noexcept {
    return gate.observe(keyL,keyR)?beginBudgetedEscape(bank,budget,objective):BudgetPlan{};
}
} // namespace mhac::counterfactual
