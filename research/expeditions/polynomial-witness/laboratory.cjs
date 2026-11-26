'use strict';
// Exact standalone witness; no dependencies, no empirical data.
const assert=require('node:assert/strict');
const gcd=(a,b)=>b===0n?(a<0n?-a:a):gcd(b,a%b);
class F {
 constructor(n,d=1n){n=BigInt(n);d=BigInt(d);assert(d!==0n);if(d<0n){n=-n;d=-d;}const g=gcd(n,d);this.n=n/g;this.d=d/g;}
 add(b){return new F(this.n*b.d+b.n*this.d,this.d*b.d)}
 sub(b){return new F(this.n*b.d-b.n*this.d,this.d*b.d)}
 mul(b){return new F(this.n*b.n,this.d*b.d)}
 div(b){return new F(this.n*b.d,this.d*b.n)}
 cmp(b){const n=this.n*b.d-b.n*this.d;return n<0n?-1:n>0n?1:0}
 toString(){return this.d===1n?String(this.n):this.n+'/'+this.d}
}
const Z=new F(0),O=new F(1),sum=x=>x.reduce((a,b)=>a.add(b),Z);
const times=(x,k)=>x.mul(new F(k)), max0=x=>x.n>0n?x:Z;
const conv=(a,b)=>Array.from({length:a.length+b.length-1},(_,k)=>sum(a.map((x,i)=>x.mul(b[k-i]??Z))));
const power2=k=>k>=0?new F(2n**BigInt(k)):new F(1n,2n**BigInt(-k));
const normalize=x=>{const s=sum(x);return x.map(v=>v.div(s))};
const rowCheck=E=>{for(const row of E){assert.equal(sum(row).cmp(O),0);assert(row.every(v=>v.n>0n));}};
const hinge=(E,z)=>sum(E[0].map((p,j)=>max0(p.sub(z.mul(E[1][j])))));
const diff=(E,G,z)=>hinge(E,z).sub(hinge(G,z));
const product=(E,G)=>E.map((r,s)=>r.flatMap(p=>G[s].map(q=>p.mul(q))));
const knots=(E,G)=>[...E[0].map((p,i)=>p.div(E[1][i])),...G[0].map((p,i)=>p.div(G[1][i]))];
const dominates=(E,G)=>knots(E,G).every(z=>diff(E,G,z).n>=0n);
function fixture(a){
 const xs=[new F(1,4),new F(1,2),O,new F(2),new F(4)];
 const h=[Z,O,Z.sub(a),O,Z], slopes=[Z,...h.slice(1).map((x,i)=>x.sub(h[i]).div(xs[i+1].sub(xs[i]))),Z];
 const jumps=xs.map((_,i)=>slopes[i+1].sub(slopes[i]));
 const mk=sign=>{const w=jumps.map((x,i)=>({w:times(x,sign),x:xs[i]})).filter(p=>p.w.n>0n);return [normalize(w.map(p=>p.w.mul(p.x))),normalize(w.map(p=>p.w))]};
 const E=mk(1),G=mk(-1);rowCheck(E);rowCheck(G);
 const M=sum(jumps.map((v,i)=>max0(v).mul(xs[i]))),mass=sum(jumps.map(max0));
 assert.equal(sum(jumps).cmp(Z),0);assert.equal(sum(jumps.map((v,i)=>v.mul(xs[i]))).cmp(Z),0);
 const scale=mass.div(M);
 for(let i=0;i<xs.length;i++)assert.equal(diff(E,G,xs[i].mul(scale)).cmp(h[i].div(M)),0);
 return {E,G,scale,M};
}
function side(c){const p=normalize(c),q=normalize(c.map((x,i)=>x.div(power2(i))));const R=[p,q];rowCheck(R);return R}
function optimal(a){const c=[O];let prev=Z;while(true){const next=a.mul(c.at(-1)).sub(prev);if(next.n<=0n)return c;prev=c.at(-1);c.push(next);assert(c.length<1000)}}
function binomial(n){let v=1n;const c=[];for(let k=0;k<=n;k++){c.push(new F(v));v=v*BigInt(n-k)/BigInt(k+1)}return c}
function firstRepeat(a){const d=new F(2).sub(a);const t=new F(2).div(d);const ceil=(t.n+t.d-1n)/t.d;return Number(2n*ceil-3n)}
function str(x){return Array.isArray(x)?x.map(str):x.toString()}
function run(){
 let profiles=0,knot_checks=0,negative_controls=0,repeat_checks=0;
 const examples=[];
 for(let den=2;den<=20;den++)for(let num=1;num<2*den;num++){
  const a=new F(num,den), P=[O,Z.sub(a),O], c=optimal(a), {E,G,scale,M}=fixture(a),R=side(c);
  const A=product(E,R),B=product(G,R),coeff=conv(P,c);assert(coeff.every(v=>v.n>=0n));assert(dominates(A,B));assert(!dominates(E,G));assert(!dominates(G,E));
  const s=R[0][0].div(R[1][0]),S=sum(c);
  for(let k=-1;k<=coeff.length;k++){
   const z=scale.mul(s).mul(power2(k-1));const expect=(coeff[k]??Z).div(S).div(M);
   assert.equal(diff(A,B,z).cmp(expect),0);knot_checks++;
  }
  if(c.length>1){const R0=side(c.slice(0,-1));assert(!dominates(product(E,R0),product(G,R0)));negative_controls++}
  const n=firstRepeat(a);
  // Independently check exact central coefficients at n and n-1.
  assert(conv(P,binomial(n)).every(v=>v.n>=0n));
  assert(conv(P,binomial(n-1)).some(v=>v.n<0n));repeat_checks+=2;
  if(den===10||den===2&&num===3||den===20&&num===39)examples.push({a:String(a),alphabet:c.length,repeated_binary_reads:n});
  profiles++;
 }
 // Nonlattice and lattice obstruction fixtures: at a>=2, no polynomial catalyst.
 for(const a of [new F(2),new F(5,2),new F(3)]){
  const {E,G}=fixture(a);for(const c of [[O],[O,O],[O,new F(3),O],[O,O,O,O]]){
   const R=side(c);assert(!dominates(product(E,R),product(G,R)));negative_controls++;
  }
  // A non-geometric side with rows [1/3,2/3] and [2/5,3/5].
  const R=[[new F(1,3),new F(2,3)],[new F(2,5),new F(3,5)]];
  assert(!dominates(product(E,R),product(G,R)));negative_controls++;
 }
 const a=new F(3,2),{E,G}=fixture(a),c=optimal(a),R=side(c);
 return {profiles,knot_checks,negative_controls,repeat_checks,examples,fixture:{E:str(E),F:str(G),R:str(R),multiplier:str(c),product_coefficients:str(conv([O,Z.sub(a),O],c))}};
}
if(require.main===module)console.log(JSON.stringify(run(),null,2));
module.exports={run};
