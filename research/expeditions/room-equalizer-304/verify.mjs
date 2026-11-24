// Refs #304. Deterministic synthetic checks.
export function run({solveRoom,pairBound,diskOracle,integerObstruction,splitRoom}){
  const assert=(ok,msg)=>{if(!ok)throw new Error(msg)};
  const close=(a,b,t=2e-7)=>Math.abs(a-b)<=t;
  const stats={triples:0,quadruples:0,random:0,oracle:0,obstructed:0,pairwiseOnly:0,allImprove:0,antipodalObstructions:0,maxOracleError:0,maxGap:0,maxRatio:0,splitChecks:0,negativeChecks:0};
  let example=null, maxExample=null;
  function check(h,exact=false,oracle=true){
    const q=solveRoom(h),p=pairBound(h);
    assert(q.status==="resolved","unresolved "+JSON.stringify(h)+" "+JSON.stringify(q));
    assert(q.lower<=q.upper+1e-9,"negative gap");
    stats.maxGap=Math.max(stats.maxGap,Math.abs(q.upper-q.lower));
    const [x,y]=q.gain;
    const e=Math.max(...h.map(([a,b])=>Math.hypot(1-a*x+b*y,a*y+b*x)));
    assert(close(e,q.upper,1e-9),"primal replay");
    const den=q.support.reduce((s,i,j)=>s+q.weights[j]*(h[i][0]**2+h[i][1]**2),0);
    const re=q.support.reduce((s,i,j)=>s+q.weights[j]*h[i][0],0),im=q.support.reduce((s,i,j)=>s+q.weights[j]*h[i][1],0);
    const dual2=den===0?1:Math.max(0,1-(re*re+im*im)/den);
    assert(close(dual2,q.lower*q.lower,1e-8),"dual replay");
    assert(q.weights.every(w=>w>=0)&&close(q.weights.reduce((a,b)=>a+b,0),1,1e-10),"invalid weights");
    assert(q.upper+1e-8>=p && q.upper<=2*p/Math.sqrt(3)+1e-8,"pair ratio");
    if(p>1e-8&&q.upper/p>stats.maxRatio){stats.maxRatio=q.upper/p;maxExample=h;}
    if(oracle){const o=diskOracle(h);stats.oracle++;stats.maxOracleError=Math.max(stats.maxOracleError,Math.abs(o-q.upper));assert(close(o,q.upper),"disk oracle mismatch "+JSON.stringify(h)+" "+o+" "+q.upper);}
    if(exact){
      const ob=integerObstruction(h);
      if(ob){stats.obstructed++;assert(close(q.upper,1,1e-9),"integer obstruction mismatch");if(ob.length===2)stats.antipodalObstructions++;if(ob.length===3&&p<1-1e-9){stats.pairwiseOnly++;example??=h;}}
      else {stats.allImprove++;assert(q.upper<1-1e-9,"missed improvement");}
    }
    return q;
  }
  const grid=[];for(let x=-2;x<=2;x++)for(let y=-2;y<=2;y++)if(x||y)grid.push([x,y]);
  for(let i=0;i<grid.length;i++)for(let j=i+1;j<grid.length;j++)for(let k=j+1;k<grid.length;k++){
    const h=[grid[i],grid[j],grid[k]];check(h,true);stats.triples++;
    for(let l=k+1;l<grid.length;l++){check([...h,grid[l]],true,false);stats.quadruples++;}
  }
  let seed=304;
  const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2**32;};
  for(let i=0;i<500;i++){
    const h=Array.from({length:2+Math.floor(rnd()*7)},()=>{const a=rnd()*2*Math.PI,w=.2+4*rnd();return [w*Math.cos(a),w*Math.sin(a)]});
    check(h);stats.random++;
  }
  const roots=[[1,0],[-.5,Math.sqrt(3)/2],[-.5,-Math.sqrt(3)/2]];
  assert(close(check(roots).upper,1)&&close(pairBound(roots),Math.sqrt(3)/2),"sharp example");
  const same=[[1,0],[1,0],[1,0]];assert(close(check(same).upper,0),"equal phase control");
  assert(check([[0,0],[1,0]]).upper===1,"zero channel control");stats.negativeChecks+=3;
  const split=splitRoom(roots,.9);assert(split.status==="resolved"&&split.count===2,"split root");
  assert(splitRoom(roots,.8).count===3,"split stricter");
  assert(splitRoom(roots,Math.sqrt(3)/2).status==="unresolved","boundary must not overclaim");
  assert(splitRoom([[0,0],[1,0]],.9).status==="infeasible","zero cannot split away");
  assert(splitRoom(same,.2).count===1,"same control");stats.splitChecks+=5;
  // Direct brute force assignment oracle for small partition instances.
  function brute(h,t){
    const groups=[];let best=h.length+1;
    function visit(i){
      if(groups.length>=best)return;
      if(i===h.length){best=groups.length;return;}
      for(const g of groups.slice()){
        g.push(h[i]);if(diskOracle(g)<t-1e-7)visit(i+1);g.pop();
      }
      groups.push([h[i]]);visit(i+1);groups.pop();
    }
    visit(0);return best;
  }
  for(let i=0;i<80;i++){
    const h=Array.from({length:5},()=>{const a=rnd()*2*Math.PI;return [Math.cos(a),Math.sin(a)]}),t=.3+.6*rnd();
    const s=splitRoom(h,t);assert(s.status==="resolved"&&s.count===brute(h,t),"partition mismatch");stats.splitChecks++;
  }
  return {stats,example,maxExample,sharp:{pair:pairBound(roots),joint:solveRoom(roots).upper,split},population:"all distinct triples and quadruples of nonzero integer points in [-2,2]^2; plus seeded samples"};
}

import * as room from "./room.mjs";
console.log(JSON.stringify(run(room),null,2));
