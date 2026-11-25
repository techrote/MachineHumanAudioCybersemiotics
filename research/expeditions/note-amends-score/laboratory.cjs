'use strict';
// Synthetic constitutional-score oracle. No participant or operational data.
function laboratory(){
  let assertions=0, maps=0, trajectories=0, classes=0;
  const check=(v,msg)=>{if(!v)throw Error(msg);assertions++};
  const choose=(n,k)=>{let x=1;for(let j=1;j<=k;j++)x=x*(n-j+1)/j;return x};
  const count=(n,k)=>choose(n,k)*(n-1)**(n-k);
  const trace=(f,start)=>{const a=[],seen=new Map();let v=start;while(!seen.has(v)){seen.set(v,a.length);a.push(v);v=f[v]}return {path:a,repeat:v,period:a.length-seen.get(v)}};
  const rows=[];
  for(let n=1;n<=5;n++){
    const census=Array(n+1).fill(0), fibres=new Map();
    for(let i=0;i<n**n;i++){
      let j=i;const f=Array.from({length:n},()=>{const v=j%n;j=Math.floor(j/n);return v});
      const k=f.filter((v,i)=>v===i).length;census[k]++;maps++;
      for(let s=0;s<n;s++){
        const t=trace(f,s);trajectories++;
        check(t.path.length<=n,"bounded path");
        check(t.period>=1&&t.period<=n,"bounded period");
        let v=s;for(let step=0;step<2*n;step++){
          const pos=step<t.path.length?step:t.path.length-t.period+(step-t.path.length)%t.period;
          check(v===t.path[pos],"trace replay");v=f[v];
        }
        const key=[...t.path,t.repeat].join(",");
        if(!fibres.has(key))fibres.set(key,{t,census:Array(n+1).fill(0)});
        fibres.get(key).census[k]++;
      }
    }
    for(let k=0;k<=n;k++)check(census[k]===count(n,k),"fixed point count");
    for(const {t,census:c} of fibres.values()){
      classes++;
      const u=n-t.path.length, b=Number(t.period===1);
      check(c.reduce((a,b)=>a+b,0)===n**u,"fibre count");
      for(let k=0;k<=n;k++){
        const d=k-b;const expected=d<0||d>u?0:choose(u,d)*(n-1)**(u-d);
        check(c[k]===expected,"conditional fixed point count");
      }
    }
    rows.push({n,maps:n**n,fixed_point_census:census,trajectory_classes:fibres.size});
  }
  const a=[1,0,2,3],b=[1,0,3,2],c=[1,2,3,0];
  check(JSON.stringify(trace(a,0))===JSON.stringify(trace(b,0)),"identical performance");
  check(a.filter((v,i)=>v===i).length===2&&b.every((v,i)=>v!==i),"different retrospective availability");
  check(trace(c,0).period===4&&c.every((v,i)=>v!==i),"four-cycle not contradiction in prospective mode");
  return {maps,trajectories,classes,assertions,rows};
}
console.log(JSON.stringify(laboratory(),null,2));
