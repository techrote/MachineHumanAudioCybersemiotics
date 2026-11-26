#include "compiler.hpp"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cstdint>
using namespace mhac::lattice;
using namespace mhac::lattice::design;
static void sample(std::ofstream& o,double x){auto u=static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(x*32767)));o.put(static_cast<char>(u&255));o.put(static_cast<char>(u>>8));}
int main(){
    constexpr double sr=48000;const std::vector<Probe> target{{375,0},{750,1},{1125,0},{1500,1},{1875,0},{2250,1}};const std::array<unsigned,4> delays{8,16,32,64};
    auto best=compile(target,sr,delays,120);Program base{{{Axis::Sum,32},{Axis::Left,32},{Axis::Right,32},{Axis::Left,24}}}; // single mixing stage, same tail budget
    std::ofstream table("routing.csv");table<<std::setprecision(17)<<"hz,target_right,compiled_right,baseline_right\n";double baseline=0;
    for(auto p:target){double a=std::norm(response(best.program,p.hz,sr).r),b=std::norm(response(base,p.hz,sr).r);table<<p.hz<<','<<p.rightPower<<','<<a<<','<<b<<'\n';baseline+=(b-p.rightPower)*(b-p.rightPower);}
    std::ofstream patch("patch.txt");patch<<std::setprecision(17)<<"evaluated="<<best.evaluated<<"\nmse="<<best.mse<<"\nbaseline_mse="<<baseline/target.size()<<'\n';for(auto s:best.program)patch<<static_cast<unsigned>(s.axis)<<','<<s.delay<<'\n';
    Lattice dsp,ref,inv;dsp.configure(best.program);ref.configure(base);inv.configure(best.program,true);
    std::ofstream dry("dry.pcm",std::ios::binary),out("compiled.pcm",std::ios::binary),old("baseline.pcm",std::ios::binary),rec("reconstructed.pcm",std::ios::binary);
    unsigned nframes=unsigned(sr*3),tail=dsp.tail();std::vector<double> history(nframes+tail);double error=0,peak=0;
    for(unsigned n=0;n<history.size();++n){double x=0;if(n<nframes){unsigned slot=n/24000;double t=(n%24000)/sr;double env=std::min({1.,t/.01,(.5-t)/.01});x=.06*env*std::sin(2*pi*target[slot].hz*t);}history[n]=x;auto y=dsp.step({x,0}),b=ref.step({x,0}),z=inv.step(y);for(auto pair:{std::pair<std::ofstream*,Frame>{&dry,{x,0}},{&out,y},{&old,b},{&rec,z}}){sample(*pair.first,pair.second.l);sample(*pair.first,pair.second.r);}error=std::max({error,std::abs(z.l-(n>=tail?history[n-tail]:0)),std::abs(z.r)});peak=std::max({peak,std::abs(y.l),std::abs(y.r)});}
    std::cout<<"evaluated="<<best.evaluated<<" mse="<<best.mse<<" baseline="<<baseline/target.size()<<" delay="<<tail<<" error="<<error<<" peak="<<peak<<'\n';if(error>1e-12)return 1;
}
