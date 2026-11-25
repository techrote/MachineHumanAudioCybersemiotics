#pragma once
#include "engine.hpp"
#include <vector>
#include <stdexcept>
namespace mhac::organ {
// Offline finite-state compiler. Never construct/search on the audio thread.
class TrajectoryCompiler {
    struct Node { unsigned a,b,level,parent,depth; };
    std::vector<Node> nodes;
    std::array<std::array<int,17>,17> best{};
    static unsigned key(unsigned a,unsigned b,unsigned level){return (a*256+b)*17+level;}
public:
    TrajectoryCompiler(){
        for(auto& row:best)row.fill(-1);
        std::vector<int> seen(256*256*17,-1);
        nodes.push_back({0,0,0,0,0});seen[0]=0;
        for(unsigned i=0;i<nodes.size();++i){
            const auto n=nodes[i];
            const int delta=int(Relays::count(n.a))-int(Relays::count(n.b));
            auto& slot=best[n.level][delta+8];if(slot<0)slot=int(i);
            for(unsigned x=0;x<17;++x){
                Relays r{n.a,n.b};r.visit(x);const auto k=key(r.a,r.b,x);
                if(seen[k]<0){seen[k]=int(nodes.size());nodes.push_back({r.a,r.b,x,i,n.depth+1});}
            }
        }
    }
    unsigned reachable() const{return unsigned(nodes.size());}
    // Signed difference is in relay counts [-8,8]. Empty means unreachable.
    // Returned levels include initial zero; ascending tie order is deterministic.
    std::vector<unsigned> shortest(unsigned level,int delta) const{
        if(level>16||delta< -8||delta>8)throw std::out_of_range("trajectory target");
        int idx=best[level][delta+8];if(idx<0)return {};
        std::vector<unsigned> path;for(;;){const auto& n=nodes[unsigned(idx)];path.push_back(n.level);if(idx==0)break;idx=int(n.parent);}
        std::reverse(path.begin(),path.end());return path;
    }
};
}
