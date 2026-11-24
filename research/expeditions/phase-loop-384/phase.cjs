// Finite cyclic time/frequency phase loops. No external dependencies.
"use strict";
const steps = {E:[1,0], N:[0,1], W:[-1,0], S:[0,-1]};
const mod = (x,n) => ((x%n)+n)%n;
function state(word) {
  let x=0,y=0,k=0;
  for(const c of word) {
    if(!Object.hasOwn(steps,c)) throw Error("invalid step");
    const [dx,dy]=steps[c]; k-=dx*y; x+=dx; y+=dy;
  }
  return {x,y,k};
}
function reverse(word) {
  const inv={E:"W",W:"E",N:"S",S:"N"};
  return [...word].reverse().map(c=>inv[c]).join("");
}
function areaLoop(area) {
  if(!Number.isSafeInteger(area)||Math.abs(area)>1000000000) throw Error("area outside supported integer range");
  if(area===0) return "";
  const A=Math.abs(area), s=Math.ceil(Math.sqrt(4*A));
  const a=Math.floor(s/2), b=s-a, d=a*b-A;
  const w="E".repeat(a)+"N".repeat(b-1)+"W".repeat(d)+"N"+"W".repeat(a-d)+"S".repeat(b);
  return area>0?w:reverse(w);
}
function residueLoop(n,r) {
  if(!Number.isSafeInteger(n)||n<2||n>2000000000||!Number.isSafeInteger(r)) throw Error("invalid modulus/residue");
  const u=mod(r,n), A=u<=n-u?u:u-n;
  return {area:A,word:areaLoop(A)};
}
// Generalized CRT in arbitrary-precision arithmetic. Return null on incompatibility.
function crt(targets) {
  let a=0n,m=1n;
  const norm=(x,n)=>(x%n+n)%n;
  function egcd(a,b) {
    let x=1n,y=0n;
    while(b!==0n) {const q=a/b; [a,b]=[b,a-q*b]; [x,y]=[y,x-q*y];}
    return [a,x];
  }
  for(const [nn,rr] of targets) {
    if(typeof nn!=="bigint"||typeof rr!=="bigint"||nn<2n) throw Error("expected BigInt modulus >=2 and residue");
    const [g,x]=egcd(m,nn), delta=rr-a;
    if(delta%g!==0n)return null;
    const l=nn/g, t=norm(delta/g*x,l);
    a=norm(a+m*t,m*l); m*=l;
  }
  return {residue:a,modulus:m,area:a<=m-a?a:a-m};
}
function verify() {
  const assert=(b,msg)=>{if(!b)throw Error(msg);};
  let areaCases=0,residueCases=0,crtCases=0,crtIncompatible=0,states=0;
  for(let A=-10000;A<=10000;A++){
    const w=areaLoop(A),s=state(w);
    assert(s.x===0&&s.y===0&&s.k===A,"area certificate");
    assert(w.length===2*Math.ceil(Math.sqrt(4*Math.abs(A))),"length certificate");
    areaCases++;
  }
  // Breadth-first lifted states: independent exhaustive shortest paths up to depth 12.
  let frontier=[[0,0,0]], seen=new Set(["0,0,0"]), shortest=new Map([[0,0]]);
  for(let t=1;t<=12;t++){
    const next=[];
    for(const [x,y,k] of frontier) for(const [dx,dy] of Object.values(steps)) {
      // Alternative cocycle integral x dy, equal on closed walks.
      const s=[x+dx,y+dy,k+x*dy],key=s.join(",");
      if(seen.has(key))continue;
      seen.add(key);next.push(s);
      if(s[0]===0&&s[1]===0&&!shortest.has(s[2]))shortest.set(s[2],t);
    }
    frontier=next;
  }
  states=seen.size;
  for(let A=-9;A<=9;A++)assert(shortest.get(A)===areaLoop(A).length,"BFS shortest");
  assert(shortest.size===19,"unexpected reachable areas");
  for(let n=2;n<=100;n++)for(let r=0;r<n;r++){
    const q=residueLoop(n,r),s=state(q.word);
    assert(s.x===0&&s.y===0&&mod(s.k,n)===r,"residue");
    if(q.word.length<=12){
      let best=Infinity;
      for(const [a,l] of shortest)if(mod(a,n)===r)best=Math.min(best,l);
      assert(best===q.word.length,"residue BFS");
    }
    residueCases++;
  }
  for(let n=2;n<=12;n++)for(let m=2;m<=12;m++)for(let r=0;r<n;r++)for(let s=0;s<m;s++){
    const q=crt([[BigInt(n),BigInt(r)],[BigInt(m),BigInt(s)]]);
    const hits=Array.from({length:n*m},(_,i)=>i).filter(i=>i%n===r&&i%m===s);
    assert((q===null)===(hits.length===0),"CRT existence");
    if(q===null)crtIncompatible++;
    else {
      assert(Number(q.residue)===hits[0]&&Number(q.modulus)===n*m/hits.length,"CRT period");
      assert(Math.abs(Number(q.area))===Math.min(hits[0],Number(q.modulus)-hits[0]),"CRT minimum area");
    }
    crtCases++;
  }
  assert(state("EEEE").x===4,"lifted closure differs from cyclic closure");
  for(const f of [()=>areaLoop(1.5),()=>residueLoop(1,0),()=>state("Q"),()=>crt([[1n,0n]])]){
    let rejected=false;try{f()}catch{rejected=true}assert(rejected,"refusal");
  }
  return {areaCases,residueCases,crtCases,crtIncompatible,states,bfsAreas:shortest.size,refusals:4};
}
module.exports={state,areaLoop,residueLoop,crt,verify};
if(require.main===module)console.log(JSON.stringify(verify(),null,2));
