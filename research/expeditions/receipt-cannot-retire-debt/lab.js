"use strict";
// MHAC #362 synthetic exact arithmetic; node lab.js
function laboratory(){
  const check=(x,m)=>{if(!x)throw Error(m)};
  const C={graphs:0,multicolour:0,directGraphEntries:0,frontiers:0,partitions:0,colourNodes:0,streamDecoderChecks:0,deadlineChecks:0};
  const matrix=(n,f)=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i!==j&&f(i,j)));
  function graph(n,mask){let k=0;const a=matrix(n,()=>false);for(let i=0;i<n;i++)for(let j=i+1;j<n;j++,k++)a[i][j]=a[j][i]=Boolean(mask&(1<<k));return a}
  const pent=matrix(5,(i,j)=>[1,4].includes((i-j+5)%5));
  const edge=graph(2,1);
  const product=(a,b)=>matrix(a.length*b.length,(i,j)=>{
    const x=Math.floor(i/b.length),y=i%b.length,u=Math.floor(j/b.length),v=j%b.length;
    return (x===u||a[x][u])&&(y===v||b[y][v]);
  });
  const induced=(a,S)=>S.map(i=>S.map(j=>a[i][j]));
  const independent=a=>a.every(row=>row.every(x=>!x));
  function colourable(a,k){
    const c=Array(a.length).fill(-1);
    function go(left,used){C.colourNodes++;if(!left)return true;
      let best=-1,sat=-1,deg=-1;
      for(let i=0;i<c.length;i++)if(c[i]<0){
        const s=new Set(a[i].flatMap((e,j)=>e&&c[j]>=0?[c[j]]:[])).size,d=a[i].filter(Boolean).length;
        if(s>sat||(s===sat&&d>deg)){best=i;sat=s;deg=d;}
      }
      for(let z=0;z<Math.min(k,used+1);z++){
        if(a[best].some((e,j)=>e&&c[j]===z))continue;
        c[best]=z;if(go(left-1,Math.max(used,z+1)))return true;c[best]=-1;
      }return false;
    }return go(a.length,0);
  }
  function chi(a,cap=a.length){for(let k=1;k<=cap;k++)if(colourable(a,k))return k;return Infinity}
  function* partitions(n,cap){
    const bins=[];
    function* visit(i){if(i===n){yield bins.map(b=>b.slice());return}
      for(let j=0;j<bins.length;j++){bins[j].push(i);yield*visit(i+1);bins[j].pop()}
      if(bins.length<cap){bins.push([i]);yield*visit(i+1);bins.pop()}
    }yield*visit(0);
  }
  // Exact finite policy search: each tag fibre branches independently; no propagation lemma used.
  function optimal(g,caps){
    const memo=new Map();
    function solve(h,t){
      if(t===caps.length)return independent(h)?1:Infinity;
      const key=t+":"+h.map(row=>row.map(Number).join("")).join("/");
      if(memo.has(key))return memo.get(key);
      const a=product(h,g),B=caps[t];
      let best=Infinity;
      if(t===caps.length-1)best=chi(a,B);
      else for(const p of partitions(a.length,B)){
        C.partitions++;
        let sum=0;
        for(const f of p){sum+=solve(induced(a,f),t+1);if(sum>=best)break}
        if(sum<best)best=sum;
      }
      memo.set(key,best);return best;
    }return solve([[false]],0);
  }
  // Separate multicolouring search: assign pairs of colours to original vertices.
  function twofold(g,k){
    const pairs=[];for(let a=0;a<k;a++)for(let b=a+1;b<k;b++)pairs.push([a,b]);
    const chosen=[];
    function go(i){if(i===g.length)return true;
      for(const p of pairs){if(chosen.some((q,j)=>g[i][j]&&p.some(x=>q.includes(x))))continue;
        chosen.push(p);if(go(i+1))return true;chosen.pop();
      }return false;
    }return go(0);
  }
  function actions(g){
    const a=[Array.from({length:g.length},(_,i)=>i)];
    for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++)if(g[i][j]){
      const m=a[0].slice();m[j]=i;a.push(m);
    }return a;
  }
  function words(n,k){let w=[[]];for(let i=0;i<k;i++)w=w.flatMap(p=>Array.from({length:n},(_,j)=>[...p,j]));return w}
  function direct(g,n){
    const a=actions(g),W=words(g.length,n);
    let p=[[false]];for(let i=0;i<n;i++)p=product(p,g);
    for(let i=0;i<W.length;i++)for(let j=0;j<W.length;j++){
      const same=i!==j&&W[i].every((x,k)=>a.some(m=>m[x]===m[W[j][k]]));
      check(same===p[i][j],"direct graph");C.directGraphEntries++;
    }
  }
  for(let n=1;n<=5;n++)for(let m=0;m<2**(n*(n-1)/2);m++){
    const g=graph(n,m),c=chi(g),d=chi(product(edge,g));
    C.graphs++;check(d>=c+1&&d<=2*c,"twofold bounds");
    // Test both sides of exact multicolour threshold independently.
    check(twofold(g,d)&&!twofold(g,d-1),"twofold equivalence");C.multicolour+=2;
    if(n<=3){
      direct(g,3);
      for(let h=1;h<=3;h++)for(let b=1;b<=Math.min(3,d-1);b++){
        check(optimal(g,Array(h).fill(b))===(b<c?Infinity:c**h),"closed frontier");C.frontiers++;
      }
    }
  }
  check(chi(pent)===3&&chi(product(edge,pent))===5&&chi(product(pent,pent))===5,"pentagon");
  direct(pent,2);
  for(let a=1;a<=5;a++)for(let b=1;b<=6;b++){
    check(optimal(pent,[a,b])===(b>=5?5:b>=3&&a>=3?9:Infinity),"two-slot pentagon");C.frontiers++;
  }
  // Direct decoder fibres, no graph formula: 4 origins, 1 flush, all actual action vectors.
  const W=words(5,4),A=actions(pent),V=words(A.length,4);
  function stream(w){
    const q=(x,y)=>(x+2*y)%5, u=q(w[0],w[1]),v=q(w[2],w[3]);
    return [0,Math.floor(u/3),u%3,Math.floor(v/3),v%3];
  }
  check(new Set(W.map(w=>stream(w).join(""))).size===25,"flush transcript count");
  // At each deadline enumerate only available tag and intervention observations.
  for(const [tick,target] of [[3,2],[5,4]]){
    const seen=new Map(),prefixCount=Math.min(tick,4);
    for(const w of words(5,prefixCount)){
      const pad=[...w,...Array(4-w.length).fill(0)],tag=stream(pad).slice(0,tick);
      for(const a of words(A.length,prefixCount)){
        const key=tag.join("")+"|"+a.join("")+"|"+w.map((x,i)=>A[a[i]][x]).join("");
        const out=w.slice(0,target).join("");
        check(!seen.has(key)||seen.get(key)===out,"deadline decoder conflict");
        seen.set(key,out);C.streamDecoderChecks++;
      }
      // Earlier emitted symbols must be invariant to every unseen suffix.
      for(const suffix of words(5,4-prefixCount)){
        check(stream([...w,...suffix]).slice(0,tick).join("")===tag.join(""),"preview");C.deadlineChecks++;
      }
    }
  }
  // Changed support x2=x1: one constant then scalar colour is valid with no flush.
  const scalar=[0,1,0,1,2],seen=new Map();
  for(let x=0;x<5;x++)for(const a of words(A.length,2)){
    const key=scalar[x]+"|"+a.join("")+"|"+a.map(j=>A[j][x]).join("");
    check(!seen.has(key)||seen.get(key)===x,"diagonal support");seen.set(key,x);
  }
  return C;
}
console.log(JSON.stringify(laboratory(), null, 2));
