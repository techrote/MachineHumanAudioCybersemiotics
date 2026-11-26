'use strict';
function laboratory(){
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const prod=a=>a.reduce((x,y)=>x*y,1);
  const pop=x=>{let n=0;while(x){n+=x&1;x>>=1}return n};
  const c=(p,t)=>t%p===0?p-1:-1;
  const signal=(ps,ss,ws=ps.map(()=>1),dc=0)=>Array.from({length:2*prod(ps)},(_,t)=>dc+(-1)**(t%2)*ps.reduce((z,p,i)=>z+ss[i]*ws[i]*c(p,t),0));
  const out={support_profiles:[],literal_correlation_entries:0,translation_checks:0,moment_profiles:0,quartic_phase_profiles:0};
  for(const ps of [[3,5],[5,7],[3,7,11],[5,7,11],[3,5,7,11]]){
    const N=2*prod(ps),m=ps.length;
    const fs=[[0,0]];
    ps.forEach((p,i)=>{for(let a=1;a<2*p;a+=2)if(a!==p)fs.push([a*N/(2*p),1<<i])});
    let dp=new Set([0]);const masks=[];
    for(let order=1;order<=6;order++){
      const next=new Set();
      for(const v of dp)for(const [f,b] of fs)next.add(((Math.floor(v/(1<<m))+f)%N)*(1<<m)+((v%(1<<m))^b));
      dp=next;
      let z=[...dp].filter(v=>v<(1<<m)).sort((a,b)=>a-b);
      assert(z.every(v=>pop(v)==0||(order===6&&pop(v)===2)),"mask bound");
      if(order===6)assert(z.length===1+m*(m-1)/2,"all pair masks");
      masks.push(z);
    }
    const base=signal(ps,ps.map(()=>1));
    const reps=[];
    for(let b=0;b<(1<<(m-1));b++){
      const s=ps.map((_,i)=>i===0?1:(b>>(i-1)&1)?-1:1);
      const x=signal(ps,s);
      const rot=x.join(",");
      for(const prev of reps){
        assert(!(prev+prev).includes(","+rot+","),"rotation collision"); // supplemental direct check below
      }
      const canon=x.map((_,j)=>x.slice(j).concat(x.slice(0,j)).join(",")).sort()[0];
      assert(!reps.includes(canon),"distinct cyclic orbits");
      reps.push(canon);out.translation_checks++;
      const bs=ps.map(p=>(p-1)*(p-2));
      const delta=20*bs.reduce((z,bi,i)=>z+bs.slice(i+1).reduce((q,bj,j)=>q+bi*bj*(s[i]*s[i+j+1]-1),0),0);
      const sum6=x.reduce((z,v)=>z+v**6,0);
      const ref6=base.reduce((z,v)=>z+v**6,0);
      assert(sum6-ref6===N*delta,"sixth moment formula");out.moment_profiles++;
    }
    out.support_profiles.push({primes:ps,N,masks,orbits:reps.length});
  }
  // Direct time-domain correlations on positive integer signals; no Fourier arithmetic.
  const x=signal([3,5],[1,1],[1,1],7),y=signal([3,5],[1,-1],[1,1],7),N=x.length;
  const shifted=a=>Array.from({length:N},(_,j)=>a.map((_,t)=>a[(t+j)%N]));
  const X=shifted(x),Y=shifted(y);
  function check(a,b,depth){
    assert(a.reduce((z,v)=>z+v,0)===b.reduce((z,v)=>z+v,0),"literal correlation mismatch");
    out.literal_correlation_entries++;
    if(depth<5)for(let j=0;j<N;j++)check(a.map((v,t)=>v*X[j][t]),b.map((v,t)=>v*Y[j][t]),depth+1);
  }
  check(x,y,1);
  // Complete fourth-order phase equations for p>=5, on the pth-root times sign grid.
  // Phases are exponents modulo 2p, and u(-a) is the conjugate.
  for(const p of [5,7]){
    let accepted=0,checked=0,mod=2*p;
    const u=Array(p).fill(0);
    function visit(a){
      if(a>(p-1)/2){
        checked++;
        const sums=new Map();
        for(let i=1;i<p;i++)for(let j=1;j<p;j++){
          const k=(i+j)%p,v=(u[i]+u[j])%mod;
          if(sums.has(k)&&sums.get(k)!==v)return;
          sums.set(k,v);
        }
        accepted++;return;
      }
      for(let z=0;z<mod;z++){u[a]=z;u[p-a]=(mod-z)%mod;visit(a+1)}
    }
    visit(1);assert(accepted===2*p,"quartic fiber finite grid");
    out.quartic_phase_profiles+=checked;
  }
  const bs=[12,30,90,132,240];
  const s1=[1,1,1,-1,1],s2=[1,1,1,-1,-1];
  const score=s=>bs.reduce((z,b,i)=>z+b*s[i],0)**2;
  assert(score(s1)===score(s2),"zero-lag collision");
  out.scalar_collision={primes:[5,7,11,13,17],signs:[s1,s2],squared_signed_sum:score(s1)};
  out.example={period:N,positive_dc:7,first_five_equal:true,centered_sixth_sums:[signal([3,5],[1,1]).reduce((z,v)=>z+v**6,0),signal([3,5],[1,-1]).reduce((z,v)=>z+v**6,0)]};
  return out;
}
console.log(JSON.stringify(laboratory(),null,2));
