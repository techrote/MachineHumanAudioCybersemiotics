'use strict';
// Exact bounded finite enumeration; no empirical observations.
function laboratory(){
"use strict";
const counts={graphFamilies:0,directReceiptChecks:0,hintPartitionChecks:0,constructedHintChecks:0,randomColorings:0,balancedEdgeChecks:0,decoderWorldChecks:0,missingIdentityChecks:0};
function check(x,msg){if(!x)throw Error(msg)}
function pairs(n){return Array.from({length:n},(_,i)=>Array.from({length:n-i-1},(_,j)=>[i,i+j+1])).flat()}
function words(n,m,visit){const a=Array(n).fill(0);function rec(i){if(i===n){visit(a);return;}for(let j=0;j<m;j++){a[i]=j;rec(i+1)}}rec(0)}
function colorable(n,edges,m){const a=Array(n).fill(-1);function go(i){if(i===n)return true;for(let c=0;c<m;c++){if(edges.some(([u,v])=>v===i&&a[u]===c))continue;a[i]=c;if(go(i+1))return true;}a[i]=-1;return false}return go(0)}
function chi(n,edges){for(let m=1;m<=n;m++)if(colorable(n,edges,m))return m;throw Error("chi")}
function image(x,[u,v]){return x===v?u:x}
function direct(n,edges,tags){for(const e of edges){const seen=new Set();for(let x=0;x<n;x++){const key=image(x,e)+":"+tags[x];if(seen.has(key))return false;seen.add(key)}}return true}
function digits(x,m,k){return Array.from({length:k},()=>{const d=x%m;x=Math.floor(x/m);return d})}
for(let n=2;n<=5;n++){
 const all=pairs(n);
 for(let mask=0;mask<2**all.length;mask++){
  const es=all.filter((_,i)=>mask>>i&1), c=chi(n,es);counts.graphFamilies++;
  for(let m=1;m<=n;m++){
   let exists=false;
   words(n,m,a=>{if(direct(n,es,a))exists=true;counts.directReceiptChecks++});
   check(exists===(c<=m),"direct receipt");
  }
  for(let m=1;m<=3;m++)for(let k=1;k<=3;k++){
   if(n<=4){
    let exists=false;
    words(es.length,k,h=>{if(Array.from({length:k},(_,j)=>colorable(n,es.filter((_,i)=>h[i]===j),m)).every(Boolean))exists=true;counts.hintPartitionChecks++});
    check(exists===(c<=m**k),"hint partition");
   }
   if(c<=m**k){
    let col=null;words(n,c,a=>{if(!col&&direct(n,es,a))col=a.slice()});check(col,"missing coloring");
    const codes=col.map(x=>digits(x,m,k));
    const groups=Array.from({length:k},()=>[]);
    for(const [u,v] of es){const j=codes[u].findIndex((x,i)=>x!==codes[v][i]);check(j>=0,"no hint");groups[j].push([u,v]);}
    for(let j=0;j<k;j++){check(direct(n,groups[j],codes.map(x=>x[j])),"constructed hint");counts.constructedHintChecks++}
   }
  }
 }
}
for(let n=2;n<=7;n++)for(let m=1;m<=Math.min(4,n);m++){
 const es=pairs(n), q=Math.floor(n/m), rem=n%m;
 const min=rem*q*(q+1)/2+(m-rem)*q*(q-1)/2;
 let observed=Infinity, balanced=0, collisions=Array(es.length).fill(0);
 words(n,m,a=>{
  const bad=es.map(([u,v])=>a[u]===a[v]?1:0), total=bad.reduce((x,y)=>x+y,0);
  observed=Math.min(observed,total);counts.randomColorings++;
  const sizes=Array(m).fill(0);for(const x of a)sizes[x]++;
  if(sizes.every(x=>x===q||x===q+1)){
   balanced++;
   for(let i=0;i<es.length;i++){collisions[i]+=bad[i];counts.balancedEdgeChecks++;
    // Direct conditional decoder: choose uniformly among all origins compatible
    // with the observed final state and receipt. Store twice the error.
    for(const x of es[i]){
     const matches=Array.from({length:n},(_,j)=>j).filter(j=>image(j,es[i])===image(x,es[i])&&a[j]===a[x]);
     check(matches.length-1===bad[i],"decoder error");counts.decoderWorldChecks++;
    }
   }
  }
 });
 check(observed===min,"balanced lower bound");
 for(const hits of collisions)check(hits*es.length===min*balanced,"minimax symmetry");
}
for(let n=2;n<=8;n++){
 // Without action identity, all translations of Z_n permit all origins at y=0.
 for(let x=0;x<n;x++){const shift=(n-x)%n;check((x+shift)%n===0,"missing action");counts.missingIdentityChecks++}
 // A single known shift has inverse, with no receipt.
 for(let x=0;x<n;x++)for(let a=0;a<n;a++){check(((x+a)%n-a+n)%n===x,"known shift");counts.missingIdentityChecks++}
}
return counts;
}
console.log(JSON.stringify(laboratory(),null,2));
