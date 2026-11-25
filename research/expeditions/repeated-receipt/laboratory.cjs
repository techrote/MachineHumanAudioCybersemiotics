"use strict";
function laboratory() {
  const C=(n,k)=>{if(k<0||k>n)return 0n;let a=1n;for(let i=1;i<=k;i++)a=a*BigInt(n-i+1)/BigInt(i);return a};
  const fact=n=>Array.from({length:n},(_,i)=>BigInt(i+1)).reduce((a,b)=>a*b,1n);
  const sum=a=>a.reduce((s,x)=>s+x,0n);
  const pop=x=>{let n=0;while(x){n+=x&1;x>>=1}return n};
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  function* profiles(m,d){if(!m){yield [BigInt(d)];return}for(let i=0;i<=d;i++)for(const a of profiles(m-1,d-i))yield [BigInt(i),...a]}
  function moments(w){const m=w.length-1, f=fact(m), den=sum(w)*f;return {den,a:w.map((_,j)=>sum(w.map((x,k)=>x*C(k,j)*(f/C(m,j))))) }}
  function histogram(w,t){const {den,a}=moments(w),m=w.length-1;return {den:den**BigInt(t),h:a.map((_,l)=>C(m,l)*sum(a.slice(l).map((x,i)=>(i%2?-1n:1n)*C(m-l,i)*x**BigInt(t))))}}
  function extremes(w,L,U){const m=w.length-1,d=sum(w),s=sum(w.map((x,k)=>x*BigInt(k)));let lo=Number(s/d),b=w.map(()=>0n),e=w.map(()=>0n);b[lo]=d-s%d;if(s%d)b[lo+1]=s%d;if(L===U)e[L]=d;else{e[L]=BigInt(U)*d-s;e[U]=s-BigInt(L)*d}return [b,e]}
  const stop=(h,z)=>sum(h.map((x,j)=>x*BigInt(Math.max(j-z,0))));
  const le=(x,y,z)=>stop(x.h,z)*y.den<=stop(y.h,z)*x.den;
  let counts={profiles:0,exact_histograms:0,labelled_cells:0,convex_tests:0,peak_floor_profiles:0,mean_checks:0,posterior_tests:0};
  const examples=[];
  for(let m=1;m<=6;m++){
    const N=1<<m,f=fact(m),pops=Array.from({length:N},(_,i)=>pop(i));
    for(const w of profiles(m,4)){
      counts.profiles++;const d=sum(w),q=sum(w.map((x,k)=>x*BigInt(k))),den=d*f;
      const active=w.map((x,k)=>x?k:-1).filter(k=>k>=0),L=active[0],U=active.at(-1);
      const [b,e]=extremes(w,0,m),[bc,ec]=extremes(w,L,U);
      if(L>0||U<m)counts.peak_floor_profiles++;
      const draws=pops.map(k=>w[k]*(f/C(m,k)));
      let state=Array(N).fill(0n);state[N-1]=1n;
      for(let t=1;t<=5;t++){
        const next=Array(N).fill(0n);
        for(let x=0;x<N;x++)if(state[x])for(let y=0;y<N;y++)if(draws[y])next[x&y]+=state[x]*draws[y];
        state=next;const literal=Array(m+1).fill(0n);state.forEach((v,i)=>literal[pops[i]]+=v);
        const a=histogram(w,t),lo=histogram(b,t),hi=histogram(e,t),lc=histogram(bc,t),hc=histogram(ec,t);
        assert(a.den===den**BigInt(t)&&sum(a.h)===a.den&&a.h.every(x=>x>=0n),"normalization");
        assert(literal.every((x,j)=>x===a.h[j]),"mask vs inversion");
        counts.exact_histograms++;counts.labelled_cells+=m+1;
        assert(sum(a.h.map((x,j)=>x*BigInt(j)))*(BigInt(m)*d)**BigInt(t)===a.den*BigInt(m)*q**BigInt(t),"mean");counts.mean_checks++;
        for(let z=0;z<=m;z++){
          assert(le(lo,a,z)&&le(a,hi,z)&&le(lc,a,z)&&le(a,hc,z),"convex order");counts.convex_tests+=4;
        }
        const acc=x=>sum(x.h.map((v,j)=>v*(fact(m+1)/BigInt(j+1))));
        assert(acc(lo)*a.den<=acc(a)*lo.den&&acc(a)*hi.den<=acc(hi)*a.den,"Bayes");counts.posterior_tests+=2;
      }
    }
  }
  for(const m of [2,4,8,16,32,64]){
    const w=Array(m+1).fill(0n);w[m/2]=1n;
    const p=moments(w);
    let n=0n,d=1n;
    for(let j=1;j<=m;j++){let x=(j%2?1n:-1n)*C(m,j)*p.den,y=p.den-p.a[j];n=n*y+x*d;d*=y;const gcd=(a,b)=>b?gcd(b,a%b):a;const g=gcd(n<0n?-n:n,d);n/=g;d/=g;}
    examples.push({false_candidates:m,balanced_mean_T_exact:n+"/"+d,balanced_mean_T_approx:Number(n*1000000n/d)/1e6,burst_mean_T:2,deadline:Array.from({length:8},(_,i)=>{let t=i+1,h=histogram(w,t);return {t,balanced_unique:Number(h.h[0]*1000000n/h.den)/1e6,burst_unique:1-2**(-t)}})});
  }
  return {status:"PASS",counts,examples,notes:"Exact BigInt labelled-mask propagation versus binomial inversion; denominator-four profiles, m=1..6, five independent draws. Decimal display values truncated to six places."};
}
console.log(JSON.stringify(laboratory(), null, 2));
