"use strict";
function run(){
const fail=(v,m)=>{if(!v)throw Error(m)};
const all=(n,L)=>L.flatMap(l=>Array.from({length:n},(_,i)=>[i,l]));
const row=(n,[i,l])=>Array.from({length:n},(_,j)=>Number((j-i+n)%n<l));
const sums=(x,E)=>E.map(([i,l])=>Array.from({length:l},(_,j)=>x[(i+j)%x.length]).reduce((a,b)=>a+b,0));
function graph(n,E){
 const adj=Array.from({length:n},()=>[]);
 for(const [i,l] of E){const j=(i+l)%n,w=Math.floor((i+l)/n);adj[i].push([j,w]);adj[j].push([i,-w]);}
 const p=Array(n).fill(null),ids=Array(n).fill(-1);let c=0,wind=false;
 for(let root=0;root<n;root++)if(p[root]===null){p[root]=0;ids[root]=c++;const stack=[root];while(stack.length){const i=stack.pop();for(const [j,w] of adj[i]){const v=p[i]-w;if(p[j]===null){p[j]=v;ids[j]=ids[i];stack.push(j);}else if(p[j]!==v)wind=true;}}}
 return {c,wind,p,ids,rank:n-c+Number(wind),knownRank:n-c+1};
}
function rank(A,n){
 A=A.map(r=>r.map(BigInt));let r=0;
 for(let j=0;j<n&&r<A.length;j++){let i=r;while(i<A.length&&A[i][j]===0n)i++;if(i===A.length)continue;[A[r],A[i]]=[A[i],A[r]];for(let k=r+1;k<A.length;k++){let b=A[k][j];if(b===0n)continue;const a=A[r][j];for(let m=j;m<n;m++)A[k][m]=a*A[k][m]-b*A[r][m];}r++;}
 return r;
}
function restore(n,E,y,Tknown=null){
 const adj=Array.from({length:n},()=>[]);E.forEach(([i,l],k)=>{const j=(i+l)%n,w=Math.floor((i+l)/n);adj[i].push([j,y[k],-w]);adj[j].push([i,-y[k],w]);});
 const a=Array(n).fill(null),b=Array(n).fill(0),q=[0];a[0]=0;let T=Tknown;
 for(let t=0;t<q.length;t++){let i=q[t];for(const [j,dy,dw] of adj[i]){const v=a[i]+dy,z=b[i]+dw;if(a[j]===null){a[j]=v;b[j]=z;q.push(j);}else{const den=b[j]-z,num=v-a[j];if(den){const cand=num/den;if(T!==null&&T!==cand)throw Error("inconsistent total");T=cand;}else if(num!==0)throw Error("inconsistent cycle");}}}
 if(q.length!==n||T===null)throw Error("not identifiable");const p=a.map((v,i)=>v+b[i]*T);return p.map((v,i)=>(i===n-1?T:p[i+1])-v);
}
const out={profiles:0,rankChecks:0,connectedBalanced:0,coveredConnectedBalanced:0,restorations:0,repairChecks:0,distances:[],witness:null};
function census(n,L){
 const E=all(n,L);
 for(let mask=0;mask<2**E.length;mask++){
  const F=E.filter((_,i)=>mask&(1<<i)),g=graph(n,F),A=F.map(e=>row(n,e));
  fail(rank(A,n)===g.rank,"rank");fail(rank([...A,Array(n).fill(1)],n)===g.knownRank,"known rank");out.profiles++;out.rankChecks+=2;
  const x=Array.from({length:n},(_,i)=>(i*i+3*i+1)%11),total=x.reduce((a,b)=>a+b,0),y=sums(x,F);
  if(g.c===1){fail(JSON.stringify(restore(n,F,y,total))===JSON.stringify(x),"known restore");out.restorations++;if(g.wind){fail(JSON.stringify(restore(n,F,y))===JSON.stringify(x),"unknown restore");out.restorations++;}else{out.connectedBalanced++;const covered=Array.from({length:n},(_,j)=>A.some(r=>r[j])).every(Boolean);if(covered){out.coveredConnectedBalanced++;if(!out.witness&&n>=4&&L.every(l=>l>=2)&&F.length>=n){
  const h=g.p.map((v,i)=>(i===n-1?1:g.p[i+1])-v);
  fail(sums(h,F).every(v=>v===0),"null witness");let replace=null;
  for(let k=0;k<F.length;k++){const [i,l]=F[k],rev=[(i+l)%n,n-l];if(F.some(e=>String(e)===String(rev)))continue;const G=F.map((e,j)=>j===k?rev:e);if(graph(n,G).wind){replace={index:k,complement:rev};break;}}
  if(replace)out.witness={n,L,windows:F,h,replace};
 }}}
 }
 if(mask%31===0){const pool=all(n,Array.from({length:n-1},(_,i)=>i+1));let G=[...F],r=g.rank,adds=0;for(const e of pool){const r2=graph(n,[...G,e]).rank;if(r2>r){G.push(e);r=r2;adds++;}}fail(r===n&&adds===n-g.rank,"repair");out.repairChecks++;}
 }
}
for(let n=2;n<=6;n++){for(let a=1;a<n;a++)census(n,[a]);for(let a=1;a<n;a++)for(let b=a+1;b<n;b++)census(n,[a,b]);}
census(4,[1,2,3]);
for(let n=2;n<=4;n++){
 const E=all(n,Array.from({length:n-1},(_,i)=>i+1));let d=n*(n-1),dt=d;
 for(let mask=0;mask<2**E.length;mask++){const g=graph(n,E.filter((_,i)=>mask&(1<<i))),erasures=E.length-mask.toString(2).replace(/0/g,"").length;if(g.rank<n)d=Math.min(d,erasures);if(g.knownRank<n)dt=Math.min(dt,erasures);}
 fail(d===(n<4?n*(n-1)/2:2*(n-1))&&dt===2*(n-1),"distance");out.distances.push({n,unknown:d,known:dt});
}
fail(out.witness!==null,"witness missing");
function wav(seq){
 const rate=8000,N=800,buf=new Uint8Array(44+2*N*seq.length),v=new DataView(buf.buffer);
 for(const [at,s] of [[0,"RIFF"],[8,"WAVE"],[12,"fmt "],[36,"data"]])for(let i=0;i<s.length;i++)buf[at+i]=s.charCodeAt(i);
 v.setUint32(4,buf.length-8,true);v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);v.setUint32(40,buf.length-44,true);
 seq.forEach((s,k)=>{for(let j=0;j<N;j++){const a=Math.min(j/40,(N-1-j)/40,1);v.setInt16(44+2*(k*N+j),Math.round(9000*a*Math.sin(2*Math.PI*(180+20*s)*j/rate)),true);}});return buf;
}
const eq=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
const fp=a=>{let h=2166136261;for(const b of a)h=Math.imul(h^b,16777619);return (h>>>0).toString(16).padStart(8,"0");};
const w=out.witness,x=Array(w.n).fill(2),z=x.map((v,i)=>v+w.h[i]),G=w.windows.map((e,i)=>i===w.replace.index?w.replace.complement:e);
const waves={latentA:wav(x),latentB:wav(z),publicA:wav(sums(x,w.windows)),publicB:wav(sums(z,w.windows)),repairA:wav(sums(x,G)),repairB:wav(sums(z,G))};
fail(!eq(waves.latentA,waves.latentB)&&eq(waves.publicA,waves.publicB)&&!eq(waves.repairA,waves.repairB),"PCM");
out.audio=Object.fromEntries(Object.entries(waves).map(([k,a])=>[k,{bytes:a.length,fnv1a:fp(a)}]));
out.witness.x=x;out.witness.z=z;out.witness.y=sums(x,w.windows);out.witness.repairedA=sums(x,G);out.witness.repairedB=sums(z,G);
return out;
}
if (typeof module !== "undefined") module.exports={run};
if (typeof require !== "undefined" && require.main===module) console.log(JSON.stringify(run(),null,2));
