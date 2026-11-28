#include "logos.hpp"
#include "articulum.hpp"
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace mhac::tts;

static void le16(std::ofstream& f,std::uint16_t v){char b[2]={char(v&255),char((v>>8)&255)};f.write(b,2);} 
static void le32(std::ofstream& f,std::uint32_t v){char b[4]={char(v&255),char((v>>8)&255),char((v>>16)&255),char((v>>24)&255)};f.write(b,4);} 
static void wav(const std::filesystem::path& path,const std::vector<double>& x,unsigned sr){
    std::ofstream f(path,std::ios::binary);if(!f)throw std::runtime_error("cannot open WAV");const std::uint32_t data=std::uint32_t(x.size()*2);
    f.write("RIFF",4);le32(f,36+data);f.write("WAVEfmt ",8);le32(f,16);le16(f,1);le16(f,1);le32(f,sr);le32(f,sr*2);le16(f,2);le16(f,16);f.write("data",4);le32(f,data);
    for(double v:x){const auto s=static_cast<std::int16_t>(std::lround(std::clamp(v,-.999, .999)*32767.0));le16(f,static_cast<std::uint16_t>(s));}
}
int main(int argc,char** argv){
    const std::filesystem::path out=argc>1?argv[1]:"tts-specimens";std::filesystem::create_directories(out);constexpr unsigned sr=48000;
    const std::string text=argc>2?argv[2]:"the word grows its own mouth";
    Logos logos; if(!logos.prepare(sr))return 2;LogosParameters lp{};lp.rate=.92f;lp.articulation=.72f;logos.set_parameters(lp);logos.set_plan(compile_text(text));logos.note_on(57,.86);
    std::vector<double> spoken(sr*5);for(std::size_t i=0;i<spoken.size();++i){if((i%256)==0)logos.begin_block();spoken[i]=logos.tick();}wav(out/"logos-spoken.wav",spoken,sr);
    Logos melodic;if(!melodic.prepare(sr))return 2;melodic.set_parameters(lp);std::vector<double> song(sr*6);const int notes[4]={48,55,60,67};for(std::size_t i=0;i<song.size();++i){if(i%(sr*3/2)==0){const auto k=(i/(sr*3/2))%4;melodic.set_plan(phrase_program(unsigned(k)));melodic.note_on(notes[k],.78);}song[i]=melodic.tick();}wav(out/"logos-melodic.wav",song,sr);
    Articulum art;if(!art.prepare(sr))return 2;art.note_on(50,.9);std::vector<double> tract(sr*6);for(std::size_t i=0;i<tract.size();++i){if(i%sr==0){ArticulumParameters p{};const unsigned k=unsigned(i/sr);p.tongueFront=float(k%3)/2.f;p.tongueHeight=.25f+.12f*float(k);p.lipRound=(k%2)?.65f:.12f;p.nasal=(k==4)?.35f:.05f;art.set_parameters(p);}tract[i]=art.tick();}wav(out/"articulum-tract.wav",tract,sr);
    std::cout<<"wrote LOGOS spoken/melodic and ARTICULUM tract specimens to "<<out.string()<<"\n";
}
