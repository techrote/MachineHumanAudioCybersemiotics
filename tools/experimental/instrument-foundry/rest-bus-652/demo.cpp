#include "rest.hpp"
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace restbus;
void u16(std::ostream& s,unsigned v){s.put(char(v));s.put(char(v>>8));}
void u32(std::ostream& s,unsigned v){u16(s,v);u16(s,v>>16);}
int main(){
    constexpr unsigned sr=48000, unit=14400, hold=9600;
    const std::array<std::array<unsigned,4>,4> gaps{{{{12,0,0,0}},{{3,3,3,3}},{{0,4,4,4}},{{3,3,3,3}}}};
    for(unsigned k=0;k<4;++k){Engine e;e.prepare(sr);if(k==3)e.domain(Domain::manual);std::vector<std::int16_t> pcm;
        auto render=[&](unsigned n){for(unsigned i=0;i<n;++i)pcm.push_back(std::int16_t(std::lround(e.tick()*32767)));};
        std::cout<<"score "<<k<<":";
        for(unsigned j=0;j<4;++j){render(gaps[k][j]*unit);std::cout<<' '<<e.index();if(!e.on(int(j),57,0,1))return 1;render(hold);e.off(int(j));}
        render(2400);std::cout<<'\n';
        std::ofstream s("rest-"+std::to_string(k)+".wav",std::ios::binary);s.write("RIFF",4);u32(s,36+unsigned(pcm.size()*2));s.write("WAVEfmt ",8);u32(s,16);u16(s,1);u16(s,1);u32(s,sr);u32(s,sr*2);u16(s,2);u16(s,16);s.write("data",4);u32(s,unsigned(pcm.size()*2));for(auto v:pcm)u16(s,std::uint16_t(v));if(!s)return 2;
    }
}
