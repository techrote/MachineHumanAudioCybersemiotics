"use strict";
// Refs #268: original synthetic laboratory; run with Node.js.
function laboratory() {
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  const pop=x=>{let k=0;for(;x;x&=x-1)k++;return k};
  const bit=i=>1<<i;
  const parity=(x,m)=>pop(x&m)&1;
  const rows=ms=>x=>ms.reduce((s,m,i)=>s|(parity(x,m)<<i),0);
  const cols=cs=>x=>cs.reduce((s,c,i)=>s^((x&bit(i))?c:0),0);
  const cycleMasks=n=>Array.from({length:n},(_,i)=>bit((i+n-1)%n)|bit((i+1)%n));
  const matching=(n,shift)=>rows(Array.from({length:n/2},(_,i)=>bit((2*i+shift)%n)|bit((2*i+shift+1)%n)));
  const path=n=>rows(Array.from({length:n-1},(_,i)=>bit(i)|bit(i+1)));
  const fullMasks=n=>Array.from({length:n},(_,i)=>(bit(n)-1)^bit(i));
  const erasures=m=>[m,...Array.from({length:32},(_,j)=>bit(j)).filter(b=>m&b).map(b=>m^b)];
  const verify=(n,enc,masks,mode)=>{
    let observations=0;
    for(let i=0;i<n;i++){
      const seen=new Map(), masksHere=mode==="erase"?erasures(masks[i]):[masks[i]];
      for(let x=0;x<bit(n);x++)for(const m of masksHere){
        const side=x&m;
        const possibilities=mode==="stale"?[side,...Array.from({length:n},(_,j)=>bit(j)).filter(b=>m&b).map(b=>side^b)]:[side];
        for(const received of possibilities){
          const k=enc(x)+":"+m+":"+received, v=(x>>i)&1;
          check(!seen.has(k)||seen.get(k)===v,"decoder collision n="+n+" receiver="+i);
          seen.set(k,v); observations++;
        }
      }
    }
    return observations;
  };
  // Independently enumerate all possible fibers on a small source alphabet.
  // A valid fiber contains no pair that can give the same receiver observation.
  const maxFiber=(n,masks,mode)=>{
    const size=bit(n), bad=Array.from({length:size},()=>0);
    for(let x=0;x<size;x++)for(let y=x+1;y<size;y++){
      const d=x^y;
      const conflict=masks.some((m,i)=>(d&bit(i))&&(
        mode==="stale"?pop(d&m)<=2:
        mode==="erase"?erasures(m).some(z=>(d&z)===0):
        (d&m)===0));
      if(conflict){bad[x]|=bit(y);bad[y]|=bit(x)}
    }
    let max=0, examined=0;
    for(let s=1;s<bit(size);s++){
      examined++;
      if(pop(s)<=max)continue;
      let valid=true;
      for(let x=0;x<size;x++)if((s&bit(x))&&(s&bad[x])){valid=false;break}
      if(valid)max=pop(s);
    }
    return {max,examined,lengthLower:Math.ceil(Math.log2(size/max))};
  };
  const result={cycle:[],clique:[],small_fibers:[],audio:{}};
  for(let n=4;n<=10;n+=2){
    const m=cycleMasks(n);
    const nominal=verify(n,matching(n,0),m,"fixed");
    let known=0,scenarios=0;
    for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(m[i]&bit(j)){
      const altered=m.slice();altered[i]^=bit(j);
      // A matching uses the missing undirected edge iff its lower cyclic endpoint has the chosen parity.
      const start=(j===(i+1)%n)?i:j;
      known+=verify(n,matching(n,1-(start%2)),altered,"fixed");scenarios++;
    }
    const universal=verify(n,path(n),m,"erase");
    result.cycle.push({n,nominal_length:n/2,known_length:n/2,unknown_length:n-1,nominal,known,scenarios,universal});
  }
  for(let n=2;n<=10;n++){
    const m=fullMasks(n),all=bit(n)-1;
    const nominal=verify(n,rows([all]),m,"fixed");
    let known=0,scenarios=0;
    for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(i!==j){
      const altered=m.slice();altered[i]^=bit(j);
      known+=verify(n,rows([all,bit(i)]),altered,"fixed");scenarios++;
    }
    const r=Math.ceil(Math.log2(n)),er=Math.ceil(Math.log2(n+1));
    const universal=verify(n,cols(Array.from({length:n},(_,i)=>i+1)),m,"erase");
    const stale=verify(n,cols(Array.from({length:n},(_,i)=>bit(r)|i)),m,"stale");
    result.clique.push({n,nominal_length:1,known_length:2,unknown_length:er,stale_length:r+1,nominal,known,scenarios,universal,stale});
  }
  for(const n of [2,3,4])for(const mode of ["fixed","erase","stale"]){
    const f=maxFiber(n,fullMasks(n),mode);
    const predicted=mode==="fixed"?1:mode==="erase"?Math.ceil(Math.log2(n+1)):1+Math.ceil(Math.log2(n));
    check(f.lengthLower===predicted,"clique fiber bound");
    result.small_fibers.push({graph:"clique",n,mode,...f});
  }
  for(const mode of ["fixed","erase"]){
    const f=maxFiber(4,cycleMasks(4),mode);
    check(f.lengthLower===(mode==="fixed"?2:3),"cycle fiber bound");
    result.small_fibers.push({graph:"cycle",n:4,mode,...f});
  }
  // Negative control: known erasure at receiver 2 of bit 3. Surviving bit 1 is zero in both states.
  const a=0,b=12,nom=matching(4,0),rob=path(4);
  check(nom(a)===nom(b)&&rob(a)!==rob(b)&&((a^b)&bit(2))&&((a^b)&bit(1))===0,"negative control");
  result.witness={states:[a,b],receiver:2,missing:3,known:1,nominal:[nom(a),nom(b)],robust:[rob(a),rob(b)]};
  // Original square-pulse score. Fixed slot counts, 8kHz, signed 16-bit mono.
  const wav=(code,length)=>{
    const samples=800*length, bytes=new Uint8Array(44+2*samples),d=new DataView(bytes.buffer);
    const tag=(offset,s)=>{for(let i=0;i<s.length;i++)bytes[offset+i]=s.charCodeAt(i)};
    tag(0,"RIFF");d.setUint32(4,bytes.length-8,true);tag(8,"WAVE");tag(12,"fmt ");
    d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,8000,true);
    d.setUint32(28,16000,true);d.setUint16(32,2,true);d.setUint16(34,16,true);tag(36,"data");d.setUint32(40,2*samples,true);
    for(let i=0;i<samples;i++){
      const slot=Math.floor(i/800),t=i%800,period=(code&bit(slot))?16:32;
      d.setInt16(44+2*i,t>=720?0:(t%period<period/2?3500:-3500),true);
    }
    return bytes;
  };
  const equal=(x,y)=>x.length===y.length&&x.every((b,i)=>b===y[i]);
  const hash=x=>{let h=2166136261;for(const b of x)h=Math.imul(h^b,16777619)>>>0;return h.toString(16).padStart(8,"0")};
  const arrays={nominal_A:wav(nom(a),2),nominal_B:wav(nom(b),2),robust_A:wav(rob(a),3),robust_B:wav(rob(b),3)};
  check(equal(arrays.nominal_A,arrays.nominal_B)&&!equal(arrays.robust_A,arrays.robust_B),"audio witness");
  result.audio=Object.fromEntries(Object.entries(arrays).map(([k,v])=>[k,{bytes:v.length,fnv1a:hash(v)}]));
  result.audio.nominal_identical=true;result.audio.robust_distinct=true;
  result.total_observations=[...result.cycle,...result.clique].reduce((s,r)=>s+r.nominal+r.known+r.universal+(r.stale||0),0);
  result.total_fibers=result.small_fibers.reduce((s,r)=>s+r.examined,0);
  return {result,arrays};
}
if (require.main === module) {
  const {result,arrays}=laboratory();
  console.log(JSON.stringify(result,null,2));
  if (process.argv[2]) {
    const fs=require("node:fs"),p=require("node:path");
    fs.mkdirSync(process.argv[2],{recursive:true});
    for(const [name,bytes] of Object.entries(arrays)) fs.writeFileSync(p.join(process.argv[2],name+".wav"),bytes);
  }
}
module.exports={laboratory};
