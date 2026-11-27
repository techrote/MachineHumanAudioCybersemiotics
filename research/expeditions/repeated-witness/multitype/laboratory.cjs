"use strict";
// MHAC #813 additive multitype deletion lab; no dependencies.
function lab(){
const assert=(p,msg)=>{if(!p)throw Error(msg)};
const alphabet="ABC";
const sum=a=>a.reduce((x,y)=>x+y,0);
function* words(c,p=""){if(!sum(c)){yield p;return}for(let a=0;a<c.length;a++)if(c[a]){let z=c.slice();z[a]--;yield*words(z,p+alphabet[a])}}
function* comps(n,q,p=[]){if(q===1){yield [...p,n];return}for(let i=0;i<=n;i++)yield*comps(n-i,q-1,[...p,i])}
const choose=(n,k)=>{if(k<0||k>n)return 0n;let v=1n;for(let i=1;i<=k;i++)v=v*BigInt(n-i+1)/BigInt(i);return v};
const multi=c=>{let n=sum(c),v=1n;for(let k of c){v*=choose(n,k);n-=k}return v};
// Count embeddings, not distinct words; descending j prevents reuse of an occurrence.
function embed(w,v){let d=Array(v.length+1).fill(0n);d[0]=1n;for(let a of w)for(let j=v.length;j>0;j--)if(a===v[j-1])d[j]+=d[j-1];return d[v.length]}
// Product of deterministic greedy prefix acceptors with remaining composition.
function count(c,vs){let memo=new Map();function rec(left,p){let key=left.join(",")+"|"+p.join(",");if(memo.has(key))return memo.get(key);if(!sum(left))return vs.every((v,i)=>p[i]===v.length)?1n:0n;let z=0n;for(let a=0;a<left.length;a++)if(left[a]){let nxt=left.slice();nxt[a]--;z+=rec(nxt,p.map((j,i)=>j<vs[i].length&&vs[i][j]===alphabet[a]?j+1:j))}memo.set(key,z);return z}return rec(c,vs.map(()=>0))}
// Multivariate formal-series coefficient via convolution of truncated gap inventories.
function coeff(s,k){let memo=new Map();const factors=[-1];for(let a=0;a<s.length;a++)for(let j=0;j<s[a];j++)factors.push(a);
function rec(i,left){if(i===factors.length)return sum(left)===0?1n:0n;let key=i+"|"+left.join(",");if(memo.has(key))return memo.get(key);let z=0n;for(let n=0;n<=sum(left);n++)for(let a of comps(n,left.length))if(a.every((x,j)=>x<=left[j]&&(j!==factors[i]||x===0)))z+=multi(a)*rec(i+1,left.map((x,j)=>x-a[j]));memo.set(key,z);return z}return rec(0,k)}
let one=0,weight=0,single=0,two=0,intersectionProfiles={};
for(let n=0;n<=7;n++)for(let c of comps(n,3)){let ws=[...words(c)];for(let m=0;m<=n;m++)for(let s of comps(m,3)){if(s.some((v,i)=>v>c[i]))continue;let k=c.map((v,i)=>v-s[i]),f=coeff(s,k);for(let v of words(s)){let a=0n,b=0n;for(let w of ws){let z=embed(w,v);if(z)a++;b+=z}assert(a===f&&a===count(c,[v]),"one stream");one++;assert(b===choose(n,m)*multi(k),"embedding mass");weight++;let lost=k.map((v,i)=>v?i:-1).filter(i=>i>=0);if(lost.length===1){let j=lost[0];assert(a===choose(m-s[j]+k[j],k[j]),"single-type");single++}}}}
let c=[3,3,0],ws=[...words(c)],vs=[...words([2,2,0])],hist={};
for(let a of vs){let h={};for(let w of ws){let e=embed(w,a);if(e)h[String(e)]=(h[String(e)]||0)+1}hist[a]=h;
for(let b of vs){let hits=ws.filter(w=>embed(w,a)&&embed(w,b));let z=count(c,[a,b]);assert(z===BigInt(hits.length),"intersection");two++;intersectionProfiles[a+"/"+b]=hits.length}}
let ternary=[];for(let n=1;n<=6;n++)for(let c of comps(n,3)){let ws=[...words(c)],vs=new Set();for(let w of ws)for(let i=0;i<w.length;i++)vs.add(w.slice(0,i)+w.slice(i+1));let v=[...vs];for(let i=0;i<v.length;i++)for(let j=i;j<v.length;j++){let a=v[i],b=v[j];let z=ws.filter(w=>embed(w,a)&&embed(w,b)).length;assert(count(c,[a,b])===BigInt(z),"two streams ternary");two++}}
for(let k of [[1,1,1],[2,2,2],[3,3,3],[5,5,5]])ternary.push({survivor:"ABCABC",lost:k,compatible:String(coeff([2,2,2],k))});
return {singleStreamCases:one,embeddingMassChecks:weight,oneTypeReductionChecks:single,twoStreamChecks:two,posteriorWeights:hist,intersections:intersectionProfiles,largerCases:ternary};
}
console.log(JSON.stringify(lab(), null, 2));
