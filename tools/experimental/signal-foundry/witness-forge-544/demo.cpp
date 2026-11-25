#include "forge.hpp"
#include <chrono>
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace mhac::forge;
constexpr double pi=3.14159265358979323846;
static void sample(std::ofstream& o,double x){auto u=static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(32767*x)));o.put(static_cast<char>(u&255));o.put(static_cast<char>(u>>8));}
int main(){
    constexpr unsigned sr=48000;
    // I/Q stereo, three active carriers, intentionally absent 400 Hz target.
    for(int grid:{0,1}){Forge e;e.restore({1,1,0,1,1,0});e.reset(sr);std::ofstream dry(grid?"sidon-dry.pcm":"collision-dry.pcm",std::ios::binary),wet(grid?"sidon-wet.pcm":"collision-wet.pcm",std::ios::binary);for(unsigned n=0;n<sr*2;++n){double l=0,r=0;double env=std::min({1.,n/480.,(sr*2-1-n)/480.});for(double f:{480.,720.,grid?880.:800.}){double phase=2*pi*f*n/sr;l+=.18*env*std::cos(phase);r+=.18*env*std::sin(phase);}auto y=e.process(l,r);sample(dry,l);sample(dry,r);sample(wet,y[0]);sample(wet,y[1]);}}
    // Musical stereo with overlapping original decaying notes; shared versus cross-only.
    Forge full,cross;full.restore({.95f,1,0,1,.65f,0});cross.restore({1,1,1,1,1,0});full.reset(sr);cross.reset(sr);
    std::ofstream dry("stereo-dry.pcm",std::ios::binary),wet("stereo-shared.pcm",std::ios::binary),delta("stereo-cross.pcm",std::ios::binary);
    for(unsigned n=0;n<sr*4;++n){double t=double(n)/sr;double q=std::fmod(t,.5),env=std::min(1.,q/.006)*std::exp(-7*q)*std::min(1.,(.5-q)/.006);unsigned k=n/(sr/2);double l=.36*env*(std::sin(2*pi*(110.+27.5*(k%4))*t)+.3*std::sin(2*pi*440*t));double r=.36*env*(std::sin(2*pi*(164.81+41.2*(k%3))*t)+.3*std::sin(2*pi*659.25*t));auto y=full.process(l,r),z=cross.process(l,r);for(auto p:{std::pair<std::ofstream*,std::array<double,2>>{&dry,{l,r}},{&wet,y},{&delta,z}}){sample(*p.first,p.second[0]);sample(*p.first,p.second[1]);}}
    Forge bench;double sum=0;auto begin=std::chrono::steady_clock::now();for(unsigned n=0;n<4000000;++n){if(n%1024==0)bench.set(Drive,(n/1024)%2);auto y=bench.process(.25,-.3);sum+=y[0];}std::cout<<std::setprecision(10)<<"4M stereo double frames seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<" checksum="<<sum<<'\n';
}
