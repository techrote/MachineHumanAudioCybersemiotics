"use strict";
// Synthetic grammar experiment, Refs #452. No human or operational claims.
const R=require("./recursive.cjs");
const MOD=17,N=8,RATE=16000,SLOT=1280,ACTIVE=960,AMP=4096,PAD=13;
const mod=x=>((x%MOD)+MOD)%MOD;
const vocab=[...R.vocab,"check14","check15","check16"];
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const refuse=()=>({status:"refused"});
const valid=x=>Number.isInteger(x)&&x>=0&&x<MOD;
const inv=x=>{for(let i=1;i<MOD;i++)if(mod(x*i)===1)return i;throw Error("zero inverse");};
function synd(x){return [mod(x.reduce((s,v)=>s+v,0)),mod(x.reduce((s,v,i)=>s+v*(i+1),0))];}
function encode(tree,mode){
 if(!["closed","protected"].includes(mode))throw Error("mode");
 const t=R.encode(tree,mode==="closed"?"closed":"prefix").map(v=>vocab.indexOf(v));
 const slots=mode==="closed"?7:5;
 if(t.length>slots||R.encode(tree,"prefix").length>4)throw Error("four-node bound");
 const x=[t.length-1,...t,...Array(slots-t.length).fill(PAD)];
 if(mode==="protected"){const [a,b]=synd(x),q=mod(7*a-b);x.push(mod(-a-q),q);}
 return x;
}
function decode(input,mode){
 if(!["closed","protected"].includes(mode)||!Array.isArray(input)||input.length!==N||input.some(v=>v!==null&&!valid(v)))return refuse();
 const x=input.slice(),missing=x.map((v,i)=>v===null?i:-1).filter(i=>i>=0);
 if(mode==="closed"&&missing.length||missing.length>2)return refuse();
 if(mode==="protected"){
  const [a,b]=synd(x.map(v=>v===null?0:v));
  if(missing.length===1)x[missing[0]]=mod(-a);
  if(missing.length===2){const [i,j]=missing;const q=mod(((i+1)*a-b)*inv(j-i));x[i]=mod(-a-q);x[j]=q;}
  if(synd(x).some(v=>v!==0))return refuse();
 }
 const slots=mode==="closed"?7:5,len=x[0]+1;
 if(len>slots||x.slice(1+len,1+slots).some(v=>v!==PAD))return refuse();
 const t=R.decode(x.slice(1,1+len).map(v=>vocab[v]),mode==="closed"?"closed":"prefix");
 if(t.status!=="ok"||R.encode(t.tree,"prefix").length>4)return refuse();
 return {status:"ok",tree:t.tree,recovered:missing};
}
const freqs=vocab.map((_,i)=>400+i*100);
function render(x,phase=0){
 if(x.length!==N||x.some(v=>v!==null&&!valid(v)))throw Error("frame");
 const pcm=new Int16Array(N*SLOT);
 x.forEach((v,i)=>{if(v!==null)for(let n=0;n<ACTIVE;n++)pcm[i*SLOT+n]=Math.round(AMP*Math.min(1,n/80,(ACTIVE-1-n)/80)*Math.sin(2*Math.PI*freqs[v]*n/RATE+phase));});
 return pcm;
}
const L=640,START=160;
const bank=freqs.map(f=>[Float64Array.from({length:L},(_,n)=>Math.cos(2*Math.PI*f*(n+START)/RATE)),Float64Array.from({length:L},(_,n)=>Math.sin(2*Math.PI*f*(n+START)/RATE))]);
function receive(pcm){
 if(!(pcm instanceof Int16Array)||pcm.length!==N*SLOT)throw Error("aligned frame required");
 return Array.from({length:N},(_,i)=>{const s=i*SLOT+START;let e=0;for(let j=0;j<L;j++)e+=pcm[s+j]**2;if(e<AMP*AMP*L*.01)return null;
 const scores=bank.map(([c,t],k)=>{let a=0,b=0;for(let j=0;j<L;j++){a+=pcm[s+j]*c[j];b+=pcm[s+j]*t[j];}return {k,z:2*(a*a+b*b)/(L*e)};}).sort((a,b)=>b.z-a.z);
 return scores[0].z>=.85&&scores[0].z-scores[1].z>=.2?scores[0].k:null;});
}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const trees=R.catalog(),metrics={},witnesses={},books={},phases=[0,.3,1.7,4.1],pcm={cases:0,energy:{},peak:0};
 for(const mode of ["closed","protected"]){
  const book=trees.map(t=>encode(t,mode));books[mode]=book;
  const seen=new Set(book.map(x=>x.join(",")));check(seen.size===trees.length,"collision");
  const mm={clean:0,deletion:{correct:0,wrong:0,refused:0},singleSub:{correct:0,wrong:0,refused:0},singleErase:{correct:0,wrong:0,refused:0},doubleErase:{correct:0,wrong:0,refused:0}};
  function test(kind,k,y){const d=decode(y,mode),status=d.status!=="ok"?"refused":eq(d.tree,trees[k])?"correct":"wrong";mm[kind][status]++;if(status==="wrong"&&!witnesses[mode+"-"+kind])witnesses[mode+"-"+kind]={sent:trees[k],input:book[k],received:y,decoded:d.tree};return status;}
  for(let k=0;k<book.length;k++){const x=book[k];check(eq(decode(x,mode).tree,trees[k]),"clean");mm.clean++;
   for(let i=0;i<N;i++){
    check(test("deletion",k,x.filter((_,j)=>j!==i))==="refused","length");
    const e=x.slice();e[i]=null;check(test("singleErase",k,e)===(mode==="protected"?"correct":"refused"),"erasure");
    for(let j=i+1;j<N;j++){const z=e.slice();z[j]=null;check(test("doubleErase",k,z)===(mode==="protected"?"correct":"refused"),"two erasures");}
    for(let v=0;v<MOD;v++)if(v!==x[i]){const z=x.slice();z[i]=v;const status=test("singleSub",k,z);if(mode==="protected")check(status==="refused","one substitution");}
   }
  }
  metrics[mode]=mm;
 }
 // Independent pair census: distance of the actual finite codebooks.
 const distance={};
 for(const mode of ["closed","protected"]){const book=books[mode],hist=Array(9).fill(0);let closest=null;
  for(let i=0;i<book.length;i++)for(let j=i+1;j<book.length;j++){let d=0;for(let k=0;k<N;k++)d+=book[i][k]!==book[j][k]?1:0;hist[d]++;if(!closest||d<closest.d)closest={d,i,j};}
  check(hist[0]===0,"unique");if(mode==="protected")check(closest.d>=3,"distance");distance[mode]={hist,closest};
 }
 // Construct exact mixed-corruption witness from minimum-distance pair.
 const {i,j,d}=distance.protected.closest,a=books.protected[i],b=books.protected[j],diff=a.map((v,k)=>v===b[k]?-1:k).filter(k=>k>=0);
 check(d===3,"expected distance 3");const corrupt=a.slice();corrupt[diff[0]]=null;for(const k of diff.slice(1))corrupt[k]=b[k];
 check(eq(decode(corrupt,"protected").tree,trees[j]),"mixed corruption witness");
 witnesses.mixed={sent:trees[i],target:trees[j],input:a,targetFrame:b,received:corrupt,decoded:decode(corrupt,"protected").tree};
 const examples=R.examples().filter(s=>R.encode(s.tree,"prefix").length<=4);
 for(const mode of ["closed","protected"]){let min=Infinity,max=0;
  for(const s of examples)for(const p of phases){const x=encode(s.tree,mode),wave=render(x,p),got=receive(wave);
   check(eq(got,x),"PCM tokens");check(eq(decode(got,mode).tree,s.tree),"PCM clean");let en=0;for(const v of wave){en+=v*v;pcm.peak=Math.max(pcm.peak,Math.abs(v));}min=Math.min(min,en);max=Math.max(max,en);pcm.cases++;
   const z=x.slice();z[1]=null;z[6]=null;const er=receive(render(z,p));check(eq(er,z),"PCM erase");check(mode==="protected"?eq(decode(er,mode).tree,s.tree):decode(er,mode).status==="refused","PCM erase outcome");pcm.cases++;
  }pcm.energy[mode]={min,max};
 }
 check(pcm.peak<=AMP,"peak");
 return {schema:"mhac-matched-integrity-v1",source:"4bed9abcb2343129c265cbfeb7d5cd0341eeaf6b",assertions,trees:trees.length,slots:N,slotMs:80,rate:RATE,frequencies:freqs,metrics,distance,witnesses,pcm,phases,examples:examples.map(s=>({...s,closed:encode(s.tree,"closed"),protected:encode(s.tree,"protected")}))};
}
module.exports={encode,decode,render,receive,qualify,vocab,synd};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),dir=process.argv[2]||"output-integrity";fs.mkdirSync(dir,{recursive:true});
 const q=qualify(),manifest=[];function save(name,frame){const data=R.wav(render(frame));fs.writeFileSync(path.join(dir,name),data);manifest.push({name,frame,sha256:crypto.createHash("sha256").update(data).digest("hex")});}
 for(const s of q.examples)for(const mode of ["closed","protected"])save(s.name+"-"+mode+".wav",s[mode]);
 save("mixed-corruption.wav",q.witnesses.mixed.received);
 fs.writeFileSync(path.join(dir,"integrity-qualification.json"),JSON.stringify(q,null,2)+"\n");fs.writeFileSync(path.join(dir,"integrity-stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify({assertions:q.assertions,metrics:q.metrics,pcm:q.pcm},null,2));
}
