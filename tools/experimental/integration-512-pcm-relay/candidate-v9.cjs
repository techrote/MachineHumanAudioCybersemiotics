'use strict';
// Refs #512. Onset-aware rearm, unchanged packet validation.
const {EpochReceiver}=require('./epoch-v8.cjs');
const N=1024,HISTORY=4096,WAIT=1600;
const cfg=Array.from({length:13},(_,i)=>{const s=1+(i-6)*.0025;return [Math.round(320*s),2*Math.cos(2*Math.PI*2300/(16000*s)),2*Math.cos(2*Math.PI*2700/(16000*s))];});
class OnsetObserver {
  constructor(from){this.ring=new Int16Array(2*N);this.at=from;this.scan=from;this.last=null;this.scans=0;this.hits=0;}
  score(s,n,c){let a=0,b=0,e=0;const p=this.ring,j=s%N;for(let i=j;i<j+n;i++){const x=p[i],z=x+c*a-b;b=a;a=z;e+=x*x;}return e<n*250**2?0:2*(a*a+b*b-c*a*b)/(n*e);}
  push(x){const i=this.at%N;this.ring[i]=this.ring[i+N]=x;this.at++;if(this.at<this.scan+650)return;const s=this.scan;this.scan+=16;this.scans++;if(cfg.some(([n,a,b])=>this.score(s,n,a)>=.72&&this.score(s+n,n,b)>=.72)){this.last=this.at;this.hits++;}}
}
class CandidateReceiver extends EpochReceiver {
  constructor(emit,mode='candidate',budget=4){super(emit,'cooldown',budget);if(!['candidate','fixed4096','fixed1920'].includes(mode))throw Error('mode');this.mode=mode;this.history=new Int16Array(mode==='fixed1920'?1920:HISTORY);this.observer=null;}
  observe(){const from=Math.max(0,this.at-1024);this.observer=new OnsetObserver(from);for(let j=from;j<this.at;j++)this.observer.push(this.history[j%this.history.length]);}
  push(p){if(this.closed||!(p instanceof Int16Array)||!Number.isSafeInteger(this.at+p.length))throw Error('input');for(const x of p){this.history[this.at%this.history.length]=x;this.at++;
    if(!this.blocked){this.one[0]=x;this.stream.push(this.one);if(this.blocked&&this.mode==='candidate')this.observe();continue;}
    if(this.epoch>=this.maxResets)continue;
    if(this.observer)this.observer.push(x);
    const since=this.at-Math.max(this.overflowAt,this.observer?.last??this.overflowAt);
    if(since<(this.mode==='candidate'?WAIT:320))continue;
    const previous=this.epoch,obs=this.observer;this.epoch++;this.origin=Math.max(0,this.at-this.history.length);this.blocked=false;this.quiet=0;this.start();this.observer=null;
    this.emit({status:'rearm',epoch:this.epoch,previous,at:this.at,discardedFrom:this.overflowAt,possibleUnresolvedFrom:this.lossFrom,historyFrom:this.origin,historySamples:this.at-this.origin,trigger:this.mode,lastObservedOnset:obs?.last??null,observerScans:obs?.scans??0,observerHits:obs?.hits??0});
    this.lossFrom=null;this.overflowAt=null;for(let j=this.origin;j<this.at&&!this.blocked;j++){this.one[0]=this.history[j%this.history.length];this.stream.push(this.one);this.replayed++;}if(this.blocked&&this.mode==='candidate')this.observe();
  }}
  readiness(){return {...super.readiness(),observer:this.observer?{lastObservedOnset:this.observer.last,scans:this.observer.scans,hits:this.observer.hits}:null};}
}
module.exports={CandidateReceiver,OnsetObserver,HISTORY,WAIT};
