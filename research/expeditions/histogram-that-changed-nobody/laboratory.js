"use strict";
// Original synthetic laboratory; run node laboratory.js [--wav-dir DIR].
function assert(ok,msg){if(!ok)throw Error(msg)}

function validate(h){if(!Array.isArray(h)||!h.length||h.some(x=>!Number.isSafeInteger(x)||x<0)||!Number.isSafeInteger(h.reduce((a,b)=>a+b,0)))throw Error("invalid histogram")}

function witness(h,a,b){validate(h);if(![a,b].every(x=>Number.isSafeInteger(x)&&x>=0))throw Error("weights must be nonnegative integers");const k=h.length,M=Array.from({length:k},()=>Array(k).fill(0));for(let j=1;j<=Math.max(...h);j++){const s=h.map((v,i)=>v>=j?i:-1).filter(i=>i>=0);if(a*(s.length-1)>b){for(let i=0;i<s.length;i++)M[s[i]][s[(i+1)%s.length]]++}else for(const i of s)M[i][i]++}return M}

function bound(h,a,b){validate(h);if(![a,b].every(x=>Number.isSafeInteger(x)&&x>=0))throw Error("invalid weights");if(a===0)return 0;const s=[...h].sort((x,y)=>y-x),N=s.reduce((x,y)=>x+y,0);if(!Number.isSafeInteger(a*N)||!Number.isSafeInteger(b*N))throw Error("unsafe score");const q=1+Math.floor(b/a);if(q>=s.length)return 0;return a*(N-s.slice(0,q).reduce((x,y)=>x+y,0))-(b%a)*s[q]}

function counts(M){let B=0,H=0,T=0;for(let i=0;i<M.length;i++)for(let j=0;j<M.length;j++){const x=M[i][j];if(i<j)B+=x;else if(i>j)H+=x;else T+=x}return {B,H,T}}

function checkMargins(M,h){for(let i=0;i<h.length;i++){assert(M[i].reduce((a,b)=>a+b,0)===h[i],"row");assert(M.reduce((s,row)=>s+row[i],0)===h[i],"col")}}

function* compositions(N,k){if(k===1){yield [N];return}for(let i=0;i<=N;i++)for(const tail of compositions(N-i,k-1))yield [i,...tail]}

function* allocations(N,cap){if(cap.length===1){if(N<=cap[0])yield [N];return}for(let x=0;x<=Math.min(N,cap[0]);x++)for(const tail of allocations(N-x,cap.slice(1)))yield [x,...tail]}

function* matrices(h,i=0,cap=h,rows=[]){if(i===h.length){if(cap.every(x=>x===0))yield rows;return}for(const row of allocations(h[i],cap))yield* matrices(h,i+1,cap.map((x,j)=>x-row[j]),[...rows,row])}

function wav(pairs){const frames=160,payload=pairs.length*frames*4,out=new Uint8Array(44+payload),v=new DataView(out.buffer);function txt(off,s){for(let i=0;i<s.length;i++)out[off+i]=s.charCodeAt(i)}txt(0,"RIFF");v.setUint32(4,36+payload,true);txt(8,"WAVE");txt(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,2,true);v.setUint32(24,8000,true);v.setUint32(28,32000,true);v.setUint16(32,4,true);v.setUint16(34,16,true);txt(36,"data");v.setUint32(40,payload,true);for(let i=0;i<pairs.length;i++)for(let t=0;t<frames;t++)for(let c=0;c<2;c++){const f=200+100*pairs[i][c],sample=t<8||t>=frames-8?0:(Math.floor(2*f*t/8000)%2?6000:-6000);v.setInt16(44+4*(i*frames+t)+2*c,sample,true)}return out}

function fingerprint(b){let h=2166136261;for(const x of b)h=Math.imul(h^x,16777619);return (h>>>0).toString(16).padStart(8,"0")}

function paired(M){const out=[];for(let i=0;i<M.length;i++)for(let j=0;j<M.length;j++)for(let z=0;z<M[i][j];z++)out.push([i,j]);return out}

function marginal(M){const p=paired(M),x=p.map(z=>z[0]).sort((a,b)=>a-b),y=p.map(z=>z[1]).sort((a,b)=>a-b);return x.map((a,i)=>[a,y[i]])}

function equal(a,b){return a.length===b.length&&a.every((x,i)=>x===b[i])}

function experiment(){const weights=[[1,0],[2,1],[1,1],[2,3],[1,2],[1,3],[1,4],[0,1],[0,0]],summary=[];let comparisons=0,aliasHistograms=0;for(let k=1;k<=5;k++){let profiles=0,tables=0,ambiguous=0;for(let N=0;N<=6;N++)for(const h of compositions(N,k)){profiles++;const lo=weights.map(()=>Infinity),hi=weights.map(()=>-Infinity);for(const M of matrices(h)){tables++;const {B,H}=counts(M);weights.forEach(([a,b],i)=>{const z=a*B-b*H;lo[i]=Math.min(lo[i],z);hi[i]=Math.max(hi[i],z)})}if(hi[2]>0)ambiguous++;weights.forEach(([a,b],i)=>{const M=witness(h,a,b);checkMargins(M,h);const {B,H}=counts(M);assert(hi[i]===bound(h,a,b)&&lo[i]===-bound(h,b,a)&&a*B-b*H===hi[i],"extrema mismatch "+JSON.stringify({h,a,b}));comparisons+=3})}aliasHistograms+=ambiguous;summary.push({k,profiles,tables,ambiguous})}let stratificationCases=0,strict=0;const hs=[];for(let N=0;N<=3;N++)hs.push(...compositions(N,4));for(const h of hs)for(const g of hs)for(const [a,b] of weights){const pooled=bound(h.map((x,i)=>x+g[i]),a,b),split=bound(h,a,b)+bound(g,a,b);assert(split<=pooled,"strata violation");stratificationCases++;if(split<pooled)strict++}
const positive=witness([1,1,1],1,1),negative=positive[0].map((_,j)=>positive.map(row=>row[j])),identity=witness([1,1,1],1,3);const scores=[positive,negative,identity].map(M=>({counts:counts(M),paired:wav(paired(M)),marginal:wav(marginal(M))}));assert(scores.every(s=>equal(s.marginal,scores[0].marginal)),"marginal alias failed");assert(!equal(scores[0].paired,scores[1].paired)&&!equal(scores[0].paired,scores[2].paired)&&!equal(scores[1].paired,scores[2].paired),"paired collision");let rejected=0;for(const h of [[],[-1],[1.5],[NaN]]){try{bound(h,1,1)}catch(e){rejected++}}assert(rejected===4,"bad input accepted");return {summary,comparisons,aliasHistograms,stratificationCases,strict,rejected,weights,audio:scores.map(s=>({counts:s.counts,bytes:s.paired.length,paired_fnv1a:fingerprint(s.paired),marginal_fnv1a:fingerprint(s.marginal)}))}}

if (require.main === module) {
 const result = experiment(); console.log(JSON.stringify(result,null,2));
 if (process.argv[2] === "--wav-dir") { const fs=require("node:fs"),path=require("node:path"),dir=process.argv[3]; fs.mkdirSync(dir,{recursive:true}); const pos=witness([1,1,1],1,1),neg=pos[0].map((_,j)=>pos.map(row=>row[j])),id=witness([1,1,1],1,3); for(const [name,M] of [["up",pos],["down",neg],["identity",id]]) for(const [kind,p] of [["paired",paired(M)],["marginal",marginal(M)]]) fs.writeFileSync(path.join(dir,name+"-"+kind+".wav"),wav(p)); }
}
module.exports={bound,witness,counts,matrices,experiment,wav,paired,marginal};
