#include "splitter.hpp"
#include <fstream>
#include <iostream>
#include <string>
#include <stdexcept>
#include <vector>
using namespace mhac::splitter;
using Frame=std::array<double,2>;
void word(std::ofstream& f,std::uint32_t x,unsigned n){for(unsigned i=0;i<n;++i)f.put(char(x>>(8*i)));}
void wav(const std::string& name,const std::vector<Frame>& x){
    std::ofstream f(name,std::ios::binary);f.write("RIFF",4);word(f,36+4*unsigned(x.size()),4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,48000,4);word(f,192000,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,4*unsigned(x.size()),4);
    for(auto a:x)for(double v:a)word(f,std::uint16_t(std::lround(v*32767)),2);if(!f)throw std::runtime_error("WAV write failed");
}
int main(){
    constexpr unsigned n=144000;constexpr double pi=3.14159265358979323846;
    std::vector<Frame> dry(n+1024),out(n+1024),rec(n+1024);double phase=0;
    for(unsigned i=0;i<n;++i){double t=i/48000.,env=std::min({1.,t*100,(3.-t)*100});phase+=2*pi*80*std::pow(100.,t/3)/48000.;dry[i][0]=std::round(8192*env*(.7*std::sin(phase)+.3*std::sin(2*pi*173*t)))/32768.;}
    wav("dry.wav",dry);
    for(unsigned k:{0u,2u}){Engine a,b;a.set(Delay,k/3.);b.set(Delay,k/3.);a.set(Mix,1);b.set(Mix,1);b.set(Inverse,1);a.reset(48000);b.reset(48000);double input=0,output=0,error=0,peak=0;
        for(unsigned i=0;i<dry.size();++i){out[i]=a.process(dry[i][0],dry[i][1]);rec[i]=b.process(out[i][0],out[i][1]);for(unsigned c=0;c<2;++c){input+=dry[i][c]*dry[i][c];output+=out[i][c]*out[i][c];error=std::max(error,std::abs(rec[i][c]-(i>=delays[k]?dry[i-delays[k]][c]:0)));peak=std::max(peak,std::abs(out[i][c]));}}
        std::cout<<delays[k]<<" samples: energy delta "<<output-input<<", max reconstruction error "<<error<<", peak "<<peak<<'\n';wav("split-"+std::to_string(delays[k])+".wav",out);if(k==2)wav("reconstructed-256.wav",rec);
    }
}
