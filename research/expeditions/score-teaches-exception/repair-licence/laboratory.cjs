"use strict";
// Standalone synthetic oracle; no human or acoustic inference.
function lab(){
 const assert=(v,m)=>{if(!v)throw Error(m)}, pop=n=>{let p=0;while(n){n&=n-1;p++}return p}, cube=Array.from({length:8},(_,x)=>x);
 const rules=Array.from({length:16},(_,h)=>cube.reduce((a,x)=>a|(pop(h&(8|x))%2<<x),0));
 const states=rules.flatMap((word,h)=>[-1,...cube].map(exception=>({h,exception,word:word^(exception<0?0:1<<exception)})));
 assert(new Set(states.map(s=>s.word)).size===144,"disjoint one-exception balls");
 const hist=Array(9).fill(0);let nearestTie=0;for(let w=0;w<256;w++){let ds=rules.map(v=>pop(w^v)),d=Math.min(...ds);hist[d]++;if(ds.filter(x=>x===d).length>1)nearestTie++;}
 const masks=new Set(),allMasks=new Set();let pairs=0;
 for(let i=0;i<states.length;i++)for(let j=0;j<i;j++){let x=states[i],y=states[j],m=x.word^y.word;allMasks.add(m);if(x.h!==y.h){assert(pop(m)>=2,"base distance");masks.add(m)}pairs++}
 for(let a=0;a<8;a++)for(let b=0;b<a;b++)assert(masks.has((1<<a)|(1<<b)),"every pair realized");
 function distances(c,ms){return Math.min(...[...ms].map(m=>c.reduce((s,v,x)=>s+((m>>x)&1)*v,0)))}
 const formula=n=>2*Math.floor(n/8)+(n%8===7?1:0),profiles=[];let designs=0;
 for(let n=0;n<=9;n++){let c=Array(8).fill(0),best=-1,joint=-1,checked=0;function visit(i,left){if(i===7){c[i]=left;let sorted=c.slice().sort((a,b)=>a-b),base=distances(c,masks),both=distances(c,allMasks);assert(base===sorted[0]+sorted[1]&&both===sorted[0],"weighted distance");best=Math.max(best,base);joint=Math.max(joint,both);checked++;return;}for(let j=0;j<=left;j++){c[i]=j;visit(i+1,left-j)}}visit(0,n);assert(best===formula(n)&&joint===Math.floor(n/8),"allocation optimum");designs+=checked;profiles.push({n,checked,best,joint})}
 let decodes=0,baseOnly=0;const extended=states.map(s=>({...s,w:s.word|(s.word<<8)}));
 for(let s of extended)for(let e=0;e<16;e++)for(let f=0;f<16;f++)if(e!==f){let received=s.w^(1<<e),keep=65535^(1<<f);let cand=extended.filter(t=>pop((t.w^received)&keep)<=1);assert(cand.length&&cand.every(t=>t.h===s.h),"base decode");if(cand.length>1)baseOnly++;decodes++}
 const w=rules[0]^3, tie=rules.map((v,h)=>({h,d:pop(v^w)})).filter(t=>t.d===2);assert(tie.length>=2,"two exceptions nonidentifiable");
 // Original synthetic score: same response notes under distinct causal/authorization accounts.
 const score=[0,1,2,3,4,5,6,7].map(x=>[x,((rules[1]^4)>>x)&1]);
 const accountA={base:1,exception:2,authority:"declared exception"},accountB={base:1,exception:null,authority:"persistent upstream fault at context 2"};
 const scoreB=cube.map(x=>[x,((rules[1]>>x)&1)^(x===2?1:0)]);assert(JSON.stringify(score)===JSON.stringify(scoreB),"same score");
 return {pairs,truthTableDistanceHistogram:hist,nearestTie,designs,profiles,decodes,baseOnly,twoExceptionAmbiguity:{word:w,baseCandidates:tie},score,accountA,accountB,assertionFailures:0};
}
console.log(JSON.stringify(lab(),null,2));
