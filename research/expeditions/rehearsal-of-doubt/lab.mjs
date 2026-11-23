function model(n,kind="private"){
 if(!Number.isInteger(n)||n<0||n>64||!["private","public"].includes(kind))throw Error("bad model");
 const worlds=Array.from({length:n+2},(_,i)=>i-1);
 const obs=(w,i)=>kind==="public"?(w===-1?"absent":"present"):
 i===0?(w===-1?"absent":"a"+Math.floor(w/2)):
 "b"+Math.floor((w+1)/2);
 return {worlds,obs,truth:new Set(worlds.filter(w=>w>=0)),kind,n};
}

function know(m,i,S){return new Set(m.worlds.filter(w=>m.worlds.every(v=>m.obs(v,i)!==m.obs(w,i)||S.has(v))))}

function everyone(m,S){const a=know(m,0,S),b=know(m,1,S);return new Set([...a].filter(w=>b.has(w)))}

function layers(m){const out=[m.truth];for(let i=0;i<=m.worlds.length;i++){const next=everyone(m,out.at(-1));if(next.size===out.at(-1).size)return out;out.push(next)}throw Error("failed fixed point")}

function depth(m,w){const l=layers(m);if(l.at(-1).has(w))return "common";return l.findLastIndex(s=>s.has(w))}

function policies(m){
 const keys=[0,1].map(i=>[...new Set(m.worlds.map(w=>m.obs(w,i)))]);
 const k=keys[0].length+keys[1].length;if(k>22)throw Error("exhaustive policy budget");
 let joint=0,safe=0,nontrivial=0;
 for(let mask=0;mask<2**k;mask++){
  const play=(w,i)=>Boolean(mask&(1<<(keys[i].indexOf(m.obs(w,i))+(i?keys[0].length:0))));
  if(!m.worlds.every(w=>play(w,0)===play(w,1)))continue;
  joint++;if(play(-1,0))continue;
  safe++;if(m.worlds.some(w=>w>=0&&play(w,0)))nontrivial++;
 }
 return {local_bits:k,candidates:2**k,joint,safe,nontrivial};
}

function render(m,w){
 if(!m.worlds.includes(w))throw Error("invalid world");
 const known=[0,1].map(i=>know(m,i,m.truth).has(w));
 const rate=16000,frames=rate*2,buf=new Uint8Array(44+frames*4),v=new DataView(buf.buffer);
 const str=(o,s)=>{for(let i=0;i<s.length;i++)buf[o+i]=s.charCodeAt(i)};
 str(0,"RIFF");v.setUint32(4,buf.length-8,true);str(8,"WAVE");str(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,2,true);v.setUint32(24,rate,true);v.setUint32(28,rate*4,true);v.setUint16(32,4,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,frames*4,true);
 for(let t=0;t<frames;t++){const j=t%8000,amp=j<3200?Math.min(6000,j*30,(3200-j)*30):0;const s=Math.floor(t/20)%2?amp:-amp;
 for(let i=0;i<2;i++)v.setInt16(44+4*t+2*i,known[i]?s:0,true)}
 return buf;
}

function runTests(){
 let count=0;const check=(p,msg)=>{count++;if(!p)throw Error(msg)};
 for(let n=0;n<=32;n++){
  const m=model(n),l=layers(m),pub=model(n,"public");
  for(const w of m.worlds){
   check(depth(m,w)===w,"private depth");
   check(depth(pub,w)===(w<0?-1:"common"),"public depth");
   for(let i=0;i<2;i++){
    const s=know(m,i,m.truth);check(!s.has(-1),"factivity");
    check([...know(m,i,s)].join() === [...s].join(),"positive introspection");
   }
   for(let d=0;d<l.length;d++)check(l[d].has(w)===(w>=d),"layer formula");
  }
  check(l.at(-1).size===0,"no common knowledge");
  if(n<=10){const q=policies(m),p=policies(pub);check(q.joint===2&&q.safe===1&&q.nontrivial===0,"private policies");check(p.joint===4&&p.safe===2&&p.nontrivial===1,"public policies")}
 }
 const m=model(8),pub=model(8,"public"),a=render(m,8),b=render(pub,8),c=render(m,0),z=render(m,-1);
 check(a.length===128044,"wav size");check(a.every((x,i)=>x===b[i]),"same rendered score");
 const av=new DataView(a.buffer),cv=new DataView(c.buffer),zv=new DataView(z.buffer);
 let active=false;for(let o=44;o<a.length;o+=4){check(av.getInt16(o,true)===av.getInt16(o+2,true),"unison");check(cv.getInt16(o,true)===av.getInt16(o,true)&&cv.getInt16(o+2,true)===0,"solo control");check(zv.getInt16(o,true)===0&&zv.getInt16(o+2,true)===0,"silence control");if(av.getInt16(o,true))active=true}
 check(active,"nontrivial audio");
 return {assertions:count,chain_lengths:[0,32],policy_enumeration_max:10,private_n8:policies(m),public_n8:policies(pub),pcm_bytes:a.length,identical_unison:true};
}

// Node 22+ CLI. No dependencies. Run with node lab.mjs [output_directory].
import {mkdirSync,writeFileSync} from "node:fs";
import {join} from "node:path";
const result=runTests();
console.log(JSON.stringify(result,null,2));
if(process.argv[2]){const out=process.argv[2];mkdirSync(out,{recursive:true});for(const [name,kind,w] of [["private-unison","private",8],["public-unison","public",8],["private-solo","private",0],["absent","private",-1]])writeFileSync(join(out,name+".wav"),render(model(8,kind),w));writeFileSync(join(out,"results.json"),JSON.stringify(result,null,2)+"\n")}
