// Exhaustive secondary experiment, run using JavaScript on 2026-11-23.
// All 6^6 total deterministic 3-state, 2-probe, binary-output Mealy machines.
// Run: node exhaustive_mealy.js
// Synthetic finite population; not a sampling estimate, nor human evidence.
// Labelled transition tables, NOT isomorphism classes. Every state is a
// possible initial state. Unit-cost queries, complete known transition table.
// The experiment was performed separately from the Python implementation.
// Observed result: 46656 machines; all pairs 35640; global adaptive 31104;
// pairwise-to-global gap 4536; winning depths 2:29376, 3:1728.
// First gap example [0,3,1,0,0,0]. Entry=3*observation+successor;
// entries state-major, 2 probes/state.
const n=3,N=6**6;
let allPair=0,full=0,gap=0,depthHist={},first=null;
function minDepth(t,initial) {
  const key=b=>b.join(",");
  const states=new Map([[key(initial),initial]]);
  const edges=new Map();
  const q=[initial];
  const rank=new Map();
  for(let i=0;i<q.length;i++){
    const b=q[i],k=key(b);
    if(b.filter(s=>s>=0).length===1){rank.set(k,0);continue;}
    const children=[];
    for(let a=0;a<2;a++){
      const groups=[[-1,-1,-1],[-1,-1,-1]];
      for(let j=0;j<n;j++)if(b[j]>=0){
        const v=t[2*b[j]+a];
        groups[Math.floor(v/3)][j]=v%3;
      }
      const kids=[];
      for(const g of groups)if(g.some(s=>s>=0)){
        const h=key(g);kids.push(h);
        if(!states.has(h)){states.set(h,g);q.push(g);}
      }
      children.push(kids);
    }
    edges.set(k,children);
  }
  for(let d=1;;d++){
    const next=[];
    for(const [k,children] of edges)if(!rank.has(k)&&children.some(kids=>kids.every(h=>rank.has(h))))next.push(k);
    if(!next.length)break;
    for(const k of next)rank.set(k,d);
    if(rank.has(key(initial)))break;
  }
  return rank.get(key(initial))??null;
}
function distinguishable(t,i,j){
  const q=[[i,j]], seen=new Set([i+","+j]);
  for(let k=0;k<q.length;k++){
    let [p,r]=q[k];
    for(let a=0;a<2;a++){
      const u=t[2*p+a],v=t[2*r+a];
      if(Math.floor(u/3)!==Math.floor(v/3))return true;
      const x=u%3,y=v%3,h=x+","+y;
      if(!seen.has(h)){seen.add(h);q.push([x,y]);}
    }
  }return false;
}
for(let z=0;z<N;z++){
  let p=z,t=[];for(let i=0;i<6;i++){t.push(p%6);p=Math.floor(p/6);}
  const pair=distinguishable(t,0,1)&&distinguishable(t,0,2)&&distinguishable(t,1,2);
  const d=minDepth(t,[0,1,2]);
  if(pair)allPair++;
  if(d!==null){full++;depthHist[d]=(depthHist[d]??0)+1;if(!pair)throw Error("global implies pairwise");}
  if(pair&&d===null){gap++;if(!first)first=t;}
}
const result={machines:N,pairwise:allPair,full,gap,depthHist,firstCounterexample:first};
console.log(JSON.stringify(result,null,2));
if(N!==46656||allPair!==35640||full!==31104||gap!==4536||depthHist[2]!==29376||depthHist[3]!==1728||
   String(first)!=="0,3,1,0,0,0")throw Error("enumeration mismatch");
