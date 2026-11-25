"use strict";
// MHAC #448 synthetic model. See README-quadratic.md.
const books={"source8":[[0,1,4,13],[0,1,5,6],[0,1,10,17],[0,1,11,12],[0,1,14,18],[0,1,15,16],[0,2,7,18],[0,2,11,13]],"source8_searched":[[0,3,8,17],[0,9,12,13],[0,1,10,17],[0,9,14,17],[0,1,4,13],[0,7,16,17],[0,3,11,14],[0,2,15,17]],"robust8":[[0,2,15,17],[0,3,5,8],[0,2,7,9],[0,1,17,18],[0,1,2,3],[0,5,6,11],[0,3,4,7],[0,1,11,12]]};
function experiment(books,prior){
 const rate=8000,ticks=16000,S0=9600,S1=16000;
 let checks=0,vertexChecks=0,fits=0;
 const check=(ok,msg)=>{checks++;if(!ok)throw Error(msg)};
 // Constraints A*s+B*b<=C, after eliminating translation.
 function rows(t,y,e,D,extra){
  const L=t.L,g=x=>4*x*(L-x),lower=t.x.map((x,i)=>[x,g(x),y[i]-e]),upper=t.x.map((x,i)=>[x,g(x),y[i]+e]);
  if(extra!==undefined){lower.push([L,0,extra-1]);upper.push([0,0,extra+1]);}
  const a=[[1,0,S1],[-1,0,-S0],[0,1,D],[0,-1,D]];
  for(const l of lower)for(const u of upper)a.push([(u[0]-l[0])*L,u[1]-l[1],(u[2]-l[2])*L*L]);
  return a;
 }
 function exact(a){
  const lo=[],hi=[],z=[];
  for(const [A,B,C] of a)if(A<0)lo.push([-A,-B,-C]);else if(A>0)hi.push([A,B,C]);else z.push([B,C]);
  for(const [a,b,c] of lo)for(const [d,f,h] of hi)z.push([f*a-b*d,h*a-c*d]);
  let ln=0,ld=1,un=0,ud=1,hasL=false,hasU=false;
  const le=(n,d,p,q)=>{const x=n*q,y=p*d;if(!Number.isSafeInteger(x)||!Number.isSafeInteger(y))throw Error("unsafe cross-product");return x<=y};
  for(let [B,C] of z){
   if(B===0){if(C<0)return false;continue;}
   if(B>0){if(!hasU||le(C,B,un,ud)){un=C;ud=B;hasU=true;}}
   else{B=-B;C=-C;if(!hasL||le(ln,ld,C,B)){ln=C;ld=B;hasL=true;}}
   if(hasL&&hasU&&!le(ln,ld,un,ud))return false;
  }
  return true;
 }
 // Independent algorithm: enumerate bounded polygon vertices in BigInt.
 function vertex(a){
  const q=a.map(r=>r.map(BigInt));
  for(let i=0;i<q.length;i++)for(let j=i+1;j<q.length;j++){
   const [A,B,C]=q[i],[D,E,F]=q[j];let den=A*E-B*D;if(den===0n)continue;
   let s=C*E-B*F,b=A*F-C*D;if(den<0n){den=-den;s=-s;b=-b;}
   if(q.every(([a,b0,c])=>a*s+b0*b<=c*den))return true;
  }return false;
 }
 function fit(t,y,e,D,extra){
  const a=rows(t,y,e,D,extra),r=exact(a);fits++;
  if(fits<=300||fits%4093===0){check(r===vertex(a),"vertex agreement");vertexChecks++;}
  return r;
 }
 const t={L:2,x:[0,1,2]};
 check(fit(t,[0,4960,9600],0,160),"positive boundary");
 check(!fit(t,[0,4961,9600],0,160),"positive outside");
 check(fit(t,[0,4640,9600],0,160),"negative boundary");
 check(!fit(t,[0,4639,9600],0,160),"negative outside");
 check(!fit(t,[0,4800,9600],0,0,10000),"false onset outside");
 check(fit(t,[0,4800,9600],0,0,9601),"false rounding boundary");
 const rng=seed=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 function envelope(t,y,e){
  let lo=S0,hi=S1;
  for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){const d=t.x[j]-t.x[i],q=y[j]-y[i];lo=Math.max(lo,(q-2*e)*t.L/d);hi=Math.min(hi,(q+2*e)*t.L/d);}
  return lo<=hi+1e-7;
 }
 const counter=()=>({correct:0,wrong:0,abstain:0,truth_omitted:0});
 function decide(c,p,id){if(!p.includes(id))c.truth_omitted++;if(p.length!==1)c.abstain++;else if(p[0]===id)c.correct++;else c.wrong++}
 const runs={};
 for(const [dataset,seeds,repeats] of [["replay",[1201,1709,2089],16],["heldout",[3011,4027,5009],8]]){
  const results={};
  for(const [name,words] of Object.entries(books)){
   const ts=words.map(w=>w.map((_,d)=>({L:w[3],x:w.filter((_,i)=>i!==d)}))),conditions=[];
   for(const insert of [false,true])for(const warp of [0,.005,.015])for(const jitter of [0,.002]){
    const D=Math.round(warp*ticks),e=Math.round(jitter*ticks)+1,counts={envelope:counter(),quadratic:counter(),quadratic_insertion_bound:counter()};
    let invalid=0,total=0,strictNarrow=0,extraNarrow=0;const examples={};
    for(const seed of seeds){const rand=rng(seed);for(let id=0;id<8;id++)for(let d=0;d<4;d++)for(let k=0;k<repeats;k++){
     const scale=.6+.4*rand(),off=.1+.1*rand(),bend=warp*(2*rand()-1);
     const raw=ts[id][d].x.map(v=>{const x=v/ts[id][d].L;return off+scale*x+4*bend*x*(1-x)+jitter*(2*rand()-1)});
     const falseTime=off+scale*rand();if(insert)raw.push(falseTime);
     const y=raw.map(x=>2*Math.round(x*rate)).sort((a,b)=>a-b);total++;
     if(new Set(y).size!==y.length){invalid++;continue;}
     const ys=insert?y.map((extra,i)=>({y:y.filter((_,j)=>i!==j),extra})):[{y}];
     const wide=[],quad=[],bound=[];
     for(let w=0;w<8;w++){
      let W=false,Q=false,F=false;
      for(const t of ts[w])for(const a of ys){
       if(!envelope(t,a.y,e+D))continue;
       W=true;if(F)continue;
       if(!fit(t,a.y,e,D))continue;
       Q=true;if(!insert||fit(t,a.y,e,D,a.extra))F=true;
      }
      if(W)wide.push(w);if(Q)quad.push(w);if(F)bound.push(w);
     }
     check(wide.includes(id)&&quad.includes(id)&&bound.includes(id),"true label");
     check(quad.every(x=>wide.includes(x))&&bound.every(x=>quad.includes(x)),"nested sets");
     if(D===0)check(wide.join()===quad.join(),"affine equality");
     if(quad.length<wide.length)strictNarrow++;
     if(bound.length<quad.length)extraNarrow++;
     if(wide.length>1&&quad.length===1&&!examples.quadratic_rescue)examples.quadratic_rescue={seed,id,d,k,scale,off,bend,receipt_half_sample_ticks:y,wide,quad,bound};
     if(quad.length>1&&bound.length===1&&!examples.insertion_bound_rescue)examples.insertion_bound_rescue={seed,id,d,k,scale,off,bend,receipt_half_sample_ticks:y,wide,quad,bound};
     decide(counts.envelope,wide,id);decide(counts.quadratic,quad,id);decide(counts.quadratic_insertion_bound,bound,id);
    }}
    for(const c of Object.values(counts))check(c.correct+c.wrong+c.abstain+invalid===total&&c.wrong===0&&c.truth_omitted===0,"accounting");
    if(dataset==="replay"&&prior){const p=prior.results[name].conditions.find(v=>v.insert===insert&&v.warp_ms===warp*1000&&v.jitter_ms===jitter*1000);check(p.invalid===invalid&&JSON.stringify(p.envelope)===JSON.stringify(counts.envelope),"run 002 reproduction "+name+" "+insert+" "+warp+" "+jitter);}
    conditions.push({insert,warp_ms:warp*1000,jitter_ms:jitter*1000,total,invalid,strictNarrow,extraNarrow,...counts,examples});
   }
   results[name]={conditions};
  }
  runs[dataset]={seeds,repeats,results};
 }
 return {schema:"mhac-448-quadratic-v1",source_head:"e9c7dc8a1d7e9c1dae54b767bc6efd96f5147d0a",rate,half_sample_ticks_per_second:ticks,checks,vertexChecks,fits,runs};
}
module.exports={experiment,books};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");const out=process.argv[2];if(!out)throw Error("usage: node quadratic.cjs OUTPUT_DIRECTORY");const prior=JSON.parse(fs.readFileSync(path.join(__dirname,"false-onset-receipt.json"),"utf8"));const r=experiment(books,prior);fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,"quadratic-receipt.json"),JSON.stringify(r,null,2)+"\n");console.log("assertions",r.checks,"vertex checks",r.vertexChecks);}
