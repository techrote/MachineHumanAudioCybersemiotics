#include "host.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <fstream>
#include <thread>
#include <chrono>
#include <string>
using namespace mhac::counterfactual;
namespace h=mhac::counterfactual::host;
namespace {
unsigned checks=0;
void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL peak host "<<checks<<'\n';std::exit(1);}}
void states(){
    Controls a{250,1000,800,1,false,false},b{880,600,500,2,true,true};b.peakMix=1000;
    h::Host host;check(host.request(b)&&host.prepare(48000));
    for(unsigned m=0;m<=1000;++m){
        auto c=a;c.peakMix=static_cast<std::uint16_t>(m);Controls d=b;
        auto s=encodeState(c);check(s.size==(m?14u:12u)&&decodeState(s,d)&&encodeState(d)==s);
        check(encodeState(h::unpack(h::pack(c)))==s);
        check(h::change(d,h::PeakMix,h::normalized(c,h::PeakMix))&&d.peakMix==m);
        check(host.request(s)&&host.save()==s);host.begin();host.end();check(host.save()==s);
    }
    auto s=encodeState(b);check(host.request(b));auto bad=s;bad.bytes[13]=255;
    check(!host.request(bad)&&host.save()==s);bad=s;bad.size=13;check(!host.request(bad)&&host.save()==s);
    bad=s;bad.bytes[3]='1';check(!host.request(bad)&&host.save()==s);
    check(!host.parameter(h::PeakMix,std::numeric_limits<double>::infinity()));
    check(host.request(encode(a)));host.begin();host.end();check(host.save()==encodeState(a)&&host.current().peakMix==0);
    std::atomic<bool> ok{true};std::thread writer([&]{for(unsigned i=0;i<20000;++i){if(!host.request(i%2?a:b))ok=false;auto p=host.save();if(p!=encodeState(a)&&p!=s)ok=false;}});
    for(unsigned i=0;i<20000;++i){host.begin();double l=0,r=0;host.frame(l,r);host.end();auto p=host.save();check(p==encodeState(a)||p==s);}
    writer.join();check(ok.load());
}
void automation(){
    for(double rate:{1000.,1234.568,44100.,48000.,96000.,384000.,1234567.8,2000000.}){
        Controls c{250,1000,800,1,false,false};h::Host a,b;Processor ref;
        check(a.request(c)&&b.request(c)&&a.prepare(rate)&&b.prepare(rate)&&ref.set(c)&&ref.prepare(rate));
        for(unsigned i=0;i<32000;++i){
            if(i%17==0)a.begin();
            if(i%101==0)b.begin();
            if(i%43==0){const unsigned m=(i*31)%1001;check(a.parameter(h::PeakMix,m/1000.0)&&b.parameter(h::PeakMix,m/1000.0)&&ref.setPeakMix(m));}
            const float l=i%131==0?.9f:0,r=i%97==0?-.7f:0;float fl=l,fr=r;double dl=l,dr=r;
            a.frame(fl,fr);b.frame(dl,dr);const auto s=ref.process(l,r);
            check(dl==s.left&&dr==s.right&&fl==static_cast<float>(dl)&&fr==static_cast<float>(dr)&&std::abs(dl)<=1&&std::abs(dr)<=1);
            if(i%17==16)a.end();
            if(i%101==100)b.end();
        }
        a.end();b.end();check(a.save()==b.save()&&a.snapshot().peakMix==ref.peakMix());
    }
}
void word(std::ostream& f,unsigned v,unsigned n){for(unsigned i=0;i<n;++i)f.put(static_cast<char>((v>>(8*i))&255));}
// Canonical component-only VST3 preset for both state versions.
struct Preset {std::array<std::uint8_t,90> bytes{};unsigned size=0;};
Preset wrap(Controls c){
    const auto s=encodeState(c);Preset result;auto& p=result.bytes;
    std::copy_n("VST3",4,p.begin());p[4]=1;std::copy_n("FBC2EF81CA534C7A8B3BC61D9929C901",32,p.begin()+8);
    const unsigned list=48+s.size;p[40]=static_cast<std::uint8_t>(list);std::copy_n(s.bytes.begin(),s.size,p.begin()+48);
    std::copy_n("List",4,p.begin()+list);p[list+4]=1;std::copy_n("Comp",4,p.begin()+list+8);p[list+12]=48;p[list+20]=static_cast<std::uint8_t>(s.size);
    result.size=list+28;return result;
}
bool unwrap(const Preset& p,Controls& out){
    if(p.size!=88&&p.size!=90)return false;
    State s;s.size=p.size-76;std::copy_n(p.bytes.begin()+48,s.size,s.bytes.begin());
    Controls c;if(!decodeState(s,c))return false;
    const auto expected=wrap(c);if(expected.size!=p.size||expected.bytes!=p.bytes)return false;
    out=c;return true;
}
void presets(){
    Controls c{250,1000,800,1,false,false};
    for(unsigned m=0;m<=1000;++m){c.peakMix=static_cast<std::uint16_t>(m);Controls d;check(unwrap(wrap(c),d)&&encodeState(c)==encodeState(d));}
    const auto p=wrap(c);
    for(unsigned i=0;i<p.size;++i)if(i<48||i>=62)for(unsigned bit=0;bit<8;++bit){auto bad=p;bad.bytes[i]^=static_cast<std::uint8_t>(1u<<bit);Controls d;check(!unwrap(bad,d)&&d.peakMix==0);}
}
void render(const std::string& dir){
    for(unsigned m:{0u,250u,1000u}){
        Controls c{250,1000,800,1,false,false};c.peakMix=static_cast<std::uint16_t>(m);h::Host host;check(host.request(encodeState(c))&&host.prepare(48000));
        constexpr unsigned n=96000;std::ofstream f;const auto p=wrap(c);const std::string name="Peak "+std::to_string(m);
        if(!dir.empty()){
            std::ofstream preset(dir+"/Presets/"+name+".vstpreset",std::ios::binary);preset.write(reinterpret_cast<const char*>(p.bytes.data()),static_cast<std::streamsize>(p.size));preset.close();check(bool(preset));
            f.open(dir+"/Audio/"+name+".wav",std::ios::binary);check(bool(f));f.write("RIFF",4);word(f,36+n*4,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,48000,4);word(f,192000,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,n*4,4);
        }
        double peak=0,tail=0;
        for(unsigned i=0;i<n;++i){double l=i==0?1.:0.,r=i==12000?-.8:0.;host.frame(l,r);for(double v:{l,r}){check(std::isfinite(v)&&std::abs(v)<=1);peak=std::max(peak,std::abs(v));if(i>=n-2400)tail+=v*v;if(f.is_open())word(f,static_cast<std::uint16_t>(static_cast<std::int16_t>(std::lround(v*32767))),2);}}
        if(f.is_open()){f.close();check(bool(f));}check(m?peak>0&&tail>0:peak==0&&tail==0);std::cout<<name<<", peak="<<peak<<", tail50ms="<<std::sqrt(tail/4800)<<'\n';
    }
}
void bench(){
    h::Host host;Controls c{250,1000,800,1,false,false};c.peakMix=1000;check(host.request(c)&&host.prepare(96000));double maxUs=0,total=0,checksum=0;unsigned misses=0;constexpr double deadline=32e6/96000;
    for(unsigned b=0;b<4000;++b){auto start=std::chrono::steady_clock::now();host.begin();for(unsigned i=0;i<32;++i){host.parameter(h::PeakMix,((b+i)%1001)/1000.0);double l=i%7==0?.8:0,r=-l;host.frame(l,r);checksum+=l*l+r*r;}host.end();double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();maxUs=std::max(maxUs,us);total+=us;if(us>deadline)++misses;}
    std::cout<<"mean_us="<<total/4000<<" max_us="<<maxUs<<" misses="<<misses<<"/4000 checksum="<<checksum<<'\n';
}
}
int main(int argc,char** argv){check(argc==1||argc==2);states();automation();presets();render(argc==2?argv[1]:"");bench();std::cout<<"PASS "<<checks<<" checks\n";}
