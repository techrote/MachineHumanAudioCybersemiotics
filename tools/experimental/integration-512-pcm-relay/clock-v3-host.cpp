// Native fixture reader for canonical 44-byte mono 16 kHz PCM16 WAVs only.
#include "clock-v3.hpp"
#include <fstream>
#include <iostream>
#include <vector>
#include <cstring>
#include <iomanip>
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream f(argv[1],std::ios::binary|std::ios::ate);if(!f)return 2;auto size=f.tellg();
 if(size<44||size>44+2*mhac_clock::max_samples)return 2;
 f.seekg(0);std::vector<unsigned char>b(static_cast<size_t>(size));if(!f.read(reinterpret_cast<char*>(b.data()),size))return 2;
 auto u16=[&](int i){return unsigned(b[i])|(unsigned(b[i+1])<<8);};
 auto u32=[&](int i){return u16(i)|(u16(i+2)<<16);};
 if(std::memcmp(b.data(),"RIFF",4)||std::memcmp(b.data()+8,"WAVEfmt ",8)||std::memcmp(b.data()+36,"data",4)||u32(4)!=b.size()-8||u32(16)!=16||u16(20)!=1||u16(22)!=1||u32(24)!=16000||u32(28)!=32000||u16(32)!=2||u16(34)!=16||u32(40)!=b.size()-44||u32(40)%2)return 2;
 std::vector<int16_t> pcm(u32(40)/2);for(size_t i=0;i<pcm.size();i++){auto v=u16(44+2*i);pcm[i]=static_cast<int16_t>(v>=32768?int(v)-65536:int(v));}
 const auto r=mhac_clock::acquire(pcm.data(),int(pcm.size()));if(!r.valid_input)return 2;
 std::cout<<std::setprecision(17)<<"{\"onsetSpan\":"<<r.onset_span<<",\"resultBytes\":"<<sizeof(r)<<",\"evidence\":[";
 for(int i=0;i<r.count;i++){const auto&h=r.hypotheses[i];if(i)std::cout<<',';std::cout<<"{\"s\":"<<h.start<<",\"scale\":"<<1+(h.scale_index-6)*.0025<<",\"q\":"<<h.quality<<",\"complete\":"<<(h.complete?"true":"false")<<",\"words\":[";for(int j=0;j<24;j++){if(j)std::cout<<',';if(h.words[j]<0)std::cout<<"null";else std::cout<<int(h.words[j]);}std::cout<<"]}";}
 std::cout<<"]}\n";
}
