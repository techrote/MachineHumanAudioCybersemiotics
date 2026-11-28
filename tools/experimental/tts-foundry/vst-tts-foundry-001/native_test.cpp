#include "logos.hpp"
#include "articulum.hpp"
#include <stdexcept>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <vector>

using namespace mhac::tts;

static void need(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}

static std::uint64_t hash_samples(const std::vector<double>& x){
    std::uint64_t h=1469598103934665603ull;
    for(double v:x){
        const auto q=static_cast<std::int32_t>(std::llround(std::clamp(v,-1.0,1.0)*1000000.0));
        for(int i=0;i<4;++i){h^=std::uint8_t((std::uint32_t(q)>>(8*i))&255u);h*=1099511628211ull;}
    }
    return h;
}

template<class Engine, class Setup>
static std::vector<double> render(double sr, unsigned block, Setup setup){
    Engine e; need(e.prepare(sr),"prepare"); setup(e); e.note_on(60.0,.8);
    const std::size_t n=static_cast<std::size_t>(sr*2.0); std::vector<double> out; out.reserve(n);
    for(std::size_t i=0;i<n;){
        e.begin_block(); const auto m=std::min<std::size_t>(block,n-i);
        for(std::size_t j=0;j<m;++j){const double y=e.tick();need(std::isfinite(y),"nonfinite sample");need(std::abs(y)<=1.000001,"sample bound");out.push_back(y);}i+=m;
    }
    return out;
}

int main(){
    const auto p=compile_text("The word grows its own mouth! 123"); need(p.valid(),"phonetic plan valid"); need(p.count>8,"phonetic plan population");
    const auto empty=compile_text("1234 !!!"); need(empty.valid(),"fallback plan valid"); need(empty.count==1,"fallback pause");
    for(double sr:{44100.0,48000.0,96000.0}){
        for(unsigned block:{1u,64u,511u}){
            auto l1=render<Logos>(sr,block,[](Logos& e){LogosParameters p{};p.rate=1.13f;p.whisper=.12f;p.formantShiftSemitones=-2.f;e.set_parameters(p);e.set_plan(compile_text("machine voice becomes song"));});
            auto l2=render<Logos>(sr,block,[](Logos& e){LogosParameters p{};p.rate=1.13f;p.whisper=.12f;p.formantShiftSemitones=-2.f;e.set_parameters(p);e.set_plan(compile_text("machine voice becomes song"));});
            need(hash_samples(l1)==hash_samples(l2),"LOGOS determinism");
            auto a1=render<Articulum>(sr,block,[](Articulum& e){ArticulumParameters p{};p.tongueFront=.7f;p.tongueHeight=.62f;p.lipRound=.38f;p.nasal=.12f;e.set_parameters(p);});
            auto a2=render<Articulum>(sr,block,[](Articulum& e){ArticulumParameters p{};p.tongueFront=.7f;p.tongueHeight=.62f;p.lipRound=.38f;p.nasal=.12f;e.set_parameters(p);});
            need(hash_samples(a1)==hash_samples(a2),"ARTICULUM determinism");
            double ep=0;for(double v:l1)ep+=v*v;need(ep>1e-5,"LOGOS energy");
            ep=0;for(double v:a1)ep+=v*v;need(ep>1e-5,"ARTICULUM energy");
        }
    }
    Logos live;need(live.prepare(48000),"live prepare");live.set_plan(compile_text("first phrase"));live.note_on(64,.7);double before=0,after=0;
    for(int i=0;i<24000;++i){if(i==12000){need(live.enqueue_plan(compile_text("second altered phrase")),"live phrase enqueue");}if((i%256)==0)live.begin_block();const double y=live.tick();if(i<12000)before+=std::abs(y);else after+=std::abs(y);}need(before>1&&after>1,"live phrase energy");
    Articulum longrun;need(longrun.prepare(384000),"longrun prepare");longrun.note_on(48,.9);for(int i=0;i<384000;++i){const double y=longrun.tick();need(std::isfinite(y)&&std::abs(y)<=1.000001,"longrun stability");}
    std::cout << "VST-TTS-FOUNDRY native PASS: phonetics, deterministic multi-rate/block render, live phrase mailbox, long-run tract stability\n";
}
