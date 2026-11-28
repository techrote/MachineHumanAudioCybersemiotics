#include "live.hpp"
#include "live2.hpp"
#include <cstdlib>
#include <iostream>
namespace v2=loom2;
using namespace loom;
static void check(bool b,const char* s){if(!b){std::cerr<<s<<'\n';std::exit(1);}}
int main(){
    const Normalized old{0,.25,.6,.9,.8,.7,0};const auto legacy=encode(old);
    v2::Normalized p{};check(v2::decode(legacy.data(),legacy.size(),p),"EL01 migration");
    for(unsigned k=0;k<Count;++k)check(old[k]==p[k],"legacy value");
    check(p[v2::Probe]==0&&p[v2::Edge]==0,"legacy endpoints");
    auto modern=p;modern[v2::Probe]=.7;modern[v2::Edge]=.8;
    const auto b=v2::encode(modern);check(v2::decode(b.data(),b.size(),p)&&p==modern,"EL02 roundtrip");
    for(std::size_t n=0;n<b.size();++n)check(!v2::decode(b.data(),n,p)&&p==modern,"truncation atomic");
    auto bad=modern;bad[v2::Probe]=std::numeric_limits<double>::quiet_NaN();auto corrupt=v2::encode(bad);
    check(!v2::decode(corrupt.data(),corrupt.size(),p)&&p==modern,"NaN state rejection");
    corrupt=b;corrupt[3]='9';check(!v2::decode(corrupt.data(),corrupt.size(),p),"unknown version");
    unsigned long long paired=0,checked=0;
    for(double rate:{1000.,8000.,44100.,48000.,96000.,192000.,2000000.}){
        Live a;v2::Live z;check(a.prepare(rate)&&z.prepare(rate),"prepare");
        check(a.restore(old)&&v2::decode(legacy.data(),legacy.size(),p)&&z.restore(p),"restore");a.reset();z.reset();
        for(unsigned i=0;i<frames*53;++i){if(i%31==0){unsigned k=(i/31)%Count;double v=(i%19)/18.;a.set(k,v);z.set(k,v);}double x=.9*std::sin(i*.193);check(a.step(x,-x)==z.step(x,-x),"legacy paired");++paired;}
        // Repair=0 and probe=0: hard dropout, or linear edge admission of original samples.
        p=v2::defaults;p[v2::Wet]=1;p[v2::Repair]=0;p[v2::Separation]=0;p[v2::Edge]=1;
        check(z.restore(p),"edge restore");z.reset();
        for(unsigned i=0;i<frames*4;++i){auto y=z.step(.25,0);unsigned pos=i%frames,lane=pos%stride;double expected=i<frames?0:pos<2*stride?.25*(1.-double(std::min(lane,stride-1-lane))/8):.25;check(y[0]==expected&&y[1]==0,"edge envelope");++checked;}
        p[v2::Edge]=0;p[v2::Probe]=1;check(z.restore(p),"probe restore");z.reset();
        for(unsigned i=0;i<frames*3;++i){auto y=z.step(.25,0);check(y[0]==(i<frames||i%frames<stride?0:.25)&&y[1]==0,"probe pass through");++checked;}
        // Dynamic normalized controls, nonfinite input and block-partition equivalence.
        v2::Live w;check(w.prepare(rate),"second prepare");z.restore(modern);w.restore(modern);z.reset();w.reset();unsigned index=0;
        for(unsigned n:{1u,17u,64u,511u,3u,144u,1024u})for(unsigned j=0;j<n;++j,++index){if(index%11==0){unsigned k=(index/11)%v2::Count;double v=(index%23)/22.;z.set(k,v);w.set(k,v);}float x=index%41==0?std::numeric_limits<float>::infinity():float(2*std::sin(index*.041));auto y=z.step(x,0),q=w.step(double(x),0);check(y==q&&y[1]==0&&std::isfinite(y[0])&&std::abs(y[0])<=1,"bounded block/format");++checked;}
        z.set(v2::Bypass,1);z.reset();for(unsigned i=0;i<frames*3;++i){auto y=z.step(i==0?.25:0,0);check(y[0]==(i==frames?.25:0)&&y[1]==0,"bypass impulse");}
        z.set(v2::Bypass,0);z.set(v2::Wet,1);z.reset();for(unsigned i=0;i<frames+7;++i)z.step(.5,-.5);for(unsigned i=0;i<ProbeEngine::tail;++i)z.step(0,0);check(z.step(0,0)==Stereo{},"finite tail");
    }
    std::cout<<"legacy_paired="<<paired<<" additional_frames="<<checked<<" EL02_bytes="<<v2::State{}.size()<<'\n';
}
