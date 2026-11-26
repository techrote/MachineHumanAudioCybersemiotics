// Offline diagnostics only. No clocks or logging are added to the plugin.
#include "live.hpp"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>
#include <string>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <time.h>
#endif
using namespace mhac::afterimage::live;
using Clock=std::chrono::steady_clock;
static void require(bool ok){if(!ok){std::fprintf(stderr,"deadline probe failed\n");std::exit(1);}}
static double cpuUs(){
#if defined(_WIN32)
    FILETIME c,e,k,u;require(GetThreadTimes(GetCurrentThread(),&c,&e,&k,&u)!=0);
    ULARGE_INTEGER a{},b{};a.LowPart=k.dwLowDateTime;a.HighPart=k.dwHighDateTime;
    b.LowPart=u.dwLowDateTime;b.HighPart=u.dwHighDateTime;
    return double(a.QuadPart+b.QuadPart)*.1;
#else
    timespec t{};require(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)==0);
    return double(t.tv_sec)*1e6+double(t.tv_nsec)*.001;
#endif
}
struct Sample {unsigned start,count,onsets;double wall,cpu,peak;};
struct Workload {
    Live engine;unsigned next=8,epoch=0,interval;
    Workload(unsigned sr,unsigned level):interval(sr*6/1000){
        require(engine.prepare(sr)&&engine.applyPatch(pack(16,3,0,1000,3,level)));
        for(int p:{57,59,62})require(engine.on(p,p,0,1)&&engine.off(p)&&engine.tick()==0);
        for(int i=0;i<8;++i)require(engine.on(i,36+i,0,1));
        for(unsigned i=0;i<sr/100;++i)engine.tick();
    }
    unsigned render(unsigned start,unsigned count,double* out){
        unsigned onsets=0;
        for(unsigned i=0;i<count;++i){
            if((start+i)%interval==0){
                for(unsigned k=0;k<8;++k)require(engine.on(static_cast<int>(next++),36+static_cast<int>((k+epoch)%12),0,1));
                ++epoch;onsets+=8;
            }
            out[i]=engine.tick();
        }
        return onsets;
    }
};
static void run(unsigned sr,unsigned block,unsigned level,unsigned frames,bool csv){
    Workload measured(sr,level),reference(sr,level);
    std::vector<Sample> samples;samples.reserve((frames+block-1)/block);
    std::vector<double> a(block),b(block);
    for(unsigned start=0;start<frames;start+=block){
        const unsigned count=std::min(block,frames-start);
        const auto w0=Clock::now();const double c0=cpuUs();
        const unsigned onsets=measured.render(start,count,a.data());
        const double c1=cpuUs();const auto w1=Clock::now();
        const double wall=std::chrono::duration<double,std::micro>(w1-w0).count(),cpu=c1-c0;
        require(wall>=0&&cpu>=0);double peak=0;
        require(reference.render(start,count,b.data())==onsets);
        for(unsigned i=0;i<count;++i){require(a[i]==b[i]&&std::isfinite(a[i])&&std::abs(a[i])<=.52);peak=std::max(peak,std::abs(a[i]));}
        samples.push_back({start,count,onsets,wall,cpu,peak});
    }
    measured.engine.reset();reference.engine.reset();require(measured.engine.tick()==0&&reference.engine.tick()==0);
    if(csv)for(const auto& s:samples)std::printf("%u,%u,%u,%u,%u,%u,%.6f,%.6f,%.6f,%.9f\n",sr,block,level,s.start,s.count,s.onsets,s.wall,s.cpu,double(s.count)*1e6/sr,s.peak);
}
int main(int argc,char** argv){
    const bool self=argc==2&&std::string(argv[1])=="--self-test";
    const bool full=argc==2&&std::string(argv[1])=="--csv";
    if(!self&&!full){std::fprintf(stderr,"usage: deadline_probe --self-test|--csv\n");return 2;}
    // A positive control: sleeping consumes wall time, not thread execution time.
    const auto w0=Clock::now();const double c0=cpuUs();
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
    const double c1=cpuUs();const auto w1=Clock::now();
    const double wall=std::chrono::duration<double,std::micro>(w1-w0).count();
    std::fprintf(stderr,"sleep control: wall %.3f us, thread CPU %.3f us\n",wall,c1-c0);
    require(wall>=20000&&c1>=c0);
    if(full)std::puts("rate,block,phase,start,count,onsets,wall_us,cpu_us,budget_us,peak");
    for(unsigned sr:{44100u,48000u,96000u})for(unsigned block:{32u,64u,257u,1024u})for(unsigned phase:{0u,1u,2u,3u})
        run(sr,block,phase,self?sr/25+1:sr*2+1,full);
    std::fprintf(stderr,"PASS 48 rate/block/phase configurations; exact untimed twin, bounds and reset\n");
}
