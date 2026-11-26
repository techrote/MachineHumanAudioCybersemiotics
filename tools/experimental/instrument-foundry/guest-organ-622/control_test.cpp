#include "control.hpp"
#include <iostream>
#define CHECK(x) do{if(!(x)){std::cerr<<"failure line "<<__LINE__<<": "<<#x<<'\n';return 1;}}while(0)
int main(){
    using namespace guest::control;
    auto p=defaults;p[7]=1;p[4]=.25;auto bytes=encode(p);Params q{};
    CHECK(decode(bytes.data(),bytes.size(),q));CHECK(encode(q)==bytes);
    for(unsigned n=0;n<bytes.size();++n)CHECK(!decode(bytes.data(),n,q));
    auto bad=bytes;bad[3]='2';CHECK(!decode(bad.data(),bad.size(),q));
    bad=bytes;bad[4]=0;bad[5]=0;bad[6]=192;bad[7]=127;CHECK(!decode(bad.data(),bad.size(),q));
    CHECK(encode(q)==bytes);
    unsigned frames=0;
    for(double sr:{1000.,1234.568,8000.,44100.,48000.,96000.,192000.,1234567.8,2000000.}){
        Engine a,b;CHECK(a.prepare(sr)&&b.prepare(sr));
        // Same-id releases overlap in separate slots; active duplicate remains rejected.
        for(int k=0;k<24;++k){CHECK(a.on(1,48,0,.8));CHECK(!a.on(1,48,0,.8));for(unsigned i=0;i<unsigned(sr*.03);++i)a.tick();a.off(1);for(unsigned i=0;i<unsigned(sr*.02);++i)a.tick();}
        for(unsigned i=0;i<unsigned(sr*.032)+2;++i){a.tick();}CHECK(a.tick().right==0);
        a.reset();a.parameter(7,1);a.parameter(4,1);b.parameter(4,1);
        CHECK(a.on(2,55,0,.8)&&b.on(2,55,0,.8));
        const unsigned boundary=4*unsigned(std::lround(sr/12));
        for(unsigned i=0;i<boundary;++i){auto x=a.tick(),y=b.tick();CHECK(x.left==y.left&&x.right==y.right);++frames;}
        bool diverged=false;for(unsigned i=0;i<unsigned(sr*.02)+2;++i){auto x=a.tick(),y=b.tick();CHECK(x.left==y.left);diverged|=x.right!=y.right;}CHECK(diverged);
        a.parameter(7,0);a.off(2);CHECK(a.on(2,55,0,.8));a.off(2);
        for(unsigned i=0;i<unsigned(sr*.032)+2;++i){a.tick();}CHECK(a.tick().right==0);
        a.restore(q);CHECK(a.tick().right==0&&encode(a.parameters())==bytes);
        a.parameter(0,std::numeric_limits<double>::quiet_NaN());CHECK(encode(a.parameters())==bytes);
        a.reset();for(int i=0;i<8;++i)CHECK(a.on(i,60,0,1));a.off(0);CHECK(!a.on(0,60,0,1));
        a.reset();CHECK(a.on(9,60,0,1));auto f=a.tick();double l=0,r=0,base=0,counter=0;double* ptrs[]{&l,&r};write(f,ptrs,2,&base,&counter,0);CHECK(l==f.left&&r==f.right&&base==f.base&&counter==f.counter);
        float mono=0;float* m[]{&mono};write(f,m,1,static_cast<float*>(nullptr),static_cast<float*>(nullptr),0);CHECK(mono==float((f.left+f.right)*.5));
    }
    std::cout<<"PASS: GO01 corruption/roundtrip, 216 repeated onsets, nine rates, "<<frames<<" exact opening frames, routing and scope\n";
}
