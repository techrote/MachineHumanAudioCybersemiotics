'use strict';
function qualify() {
  const assert=(p,msg)=>{if(!p)throw Error(msg)};
  const sum=a=>a.reduce((x,y)=>x+y,0n);
  function choose(n,k){let c=1n;for(let j=1;j<=k;j++)c=c*BigInt(n-j+1)/BigInt(j);return c}
  function basis(k){let d=k+1,u=Array.from({length:d+1},(_,i)=>(i%2?-1n:1n)*choose(d,i));u.push(0n);let v=[0n,...u.slice(0,-1)];return {u,v,cat:choose(2*d,d)/BigInt(d+1)}}
  function score(a,b){let s=0n,z=0n,t=sum(b);for(let i=0;i<a.length;i++){z+=a[i]*(2n*s+b[i]-t);s+=b[i]}return z}
  function literal(a,b){let z=0n;for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)z+=BigInt(Math.sign(i-j))*a[i]*b[j];return z}
  function moments(a,k,levels=a.map((_,i)=>BigInt(i))){return Array.from({length:k+1},(_,j)=>sum(a.map((v,i)=>v*levels[i]**BigInt(j))))}
  function match(a,k){let m=moments(a[0],k).join(",");return a.every(x=>x.every(y=>y>=0n)&&moments(x,k).join(",")===m)}
  function convolve(a,b){let c=Array(a.length+b.length-1).fill(0n);a.forEach((x,i)=>b.forEach((y,j)=>c[i+j]+=x*y));return c}
  function cycle(k){let {u,v,cat}=basis(k),M=[...u.map(x=>-x),...v.map(x=>-x),...u.map((x,i)=>x+v[i])].reduce((a,b)=>a>b?a:b);return {cat,M,p:[v.map(x=>M+x),u.map(x=>M+x),u.map((x,i)=>M-x-v[i])]}}
  const receipt={scope:"Synthetic independent draws, tie-half comparison; exact BigInt arithmetic",cycles:[],repeated:[],tournaments:0,tournamentPairChecks:0,smallAlphabet:{profiles:0,fibres:0,triples:0},failures:0};
  for(let k=1;k<=32;k++){let {u,v,cat}=basis(k),{M,p}=cycle(k);assert(score(v,u)===cat,"Catalan");assert(literal(v,u)===cat,"literal");assert(match(p,k),"moment cycle");let s=[score(p[0],p[1]),score(p[1],p[2]),score(p[2],p[0])];assert(s.every(x=>x===cat),"balanced");receipt.cycles.push({k,levels:k+3,countsPerLaw:String(sum(p[0])),marginNumerator:String(cat),marginDenominator:String(2n*sum(p[0])**2n)});}
  for(let k=1;k<=10;k++){let {p}=cycle(k),q=p;for(let draws=1;draws<=12;draws++){assert(match(q,k),"convolved moments");let s=[score(q[0],q[1]),score(q[1],q[2]),score(q[2],q[0])];assert(s[0]===literal(q[0],q[1])&&s[1]===literal(q[1],q[2])&&s[2]===literal(q[2],q[0]),"convolved literal");receipt.repeated.push({k,draws,net:s.map(String),denominator:String(2n*sum(q[0])**2n),signs:s.map(x=>x>0n?"+":x<0n?"-":"0").join("")});q=q.map((x,i)=>convolve(x,p[i]))}}
  // One disjoint moment-null block per vertex except the last; each unordered pair has exactly one nonzero cross-term.
  for(let k=1;k<=3;k++){let {u,v,cat}=basis(k),M=[...u,...v].reduce((m,x)=>{let a=x<0n?-x:x;return a>m?a:m},0n);
    for(let t=2;t<=5;t++){let edges=[];for(let i=0;i<t;i++)for(let j=i+1;j<t;j++)edges.push([i,j]);for(let mask=0;mask<2**edges.length;mask++){
      let desired=Array.from({length:t},()=>Array(t).fill(0n));edges.forEach(([i,j],idx)=>{desired[i][j]=(mask>>idx)&1?1n:-1n;desired[j][i]=-desired[i][j]});
      let p=Array.from({length:t},(_,i)=>Array.from({length:t-1},(_,b)=>u.map((x,l)=>M+(i===b?v[l]:i>b?desired[b][i]*x:0n))).flat());
      assert(match(p,k),"tournament moments");for(let [i,j] of edges){assert(score(p[i],p[j])===desired[i][j]*cat,"tournament edge");receipt.tournamentPairChecks++}receipt.tournaments++;
    }}
  }
  function* compositions(total,n,p=[]){if(n===1){yield [...p,BigInt(total)];return}for(let i=0;i<=total;i++)yield*compositions(total-i,n-1,[...p,BigInt(i)])}
  // Literal finite negative controls: nonuniform ordered alphabets, k+2 or fewer levels.
  for(let k=1;k<=4;k++)for(let n=2;n<=k+2;n++)for(let kind=0;kind<2;kind++){
    let levels=Array.from({length:n},(_,i)=>BigInt(kind?i*i+i:i)),fibres=new Map();
    for(let a of compositions(8,n)){let key=moments(a,k,levels).join(",");if(!fibres.has(key))fibres.set(key,[]);fibres.get(key).push(a);receipt.smallAlphabet.profiles++}
    for(let f of fibres.values()){receipt.smallAlphabet.fibres++;for(let i=0;i<f.length;i++)for(let j=i+1;j<f.length;j++)for(let l=j+1;l<f.length;l++){let s=[literal(f[i],f[j]),literal(f[j],f[l]),literal(f[l],f[i])];assert(!s.every(x=>x>0n)&&!s.every(x=>x<0n),"forbidden small cycle");receipt.smallAlphabet.triples++}}
  }
  return receipt;
}
console.log(JSON.stringify(qualify(), null, 2));
