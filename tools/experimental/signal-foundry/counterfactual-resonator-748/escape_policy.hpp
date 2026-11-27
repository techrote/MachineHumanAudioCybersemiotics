#pragma once
#include "resonator.hpp"
#include <limits>

namespace mhac::counterfactual {
// Exact offline compiler for the finite, undriven, single-channel q=9 lattice.
// Construct off the audio thread; lookup is constant time and allocation-free.
class EscapePolicy {
public:
    static constexpr unsigned side=2*limit+1, states=side*side, weight=states+1;
    static constexpr unsigned infinity=std::numeric_limits<unsigned>::max()/2;
    struct Decision { unsigned interventions=0, ticks=0; bool truncate=false, valid=false; };
private:
    std::array<unsigned,states> costs_{};
    static constexpr unsigned index(IntegerState s) noexcept {
        return unsigned(s.x+limit)*side+unsigned(s.y+limit);
    }
    static constexpr IntegerState state(unsigned i) noexcept {
        return {int(i/side)-limit,int(i%side)-limit};
    }
public:
    EscapePolicy() noexcept {
        costs_.fill(infinity); costs_[index({0,0})]=0;
        // Synchronous Bellman relaxation; positive weights imply a simple optimum.
        for(unsigned pass=0;pass<states-1;++pass){
            auto next=costs_; bool changed=false;
            for(unsigned i=0;i<states;++i){
                const auto s=state(i);
                const unsigned n=costs_[index(step(s,0,false))]+1;
                const unsigned t=costs_[index(step(s,0,true))]+weight+1;
                next[i]=std::min(costs_[i],std::min(n,t)); changed|=next[i]!=costs_[i];
            }
            costs_=next; if(!changed)break;
        }
    }
    Decision lookup(IntegerState s) const noexcept {
        if(s.x<-limit||s.x>limit||s.y<-limit||s.y>limit)return {};
        const unsigned c=costs_[index(s)];
        if(c>=infinity)return {};
        if(c==0)return {0,0,false,true};
        const bool t=costs_[index(step(s,0,false))]+1!=c;
        return {c/weight,c%weight,t,true};
    }
};
} // namespace mhac::counterfactual
