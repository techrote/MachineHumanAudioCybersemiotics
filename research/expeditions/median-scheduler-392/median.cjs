'use strict';
// Original synthetic research prototype; no dependencies.
function compile(x) {
  if (!Array.isArray(x)||x.length<3||x.length>128||x.some(v=>v!==0&&v!==1)) throw Error("expected 3..128 binary cells");
  const n=x.length, eligible=x.map((v,i)=>v!==x[(i+n-1)%n]&&v!==x[(i+1)%n]);
  const ok=(i,a,b,c)=> (!b||eligible[i]&&!a&&!c)&&(!eligible[i]||a||b||c);
  const sum=x.reduce((a,b)=>a+b,0), bins=new Map();
  function add(map,key,count,flips,word) {
    const old=map.get(key);
    if (!old) map.set(key,{count,flips,word});
    else { old.count+=count; if(flips<old.flips){old.flips=flips;old.word=word;} }
  }
  for(let a=0;a<2;a++)for(let b=0;b<2;b++){
    let dp=new Map([[`${a},${b},${a*(1-2*x[0])+b*(1-2*x[1])}`,{count:1n,flips:a+b,word:`${a}${b}`} ]]);
    for(let i=2;i<n;i++){
      const next=new Map();
      for(const [key,v] of dp){
        const [p,q,d]=key.split(",").map(Number);
        for(let c=0;c<2;c++) if(ok(i-1,p,q,c)) add(next,`${q},${c},${d+c*(1-2*x[i])}`,v.count,v.flips+c,v.word+c);
      }
      dp=next;
    }
    for(const [key,v] of dp){
      const [p,q,d]=key.split(",").map(Number);
      if(ok(n-1,p,q,a)&&ok(0,q,a,b)) add(bins,sum+d,v.count,v.flips,v.word);
    }
  }
  return [...bins].sort((a,b)=>a[0]-b[0]).map(([ones,v])=>({ones,count:v.count.toString(),minFlips:v.flips,schedule:[...v.word].flatMap((b,i)=>b==="1"?[i]:[])}));
}
function step(x) { const n=x.length; return x.map((v,i)=>Number(v+x[(i+n-1)%n]+x[(i+1)%n]>=2)); }
function verify(){
  let inputs=0, terminalPairs=0, unreachable=0, cycles=0, multiple=0, schedules=0;
  const census=[];
  function check(c,msg){if(!c)throw Error(msg);}
  for(let n=3;n<=12;n++){
    const states=1<<n, mask=states-1, cache=new Map();
    function next(s){return ((s<<1)|(s>>(n-1)))&mask;}
    function prev(s){return (s>>1)|((s&1)<<(n-1));}
    function endpoints(s){
      if(cache.has(s))return cache.get(s);
      const a=next(s),b=prev(s),target=(s&a)|(s&b)|(a&b),diff=s^target;
      const out=new Set();
      if(!diff)out.add(s);
      else for(let i=0;i<n;i++)if(diff&(1<<i))for(const t of endpoints(s^(1<<i)))out.add(t);
      cache.set(s,out);return out;
    }
    const pop=s=>s.toString(2).replace(/0/g,"").length;
    let row={n,inputs:states,terminalPairs:0,multiple:0,snapshotUnreachable:0,twoCycles:0};
    for(let s=0;s<states;s++){
      const x=Array.from({length:n},(_,i)=>(s>>i)&1), expected=endpoints(s), bins=new Map();
      for(const t of expected){
        const k=pop(t),f=pop(t^s),v=bins.get(k)||{count:0,min:Infinity};v.count++;v.min=Math.min(v.min,f);bins.set(k,v);
      }
      const got=compile(x);
      check(got.length===bins.size,"bin size");
      for(const v of got){
        const e=bins.get(v.ones);check(e&&BigInt(v.count)===BigInt(e.count)&&v.minFlips===e.min,"count/min");
        let y=s;
        for(const i of v.schedule){
          check(((y>>i)&1)!==((y>>((i+n-1)%n))&1)&&((y>>i)&1)!==((y>>((i+1)%n))&1),"illegal witness");y^=1<<i;
        }
        check(expected.has(y)&&pop(y)===v.ones&&v.schedule.length===v.minFlips,"witness");schedules++;
      }
      const eligible=x.map((v,i)=>v!==x[(i+n-1)%n]&&v!==x[(i+1)%n]);
      let y=x, steps=0, period=0;
      while(true){const z=step(y);if(z.join("")===y.join(""))break;if(step(z).join("")===y.join("")){period=2;break;}y=z;steps++;check(steps<=n,"snapshot bound");}
      if(eligible.every(Boolean)){check(period===2,"alternating");row.twoCycles++;}
      else {
        check(period===0,"nonalternating period");
        const start=eligible.indexOf(false),runs=[];let k=0;
        for(let i=1;i<=n;i++){if(eligible[(start+i)%n])k++;else if(k){runs.push(k);k=0;}}
        check(steps===Math.ceil(Math.max(0,...runs)/2),"time formula");
        const dest=y.reduce((a,v,i)=>a+(v<<i),0), unreachable=!expected.has(dest);
        check(unreachable===runs.some(k=>k%4===2),"snapshot reachability formula");
        if(unreachable)row.snapshotUnreachable++;
      }
      row.terminalPairs+=expected.size;if(expected.size>1)row.multiple++;
    }
    inputs+=states;terminalPairs+=row.terminalPairs;unreachable+=row.snapshotUnreachable;cycles+=row.twoCycles;multiple+=row.multiple;census.push(row);
  }
  let perrin=[3n,0n,2n];for(let i=3;i<=128;i++)perrin.push(perrin[i-2]+perrin[i-3]);
  const alternating=[];
  for(let n=4;n<=128;n+=2){
    const bins=compile(Array.from({length:n},(_,i)=>i%2)),count=bins.reduce((s,b)=>s+BigInt(b.count),0n);
    check(count===perrin[n]&&bins[0].ones===0&&bins.at(-1).ones===n,"Perrin/extremes");
    if([4,6,8,12,16,24,32,64,128].includes(n))alternating.push({n,count:count.toString(),attainableOnes:bins.map(b=>b.ones)});
  }
  for(const x of [[],[0,1,2],"010",Array(129).fill(0)]){let refused=false;try{compile(x)}catch{refused=true}check(refused,"invalid accepted");}
  return {inputs,terminalPairs,multiple,snapshotUnreachable:unreachable,twoCycles:cycles,witnesses:schedules,census,alternating,negative:{input:[0,0,1,0,1,1],snapshot:step([0,0,1,0,1,1]),async:compile([0,0,1,0,1,1])},refusals:4};
}
module.exports={compile,step,verify};
if(require.main===module)console.log(JSON.stringify(verify(),null,2));
