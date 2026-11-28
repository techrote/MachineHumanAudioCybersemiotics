#include "axis_memory.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace mhac::counterfactual;
static void require(bool ok,const char* msg){if(!ok){std::cerr<<msg<<'\n';std::exit(1);}}
static void put(std::ostream& o,unsigned x,unsigned n){for(unsigned i=0;i<n;++i)o.put(static_cast<char>((x>>(8*i))&255));}
static void wav(const std::string& path,const std::vector<Stereo>& v,unsigned rate){
    std::ofstream o(path,std::ios::binary);const auto bytes=static_cast<unsigned>(v.size()*4);
    o.write("RIFF",4);put(o,36+bytes,4);o.write("WAVEfmt ",8);put(o,16,4);put(o,1,2);put(o,2,2);put(o,rate,4);put(o,rate*4,4);put(o,4,2);put(o,16,2);o.write("data",4);put(o,bytes,4);
    for(auto x:v){for(double y:{x.left,x.right})put(o,static_cast<unsigned>(static_cast<int>(std::lround(y*32767))),2);}require(bool(o),"WAV write");
}
static std::vector<Stereo> render(unsigned rate,unsigned mode,unsigned block){
    AxisMemory p;Controls m,s;m.hz=220;s.hz=330;m.gain=s.gain=500;m.peakMix=s.peakMix=1000;
    require(p.configure(m,s,1000)&&p.prepare(rate),"prepare");
    std::vector<Stereo> out(2*rate);std::vector<double> l(block),r(block),ol(block),orr(block);
    const unsigned trigger=rate,stop=rate/2;
    for(unsigned i=0;i<out.size();){
        if(i==trigger){if(mode&1)require(p.eraseMid(),"mid admission");if(mode&2)require(p.eraseSide(),"side admission");}
        unsigned n=std::min(block,static_cast<unsigned>(out.size())-i);if(i<trigger)n=std::min(n,trigger-i);
        for(unsigned j=0;j<n;++j){const unsigned t=i+j;const double a=t<stop?0.45*std::sin(6.283185307179586*220*t/rate):0;const double b=t<stop?0.45*std::sin(6.283185307179586*330*t/rate):0;l[j]=a+b;r[j]=a-b;}
        p.processBlock(l.data(),r.data(),ol.data(),orr.data(),n);
        for(unsigned j=0;j<n;++j){require(std::isfinite(ol[j])&&std::isfinite(orr[j])&&std::abs(ol[j])<=1&&std::abs(orr[j])<=1,"bounds");out[i+j]={ol[j],orr[j]};}i+=n;
    }
    require(bool(magnitude(p.midState()))==!(mode&1),"mid tail state");require(bool(magnitude(p.sideState()))==!(mode&2),"side tail state");
    require(bool(p.midInterventions())==bool(mode&1)&&bool(p.sideInterventions())==bool(mode&2),"intervention isolation");
    return out;
}
int main(int argc,char** argv){
    for(unsigned rate:{44100u,48000u,96000u}){
        auto base=render(rate,0,1);double em=0,es=0;
        for(unsigned mode=0;mode<4;++mode){auto a=render(rate,mode,1),b=render(rate,mode,257),c=render(rate,mode,1024);
            for(unsigned i=0;i<a.size();++i){require(a[i].left==b[i].left&&a[i].right==b[i].right&&a[i].left==c[i].left&&a[i].right==c[i].right,"partition");
                if(i<rate)require(a[i].left==base[i].left&&a[i].right==base[i].right,"prefix");
                if(i>=rate+rate/4){const double m=a[i].left+a[i].right,s=a[i].left-a[i].right;
                    require(std::abs(m-((mode&1)?0:base[i].left+base[i].right))<1e-15,"mid oracle");require(std::abs(s-((mode&2)?0:base[i].left-base[i].right))<1e-15,"side oracle");if(mode==0){em+=m*m;es+=s*s;}}
            }
            if(argc==2&&rate==48000)wav(std::string(argv[1])+"/axis-"+std::to_string(mode)+".wav",a,rate);
        }
        require(em>0&&es>0,"nontrivial persistent axes");std::cout<<rate<<" mid energy "<<em<<" side energy "<<es<<'\n';
        AxisMemory p;Controls x;require(p.configure(x,x,0)&&p.prepare(rate),"dry setup");auto z=p.process(.2,-.4);require(z.left==.2&&z.right==-.4,"dry exact");
        require(!p.configure(x,x,1001)&&!p.prepare(0),"invalid controls");z=p.process(std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN());require(z.left==0&&z.right==0,"nonfinite");p.reset();z=p.process(0,0);require(z.left==0&&z.right==0,"reset");
    }
    std::cout<<"AXIS_MEMORY_PASS cases=12 partitions=3\n";
}
