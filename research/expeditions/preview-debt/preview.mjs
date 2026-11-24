import {pathToFileURL} from 'node:url';
function laboratory(run=true){
  const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
  const close=(a,b,tol=1e-9)=>Math.abs(a-b)<=tol;
  const conv=(p,q)=>{const z=Array(p.length+q.length-1).fill(0);p.forEach((v,i)=>q.forEach((u,j)=>z[i+j]+=v*u));return z};
  const sub=(p,q)=>Array.from({length:Math.max(p.length,q.length)},(_,i)=>(p[i]||0)-(q[i]||0));
  const monomial=d=>Array(d).fill(0).concat(1);
  const divide=(p,a)=>{const q=Array(p.length-1).fill(0);for(let i=q.length-1;i>=0;i--)q[i]=p[i+1]+a*(q[i+1]||0);return {q,remainder:p[0]+a*q[0]}};
  function design(a,d,n=1){
    if(!(a>0&&a<1)||!Number.isSafeInteger(d)||d<0||d>4096||![1,2].includes(n))throw Error("domain: 0<a<1, integer 0<=d<=4096, n=1 or 2");
    const c=a**d, hnum=[-a,1], hden=[1,-a];
    if (!(c>0)) throw Error("numeric underflow: use higher precision");
    if(n===1){
      const q=d?Array.from({length:d},(_,i)=>a**(d-1-i)):[0];
      return {gain:c,gnum:conv(q,hden),gden:[1],enum:[c],eden:[1]};
    }
    if(d<2)return {gain:1,gnum:[0],gden:[1],enum:monomial(d),eden:[1]};
    const b=d*a**(d-1)*(1-a*a), m=(b+Math.hypot(b,2*c))/2, rr=c/m;
    const eden=[1-rr*a,rr-a], en=[m*(rr-a),m*(1-rr*a)];
    if (!(m>0 && Math.abs(eden[1])<Math.abs(eden[0]))) throw Error("numerically ill-conditioned equalizer");
    const v=sub(conv(monomial(d),eden),en);
    const f=divide(v,a), g=divide(f.q,a);
    assert(Math.abs(f.remainder)<1e-10&&Math.abs(g.remainder)<1e-10,"zero cancellation");
    return {gain:m,gnum:conv(g.q,conv(hden,hden)),gden:eden,enum:en,eden};
  }
  function evalPoly(p,w){
    let x=0,y=0;for(let i=p.length-1;i>=0;i--){const u=x*w[0]-y*w[1]+p[i];y=x*w[1]+y*w[0];x=u;}return [x,y];
  }
  const mul=(u,v)=>[u[0]*v[0]-u[1]*v[1],u[0]*v[1]+u[1]*v[0]];
  const div=(u,v)=>{const den=v[0]**2+v[1]**2;return [(u[0]*v[0]+u[1]*v[1])/den,(u[1]*v[0]-u[0]*v[1])/den]};
  const mag=u=>Math.hypot(...u);
  function filter(x,b,c){
    const y=[];for(let t=0;t<x.length;t++){let v=0;for(let i=0;i<b.length&&i<=t;i++)v+=b[i]*x[t-i];for(let i=1;i<c.length&&i<=t;i++)v-=c[i]*y[t-i];y.push(v/c[0]);}return y;
  }
  if (!run) return {design, filter};
  let designs=0, freqChecks=0, impulseChecks=0, witnessChecks=0;
  let maxFrequencyError=0,maxTimeError=0, maxWitnessError=0;
  const rows=[];
  for(const a of [.1,.25,.5,.75,.9,.95,.99]){
    for(let d=0;d<=32;d++){
      const values=[];
      for(const n of [1,2]){
        const z=design(a,d,n);designs++;
        const hn=n===1?[-a,1]:conv([-a,1],[-a,1]), hd=n===1?[1,-a]:conv([1,-a],[1,-a]);
        // Polynomial cross multiplication: no sampling needed for transfer identity.
        const diff=sub(conv(sub(conv(monomial(d),z.eden),z.enum),conv(hd,z.gden)),conv(conv(hn,z.gnum),z.eden));
        assert(diff.every(v=>Math.abs(v)<1e-9),"polynomial transfer identity");
        assert(z.gden.length===1||Math.abs(z.gden[1])<Math.abs(z.gden[0]),"stable equalizer denominator");
        for(let k=0;k<=512;k++){
          const t=Math.PI*k/512,w=[Math.cos(t),Math.sin(t)];
          const h=div(evalPoly(hn,w),evalPoly(hd,w));
          const e=mul(h,div(evalPoly(z.gnum,w),evalPoly(z.gden,w)));
          const target=evalPoly(monomial(d),w);
          const err=Math.abs(mag([target[0]-e[0],target[1]-e[1]])-z.gain);
          maxFrequencyError=Math.max(maxFrequencyError,err);
          assert(err<1e-6&&Math.abs(mag(h)-1)<1e-7,"all-pass / residual norm");
          freqChecks++;
        }
        const x=Array.from({length:512},(_,i)=>i===0?1:0);
        const y=filter(x,hn,hd), u=filter(y,z.gnum,z.gden), er=filter(x,z.enum,z.eden);
        for(let t=0;t<x.length;t++){
          const v=Math.abs((x[t-d]||0)-u[t]-er[t]);maxTimeError=Math.max(maxTimeError,v);
          assert(v<1e-7,"direct recurrence identity");impulseChecks++;
        }
        values.push(z.gain);
      }
      // A bi-infinite bounded input with an exponentially decaying prehistory.
      // y[-101]=0 exactly by the convergent convolution, not zero-state x initialization.
      let yp=0,xp=a**(d+101);
      for(let t=-100;t<=d;t++){
        const x=a**(d-t),y=-a*x+xp+a*yp;
        maxWitnessError=Math.max(maxWitnessError,Math.abs(y));assert(Math.abs(y)<1e-12,"indistinguishable prefix");witnessChecks++;yp=y;xp=x;
      }
      assert(values[1]+1e-12>=values[0],"cascade cannot improve optimum");
      rows.push({a,d,one:values[0],two:values[1]});
    }
  }
  assert(design(.5,1,2).gain===1&&design(.5,1,1).gain===.5,"repeated zero control");
  for(const args of [[0,1,1],[1,1,1],[.5,-1,1],[.5,1.2,1],[.5,1,3],[.5,4097,1],[.1,4096,2]]){let rejected=false;try{design(...args)}catch{rejected=true}assert(rejected,"invalid input accepted")}
  return {designs,freqChecks,impulseChecks,witnessChecks,maxFrequencyError,maxTimeError,maxWitnessError,rows};
}
const {design, filter} = laboratory(false);
export {design, filter, laboratory};
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) console.log(JSON.stringify(laboratory(), null, 2));
