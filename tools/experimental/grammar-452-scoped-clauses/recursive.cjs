"use strict";
const MHACRecursive = (function recursiveLab(){
"use strict";
const atoms=["fault","open","stopped","overload"],unary=["not","quote","question","verify","pump-reports","relay-reports","uncertain"],binary=["and","if"],end="end";
const vocab=[...atoms,...unary,...binary,end],arity=new Map([...atoms.map(x=>[x,0]),...unary.map(x=>[x,1]),...binary.map(x=>[x,2])]);
const RATE=16000,SLOT=1280,ACTIVE=960,AMP=4096,MAX=128,DEPTH=12,NODES=64;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function encode(tree,mode="closed"){
 if(!["closed","prefix"].includes(mode))throw Error("mode");
 const out=[];let count=0;
 function walk(t,d){if(d>DEPTH||++count>NODES||!Array.isArray(t)||!arity.has(t[0])||t.length!==1+arity.get(t[0]))throw Error("invalid tree");out.push(t[0]);for(const child of t.slice(1))walk(child,d+1);if(mode==="closed"&&t.length>1)out.push(end);}
 walk(tree,0);if(out.length>MAX)throw Error("too long");return out;
}
function decode(tokens,mode="closed"){
 if(!["closed","prefix"].includes(mode)||!Array.isArray(tokens)||tokens.length<1||tokens.length>MAX||tokens.some(t=>!vocab.includes(t)))return {status:"refused"};
 let i=0,count=0;
 function parse(d){if(d>DEPTH||++count>NODES)throw Error("limit");const t=tokens[i++],n=arity.get(t);if(n===undefined)throw Error("expected node");const result=[t];for(let j=0;j<n;j++)result.push(parse(d+1));if(mode==="closed"&&n&&tokens[i++]!==end)throw Error("expected end");return result;}
 try{const tree=parse(0);if(i!==tokens.length)throw Error("trailing symbols");return {status:"ok",tree};}catch(e){return {status:"refused"};}
}
function catalog(max=4){
 if(!Number.isInteger(max)||max<1||max>4)throw Error("catalog bound");
 const levels=[[],atoms.map(a=>[a])];
 for(let n=2;n<=max;n++){const rows=[];for(const u of unary)for(const child of levels[n-1])rows.push([u,child]);for(let l=1;l<n-1;l++)for(const b of binary)for(const x of levels[l])for(const y of levels[n-1-l])rows.push([b,x,y]);levels.push(rows);}
 return levels.flat();
}
const FREQ=vocab.map((_,i)=>400+100*i);
function render(tokens,phase=0){
 if(!Array.isArray(tokens)||!tokens.length||tokens.length>MAX||tokens.some(t=>t!==null&&!vocab.includes(t))||!Number.isFinite(phase))throw Error("invalid render");
 const pcm=new Int16Array(tokens.length*SLOT);
 tokens.forEach((t,i)=>{if(t===null)return;const f=FREQ[vocab.indexOf(t)];for(let n=0;n<ACTIVE;n++)pcm[i*SLOT+n]=Math.round(AMP*Math.min(1,n/80,(ACTIVE-1-n)/80)*Math.sin(2*Math.PI*f*n/RATE+phase));});return pcm;
}
const INNER0=160,INNER1=800,L=INNER1-INNER0;
const templates=FREQ.map(f=>[Float64Array.from({length:L},(_,n)=>Math.cos(2*Math.PI*f*(n+INNER0)/RATE)),Float64Array.from({length:L},(_,n)=>Math.sin(2*Math.PI*f*(n+INNER0)/RATE))]);
function receive(pcm){
 if(!(pcm instanceof Int16Array)||!pcm.length||pcm.length%SLOT||pcm.length/SLOT>MAX)throw Error("requires aligned full slots");
 return Array.from({length:pcm.length/SLOT},(_,i)=>{let e=0;const start=i*SLOT+INNER0;for(let n=0;n<L;n++)e+=pcm[start+n]**2;if(e<AMP*AMP*L*.01)return null;
 const scores=templates.map(([c,s],k)=>{let a=0,b=0;for(let n=0;n<L;n++){a+=pcm[start+n]*c[n];b+=pcm[start+n]*s[n];}return {k,v:2*(a*a+b*b)/(L*e)};}).sort((a,b)=>b.v-a.v);
 return scores[0].v>=.85&&scores[0].v-scores[1].v>=.2?vocab[scores[0].k]:null;});
}
function wav(pcm){const bytes=new Uint8Array(44+pcm.length*2),v=new DataView(bytes.buffer);const s=(i,x)=>{for(let j=0;j<x.length;j++)bytes[i+j]=x.charCodeAt(j);};s(0,"RIFF");v.setUint32(4,bytes.length-8,true);s(8,"WAVE");s(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,RATE,true);v.setUint32(28,RATE*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,"data");v.setUint32(40,pcm.length*2,true);for(let i=0;i<pcm.length;i++)v.setInt16(44+i*2,pcm[i],true);return bytes;}
function examples(){return [
 {name:"negation-outside-quotation",tree:["not",["quote",["fault"]]]},
 {name:"negation-inside-quotation",tree:["quote",["not",["fault"]]]},
 {name:"relay-questions-pump-report",tree:["question",["pump-reports",["fault"]]]},
 {name:"relay-reports-pump-question",tree:["relay-reports",["question",["fault"]]]},
 {name:"conditional-verification",tree:["if",["fault"],["verify",["overload"]]]},
 {name:"uncertain-conjunction",tree:["uncertain",["and",["open"],["stopped"]]]}
 ];}
function qualify(){
 let assertions=0;const check=(v,m)=>{assertions++;if(!v)throw Error(m);};
 const trees=catalog(),metrics={},witnesses={};
 for(const mode of ["prefix","closed"]){
 const m={clean:0,slots:0,deletion:{correct:0,wrong:0,refused:0},substitution:{correct:0,wrong:0,refused:0},knownErasure:{wrong:0,refused:0,correct:0}},seen=new Set();
 const count=(type,out,tree,input,received)=>{const k=out.status!=="ok"?"refused":eq(out.tree,tree)?"correct":"wrong";m[type][k]++;if(k==="wrong"&&!witnesses[mode+"-"+type])witnesses[mode+"-"+type]={tree,input,received,decoded:out.tree};};
 for(const t of trees){const x=encode(t,mode),key=x.join(",");check(!seen.has(key),"collision");seen.add(key);check(eq(decode(x,mode).tree,t),"round trip");m.clean++;m.slots+=x.length;
 for(let i=0;i<x.length;i++){
 const d=x.filter((_,j)=>i!==j),e=x.map((v,j)=>j===i?null:v);
 const rd=decode(d,mode),re=decode(e,mode);count("deletion",rd,t,x,d);count("knownErasure",re,t,x,e);check(re.status==="refused","erasure must refuse");
 if(mode==="closed")check(rd.status==="refused","closed single deletion");
 for(const v of vocab)if(v!==x[i]){const z=x.slice();z[i]=v;count("substitution",decode(z,mode),t,x,z);}
 }}
 metrics[mode]=m;
 }
 let pcmCases=0;const phases=[0,.3,Math.PI/2,Math.PI,5.7],spec=examples();
 for(const mode of ["prefix","closed"])for(const {tree} of spec)for(const p of phases){const x=encode(tree,mode),pcm=render(x,p),got=receive(pcm);check(eq(got,x),"phase invariant");check(eq(decode(got,mode).tree,tree),"PCM roundtrip");check(pcm.every(x=>Math.abs(x)<=AMP),"PCM peak");pcmCases++;
 const erased=x.map((t,i)=>i===1?null:t);check(eq(receive(render(erased,p)),erased),"PCM erasure");check(decode(receive(render(erased,p)),mode).status==="refused","PCM refusal");pcmCases++;}
 const a=encode(spec[0].tree),b=encode(spec[1].tree);check(!eq(a,b),"scope collision");
 const doubleDelete=["not","fault","end"];const removed=doubleDelete.filter(x=>x!=="not"&&x!=="end");check(eq(decode(removed).tree,["fault"]),"double deletion witness");
 const bytes=wav(render(a)),d=new DataView(bytes.buffer);check(d.getUint32(24,true)===RATE&&d.getUint32(40,true)===a.length*SLOT*2,"wav header");
 // Boundary validation and trailing junk rejection.
 check(decode(["fault","end"]).status==="refused","trailing");check(decode(Array(129).fill("fault")).status==="refused","bound");check(decode(["not","fault"]).status==="refused","missing end");check(decode(["and","fault","open","end"]).status==="ok","binary");
 return {schema:"mhac-recursive-clauses-v1",assertions,catalogByNodes:[1,2,3,4].map(n=>catalog(n).length-(n===1?0:catalog(n-1).length)),metrics,pcmCases,phases,slotMs:80,rate:RATE,frequencies:Object.fromEntries(vocab.map((t,i)=>[t,FREQ[i]])),peakLimit:AMP,witnesses,doubleDeletionWitness:{sent:doubleDelete,received:removed,decoded:decode(removed).tree},specimens:spec.map(s=>({...s,closed:encode(s.tree),prefix:encode(s.tree,"prefix")}))};
}
return {vocab,arity,encode,decode,catalog,render,receive,wav,examples,qualify};
})();
module.exports=MHACRecursive;
if(require.main===module){const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"output-recursive";fs.mkdirSync(out,{recursive:true});const result=MHACRecursive.qualify();fs.writeFileSync(path.join(out,"recursive-qualification.json"),JSON.stringify(result,null,2)+"\n");const manifest=[];for(const s of MHACRecursive.examples())for(const mode of ["prefix","closed"]){const tokens=MHACRecursive.encode(s.tree,mode),bytes=MHACRecursive.wav(MHACRecursive.render(tokens)),name=s.name+"-"+mode+".wav";fs.writeFileSync(path.join(out,name),bytes);manifest.push({name,mode,tree:s.tree,tokens,sha256:crypto.createHash("sha256").update(bytes).digest("hex")});}fs.writeFileSync(path.join(out,"stimuli.json"),JSON.stringify(manifest,null,2)+"\n");console.log(JSON.stringify(result,null,2));}
