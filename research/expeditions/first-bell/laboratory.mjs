// Original synthetic laboratory, MHAC #284. Node 18+; no dependencies.
import {writeFileSync,mkdirSync} from "node:fs";
import {join} from "node:path";
function render(counts, positives, paired=false) {
  const rows=[];
  for(let mask=0;mask<4;mask++)for(let j=0;j<counts[mask];j++)rows.push([mask,j<positives[mask]?1:0]);
  const rate=8000, frames=800, channels=paired?2:1, length=rows.length*2*frames*channels*2;
  const bytes=new Uint8Array(44+length), d=new DataView(bytes.buffer);
  const txt=(offset,s)=>{for(let i=0;i<s.length;i++)bytes[offset+i]=s.charCodeAt(i)};
  txt(0,"RIFF");d.setUint32(4,36+length,true);txt(8,"WAVE");txt(12,"fmt ");d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,channels,true);d.setUint32(24,rate,true);d.setUint32(28,rate*channels*2,true);d.setUint16(32,channels*2,true);d.setUint16(34,16,true);txt(36,"data");d.setUint32(40,length,true);
  function tone(i,f) {
    let x=(i*f)%rate, tri=rate-4*Math.abs(x-rate/2);
    return Math.trunc(tri*4500*Math.min(i,frames-1-i,64)/(rate*64));
  }
  let offset=44;
  for(const [mask,y] of rows)for(let t=0;t<2;t++)for(let i=0;i<frames;i++){
    d.setInt16(offset,tone(i,(mask>>t)&1?500:450),true);offset+=2;
    if(paired){d.setInt16(offset,tone(i,y?740:260),true);offset+=2;}
  }
  return bytes;
}
function experiment() {
 const assert=(x,msg)=>{if(!x)throw Error(msg)};
 const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
 const gcd=(a,b)=>b?gcd(b,a%b):a;
 const ratio=(a,b)=>{const g=gcd(a,b);return `${a/g}/${b/g}`};
 const cmp=(a,b)=>a[0]*b[1]-b[0]*a[1];
 const eq=(a,b)=>cmp(a,b)===0;
 const census=[];
 for(let n=2;n<=7;n++){
  let cases=0,groups=0,biased=0,strictBoth=0,attainsUniversalLo=0,attainsUniversalHi=0,checks=0;
  for(let k=1;k<n;k++){
   let pos=(1<<k)-1,all=(1<<n)-1,by=new Map(), extrema=new Map();
   for(let mask=1;mask<=all;mask++){
    let a=pop(mask&pos),b=pop(mask&(all^pos));if(!a||!b)continue;
    const p=ratio(a,a+b);
    if(!by.has(p))by.set(p,[]);
    by.get(p).push({mask,a,b});
   }
   for(const list of by.values())for(const x of list)for(const y of list)for(const z of list){
    const A=x.a+y.a+z.a,B=x.b+y.b+z.b;
    const alo=Math.max(x.a,y.a,z.a),ahi=Math.min(k,A),blo=Math.max(x.b,y.b,z.b),bhi=Math.min(n-k,B);
    const u=x.mask|y.mask|z.mask, a=pop(u&pos),b=pop(u&(all^pos)),q=[a,a+b],p=[x.a,x.a+x.b];
    const lo=[alo,alo+bhi],hi=[ahi,ahi+blo],ulo=[x.a,x.a+3*x.b],uhi=[3*x.a,3*x.a+x.b];
    assert(cmp(q,lo)>=0&&cmp(q,hi)<=0&&cmp(q,ulo)>=0&&cmp(q,uhi)<=0,"union bound");checks+=4;
    assert(A*(x.a+x.b)===x.a*(A+B),"pooled occurrence calibration");
    // Exact covariance identity: E[YK]-E[Y]E[K] = (p-r)E[K].
    assert((A*(a+b)-a*(A+B))*(x.a+x.b)===(x.a*(a+b)-a*(x.a+x.b))*(A+B),"covariance");
    checks+=2;cases++;if(!eq(q,p))biased++;
    if(eq(q,ulo))attainsUniversalLo++;
    if(eq(q,uhi))attainsUniversalHi++;
    const key=[x.a,x.b,y.a,y.b,z.a,z.b].join(",");
    let g=extrema.get(key);
    if(!g){g={min:q,max:q,lo,hi,p};extrema.set(key,g);}
    if(cmp(q,g.min)<0)g.min=q;
    if(cmp(q,g.max)>0)g.max=q;
   }
   for(const g of extrema.values()){
    assert(eq(g.min,g.lo)&&eq(g.max,g.hi),"sharp cohort bound");checks+=2;groups++;
    if(cmp(g.min,g.p)<0&&cmp(g.max,g.p)>0)strictBoth++;
   }
  }
  census.push({n,cases,groups,biased,strictBoth,attainsUniversalLo,attainsUniversalHi,checks});
 }
 // Enumerate every two-tick trace table with 0..4 cases per trace cell.
 // Each cell is subdivided into positives and negatives; no row permutations.
 let tables=0,valid=0;const traces=new Map();
 for(let c0=0;c0<=4;c0++)for(let c1=0;c1<=4;c1++)for(let c2=0;c2<=4;c2++)for(let c3=0;c3<=4;c3++){
  let c=[c0,c1,c2,c3],N=c0+c1+c2+c3,h1=c1+c3,h2=c2+c3,H=N-c0;
  for(let z0=0;z0<=c0;z0++)for(let z1=0;z1<=c1;z1++)for(let z2=0;z2<=c2;z2++)for(let z3=0;z3<=c3;z3++){
   tables++;let M=z0+z1+z2+z3,a1=z1+z3,a2=z2+z3;
   if(!h1||!h2||h1===N||h2===N||!a1||a1===h1||a1*h2!==a2*h1||M*h1===a1*N)continue;
   valid++;
   // z3 free; the four cell capacity inequalities give this interval.
   const L=Math.max(0,a1-c1,a2-c2,a1+a2-M);
   const U=Math.min(c3,a1,a2,c0+a1+a2-M);
   assert(z3>=L&&z3<=U,"trace bounds");
   const key=[...c,M,a1,a2].join(",");
   const g=traces.get(key)??{min:z3,max:z3,L,U,a1,a2,H,p:[a1,h1]};
   g.min=Math.min(g.min,z3);g.max=Math.max(g.max,z3);traces.set(key,g);
  }
 }
 let opposite=0,nonidentified=0;
 for(const g of traces.values()){
   assert(g.min===g.L&&g.max===g.U,"sharp trace interval");
   if(g.min!==g.max)nonidentified++;
   if(cmp([g.a1+g.a2-g.max,g.H],g.p)<0&&cmp([g.a1+g.a2-g.min,g.H],g.p)>0)opposite++;
 }
 // Exact stopping control: all 256 terminal outcome assignments on 8 equiprobable leaves.
 let controlChecks=0;
 for(let labels=0;labels<256;labels++){
  let groups=new Map();
  for(let i=0;i<8;i++){
   let t,p;
   for(t=1;t<=3;t++){
    const size=8>>t,start=Math.floor(i/size)*size;
    p=[pop(labels&(((1<<size)-1)<<start)),size];
    if(p[0]*2===p[1]||t===3)break;
   }
   const key=t+":"+ratio(...p),g=groups.get(key)??[0,0,p];
   g[0]+=(labels>>i)&1;g[1]++;groups.set(key,g);
  }
  for(const [a,b,p] of groups.values()){assert(eq([a,b],p),"posterior stopping control");controlChecks++}
 }
 const c=[4,4,4,4],zHigh=[0,3,3,1],zLow=[3,0,0,4];
 const hi=render(c,zHigh),lo=render(c,zLow),hp=render(c,zHigh,true),lp=render(c,zLow,true);
 const equal=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
 const fingerprint=a=>{let h=2166136261;for(const b of a)h=Math.imul(h^b,16777619);return (h>>>0).toString(16).padStart(8,"0")};
 assert(equal(hi,lo)&&!equal(hp,lp),"PCM contrast");
 return {census,traceCensus:{tables,valid,groups:traces.size,nonidentified,opposite},historyPosteriorControl:{assignments:256,checks:controlChecks},witness:{counts:c,positiveHigh:zHigh,positiveLow:zLow,selectedHigh:"7/12",selectedLow:"4/12",p:"1/2",other:"3/8"},audio:{publicHigh:{bytes:hi.length,fnv1a:fingerprint(hi)},publicLow:{bytes:lo.length,fnv1a:fingerprint(lo)},pairedHigh:{bytes:hp.length,fnv1a:fingerprint(hp)},pairedLow:{bytes:lp.length,fnv1a:fingerprint(lp)},publicEqual:true,pairedEqual:false}};
}
const receipt=experiment();
if(process.argv[2]){const dir=process.argv[2];mkdirSync(dir,{recursive:true});const {counts,positiveHigh,positiveLow}=receipt.witness;for(const [name,z] of [["high",positiveHigh],["low",positiveLow]])for(const paired of [false,true])writeFileSync(join(dir,name+(paired?"-paired":"-public")+".wav"),render(counts,z,paired));}
console.log(JSON.stringify(receipt,null,2));
