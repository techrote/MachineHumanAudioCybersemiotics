// Exact nonnegative common-filter laboratory; synthetic only.
function run(){
  const check=(x,label)=>{if(!x)throw Error(label);};
  const P=(...x)=>x.map(BigInt),one=P(1);
  const mul=(a,b)=>{const c=Array(a.length+b.length-1).fill(0n);
    for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)c[i+j]+=a[i]*b[j];return c;};
  const prod=xs=>xs.reduce(mul,one),sum=a=>a.reduce((s,x)=>s+x,0n);
  const powers=(p,n)=>{const a=[one];for(let i=0;i<n;i++)a.push(mul(a[i],p));return a;};
  const eq=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
  const normEq=(a,b)=>a.length===b.length&&a.every((x,i)=>x*sum(b)===b[i]*sum(a));
  const pos=a=>a.every(x=>x>=0n),strict=a=>a.every(x=>x>0n);
  // Long division, independent of the exponent-vector quotient construction.
  function divide(a,b){
    if(a.length<b.length)return null;
    const rem=a.slice(),q=Array(a.length-b.length+1).fill(0n),lead=b.at(-1);
    for(let j=q.length-1;j>=0;j--){
      if(rem[j+b.length-1]%lead!==0n)return null;
      q[j]=rem[j+b.length-1]/lead;
      for(let i=0;i<b.length;i++)rem[i+j]-=q[j]*b[i];
    }
    return rem.every(x=>x===0n)?q:null;
  }
  function* vectors(m,k,p=[]){
    if(!m){yield p;return;}
    for(let i=0;i<=k;i++)yield* vectors(m-1,k,[...p,i]);
  }
  const choose=(n,k)=>{let x=1;for(let j=1;j<=k;j++)x=x*(n-j+1)/j;return x;};
  function family(ps,k,strictMode){
    const m=ps.length,t=(m-1)*k;
    const q=strictMode?P(2*t,-(2*t-1),2*t):P(1,-1,1);
    const pp=ps.map(p=>powers(p,k)),g=prod(pp.map(p=>p[k])),y=mul(g,powers(q,t)[t]);
    check(pos(g)&&pos(y),'valid observations');
    if(strictMode)check(strict(g)&&strict(y),'strict observations');
    let total=0,feasible=0,maximal=0,strictFeasible=0,negative=0;
    for(const v of vectors(m,k)){
      const s=v.reduce((a,b)=>a+b,0),h=prod(v.map((e,i)=>pp[i][e]));
      const a=divide(g,h),b=divide(y,h);
      check(a&&b&&eq(mul(a,h),g)&&eq(mul(b,h),y),'exact division/reassembly');
      const ok=pos(h)&&pos(a)&&pos(b);
      check(ok===(s<=k),'simplex equivalence');
      if(ok){
        feasible++;
        if(strict(h)&&strict(a)&&strict(b))strictFeasible++;
        if(s===k)maximal++;
        check(h.length===2*s+1,'degree');
        if(s)check(h[1]===BigInt(s)*h[0],'early ratio');
      }else{negative++;check(b[1]<0n,'negative first-lag certificate');}
      total++;
    }
    check(feasible===choose(m+k,m),'feasible count');
    check(maximal===choose(m+k-1,m-1),'maximal count');
    if(strictMode)check(strictFeasible===feasible,'strict factors');
    return {m,k,strictMode,total,feasible,maximal,strictFeasible,negative};
  }
  const rows=[];
  for(let m=2;m<=5;m++)for(let k=1;k<=5;k++){
    const ps=Array.from({length:m},(_,i)=>P(4*m,4*m,m+i+1));
    for(const strictMode of [false,true])rows.push(family(ps,k,strictMode));
  }
  // Equal normalized first two taps, unequal third tap.
  const ps=[P(5,5,2),P(25,25,16),P(125,125,113)];
  const probeFamily=family(ps,2,true),hA=mul(ps[0],ps[2]),hB=mul(ps[1],ps[1]);
  const cross=(a,b,i)=>a[i]*sum(b)-b[i]*sum(a);
  check(hA.length===hB.length&&cross(hA,hB,0)===0n&&cross(hA,hB,1)===0n,'two-tap alias');
  check(cross(hA,hB,2)!==0n&&!normEq(hA,hB),'third tap separates');
  const p=P(1,1,1),r=P(2,2,1),q=P(1,-1,1);
  const observations=[mul(mul(p,r),q),mul(p,r)];
  const aSources=[mul(r,q),r],bSources=[mul(p,q),p];
  const aObs=aSources.map(s=>mul(p,s)),bObs=bSources.map(s=>mul(r,s));
  check(aObs.every((v,i)=>eq(v,bObs[i])&&eq(v,observations[i])),'observational alias');
  check(!normEq(p,r)&&pos(mul(p,q))&&pos(mul(r,q)),'different admissible kernels');
  check(divide(observations[0],observations[1])[1]===-1n,'gcd refusal');
  // Integer pulse-train PCM: 8 kHz, 100 ms tap spacing, 0.8s fixed duration.
  function wav(a){
    const N=6400,bytes=new Uint8Array(44+2*N),d=new DataView(bytes.buffer);
    const tag=(i,s)=>{for(let j=0;j<s.length;j++)bytes[i+j]=s.charCodeAt(j);};
    tag(0,'RIFF');d.setUint32(4,36+2*N,true);tag(8,'WAVE');tag(12,'fmt ');
    d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);
    d.setUint32(24,8000,true);d.setUint32(28,16000,true);d.setUint16(32,2,true);
    d.setUint16(34,16,true);tag(36,'data');d.setUint32(40,2*N,true);
    check((a.length-1)*800+80<=N,'PCM capacity');
    const den=sum(a);
    for(let j=0;j<a.length;j++)for(let i=0;i<80;i++){
      const z=i%40,shape=(z<20?z:40-z)*(i<40?1:-1);
      d.setInt16(44+2*(800*j+i),Number(a[j]*BigInt(1000*shape)/den),true);
    }
    return bytes;
  }
  const byteEq=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
  const fnv=a=>{let h=2166136261;for(const x of a)h=Math.imul(h^x,16777619)>>>0;return h.toString(16).padStart(8,'0');};
  const pcm={observed1A:wav(aObs[0]),observed1B:wav(bObs[0]),observed2A:wav(aObs[1]),observed2B:wav(bObs[1]),pilotA:wav(p),pilotB:wav(r)};
  check(byteEq(pcm.observed1A,pcm.observed1B)&&byteEq(pcm.observed2A,pcm.observed2B),'same audio');
  check(!byteEq(pcm.pilotA,pcm.pilotB),'different pilots');
  const strs=a=>a.map(String);
  return {pcm,receipt:{model:'exact nonnegative finite linear convolution',rows,
    totals:Object.fromEntries(['total','feasible','maximal','strictFeasible','negative'].map(key=>[key,rows.reduce((s,x)=>s+x[key],0)])),
    probeFamily,probe:{rawA:strs(hA),rawB:strs(hB),sumA:String(sum(hA)),sumB:String(sum(hB)),firstTwoEqual:true,thirdEqual:false},
    witness:{p:strs(p),r:strs(r),q:strs(q),observations:observations.map(strs),aSources:aSources.map(strs),bSources:bSources.map(strs)},
    audio:Object.fromEntries(Object.entries(pcm).map(([key,bytes])=>[key,{bytes:bytes.length,fnv1a:fnv(bytes)}])),assertionFailures:0}};
}
// CLI writes receipt to stdout and optional original WAVs.
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('laboratory.mjs')){
  const {receipt,pcm}=run();
  const fs=await import('node:fs/promises');
  if(process.argv.includes('--wav')){
    await fs.mkdir('echo-wavs',{recursive:true});
    for(const [name,data] of Object.entries(pcm))await fs.writeFile('echo-wavs/'+name+'.wav',data);
  }
  console.log(JSON.stringify(receipt,null,2));
}
