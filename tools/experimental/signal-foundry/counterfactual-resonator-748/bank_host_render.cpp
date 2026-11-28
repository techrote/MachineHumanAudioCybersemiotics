#include "bank_host.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace mhac::counterfactual;
namespace bh=mhac::counterfactual::bankhost;
static constexpr double pi=3.14159265358979323846;
int main(int argc,char** argv){
    if(argc!=2){std::cerr<<"usage: bank_host_render output-directory\n";return 1;}
    const char* names[]={"broad-retain.wav","selective-retain.wav","broad-discard.wav","selective-discard.wav"};
    for(unsigned j=0;j<4;++j){
        bh::Host h;MemoryConfig c{};c.wet=1000;
        for(auto& b:c.bands){b.gain=800;b.peakMix=1000;b.excite=false;}
        c.bands[0].hz=250;c.bands[1].hz=900;
        for(unsigned k=0;k<2;++k){c.bands[k].excite=true;c.bands[k].selectivity=(j%2)?1000:0;c.bands[k].discardOnClose=j>=2;}
        if(!h.request(bh::encode(c))||!h.prepare(48000))return 2;
        std::ofstream f(std::string(argv[1])+"/"+names[j],std::ios::binary);
        const auto u=[&](unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));};
        constexpr unsigned frames=144000, bytes=frames*4;
        f.write("RIFF",4);u(36+bytes,4);f.write("WAVEfmt ",8);u(16,4);u(1,2);u(2,2);u(48000,4);u(192000,4);u(4,2);u(16,2);f.write("data",4);u(bytes,4);
        std::array<double,127> l{},r{};
        for(unsigned start=0;start<frames;){const unsigned n=std::min(127u,frames-start);
            std::array<bh::Event,8> ev{};unsigned m=0;
            for(unsigned i=0;i<n;++i){const unsigned t=start+i;l[i]=t<24000?0.35*std::sin(2*pi*250*t/48000):0;r[i]=0;
                if(t==24000||t==96000)for(unsigned k=0;k<4;++k){const unsigned id=bh::FirstBand+k*bh::Stride;ev[m++]={i,id+bh::Excite,0};ev[m++]={i,id+bh::Erase,t==96000?1.0:0.0};}}
            if(!h.process(l.data(),r.data(),l.data(),r.data(),n,ev.data(),m))return 3;
            for(unsigned i=0;i<n;++i){if(r[i]!=0||(start+i>=120000&&l[i]!=0))return 4;
                for(double v:{l[i],r[i]})u(static_cast<unsigned>(static_cast<int>(std::round(v*32767))),2);}
            start+=n;
        }
        if(!f)return 5;
        std::cout<<names[j]<<" rendered via HM01 and sample-offset automation\n";
    }
}
