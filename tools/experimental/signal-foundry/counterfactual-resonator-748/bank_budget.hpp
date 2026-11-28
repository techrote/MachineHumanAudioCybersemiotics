#pragma once
#include "harmonic_bank.hpp"

namespace mhac::counterfactual {
// Snapshot admission budget, not a time-window rate limiter. One T update
// acts on a band's stereo state; simultaneous updates in two bands cost two.
enum class BudgetObjective { count, energy };
struct BudgetCandidate { unsigned cost=0, energy=0; }; // zero cost means unavailable
struct BudgetPlan { unsigned mask=0, cost=0, count=0, energy=0; };
constexpr bool betterBudget(BudgetPlan a,BudgetPlan b,BudgetObjective objective) noexcept {
    if(objective==BudgetObjective::energy&&a.energy!=b.energy)return a.energy>b.energy;
    if(a.count!=b.count)return a.count>b.count;
    if(a.energy!=b.energy)return a.energy>b.energy;
    if(a.cost!=b.cost)return a.cost<b.cost;
    return a.mask<b.mask;
}
constexpr BudgetPlan chooseBudget(const std::array<BudgetCandidate,4>& candidates,
                                  unsigned budget,BudgetObjective objective) noexcept {
    BudgetPlan best{};
    if(budget>16)return best;
    for(unsigned mask=1;mask<16;++mask){
        BudgetPlan p{mask,0,0,0}; bool eligible=true;
        for(unsigned i=0;i<4;++i)if(mask&(1u<<i)){
            const auto c=candidates[i];
            if(c.cost<1||c.cost>4||c.energy<1||c.energy>1024){eligible=false;break;}
            p.cost+=c.cost; ++p.count; p.energy+=c.energy;
        }
        if(eligible&&p.cost<=budget&&betterBudget(p,best,objective))best=p;
    }
    return best;
}
inline BudgetCandidate budgetCandidate(const HarmonicBank& bank,unsigned band) noexcept {
    if(!bank.canBeginNewOptimalEscape(band))return {};
    const auto l=bank.lattice(band,0),r=bank.lattice(band,1);
    return {unsigned(std::min(4,std::max(magnitude(l),magnitude(r)))),
            unsigned(l.x*l.x+l.y*l.y+r.x*r.x+r.y*r.y)};
}
// Audio-owner only: snapshot and admission run synchronously between samples.
// No allocations, clock changes or interference with already-running policies.
inline BudgetPlan beginBudgetedEscape(HarmonicBank& bank,unsigned budget,
                                       BudgetObjective objective,unsigned eligibleMask=15) noexcept {
    if(eligibleMask>15)return {};
    std::array<BudgetCandidate,4> candidates{};
    for(unsigned i=0;i<4;++i)if(eligibleMask&(1u<<i))candidates[i]=budgetCandidate(bank,i);
    const auto plan=chooseBudget(candidates,budget,objective);
    BudgetPlan admitted{};
    for(unsigned i=0;i<4;++i)if((plan.mask&(1u<<i))&&bank.beginOptimalEscape(i)){
        admitted.mask|=1u<<i; admitted.cost+=candidates[i].cost;
        ++admitted.count; admitted.energy+=candidates[i].energy;
    }
    return admitted;
}
} // namespace mhac::counterfactual
