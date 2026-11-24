"use strict";
function lab(){
  "use strict";
  const count={frontierWitnesses:0,contextDecoders:0,decoderCells:0,deterministicPolicies:0,mixedPolicies:0,rigidityChannels:0,rigidityOptimal:0,negativeControls:0};
  function check(ok,msg){if(!ok)throw Error(msg);}
  function add(m,k,v){m.set(k,(m.get(k)||0)+v);}
  function model(d){
    check(Number.isInteger(d)&&d>=1&&d<=8,"bad dimension");
    const n=2**d,N=n+2, a=n,b=n+1;
    const bits=Array.from({length:N},(_,x)=>x===a?"0".repeat(d+2):x===b?"1".repeat(d+2):x.toString(2).padStart(d,"0")+"01");
    const edges=Array.from({length:d+2},(_,i)=>[[a,b],...Array.from({length:n},(_,x)=>[x,bits[x][i]==="0"?b:a])]);
    return {d,n,N,a,b,bits,edges};
  }
  function masks(d,r){return Array.from({length:2**d},(_,m)=>m).filter(m=>m.toString(2).replace(/0/g,"").length===r);}
  function tuple(bits,m,d){return [...bits].map((c,i)=>i<d&&(m&(1<<i))?"?":c).join("|");}
  function witness(M,r,t){ // t/2 mixture with next erasure count, t=0 or 1
    const A=masks(M.d,r),B=t?masks(M.d,r+1):[0],D=2*A.length*B.length;
    const rows=M.bits.map((bits,x)=>{
      const row=new Map();
      if(x>=M.n)add(row,tuple(bits,0,M.d),D);
      else {
        for(const m of A)add(row,tuple(bits,m,M.d),(2-t)*B.length);
        if(t)for(const m of B)add(row,tuple(bits,m,M.d),t*A.length);
      }
      return row;
    });
    return {rows,D};
  }
  function sumMax(rows){
    const maxima=new Map();
    for(const row of rows)for(const [key,v] of row)maxima.set(key,Math.max(v,maxima.get(key)||0));
    return [...maxima.values()].reduce((a,b)=>a+b,0);
  }
  function verify(M,rows,D){
    check(rows.length===M.N,"row count");
    for(const row of rows)check([...row.values()].every(v=>Number.isSafeInteger(v)&&v>0)&&[...row.values()].reduce((a,b)=>a+b,0)===D,"row mass");
    const marg=M.edges.map((_,i)=>rows.map(row=>{
      const out=new Map();for(const [key,v] of row)add(out,key.split("|")[i],v);return out;
    }));
    for(let i=0;i<M.edges.length;i++){
      for(const [u,v] of M.edges[i]){
        // Direct recovery from actual collapsed-state observation, not just graph support.
        const obs=new Map();
        for(let x=0;x<M.N;x++)for(const [tag,w] of marg[i][x]){
          const key=JSON.stringify([x===v?u:x,tag]);
          check(!obs.has(key)||obs.get(key)===x,"ambiguous decoder");obs.set(key,x);count.decoderCells++;
        }
        count.contextDecoders++;
      }
    }
    const local=marg.map(sumMax),joint=sumMax(rows);
    check(local.every(m=>m>=2*D),"local lower bound");
    const S=Math.min(D,Math.max(...local.slice(0,M.d))-2*D),r=Math.floor(M.d*S/D),rem=M.d*S-r*D;
    const lower=r===M.d?3*D:2*D+2**(M.d-r)*(D-rem)+2**(M.d-r-1)*rem;
    check(joint>=lower,"joint lower bound");
    return {local,joint,lower};
  }
  for(let d=1;d<=5;d++){
    const M=model(d);
    for(let r=0;r<=d;r++)for(const t of (r===d?[0]:[0,1])){
      const {rows,D}=witness(M,r,t),v=verify(M,rows,D);
      check(v.local.slice(0,d).every(x=>2*d*(x-2*D)===D*(2*r+t)),"exact local budget");
      check(v.local.slice(d).every(x=>x===2*D),"sentinel optimal");
      const expected=2*D+(2-t)*D*2**(d-r)/2+(t?D*2**(d-r-1)/2:0);
      check(v.joint===expected&&v.joint===v.lower,"sharp witness");
      count.frontierWitnesses++;
    }
  }
  const M=model(2);
  for(let code=0;code<4**M.n;code++){
    const rows=M.bits.map((b,x)=>new Map([[tuple(b,x<M.n?(code>>(2*x))&3:0,2),1]]));
    verify(M,rows,1);count.deterministicPolicies++;
  }
  let seed=1729;
  function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;}
  for(let j=0;j<240;j++){
    const d=2+j%3,M=model(d),D=7;
    // Source-dependent erasure and extra suffix labels; anchors use only bits.
    const rows=M.bits.map((b,x)=>{
      const row=new Map();for(let k=0;k<D;k++){
        const m=x<M.n?rand(2**d):0;
        const key=tuple(b,m,d).split("|").map((c,i)=>x<M.n&&i<d&&rand(5)===0?c+"extra"+rand(3):c).join("|");
        add(row,key,1);
      }return row;
    });
    verify(M,rows,D);count.mixedPolicies++;
  }
  // Exhaustive independent small-channel rigidity test on a four-state path.
  const triples=[];for(let a=0;a<=2;a++)for(let b=0;b<=2-a;b++)triples.push([a,b,2-a-b]);
  for(const a of triples)for(const b of triples)for(const c of triples)for(const d of triples){
    const rows=[a,b,c,d];if([0,1,2].some(i=>[0,1,2].some(j=>rows[i][j]&&rows[i+1][j])))continue;
    count.rigidityChannels++;
    const s=[0,1,2].reduce((z,j)=>z+Math.max(...rows.map(r=>r[j])),0);
    check(s>=4,"rigidity lower bound");
    if(s===4){
      for(let j=0;j<3;j++)check(a[j]===c[j]&&b[j]===d[j]&&!(a[j]&&b[j]),"rigidity equality");
      count.rigidityOptimal++;
    }
  }
  // Fixed-context replay versus a changing-context complete transcript.
  const C=model(3),{rows,D}=witness(C,0,0),res=verify(C,rows,D);
  check(res.local[0]===2*D&&res.joint===C.N*D,"local-optimal complete disclosure");count.negativeControls++;
  const repeated=rows.map(row=>new Map([...row].map(([key,w])=>[key.split("|")[0].repeat(8),w])));
  check(sumMax(repeated)===2*D,"fixed receipt replay");count.negativeControls++;
  const common=witness(C,3,0);check(verify(C,common.rows,common.D).joint===3*common.D,"common receipt lower bound");count.negativeControls++;
  let rejected=false;try{model(0);}catch(e){rejected=true;}check(rejected,"invalid input");count.negativeControls++;
  return count;
}
console.log(JSON.stringify(lab(), null, 2));
