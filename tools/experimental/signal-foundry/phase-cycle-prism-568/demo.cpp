#include "prism.hpp"
#include <fstream>
#include <cstdint>
#include <iostream>
using namespace prism;
void put(std::ofstream& f,std::uint32_t v,int n){for(int i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
int main(){
    constexpr int sr=48000,frames=sr*2;
    for(int mode=0;mode<3;++mode){
        const char* names[]={"dry.wav","raw.wav","corrected.wav"};std::ofstream f(names[mode],std::ios::binary);
        f.write("RIFF",4);put(f,36+frames*4,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,sr,4);put(f,sr*4,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,frames*4,4);
        Prism p;p.set({1,mode==2?1.:0.,mode==0?0.:1.,.7});if(!p.prepare(sr))return 1;auto n=p.latency();double peak=0;
        for(int t=0;t<frames;++t){C x{};if(t<sr*3/2)for(int j=1;j<4;++j)x+=std::polar(.18,tau*bins[j]*double(t%n)/double(n));auto y=p.step(x.real(),x.imag());
            for(double v:{y.real(),y.imag()}){peak=std::max(peak,std::abs(v));put(f,static_cast<std::uint16_t>(std::lround(v*32767)),2);}}
        if(!f)return 2;
        std::cout<<names[mode]<<" peak="<<peak<<"\n";
    }
}
