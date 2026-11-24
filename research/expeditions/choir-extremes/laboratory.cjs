"use strict";
// Exact BigInt moment-polytope vertex census. Run: node laboratory.cjs
function laboratory(){
 const gcd=(a,b)=>b?gcd(b,a%b):a<0n?-a:a;
 const F=(a,b=1n)=>{a=BigInt(a);b=BigInt(b);if(b<0n){a=-a;b=-b}const g=gcd(a,b);return [a/g,b/g]};
 const add=(a,b)=>F(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
 const neg=a=>F(-a[0],a[1]);
 const sub=(a,b)=>add(a,neg(b));
 const mul=(a,b)=>F(a[0]*b[0],a[1]*b[1]);
 const abs=a=>a[0]<0n?neg(a):a;
 const cmp=(a,b)=>{const z=a[0]*b[1]-b[0]*a[1];return z<0n?-1:z>0n?1:0};
 const key=(q,d)=>`${q[0]}/${q[1]},${d[0]}/${d[1]}`;
 const check=(b,msg)=>{if(!b)throw Error(msg)};
 const zero=F(0), one=F(1);
 function* choose(a,k,i=0,p=[]){if(!k){yield p;return}for(let j=i;j<=a.length-k;j++)yield* choose(a,k-1,j+1,[...p,a[j]])}
 function weights(s,n){
   return s.map((x,i)=>{
     let p=[1n],den=1n;
     for(let j=0;j<s.length;j++)if(j!==i){
       let y=BigInt(s[j]),v=Array(p.length+1).fill(0n);
       for(let l=0;l<p.length;l++){v[l]-=p[l]*y;v[l+1]+=p[l]}
       p=v;den*=BigInt(x)-y;
     }
     return F(p[0]+BigInt(n)*(p[2]??0n),den);
   });
 }
 let supportChecks=0,feasibleVertices=0,cornerChecks=0,momentChecks=0,tailChecks=0,profiles=0;
 let examples=[];
 for(let n=2;n<=30;n++)for(let k=2;k<=Math.min(3,n);k++){
   const nodes=Array.from({length:n+1},(_,i)=>2*i-n);
   const cap=F(1,n+(n%2)), qcross=k===2?F(1,n%2?n+1:n+2):n%2?F(n-2,2*(n-1)*(n+1)):F(n-4,2*(n-1)*(n-2));
   let wanted;
   if(n===2)wanted=[[F(1,2),zero]];
   else if(n===3)wanted=k===2?[[cap,cap],[cap,neg(cap)]]:[[cap,zero]];
   else wanted=[[zero,zero],[cap,zero],[qcross,qcross],[qcross,neg(qcross)]];
   const projected=new Set();
   const thresholds=nodes.filter(x=>x>0);
   let mins=thresholds.map(()=>one),maxs=thresholds.map(()=>zero);
   for(const s of choose(nodes,k+1)){
     supportChecks++;const w=weights(s,n);
     if(w.some(x=>x[0]<0n))continue;
     feasibleVertices++;
     for(let j=0;j<=k;j++){
       let actual=w.reduce((sum,x,i)=>add(sum,mul(x,F(BigInt(s[i])**BigInt(j)))),zero);
       check(cmp(actual,F(j===0?1:j===2?n:0))===0,"moments");momentChecks++;
     }
     const a=w[s.indexOf(-n)]??zero,b=w[s.indexOf(n)]??zero;
     const q=add(a,b),d=sub(b,a),ad=abs(d);
     projected.add(key(q,d));
     check(cmp(ad,q)<=0&&cmp(q,cap)<=0,`basic ${n},${k}`);
     if(n===2)check(cmp(q,F(1,2))===0&&cmp(d,zero)===0,"n2");
     else if(n===3){check(cmp(q,cap)===0,"n3");if(k===3)check(cmp(d,zero)===0,"n3 triple")}
     else if(k===2&&n%2===0)check(cmp(add(mul(F(n),q),mul(F(2),ad)),one)<=0,"pair even");
     else if(k===3){
       const slope=n%2?F(n-2,n):F(n*(n-4),n*n-2*n+4);
       check(cmp(ad,mul(slope,sub(cap,q)))<=0,`triple ${n}`);
     }
     thresholds.forEach((h,i)=>{
       const t=w.reduce((sum,x,j)=>Math.abs(s[j])>=h?add(sum,x):sum,zero);
       if(cmp(t,mins[i])<0)mins[i]=t;
       if(cmp(t,maxs[i])>0)maxs[i]=t;
     });
   }
   for(const [q,d] of wanted){
     // (cap,0) is not a vertex for odd pairwise n, but midpoint of two attainable corners.
     if(k===2&&n>=5&&n%2&&cmp(q,cap)===0&&cmp(d,zero)===0)continue;
     check(projected.has(key(q,d)),`missing corner ${n},${k}: ${key(q,d)}`);cornerChecks++;
   }
   thresholds.forEach((h,i)=>{
     const m=n%2;
     const upper=h*h<=n?one:F(n-m*m,h*h-m*m);
     const l=h-2;
     const lower=h===m?one:l*l>=n?zero:F(n-l*l,n*n-l*l);
     check(cmp(maxs[i],upper)===0&&cmp(mins[i],lower)===0,`tail ${n},${k},${h}`);tailChecks++;
   });
   profiles++;
   if([3,4,6,7,16,30].includes(n))examples.push({n,k,maxUnanimity:key(cap,zero).split(",")[0],perfectWitness:key(n===2||n===3&&k===3?zero:n===3?cap:qcross,zero).split(",")[0]});
 }
 return {supportChecks,feasibleVertices,momentChecks,cornerChecks,tailChecks,profiles,examples,assertionFailures:0};
}
if (require.main === module) console.log(JSON.stringify(laboratory(), null, 2));
module.exports = laboratory;
