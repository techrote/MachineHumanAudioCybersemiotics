"use strict";
// Synthetic zero-error laboratory. No participant or hardware data.
function insist(x,m){if(!x)throw Error(m)}
function parity(x){let p=0;while(x){p^=1;x&=x-1}return p}
function unpack(x,d,T){return Array.from({length:T},(_,j)=>(x>>>(j*d))&((1<<d)-1))}
function pack(a,d){return a.reduce((v,x,i)=>v|(x<<(i*d)),0)}
// Greedy minimum switches in a trajectory annihilating every difference.
function greedy(w,d){
  let span=[0],cuts=0;
  for(const x of w){
    const next=[...new Set([...span,...span.map(y=>x^y)])];
    if(next.length===1<<d){cuts++;span=x?[0,x]:[0]}else span=next;
  }
  return cuts;
}
// Independent dynamic program on actual observer identities, no rank operations.
function observerDP(w,d){
  let prev=Array(1<<d).fill(Infinity);
  for(let a=1;a<1<<d;a++)prev[a]=0;
  for(const x of w){
    const mn=Math.min(...prev),next=prev.map((v,a)=>a&&!parity(a&x)?Math.min(v,mn+1):Infinity);
    prev=next;
  }
  return Math.min(...prev);
}
function paths(d,T,s){
  const all=[];
  function walk(a,k){if(a.length===T){all.push(a);return}
    for(let b=1;b<1<<d;b++){const c=a.length&&b!==a.at(-1)?1:0;if(k+c<=s)walk([...a,b],k+c)}
  }
  walk([],0);return all;
}
function observe(w,a){return w.map((x,i)=>parity(x&a[i])).join("")}
function checkBook(book,d,T,s){
  let n=0;for(const a of paths(d,T,s)){
    const out=new Set(book.map(x=>observe(unpack(x,d,T),a)));
    insist(out.size===book.length,"decoder collision");n+=book.length;
  }return n;
}
// Translation invariance permits fixing the zero word. Upper certificate is
// exact increasing-index clique enumeration; greedy coloring bounds extensions.
function clique(d,T,s){
  const good=new Set();for(let x=1;x<1<<(d*T);x++)if(greedy(unpack(x,d,T),d)>s)good.add(x);
  const V=[...good],adj=V.map(x=>V.reduce((b,y,j)=>good.has(x^y)?b|(1n<<BigInt(j)):b,0n));
  const bit=V.map((_,j)=>1n<<BigInt(j)),index=new Map(bit.map((b,j)=>[b,j]));
  let best=[],nodes=0;
  function expand(C,P){
    nodes++;if(C.length>best.length)best=C.slice();
    let rem=P,color=0,order=[],bounds=[];
    // Each color class is independent in the current candidate graph.
    while(rem){color++;let avail=rem;while(avail){
      const b=avail&-avail,i=index.get(b);order.push(i);bounds.push(color);
      rem^=b;avail&=~(b|adj[i]);
    }}
    for(let j=order.length-1;j>=0;j--){
      if(C.length+bounds[j]<=best.length)return;
      const i=order[j];expand([...C,i],P&adj[i]);P&=~bit[i];
    }
  }
  expand([], (1n<<BigInt(V.length))-1n);
  const book=[0,...best.map(i=>V[i])];
  return {d,T,s,good:V.length,max:book.length,nodes,book,decoderObservations:checkBook(book,d,T,s)};
}
// Independent upper-bound check for a prescribed clique size. No coloring;
// uses direct observer DP rather than greedy rank.
function noClique(d,T,s,want){
  const V=[];for(let x=1;x<1<<(d*T);x++)if(observerDP(unpack(x,d,T),d)>s)V.push(x);
  const good=new Set(V);let nodes=0;
  function search(candidates,need){
    nodes++;if(!need)return true;
    for(let i=0;i<=candidates.length-need;i++){
      const a=candidates[i],rest=candidates.slice(i+1).filter(b=>good.has(a^b));
      if(search(rest,need-1))return true;
    }return false;
  }
  return {found:search(V,want-1),nodes};
}
function mul(a,b,d,poly){let z=0;while(b){if(b&1)z^=a;b>>>=1;a<<=1;if(a&(1<<d))a^=poly}return z}
function thresholdBook(d,s,poly){
  const T=(s+1)*(d-1)+1;
  const words=Array.from({length:1<<d},(_,m)=>Array.from({length:T},(_,j)=>mul(m,1<<(j%d),d,poly)));
  let pairs=0;
  for(let i=0;i<words.length;i++)for(let j=i+1;j<words.length;j++){
    const w=words[i].map((x,t)=>x^words[j][t]);
    insist(greedy(w,d)===s+1,"threshold rank");
    insist(observerDP(w,d)===s+1,"threshold observer");pairs++;
  }
  return {d,s,T,messages:words.length,pairs};
}
// Unknown fixed observer: output sets are nonzero vectors in binary row spaces
// (plus zero for a deficient matrix). Construct a spread over GF(4).
function hiddenSpread(k){
  const d=2,T=2*k,poly=7,seen=new Set(),words=[Array(T).fill(0)];
  const scale=(v,a)=>Array.from({length:k},(_,i)=>mul((v>>(2*i))&3,a,2,poly)).reduce((z,x,i)=>z|(x<<(2*i)),0);
  for(let v=1;v<1<<T;v++)if(!seen.has(v)){
    const line=[v,scale(v,2),scale(v,3)];for(const y of line)seen.add(y);
    insist(new Set(line).size===3,"spread line");
    const b=line[1];words.push(Array.from({length:T},(_,i)=>((v>>i)&1)|(((b>>i)&1)<<1)));
  }
  const outputs=new Map();for(let m=0;m<words.length;m++)for(let a=1;a<=3;a++){
    const y=observe(words[m],Array(T).fill(a));insist(!outputs.has(y)||outputs.get(y)===m,"hidden observer collision");outputs.set(y,m);
  }
  insist(outputs.size===1<<T,"spread cover");
  return {d,T,messages:words.length,distinctOutputs:outputs.size};
}
function pcm(bits){
  const rate=8000,n=800,buf=new Uint8Array(44+2*n*bits.length),v=new DataView(buf.buffer);
  function ascii(o,s){for(let i=0;i<s.length;i++)buf[o+i]=s.charCodeAt(i)}
  ascii(0,"RIFF");v.setUint32(4,buf.length-8,true);ascii(8,"WAVE");ascii(12,"fmt ");v.setUint32(16,16,true);
  v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,2*rate,true);
  v.setUint16(32,2,true);v.setUint16(34,16,true);ascii(36,"data");v.setUint32(40,buf.length-44,true);
  for(let j=0;j<bits.length;j++)for(let i=0;i<n;i++){
    const period=bits[j]==="1"?20:40,env=Math.min(i,n-1-i,40);
    v.setInt16(44+2*(j*n+i),((i%period)<period/2?1:-1)*env*150,true);
  }return buf;
}
function fingerprint(b){let h=2166136261;for(const x of b)h=Math.imul(h^x,16777619);return (h>>>0).toString(16).padStart(8,"0")}
function same(a,b){return a.length===b.length&&a.every((x,i)=>x===b[i])}
function audio(){
  const a=[0,0],b=[1,2],fixed=[1,1],switching=[2,1];
  const seqs={fixedA:observe(a,fixed),fixedB:observe(b,fixed),switchedA:observe(a,switching),switchedB:observe(b,switching),
    repairedA:observe([0,0,0],[2,1,1]),repairedB:observe([1,2,1],[2,1,1])};
  const wavs=Object.fromEntries(Object.entries(seqs).map(([k,v])=>[k,pcm(v)]));
  insist(!same(wavs.fixedA,wavs.fixedB),"fixed sound");
  insist(same(wavs.switchedA,wavs.switchedB),"switched sound");
  insist(!same(wavs.repairedA,wavs.repairedB),"repaired sound");
  return {wavs,receipt:Object.fromEntries(Object.keys(seqs).map(k=>[k,{bits:seqs[k],bytes:wavs[k].length,fnv1a:fingerprint(wavs[k])}]))};
}
function run(){
  let comparisons=0;const census=[];
  for(const [d,maxT] of [[2,8],[3,5]]){
    for(let T=1;T<=maxT;T++){let counts=Array(T).fill(0);
      for(let x=0;x<1<<(d*T);x++){
        const w=unpack(x,d,T),g=greedy(w,d),o=observerDP(w,d);
        insist(g===o,"greedy/DP mismatch");counts[g]++;comparisons++;
      }
      census.push({d,T,minimumSwitchHistogram:counts});
    }
  }
  const maxima=[[2,0],[3,1],[4,1],[4,2],[5,2],[5,3],[6,3]].map(([T,s])=>clique(2,T,s));
  insist(maxima.map(x=>x.max).join(",")==="4,4,8,4,5,4,4","maxima mismatch");
  const upper=noClique(2,5,2,6);insist(!upper.found,"six-word counterexample");
  const threshold=[];for(const [d,p] of [[2,7],[3,11],[4,19],[5,37],[6,67]])for(let s=0;s<=4;s++)threshold.push(thresholdBook(d,s,p));
  const spreads=[1,2,3,4,5].map(hiddenSpread);
  return {model:"synthetic binary vector, decoder-known path unless noted",comparisons,census,maxima,independentSixWordRefusal:upper,threshold,spreads,audio:audio().receipt};
}
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
  const result=run();console.log(JSON.stringify(result,null,2));
  if(process.argv[2]==="--out"){const fs=require("node:fs"),p=require("node:path"),dir=process.argv[3];if(!dir)throw Error("output directory required");fs.mkdirSync(dir,{recursive:true});for(const [k,v] of Object.entries(audio().wavs))fs.writeFileSync(p.join(dir,k+".wav"),v)}
}
