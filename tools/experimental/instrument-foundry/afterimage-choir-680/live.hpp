#pragma once
#include "afterimage.hpp"
#include <atomic>
#include <cstring>
#include <mutex>
namespace mhac::afterimage::live {
// Stable native control indices: pair rank, receipt, minimum ms, memory permille.
// 30 bits suffice for exact discrete controls. No floating point state tearing.
constexpr unsigned FirstID=1600, Count=6;
using Word=std::uint32_t;
constexpr Word pack(unsigned pair,unsigned mode,unsigned ms,unsigned memory,unsigned depth=1) {
    return pair | (mode<<5) | (ms<<7) | (memory<<18) | ((depth-1u)<<28);
}
constexpr Word Default=pack(16,1,80,800); // pair (2,6): rank 13+3
inline unsigned depthOf(Word w) { return 1u+((w>>28)&3u); }
inline bool valid(Word w) { return !(w>>30) && depthOf(w)<=3 && (w&31)<28 && ((w>>7)&2047)<=2000 && ((w>>18)&1023)<=1000; }
inline Pair pairAt(unsigned rank) {
    for(unsigned l=0;l<7;++l) for(unsigned h=l+1;h<8;++h) if(rank--==0) return {l,h};
    return {};
}
inline Patch patch(Word w) { return {pairAt(w&31),static_cast<Mode>((w>>5)&3),double((w>>7)&2047),double((w>>18)&1023)/1000}; }
inline double normalized(Word w,unsigned i) {
    switch(i){case 0:return double(w&31)/27;case 1:return double((w>>5)&3)/3;case 2:return double((w>>7)&2047)/2000;case 3:return double((w>>18)&1023)/1000;case 5:return double(depthOf(w)-1)/2;default:return 0;}
}
using State=std::array<unsigned char,8>;
inline State encode(Word w) { State s{'A','C','0',static_cast<unsigned char>(depthOf(w)==1?'1':'2'),0,0,0,0}; for(unsigned i=0;i<4;++i)s[i+4]=static_cast<unsigned char>(w>>(8*i)); return s; }
inline bool decode(const unsigned char* s,unsigned n,Word& out) {
    if(!s||n!=8||std::memcmp(s,"AC0",3)||(s[3]!='1'&&s[3]!='2'))return false;
    Word w=0;for(unsigned i=0;i<4;++i)w|=Word(s[4+i])<<(8*i);
    if(!valid(w)||(s[3]=='1'&&depthOf(w)!=1)||(s[3]=='2'&&depthOf(w)==1))return false;
    out=w;return true;
}
class Live {
    Engine engine; Word controls=Default; bool cancel=false;
    struct Note {bool held=false;int host=0;int token=0;};
    // Eight held voices plus one spare token for atomic replacement.
    std::array<Note,9> notes{};
public:
    Live(){engine.configure(patch(controls));}
    bool prepare(double sr){if(!engine.prepare(sr))return false;reset();return true;}
    void reset(){engine.reset();notes={};cancel=false;}
    Word parameters()const{return controls;}
    bool applyPatch(Word w){if(!valid(w)||!engine.configure(patch(w)))return false;engine.setHistoryDepth(depthOf(w));controls=w;return true;}
    bool restorePatch(Word w){if(!applyPatch(w))return false;cancel=false;return true;}
    bool parameter(unsigned i,double x){
        if(i>=Count||!std::isfinite(x)||x<0||x>1)return false;
        if(i==4){cancel=x>=.5;return true;}
        if(i==5)return applyPatch((controls&~(Word(3)<<28))|(Word(std::lround(x*2))<<28));
        constexpr unsigned max[]{27,3,2000,1000},shift[]{0,5,7,18},bits[]{31,3,2047,1023};
        return applyPatch((controls&~(Word(bits[i])<<shift[i]))|(Word(std::lround(x*max[i]))<<shift[i]));
    }
    // Host identifiers may be negative fallback keys. Duplicate held keys are
    // rejected; release and retrigger use different internal bounded tokens.
    bool on(int host,int pitch,double cents,double velocity){
        if(velocity==0)return off(host);
        for(const auto& n:notes)if(n.held&&n.host==host)return false;
        for(auto& n:notes)if(!n.held){
            // Token reuse is harmless for released voices: off() only matches held voices.
            int token=static_cast<int>(&n-notes.data());
            int displaced=-1;
            if(!engine.on(token,pitch,velocity,cents,&displaced))return false;
            if(displaced>=0) notes[static_cast<unsigned>(displaced)]={};
            n={true,host,token};return true;
        }
        return false;
    }
    bool off(int host){for(auto& n:notes)if(n.held&&n.host==host){n.held=false;return engine.off(n.token,!cancel);}return false;}
    double tick(){return engine.tick();}
    unsigned remembered()const{return engine.remembered();}
    unsigned active()const{return engine.active();}
};
// The two packed mailboxes each hold generation + complete 30-bit patch.
// Non-audio callers serialize; audio reads and publishes once per block.
class Bridge {
    static_assert(std::atomic<std::uint64_t>::is_always_lock_free,"64-bit lock-free atomics required");
    std::atomic<std::uint64_t> requested{Default},published{Default};
    std::mutex mutex; std::uint32_t applied=0;
    static std::uint32_t gen(std::uint64_t v){return std::uint32_t(v>>32);}
public:
    bool request(Word w){if(!valid(w))return false;std::lock_guard<std::mutex> lock(mutex);auto g=gen(requested.load())+1u;requested.store((std::uint64_t(g)<<32)|w);return true;}
    Word save(){std::lock_guard<std::mutex> lock(mutex);auto r=requested.load(),p=published.load();return Word(gen(r)==gen(p)?p:r);}
    void begin(Live& e){auto r=requested.load();if(gen(r)!=applied&&e.restorePatch(Word(r)))applied=gen(r);}
    void end(const Live& e){published.store((std::uint64_t(applied)<<32)|e.parameters());}
};
}
