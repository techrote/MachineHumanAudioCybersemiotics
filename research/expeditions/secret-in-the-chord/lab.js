#!/usr/bin/env node
// MHAC #218: original finite synthetic laboratory. No external dependencies.
function laboratory(){
  "use strict";
  const assert=(ok,msg)=>{if(!ok)throw new Error(msg)};
  // All masses are nonnegative integer counts on a common denominator.
  function table(n,a,b,t){
    assert([n,a,b,t].every(Number.isSafeInteger)&&n>0&&a>=0&&b>=0&&a<=n&&b<=n,"invalid margins");
    assert(t>=Math.max(0,a+b-n)&&t<=Math.min(a,b),"infeasible coupling");
    return [n-a-b+t,b-t,a-t,t]; // order 00,01,10,11
  }
  function tvNumerator(x,y){
    assert(x.length===y.length&&x.every(v=>Number.isSafeInteger(v)&&v>=0)&&y.every(v=>Number.isSafeInteger(v)&&v>=0),"invalid counts");
    const sum=z=>z.reduce((a,b)=>a+b,0);
    assert(sum(x)>0&&sum(x)===sum(y),"unequal total mass");
    return x.reduce((s,v,i)=>s+Math.abs(v-y[i]),0); // denominator 2*total
  }
  function marginals(x){return [x[2]+x[3],x[1]+x[3]]}
  function independentTable(n,a,b){
    return [(n-a)*(n-b),(n-a)*b,a*(n-b),a*b]; // denominator n^2
  }
  function parity(x){let s=0;while(x){s^=x&1;x>>>=1;}return s}
  function parityProjection(n,mask,secret){
    assert(Number.isInteger(n)&&n>=2&&n<=12&&Number.isInteger(mask)&&mask>=0&&mask<(1<<n)&&(secret===0||secret===1),"invalid parity inputs");
    const c=Array(1<<n).fill(0);
    for(let v=0;v<(1<<n);v++)if(parity(v)===secret)c[v&mask]++;
    return c;
  }
  // Independent construction: enumerate every nonnegative four-cell table
  // and group by its margins, without using the coupling parameterization.
  function enumerateTables(n){
    const groups=new Map();
    for(let a=0;a<=n;a++)for(let b=0;b<=n-a;b++)for(let c=0;c<=n-a-b;c++){
      const x=[a,b,c,n-a-b-c], key=marginals(x).join(",");
      if(!groups.has(key))groups.set(key,[]);
      groups.get(key).push(x);
    }
    return groups;
  }
  // Original stereo chord, not a model of auditory perception. 16-bit PCM,
  // one second; independently rendered channel oscillators, fixed envelope.
  function pcm(left,right,rate=8000){
    assert([left,right].every(x=>x===0||x===1)&&Number.isInteger(rate)&&rate>=8000&&rate<=48000,"invalid PCM parameters");
    const frames=rate, bytes=new Uint8Array(44+frames*4), dv=new DataView(bytes.buffer);
    const ascii=(offset,s)=>{for(let i=0;i<s.length;i++)bytes[offset+i]=s.charCodeAt(i)};
    ascii(0,"RIFF");dv.setUint32(4,bytes.length-8,true);ascii(8,"WAVE");ascii(12,"fmt ");
    dv.setUint32(16,16,true);dv.setUint16(20,1,true);dv.setUint16(22,2,true);dv.setUint32(24,rate,true);
    dv.setUint32(28,rate*4,true);dv.setUint16(32,4,true);dv.setUint16(34,16,true);ascii(36,"data");dv.setUint32(40,frames*4,true);
    const freqs=[220+110*left,440+220*right];
    for(let i=0;i<frames;i++){
      const e=Math.min(1,i/160,(frames-1-i)/160);
      for(let ch=0;ch<2;ch++)dv.setInt16(44+i*4+ch*2,Math.round(10000*e*Math.sin(2*Math.PI*freqs[ch]*i/rate)),true);
    }
    return bytes;
  }
  function channel(bytes,ch){const d=new DataView(bytes.buffer);return Array.from({length:(bytes.length-44)/4},(_,i)=>d.getInt16(44+4*i+2*ch,true))}
  function equal(a,b){return a.length===b.length&&a.every((x,i)=>x===b[i])}
  function run(){
    let comparisons=0,marginGroups=0,tablePairs=0,parityChecks=0,independenceChecks=0;
    for(let n=1;n<=12;n++){
      const groups=enumerateTables(n);
      for(const [key,rows] of groups){
        const [a,b]=key.split(",").map(Number), lo=Math.max(0,a+b-n),hi=Math.min(a,b),w=Math.min(a,n-a,b,n-b);
        assert(hi-lo===w,"width identity");
        assert(rows.length===hi-lo+1,"missing coupling");
        marginGroups++;
        let max=0;
        for(const x of rows){
          assert(equal(x,table(n,a,b,x[3])),"table mismatch");
          for(const y of rows){
            const v=tvNumerator(x,y);
            assert(v===4*Math.abs(x[3]-y[3]),"TV identity");
            assert(v<=4*w,"bound failed");
            max=Math.max(max,v);tablePairs++;comparisons++;
          }
        }
        assert(max===4*w&&tvNumerator(table(n,a,b,lo),table(n,a,b,hi))===max,"sharpness failed");
        // Negative control: the conditionally independent joint distribution
        // is uniquely fixed by its margins, independent of the secret.
        const z=independentTable(n,a,b);
        assert(equal(marginals(z),[n*a,n*b]),"independence margin mismatch");
        assert(tvNumerator(z,z)===0,"identical joint control");independenceChecks++;
      }
    }
    for(let n=2;n<=8;n++)for(let m=0;m<(1<<n);m++){
      const x=parityProjection(n,m,0),y=parityProjection(n,m,1),total=1<<(n-1);
      assert(x.reduce((a,b)=>a+b,0)===total&&y.reduce((a,b)=>a+b,0)===total,"parity mass");
      const expected=m===(1<<n)-1?2*total:0;
      assert(tvNumerator(x,y)===expected,"parity projection failure");
      parityChecks++;comparisons++;
    }
    let refused=0;
    for(const bad of [()=>table(4,2,2,3),()=>table(4,-1,2,0),()=>tvNumerator([1,0],[0,2]),()=>parityProjection(3,8,0),()=>pcm(2,0)]){
      try{bad()}catch(e){refused++}
    }
    assert(refused===5,"malformed inputs not refused");
    const w00=pcm(0,0),w01=pcm(0,1),w10=pcm(1,0),w11=pcm(1,1);
    assert(equal(channel(w00,0),channel(w01,0))&&equal(channel(w10,0),channel(w11,0)),"left isolation failure");
    assert(equal(channel(w00,1),channel(w10,1))&&equal(channel(w01,1),channel(w11,1)),"right isolation failure");
    assert(!equal(channel(w00,0),channel(w10,0))&&!equal(channel(w00,1),channel(w01,1)),"distinct acoustic symbols required");
    assert(w00.length===32044&&new DataView(w00.buffer).getUint32(40,true)===32000,"WAV size");
    return {schema:"mhac-secret-in-the-chord-v1",comparisons,marginGroups,tablePairs,parityChecks,independenceChecks,refused,pcmChecks:"passed",examples:[
      {n:4,a:2,b:2,low:table(4,2,2,0),high:table(4,2,2,2),tvNumerator:8,tvDenominator:8},
      {n:4,a:1,b:2,low:table(4,1,2,0),high:table(4,1,2,1),tvNumerator:4,tvDenominator:8},
      {n:4,a:0,b:2,low:table(4,0,2,0),high:table(4,0,2,0),tvNumerator:0,tvDenominator:8}
    ]};
  }
  return {run,pcm,table,tvNumerator,parityProjection};
}
const lab = laboratory();
if (typeof module !== 'undefined') module.exports = lab;
if (typeof require !== 'undefined' && require.main === module) {
  console.log(JSON.stringify(lab.run(), null, 2));
  if (process.argv[2] === '--wav-dir') {
    if (!process.argv[3]) throw new Error('Specify output directory');
    const fs = require('node:fs'), path = require('node:path');
    fs.mkdirSync(process.argv[3], {recursive:true});
    for (let a=0;a<2;a++) for(let b=0;b<2;b++) fs.writeFileSync(path.join(process.argv[3], `chord-${a}${b}.wav`),lab.pcm(a,b));
  }
}
