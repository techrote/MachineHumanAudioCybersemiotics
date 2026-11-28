#include "shuttle_control.hpp"
#include <iostream>
#include <limits>
using namespace mhac::accel;
int main(){
    unsigned checks=0;
    for(unsigned id=0;id<4;++id)for(unsigned n=0;n<=1000;++n){
        ShuttlePatch p{};if(!applyShuttleNormalized(p,id,n/1000.)||shuttleNormalized(p,id)!=n/1000.)return 1;
        ShuttlePatch q{};if(!decode(encode(p),q)||encode(q)!=encode(p))return 2;
        ++checks;
    }
    ShuttlePatch p{};auto before=encode(p);
    for(double x:{-1.,1.1,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        for(unsigned id=0;id<5;++id){if(applyShuttleNormalized(p,id,x)||encode(p)!=before)return 3;++checks;}
    if(applyShuttleNormalized(p,5,.5)||encode(p)!=before)return 4;
    if(!applyShuttleNormalized(p,4,.5)||!p.bypass||!applyShuttleNormalized(p,4,.499)||p.bypass)return 5;
    std::cout<<"PASS "<<checks+3<<" mapping/state checks\n";
}
