#pragma once
#include "../lattice.hpp"
#include <complex>
#include <vector>
#include <stdexcept>
#include <limits>
namespace mhac::lattice::design {
using C=std::complex<double>;
struct Probe {double hz, rightPower;};
struct Response {C l,r;};
constexpr double pi=3.14159265358979323846;
inline Response stage(Response x, Axis axis, C z) {
    Response p{};
    switch(axis) {
    case Axis::Left:p.l=x.l;break;
    case Axis::Right:p.r=x.r;break;
    case Axis::Sum:p.l=p.r=(x.l+x.r)*.5;break;
    case Axis::Difference:p.l=(x.l-x.r)*.5;p.r=-p.l;break;
    }
    return {x.l+(z-1.)*p.l,x.r+(z-1.)*p.r};
}
inline Response response(const Program& program,double hz,double sr) {
    Response x{1.,0.};
    for(auto s:program)x=stage(x,s.axis,std::polar(1.,-2*pi*hz*s.delay/sr));
    return x;
}
struct Result {Program program{}; double mse=std::numeric_limits<double>::infinity(); unsigned evaluated=0;};
// Offline only. Four distinct positive delay choices, four axes, four stages.
inline Result compile(const std::vector<Probe>& probes,double sr,const std::array<unsigned,4>& delays,unsigned budget=4096) {
    if(!std::isfinite(sr)||sr<8000||sr>384000||probes.empty()||probes.size()>64||budget<4||budget>4096)throw std::invalid_argument("search bounds");
    for(unsigned i=0;i<4;++i){if(delays[i]<1||delays[i]>1024)throw std::invalid_argument("delay");for(unsigned j=0;j<i;++j)if(delays[i]==delays[j])throw std::invalid_argument("duplicate delay");}
    std::vector<std::array<C,4>> phases(probes.size());
    for(unsigned i=0;i<probes.size();++i){auto p=probes[i];if(!std::isfinite(p.hz)||p.hz<0||p.hz>sr/2||!std::isfinite(p.rightPower)||p.rightPower<0||p.rightPower>1)throw std::invalid_argument("probe");for(unsigned j=0;j<4;++j)phases[i][j]=std::polar(1.,-2*pi*p.hz*delays[j]/sr);}
    Result best; unsigned bestTail=4097;
    for(unsigned code=0;code<65536;++code){unsigned tail=0;Program p{};std::array<unsigned,4> choice{};for(unsigned j=0;j<4;++j){choice[j]=(code>>(4*j))&15;p[j]={static_cast<Axis>(choice[j]/4),delays[choice[j]%4]};tail+=p[j].delay;}if(tail>budget)continue;
        ++best.evaluated;double err=0;for(unsigned i=0;i<probes.size();++i){Response x{1.,0.};for(unsigned j=0;j<4;++j)x=stage(x,p[j].axis,phases[i][choice[j]%4]);double d=std::norm(x.r)-probes[i].rightPower;err+=d*d;}err/=probes.size();
        // Stable enumeration order breaks exact ties after tail; no approximate-optimal claim.
        if(err<best.mse||(err==best.mse&&tail<bestTail)){best.program=p;best.mse=err;bestTail=tail;}
    }
    if(!best.evaluated)throw std::invalid_argument("no feasible program");
    return best;
}
}
