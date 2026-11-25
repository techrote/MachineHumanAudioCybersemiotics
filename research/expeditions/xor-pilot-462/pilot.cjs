/* Original synthetic expedition; no dependencies. */
const api = (function moduleBody(){
  "use strict";
  function requireInt(x,lo,hi){if(!Number.isSafeInteger(x)||x<lo||x>hi)throw new RangeError("integer outside supported range")}
  function params(n,t){requireInt(n,1,512);requireInt(t,0,1000000000);let P=1;while(n%(2*P)===0)P*=2;const d=Math.min(P,t);let p=1;while(2*p<=d)p*=2;return {n,t,P,d,p}}
  function bits(x,n){if(typeof x!=="bigint"||x<0n||x>=(1n<<BigInt(n)))throw new RangeError("word outside ring")}
  function evolve(n,t,x){params(n,t);bits(x,n);const mask=(1n<<BigInt(n))-1n;let k=1%n;while(t){if(t%2){const s=BigInt(k);x^=((x<<s)|(x>>BigInt(n-k)))&mask}t=Math.floor(t/2);k=(2*k)%n}return x}
  function compile(n,t,e){
    const {d,p}=params(n,t);requireInt(e,0,n);const r=e+1;
    if(!d)return {status:"ok",dimension:0,pilots:[],minimum:0,distance:null};
    const distance=n/p;
    if(r>distance)return {status:"impossible",dimension:d,distance};
    let pilots=[];
    if(r===1)pilots=Array.from({length:d},(_,i)=>i);
    else if(d===p){for(let i=0;i<p;i++)for(let j=0;j<r;j++)pilots.push(i+j*p)}
    else{
      const Q=2*p;let b=1;while(b<Q-d)b*=2;
      const a=Math.floor(r/2),h=Math.ceil(r/2);
      for(let i=0;i<p;i++){
        const low=r%2&&i>=b?h:a;
        for(let j=0;j<low;j++)pilots.push(i+j*Q);
        for(let j=0;j<h;j++)pilots.push(i+p+j*Q);
      }
    }
    pilots.sort((a,b)=>a-b);
    return {status:"ok",dimension:d,pilots,minimum:pilots.length,distance};
  }
  // Complete output + surviving exact input-bit observations.
  function decode(n,t,y,observations){
    params(n,t);bits(y,n);
    if(!Array.isArray(observations))throw new TypeError("observations must be pairs");
    const cols=Array.from({length:n},(_,i)=>evolve(n,t,1n<<BigInt(i)));
    const rows=Array.from({length:n},(_,j)=>[cols.reduce((s,v,i)=>s|(((v>>BigInt(j))&1n)<<BigInt(i)),0n),Number((y>>BigInt(j))&1n)]);
    const seen=new Set();
    for(const pair of observations){if(!Array.isArray(pair)||pair.length!==2)throw new TypeError("invalid observation");const [i,b]=pair;requireInt(i,0,n-1);requireInt(b,0,1);if(seen.has(i))throw new RangeError("duplicate pilot");seen.add(i);rows.push([1n<<BigInt(i),b])}
    let rank=0;const pivots=[];
    for(let i=0;i<n;i++){const bit=1n<<BigInt(i);const k=rows.findIndex(([a],j)=>j>=rank&&!!(a&bit));if(k<0)continue;[rows[k],rows[rank]]=[rows[rank],rows[k]];for(let j=0;j<rows.length;j++)if(j!==rank&&(rows[j][0]&bit)){rows[j][0]^=rows[rank][0];rows[j][1]^=rows[rank][1]}pivots.push(i);rank++}
    if(rows.some(([a,b])=>a===0n&&b))return {status:"inconsistent",rank};
    if(rank<n)return {status:"ambiguous",rank};
    let x=0n;for(let j=0;j<rank;j++)if(rows[j][1])x|=1n<<BigInt(pivots[j]);return {status:"unique",rank,x};
  }
  return {params,evolve,compile,decode};
})();
module.exports = api;
