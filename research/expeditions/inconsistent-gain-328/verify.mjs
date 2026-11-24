import {solve,lossNumerator} from './gain.mjs';
function check(x,m){if(!x)throw Error(m)}
function bruteCycle(d){let p=0,q=1;const n=d.length;function rec(s,path,sum){let a=path.at(-1),v=sum+d[a][s];if(v*q>p*path.length){p=v;q=path.length}for(let j=s+1;j<n;j++)if(!path.includes(j))rec(s,[...path,j],sum+d[a][j])}for(let s=0;s<n;s++)rec(s,[s],0);return [p,q]}
function validate(r,edges){const {d,diameter,radius:[p,q],centerNumerators:y,cycle}=r;check(lossNumerator(d,y,q)===p,"primal");check(edges.every(([i,j,l,h])=>q*l<=y[j]-y[i]&&y[j]-y[i]<=q*h),"feasible center");check(cycle[0]===cycle.at(-1),"cycle");check(cycle.slice(1).reduce((s,v,k)=>s+d[cycle[k]][v],0)*q===p*(cycle.length-1),"dual");const [a,b]=bruteCycle(d);check(a*q===p*b,"oracle");check(2*p>=q*diameter&&p*d.length<=q*diameter*(d.length-1),"Jung");}
let count=0,gaps=0,midpointBad=0, hist={};
for(let id=0;id<729;id++){let u=id,edges=[];for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){let a=u%3;u=Math.floor(u/3);let b=u%3;u=Math.floor(u/3);edges.push([i,j,-a,b])}const r=solve(3,edges);validate(r,edges);
const pts=[];for(let x=-2;x<=2;x++)for(let y=-2;y<=2;y++){let v=[0,x,y];if(edges.every(([i,j,l,h])=>l<=v[j]-v[i]&&v[j]-v[i]<=h))pts.push(v)}
for(let i=0;i<3;i++)for(let j=0;j<3;j++)check(Math.max(...pts.map(v=>v[j]-v[i]))===r.d[i][j],"direct extrema");
let best=Infinity;for(let x=-12;x<=12;x++)for(let y=-12;y<=12;y++){let z=[0,x,y];let loss=Math.max(...pts.map(v=>{let w=v.map((a,i)=>6*a-z[i]);return Math.max(...w)-Math.min(...w)}));best=Math.min(best,loss)}
check(best*r.radius[1]===6*r.radius[0],"grid oracle");count++;if(2*r.radius[0]>r.radius[1]*r.diameter)gaps++;
const d=r.d;if(d[0][1]-d[1][0]+d[1][2]-d[2][1]!==d[0][2]-d[2][0])midpointBad++;
let key=r.radius.join("/");hist[key]=(hist[key]||0)+1;
}
const family=[];
for(let n=2;n<=12;n++){let e=Array.from({length:n-1},(_,i)=>[i,i+1,0,1]);e.push([0,n-1,0,1]);const r=solve(n,e);check(r.radius[0]*n===(n-1)*r.radius[1]&&r.diameter===1,"family");check(lossNumerator(r.d,r.centerNumerators,r.radius[1])===r.radius[0],"family center");family.push({n,radius:r.radius,center:r.centerNumerators})}
check(solve(3,[[0,1,0,1]]).status==="unbounded","disconnected");
check(solve(3,[[0,1,1,1],[1,2,1,1],[0,2,0,0]]).status==="infeasible","inconsistent");
const shifted=solve(3,[[0,1,10,11],[1,2,-5,-4],[0,2,5,6]]);validate(shifted,[[0,1,10,11],[1,2,-5,-4],[0,2,5,6]]);
console.log(JSON.stringify({population:count,strictRadiusGap:gaps,inconsistentPairMidpoints:midpointBad,radiusHistogram:hist,family,negativeControls:"passed",shifted},null,2));
