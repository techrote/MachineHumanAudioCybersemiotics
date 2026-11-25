#include "live.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
namespace L=loom::live;
void check(bool v){if(!v){std::cerr<<"failure\n";std::exit(1);}}
void word(std::ofstream& o,unsigned v,int n){for(int i=0;i<n;++i)o.put(char((v>>(8*i))&255));}
void demo(const std::string& path,bool swap){
    L::Engine e;check(e.prepare(48000));auto p=L::defaults;p[4]=1;p[0]=.5;p[1]=(.16-.025)/1.975;
    for(unsigned i=0;i<16;++i)p[5+i]=double(swap&&i%2==0);
    std::ofstream o(path,std::ios::binary);unsigned n=192000*4;
    o.write("RIFF",4);word(o,36+n,4);o.write("WAVEfmt ",8);word(o,16,4);word(o,1,2);word(o,2,2);word(o,48000,4);word(o,192000,4);word(o,4,2);word(o,16,2);o.write("data",4);word(o,n,4);
    for(int i=0;i<192000;++i){if(i==0)e.on(1,48,0,.9,p);if(i==12000)e.on(2,55,0,.8,p);if(i==24000)e.on(3,64,0,.7,p);if(i==160000){e.off(1);e.off(2);e.off(3);}auto x=e.tick();word(o,unsigned(std::lround(x.l*32767)),2);word(o,unsigned(std::lround(x.r*32767)),2);}check(bool(o));
}
int main(int argc,char** argv){
    auto old=loom::defaults;old[3]=1;auto legacy=loom::encode(old);L::Params p{};check(L::decode(legacy.data(),legacy.size(),p));check(p[3]==1&&p[4]==0&&L::mask(p)==0);p[4]=1;p[5]=1;p[20]=1;check(L::mask(p)==0x8001);auto s=L::encode(p);L::Params q{};check(L::decode(s.data(),s.size(),q)&&L::encode(q)==s);check(!L::decode(s.data(),s.size()-1,q));auto bad=s;bad[4+4*5]=0;bad[5+4*5]=0;bad[6+4*5]=0;bad[7+4*5]=63;check(!L::decode(bad.data(),bad.size(),q)&&L::encode(q)==s);
    std::uint64_t frames=0;double peak=0;
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,384000.,1234567.8,2000000.}){
        L::Engine a,b;check(a.prepare(sr)&&b.prepare(sr));auto z=L::defaults;z[1]=0;z[0]=.75;z[4]=1;auto w=z;w[5]=1;w[20]=1;check(a.on(1,69,0,.9,z)&&b.on(1,69,0,.9,w));
        auto period=std::llround(.025*sr);for(std::int64_t i=0;i<3*period+std::llround(.05*sr);++i){if(i==3*period){a.off(1);b.off(1);}auto x=a.tick(),y=b.tick();check(x.l+x.r==y.l+y.r);check(i<period?(x.l==y.l&&x.r==y.r):(x.l==y.r&&x.r==y.l));peak=std::max(peak,std::abs(x.l-y.l));++frames;}check(a.tick().l==0&&b.tick().r==0);
    }
    check(peak>.01);
    loom::Engine original;L::Engine upgraded;check(original.prepare(48000)&&upgraded.prepare(48000));auto patch=L::defaults;patch[3]=1;patch[1]=0;loom::Params op{patch[0],patch[1],patch[2],patch[3]};check(original.on(1,60,0,.9,loom::patch(op))&&upgraded.on(1,60,0,.9,patch));patch[4]=1;patch[5]=1;
    for(int i=0;i<10000;++i){if(i==5000){original.off(1);upgraded.off(1);}auto a=original.tick(),b=upgraded.tick();check(a.l==b.l&&a.r==b.r);}
    L::Engine a,b;check(!a.prepare(NAN)&&!a.prepare(999)&&a.prepare(48000)&&b.prepare(48000));for(int i=0;i<8;++i){patch[4]=double(i%2);check(a.on(i,60+i,0,1,patch)&&b.on(i,60+i,0,1,patch));}check(!a.on(8,60,0,1,patch)&&!a.on(0,60,0,1,patch));std::array<float,1024> l{},r{},ll{},rr{};a.render(l.data(),r.data(),1024);for(int i=0;i<1024;i+=17)b.render(ll.data()+i,rr.data()+i,std::min(17,1024-i));check(l==ll&&r==rr);for(auto v:l)check(std::isfinite(v)&&std::abs(v)<=.4f);for(auto v:r)check(std::isfinite(v)&&std::abs(v)<=.4f);a.reset();a.render(l.data(),static_cast<float*>(nullptr),1024);for(auto v:l)check(v==0);
    std::cout<<"paired frames="<<frames<<" max stereo delta="<<peak<<"; legacy, mixed voices, state, partition PASS\n";
    if(argc>1){std::string d=argv[1];demo(d+"/chord-cross.wav",false);demo(d+"/chord-score.wav",true);}
}
