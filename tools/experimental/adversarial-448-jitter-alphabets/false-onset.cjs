"use strict";
// MHAC #448 / adversarial continuation; synthetic only. See README-false-onset.md.
const books={"source8":[[0,1,4,13],[0,1,5,6],[0,1,10,17],[0,1,11,12],[0,1,14,18],[0,1,15,16],[0,2,7,18],[0,2,11,13]],"source8_searched":[[0,3,8,17],[0,9,12,13],[0,1,10,17],[0,9,14,17],[0,1,4,13],[0,7,16,17],[0,3,11,14],[0,2,15,17]],"robust8":[[0,2,15,17],[0,3,5,8],[0,2,7,9],[0,1,17,18],[0,1,2,3],[0,5,6,11],[0,3,4,7],[0,1,11,12]]};
function run(books){
  const rate=8000,seeds=[1201,1709,2089],repeats=16;let checks=0;
  const check=(b,m)=>{checks++;if(!b)throw Error(m)};
  const rng=seed=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
  const triples=w=>w.map((_,i)=>w.filter((_,j)=>j!==i).map(t=>t/w[3]));
  const subsets=y=>y.length===3?[y]:y.map((_,i)=>y.filter((_,j)=>j!==i));
  const ratio=t=>(t[1]-t[0])/(t[2]-t[0]);
  function fit(t,y,e){let lo=.6,hi=1;for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){let d=t[j]-t[i],q=y[j]-y[i];lo=Math.max(lo,(q-2*e)/d);hi=Math.min(hi,(q+2*e)/d)}return lo<=hi+1e-12}
  function decide(c,picks,id){if(!picks.includes(id))c.truth_omitted++;if(picks.length!==1)c.abstain++;else if(picks[0]===id)c.correct++;else c.wrong++}
  const counter=()=>({correct:0,wrong:0,abstain:0,truth_omitted:0});
  function wav(samples){const len=samples.at(-1)+160,pcm=new Int16Array(len);for(const s of samples)for(let k=0;k<80;k++)pcm[s+k]+=Math.round(4000*Math.sin(2*Math.PI*500*k/rate)*Math.sin(Math.PI*k/79)**2);const b=new Uint8Array(44+len*2),v=new DataView(b.buffer);const tag=(o,s)=>{for(let i=0;i<s.length;i++)b[o+i]=s.charCodeAt(i)};tag(0,"RIFF");v.setUint32(4,b.length-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,2*rate,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,len*2,true);for(let i=0;i<len;i++)v.setInt16(44+i*2,pcm[i],true);check(pcm.every(x=>Math.abs(x)<=16000),"peak");return b}
  const results={},audio={};
  for(const [name,words] of Object.entries(books)){
    check(words.length===8,"size");const ts=words.map(triples),cert=[];
    // Exact integer-sample witnesses. Retain endpoints and a private interior from each word.
    for(let i=0;i<8;i++)for(let j=i+1;j<8;j++){
      const A=words[i],B=words[j],den=A[3]*B[3],span=den*Math.ceil(4800/den),off=800;
      const a=A.map(x=>off+x*(span/A[3])),b=B.map(x=>off+x*(span/B[3]));
      const ai=a.find((x,k)=>k>0&&k<3&&!b.includes(x)),bi=b.find((x,k)=>k>0&&k<3&&!a.includes(x));
      check(ai!==undefined&&bi!==undefined,"private interior");
      const ya=[a[0],ai,a[3],bi].sort((x,y)=>x-y),yb=[b[0],bi,b[3],ai].sort((x,y)=>x-y);
      check(span>=4800&&span<=8000&&ya.every(Number.isInteger),"exact grid");
      check(new Set(ya).size===4&&ya.every((x,k)=>x===yb[k]),"equal observation");
      check(a.filter(x=>!ya.includes(x)).length===1&&ya.filter(x=>!a.includes(x)).length===1&&b.filter(x=>!yb.includes(x)).length===1&&yb.filter(x=>!b.includes(x)).length===1,"one substitution per world");
      const wa=wav(ya),wb=wav(yb);check(wa.length===wb.length&&wa.every((x,k)=>x===wb[k]),"PCM equality");
      const picks=ts.map((t,k)=>t.some(z=>subsets(ya.map(x=>x/rate)).some(y=>fit(z,y,0)))?k:-1).filter(k=>k>=0);
      check(picks.includes(i)&&picks.includes(j),"zero jitter ambiguity");
      cert.push({words:[i,j],scale_samples:span,original_a:a,original_b:b,deleted_a:a.find(x=>!ya.includes(x)),deleted_b:b.find(x=>!yb.includes(x)),false_a:bi,false_b:ai,receipt:ya,candidates:picks});
      if(i===0&&j===1)audio[name]=wa;
    }
    const conditions=[];
    for(const insert of [false,true])for(const warp of [0,.005,.015])for(const jitter of [0,.002]){
      const nearest=counter(),nominal=counter(),envelope=counter();let invalid=0,total=0;const examples={};
      for(const seed of seeds){const rand=rng(seed);for(let id=0;id<8;id++)for(let d=0;d<4;d++)for(let k=0;k<repeats;k++){
        const scale=.6+.4*rand(),off=.1+.1*rand(),bend=warp*(2*rand()-1),t=ts[id][d];
        const raw=t.map(x=>off+scale*x+4*bend*x*(1-x)+jitter*(2*rand()-1));
        const falseTime=off+scale*rand();if(insert)raw.push(falseTime);
        const y=raw.map(x=>Math.round(x*rate)/rate).sort((a,b)=>a-b);total++;
        if(new Set(y).size!==y.length){invalid++;continue}
        const ys=subsets(y),e=jitter+.5/rate;
        const narrow=[],wide=[],scores=[];
        for(let i=0;i<8;i++){const pairs=ts[i].flatMap(t=>ys.map(y=>[t,y]));if(pairs.some(([t,y])=>fit(t,y,e)))narrow.push(i);if(pairs.some(([t,y])=>fit(t,y,e+warp)))wide.push(i);scores.push(Math.min(...pairs.map(([t,y])=>Math.abs(ratio(t)-ratio(y)))))}
        const min=Math.min(...scores),near=scores.map((x,i)=>Math.abs(x-min)<=1e-12?i:-1).filter(x=>x>=0);
        decide(nearest,near,id);decide(nominal,narrow,id);decide(envelope,wide,id);
        check(wide.includes(id),"envelope must retain true word");
        if(narrow.length===1&&narrow[0]!==id&&!examples.nominal_wrong)examples.nominal_wrong={seed,id,d,k,scale,off,bend,jitter,receipt:y,picks:narrow,wide};
        if(near.length===1&&near[0]!==id&&!examples.nearest_wrong)examples.nearest_wrong={seed,id,d,k,scale,off,bend,jitter,receipt:y,picks:near,wide};
      }}
      for(const c of [nearest,nominal,envelope])check(c.correct+c.wrong+c.abstain+invalid===total,"accounting");
      check(envelope.wrong===0&&envelope.truth_omitted===0,"envelope invariant");
      if(warp===0)check(JSON.stringify(nominal)===JSON.stringify(envelope),"zero warp equality");
      conditions.push({insert,warp_ms:warp*1000,jitter_ms:jitter*1000,total,invalid,nearest,nominal,envelope,examples});
    }
    results[name]={words,certificates:cert,conditions};
  }
  return {receipt:{source_head:"7beb5383e6fb0700a1daf41f8a5c6c9b3d50dd17",rate,seeds,repeats,checks,results},audio};
}
if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");const out=process.argv[2];if(!out)throw Error("usage: node false-onset.cjs OUTPUT_DIRECTORY");fs.mkdirSync(out,{recursive:true});const {receipt,audio}=run(books);fs.writeFileSync(path.join(out,"false-onset-receipt.json"),JSON.stringify(receipt,null,2)+"\n");for(const [name,bytes] of Object.entries(audio)){fs.writeFileSync(path.join(out,name+"-replacement.wav"),bytes);console.log(name,crypto.createHash("sha256").update(bytes).digest("hex"));}console.log("assertions",receipt.checks);}
module.exports={run,books};
