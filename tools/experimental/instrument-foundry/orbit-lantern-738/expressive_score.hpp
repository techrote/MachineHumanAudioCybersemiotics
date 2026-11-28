#pragma once
#include "host.hpp"
#include <vector>
namespace mhac::orbit::expressive {
struct Note {unsigned on,off;int pitch;double velocity;Patch attack;unsigned mode,depth;};
constexpr Note score[]{
    {0,1800,48,.76,{180,650,-12,0,0,900,1400},2,700},
    {500,2300,55,.68,{700,900,0,0,0,1000,6000},1,250},
    {1000,2800,64,.82,{550,180,12,0,0,800,320},2,800},
    {2000,3400,69,.70,{350,500,-7,0,0,500,780},0,0}
};
constexpr Patch fixed{180,650,-12,2,700,0,1000};
struct Control {unsigned at,index;double value;};
inline std::vector<Control> controls(bool expressive){
    std::vector<Control> c;
    for(const auto& n:score){const auto p=expressive?n.attack:fixed;
        for(unsigned k=0;k<host::count;++k)c.push_back({n.on,k,host::normalized(p,k)});
        c.push_back({n.off,3,expressive?n.mode/2.:fixed.releaseMode/2.});
        c.push_back({n.off,4,expressive?n.depth/1000.:fixed.spectralDepth/1000.});}
    // Mid-note change: neither note admission nor release at this offset.
    if(expressive){c.push_back({750,5,0.});c.push_back({750,6,1.});}
    std::stable_sort(c.begin(),c.end(),[](auto a,auto b){return a.at<b.at||(a.at==b.at&&a.index<b.index);});return c;
}
}
