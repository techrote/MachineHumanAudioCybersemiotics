function gcd(a,b){while(b!==0n){[a,b]=[b,a%b]}return a}

function mod(a,m){return (a%m+m)%m}

function ceil(a,b){return (a+b-1n)/b}

function parse(p){if(!Array.isArray(p)||p.length<1||p.length>256||p.some(x=>typeof x!=="bigint"||x<1n))throw new RangeError("1..256 positive BigInt periods required");return p}

function groups(p){parse(p);const m=new Map();p.forEach((v,i)=>{if(!m.has(v))m.set(v,[]);m.get(v).push(i)});return [...m].map(([period,indices])=>({period,indices})).sort((a,b)=>a.period<b.period?-1:a.period>b.period?1:0)}

function compile(p){
  const gs=groups(p);
  const g=gs.length===1?gs[0].period:gcd(gs[0].period,gs[1].period);
  for(let i=0;i<gs.length;i++)for(let j=0;j<i;j++)if(gcd(gs[i].period,gs[j].period)!==g)throw new RangeError("distinct periods do not share a constant pairwise gcd");
  const offsets=Array(p.length), chunks=[];let k=0n;
  for(const {period,indices} of gs){
    const a=period/g;
    for(let j=0;j<indices.length;){
      const residue=k%g;let length=0n;
      while(j<indices.length&&length<a){offsets[indices[j++]]=residue+g*length;length++}
      chunks.push({period,residue,length});k++;
    }
  }
  return {offsets,g,peak:ceil(k,g),chunks};
}

function egcd(a,b){let x=1n,y=0n;while(b!==0n){let q=a/b;[a,b]=[b,a%b];[x,y]=[y,x-q*y]}return [a,x]}

function merge(a,m,b,n){
  const d=gcd(m,n);
  if((b-a)%d!==0n)return null;
  const k=mod((b-a)/d*egcd(m/d,n/d)[1],n/d);
  const l=m/d*n;
  return [mod(a+m*k,l),l];
}

function certificate(p,offsets){
  const gs=groups(p);
  if(!Array.isArray(offsets)||offsets.length!==p.length||offsets.some((x,i)=>typeof x!=="bigint"||x<0n||x>=p[i]))throw new RangeError("invalid offsets");
  const g=gs.length===1?gs[0].period:gcd(gs[0].period,gs[1].period);
  for(let i=0;i<gs.length;i++)for(let j=0;j<i;j++)if(gcd(gs[i].period,gs[j].period)!==g)throw new RangeError("unsupported gcd geometry");
  const buckets=new Map();
  for(const {period,indices} of gs){
    const maxima=new Map(), counts=new Map();
    for(const i of indices){
      const v=offsets[i],r=v%g, count=(counts.get(v)||0n)+1n;counts.set(v,count);
      if(!maxima.has(r)||count>maxima.get(r).count)maxima.set(r,{v,count});
    }
    for(const [r,{v,count}] of maxima){
      const b=buckets.get(r)||{peak:0n,time:0n,repeat:1n};
      const merged=merge(b.time,b.repeat,v,period);
      if(!merged)throw Error("unexpected CRT failure");
      buckets.set(r,{peak:b.peak+count,time:merged[0],repeat:merged[1]});
    }
  }
  const best=[...buckets.values()].reduce((a,b)=>b.peak>a.peak?b:a);
  const active=p.map((v,i)=>best.time%v===offsets[i]?i:-1).filter(i=>i>=0);
  if(BigInt(active.length)!==best.peak)throw Error("witness mismatch");
  // Repeat interval for the entire schedule, not merely the winning groups.
  const hyperperiod=p.reduce((a,b)=>a/gcd(a,b)*b,1n);
  return {...best,repeat:hyperperiod,active};
}

module.exports={compile,certificate,merge};
