#include "freeze.hpp"
#include <cstdlib>
#include <iostream>
#include <cmath>
#include <array>
using namespace mhac::freeze;
static unsigned long long checks=0;
void require(bool ok, const char* name, double sr, double rate, unsigned long long sample){
    ++checks;if(!ok){std::cerr<<name<<" sr="<<sr<<" rate="<<rate<<" sample="<<sample<<'\n';std::exit(1);}
}
int main(){
    // Rational oracle: quarter-Hz powers at integer sample rates. Check every
    // frame over three wraps, including the two sides of every boundary.
    for(unsigned sr:{8000u,44100u,48000u,96000u,192000u,384000u,768000u,1000000u,2000000u}){
        for(unsigned j=0;j<=6;++j){
            Engine e;e.reset(sr);e.set(Rate,j/6.);
            const unsigned long long num=1ull<<j,den=4ull*sr;
            const auto frames=(3*den+num-1)/num+1;
            for(unsigned long long n=1;n<=frames;++n){
                e.nextGain();
                require(e.slot()==(n*num/den)%4,"rational clock",sr,num/4.,n);
            }
        }
    }
    // Pause and rate automation preserve fractional progress. All segments
    // have dyadic rates; the exact integer numerator ignores paused frames.
    for(unsigned sr:{44100u,48000u,192000u}){
        Engine e;e.reset(sr);e.set(Mode,.5);
        unsigned long long units=0,den=4ull*sr;
        for(unsigned n=0;n<sr*9u;++n){
            const unsigned j=(n/12347u)%7u; const bool pause=(n/7919u)%5u==2u;
            e.set(Rate,j/6.);e.set(Hold,pause?1.:0.);e.nextGain();
            if(!pause)units+=1ull<<j;
            require(e.slot()==(units/den)%4,"automated clock",sr,(1ull<<j)/4.,n+1);
        }
        e.reset(sr);require(e.slot()==0,"reset",sr,0,0);
    }
    // Fractional SDK rates and non-dyadic automation: compare against a
    // long-double integrated reference, excluding numerically ambiguous ties.
    // The rational oracle above covers exact boundaries without that exclusion.
    unsigned long long ambiguous=0;
    for(double sr:{1234.5678,44100.1,1234567.8}){
        Engine e;e.reset(sr);e.set(Mode,.5);long double phase=0;
        for(unsigned n=0;n<3000000u;++n){
            const double norm=double((n/12347u)%97u)/96.;const bool pause=(n/7919u)%5u==2u;
            e.set(Rate,norm);e.set(Hold,pause?1.:0.);e.nextGain();
            if(!pause)phase+=static_cast<long double>(.25*std::exp2(6*norm)/sr);
            const auto distance=std::abs(phase-std::round(phase));
            if(distance<1e-8L){++ambiguous;continue;}
            require(e.slot()==static_cast<unsigned long long>(std::floor(phase))%4,"fractional clock",sr,norm,n+1);
        }
    }
    std::cout<<"PASS "<<checks<<" clock assertions; "<<ambiguous<<" fractional near-tie frames excluded\n";
}
