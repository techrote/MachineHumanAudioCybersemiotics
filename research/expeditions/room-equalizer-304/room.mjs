// Synthetic/formal experiment, Refs #304. No dependencies.
// Complex numbers are [real, imag]. Normalized gain coordinates are used internally.
const add=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const mul=(a,s)=>[a[0]*s,a[1]*s];
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0];
const norm=a=>Math.hypot(...a);
const inv=a=>[a[0]/dot(a,a),-a[1]/dot(a,a)];
function validate(h) {
  if(!Array.isArray(h)||!h.length||h.length>64||h.some(z=>!Array.isArray(z)||z.length!==2||z.some(x=>!Number.isFinite(x)||Math.abs(x)>1e100)))
    throw new RangeError("expected 1..64 finite complex coefficients, components <= 1e100");
}
function bary(p,a,b,c) {
  const v=sub(b,a),w=sub(c,a),d=cross(v,w);
  if(Math.abs(d)<=1e-14*norm(v)*norm(w))return null;
  const u=sub(p,a),y=cross(u,w)/d,z=cross(v,u)/d;
  return [1-y-z,y,z];
}
// Candidate enumeration + feasible dual mixture. Bounds are floating-point estimates,
// not interval-arithmetic certificates; refuse to claim resolution if gap is large.
export function solveRoom(h) {
  validate(h);
  const zi=h.findIndex(z=>norm(z)===0);
  if(zi>=0)return {status:"resolved",gain:[0,0],lower:1,upper:1,support:[zi],weights:[1]};
  const scale=Math.max(...h.map(norm));
  h=h.map(z=>[z[0]/scale,z[1]/scale]);
  const w=h.map(norm);
  if(Math.min(...w)<1e-6||scale<1e-100)throw new RangeError("unsupported gain dynamic range");
  const c=h.map(inv),n=h.length;
  let best=[0,0],upper2=1,lower2=0,support=[0],weights=[1];
  const value=(g,i)=>dot(sub(g,c[i]),sub(g,c[i]))*w[i]**2;
  function candidate(g) {
    if(!g.every(Number.isFinite))return;
    const e=Math.max(...c.map((_,i)=>value(g,i)));
    if(e<upper2){best=g;upper2=e;}
  }
  function dual(ids,mu) {
    if(!mu||mu.some(v=>!Number.isFinite(v)||v< -1e-10))return;
    let lam=mu.map((v,j)=>Math.max(0,v)/w[ids[j]]**2);
    const sum=lam.reduce((a,b)=>a+b,0);
    if(!(sum>0))return;
    lam=lam.map(v=>v/sum);
    let den=0, num=[0,0];
    ids.forEach((i,j)=>{const a=lam[j]*w[i]**2;den+=a;num=add(num,mul(c[i],a));});
    const g=mul(num,1/den);
    const lo=ids.reduce((s,i,j)=>s+lam[j]*value(g,i),0);
    if(lo>lower2){lower2=lo;support=ids;weights=lam;}
    candidate(g);
  }
  for(let i=0;i<n;i++)candidate(c[i]);
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
    const mu=[w[i]/(w[i]+w[j]),w[j]/(w[i]+w[j])];
    dual([i,j],mu);
  }
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)for(let k=j+1;k<n;k++){
    const ids=[i,j,k];
    // g=0 has equal residual 1 at all receivers; try its dual certificate.
    dual(ids,bary([0,0],c[i],c[j],c[k]));
    // In reciprocal coordinates u=1/g, equal residuals mean equal distances
    // to the three h values. Solve the circumcenter equations.
    const a=sub(h[j],h[i]),b=sub(h[k],h[i]),d=cross(a,b);
    if(Math.abs(d)<=1e-14*norm(a)*norm(b))continue;
    const x=(dot(h[j],h[j])-dot(h[i],h[i]))/2;
    const y=(dot(h[k],h[k])-dot(h[i],h[i]))/2;
    const u=[(x*b[1]-y*a[1])/d,(a[0]*y-b[0]*x)/d];
    if(norm(u)<1e-14)continue;
    const g=inv(u);
    candidate(g);
    dual(ids,bary(g,c[i],c[j],c[k]));
  }
  const lower=Math.sqrt(Math.max(0,lower2)),upper=Math.sqrt(Math.max(0,upper2));
  return {status:Math.abs(upper-lower)<=1e-8?"resolved":"unresolved",gain:best.map(x=>x/scale),
    lower,upper,support,weights};
}
export function pairBound(h) {
  validate(h);let m=h.some(z=>norm(z)===0)?1:0;
  for(let i=0;i<h.length;i++)for(let j=i+1;j<h.length;j++){
    const d=norm(h[i])+norm(h[j]); if(d)m=Math.max(m,norm(sub(h[i],h[j]))/d);
  }
  return m;
}
// Independent algorithm: binary search over the intersection of weighted disks.
// Any nonempty finite disk intersection contains a center or a boundary crossing.
// Used as a numerical cross-check, not a rigorous interval oracle.
export function diskOracle(h) {
  validate(h);
  if(h.some(z=>norm(z)===0))return 1;
  const scale=Math.max(...h.map(norm));
  h=h.map(z=>[z[0]/scale,z[1]/scale]);
  const c=h.map(inv),w=h.map(norm);
  if(Math.min(...w)<1e-6||scale<1e-100)throw new RangeError("unsupported gain dynamic range");
  function feasible(t){
    const rr=w.map(x=>t/x);
    const ok=p=>c.every((z,i)=>norm(sub(p,z))<=rr[i]+1e-11*Math.max(1,rr[i],norm(z)));
    if(c.some(ok))return true;
    for(let i=0;i<c.length;i++)for(let j=i+1;j<c.length;j++){
      const v=sub(c[j],c[i]),d=norm(v),a=rr[i],b=rr[j];
      if(d===0||d>a+b||d<Math.abs(a-b))continue;
      const x=(a*a-b*b+d*d)/(2*d),y=Math.sqrt(Math.max(0,a*a-x*x));
      const e=mul(v,1/d),mid=add(c[i],mul(e,x)),perp=[-e[1]*y,e[0]*y];
      if(ok(add(mid,perp))||ok(sub(mid,perp)))return true;
    }
    return false;
  }
  let lo=0,hi=1;
  for(let i=0;i<48;i++){const m=(lo+hi)/2;if(feasible(m))hi=m;else lo=m;}
  return hi;
}
// Exact combinatorial strict-improvement decision for integer coefficients.
// For nonzero vectors, origin in convex hull iff an antipodal pair or an
// origin-containing triangle exists. BigInt cross/dot tests avoid float geometry.
export function integerObstruction(h){
  validate(h);
  if(h.some(z=>z.some(x=>!Number.isSafeInteger(x))))throw new RangeError("integer coefficients required");
  const p=h.map(z=>z.map(BigInt)),C=(a,b)=>a[0]*b[1]-a[1]*b[0],D=(a,b)=>a[0]*b[0]+a[1]*b[1];
  for(let i=0;i<p.length;i++)if(D(p[i],p[i])===0n)return [i];
  for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)if(C(p[i],p[j])===0n&&D(p[i],p[j])<0n)return [i,j];
  for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)for(let k=j+1;k<p.length;k++){
    const s=[C(p[i],p[j]),C(p[j],p[k]),C(p[k],p[i])];
    if(s.every(x=>x>=0n)&&s.some(x=>x>0n)||s.every(x=>x<=0n)&&s.some(x=>x<0n))return [i,j,k];
  }
  return null;
}
// Fixed-threshold split into independent gain groups. Numerical ambiguities
// are not silently classified: a group is accepted only with upper < target-margin,
// rejected only with lower > target+margin. Otherwise return unresolved.
export function splitRoom(h,target,margin=1e-8){
  validate(h);
  if(h.length>12||!(target>0&&target<1)||!(margin>0&&margin<target))throw new RangeError("split supports 1..12 receivers, 0<target<1");
  const n=h.length,N=1<<n,forbid=[];
  for(let m=1;m<N;m++){
    const ids=Array.from({length:n},(_,i)=>i).filter(i=>m&(1<<i));
    if(ids.length>3)continue;
    const q=solveRoom(ids.map(i=>h[i]));
    if(q.lower>target+margin)forbid.push(m);
    else if(!(q.upper<target-margin))return {status:"unresolved",ambiguous:ids};
  }
  const good=Array.from({length:N},(_,m)=>!forbid.some(f=>(m&f)===f));
  const dp=Array(N).fill(Infinity),pick=Array(N).fill(0);dp[0]=0;
  for(let m=1;m<N;m++){
    const first=m&-m;
    for(let s=m;s;s=(s-1)&m)if((s&first)&&good[s]&&1+dp[m^s]<dp[m]){
      dp[m]=1+dp[m^s];pick[m]=s;
    }
  }
  if(!Number.isFinite(dp[N-1]))return {status:"infeasible"};
  const groups=[];
  for(let m=N-1;m;m^=pick[m]){
    const ids=Array.from({length:n},(_,i)=>i).filter(i=>pick[m]&(1<<i));
    const q=solveRoom(ids.map(i=>h[i]));
    if(!(q.upper<target-margin))return {status:"unresolved",ambiguous:ids};
    groups.push({ids,gain:q.gain,error:q.upper});
  }
  return {status:"resolved",count:groups.length,groups,forbidden:forbid.length};
}
