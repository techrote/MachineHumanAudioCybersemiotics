#include "state.hpp"
#include <iostream>
#include <stdexcept>
using namespace mhac::tts;
static void need(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
int main(){
    auto a=logosDefaults; auto b=encode_logos(a); LogosPatch c{};
    need(decode_logos(b,c)&&c==a,"LOGOS roundtrip");
    b[0]='X'; need(!decode_logos(b,c),"LOGOS corrupt magic refusal");
    auto d=articulumDefaults; auto e=encode_articulum(d); ArticulumPatch f{};
    need(decode_articulum(e,f)&&f==d,"ARTICULUM roundtrip");
    e[1]='X'; need(!decode_articulum(e,f),"ARTICULUM corrupt magic refusal");
    std::cout<<"VST-TTS-FOUNDRY state PASS\n";
}
