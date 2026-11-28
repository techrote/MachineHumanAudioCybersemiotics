#include "descriptor-v56.hpp"
#include <fstream>
#include <iostream>
#include <string>
#include <stdexcept>
using namespace mhac56;
static unsigned checks=0;
static void ck(bool v){++checks;if(!v)throw std::runtime_error("check "+std::to_string(checks));}
static int digit(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;return -1;}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    std::ifstream in(argv[1]);ck(bool(in));std::string h;unsigned n=0;
    while(in>>h){ck(h.size()==40);Wire w{},out{};for(unsigned i=0;i<20;++i){int a=digit(h[2*i]),b=digit(h[2*i+1]);ck(a>=0&&b>=0);w[i]=static_cast<std::uint8_t>(16*a+b);}Descriptor d{};ck(decode(w,d));ck(encode(d,out));ck(w==out);++n;}
    ck(n>0);
    Wire w{};Descriptor d{255,255,1,7,4,3,8,4,0xffffffffu,-0.0},out{};ck(encode(d,w));ck(decode(w,out));ck(out.challenge==d.challenge&&std::signbit(out.phase));Wire copy{};ck(encode(out,copy)&&copy==w);
    for(unsigned k: {0u,2u,3u,4u,5u,6u,7u}){copy=w;copy[k]=0xff; if(k==0)copy[k]=0;ck(!decode(copy,out));}
    copy=w;for(unsigned k=8;k<12;++k)copy[k]=0;ck(!decode(copy,out));copy=w;copy[12]=0x7f;copy[13]=0xf0;for(unsigned k=14;k<20;++k)copy[k]=0;ck(!decode(copy,out));
    std::cout<<"PASS "<<checks<<" assertions, "<<n<<" wire vectors, sizeof(Descriptor)="<<sizeof(Descriptor)<<", sizeof(Wire)="<<sizeof(Wire)<<"\n";
}
