'use strict';
function laboratory(){
  const modes=["replay","adopt","cite","cite+adopt"];
  const motif=[220,330,275,385];
  function event(parent,mode){
    if(!Number.isInteger(mode)||mode<0||mode>3)throw Error("invalid mode");
    return {parent,mode,cite:!!(mode&2),adopt:!!(mode&1),motif:[...motif]};
  }
  function plan(mode){
    const e=event(null,mode);
    return [...e.motif.map(f=>[f,0]),...[0,1,2,3].map(i=>[165,e.adopt?e.motif[3-i]*2:0])];
  }
  function wav(mode){
    const rate=16000,slot=4000,seq=plan(mode),frames=slot*seq.length;
    const buf=new Uint8Array(44+frames*4),v=new DataView(buf.buffer);
    const str=(off,s)=>{for(let i=0;i<s.length;i++)buf[off+i]=s.charCodeAt(i)};
    str(0,"RIFF");v.setUint32(4,buf.length-8,true);str(8,"WAVE");str(12,"fmt ");
    v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,2,true);v.setUint32(24,rate,true);
    v.setUint32(28,rate*4,true);v.setUint16(32,4,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,frames*4,true);
    for(let s=0;s<seq.length;s++)for(let i=0;i<slot;i++)for(let ch=0;ch<2;ch++){
      const f=seq[s][ch],env=Math.max(0,Math.min(1,i/240,(3400-i)/240));
      const val=f?Math.round(7000*env*(Math.sin(2*Math.PI*f*i/rate)+.18*Math.sin(4*Math.PI*f*i/rate))/1.18):0;
      v.setInt16(44+4*(s*slot+i)+2*ch,val,true);
    }
    return buf;
  }
  function check(){
    let assertions=0, histories=0, inheritedFalseAdoptions=0;
    const assert=(b)=>{assertions++;if(!b)throw Error("test "+assertions)};
    const eq=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
    function walk(path, inherited,depth){
      if(depth===6)return;
      for(let m=0;m<4;m++){
        const prior=path.at(-1)??null,e=event(prior,m),newInherited=inherited||e.adopt;
        histories++;
        assert(e.parent===prior);
        assert(e.cite=== (m>=2));
        assert(e.adopt=== (m%2===1));
        assert(eq(e.motif,motif));
        if(newInherited&&!e.adopt)inheritedFalseAdoptions++;
        walk([...path,e],newInherited,depth+1);
      }
    }
    walk([],false,0);
    assert(histories===5460);assert(inheritedFalseAdoptions===2604);
    const a=modes.map((_,i)=>wav(i));
    for(let i=0;i<4;i++){
      assert(eq(a[i],wav(i)));assert(a[i].length===128044);
      assert(eq(a[0].slice(44,64044),a[i].slice(44,64044)));
      const dv=new DataView(a[i].buffer);
      assert(dv.getUint32(40,true)===128000);
      for(let j=44;j<a[i].length;j+=2)assert(Math.abs(dv.getInt16(j,true))<=7000);
    }
    assert(eq(a[0],a[2]));assert(eq(a[1],a[3]));assert(!eq(a[0],a[1]));
    for(let i=64044;i<a[0].length;i+=4){assert(a[0][i]===a[1][i]&&a[0][i+1]===a[1][i+1]);}
    return {histories,inheritedFalseAdoptions,assertions,recordings:4,framesPerRecording:32000,commonPrefixFrames:16000};
  }
  return {modes,plan,wav,check};
}
const lab=laboratory();
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const receipt=lab.check(); console.log(JSON.stringify(receipt,null,2));
 if(process.argv[2]){const out=process.argv[2];fs.mkdirSync(out,{recursive:true});for(let i=0;i<4;i++)fs.writeFileSync(path.join(out,lab.modes[i]+'.wav'),lab.wav(i));fs.writeFileSync(path.join(out,'receipt.txt'),JSON.stringify(receipt,null,2)+'\n');}
}
module.exports=lab;
