// Refs #632; native audition, not VST3/DAW or human evidence.
// Include only pinned external headers; no vendored dependency.
#include "afterimage.hpp"
#include "receipt_live.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
namespace ac=mhac::afterimage;
namespace rf=mhac::receipt;
using Signal=std::vector<float>;
void need(bool x){if(!x)throw std::runtime_error("chain invariant failed");}
Signal render(unsigned rate,unsigned block,ac::Mode memory,rf::Mode receipt,bool bypass,double drive){
    ac::Engine synth;rf::Live effect;
    need(synth.prepare(rate)&&synth.configure({{2,6},memory,80,.8}));
    need(effect.prepare(rate)&&effect.apply({{2,4},receipt,bypass,.65}));
    Signal out;out.reserve(3*rate);
    for(unsigned pos=0;pos<3*rate;){
        const unsigned end=std::min(pos+block,3*rate);
        for(;pos<end;++pos){
            if(pos==rate/10)need(synth.on(1,62,.8));
            if(pos==rate*8/10){need(synth.off(1));need(synth.remembered()==(memory==ac::Mode::fixed?2u:6u));}
            if(pos==rate)need(synth.on(2,60,.8));
            if(pos==rate*17/10)need(synth.off(2));
            if(pos==rate*19/10){need(synth.on(3,60,.8));need(synth.on(4,64,.8));need(synth.on(5,67,.8));}
            if(pos==rate*26/10){need(synth.off(3));need(synth.off(4));need(synth.off(5));}
            const double dry=synth.tick()*drive;
            need(std::isfinite(dry)&&std::abs(dry)<=1);
            float l=static_cast<float>(dry),r=l;
            effect.frame(l,r);
            need(l==r&&std::isfinite(l)&&std::abs(l)<=1);
            if(bypass)need(l==static_cast<float>(dry));
            if(pos<rate/10||pos>=rate*27/10)need(l==0);
            out.push_back(l);
        }
    }
    need(synth.active()==0);return out;
}
void raw(const std::filesystem::path& p,const Signal& x){
    std::ofstream f(p,std::ios::binary);f.write(reinterpret_cast<const char*>(x.data()),static_cast<std::streamsize>(x.size()*sizeof(float)));need(bool(f));
}
int main(int argc,char** argv){try{
    need(argc<=2);unsigned cases=0;std::uint64_t frames=0;
    for(unsigned rate:{44100u,48000u,96000u})for(double drive:{1.,3.}){
        Signal previous;
        for(auto mem:{ac::Mode::fixed,ac::Mode::preview}){
            std::array<Signal,5> results;
            for(unsigned mode=0;mode<5;++mode){
                const auto m=static_cast<rf::Mode>(mode%4);const bool bypass=mode==4;
                auto x=render(rate,257,mem,m,bypass,drive);
                need(x==render(rate,1024,mem,m,bypass,drive));frames+=x.size();++cases;
                if(argc==2&&rate==48000&&drive==1.){
                    std::filesystem::create_directories(argv[1]);
                    raw(std::filesystem::path(argv[1])/(std::string(mem==ac::Mode::fixed?"fixed":"preview")+"-"+std::to_string(mode)+".f32"),x);
                }
                results[mode]=std::move(x);
            }
            // Pair (2,4) collides under both no receipt and parity; preview/full resolve it.
            need(results[0]==results[1]&&results[2]==results[3]&&results[0]!=results[2]&&results[2]!=results[4]);
            if(!previous.empty())need(previous!=results[4]);
            previous=std::move(results[4]);
        }
    }
    std::cout<<cases<<" partition-paired cases, "<<frames<<" exact frames; bounds, silence, stereo, history and receipt equivalences PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
