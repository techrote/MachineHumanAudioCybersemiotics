#pragma once
#include "../live-576/live.hpp"
namespace prism {
// Differential resynthesis: keep the delayed input, add the modeled change,
// and optionally remove its complementary residual. No allocation in step().
class ResidualPrism {
    struct Frame { Coeff linear{},delta{}; unsigned grid=1; };
    std::vector<C> basis,delay;
    Frame from{},to{}; Coeff sum{};
    LiveParams target=defaults;
    std::size_t n=0,pos=0; unsigned capture=1;
    double retention=1.,keep=1.,wet=.5,gain=.5,slew=.01;
    C carrier(unsigned j,unsigned grid) const noexcept { return basis[(pos*unsigned(bins[j])*grid)%n]; }
    C synth(const Coeff& c,unsigned grid) const noexcept {
        C y{}; for(unsigned j=0;j<4;++j) y+=c[j]*carrier(j,grid); return y;
    }
    double move(double x,double t) const noexcept { return x+std::clamp(t-x,-slew,slew); }
public:
    bool prepare(double sr) {
        const auto len=frameLength(sr); if(!len) return false;
        try { std::vector<C> b(len),d(len); for(std::size_t i=0;i<len;++i)b[i]=std::polar(1.,tau*double(i)/double(len)); basis.swap(b);delay.swap(d); }
        catch(...) { return false; }
        n=len;slew=std::min(1.,200./sr);reset();return true;
    }
    void set(unsigned id,double v) noexcept {
        if(!std::isfinite(v))return;
        if(id<Count)target[id]=std::clamp(v,0.,1.);
        else if(id==Count)retention=std::clamp(v,0.,1.);
    }
    void reset() noexcept {
        pos=0;sum={};capture=factor(target[Grid]);from=to=Frame{{},{},capture};
        std::fill(delay.begin(),delay.end(),C{});wet=target[Bypass]>=.5?0.:target[Wet];gain=target[Gain];keep=retention;
    }
    std::size_t latency() const noexcept {return n;}
    std::size_t tailBound() const noexcept {return 3*n;}
    C step(double l,double r) noexcept {
        if(!n)return {};
        if(pos==0)capture=factor(target[Grid]);
        const C x{bound(l,-1,1),bound(r,-1,1)},dry=delay[pos];delay[pos]=x;
        for(unsigned j=0;j<4;++j)sum[j]+=x*std::conj(carrier(j,capture));
        const double a=double(pos+1)/double(n);
        const C l0=synth(from.linear,from.grid),l1=synth(to.linear,to.grid);
        const C d0=synth(from.delta,from.grid),d1=synth(to.delta,to.grid);
        const C linear=l0+a*(l1-l0),delta=d0+a*(d1-d0);
        wet=move(wet,target[Bypass]>=.5?0.:target[Wet]);gain=move(gain,target[Gain]);keep=move(keep,retention);
        const C y=dry+wet*((gain-1.)*linear+gain*delta+(keep-1.)*(dry-linear));
        if(++pos==n){
            pos=0;for(auto& c:sum)c/=double(n);
            const double drive=2*target[Drive]-1;
            const auto raw=cubic(sum,drive),clean=cycle(sum,drive);
            from=to;to.grid=capture;to.linear=sum;
            for(unsigned j=0;j<4;++j)to.delta[j]=(raw[j]-sum[j])+target[Cancel]*(clean[j]-raw[j]);
            sum={};
        }
        return {bound(y.real(),-1,1),bound(y.imag(),-1,1)};
    }
};
}
