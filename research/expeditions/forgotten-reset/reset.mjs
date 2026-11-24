// MHAC #232: exact silent-deletion robust reset lab. Node.js, no dependencies.
// State maps are arrays of integer destinations, command words arrays of map indices.
function validate(maps,k){
  if(!Array.isArray(maps)||!maps.length||!Array.isArray(maps[0]))throw Error("empty alphabet");
  const n=maps[0].length;
  if(n<1||n>12||!Number.isInteger(k)||k<0||k>2)throw Error("supported n=1..12, k=0..2");
  for(const f of maps)if(f.length!==n||f.some(x=>!Number.isInteger(x)||x<0||x>=n))throw Error("invalid map");
  return n;
}
function table(f){
  const t=new Int32Array(1<<f.length);
  for(let m=1;m<t.length;m++){const b=m&-m,i=31-Math.clz32(b);t[m]=t[m^b]|(1<<f[i]);}
  return t;
}
function singleton(m){return m!==0&&(m&(m-1))===0;}
function step(s,t){return s.map((m,j)=>t[m]|(j?s[j-1]:0));}
function trace(maps,word,k){
  const n=validate(maps,k),ts=maps.map(table);let s=Array(k+1).fill((1<<n)-1);
  const out=[s];
  for(const a of word){if(!ts[a])throw Error("invalid command");s=step(s,ts[a]);out.push(s);}
  return out;
}
function solve(maps,k,{certificate=false,maxVisited=2000000}={}){
  const n=validate(maps,k),ts=maps.map(table),s=Array(k+1).fill((1<<n)-1);
  const key=x=>x.join(","),q=[s],seen=new Map([[key(s),null]]);
  for(let i=0;i<q.length;i++){
    const x=q[i],id=key(x);
    if(singleton(x[k])){
      const word=[];let at=id;
      while(seen.get(at)!==null){const [p,a]=seen.get(at);word.push(a);at=p;}
      return {status:"found",word:word.reverse(),target:31-Math.clz32(x[k]),visited:q.length};
    }
    for(let a=0;a<ts.length;a++){
      const y=step(x,ts[a]),yk=key(y);
      if(!seen.has(yk)){
        if(q.length>=maxVisited)return {status:"budget",visited:q.length};
        seen.set(yk,[id,a]);q.push(y);
      }
    }
  }
  return {status:"impossible",visited:q.length,...(certificate?{closure:q}:{})};
}
function verifyClosure(maps,k,closure){
  const n=validate(maps,k),ts=maps.map(table),keys=new Set(closure.map(x=>x.join(",")));
  return keys.has(Array(k+1).fill((1<<n)-1).join(",")) &&
    closure.every(s=>s.length===k+1&&s.every((m,j)=>Number.isInteger(m)&&m>0&&m<(1<<n)&&(!j||(m&s[j-1])===s[j-1]))&&!singleton(s[k])&&ts.every(t=>keys.has(step(s,t).join(","))));
}
// Independent witness evaluator: explicitly branch on each deletion decision, no subset recurrence.
function direct(maps,word,k){
  const n=validate(maps,k);const out=new Set();
  function walk(i,state,left){
    if(i===word.length){out.add(state);return;}
    walk(i+1,maps[word[i]][state],left);
    if(left)walk(i+1,state,left-1);
  }
  for(let i=0;i<n;i++)walk(0,i,k);
  return [...out].sort((a,b)=>a-b);
}
function cerny(n){return [Array.from({length:n},(_,i)=>(i+1)%n),Array.from({length:n},(_,i)=>i===n-1?0:i)];}
function construction(n){
  if(n===2)return [1,1];
  const a=m=>Array(m).fill(0);
  return [1,...a(n-1),1,...Array.from({length:n-3},()=>[0,1,...a(n-2),1]).flat(),0,1,...a(n-1),1];
}
function transformations(n){
  return Array.from({length:n**n},(_,j)=>Array.from({length:n},()=>{const a=j%n;j=Math.floor(j/n);return a;}));
}
function census(n){
  const fs=transformations(n),hist={},examples={};let ordinary=0,robust=0,impossible=0,checked=0;
  for(const a of fs)for(const b of fs){
    const maps=[a,b],s=solve(maps,0);
    if(s.status==="impossible")continue;
    if(s.status!=="found")throw Error("ordinary budget");
    ordinary++;
    const r=solve(maps,1,{certificate:true});
    if(r.status==="found"){
      robust++;const targets=direct(maps,r.word,1);
      if(targets.length!==1||targets[0]!==r.target)throw Error("direct witness mismatch");
    }else if(r.status==="impossible"){
      impossible++;if(!verifyClosure(maps,1,r.closure))throw Error("invalid closure");
    }else throw Error("robust budget");
    checked++;
    const h=s.word.length+":"+(r.status==="found"?r.word.length:"impossible");
    hist[h]=(hist[h]||0)+1;
    if(!examples[h])examples[h]={maps,ordinary:s.word,robust:r.word??null};
  }
  return {n,total:fs.length**2,ordinary,robust,impossible,checked,hist,examples};
}
function run(){
  const check=(x,msg)=>{if(!x)throw Error(msg);};
  // Exhaustive independent direct deletion evaluation for all two-state maps,
  // all words of lengths 0..5 and budgets 0..2.
  let traceChecks=0;
  for(const a of transformations(2))for(const b of transformations(2))for(let len=0;len<=5;len++)for(let w=0;w<2**len;w++)for(let k=0;k<=2;k++){
    const word=Array.from({length:len},(_,i)=>(w>>i)&1),maps=[a,b];
    const t=trace(maps,word,k).at(-1)[k],d=direct(maps,word,k);
    check(t===d.reduce((s,v)=>s|(1<<v),0),"trace mismatch");traceChecks++;
  }
  const family=[];
  for(let n=2;n<=10;n++){
    const maps=cerny(n),row={n,budgets:[]};
    for(let k=0;k<=2;k++){
      const r=solve(maps,k,{certificate:true});
      check(r.status!=="budget","unexpected budget");
      if(r.status==="found")check(direct(maps,r.word,k).length===1,"family replay");
      else check(verifyClosure(maps,k,r.closure),"family closure");
      row.budgets.push({k,status:r.status,length:r.word?.length??null,word:r.word?.map(i=>"ab"[i]).join("")??null,target:r.target??null,visited:r.visited});
    }
    const w=construction(n);check(direct(maps,w,1).length===1,"construction");if(n>=3)check(w.length===n*n,"construction length");
    family.push(row);
  }
  // Large constructions checked without exponential subset tables or recursion:
  let large=0;
  for(let n=3;n<=64;n++){
    const w=construction(n),maps=cerny(n);
    let x=new Set(Array.from({length:n},(_,i)=>i)),y=new Set(x);
    for(const a of w){const f=maps[a],old=x;x=new Set([...x].map(i=>f[i]));y=new Set([...y].map(i=>f[i]).concat([...old]));}
    check(x.size===1&&y.size===1&&y.has(0)&&w.length===n*n,"large construction");large++;
  }
  const counts=[2,3,4].map(census);
  check(counts[0].ordinary===12&&counts[0].impossible===0,"2 state census");
  return {schema:"mhac-deletion-reset-v1",traceChecks,largeConstructionChecks:large,family,counts};
}

console.log(JSON.stringify(run(),null,2));
