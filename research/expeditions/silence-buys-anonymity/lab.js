'use strict';
// Exact bounded integer test-only laboratory. No packages or real observations.
function assert(x, msg) { if (!x) throw Error(msg); }

function parity(x) { let p=0; while(x){p^=x&1;x>>>=1;}return p; }

function words(G) { return Array.from({length:2**G},(_,i)=>i).filter(x=>parity(x)===0); }

function add(m,k,v){if(v)m.set(k,(m.get(k)||0)+v);}

function l1(a,b){let s=0;for(const k of new Set([...a.keys(),...b.keys()]))s+=Math.abs((a.get(k)||0)-(b.get(k)||0));return s;}

function validate(G,L,c,e,w){if(!Number.isInteger(G)||G<2||G>7||!Number.isInteger(L)||L<1||L>5||2**((G-1)*(L-1))>65536||[c,e,w].some(x=>!Number.isSafeInteger(x)||x<0||x>1000)||c+e+w===0)throw Error("bounded integer fixture required");}

function prefixRows(G,L,g,visit){
  const W=words(G);const by=[W.filter(x=>((x>>g)&1)===0),W.filter(x=>((x>>g)&1)===1)];
  for(let bp=0;bp<2**(L-1);bp++){
    function rec(t,seq,xor){
      if(t===L-1){visit(seq,xor,1^parity(bp));return;}
      for(const x of by[(bp>>t)&1])rec(t+1,[...seq,x],xor^x);
    }
    rec(0,[],0);
  }
}

function build(G,L,c,e,w,g,sourceParity=1){
  validate(G,L,c,e,w);assert(G%2===1,"odd construction");
  const D=c+e+w,all=(1<<G)-1,scale=G*(G-1),M=new Map();let err=0,erased=0,prefixCount=0;
  prefixRows(G,L,g,(seq,xor,lastOdd)=>{
    prefixCount++;const last=sourceParity===1?lastOdd:1^lastOdd;
    assert(((xor>>g)&1)^last===sourceParity,"source parity");
    // C and W only defined for odd source parity; use separate control for even.
    assert(sourceParity===1,"odd source");
    const put=(x,n)=>{assert(parity(x)===0,"illegal word");add(M,[...seq,x].join(","),n);if(((x>>g)&1)!==last)err+=n;};
    if(e){const n=e*scale;add(M,[...seq,"E"].join(","),n);erased+=n;}
    for(let h=0;h<G;h++){
      const x=(all^(1<<h))^xor;
      if(h!==g)put(x,c*G);
      put(x,w*(G-1));
    }
  });
  const den=prefixCount*scale*D;
  assert(prefixCount===2**((G-1)*(L-1)),"prefix count");
  assert([...M.values()].reduce((a,b)=>a+b,0)===den,"mass");
  assert(erased*D===e*den,"erasure budget");
  assert(err*G*D===w*den,"wrong budget");
  return {M,den,err,erased};
}

function control(G,L,sourceParity,g){
  const target=sourceParity?((1<<G)-1):0;assert(parity(target)===0,"control target must be even");const M=new Map();
  prefixRows(G,L,g,(seq,xor,lastOdd)=>{
    const bit=sourceParity?lastOdd:1^lastOdd, x=target^xor;
    assert(parity(x)===0&&((x>>g)&1)===bit,"control utility");add(M,[...seq,x].join(","),1);
  });
  return M;
}

function compositions(n,k){if(k===1)return [[n]];const a=[];for(let i=0;i<=n;i++)for(const t of compositions(n-i,k-1))a.push([i,...t]);return a;}

function test(){
  let mixtures=0,pairComparisons=0,prefixRowsChecked=0,arbitraryTriples=0,controls=0,refusals=0;
  for(const [G,L] of [[3,1],[3,2],[3,3],[3,4],[5,1],[5,2],[5,3],[7,1],[7,2]]){
    for(const [c,e,w] of compositions(6,3)){
      const rows=Array.from({length:G},(_,g)=>build(G,L,c,e,w,g));
      prefixRowsChecked+=G*2**((G-1)*(L-1));mixtures++;
      for(let g=0;g<G;g++)for(let h=g+1;h<G;h++){
        const {den}=rows[g];assert(den===rows[h].den,"den");
        assert(l1(rows[g].M,rows[h].M)*6*(G-1)===2*den*c,"sharp frontier");
        pairComparisons++;
      }
    }
  }
  // Arbitrary unrelated group laws: one-tick source is always 1.
  // Enumerate every rational grid distribution on all five outcomes, no shared policy form.
  const keys=[0,3,5,6,"E"];
  for(let D=1;D<=3;D++){
    const laws=compositions(D,5).map(a=>new Map(keys.map((k,i)=>[k,a[i]])));
    const tv=laws.map(a=>laws.map(b=>l1(a,b)));
    const wrong=Array.from({length:3},(_,g)=>laws.map(a=>keys.filter(k=>k!=="E"&&((k>>g)&1)===0).reduce((s,k)=>s+a.get(k),0)));
    for(let a=0;a<laws.length;a++)for(let b=0;b<laws.length;b++)for(let c=0;c<laws.length;c++){
      const E=laws[a].get("E")+laws[b].get("E")+laws[c].get("E");
      const W=wrong[0][a]+wrong[1][b]+wrong[2][c];
      const V=Math.max(tv[a][b],tv[b][c],tv[a][c]);
      assert(6*V>=2*(3*D-E-3*W),"arbitrary law violates lower bound");
      arbitraryTriples++;
    }
  }
  for(const [G,L,P] of [[2,4,1],[4,3,1],[6,2,1],[3,4,0],[5,3,0]]){
    const rows=Array.from({length:G},(_,g)=>control(G,L,P,g));
    for(let h=1;h<G;h++){assert(l1(rows[0],rows[h])===0,"private negative control");controls++;}
  }
  // Conditioning on delivery alone hides a group-dependent erasure probability.
  const A=new Map([["x",3],["E",1]]),B=new Map([["x",1],["E",3]]);
  assert(l1(A,B)===4,"visible erasure leak");controls++;
  for(const args of [[2,0,1,0,0],[3,2,-1,0,0],[3,1,0,0,0],[9,2,1,0,0],[7,5,1,0,0]]){let rejected=false;try{validate(...args)}catch{rejected=true;}assert(rejected,"malformed accepted");refusals++;}
  return {mixtures,pairComparisons,prefixRowsChecked,arbitraryTriples,controls,refusals};
}
console.log(JSON.stringify(test(),null,2));
