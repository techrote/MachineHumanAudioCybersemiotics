"use strict";
// Synthetic exact finite checks, no participants or acoustic data.
function main(){
  const assert=(b,msg)=>{if(!b)throw Error(msg)};
  const pop=x=>{let c=0;while(x){x&=x-1;c++}return c};
  const xor=(a)=>a.reduce((x,y)=>x^y,0);
  const syn=(H,x)=>xor(H.filter((_,i)=>x>>i&1));
  const span=(H)=>{let s=new Set([0]);for(const h of H)for(const x of [...s])s.add(x^h);return s};
  const inc=(m,k,v=1)=>m.set(k,(m.get(k)||0)+v);
  const tv2=(a,b)=>[...new Set([...a.keys(),...b.keys()])].reduce((s,k)=>s+Math.abs((a.get(k)||0)-(b.get(k)||0)),0);
  let matrices=0,masks=0,lawFamilies=0,hintChecks=0,transcriptPairs=0,transcriptDraws=0,policies=0;
  const projections=new Map();
  for(let n=1;n<=4;n++)for(let code=0;code<4**n;code++){
    const H=Array.from({length:n},(_,i)=>code>>(2*i)&3);
    const words=Array.from({length:1<<n},(_,i)=>i);
    const bs=[...span(H)].sort((a,b)=>a-b);
    matrices++;
    for(let E=0;E<1<<n;E++){
      masks++;
      const K=((1<<n)-1)^E,S=span(H.filter((_,i)=>E>>i&1));
      const f=(1<<pop(E))/S.size;
      const cl=b=>Math.min(...[...S].map(s=>s^b));
      for(const b of bs){
        const P=[...new Set(words.filter(x=>syn(H,x)===b).map(x=>x&K))].sort((a,b)=>a-b);
        assert(P.includes(0)===S.has(b),"projection zero");
        if(P.length<=4)projections.set(P.join(","),P);
      }
      for(let M=1;M<1<<bs.length;M++){
        const B=bs.filter((_,i)=>M>>i&1);
        const X=words.filter(x=>B.includes(syn(H,x)));
        const buckets=new Map(),groups=new Map();
        for(const x of X)inc(buckets,x&K);
        for(const b of B)inc(groups,cl(b));
        lawFamilies++;
        assert(buckets.size*f*B.length===X.length*groups.size,"success formula");
        for(const [y,c] of buckets){
          const observed=new Set(X.filter(x=>(x&K)===y).map(x=>syn(H,x)));
          assert(c===f*observed.size,"fiber law count");
          assert([...observed].every(b=>cl(b)===cl([...observed][0])),"quotient equality");
          assert(observed.size===groups.get(cl([...observed][0])),"quotient completeness");
        }
        // A hint assigns labels independently inside each quotient class.
        const next=new Map(),hint=new Map();
        for(const b of B){const k=cl(b),l=next.get(k)||0;next.set(k,l+1);hint.set(b,l)}
        const hintBuckets=new Map();
        for(const x of X)inc(hintBuckets,`${x&K}/${hint.get(syn(H,x))}`);
        assert([...hintBuckets.values()].every(v=>v===f),"hint construction");
        assert(new Set(hint.values()).size===Math.max(...groups.values()),"hint alphabet");
        hintChecks++;
        if(S.size===(1<<pop(E))&&B.every(b=>S.has(b)))assert(buckets.size*B.length===X.length,"private blind success");
      }
    }
  }
  // Enumerate actual complete row-transcript laws for projected affine cosets.
  for(const P of projections.values())for(const G of [3,5]){
    const laws=[],inside=P.includes(0);
    for(let g=0;g<G;g++){
      const law=new Map();
      const partners=Array.from({length:G},(_,i)=>i).filter(i=>i!==g);
      const deps=inside?partners.slice(0,1):partners;
      for(const dep of deps){
        const rows=new Array(G).fill(0);
        const independent=Array.from({length:G},(_,i)=>i).filter(i=>i!==dep);
        function rec(i){
          if(i===independent.length){rows[dep]=xor(independent.map(j=>rows[j]));inc(law,rows.join(","));transcriptDraws++;return}
          for(const p of P){rows[independent[i]]=p;rec(i+1)}
        }
        rec(0);
      }
      const total=[...law.values()].reduce((a,b)=>a+b,0);
      for(const [k,c] of law){
        const rows=k.split(",").map(Number);
        assert(P.includes(rows[g])&&xor(rows)===0,"exact row and parity");
      }
      for(const p of P)assert([...law].filter(([k])=>+k.split(",")[g]===p).reduce((s,[,c])=>s+c,0)*P.length===total,"actual uniform");
      laws.push({law,total});
    }
    for(let g=0;g<G;g++)for(let h=g+1;h<G;h++){
      const {law:a,total:t}=laws[g],{law:b,total:u}=laws[h];
      assert(t===u,"equal denominators");
      assert(tv2(a,b)*(inside?1:G-1)===(inside?0:2*t),"sharp conditional TV");
      transcriptPairs++;
    }
  }
  // All policies on the G=3 one-bit even alphabet at quarter probability steps.
  const D=4,alphabet=[0,3,5,6];
  const worst=(laws)=>Math.max(...[0,1,2].flatMap(g=>Array.from({length:g},(_,h)=>tv2(laws[g],laws[h]))));
  let minConditional=Infinity,minPooled=Infinity,minConditionalAtPerfectPool=Infinity,minPoolAtOptimalConditional=Infinity;
  const policy=(params)=>{
    const c=[0,1].map(b=>[0,1,2].map(g=>{
      const allowed=alphabet.filter(w=>(w>>g&1)===b);
      const p=params[b*3+g];return new Map([[allowed[0],p],[allowed[1],D-p]])
    }));
    const mix=[0,1,2].map(g=>new Map(alphabet.map(w=>[w,(c[0][g].get(w)||0)+(c[1][g].get(w)||0)])));
    const C=Math.max(...[0,1,2].flatMap(g=>Array.from({length:g},(_,h)=>tv2(c[0][g],c[0][h])+tv2(c[1][g],c[1][h]))));
    const P=worst(mix); // C,P use same denominator 4D.
    return [C,P]
  };
  for(let i=0;i<(D+1)**6;i++){
    let z=i;const p=Array.from({length:6},()=>{const a=z%(D+1);z=Math.floor(z/(D+1));return a});
    const [C,P]=policy(p);policies++;
    assert(C>=D&&C+P>=2*D,"conditional/pooled frontier");
    minConditional=Math.min(minConditional,C);
    minPooled=Math.min(minPooled,P);
    if(P===0)minConditionalAtPerfectPool=Math.min(minConditionalAtPerfectPool,C);
    if(C===D)minPoolAtOptimalConditional=Math.min(minPoolAtOptimalConditional,P);
  }
  assert(minConditional===D&&minPooled===0&&minConditionalAtPerfectPool===2*D&&minPoolAtOptimalConditional===D,"sharp endpoints");
  return {matrices,masks,lawFamilies,hintChecks,projectionCosets:projections.size,transcriptPairs,transcriptDraws,policies,minConditional:minConditional/(4*D),minConditionalAtPerfectPool:minConditionalAtPerfectPool/(4*D),minPoolAtOptimalConditional:minPoolAtOptimalConditional/(4*D)};
}
console.log(JSON.stringify(main(), null, 2));
