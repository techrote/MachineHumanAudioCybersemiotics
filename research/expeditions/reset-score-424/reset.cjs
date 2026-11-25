"use strict";
// Original synthetic expedition, issue #424. Node 18+.
function requireCondition(ok,msg){if(!ok)throw Error(msg);}

function apply(word,m,x){
  for(const c of word){if(c!== "+"&&c!=="-")throw Error("invalid symbol");x=Math.max(0,Math.min(m,x+(c==="+"?1:-1)));}
  return x;
}

function profile(word,R){
  if(!Number.isInteger(R)||R<1||R>256)throw Error("capacity range 1..256");
  let p=0,a=0,b=0;const targets=[];
  for(let i=word.length-1;i>=0;i--){
    const c=word[i];if(c!=="+"&&c!=="-")throw Error("invalid symbol");
    p+=c==="+"?1:-1;
    if(p>a){a=p;if(targets.length<R)targets.push(a);}
    if(p<b){b=p;if(targets.length<R)targets.push(a);}
  }
  return {net:p,range:a-b,targets,images:Array.from({length:R},(_,i)=>i<targets.length?[targets[i],targets[i]]:[a,i+1+b])};
}

function compile(anchors){
  const R=anchors.length;
  if(!Array.isArray(anchors)||R<1||R>256)throw Error("capacity range 1..256");
  for(let i=0;i<R;i++)if(anchors[i]!==null&&(!Number.isInteger(anchors[i])||anchors[i]<0||anchors[i]>i+1))throw Error("invalid anchor");
  // DP state: positive expansions so far, direction of most recent record.
  let dp=new Map([["0,0",{a:0,last:0,cost:0,bits:""}]]);
  for(let m=1;m<=R;m++){
    const next=new Map();
    for(const {a,last,cost,bits} of dp.values())for(const d of [-1,1]){
      const aa=a+(d===1?1:0);
      if(anchors[m-1]!==null&&aa!==anchors[m-1])continue;
      const v={a:aa,last:d,cost:cost+(last===0||last===d?1:m),bits:bits+(d===1?"+":"-")};
      const key=aa+","+d,old=next.get(key);
      if(!old||v.cost<old.cost||(v.cost===old.cost&&v.bits<old.bits))next.set(key,v);
    }
    if(!next.size)throw Error("incompatible anchors");
    dp=next;
  }
  let best=null;
  for(const v of dp.values()){
    const total=v.cost+(v.last===1?v.a:R-v.a);
    if(!best||total<best.length||(total===best.length&&v.bits<best.bits))best={...v,length:total};
  }
  let p=0,a=0,b=0,rev="";
  for(const c of best.bits){
    const dest=c==="+"?++a:--b;
    rev+=(dest>=p?"+":"-").repeat(Math.abs(dest-p));p=dest;
  }
  rev+=(p>0?"-":"+").repeat(Math.abs(p));
  const word=rev.split("").reverse().join("");
  const checked=profile(word,R);
  requireCondition(word.length===best.length&&checked.net===0&&checked.range===R,"compiler certificate");
  requireCondition(anchors.every((v,i)=>v===null||v===checked.targets[i]),"anchor certificate");
  return {word,length:word.length,targets:checked.targets,recordDirections:best.bits};
}

function verify(){
  const eq=(x,y)=>JSON.stringify(x)===JSON.stringify(y);
  let words=0,images=0,profiles=0,sparse=0,bfsStates=0,invalid=0;
  const bfsRows=[];
  for(let len=0;len<=12;len++)for(let mask=0;mask<2**len;mask++){
    const w=Array.from({length:len},(_,i)=>mask&(1<<i)?"+":"-").join("");
    const z=profile(w,8);words++;
    for(let m=1;m<=8;m++){
      const actual=Array.from({length:m+1},(_,i)=>apply(w,m,i));
      requireCondition(eq(z.images[m-1],[Math.min(...actual),Math.max(...actual)]),"image mismatch");images++;
    }
  }
  for(let R=1;R<=7;R++){
    const optimal=new Map(),all=[];
    for(let mask=0;mask<2**R;mask++){
      let a=0;const f=Array.from({length:R},(_,i)=>a+=(mask>>i)&1);
      const z=compile(f);profiles++;
      requireCondition(eq(z.targets,f),"target mismatch");
      all.push(z);
    }
    // Independent breadth-first search on full transition images (not record directions).
    const initial=Array.from({length:R},(_,i)=>[0,i+1]).flat();
    const queue=[{s:0,img:initial,L:0}],seen=new Set(["0:"+initial.join(",")]);let h=0;
    while(h<queue.length&&optimal.size<2**R){
      const {s,img,L}=queue[h++];bfsStates++;
      if(s===0&&img.every((x,i)=>i%2||x===img[i+1])){
        const k=img.filter((_,i)=>i%2===0).join(",");
        if(!optimal.has(k))optimal.set(k,L);
      }
      for(const d of [-1,1]){
        const im=img.map((x,i)=>Math.max(0,Math.min(Math.floor(i/2)+1,x+d)));
        const ns=s+d,k=ns+":"+im.join(",");
        if(!seen.has(k)){seen.add(k);queue.push({s:ns,img:im,L:L+1});}
      }
      requireCondition(h<1000000,"BFS budget exceeded");
    }
    requireCondition(optimal.size===2**R,"BFS incomplete");
    for(const z of all)requireCondition(optimal.get(z.targets.join(","))===z.length,"BFS optimum mismatch");
    bfsRows.push({R,profiles:all.length,min:Math.min(...all.map(z=>z.length)),max:Math.max(...all.map(z=>z.length)),states:h});
    // All feasible sparse-anchor patterns induced by every full profile.
    const wanted=new Map();
    for(const z of all)for(let mask=0;mask<2**R;mask++){
      const a=z.targets.map((v,i)=>mask&(1<<i)?v:null),k=JSON.stringify(a);
      if(!wanted.has(k)||wanted.get(k)>z.length)wanted.set(k,z.length);
    }
    for(const [k,L] of wanted){requireCondition(compile(JSON.parse(k)).length===L,"sparse optimum mismatch");sparse++;}
  }
  for(const a of [[],[2],[1,0],[0,2],[null,3],[0,1.5]]){let failed=false;try{compile(a);}catch{failed=true;}requireCondition(failed,"invalid target accepted");invalid++;}
  const witnesses={ascending:compile([1,2,3,4,5,6,7,8]),alternating:compile([1,1,2,2,3,3,4,4]),sparse:compile([null,1,null,2,null,3,null,4]),reverse:compile([0,1,1,2,2,3,3,4])};
  return {words,images,profiles,sparse,bfsStates,invalid,bfsRows,witnesses};
}

module.exports={apply,profile,compile,verify};
if(require.main===module) console.log(JSON.stringify(verify(),null,2));
