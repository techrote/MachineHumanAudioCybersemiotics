// Synthetic finite bipolar block compiler. No external dependencies.
// n <= 32 and r <= 5 keep integer moment sums exactly representable.
function integrate(s) {
  let z=0; return s.map(x=>(z+=x));
}
function moments(s,r) {
  return Array.from({length:r},(_,k)=>s.reduce((a,x,i)=>a+x*i**k,0));
}
function metrics(s,r) {
  if(s.some(x=>x!==1&&x!==-1)||!s.length||r<1||r>=s.length||!Number.isInteger(r))
    throw Error("invalid bipolar block/order");
  let q=s.slice(),peak=0;
  for(let j=0;j<r;j++){
    q=integrate(q);
    if(j===0) peak=Math.max(...q.map(Math.abs));
    if(q.at(-1)!==0) return null;
    q.pop();
  }
  const switches=s.slice(1).filter((x,i)=>x!==s[i]).length;
  const leakage=q.reduce((a,x)=>a+Math.abs(x),0);
  return {switches,peak,leakage,quotient:q};
}
function compile(n,r,maxMatches=5000000) {
  if(!Number.isInteger(n)||n<2||n>32||!Number.isInteger(r)||r<1||r>5||r>=n||
      !Number.isSafeInteger(maxMatches)||maxMatches<1) throw Error("unsupported search bounds");
  const h=Math.floor(n/2), t=n-h;
  const left=new Map();
  const signs=(mask,len)=>Array.from({length:len},(_,i)=>(mask>>i)&1?-1:1);
  function key(s,start,sign) {
    return Array.from({length:r},(_,k)=>sign*s.reduce((a,x,i)=>a+x*(i+start)**k,0)).join(",");
  }
  for(let mask=0;mask<2**h;mask+=2){
    const k=key(signs(mask,h),0,1);
    if(!left.has(k))left.set(k,[]);
    left.get(k).push(mask);
  }
  let count=0, frontier=[], minLeak=null, minSwitch=null;
  const dominates=(a,b)=>a.switches<=b.switches&&a.peak<=b.peak&&a.leakage<=b.leakage;
  for(let mask=0;mask<2**t;mask++){
    const tail=signs(mask,t), hits=left.get(key(tail,h,-1))||[];
    for(const m of hits){
      if(count===maxMatches)return {status:"budget_exhausted",count,frontier};
      count++;
      const s=signs(m,h).concat(tail), v=metrics(s,r);
      if(!v)throw Error("moment/integration disagreement");
      const w={switches:v.switches,peak:v.peak,leakage:v.leakage,word:s.map(x=>x===1?"+":"-").join("")};
      if(!minLeak||w.leakage<minLeak.leakage)minLeak=w;
      if(!minSwitch||w.switches<minSwitch.switches)minSwitch=w;
      if(!frontier.some(a=>dominates(a,w))){
        frontier=frontier.filter(a=>!dominates(w,a));frontier.push(w);
      }
    }
  }
  frontier.sort((a,b)=>a.switches-b.switches||a.peak-b.peak||a.leakage-b.leakage);
  return {status:"complete",count,frontier,minLeak,minSwitch};
}
function ptm(r){
  if(!Number.isInteger(r)||r<1||r>12)throw Error("unsupported PTM order");
  let s=[1];for(let i=0;i<r;i++)s=s.concat(s.map(x=>-x));return s;
}
function difference(x){return x.slice(1).map((v,i)=>v-x[i]);}
function adversary(s,r){
  const m=metrics(s,r);if(!m)throw Error("non-null word");
  let x=m.quotient.map(v=>(-1)**r*Math.sign(v));
  for(let i=0;i<r;i++)x=[0,...integrate(x)];
  if(x.some(v=>!Number.isSafeInteger(v)))throw Error("overflow");
  return x;
}
function run(){
  const rows=[];
  for(const [n,r] of [[4,1],[4,2],[4,3],[8,2],[8,3],[8,4],[12,2],[12,3],[16,2],[16,3],[16,4],[16,5],[20,3],[24,3],[24,4],[28,3],[32,3],[32,4],[32,5]]){
    rows.push({n,r,...compile(n,r)});
  }
  let bruteChecks=0,witnessChecks=0;
  for(let n=2;n<=12;n++){
    for(let r=1;r<=Math.min(5,n-1);r++){
      const exact=compile(n,r), brute=[];
      for(let mask=0;mask<2**n;mask+=2){
        const s=Array.from({length:n},(_,i)=>(mask>>i)&1?-1:1);
        const zero=moments(s,r).every(x=>x===0), m=metrics(s,r);
        if(zero!==Boolean(m))throw Error("direct moment disagreement");
        if(zero)brute.push(m);
        bruteChecks++;
      }
      const d=(a,b)=>a.switches<=b.switches&&a.peak<=b.peak&&a.leakage<=b.leakage;
      if(exact.count!==brute.length||brute.some(v=>!exact.frontier.some(w=>d(w,v)))||
        exact.frontier.some(v=>!brute.some(w=>d(w,v))||brute.some(w=>d(w,v)&&!d(v,w))))
        throw Error("frontier disagreement");
    }
  }
  for(const row of rows)for(const w of row.frontier){
    const s=[...w.word].map(c=>c==="+"?1:-1), x=adversary(s,row.r);
    let z=x;for(let i=0;i<row.r;i++)z=difference(z);
    if(Math.max(...z.map(Math.abs))!==1||s.reduce((a,v,i)=>a+v*x[i],0)!==w.leakage)
      throw Error("sharp leakage witness failed");
    witnessChecks++;
  }
  const family=[];
  for(let r=1;r<=10;r++){
    const s=ptm(r),m=metrics(s,r);
    if(!m||m.peak!==1||m.leakage!==2**(r*(r-1)/2))throw Error("PTM identity");
    family.push({r,n:s.length,switches:m.switches,peak:m.peak,leakage:m.leakage});
  }
  const limited=compile(8,1,1);
  if(limited.status!=="budget_exhausted")throw Error("budget classification");
  return {rows,bruteChecks,witnessChecks,family,budgetControl:limited.status};
}

export {integrate,moments,metrics,compile,ptm,difference,adversary,run};
