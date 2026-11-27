"use strict";
function laboratory() {
  const N=12, A=Array.from({length:N},(_,i)=>+(i%3===0)), B=Array.from({length:N},(_,i)=>+(i%4===0));
  const templates=[3,4].flatMap(p=>Array.from({length:p},(_,s)=>({id:`${p}:${s}`,v:Array.from({length:N},(_,i)=>i%p===s?72/(N/p):-72/(N-N/p))})));
  const dot=(x,y)=>x.reduce((z,v,i)=>z+v*y[i],0);
  const check=(x,msg)=>{if(!x)throw Error(msg)};
  const x=A.concat(B), coeff=(t,a,b)=>t.v.map(v=>a*v).concat(t.v.map(v=>b*v));
  const winners=s=>templates.filter((_,i)=>s[i]===Math.max(...s)).map(t=>t.id);
  const score=(x,a,b)=>templates.map(t=>dot(x,coeff(t,a,b)));
  const cross=templates.map(t=>({id:t.id,amplitude:dot(A,t.v),pitch:dot(B,t.v)}));
  check(JSON.stringify(cross.map(t=>[t.amplitude,t.pitch]))===JSON.stringify([[72,0],[-36,0],[-36,0],[0,72],[0,-24],[0,-24],[0,-24]]),"cross scores");
  let weightChecks=0;
  for(let a=0;a<=40;a++)for(let b=0;b<=40;b++)if(a+b){
    const expected=a>b?["3:0"]:b>a?["4:0"]:["3:0","4:0"];
    check(JSON.stringify(winners(score(x,a,b)))===JSON.stringify(expected),"weight phase transition");weightChecks++;
  }
  function radius(a,b){
    const s=score(x,a,b), best=s.indexOf(Math.max(...s)), C=templates.map(t=>coeff(t,a,b));
    let min=Infinity, witness=null;
    for(let j=0;j<C.length;j++)if(j!==best){
      const gap=s[best]-s[j], gains=x.map((v,i)=>({i,g:(1-2*v)*(C[j][i]-C[best][i])})).filter(z=>z.g>0).sort((u,v)=>v.g-u.g||u.i-v.i);
      let sum=0,k=0;while(sum<gap&&k<gains.length)sum+=gains[k++].g;
      if(sum>=gap&&k<min){min=k;witness={rival:templates[j].id,flips:gains.slice(0,k).map(z=>z.i)}}
    }
    const y=x.slice();for(const i of witness.flips)y[i]^=1;
    check(winners(score(y,a,b)).length!==1||winners(score(y,a,b))[0]!==templates[best].id,"edit witness");
    return {a,b,winner:templates[best].id,minimum_edits:min,...witness,after:winners(score(y,a,b))};
  }
  let bruteMasks=0;const margins=[];
  for(const [a,b] of [[1,1],[2,1],[1,2],[3,1],[1,3],[9,1],[1,9]]){
    const row=radius(a,b), C=templates.map(t=>coeff(t,a,b)), s=score(x,a,b), best=s.indexOf(Math.max(...s));
    let brute=null;
    const visit=(start,left,values)=>{
      if(left===0){bruteMasks++;return values.some((v,i)=>i!==best&&v>=values[best]);}
      for(let i=start;i<=24-left;i++){const next=values.map((v,j)=>v+(1-2*x[i])*C[j][i]);if(visit(i+1,left-1,next))return true;}return false;
    };
    for(let k=0;k<=Math.min(4,row.minimum_edits);k++)if(visit(0,k,s)){brute=k;break;}
    check(row.minimum_edits<=4?brute===row.minimum_edits:brute===null,"brute margin");
    margins.push({...row,brute_through_four:brute});
  }
  const census={};let censusTotal=0;
  for(let m=0;m<4096;m++){
    const v=Array.from({length:N},(_,i)=>(m>>i)&1), w=winners(templates.map(t=>dot(v,t.v)));
    census[w.length]=(census[w.length]||0)+1;censusTotal++;
  }
  check(censusTotal===4096&&census[7]>=2,"census");
  const rate=16000,tick=2880, audible=1920;
  function render(n,amp,pitch){
    const out=new Int16Array(n*tick);
    for(let t=0;t<n;t++){
      const f=pitch(t)?330:220, level=amp(t)?10000:5000;
      for(let i=0;i<audible;i++){
        const phase=(i*f)%rate, tri=rate-4*Math.abs(phase-rate/2), env=Math.min(i,160,audible-1-i);
        out[t*tick+i]=Math.trunc(level*tri*env/(rate*160));
      }
    }return out;
  }
  const target=render(48,t=>t%3===0,t=>t%4===0);
  const pre3=render(12,t=>t%3===0,()=>false),pre4=render(12,t=>t%4===0,()=>false);
  function join(a,b){const z=new Int16Array(a.length+b.length);z.set(a);z.set(b,a.length);return z;}
  const editions={target,context3:join(pre3,target),context4:join(pre4,target)};
  function fingerprint(x){let h=2166136261;for(const s of x){h=Math.imul(h^(s&255),16777619);h=Math.imul(h^((s>>8)&255),16777619);}return (h>>>0).toString(16).padStart(8,"0");}
  const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
  check(same(editions.context3.subarray(pre3.length),target)&&same(editions.context4.subarray(pre4.length),target),"identical target");
  check(!same(editions.context3,editions.context4),"different contexts");
  const audio={};
  for(const [name,pcm] of Object.entries(editions)){let peak=0;for(const s of pcm)peak=Math.max(peak,Math.abs(s));check(peak<=10000,"peak");audio[name]={frames:pcm.length,pcm_fnv1a32:fingerprint(pcm),peak};}
  return {receipt:{status:"PASS",cross,weightChecks,margins,bruteMasks,census,censusTotal,rate,tick,audio,target_identical:true,context_different:true,scope:"synthetic symbolic cue model; no human metric judgments"},editions};
}

if (typeof module !== "undefined" && require.main === module) {
  const {receipt,editions}=laboratory();
  if(process.argv[2]) {
    const fs=require("node:fs"), path=require("node:path");
    fs.mkdirSync(process.argv[2],{recursive:true});
    for(const [name,pcm] of Object.entries(editions)) {
      const b=Buffer.alloc(44+2*pcm.length);b.write("RIFF");b.writeUInt32LE(b.length-8,4);b.write("WAVEfmt ",8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write("data",36);b.writeUInt32LE(2*pcm.length,40);for(let i=0;i<pcm.length;i++)b.writeInt16LE(pcm[i],44+2*i);fs.writeFileSync(path.join(process.argv[2],name+".wav"),b);
    }
  }
  console.log(JSON.stringify(receipt,null,2));
}
