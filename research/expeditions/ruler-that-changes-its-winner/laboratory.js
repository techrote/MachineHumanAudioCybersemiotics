"use strict";
// MHAC #244 — exact bounded integer/rational laboratory. Node.js, no dependencies.
function assert(b,msg){if(!b)throw Error(msg)}

function gcd(a,b){a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b]}return a||1}

function frac(n,d=1){assert(d!==0,"zero denominator");if(d<0){n=-n;d=-d}let g=gcd(n,d);return [n/g,d/g]}

function cmp(a,b){return Math.sign(a[0]*b[1]-b[0]*a[1])}

function value(a,b,t){return frac(a*t[0]+b*(t[1]-t[0]),t[1])}

function maxf(a,b){return cmp(a,b)>=0?a:b}

function minf(a,b){return cmp(a,b)<=0?a:b}

function cross(a,b,c,d){let den=(a-b)-(c-d);if(!den)return null;let t=frac(d-b,den);return cmp(t,[0,1])>=0&&cmp(t,[1,1])<=0?t:null}

function points(lines){let ts=[[0,1],[1,1]];for(let i=0;i<lines.length;i++)for(let j=i+1;j<lines.length;j++){let t=cross(...lines[i],...lines[j]);if(t)ts.push(t)}return ts}

function permutations(xs){if(!xs.length)return [[]];return xs.flatMap((x,i)=>permutations(xs.filter((_,j)=>j!==i)).map(a=>[x,...a]))}

function* compositions(n,k){if(k===1){yield [n];return}for(let i=0;i<=n;i++)for(const tail of compositions(n-i,k-1))yield [i,...tail]}

function ranks(ballots,counts){
 const m=ballots[0].length,n=counts.reduce((a,b)=>a+b,0);
 assert(n>0&&m>=2&&counts.length===ballots.length,"bad size");
 assert(ballots.every(b=>b.length===m&&[...b].sort((x,y)=>x-y).every((x,i)=>x===i)),"bad ballot");
 assert(counts.every(c=>Number.isSafeInteger(c)&&c>=0),"bad count");
 const R=Array.from({length:m},()=>Array(m-1).fill(0));
 for(let i=0;i<ballots.length;i++)for(let k=0;k<m-1;k++)for(let r=0;r<=k;r++)R[ballots[i][r]][k]+=counts[i];
 return R
}

function losses(R){let M=R[0].map((_,k)=>Math.max(...R.map(r=>r[k])));return R.map(r=>r.map((v,k)=>M[k]-v))}

function pure(L){return Math.min(...L.map(r=>Math.max(...r)))}

function mixed2(L){
 assert(L.every(r=>r.length===2),"two thresholds required");
 let best={v:[Infinity,1],i:0,j:0,t:[1,1]};
 for(let i=0;i<L.length;i++)for(let j=i;j<L.length;j++){
  let ts=[[0,1],[1,1]],t=cross(L[i][0],L[j][0],L[i][1],L[j][1]);if(t)ts.push(t);
  for(const q of ts){let v=maxf(value(L[i][0],L[j][0],q),value(L[i][1],L[j][1],q));
   if(best.v[0]===Infinity||cmp(v,best.v)<0)best={v,i,j,t:q}}
 }
 return best
}

function dual2(L){
 let best={v:[-1,1],t:[0,1]};
 for(const t of points(L)){let v=L.map(r=>value(...r,t)).reduce(minf);if(cmp(v,best.v)>0)best={v,t}}
 return best
}

function possible2(R){const s=new Set();for(const t of points(R)){const vs=R.map(r=>value(...r,t)),v=vs.reduce(maxf);vs.forEach((x,i)=>{if(cmp(x,v)===0)s.add(i)})}return [...s].sort((a,b)=>a-b)}

function condorcet(ballots,counts){
 const n=counts.reduce((a,b)=>a+b,0),m=ballots[0].length;
 return Array.from({length:m},(_,i)=>i).filter(i=>Array.from({length:m},(_,j)=>j).every(j=>i===j||2*ballots.reduce((a,b,k)=>a+(b.indexOf(i)<b.indexOf(j)?counts[k]:0),0)>n))
}

function family(m){
 assert(Number.isInteger(m)&&m>=3&&m<=12,"bounded dimension");
 const d=m-1,N=m*m,L=Array.from({length:m},(_,i)=>Array.from({length:d},(_,k)=>i===k||i===d?m:0));
 const R=L.map(row=>row.map((v,k)=>(k+1)*m+2-v));
 const H=R.map(r=>[r[0],...r.slice(1).map((v,k)=>v-r[k]),N-r[d-1]]);
 assert(H.every(row=>row.every(x=>x>=0)&&row.reduce((a,b)=>a+b,0)===N),"row balance");
 assert(H[0].every((_,k)=>H.reduce((s,r)=>s+r[k],0)===N),"column balance");
 // Realize integer doubly stochastic counts by repeated perfect matching.
 let remaining=H.map(r=>[...r]),ballots=[];
 function match(k,used,order){if(k===m)return [...order];for(let i=0;i<m;i++)if(!used.has(i)&&remaining[i][k]>0){used.add(i);order.push(i);let result=match(k+1,used,order);if(result)return result;order.pop();used.delete(i)}return null}
 for(let i=0;i<N;i++){let b=match(0,new Set(),[]);assert(b,"Hall matching");b.forEach((x,k)=>remaining[x][k]--);ballots.push(b)}
 const actual=ranks(ballots,Array(N).fill(1));assert(JSON.stringify(actual)===JSON.stringify(R),"realization mismatch");
 assert(JSON.stringify(losses(R))===JSON.stringify(L),"loss mismatch");
 // Uniform mix over d specialized choices and uniform adversarial threshold
 // furnish primal/dual certificates. Every pure action has maximum m.
 assert(pure(L)===m&&L.every(r=>r.reduce((s,x)=>s+x,0)>=m),"dual");
 assert(L[0].every((_,k)=>L.slice(0,d).reduce((s,r)=>s+r[k],0)===m),"primal");
 return {m,voters:N,deterministic:m,mixed:frac(m,d),ratio:d,rank_counts:H,ballots}
}

function wave(R,t){
 // Two segments per candidate, fixed amplitude and square-wave pitch label
 // with frequency determined by integer weighted score; deterministic PCM.
 const m=R.length,rate=8000,segment=800,frames=m*segment,bytes=new Uint8Array(44+frames*2),v=new DataView(bytes.buffer);
 function ascii(off,s){for(let i=0;i<s.length;i++)bytes[off+i]=s.charCodeAt(i)}
 ascii(0,"RIFF");v.setUint32(4,bytes.length-8,true);ascii(8,"WAVE");ascii(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);ascii(36,"data");v.setUint32(40,frames*2,true);
 R.forEach((r,i)=>{let score=value(...r,t);let f=220+Math.round(40*score[0]/score[1]);for(let j=0;j<segment;j++){let env=Math.min(j,segment-1-j,40);let s=(Math.floor(2*f*j/rate)%2?1:-1)*env*120;v.setInt16(44+2*(i*segment+j),s,true)}});
 return bytes
}

function fingerprint(bytes){let h=2166136261;for(let x of bytes){h=Math.imul(h^x,16777619)>>>0}return h.toString(16).padStart(8,"0")}

function run(){
 const B=permutations([0,1,2]),rows=[],witnesses={};
 for(let n=1;n<=10;n++){
  let row={voters:n,profiles:0,no_robust_winner:0,mixed_strictly_better:0,borda_excess:0,condorcet_not_robust:0,nonpossible_pure_minimax:0,sharp_factor_two:0};
  for(let c of compositions(n,6)){
   let R=ranks(B,c),L=losses(R),p=pure(L),mix=mixed2(L),dual=dual2(L),possible=possible2(R);
   assert(cmp(mix.v,dual.v)===0,"primal/dual gap");
   assert(cmp(mix.v,[p,1])<=0&&cmp([2*mix.v[0],mix.v[1]],[p,1])>=0,"factor bound");
   let winners=L.map((r,i)=>Math.max(...r)===p?i:-1).filter(i=>i>=0),bs=R.map(r=>r[0]+r[1]),borda=bs.map((v,i)=>v===Math.max(...bs)?i:-1).filter(i=>i>=0),cw=condorcet(B,c);
   row.profiles++;
   if(p>0)row.no_robust_winner++;
   if(cmp(mix.v,[p,1])<0){row.mixed_strictly_better++;witnesses.mixed??={counts:c,R,L,p,mix,dual}}
   if(borda.every(i=>Math.max(...L[i])>p)){row.borda_excess++;witnesses.borda??={counts:c,R,L,p,borda}}
   if(cw.length&&Math.max(...L[cw[0]])>0){row.condorcet_not_robust++;witnesses.condorcet??={counts:c,R,L,p,cw}}
   if(winners.some(i=>!possible.includes(i))){row.nonpossible_pure_minimax++;witnesses.nonpossible??={counts:c,R,L,p,winners,possible}}
   if(p>0&&cmp([2*mix.v[0],mix.v[1]],[p,1])===0){row.sharp_factor_two++;witnesses.sharp??={counts:c,R,L,p,mix,dual}}
  }
  rows.push(row)
 }
 const families=Array.from({length:10},(_,i)=>family(i+3));
 const R=witnesses.sharp.R,a=wave(R,[1,1]),b=wave(R,[0,1]),mid=wave(R,[1,2]);assert(a.length===4844&&a.length===b.length,"WAV size");
 assert(a.some((x,i)=>x!==b[i]),"policy audio must differ");
 assert(a.every((x,i)=>x===wave(R,[1,1])[i]),"determinism");
 // endpoints and same-score control: unanimity.
 assert(pure(losses(ranks(B,[1,0,0,0,0,0])))===0,"unanimity");
 let refused=false;try{ranks(B,[-1,2,0,0,0,0])}catch{refused=true}assert(refused,"negative counts rejected");
 return {schema:"mhac-ruler-v1",ballot_order:B,rows,totals:Object.fromEntries(Object.keys(rows[0]).filter(k=>k!=="voters").map(k=>[k,rows.reduce((s,r)=>s+r[k],0)])),witnesses,families:families.map(({ballots,...rest})=>({...rest,first_ballots:ballots.slice(0,3)})),audio:{bytes:a.length,plurality_fnv1a32:fingerprint(a),veto_fnv1a32:fingerprint(b),borda_fnv1a32:fingerprint(mid),note:"FNV-1a is a reproducibility fingerprint, not cryptographic custody"}}
}

if(require.main===module){const r=run(); console.log(JSON.stringify(r,null,2)); if(process.argv[2]){const fs=require('node:fs');const dir=process.argv[2];fs.mkdirSync(dir,{recursive:true});for(const [name,t] of [['plurality',[1,1]],['veto',[0,1]],['borda',[1,2]]])fs.writeFileSync(require('node:path').join(dir,name+'.wav'),wave(r.witnesses.sharp.R,t));}}
module.exports={ranks,losses,pure,mixed2,dual2,possible2,family,wave,run};
