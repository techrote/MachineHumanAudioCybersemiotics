#include "inactive_aux.hpp"
#include <iostream>
#include <stdexcept>
using mhac::mainline::acceptsOutputShape;
template<int N> void check() {
    unsigned cases=0, accepted=0, exceptions=0;
    for(int bus=-1;bus<=4;++bus)for(bool active:{false,true})
        for(int expected=-1;expected<=3;++expected)for(int supplied=-1;supplied<=3;++supplied)
            for(bool nullArray:{false,true}) {
                // Independent enumeration of the legal negotiated bus profiles.
                bool ordinary=false;
                if(bus==0) ordinary=(expected==1&&supplied==1)||(expected==2&&supplied==2);
                for(int aux=1;aux<=N;++aux) if(bus==aux&&expected==1&&supplied==1) ordinary=true;
                const bool exceptional=bus>=1&&bus<=N&&!active&&expected==1&&supplied==0&&nullArray;
                const bool got=acceptsOutputShape<N>(bus,active,expected,supplied,nullArray);
                if(got!=(ordinary||exceptional))throw std::runtime_error("bus shape mismatch");
                ++cases;accepted+=got;exceptions+=got&&!ordinary;
            }
    if(cases!=600||accepted!=unsigned(8+5*N)||exceptions!=unsigned(N))throw std::runtime_error("profile census");
    std::cout<<"max_aux="<<N<<" cases="<<cases<<" accepted="<<accepted<<" exceptions="<<exceptions<<'\n';
}
int main(){check<2>();check<3>();}
