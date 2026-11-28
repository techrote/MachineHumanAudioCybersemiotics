#pragma once
#include "orbit.hpp"
namespace mhac::orbit::escape {
// Lexicographic shortest paths on the closure of the 68-state orbit under N/T.
// The graph is constructed in prepare(), never in an audio callback.
struct PhaseRoute {
    unsigned length=0, interventions=0;
    std::array<double,61> gain{};
    double sample(unsigned elapsed,unsigned duration) const noexcept {
        if(!length||!duration||elapsed>=duration)return 0.;
        const double t=double(elapsed)*length/duration;
        const unsigned i=std::min(length-1,unsigned(t));
        return gain[i]+(t-i)*(gain[i+1]-gain[i]);
    }
};
class PhaseBank {
    static constexpr int side=33, count=side*side, weight=count+1, inf=100000000;
    std::array<PhaseRoute,68> routes_{};
    static int index(Point p) noexcept {
        if(std::abs(p.x)>16||std::abs(p.y)>16)return -1;
        return (p.x+16)*side+p.y+16;
    }
    static Point point(int i) noexcept {return {i/side-16,i%side-16};}
public:
    bool prepare() noexcept {
        std::array<int,count> queue{},n{},t{},d{};
        std::array<bool,count> seen{};
        const int start=index({-16,4}),zero=index({});
        int size=1;queue[0]=start;seen[start]=true;
        for(int i=0;i<size;++i){
            const int u=queue[i];Point a,b;
            if(!step(point(u),8,4,9,true,a)||!step(point(u),8,4,9,false,b))return false;
            n[u]=index(a);t[u]=index(b);
            if(n[u]<0||t[u]<0)return false;
            for(int v:{n[u],t[u]})if(!seen[v]){seen[v]=true;queue[size++]=v;}
        }
        if(!seen[zero])return false;
        d.fill(inf);d[zero]=0;
        // Simple optimal paths have fewer than count edges. Positive costs
        // encode (truncations, steps) without allowing a step to carry into cost.
        for(int pass=0;pass<size;++pass){
            bool changed=false;
            for(int i=0;i<size;++i){const int u=queue[i];
                const int cost=std::min(d[n[u]]+1,d[t[u]]+weight+1);
                if(cost<d[u]){d[u]=cost;changed=true;}}
            if(!changed)break;
        }
        int phase=start;
        for(auto& route:routes_){
            route={};route.gain[0]=1.;int u=phase;
            const auto p=point(u);const double energy=double(p.x*p.x+p.y*p.y);
            if(energy==0)return false;
            while(u!=zero){
                if(route.length>=60||d[u]>=inf)return false;
                if(d[u]==d[n[u]]+1)u=n[u];
                else if(d[u]==d[t[u]]+weight+1){u=t[u];++route.interventions;}
                else return false;
                const auto z=point(u);
                route.gain[++route.length]=std::min(1.,double(z.x*z.x+z.y*z.y)/energy);
            }
            if(d[phase]!=int(route.interventions)*weight+int(route.length))return false;
            phase=n[phase];
        }
        return phase==start;
    }
    static unsigned phaseIndex(double phase) noexcept {
        if(!std::isfinite(phase)||phase<0.||phase>=tau)return 0;
        return std::min(67u,unsigned(phase*68./tau));
    }
    const PhaseRoute& route(unsigned i) const noexcept {return routes_[std::min(67u,i)];}
};
} // namespace mhac::orbit::escape
