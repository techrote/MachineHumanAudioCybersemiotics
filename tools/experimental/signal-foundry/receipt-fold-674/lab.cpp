#include "receipt_fold.hpp"
#include <array>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <fstream>
#include <string>
#include <type_traits>
using namespace mhac::receipt;
static void check(bool ok) { if(!ok) std::abort(); }
static void put(std::ofstream& f,unsigned v,unsigned n) { for(unsigned j=0;j<n;++j) f.put(static_cast<char>((v>>(8*j))&255)); }
static void demo(Mode m,const char* name) {
    constexpr unsigned n=48000*3;
    std::ofstream f(name,std::ios::binary);
    f.write("RIFF",4);put(f,36+4*n,4);f.write("WAVEfmt ",8);put(f,16,4);put(f,1,2);put(f,2,2);put(f,48000,4);put(f,192000,4);put(f,4,2);put(f,16,2);f.write("data",4);put(f,4*n,4);
    Engine e;e.prepare(48000);e.setMode(m);e.setWet(1);
    for(unsigned i=0;i<n;++i){
        if(i%12000==0) {const unsigned k=i/12000; e.setAction(k%4,4+(k*3+k/2)%4);}
        const double t=i/48000.0, env=std::max(0.0,std::min({1.0,t*20,(2.8-t)*20}));
        double l=env*(.65*std::sin(6.283185307179586*110*t)+.18*std::sin(6.283185307179586*330*t)),r=env*.65*std::sin(6.283185307179586*165*t);
        e.frame(l,r);put(f,static_cast<unsigned>(static_cast<int>(l*32767)),2);put(f,static_cast<unsigned>(static_cast<int>(r*32767)),2);
    }
    check(bool(f));
}
template<class T> static void stream() {
    for(double rate:{8000.,44100.,48000.,96000.,192000.,384000.}){
        Engine a,b;a.prepare(rate);b.prepare(rate);a.setWet(1);b.setWet(1);
        for(unsigned i=0;i<4096;++i){
            if(i%97==0){a.setAction(i%8,(i/8)%8);b.setAction(i%8,(i/8)%8);a.setMode(static_cast<Mode>((i/97)%4));b.setMode(static_cast<Mode>((i/97)%4));}
            if(i==2048){a.setWet(0);b.setWet(0);}
            T l=static_cast<T>(std::sin(i*.17)),r=static_cast<T>(std::cos(i*.31)),ll=l,rr=r;
            a.frame(l,r);b.frame(ll,rr);check(l==ll&&r==rr&&std::abs(l)<=1&&std::abs(r)<=1);
            if(i==4095){check(l==static_cast<T>(std::sin(i*.17)));check(r==static_cast<T>(std::cos(i*.31)));}
        }
        T x=std::numeric_limits<T>::infinity(),y=std::numeric_limits<T>::quiet_NaN();a.frame(x,y);check(x==0&&y==0);
        a.setWet(1);for(int j=0;j<2048;++j){x=0;y=0;a.frame(x,y);check(x==0&&y==0);}
    }
}
int main(int argc,char** argv){
    std::array<unsigned,4> errors{},amb{};
    for(unsigned lo=0;lo<8;++lo)for(unsigned hi=lo+1;hi<8;++hi){
        const auto p=pair(lo,hi);
        for(unsigned x=0;x<8;++x)for(unsigned m=0;m<4;++m){
            const auto mode=static_cast<Mode>(m);auto y=decode(collapse(x,p),p,encode(x,mode,hint(p)));
            check(!y.invalid);errors[m]+=y.index!=x;amb[m]+=y.ambiguous;
            if(m>=2) check(y.index==x&&!y.ambiguous);
        }
    }
    check((errors==std::array<unsigned,4>{28,12,0,0}));check((amb==std::array<unsigned,4>{56,24,0,0}));
    check(decode(6,pair(1,6),{0,0}).invalid);check(decode(1,pair(1,6),{8,1}).invalid);
    stream<float>();stream<double>();
    for(unsigned m=0;m<4;++m)std::cout<<m<<": errors="<<errors[m]<<" ambiguous="<<amb[m]<<'\n';
    if(argc==2&&std::string(argv[1])=="--render"){demo(Mode::absent,"absent.wav");demo(Mode::fixed,"fixed.wav");demo(Mode::preview,"preview.wav");demo(Mode::full,"full.wav");}
}
