#include "compiler.hpp"
#include <iostream>
#include <iomanip>
#include <string>
using namespace mhac::lattice::design;
static double number(const char* s){std::size_t n=0;std::string text(s);double v=std::stod(text,&n);if(n!=text.size())throw std::invalid_argument("number");return v;}
static unsigned integer(const char* s,unsigned max){double v=number(s);if(!std::isfinite(v)||v<1||v>max||std::floor(v)!=v)throw std::invalid_argument("integer");return static_cast<unsigned>(v);}
int main(int argc,char** argv){try{if(argc<9||(argc-7)%2)throw std::invalid_argument("usage: compiler_cli rate budget d1 d2 d3 d4 hz rightPower [hz rightPower ...]");double sr=number(argv[1]);unsigned budget=integer(argv[2],4096);std::array<unsigned,4> ds{};for(unsigned i=0;i<4;++i)ds[i]=integer(argv[3+i],1024);std::vector<Probe> probes;for(int i=7;i<argc;i+=2)probes.push_back({number(argv[i]),number(argv[i+1])});auto result=compile(probes,sr,ds,budget);std::cout<<std::setprecision(17)<<"candidates="<<result.evaluated<<" mse="<<result.mse<<'\n';for(auto s:result.program)std::cout<<"LRSD"[static_cast<unsigned>(s.axis)]<<' '<<s.delay<<'\n';for(auto p:probes)std::cout<<p.hz<<','<<p.rightPower<<','<<std::norm(response(result.program,p.hz,sr).r)<<'\n';return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}}
