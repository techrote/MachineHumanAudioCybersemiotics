#pragma once
#include "random_receipt.hpp"
namespace mhac::receipt::multi {
// A matching is an involution; singleton states retain their identity.
struct Matching {
    unsigned bits=3;
    std::array<unsigned,256> mate{};
    explicit Matching(unsigned b=3) noexcept : bits(b>=3&&b<=8?b:3) {
        for(unsigned i=0;i<256;++i)mate[i]=i;
    }
    unsigned size() const noexcept {return 1u<<bits;}
    bool pair(unsigned a,unsigned b) noexcept {
        if(a>=size()||b>=size()||a==b||mate[a]!=a||mate[b]!=b)return false;
        mate[a]=b;mate[b]=a;return true;
    }
    unsigned collapse(unsigned q) const noexcept {return std::min(q,mate[q]);}
};
enum class Contract : unsigned {fixed,balanced,preview,known};
struct Config {
    unsigned bits=3,pairs=4,budget=1,epoch_ms=25;
    Contract contract=Contract::balanced;
    std::uint32_t geometry=1,seed=42;
    bool bypass=false;double wet=0;
};
inline bool valid(const Config& p) noexcept {
    return p.bits>=3&&p.bits<=8&&p.pairs<=((1u<<p.bits)/2)&&p.budget<=p.bits&&
        p.epoch_ms>=5&&p.epoch_ms<=1000&&static_cast<unsigned>(p.contract)<4&&
        std::isfinite(p.wet)&&p.wet>=0&&p.wet<=1;
}
inline Matching geometry(const Config& p) noexcept {
    Matching m(p.bits);if(!valid(p))return m;std::array<unsigned,256> order{};
    for(unsigned i=0;i<m.size();++i)order[i]=i;
    auto key=std::uint64_t(p.geometry);
    for(unsigned i=m.size()-1;i>0;--i){key=randomized::hash(key);std::swap(order[i],order[static_cast<unsigned>(key%(i+1))]);}
    for(unsigned i=0;i<p.pairs;++i)m.pair(order[2*i],order[2*i+1]);
    return m;
}
// A single digit for the WHOLE action, not one hint per edge.
inline unsigned preview_digit(const Matching& m) noexcept {
    unsigned best=0,score=0;
    for(unsigned b=0;b<m.bits;++b){unsigned s=0;
        for(unsigned q=0;q<m.size();++q)if(q<m.mate[q]&&((q^m.mate[q])&(1u<<b)))++s;
        if(s>score){score=s;best=b;}}
    return best;
}
struct Receipt {
    Contract mode;unsigned budget,digit;randomized::Draw draw;
    unsigned tag(const Matching& m,unsigned q) const noexcept {
        switch(mode){
        case Contract::known:return q>m.mate[q]?1u:0u;
        case Contract::preview:return (q>>digit)&1u;
        case Contract::balanced:return randomized::multiply(q,draw.multiplier,m.bits)&((1u<<budget)-1u);
        default:return q&((1u<<budget)-1u);
        }
    }
    unsigned decode(const Matching& m,unsigned output,unsigned receipt) const noexcept {
        const unsigned other=m.mate[output];
        if(other==output)return output;
        const bool a=tag(m,output)==receipt,b=tag(m,other)==receipt;
        if(a&&b)return mode==Contract::balanced&&draw.upper?other:output;
        return b?other:output; // trusted valid receipt, no corrupt-channel claim
    }
};
using State=std::array<std::uint8_t,28>;
inline State save(const Config& p) noexcept {
    State s{'M','R','0','1',static_cast<std::uint8_t>(p.bits),static_cast<std::uint8_t>(p.pairs),
        static_cast<std::uint8_t>(p.budget),static_cast<std::uint8_t>(p.contract),
        static_cast<std::uint8_t>(p.epoch_ms),static_cast<std::uint8_t>(p.epoch_ms>>8),static_cast<std::uint8_t>(p.bypass),0};
    std::uint64_t w=0;std::memcpy(&w,&p.wet,8);
    for(unsigned i=0;i<4;++i){s[12+i]=static_cast<std::uint8_t>(p.geometry>>(8*i));s[16+i]=static_cast<std::uint8_t>(p.seed>>(8*i));}
    for(unsigned i=0;i<8;++i)s[20+i]=static_cast<std::uint8_t>(w>>(8*i));
    return s;
}
inline bool load(const std::uint8_t* s,std::size_t n,Config& p) noexcept {
    if(!s||n!=28||s[0]!='M'||s[1]!='R'||s[2]!='0'||s[3]!='1'||s[10]>1||s[11])return false;
    Config q{s[4],s[5],s[6],unsigned(s[8])+(unsigned(s[9])<<8),static_cast<Contract>(s[7]),0,0,s[10]!=0,0};
    std::uint64_t w=0;for(unsigned i=0;i<4;++i){q.geometry|=std::uint32_t(s[12+i])<<(8*i);q.seed|=std::uint32_t(s[16+i])<<(8*i);}
    for(unsigned i=0;i<8;++i)w|=std::uint64_t(s[20+i])<<(8*i);
    std::memcpy(&q.wet,&w,8);if(!valid(q))return false;p=q;return true;
}
class Live {
    using Table=std::array<double,256>;
    Config p_{};Matching m_=geometry(p_);unsigned digit_=preview_digit(m_);
    randomized::Schedule seq_{};randomized::Draw draw_{1,false};
    Table start_{},goal_{};double rate_=48000,wet_=0;
    unsigned ramp_=240,left_=0,epoch_=1200,until_=1200;
    double at(unsigned i) const noexcept {return left_?start_[i]+(goal_[i]-start_[i])*double(ramp_-left_)/ramp_:goal_[i];}
    Table table() const noexcept {
        Table t{};Receipt r{p_.contract,p_.budget,digit_,draw_};
        for(unsigned q=0;q<m_.size();++q){const auto decoded=r.decode(m_,m_.collapse(q),r.tag(m_,q));
            const double v=resolution::amplitude(decoded,p_.bits);const unsigned span=256/m_.size();
            for(unsigned j=0;j<span;++j)t[q*span+j]=v;}
        return t;
    }
    void target() noexcept {const auto t=table();if(t==goal_)return;for(unsigned i=0;i<256;++i)start_[i]=at(i);goal_=t;left_=ramp_;}
    void restart() noexcept {seq_.reset(p_.bits,p_.seed);draw_=seq_.next();epoch_=static_cast<unsigned>(std::ceil(rate_*p_.epoch_ms*.001));until_=epoch_;}
    double sample(double in) const noexcept {const double x=clean(in);if(x==0||wet_==0)return x;
        const unsigned q=std::min(255u,static_cast<unsigned>((x+1)*128));return clean(x*(1-wet_)+at(q)*wet_);}
public:
    Live() noexcept {reset();}
    bool prepare(double rate) noexcept {if(!std::isfinite(rate)||rate<1000||rate>2000000)return false;rate_=rate;ramp_=static_cast<unsigned>(std::ceil(rate*.005));reset();return true;}
    void reset() noexcept {restart();start_=goal_=table();left_=0;wet_=0;}
    const Config& config() const noexcept{return p_;}
    bool apply(const Config& p) noexcept {
        if(!valid(p))return false;
        const bool clock=p.bits!=p_.bits||p.seed!=p_.seed||p.epoch_ms!=p_.epoch_ms;
        const bool geom=p.bits!=p_.bits||p.pairs!=p_.pairs||p.geometry!=p_.geometry;
        const bool law=clock||geom||p.budget!=p_.budget||p.contract!=p_.contract;
        p_=p;if(geom){m_=geometry(p_);digit_=preview_digit(m_);}if(clock)restart();if(law)target();return true;
    }
    template<class T> void frame(T& l,T& r) noexcept {
        if(!until_){draw_=seq_.next();until_=epoch_;if(p_.contract==Contract::balanced)target();}
        --until_;if(left_)--left_;
        const double dest=p_.bypass?0:p_.wet,step=1.0/ramp_;wet_+=std::clamp(dest-wet_,-step,step);
        l=static_cast<T>(sample(l));r=static_cast<T>(sample(r));
    }
};
}
