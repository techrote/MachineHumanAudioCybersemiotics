"use strict";
// Synthetic exact integer checks. B=4*b; receiver actions are rational means.
function compositions(n) {
  if (n===0) return [[]];
  const out=[];
  for(let i=1;i<=n;i++) for(const tail of compositions(n-i)) out.push([i,...tail]);
  return out;
}

function partitions(n) {
  const out=[];
  function rec(i,blocks) {
    if(i===n){out.push(blocks.map(b=>[...b]));return;}
    for(const b of blocks){b.push(i);rec(i+1,blocks);b.pop();}
    rec(i+1,[...blocks,[i]]);
  }
  rec(0,[]);return out;
}

function checkInput(n,B) {
  if(!Number.isInteger(n)||n<1||n>10000||!Number.isInteger(B)||Math.abs(B)>1000000) throw Error("n=1..10000 and integer quarter-bias B within +/-1000000 required");
}

function boundaryOK(lens,B) {
  for(let i=1;i<lens.length;i++) if(Math.abs(lens[i]-lens[i-1]-B)>2)return false;
  return true;
}

function maxActions(n,B) {
  checkInput(n,B);const d=Math.max(0,Math.abs(B)-2);
  let k=1;
  while(k<n && (k+1)+d*k*(k+1)/2<=n) k++;
  return k;
}

function witness(n,B) {
  const k=maxActions(n,B), d=Math.max(0,Math.abs(B)-2);
  const extra=n-k-d*k*(k-1)/2, q=Math.floor(extra/k), rem=extra%k;
  const lens=Array.from({length:k},(_,i)=>1+i*d+q+(i>=k-rem?1:0));
  return B<0?lens.reverse():lens;
}

function contiguous(lens) {
  let t=0;return lens.map(l=>Array.from({length:l},()=>t++));
}

function directOracle(blocks,B) {
  const stats=blocks.map(b=>({sum:b.reduce((s,t)=>s+t,0),n:b.length}));
  for(let i=0;i<blocks.length;i++)for(const t of blocks[i]){
    const x=4*t+B, a=stats[i], own=(4*a.sum-x*a.n)**2;
    for(const b of stats)if((4*b.sum-x*b.n)**2*a.n*a.n < own*b.n*b.n)return false;
  }
  return true;
}

function distinctActions(blocks){
  const actions=[];
  for(const b of blocks){
    const s=b.reduce((a,t)=>a+t,0), n=b.length;
    if(!actions.some(a=>a.s*n===s*a.n))actions.push({s,n});
  }
  return actions.length;
}

function loss12n(lens){return lens.reduce((s,l)=>s+l*l*l-l,0);}

function penalty2(n,B) {
  checkInput(n,B);
  const x=Math.min(n-1,Math.abs(B)/4);
  return Math.max(...[Math.floor(x),Math.ceil(x)].map(d=>Math.abs(B)*d-2*d*d));
}

function directPenalty2(n,B){
  let mx=0;
  for(let t=0;t<n;t++)for(let j=0;j<n;j++){
    const d=j-t;
    // Squared losses in units of 1/16; multiply their difference by 1/8.
    mx=Math.max(mx,(B*B-(4*d-B)**2)/8);
  }
  return mx;
}

function requireTest(v,msg){if(!v)throw Error(msg);}

function run(){
  const receipt={compositionChecks:0,maximumChecks:0,witnessChecks:0,arbitraryPartitionChecks:0,arbitraryMaximumChecks:0,penaltyChecks:0,namedChecks:0,refusals:0,frontier:[]};
  for(let n=1;n<=14;n++){
    const cs=compositions(n);
    for(let B=-24;B<=24;B++){
      let best=0;
      for(const l of cs){
        const boundary=boundaryOK(l,B);
        requireTest(boundary===directOracle(contiguous(l),B),"composition mismatch "+n+" "+B+" "+l);
        receipt.compositionChecks++;
        if(boundary)best=Math.max(best,l.length);
      }
      requireTest(best===maxActions(n,B),"max mismatch");receipt.maximumChecks++;
      const w=witness(n,B);
      requireTest(w.reduce((s,v)=>s+v,0)===n && w.length===best && w.every(v=>v>=1) && directOracle(contiguous(w),B),"bad witness");receipt.witnessChecks++;
    }
  }
  for(let n=1;n<=8;n++){
    const ps=partitions(n);
    for(let B=-16;B<=16;B++){
      let best=0;
      for(const p of ps){
        if(directOracle(p,B))best=Math.max(best,distinctActions(p));
        receipt.arbitraryPartitionChecks++;
      }
      requireTest(best===maxActions(n,B),"arbitrary maximum mismatch");receipt.arbitraryMaximumChecks++;
    }
  }
  for(let n=1;n<=60;n++)for(let B=-80;B<=80;B++){
    requireTest(penalty2(n,B)===directPenalty2(n,B),"penalty mismatch");receipt.penaltyChecks++;
  }
  for(const B of [0,2,3,4,6,10,16,17]){
    const n=16, max=maxActions(n,B), w=witness(n,B);
    let bestLoss=Infinity,best=null;
    for(const l of compositions(n))if(boundaryOK(l,B)&&loss12n(l)<bestLoss){bestLoss=loss12n(l);best=l;}
    receipt.frontier.push({n,B,maxActions:max,witness:w,bestReceiverLengths:best,receiverLossNumerator:bestLoss,receiverLossDenominator:12*n,truthfulPenaltyTwice:penalty2(n,B)});
  }
  for(const v of [maxActions(16,2)===16,maxActions(16,3)===5,maxActions(16,6)===3,maxActions(16,16)===2,maxActions(16,17)===1,
    directOracle([[0,3],[1,2]],0),distinctActions([[0,3],[1,2]])===1,penalty2(16,3)===1,penalty2(16,2)===0,
    maxActions(16,-3)===maxActions(16,3),directOracle([[0,1,2,3]],100)]){requireTest(v,"named check");receipt.namedChecks++;}
  for(const [n,B] of [[0,0],[1.5,0],[2,0.5],[10001,0],[2,Infinity]]){let refused=false;try{maxActions(n,B);}catch(e){refused=true;}requireTest(refused,"invalid accepted");receipt.refusals++;}
  return receipt;
}

if (typeof require !== 'undefined' && require.main === module) console.log(JSON.stringify(run(),null,2));
if (typeof module !== 'undefined') module.exports={maxActions,witness,boundaryOK,penalty2,run};
