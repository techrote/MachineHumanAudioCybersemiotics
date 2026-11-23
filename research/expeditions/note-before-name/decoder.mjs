function analyze(input) {
  const C=[...input].sort();
  if(!C.length || C.some(w=>typeof w!=="string" || !/^[01]+$/.test(w)) || new Set(C).size!==C.length) throw Error("distinct nonempty binary words required");
  const states=new Map(), key=(a,b)=>a+"|"+b;
  const starts=[];
  for(let i=0;i<C.length;i++)for(let j=i+1;j<C.length;j++)starts.push([C[i],C[j]]);
  const queue=starts.map(([a,b])=>({a,b,path:"",first:[a,b]}));
  let collision=null;
  for(let i=0;i<queue.length;i++){
    const {a,b,path,first}=queue[i], k=key(a,b);
    if(states.has(k))continue;
    const node={a,b,edges:[],path,first};states.set(k,node);
    if(a[0]!==b[0])continue;
    if(a.length===1 && b.length===1 && collision===null)collision={bits:path+a[0],first};
    for(const x of (a.length===1?C:[a.slice(1)]))
      for(const y of (b.length===1?C:[b.slice(1)])){
        node.edges.push(key(x,y));queue.push({a:x,b:y,path:path+a[0],first});
      }
  }
  const color=new Map(), memo=new Map(), stack=[];let cycle=null;
  function visit(k){
    if(color.get(k)===1){
      if(!cycle){const j=stack.indexOf(k);cycle={stem:stack.slice(0,j).map(s=>states.get(s).a[0]).join(""),period:stack.slice(j).map(s=>states.get(s).a[0]).join(""),first:states.get(stack[0]).first,states:stack.slice(j)};}
      return Infinity;
    }
    if(color.get(k)===2)return memo.get(k);
    color.set(k,1);stack.push(k);
    const n=states.get(k);let v=0;
    for(const e of n.edges)v=Math.max(v,1+visit(e));
    stack.pop();color.set(k,2);memo.set(k,v);return v;
  }
  // First-word labels of a cycle witness must be those of the actual DFS root,
  // not the BFS root that happened to discover its residual state.
  let longest=0, longestStart=null;
  for(const [a,b] of starts){
    const prior=cycle; const v=visit(key(a,b));
    if(!prior&&cycle)cycle.first=[a,b];
    if(v>longest){longest=v;longestStart=[a,b];}
  }
  let witness=null;
  if(Number.isFinite(longest)&&longestStart){
    let k=key(...longestStart), bits="";
    while(memo.get(k)>0){const n=states.get(k);bits+=n.a[0];k=n.edges.find(e=>memo.get(e)===memo.get(k)-1);}
    witness={first:longestStart,bits};
  }
  const prefix=C.every(a=>C.every(b=>a===b||!b.startsWith(a)));
  return {code:C,kind:collision?"non_ud":cycle?"ud_unbounded":prefix?"prefix_free":"ud_finite",states:states.size,collision,cycle,max_shared_prefix:Number.isFinite(longest)?longest:null,longest_witness:witness};
}

function sardinas(C){
  const todo=[],seen=new Set();
  for(const a of C)for(const b of C)if(a!==b&&b.startsWith(a))todo.push(b.slice(a.length));
  for(let i=0;i<todo.length;i++){
    const r=todo[i];if(!r)return false;if(seen.has(r))continue;seen.add(r);
    for(const w of C){if(r.startsWith(w))todo.push(r.slice(w.length));if(w.startsWith(r))todo.push(w.slice(r.length));}
  }
  return true;
}

function canParse(C,bits,first,complete){
  if(!bits.startsWith(first.slice(0,Math.min(bits.length,first.length))))return false;
  if(bits.length<first.length)return !complete;
  const rest=bits.slice(first.length), reach=new Set([0]);
  for(let i=0;i<=rest.length;i++)if(reach.has(i)){
    if(i===rest.length)return true;
    for(const w of C){
      if(rest.startsWith(w,i))reach.add(i+w.length);
      if(!complete && w.startsWith(rest.slice(i)))return true;
    }
  }
  return false;
}

function prefixOracle(C,h){
  let layer=new Map();
  for(const w of C)layer.set(w,new Set([w]));
  // Direct enumeration of bit strings, independent of product graph.
  for(let n=0;n<=h;n++){
    let ambiguous=false;
    for(let i=0;i<2**n;i++){
      const bits=n===0?"":i.toString(2).padStart(n,"0");
      if(C.filter(w=>canParse(C,bits,w,false)).length>1){ambiguous=true;break;}
    }
    if(!ambiguous)return n-1;
  }
  return null;
}

function experiment(){
  const check=(x,m)=>{if(!x)throw Error(m)};
  const examples=[["0","10","11"],["0","01"],["0","01","11"],["0","01","10"],["00","01","10","11"],["110","11","100","00","10"]].map(analyze);
  check(examples[0].kind==="prefix_free","prefix");
  check(examples[1].kind==="ud_finite"&&examples[1].max_shared_prefix===1,"bounded");
  check(examples[2].kind==="ud_unbounded","infinite");
  check(examples[3].kind==="non_ud"&&examples[3].collision.bits==="010","collision");
  let words=[];for(let n=1;n<=4;n++)for(let i=0;i<2**n;i++)words.push(i.toString(2).padStart(n,"0"));
  const census={}, maxima={}, maxExamples={};let tested=0,collisionChecks=0,cycleChecks=0,prefixChecks=0;
  for(let i=0;i<words.length;i++)for(let j=i+1;j<words.length;j++)for(let k=j+1;k<words.length;k++){
    const C=[words[i],words[j],words[k]],r=analyze(C);tested++;
    check((r.kind!=="non_ud")===sardinas(C),"SP mismatch "+C);
    census[r.kind]=(census[r.kind]||0)+1;
    if(r.collision){check(r.collision.first.every(w=>canParse(C,r.collision.bits,w,true)),"invalid collision witness");collisionChecks++;}
    if(r.cycle){const {stem,period,first}=r.cycle;check(period.length>0,"empty period");for(let z=0;z<5;z++)check(first.every(w=>canParse(C,stem+period.repeat(z),w,false)),"invalid cycle prefix");cycleChecks++;}
    if(r.longest_witness){const {bits,first}=r.longest_witness;check(bits.length===r.max_shared_prefix&&first.every(w=>canParse(C,bits,w,false)),"longest witness");}
    if(r.kind==="ud_finite" && (maxima.ud_finite===undefined||r.max_shared_prefix>maxima.ud_finite)){maxima.ud_finite=r.max_shared_prefix;maxExamples.ud_finite=r;}
    if(C.every(w=>w.length<=3)){
      const brute=prefixOracle(C,10);
      check(brute===null?r.max_shared_prefix===null||r.max_shared_prefix>=10:brute===r.max_shared_prefix,"prefix oracle mismatch "+C);prefixChecks++;
    }
  }
  const family=[];
  for(let m=1;m<=32;m++){
    const C=["0","0"+"1".repeat(m),"1".repeat(m+1)+"0"],r=analyze(C);
    family.push({m,kind:r.kind,max_shared_prefix:r.max_shared_prefix});
  }
  return {examples,census,tested,collisionChecks,cycleChecks,prefixChecks,maxima,maxExamples,family};
}

export {analyze,sardinas,canParse,prefixOracle,experiment};
