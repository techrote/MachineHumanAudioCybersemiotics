// Original synthetic finite-grid notch compiler, MHAC #336.
// Coefficients are nonnegative integer increments, not audio samples.
// All polynomial divisibility and five-period comparisons use BigInt.
function order(n) {
  if (!Number.isSafeInteger(n)||n<2||n>128) throw Error("order must be integer 2..128");
  return n;
}
function trim(a) { while(a.length>1 && a[a.length-1]===0n)a.pop();return a; }
function mul(a,b) {
  const c=Array(a.length+b.length-1).fill(0n);
  for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)c[i+j]+=a[i]*b[j];
  return trim(c);
}
function divide(a,b) {
  a=trim(a.slice());
  if(b[b.length-1]!==1n)throw Error("monic divisor required");
  const q=Array(Math.max(1,a.length-b.length+1)).fill(0n);
  for(let i=a.length-b.length;i>=0;i--){
    q[i]=a[i+b.length-1];
    for(let j=0;j<b.length;j++)a[i+j]-=q[i]*b[j];
  }
  return {q:trim(q),rem:trim(a)};
}
const cache=new Map([[1,[-1n,1n]]]);
function phi(n){
  if(n!==1)order(n);
  if(cache.has(n))return cache.get(n).slice();
  let a=Array(n+1).fill(0n);a[0]=-1n;a[n]=1n;
  for(let d=1;d<n;d++)if(n%d===0){
    const z=divide(a,phi(d));
    if(z.rem.some(Boolean))throw Error("cyclotomic division invariant");
    a=z.q;
  }
  cache.set(n,a);return a.slice();
}
function factors(n){const a=[];for(let p=2;p<=n;p++)if(n%p===0){a.push(p);while(n%p===0)n/=p;}return a;}
function mass(a){return a.reduce((s,x)=>s+x,0n);}
function product(orders){
  if(!Array.isArray(orders)||!orders.length||orders.length>8)throw Error("1..8 orders required");
  const qs=[...new Set(orders.map(order))].sort((a,b)=>a-b);
  return {qs,p:qs.reduce((a,q)=>mul(a,phi(q)),[1n])};
}
function plan(orders){
  const {qs,p}=product(orders);
  let witness=[1n];
  for(const q of qs){
    const f=factors(q)[0],step=q/f;
    const comb=Array(q-step+1).fill(0n);
    for(let j=0;j<f;j++)comb[j*step]=1n;
    witness=mul(witness,comb);
  }
  const massDivisor=mass(p);
  const degreeLower=Math.max(p.length-1,...qs.map(q=>Math.ceil(q/2)));
  const nonnegative=p.every(x=>x>=0n);
  if(nonnegative)witness=p;
  return {orders:qs,product:p,degreeLower,massDivisor,witness,
    span:witness.length-1,mass:mass(witness),
    spanOptimal:witness.length-1===degreeLower,
    massOptimal:mass(witness)===massDivisor};
}
function exactNotch(a,orders){
  if(!Array.isArray(a)||!a.length||a.some(x=>typeof x!=="bigint"||x<0n)||mass(a)===0n)throw Error("positive mass of nonnegative BigInts required");
  return !divide(a,product(orders).p).rem.some(Boolean);
}
// Bounded mass minimization within a span limit, exhaustive, no floating roots.
function search(orders,span,maxMass,budget=1000000){
  if(!Number.isSafeInteger(span)||span<0||span>24||!Number.isSafeInteger(maxMass)||maxMass<1||maxMass>128||!Number.isSafeInteger(budget)||budget<1)throw Error("invalid search limits");
  const {p}=product(orders), low=plan(orders).degreeLower;
  if(span<low)return {status:"infeasible-span",visited:0};
  const step=Number(mass(p)); // <= 128^8 but refuse unsafe coercion
  if(!Number.isSafeInteger(step)||step<1)throw Error("mass divisor overflow");
  let visited=0,word=Array(span+1).fill(0n),found=null,exhausted=false;
  function rec(i,left){
    if(found||exhausted)return;
    if(i===span){
      word[i]=BigInt(left);
      if(visited>=budget){exhausted=true;return;}
      visited++;
      if(!divide(word,p).rem.some(Boolean))found=trim(word.slice());
      return;
    }
    // Shift invariance permits a positive first coefficient.
    for(let x=i===0?1:0;x<=left;x++){
      word[i]=BigInt(x);rec(i+1,left-x);
      if(found||exhausted)return;
    }
  }
  for(let m=step;m<=maxMass;m+=step){
    rec(0,m);
    if(found)return {status:"optimal-within-span",visited,mass:m,witness:found};
    if(exhausted)return {status:"budget-exhausted",visited};
  }
  return {status:"no-witness-within-mass-cap",visited};
}
// For four taps at a primitive fifth root, twice squared unnormalized gain
// equals A+B*sqrt(5). Compare exactly in Q(sqrt(5)).
function squared5(w){
  if(w.length!==4||w.some(x=>typeof x!=="bigint"||x<0n))throw Error("four nonnegative BigInts required");
  const [a,b,c,d]=w;
  const c1=a*b+b*c+c*d,c23=a*c+b*d+a*d;
  return [2n*(a*a+b*b+c*c+d*d)-c1-c23,c1-c23];
}
function signSurd(a,b){
  if(a===0n)return b===0n?0:b>0n?1:-1;
  if(b===0n)return a>0n?1:-1;
  if((a>0n)===(b>0n))return a>0n?1:-1;
  const z=a*a-5n*b*b;
  return z===0n?0:(z>0n)===(a>0n)?1:-1;
}
function cmp(x,y){return signSurd(x[0]-y[0],x[1]-y[1]);}
function bestShort5(m){
  if(!Number.isSafeInteger(m)||m<1||m>128)throw Error("mass 1..128");
  let best=null,winner=null,visited=0,ties=0;
  for(let a=0;a<=m;a++)for(let b=0;b<=m-a;b++)for(let c=0;c<=m-a-b;c++){
    const w=[a,b,c,m-a-b-c].map(BigInt),v=squared5(w);
    const s=best===null?-1:cmp(v,best);
    visited++;
    if(s<0){best=v;winner=w;ties=1;}else if(s===0)ties++;
  }
  return {mass:m,witness:winner,squaredTwice:best,visited,ties};
}
function complexGain(a,q,k=1){
  order(q);let re=0,im=0;const m=Number(mass(a));
  if(!Number.isFinite(m)||m<=0)throw Error("unsupported numerical mass");
  for(let j=0;j<a.length;j++){const t=2*Math.PI*k*j/q;re+=Number(a[j])*Math.cos(t)/m;im+=Number(a[j])*Math.sin(t)/m;}
  return Math.hypot(re,im);
}
function fibShort5(k){
  if(!Number.isSafeInteger(k)||k<1||k>100)throw Error("index 1..100");
  let a=0n,b=1n;
  for(let i=0;i<k;i++){[a,b]=[b,a+b];}
  return [a+b,a,a,a+b];
}
export {trim,mul,divide,phi,plan,exactNotch,search,squared5,cmp,bestShort5,complexGain,fibShort5,mass};
