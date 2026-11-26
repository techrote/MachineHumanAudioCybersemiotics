"use strict";
function run(){
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const key=p=>p.join(",");
  const tally=(items)=>{const m=new Map();for(const [x,w] of items)m.set(x,(m.get(x)||0)+w);return m};
  const project=(law,v)=>tally(law.map(([p,w])=>[dot(p,v),w]));
  const sig=m=>JSON.stringify([...m.entries()].filter(([,w])=>w!==0).sort((a,b)=>a[0]-b[0]));
  const tv2=(a,b)=>[...new Set([...a.keys(),...b.keys()])].reduce((s,k)=>s+Math.abs((a.get(k)||0)-(b.get(k)||0)),0);
  const joint=law=>tally(law.map(([p,w])=>[key(p),w]));
  const dirs=[[1,0],[0,1],[1,1],[1,-1],[1,2],[2,1],[1,3]];
  const grid=Array.from({length:25},(_,i)=>[Math.floor(i/5)-2,i%5-2]);
  const fixtures=[];
  for(let i=0;i<25;i++)for(let j=i+1;j<25;j++)for(let k=j+1;k<25;k++){
    const law=[i,j,k].map(n=>[grid[n],1]);
    fixtures.push({law,code:dirs.map(v=>sig(project(law,v)))});
  }
  let subsetChecks=0,threeCollisions=0,quadChecks=0;
  for(let i=0;i<dirs.length;i++)for(let j=i+1;j<dirs.length;j++)for(let k=j+1;k<dirs.length;k++){
    const seen=new Set();
    for(const f of fixtures){
      const s=[i,j,k].map(t=>f.code[t]).join("|");
      if(seen.has(s))threeCollisions++;seen.add(s);subsetChecks++;
    }
    for(let l=k+1;l<dirs.length;l++){
      const seen4=new Set();
      for(const f of fixtures){
        const s=[i,j,k,l].map(t=>f.code[t]).join("|");
        assert(!seen4.has(s),"four projections collision");seen4.add(s);quadChecks++;
      }
    }
  }
  assert(threeCollisions>0,"missing three-line negative control");
  let decodes=0;
  for(let n=0;n<fixtures.length;n+=23){
    const truth=fixtures[n], receipt=truth.code.slice();
    receipt[n%7]="corrupted";receipt[(n+1)%7]=null;
    const candidates=fixtures.filter(f=>f.code.reduce((s,x,i)=>s+(receipt[i]!==null&&receipt[i]!==x?1:0),0)<=1);
    assert(candidates.length===1&&candidates[0]===truth,"one error plus one erasure");
    decodes++;
  }
  let seed=690;
  const rng=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
  let tvChecks=0, agreementChecks=0, tight=0;
  for(let d=2;d<=5;d++)for(let m=2;m<=5;m++)for(let trial=0;trial<80;trial++){
    const make=()=>{let p=[];while(p.length<m){let a=Array.from({length:d},()=>rng(7)-3);if(!p.some(([x])=>key(x)===key(a)))p.push([a,1])}return p};
    let a=make(),b=make(),L=m*(d-1)+3,B=m*(d-1);
    let tv=tv2(joint(a),joint(b)),sum=0,eq=0;
    // distinct integer moment-curve directions: every d have full rank.
    for(let t=0;t<L;t++){
      let v=Array.from({length:d},(_,i)=>t**i);
      let dist=tv2(project(a,v),project(b,v));sum+=dist;eq+=+(dist===0);
    }
    assert(sum>=(L-B)*tv,"quantitative overlap bound");
    if(tv>0)assert(eq<=B,"agreement bound");
    tvChecks++;agreementChecks++;if(tv>0&&sum===(L-B)*tv)tight++;
  }
  // Exact three-direction switching component for any three nonparallel planar normals.
  const det=(a,b)=>a[0]*b[1]-a[1]*b[0];
  const neg=a=>a.map(x=>-x);
  let hexChecks=0;
  for(let i=0;i<dirs.length;i++)for(let j=i+1;j<dirs.length;j++)for(let k=j+1;k<dirs.length;k++){
    const ns=[dirs[i],dirs[j],dirs[k]], ks=ns.map(([x,y])=>[-y,x]);
    const a=ks.map((p,l)=>p.map(x=>x*det(ks[(l+1)%3],ks[(l+2)%3])));
    assert(a[0].map((x,l)=>x+a[1][l]+a[2][l]).every(x=>x===0),"closed triangle");
    const b=a.map(neg);
    assert(new Set([...a,...b].map(key)).size===6,"six distinct atoms");
    for(const v of ns){
      assert(sig(project(a.map(p=>[p,1]),v))===sig(project(b.map(p=>[p,1]),v)),"hexagon projections");
      hexChecks++;
    }
  }
  // Quantitative tight example: the three vertex spokes and a generic fourth.
  const a=[[1,0],[0,-1],[-1,1]].map(p=>[p,1]),b=a.map(([p,w])=>[neg(p),w]);
  const dist=dirs.slice(0,3).map(v=>tv2(project(a,v),project(b,v)));
  assert(dist.every(x=>x===0),"vertex spokes");
  const extra=[1,4];assert(tv2(project(a,extra),project(b,extra))===6,"generic projection disjoint");
  // Hidden affine term: x,y projections match but x+y differs for this pair.
  const c=[[1,0],[0,1],[-1,-1]].map(p=>[p,1]),e=c.map(([p,w])=>[neg(p),w]);
  assert([dirs[0],dirs[1],dirs[3]].every(v=>sig(project(c,v))===sig(project(e,v))),"curvature-only control");
  assert(sig(project(c,dirs[2]))!==sig(project(e,dirs[2])),"missing row projection");
  return {schema:"mhac-690-census-v1",equal_weight_grid_triples:fixtures.length,three_direction_signature_checks:subsetChecks,three_direction_duplicate_insertions:threeCollisions,four_direction_signature_checks:quadChecks,one_error_one_erasure_dictionary_decodes:decodes,quantitative_tv_checks:tvChecks,agreement_bound_checks:agreementChecks,random_tight_instances:tight,arbitrary_planar_hexagon_projection_checks:hexChecks,sharp_quantitative_example:true,assertion_failures:0,scope:"Finite integer measures and exact projected counts. Not empirical audio or independent review."};
}
module.exports=run;
if(require.main===module)process.stdout.write(JSON.stringify(run(),null,2)+"\n");
