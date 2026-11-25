#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace winters {
using Bank=std::array<int,4>;
struct Score {
    Bank bank{{0,1,2,3}}, snapshot=bank;
    int moving=0, paused=0, latched=0;
    bool held=false;
    void hold() noexcept { if(!held){latched=bank[moving];snapshot=bank;held=true;} }
    void release() noexcept {held=false;}
    void tick() noexcept {moving=(moving+1)%4;if(!held)paused=(paused+1)%4;}
    void edit(int slot,int token) noexcept {if(slot>=0&&slot<4)bank[slot]=std::clamp(token,0,3);}
    Bank::value_type token(int lane) const noexcept {
        if(lane==0)return held?latched:bank[moving];
        if(lane==1)return bank[paused];
        return (held?snapshot:bank)[moving];
    }
};
struct Engine {
    static constexpr int capacity=4;
    static constexpr double pi=3.14159265358979323846;
    struct Voice { bool active=false, releasing=false; int id=0, note=0; double velocity=0, velocityTarget=0, env=0; std::array<double,3> phase{},inc{},target{}; };
    Score score{};
    std::array<Voice,capacity> voices{};
    double rate=48000, attack=1./240, releaseStep=1./1920, glide=1./240;
    static double sane(double v,double fallback) noexcept {return std::isfinite(v)?v:fallback;}
    bool setup(double sr) noexcept {
        if(!std::isfinite(sr)||sr<1000||sr>2000000)return false;
        rate=sr;attack=1/std::max(1.,rate*.005);releaseStep=1/std::max(1.,rate*.04);glide=attack;reset();return true;
    }
    void reset() noexcept {score=Score{};voices={};}
    double frequency(int note,int lane) const noexcept {
        constexpr int intervals[4]={0,3,7,10};
        return std::min(rate*.45,440*std::exp2((note+intervals[score.token(lane)]-69)/12.))/rate;
    }
    void retarget() noexcept {for(auto& v:voices)if(v.active)for(int i=0;i<3;++i)v.target[i]=frequency(v.note,i);}
    void hold() noexcept {score.hold();retarget();}
    void release() noexcept {score.release();retarget();}
    void tick() noexcept {score.tick();retarget();}
    void edit(int slot,int token) noexcept {score.edit(slot,token);retarget();}
    bool noteOn(int id,int note,double velocity) noexcept {
        if(!std::isfinite(velocity)||velocity<=0||note<0||note>127)return false;
        for(auto& v:voices)if(v.active&&v.id==id){
            if(!v.releasing)return false;
            // Re-articulate the releasing voice without resetting phase or envelope.
            v.releasing=false;v.note=note;v.velocityTarget=std::min(1.,velocity);
            for(int i=0;i<3;++i)v.target[i]=frequency(note,i);
            return true;
        }
        for(auto& v:voices)if(!v.active){v=Voice{};v.active=true;v.id=id;v.note=note;v.velocity=v.velocityTarget=std::min(1.,velocity);for(int i=0;i<3;++i)v.inc[i]=v.target[i]=frequency(note,i);return true;}
        return false; // refuse excess notes rather than abruptly stealing a sounding voice
    }
    void noteOff(int id) noexcept {for(auto& v:voices)if(v.active&&v.id==id)v.releasing=true;}
    std::array<double,3> sample() noexcept {
        std::array<double,3> out{};
        for(auto& v:voices)if(v.active){
            v.env=v.releasing?std::max(0.,v.env-releaseStep):std::min(1.,v.env+attack);
            if(v.releasing&&v.env<=0){v=Voice{};continue;}
            v.velocity+=std::clamp(v.velocityTarget-v.velocity,-attack,attack);
            for(int i=0;i<3;++i){
                v.inc[i]+=std::clamp(v.target[i]-v.inc[i],-glide*.45,glide*.45);
                v.phase[i]+=v.inc[i];if(v.phase[i]>=1)v.phase[i]-=1;
                out[i]+=.05*v.velocity*v.env*std::sin(2*pi*v.phase[i]);
            }
        }
        return out;
    }
    template<class T> void process(T* left,T* right,unsigned n) noexcept {
        for(unsigned i=0;i<n;++i){const auto s=sample();const double l=s[0]+.5*s[1],r=s[2]+.5*s[1];
            if(left&&right&&left==right)left[i]=static_cast<T>((l+r)*.5);
            else {if(left)left[i]=static_cast<T>(right?l:(l+r)*.5);if(right)right[i]=static_cast<T>(left?r:(l+r)*.5);}
        }
    }
};
}
