#pragma once
// Refs #512. Original experimental DSP adapter; no allocation, I/O or semantic trust.
#include <cmath>
#include <cstddef>
#include <cstdint>
namespace mhac_clock {
constexpr int max_samples=38400, max_hypotheses=13, frame=31360;
struct Hypothesis { int start=0, scale_index=0; double quality=0; int8_t words[24]{}; bool complete=false; };
struct Result { Hypothesis hypotheses[max_hypotheses]{}; int count=0, onset_span=0; bool valid_input=false; };
inline double score(const int16_t* p,int length,int start,int n,double coeff){
 if(start<0||start+n>length)return 0;
 double a=0,b=0,e=0;
 for(int i=0;i<n;i++){double x=p[start+i],z=x+coeff*a-b;b=a;a=z;e+=x*x;}
 if(e<n*250.*250.)return 0;
 return 2*(a*a+b*b-coeff*a*b)/(n*e);
}
inline double coefficient(double hz,double scale){return 2*std::cos(6.2831853071795864769*hz/(16000*scale));}
inline Result acquire(const int16_t* p,int length){
 Result result{};if(!p||length<0||length>max_samples)return result;result.valid_input=true;
 int lo=max_samples,hi=-1;
 for(int k=0;k<max_hypotheses;k++){
  const double scale=1+(k-6)*.0025;const int n=std::lround(320*scale);
  const double ca=coefficient(2300,scale),cb=coefficient(2700,scale);double best=0;int start=-1;
  for(int s=0;s+2*n<=length;s+=16){const double a=score(p,length,s,n,ca);if(a<.72)continue;const double b=score(p,length,s+n,n,cb),q=a<b?a:b;
   if(q>=.72){if(s<lo)lo=s;if(s>hi)hi=s;if(q>best){best=q;start=s;}}
  }
  if(start<0)continue;
  auto& h=result.hypotheses[result.count++];h.start=start;h.scale_index=k;h.quality=best;h.complete=start+std::lround(frame*scale)-320<=length;
  double c[17];for(int v=0;v<17;v++)c[v]=coefficient(400+100*v,scale);
  for(int i=0;i<24;i++){
   const int s=std::lround(start+(640+i*1280+320)*scale);double a=0,b=0;int value=-1;
   for(int v=0;v<17;v++){const double q=score(p,length,s,n,c[v]);if(q>a){b=a;a=q;value=v;}else if(q>b)b=q;}
   h.words[i]=(a>=.85&&a-b>=.2)?value:-1;
  }
 }
 result.onset_span=result.count?hi-lo:0;return result;
}
} // namespace mhac_clock
