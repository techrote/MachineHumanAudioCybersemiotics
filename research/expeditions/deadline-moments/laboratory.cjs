'use strict';
function laboratory(){
  const abs=x=>x<0n?-x:x;
  const gcd=(a,b)=>{a=abs(a);b=abs(b);while(b){[a,b]=[b,a%b]}return a};
  const lcm=(a,b)=>abs(a/gcd(a,b)*b);
  function* choose(a,k,start=0,p=[]){if(k===0){yield p;return;}for(let i=start;i<=a.length-k;i++)yield* choose(a,k-1,i+1,[...p,a[i]])}
  function witness(nodes){
    const x=nodes.map(BigInt), d=x.map((v,i)=>x.reduce((a,z,j)=>i===j?a:a*(v-z),1n));
    const L=d.reduce(lcm,1n), raw=d.map(v=>L/v), g=raw.reduce(gcd,0n), w=raw.map(v=>v/g), mass=w.reduce((a,v)=>a+(v>0n?v:0n),0n);
    return {x,w,mass};
  }
  const cmp=(a,b)=>a[0]*b[1]>b[0]*a[1];
  const reduce=(a,b)=>{const g=gcd(a,b);return [a/g,b/g]};
  const str=([a,b])=>`${a}/${b}`;
  const gap=(w,t)=>reduce(abs(w.w.reduce((a,v,i)=>a+(w.x[i]<=BigInt(t)?v:0n),0n)),w.mass);
  let momentChecks=0,compilerSupports=0,compilerProfiles=0,guardChecks=0,cdfMinors=0,nearChecks=0;
  function verify(w,k){for(let j=0;j<=k;j++){if(w.w.reduce((s,v,i)=>s+v*w.x[i]**BigInt(j),0n)!==0n)throw Error("moment mismatch");momentChecks++;}if(w.w.reduce((s,v)=>s+abs(v),0n)!==2n*w.mass)throw Error("mass");}
  const near=[];
  for(let k=1;k<=12;k++){
    let previous=[0n,1n];
    for(const D of [2,5,10,100,1000,10000,1000000]){
      let w=witness([-1,1,...Array.from({length:k},(_,i)=>D*(i+1))]);verify(w,k);
      let f=gap(w,0);if(!cmp(f,previous))throw Error("near-gap monotonic regression");previous=f;nearChecks++;
      if(D===10||D===1000||D===1000000)near.push({k,D,gap:str(f),decimal:Number(f[0])/Number(f[1])});
    }
  }
  function compile(nodes,k,t){if(k>=nodes.length-1)return {g:[0n,1n],nodes:[],w:[],mass:0n};
    let best={g:[0n,1n]};for(const s of choose(nodes,k+2)){const w=witness(s);verify(w,k);compilerSupports++;const g=gap(w,t);if(cmp(g,best.g)||!best.nodes)best={g,nodes:s,w:w.w,mass:w.mass};}
    compilerProfiles++;return best;
  }
  const grids=[];
  for(let n=3;n<=12;n++){const x=Array.from({length:n},(_,i)=>i);for(let t=0;t<n-1;t++){let last=[1n,1n];for(let k=0;k<n-1;k++){
    const w=compile(x,k,t);if(cmp(w.g,last))throw Error("nonmonotone moment budget");last=w.g;
    if(k===n-2){const bin=(n,k)=>{let r=1n;for(let i=1;i<=k;i++)r=r*BigInt(n-i+1)/BigInt(i);return r};const want=reduce(bin(n-2,t),2n**BigInt(n-2));if(str(w.g)!==str(want))throw Error("last moment");}
    if(n===10&&t===4)grids.push({n,t,k,gap:str(w.g),support:w.nodes,weights:w.w.map(String),mass:String(w.mass)});
  }}}
  const guards=[];
  for(let B=2;B<=10;B++){for(let a=1;a<B;a++){let x=Array.from({length:2*B+1},(_,i)=>i-B).filter(v=>Math.abs(v)>=a);for(let k=1;k<=2;k++){let w=compile(x,k,0),want=reduce(BigInt(B-a),BigInt(B+a));if(str(w.g)!==str(want))throw Error("guard");guardChecks++;if(B===10&&k===2)guards.push({delta:a/B,gap:str(w.g)});}}}
  // Bareiss elimination: exact determinant of an integer matrix.
  function det(a){a=a.map(r=>r.slice());let prev=1n,sign=1n;for(let j=0;j<a.length-1;j++){if(a[j][j]===0n){let i=a.findIndex((r,i)=>i>j&&r[j]!==0n);if(i<0)return 0n;[a[i],a[j]]=[a[j],a[i]];sign=-sign;}let p=a[j][j];for(let i=j+1;i<a.length;i++){for(let k=j+1;k<a.length;k++){let v=a[i][k]*p-a[i][j]*a[j][k];if(v%prev)throw Error("noninteger elimination");a[i][k]=v/prev;}a[i][j]=0n;}prev=p;}return sign*a[a.length-1][a.length-1];}
  for(let n=2;n<=13;n++){let x=Array.from({length:n},(_,i)=>BigInt(i*i+i+1));for(let k=1;k<n;k++)for(const cols of choose(Array.from({length:n-1},(_,i)=>i),k)){let a=Array.from({length:k},(_,r)=>cols.map(j=>x[j+1]**BigInt(r+1)-x[j]**BigInt(r+1)));if(det(a)<=0n)throw Error("CDF minor");cdfMinors++;}}
  const audio=witness([-1,1,5,10]);verify(audio,2);
  return {momentChecks,compilerSupports,compilerProfiles,guardChecks,cdfMinors,nearChecks,near,grids,guards,audio:{nodes:audio.x.map(String),weights:audio.w.map(String),mass:String(audio.mass)},assertionFailures:0};
}
console.log(JSON.stringify(laboratory(), null, 2));
