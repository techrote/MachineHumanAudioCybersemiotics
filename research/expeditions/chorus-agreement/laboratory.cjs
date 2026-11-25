function laboratory(){
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const pop=x=>{let c=0;while(x){x&=x-1;c++}return c};
  const maps=n=>Array.from({length:n**n},(_,i)=>Array.from({length:n},(_,j)=>Math.floor(i/n**j)%n));
  const cerny=n=>[Array.from({length:n},(_,i)=>(i+1)%n),Array.from({length:n},(_,i)=>i===n-1?0:i)];
  function model(A){
    const n=A[0].length, full=(1<<n)-1, pairs=[];
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)pairs.push([i,j]);
    const pf=(1<<pairs.length)-1;
    const index=new Map(pairs.map((p,i)=>[p.join(","),i]));
    const sm=A.map(f=>Array.from({length:1<<n},(_,s)=>f.reduce((m,x,i)=>m|((s>>i&1)<<x),0)));
    const pm=A.map(f=>pairs.map(([i,j])=>f[i]===f[j]?0:1<<index.get([f[i],f[j]].sort((a,b)=>a-b).join(","))));
    const pmap=(a,s)=>{let t=0;while(s){let b=s&-s;t|=pm[a][31-Math.clz32(b)];s^=b}return t};
    return {A,n,full,pf,sm,pmap};
  }
  function step(M,S,a,kind){
    if(kind==="pair")return S.map((s,j)=>M.pmap(a,s)|(j?S[j-1]:0));
    if(kind==="delete")return S.map((s,j)=>M.sm[a][s]|(j?S[j-1]:0));
    const T=[];
    for(let j=0;j<S.length;j++){
      let t=M.sm[a][S[j]];
      if(j){
        t|=S[j-1];
        for(let b=0;b<M.A.length;b++)t|=M.sm[b][S[j-1]]|M.sm[b][T[j-1]];
      }
      T.push(t);
    }
    return T;
  }
  function run(M,w,d,kind){
    let S=Array(d+1).fill(kind==="pair"?M.pf:M.full);
    for(const a of w)S=step(M,S,Number(a),kind);
    return S[d];
  }
  function bfs(M,d,kind,cap=500000){
    const start=Array(d+1).fill(kind==="pair"?M.pf:M.full), k=s=>s.join(",");
    const queue=[[start,""]],seen=new Set([k(start)]);
    for(let i=0;i<queue.length;i++){
      const [S,w]=queue[i],s=S[d];
      if(kind==="pair"?s===0:pop(s)===1)return {word:w,length:w.length,visited:seen.size};
      for(let a=0;a<M.A.length;a++){let T=step(M,S,a,kind),key=k(T);if(!seen.has(key)){seen.add(key);queue.push([T,w+a]);if(seen.size>cap)return {capped:true,visited:seen.size}}}
    }
    return {impossible:true,visited:seen.size};
  }
  function variants(w,d,allEdits){
    let seen=new Set([w]),front=[w];
    for(let j=0;j<d;j++){
      const next=[];
      const add=s=>{if(!seen.has(s)){seen.add(s);next.push(s)}};
      for(const s of front){
        for(let i=0;i<s.length;i++){add(s.slice(0,i)+s.slice(i+1));if(allEdits)add(s.slice(0,i)+(s[i]==="0"?"1":"0")+s.slice(i+1))}
        if(allEdits)for(let i=0;i<=s.length;i++)for(const a of ["0","1"])add(s.slice(0,i)+a+s.slice(i));
      }front=next;
    }return seen;
  }
  function image(M,w){let s=M.full;for(const a of w)s=M.sm[Number(a)][s];return s}
  function direct(M,V){let union=0,weak=true;for(let w of V){const s=image(M,w);union|=s;weak&&=pop(s)===1}return {union,weak}}
  const words=max=>Array.from({length:2**(max+1)-1},(_,i)=>(i+1).toString(2).slice(1));
  function sink(M){
    const reach=M.A[0].map((_,i)=>{let s=1<<i,t;do{t=s;for(const sm of M.sm)s|=sm[s]}while(s!==t);return s});
    return reach.reduce((s,t)=>s&t,M.full);
  }
  const receipt={model:"synthetic complete deterministic binary automata",census:[],cerny:[],directDeletionChecks:0,directEditChecks:0,highBudgetChecks:0,threeStateWordChecks:0};
  const D=words(5).map(w=>[w,variants(w,0,false),variants(w,1,false),variants(w,2,false)]);
  const E=words(3).map(w=>[w,variants(w,1,true)]);
  for(let n=2;n<=3;n++){
    const row={n,automata:0,synchronizing:0,absorbing:0,strongEditOne:0,ordinaryNoStrongEditOne:0};
    for(const a of maps(n))for(const b of maps(n)){
      const M=model([a,b]);row.automata++;
      for(const [w,...vv] of D)for(let d=0;d<=2;d++){
        let v=direct(M,vv[d]);
        assert((run(M,w,d,"pair")===0)===v.weak,"pair direct");
        assert(run(M,w,d,"delete")===v.union,"delete direct");
        receipt.directDeletionChecks++;
      }
      for(const [w,V] of E){assert(run(M,w,1,"edit")===direct(M,V).union,"edit direct");receipt.directEditChecks++}
      const ord=bfs(M,0,"pair"),strong=bfs(M,1,"edit");
      assert(!ord.capped&&!strong.capped,"small census capped");
      const absorbing=a.some((x,i)=>x===i&&b[i]===i);
      if(ord.word!==undefined){
        row.synchronizing++;if(absorbing)row.absorbing++;
        assert((strong.word!==undefined)===absorbing,"absorbing criterion");
        if(strong.word!==undefined)row.strongEditOne++;else row.ordinaryNoStrongEditOne++;
        const C=sink(M);assert(C!==0,"sink");
        const z=31-Math.clz32(C&-C);
        const start=image(M,ord.word),Q=[[start,""]],seen=new Set([start]);let suffix;
        for(let i=0;i<Q.length;i++){let [s,w]=Q[i];if(s===(1<<z)){suffix=w;break}for(let c=0;c<2;c++){let t=M.sm[c][s];if(!seen.has(t)){seen.add(t);Q.push([t,w+c])}}}
        assert(suffix!==undefined,"sink target");
        const d=n-1,w=(ord.word+suffix).repeat(d+1);
        assert(run(M,w,d,"edit")===C,"sink equality");receipt.highBudgetChecks++;
      }else assert(strong.impossible,"no ordinary but robust");
    }
    receipt.census.push(row);
  }
  // Explicit gap-chain deletion witness for every binary word through length 15.
  function eraseBadGaps(w){
    const b=[];for(let i=0;i<w.length;i++)if(w[i]==="1")b.push(i);
    const bad=b.slice(1).map((v,i)=>(v-b[i]-1)%3===2),del=new Set();
    for(let i=0;i<bad.length;){
      if(!bad[i]){i++;continue}
      let j=i;while(j<bad.length&&bad[j])j++;
      for(let k=i;k+1<j;k+=2)del.add(b[k+1]);
      if((j-i)%2)del.add(b[j-1]+1);
      i=j;
    }
    return {count:del.size,word:[...w].filter((_,i)=>!del.has(i)).join("")};
  }
  const M3=model(cerny(3));
  for(const w of words(15)){
    const z=eraseBadGaps(w);
    assert(z.count<=Math.floor(w.length/4),"gap count");
    assert(pop(image(M3,z.word))>1,"gap witness not nonreset");
    receipt.threeStateWordChecks++;
  }
  for(let n=2;n<=6;n++){
    const M=model(cerny(n));
    const max=n===3?6:n===4?3:n===5?2:n===6?1:3;
    for(let d=0;d<=max;d++){
      const weak=bfs(M,d,"pair"),strong=bfs(M,d,"delete");
      assert(!weak.capped&&!strong.capped,"Cerny census cap");
      if(n===3)assert(weak.length===4*(d+1),"C3 sharp");
      if(n>=3&&d>=2)assert(strong.impossible,"Cerny no strong");
      if(weak.word!==undefined)assert(run(M,weak.word,d,"pair")===0,"weak witness");
      receipt.cerny.push({n,d,weak,strong,weakUnion:pop(run(M,weak.word,d,"delete"))});
    }
  }
  return receipt;
}
console.log(JSON.stringify(laboratory(), null, 2));
