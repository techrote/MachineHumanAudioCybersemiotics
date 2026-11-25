function laboratory() {
  "use strict";
  // Synthetic graph of binary-valued voices; an edge is violated iff endpoints differ.
  const pop = x => { let n=0; for(;x;x&=x-1)n++;return n; };
  const edges = n => Array.from({length:n},(_,i)=>Array.from({length:n-i-1},(_,j)=>[i,i+j+1])).flat();
  const cut = (es,x) => es.reduce((m,[a,b],i)=>m|((((x>>a)^(x>>b))&1)<<i),0);
  // Independent parity propagation; edges marked 1 require opposite labels.
  const solve = (n,es,y) => {
    const x=Array(n).fill(-1);let c=0;
    for(let v=0;v<n;v++)if(x[v]<0){
      c++;x[v]=0;const q=[v];
      for(let h=0;h<q.length;h++)for(let i=0;i<es.length;i++){
        const [a,b]=es[i],u=q[h],w=a===u?b:b===u?a:-1;
        if(w<0)continue;const z=x[u]^((y>>i)&1);
        if(x[w]<0){x[w]=z;q.push(w);}else if(x[w]!==z)return null;
      }
    }
    return {components:c,assignment:x.reduce((m,v,i)=>m|(v<<i),0)};
  };
  // Independent connectivity after deleting specified edges.
  const reach=(es,deleted,a,b)=>{
    let seen=1<<a,old;
    do{old=seen;es.forEach(([u,v],i)=>{if(!(deleted&(1<<i))&&(seen&((1<<u)|(1<<v))))seen|=(1<<u)|(1<<v);});}while(old!==seen);
    return Boolean(seen&(1<<b));
  };
  let assertions=0, graphs=0, patterns=0, targets=0, bridges=0;
  const check=(v,msg)=>{assertions++;if(!v)throw Error(msg);};
  const histogram={};
  for(let n=1;n<=5;n++){
    const universe=edges(n);
    for(let g=0;g<1<<universe.length;g++){
      graphs++;const es=universe.filter((_,i)=>g&(1<<i)),m=es.length;
      const cuts=new Map();
      for(let x=0;x<1<<n;x++){const y=cut(es,x);cuts.set(y,(cuts.get(y)||0)+1);}
      const c=solve(n,es,0).components;
      check(cuts.size===2**(n-c),"cut dimension");
      for(const count of cuts.values())check(count===2**c,"fiber size");
      let allSingle=true;
      for(let y=0;y<1<<m;y++){
        patterns++;const s=solve(n,es,y);
        check(Boolean(s)===cuts.has(y),"parity versus cut enumeration");
        if(s)check(cut(es,s.assignment)===y,"propagated witness");
      }
      for(let i=0;i<m;i++){
        targets++;const [a,b]=es[i],bit=1<<i;
        const minCut=Math.min(...[...cuts.keys()].filter(y=>y&bit).map(pop));
        const isBridge=!reach(es,bit,a,b);
        if(isBridge)bridges++;else allSingle=false;
        check((minCut===1)===isBridge,"single exception iff bridge");
        let minDelete=m+1;
        for(let d=1;d<1<<m;d++)if((d&bit)&&pop(d)<minDelete&&!reach(es,d,a,b))minDelete=pop(d);
        check(minCut===minDelete,"cut versus deletion optimum");
        histogram[minCut]=(histogram[minCut]||0)+1;
      }
      check(allSingle===(m===n-c),"all independent iff forest");
      // Construct spanning forest without changing legal zero-violation assignments.
      const forest=[];
      for(const [a,b] of es)if(!reach(forest,0,a,b))forest.push([a,b]);
      check(forest.length===n-c,"forest size");
      for(let x=0;x<1<<n;x++)check((cut(es,x)===0)===(cut(forest,x)===0),"same conforming assignments");
    }
  }
  const examples=[
    [[0,1],[1,2],[2,3]],
    [[0,1],[1,2],[2,3],[3,0]],
    edges(4)
  ].map(es=>{const vals=Array.from({length:16},(_,x)=>cut(es,x));return {edges:es,conforming:vals.filter(v=>v===0).length,minAB:Math.min(...vals.filter(v=>v&1).map(pop)),witness:cut(es,14)};});
  check(examples.map(e=>e.minAB).join()==="1,2,3","path/cycle/clique controls");
  check(examples.every(e=>e.conforming===2),"same legal repertoire");
  check(solve(3,[[0,1],[1,2],[0,2]],1)===null,"impossible isolated cycle violation");
  const result={graphs,patterns,targets,bridges,histogram,assertions,examples};
  return result;
}
console.log(JSON.stringify(laboratory(), null, 2));
