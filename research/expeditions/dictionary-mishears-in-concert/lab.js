'use strict';
function lab(){
const assert=(c,m)=>{if(!c)throw Error(m)};
const pop=x=>{let n=0;for(;x;x&=x-1)n++;return n};
const f=(m,x)=>m>>x&1?1:-1;
const ch=(a,x)=>1-2*(pop(a&x)%2);
const masks=Array.from({length:256},(_,i)=>i).filter(m=>(m&1)&&pop(m)===4);
const witness=[27,53,71,141],affine=[85,51,15,153];
const valids=[];let candidates=0;
for(let i=0;i<masks.length;i++)for(let j=i+1;j<masks.length;j++)for(let k=j+1;k<masks.length;k++)for(let l=k+1;l<masks.length;l++){
 const a=[masks[i],masks[j],masks[k],masks[l]];candidates++;
 const good=a.every((x,i)=>a.slice(i+1).every(y=>pop(x^y)===4))&&pop(a.reduce((x,y)=>x^y,0))===4;
 const sig=Array.from({length:8},(_,x)=>a.reduce((s,m,i)=>s|((f(m,x)>0?1:0)<<i),0));
 const direct=new Set(sig.map(s=>Math.min(s,15^s))).size===8;
 assert(good===direct,"antipodal criterion");if(good)valids.push(a);
}
const conv=(m,p)=>Array.from({length:8},(_,y)=>p.reduce((s,v,e)=>s+v*f(m,y^e),0));
const score=(m,p)=>conv(m,p).reduce((s,v)=>s+Math.abs(v),0); // denominator 8 sum(p)
const endpoint=[1,1,1,0,1,0,0,0];
const strong=masks.filter(m=>score(m,endpoint)>8);
assert(strong.length===4&&valids.every(a=>a.some(m=>score(m,endpoint)<=8)),"upper certificate");
assert(strong.every(m=>Array.from({length:8},(_,a)=>a).some(a=>pop(a)%2&&Array.from({length:8},(_,x)=>x).every(x=>f(m,x)===ch(a,x)))),"odd characters");
const spectra=witness.map(m=>Array.from({length:8},(_,a)=>Array.from({length:8},(_,x)=>f(m,x)*ch(a,x)).reduce((a,b)=>a+b,0)));
assert(spectra.every(s=>s.filter((v,a)=>Math.abs(v)===4&&pop(a)===1).length===2&&s.filter((v,a)=>Math.abs(v)===4&&pop(a)===2).length===2&&s.reduce((t,v)=>t+v*v,0)===64),"witness spectrum");
const one=spectra.map(s=>s.findIndex((v,a)=>Math.abs(v)===4&&pop(a)===1));
let enumerated=0,qualified=0,decoderChecks=0,lawBlindChecks=0;const worst={};
function verify(p,D){
 enumerated++;
 const q=[1,2,4].map(a=>p.reduce((s,v,e)=>s+((e&a)?v:0),0));
 if(q[0]!==q[1]||q[0]!==q[2]||2*q[0]>D)return;
 qualified++;
 const n=q[0],bound=4*(D-2*n+Math.max(0,D-4*n)); // 8D times robust T
 for(let i=0;i<4;i++){
  const m=witness[i],v=conv(m,p),sc=v.reduce((s,x)=>s+Math.abs(x),0);
  assert(sc>=bound,"Bayes robust lower");
  const d=y=>4*n<=D?f(m,y):Math.sign(spectra[i][one[i]])*ch(one[i],y);
  let acc=0;
  for(let y=0;y<8;y++){
   // Unnormalized conditional rows P(y|i,+/-), denominator 4D.
   const plus=p.reduce((s,w,e)=>s+w*(f(m,y^e)===1),0),minus=p.reduce((s,w,e)=>s+w*(f(m,y^e)===-1),0);
   assert(plus-minus===v[y]&&plus+minus===D,"direct conditional row");
   decoderChecks++;acc+=d(y)*(plus-minus);
  }
  assert(acc>=bound,"law-blind lower");lawBlindChecks++;
  worst[n]=Math.min(worst[n]??Infinity,sc);
 }
}
for(const D of [4,8,12]){
 const p=Array(8).fill(0);
 function compositions(i,left){if(i===7){p[i]=left;verify(p,D);return}for(let n=0;n<=left;n++){p[i]=n;compositions(i+1,left-n)}}
 compositions(0,D);
 // Explicit upper law, scale denominator to avoid rational mixture.
 for(let n=0;n<=D/2;n++){
  const P=4*n<=D?[8*(D-3*n),8*n,8*n,0,8*n,0,0,0]:endpoint.map(v=>v*(4*D-8*n)+(4*n-D)); // endpoint weights must scale: mixture w=(2D-4n)/D, endpoint/4; 8D denominator -> 2(2D-4n) v plus (4n-D)
  assert(P.reduce((a,b)=>a+b,0)===8*D,"upper normalization");
  assert([1,2,4].every(a=>P.reduce((s,v,e)=>s+((e&a)?v:0),0)===8*n),"upper marginals");
  const scores=new Map(masks.map(m=>[m,score(m,P)]));
  const upper=Math.max(...valids.map(a=>Math.min(...a.map(m=>scores.get(m)))));
  assert(upper===32*(D-2*n+Math.max(0,D-4*n)),"upper optimum");
 }
}
function audit(a,p){
 const D=p.reduce((s,x)=>s+x,0),v=a.map(m=>conv(m,p));
 let max=0,targets=0;
 for(let mask=0;mask<256;mask++)if(pop(mask)===4){
  let s=0;
  for(let y=0;y<8;y++){
   let A=0,B=0;
   for(let i=0;i<4;i++){A+=((mask>>(2*i))&1)?D+v[i][y]:0;A+=((mask>>(2*i+1))&1)?D-v[i][y]:0;
    B+=((mask>>(2*i))&1)?0:D+v[i][y];B+=((mask>>(2*i+1))&1)?0:D-v[i][y];}
   s+=Math.max(A,B);
  }max=Math.max(max,s);targets++;
 }
 return {T:v.map(row=>row.reduce((a,b)=>a+Math.abs(b),0)/(8*D)),V:max/(64*D),targets};
}
const examples={};for(const [name,p] of Object.entries({exclusive:[7,1,1,0,1,0,0,0],independent:Array.from({length:8},(_,e)=>9**(3-pop(e))),common:[9,0,0,0,0,0,0,1]}))examples[name]={affine:audit(affine,p),nonlinear:audit(witness,p)};
assert(examples.exclusive.nonlinear.T.every(v=>v===.7)&&examples.common.nonlinear.T.every(v=>v===.9),"same marginals control");
assert(examples.common.nonlinear.V===.6875&&examples.independent.nonlinear.V===.65,"privacy change");
const pairwise=[ [7,2,2,1,2,1,1,0],[6,3,3,0,3,0,0,1] ]; // both marginals 4/16 and pair intersections 1/16
const independent=Array.from({length:8},(_,e)=>3**(3-pop(e)));
const zeroTriple=pairwise[0].map((v,i)=>v+pairwise[1][i]);
assert([pairwise[0],pairwise[1],zeroTriple].every(p=>{const D=p.reduce((a,b)=>a+b,0);return [1,2,4].every(a=>4*p.reduce((s,v,e)=>s+((e&a)?v:0),0)===D)&&[3,5,6].every(a=>16*p.reduce((s,v,e)=>s+((e&a)===a?v:0),0)===D)}),"pairwise control");
assert(score(105,pairwise[0])===32&&score(105,zeroTriple)===0,"third-order distinction");
return {candidates,valid:valids.length,strong,spectra,enumerated,qualified,decoderChecks,lawBlindChecks,examples,pairwise:{nonzero:score(105,pairwise[0])/128,zero:score(105,zeroTriple)/256}};
}
console.log(JSON.stringify(lab(),null,2));
