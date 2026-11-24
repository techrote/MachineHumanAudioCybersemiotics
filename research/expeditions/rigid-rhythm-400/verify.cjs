const {compile,certificate,merge}=require("./rhythm.cjs");
function gcd(a,b){while(b!==0n){[a,b]=[b,a%b]}return a}
function verify(){
  let cases=0,assignments=0,witnesses=0,skipped=0;
  const hist={};
  function brute(p){
    let H=p.reduce((a,b)=>a/gcd(a,b)*b,1n);const h=Number(H),n=p.length;
    let min=n;
    const events=p.map(v=>Array.from({length:Number(v)},(_,r)=>Array.from({length:h},(_,t)=>t%Number(v)===r?1:0)));
    const counts=new Uint8Array(h);
    function dfs(i){
      if(i===n){assignments++;let peak=0;for(const v of counts)peak=Math.max(peak,v);min=Math.min(min,peak);return}
      for(const e of (i===0?[events[i][0]]:events[i])){
        for(let t=0;t<h;t++)counts[t]+=e[t];
        dfs(i+1);
        for(let t=0;t<h;t++)counts[t]-=e[t];
      }
    }
    dfs(0);return BigInt(min);
  }
  function check(p){
    let c;try{c=compile(p)}catch(e){if(e instanceof RangeError){skipped++;return}throw e}
    const o=brute(p),w=certificate(p,c.offsets);
    if(o!==c.peak||w.peak!==o||w.time<0n||w.time>=w.repeat)throw Error("optimum mismatch "+p);
    cases++;witnesses++;hist[String(o)]=(hist[String(o)]||0)+1;
    const aligned=certificate(p,p.map(()=>0n));if(aligned.peak!==BigInt(p.length))throw Error("aligned mismatch");
  }
  function enumerate(p,min,n){if(p.length===n){check(p);return}for(let i=min;i<=7;i++)enumerate([...p,BigInt(i)],i,n)}
  for(let n=1;n<=5;n++)enumerate([],1,n);
  // Low density, arbitrarily large hyperperiod, and no timeline enumeration.
  const big=[1000000007n,1000000009n,1000000033n,1000000087n].map(v=>2n*v);
  const b=compile(big),w=certificate(big,b.offsets);
  if(b.peak!==2n||w.peak!==2n)throw Error("large witness");
  // Outside-family refusal: gcd(6,10)=2, gcd(6,15)=3.
  let refused=false;try{compile([6n,10n,15n])}catch(e){refused=e instanceof RangeError}if(!refused)throw Error("invalid family accepted");
  // A late coincidence is not ruled out by a clean finite prefix.
  const late=merge(0n,101n,1n,103n);
  if(late[0]!==5151n||late[1]!==10403n)throw Error("late CRT mismatch");
  return {cases,assignments,witnesses,skipped,hist,big:{periods:big.map(String),offsets:b.offsets.map(String),peak:String(b.peak),time:String(w.time),hyperperiod:String(w.repeat)},late:{time:String(late[0]),repeat:String(late[1])}};
}
console.log(JSON.stringify(verify(),null,2));
