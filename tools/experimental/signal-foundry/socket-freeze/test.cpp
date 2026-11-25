#include "freeze.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
using namespace mhac;
unsigned checks=0;
void check(bool b){++checks;if(!b)throw std::runtime_error("failed check "+std::to_string(checks));}
void tick(Freeze& f){unsigned s=f.phase();for(int i=0;i<10000&&f.phase()==s;++i)f.step();check(f.phase()!=s);}
int main(){
 for(int m=0;m<3;++m){Freeze f;f.prepare(8000);f.set(Rate,1);f.set(Mode,m/2.0);f.set(Hold,1);f.step();check(f.target()==defaults[0]);f.set(S0,0.3);f.set(S1,0.7);
 if(m==1){for(int i=0;i<2000;++i)f.step();check(f.phase()==0);check(f.target()==0.3);}else{tick(f);check(f.target()==(m==0?defaults[0]:defaults[1]));}
 f.set(Hold,0);f.step();check(f.target()==(m==1?0.3:0.7));
 }
 for(double sr:{8000.,44100.,48000.,96000.,192000.,384000.}){Freeze a,b;a.prepare(sr);b.prepare(sr);a.set(Rate,1);b.set(Rate,1);std::vector<double> ref;for(int i=0;i<20000;++i){if(i==700)a.set(Hold,1);if(i==12000)a.set(Hold,0);double g=a.step();check(g>=0&&g<=1&&std::isfinite(g));ref.push_back(g);}int n=0;for(int block:{1,31,511,3,1024,7,4096,14327}){for(int j=0;j<block&&n<20000;++j,++n){if(n==700)b.set(Hold,1);if(n==12000)b.set(Hold,0);check(b.step()==ref[n]);}}check(n==20000);a.set(Bypass,1);for(int j=0;j<int(sr*0.2);++j)a.step();check(std::abs(a.step()-1)<1e-12);}
 check(Freeze::apply(std::numeric_limits<float>::infinity(),0.5)==0);check(Freeze::apply(std::numeric_limits<double>::quiet_NaN(),0.5)==0);check(Freeze::apply(2.f,0.5)==1.f);check(Freeze::apply(-2.,0.5)==-1.);check(Freeze::apply(1e-25,1)==0);
 Freeze f;f.prepare(48000);f.set(0,std::numeric_limits<double>::quiet_NaN());check(f.parameters()[0]==0);f.set(1,2);check(f.parameters()[1]==1);f.set(2,-1);check(f.parameters()[2]==0);
 std::cout<<checks<<" checks passed\n";
}
