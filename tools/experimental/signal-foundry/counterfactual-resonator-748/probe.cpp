#include "resonator.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::counterfactual;
namespace {
unsigned checks=0;
void require(bool ok){++checks;if(!ok){std::cerr<<"FAIL probe "<<checks<<'\n';std::exit(1);}}
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
struct Wav {
    std::ofstream f;
    explicit Wav(const std::string& path,unsigned n):f(path,std::ios::binary){require(bool(f));f.write("RIFF",4);word(f,36+n*4,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,48000,4);word(f,192000,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,n*4,4);}
    void write(Stereo s){for(double x:{s.left,s.right})word(f,static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(std::clamp(x,-1.0,1.0)*32767))),2);}
};
struct Stats {
    double peak=0,energy=0,tail=0;
    void add(Stereo s,unsigned i){for(double x:{s.left,s.right}){peak=std::max(peak,std::abs(x));energy+=x*x;if(i>=93600)tail+=x*x;}}
};
void impulse(){
    // A one-sample full-scale impulse cannot excite the 250 Hz / 48 kHz averaged-drive lattice.
    // At 6 kHz it injects 3 units instead; this is a retained negative control, not ideal impulse fidelity.
    for(unsigned hz:{250u,6000u}){
        Controls c{static_cast<std::uint16_t>(hz),1000,1000,1,false,false};Processor p;require(p.set(c)&&p.prepare(48000));double peak=0;
        for(unsigned i=0;i<4800;++i){auto s=p.process(i==0?1:0,0);peak=std::max(peak,std::abs(s.left));require(s.right==0);}
        require(hz==250?peak==0:peak==3.0/16);std::cout<<"impulse_hz="<<hz<<",peak="<<peak<<'\n';
    }
}
void sweep(const std::string& dir){
    constexpr unsigned n=96000;constexpr double pi=3.14159265358979323846;
    Processor reference,discrete,residual,intervened;Controls c{250,1000,800,0,false,false};require(reference.set(c)&&intervened.set(c));c.monitor=1;require(discrete.set(c));c.monitor=2;require(residual.set(c));for(auto* p:{&reference,&discrete,&residual,&intervened})require(p->prepare(48000));
    // Always exercise the same numerical oracle; WAV output is optional and outside DSP.
    const bool render=!dir.empty();std::array<Stats,4> stats{};
    const auto run=[&](Wav* dry,Wav* ref,Wav* quantized,Wav* diff){
        for(unsigned i=0;i<n;++i){const double t=double(i)/48000.0;const double angle=2*pi*40.0*std::expm1(std::log(300.0)*t)/std::log(300.0);const Stereo input=i<48000?Stereo{0.8*std::sin(angle),0.8*std::sin(angle+pi/2)}:Stereo{};
            const auto a=reference.process(input.left,input.right),b=discrete.process(input.left,input.right),d=residual.process(input.left,input.right);
            auto p=intervened.controls();p.erase=(i%113)<53;require(intervened.set(p));if(i%37==0)intervened.requestIntervention();const auto e=intervened.process(input.left,input.right);
            require(a.left==e.left&&a.right==e.right);require(std::abs(d.left-0.5*(b.left-a.left))<1e-14&&std::abs(d.right-0.5*(b.right-a.right))<1e-14);
            require(std::isfinite(a.left)&&std::isfinite(b.left)&&std::isfinite(d.left)&&std::abs(a.left)<=1&&std::abs(b.left)<=1&&std::abs(d.left)<=1);
            stats[0].add(input,i);stats[1].add(a,i);stats[2].add(b,i);stats[3].add(d,i);if(dry){dry->write(input);ref->write(a);quantized->write(b);diff->write(d);}
        }
    };
    if(render){Wav dry(dir+"/Audio/sweep-dry.wav",n),ref(dir+"/Audio/sweep-reference.wav",n),quantized(dir+"/Audio/sweep-persistent.wav",n),diff(dir+"/Audio/sweep-residual.wav",n);run(&dry,&ref,&quantized,&diff);require(bool(dry.f)&&bool(ref.f)&&bool(quantized.f)&&bool(diff.f));}else run(nullptr,nullptr,nullptr,nullptr);
    require(stats[1].tail==0);require(stats[3].energy>0);const char* names[]={"sweep-dry","sweep-reference","sweep-persistent","sweep-residual"};for(unsigned i=0;i<4;++i)std::cout<<names[i]<<",peak="<<stats[i].peak<<",rms="<<std::sqrt(stats[i].energy/(2*n))<<",final50ms_rms="<<std::sqrt(stats[i].tail/4800)<<'\n';
}
void transition(){
    // Bypass does not clear the persistent state, and zero-wet becomes exactly dry.
    Processor p;Controls c{250,1000,1000,1,false,false};require(p.set(c)&&p.prepare(48000));for(unsigned i=0;i<48;++i)p.process(0.5,0);for(unsigned i=0;i<4800;++i)p.process(0,0);c.bypass=true;require(p.set(c));for(unsigned i=0;i<241;++i)p.process(0,0);const auto s=p.process(0.375,-0.25);require(s.left==0.375&&s.right==-0.25);const auto state=p.lattice(0);require(state.x!=0||state.y!=0);p.reset();require(p.lattice(0).x==0&&p.lattice(0).y==0&&p.ticks()==0);
}
}
int main(int argc,char** argv){impulse();transition();sweep(argc==3&&std::string(argv[1])=="--render"?argv[2]:"");std::cout<<"PASS "<<checks<<" probe checks\n";}
