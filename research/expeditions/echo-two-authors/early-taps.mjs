// Geometric normalization extension: exact early-tap equivalence classes.
function run(){
  const check=(ok,label)=>{if(!ok)throw Error(label);};
  function* compositions(m,k,p=[]){
    if(m===1){yield [...p,k];return;}
    for(let e=0;e<=k;e++)yield* compositions(m-1,k-e,[...p,e]);
  }
  const mul=(a,b)=>{const c=Array(a.length+b.length-1).fill(0n);
    for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)c[i+j]+=a[i]*b[j];return c;};
  const sum=a=>a.reduce((s,x)=>s+x,0n);
  const gcd=(a,b)=>b?gcd(b,a%b):a;
  const ratio=(a,b)=>{const d=gcd(a,b);return String(a/d)+'/'+String(b/d);};
  const normKey=a=>a.map(x=>ratio(x,sum(a))).join(',');
  const choose=(n,k)=>{let x=1;for(let j=1;j<=k;j++)x=x*(n-j+1)/j;return x;};
  const rows=[];
  for(let m=2;m<=6;m++)for(let k=1;k<=8;k++){
    // C=5/2, R=(10m+1)/(10m). 2+a_i=C R^i.
    const p=Array.from({length:m},(_,i)=>{
      const u=5n*BigInt(10*m+1)**BigInt(i),v=2n*BigInt(10*m)**BigInt(i);
      const a=u-2n*v;
      check(4n*a>v&&a<=v,'coefficient interval');
      return [v,v,a];
    });
    const groups=new Map(),seen=new Set(),keys=new Map();
    let count=0;
    for(const e of compositions(m,k)){
      let h=[1n],w=0;
      for(let i=0;i<m;i++){w+=i*e[i];for(let j=0;j<e[i];j++)h=mul(h,p[i]);}
      check(h.length===2*k+1&&h[1]===BigInt(k)*h[0],'length/early ratio');
      const key=ratio(h[0],sum(h))+';'+ratio(h[1],sum(h)),whole=normKey(h);
      check(!seen.has(whole),'distinct entire normalized filters');seen.add(whole);
      if(groups.has(w))check(groups.get(w).key===key,'same weight gives same two taps');
      else groups.set(w,{key,count:0,example:e});
      if(keys.has(key))check(keys.get(key)===w,'different weight gives different taps');
      keys.set(key,w);groups.get(w).count++;count++;
    }
    check(count===choose(m+k-1,m-1),'composition count');
    check(groups.size===(m-1)*k+1,'all weights represented');
    const biggest=[...groups.entries()].sort((a,b)=>b[1].count-a[1].count||a[0]-b[0])[0];
    check(biggest[1].count>=Math.ceil(count/groups.size),'pigeonhole bound');
    rows.push({m,k,count,earlyTapClasses:groups.size,largestClass:biggest[1].count,weight:biggest[0],firstTwoTaps:biggest[1].key});
  }
  return {rows,totalDistinctMaximalFiltersAcrossInstances:rows.reduce((s,x)=>s+x.count,0),assertionFailures:0};
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('early-taps.mjs'))console.log(JSON.stringify(run(),null,2));
