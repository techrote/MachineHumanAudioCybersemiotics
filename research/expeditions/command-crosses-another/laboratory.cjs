"use strict";
function laboratory() {
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  const pop=x=>{let n=0;while(x){x&=x-1;n++}return n};
  const dist=(a,b)=>pop(a^b);
  const gap=(a,b,c)=>pop((a^c)&(b^c));
  const choose=(n,k)=>{let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return Math.round(v)};
  const counts={intervalTriples:0,pathComparisons:0,codebooks:0,balancedTriples:0,simplexTriples:0,noiseComparisons:0,guardChecks:0};
  const intervals=(a,b)=>{let d=a^b,out=[];for(let s=d;;s=(s-1)&d){out.push(a^s);if(!s)break}return out};
  for(let n=2;n<=6;n++){
    for(let a=0;a<2**n;a++)for(let b=a+1;b<2**n;b++){
      const vs=intervals(a,b);
      for(let c=0;c<2**n;c++)if(c!==a&&c!==b){
        const d=Math.min(...vs.map(v=>dist(v,c)));
        check(d===gap(a,b,c)&&2*d===dist(a,c)+dist(b,c)-dist(a,b),"interval");
        counts.intervalTriples++;
        if(n<=3)for(let e=0;e<=n;e++)for(let t=0;t<=n;t++){
          let exists=false;
          for(const v of vs)for(let y=0;y<2**n;y++)if(dist(v,y)<=e&&dist(y,c)<=t)exists=true;
          check(exists===(d<=e+t),"noise ball");
          counts.noiseComparisons++;
        }
      }
    }
  }
  const paths=(a,b)=>{
    const result=[];
    function walk(v,mask){if(v===b){result.push(mask);return}let left=v^b;while(left){const bit=left&-left;left^=bit;const w=v^bit;walk(w,mask|(1<<w))}}
    walk(a,1<<a);return result;
  };
  const pathDP=(a,b,bad)=>{
    const memo=new Map();
    function rec(v){if((bad>>>v)&1)return 0;if(v===b)return 1;if(memo.has(v))return memo.get(v);
      let left=v^b,total=0;while(left){const bit=left&-left;left^=bit;total+=rec(v^bit)}memo.set(v,total);return total}
    return rec(a);
  };
  const census=[];
  for(let n=2;n<=4;n++){
    const N=2**n,pairs=[];
    for(let a=0;a<N;a++)for(let b=a+1;b<N;b++)pairs.push({a,b,end:(1<<a)|(1<<b),p:paths(a,b),interval:intervals(a,b).reduce((m,v)=>m|(1<<v),0)});
    const row={n,books:0,universal:0,scheduled:0,scheduledOnly:0,noSchedule:0,maxUniversal:0,maxScheduled:0,maxUniversalWitness:[],maxScheduledWitness:[]};
    for(let book=0;book<2**N;book++){
      const m=pop(book);if(m<3)continue;
      row.books++;counts.codebooks++;let all=true,some=true,allByInterval=true;
      for(const p of pairs)if((book&p.end)===p.end){
        const bad=book^p.end;
        const safe=p.p.filter(mask=>!(mask&bad)).length;
        check(safe===pathDP(p.a,p.b,bad),"path DP");
        counts.pathComparisons++;
        all=all&&safe===p.p.length;some=some&&safe>0;allByInterval=allByInterval&&!(p.interval&bad);
      }
      check(all===allByInterval,"universal interval classification");
      const words=()=>Array.from({length:N},(_,i)=>i).filter(i=>book&(1<<i)).map(v=>v.toString(2).padStart(n,"0"));
      if(all){row.universal++;if(m>row.maxUniversal){row.maxUniversal=m;row.maxUniversalWitness=words()}}
      if(some){row.scheduled++;if(m>row.maxScheduled){row.maxScheduled=m;row.maxScheduledWitness=words()}}
      if(some&&!all)row.scheduledOnly++;
      if(!some)row.noSchedule++;
    }
    census.push(row);
  }
  const designs=[];
  function metrics(cols,M,counter){
    let minGap=Infinity,maxGap=0,minDist=Infinity,maxDist=0;
    for(let a=0;a<M;a++)for(let b=a+1;b<M;b++){
      let d=0;for(const col of cols)d+=((col>>>a)^(col>>>b))&1;
      minDist=Math.min(minDist,d);maxDist=Math.max(maxDist,d);
      for(let c=0;c<M;c++)if(c!==a&&c!==b){
        let g=0;for(const col of cols){const x=(col>>>a)&1,y=(col>>>b)&1,z=(col>>>c)&1;g+=Number(x===y&&x!==z)}
        minGap=Math.min(minGap,g);maxGap=Math.max(maxGap,g);counts[counter]++;
      }
    }
    const n=cols.length,bound=Math.floor(n*Math.floor(M*M/4)/(M*(M-1)));
    check(minGap===bound&&minGap===maxGap&&minDist===maxDist&&minDist===2*minGap,"sharp design");
    return {M,n,minGap,maxGap,minDist,maxDist,staticCorrection:Math.floor((minDist-1)/2),transitionCorrection:Math.floor((minGap-1)/2)};
  }
  for(let M=3;M<=10;M++){
    const cols=[];for(let col=0;col<2**M;col++)if(pop(col)===Math.floor(M/2))cols.push(col);
    check(cols.length===choose(M,Math.floor(M/2)),"balanced size");
    designs.push({kind:"balanced",...metrics(cols,M,"balancedTriples")});
  }
  for(let k=2;k<=5;k++){
    const M=2**k;
    // Keep columns as BigInt masks for M=32, then signed 32-bit unsigned shifts work.
    const cols=[];for(let v=1;v<M;v++){let col=0;for(let m=0;m<M;m++)if(pop(m&v)%2)col|=1<<m;cols.push(col)}
    designs.push({kind:"simplex",...metrics(cols,M,"simplexTriples")});
  }
  // Static distance arbitrarily large but exact third command on a transition.
  const repeated=[];
  for(let m=1;m<=8;m++){
    const a=0,c=(1<<(2*m))-1,b=2**(4*m)-1;
    // avoid 32-bit sign at m=8 by only using positive low 32-bit operations
    const d=Math.min(dist(a,b),dist(a,c),dist(b,c));
    check(d===2*m&&gap(a,b,c)===0,"repeated witness");repeated.push({n:4*m,minDist:d,staticCorrection:Math.floor((d-1)/2),gap:0});
  }
  // For simplex [7,3,4], a single bit error can move an intermediate
  // to a word at distance one from a third valid word.
  const simplex=Array.from({length:8},(_,m)=>Array.from({length:7},(_,i)=>pop(m&(i+1))%2).reduce((w,b,i)=>w|(b<<i),0));
  const [a,b,c]=simplex;
  const v=intervals(a,b).find(x=>dist(x,c)===2);
  const y=Array.from({length:128},(_,i)=>i).find(x=>dist(v,x)===1&&dist(x,c)===1);
  check(y!==undefined&&simplex.filter(x=>dist(x,y)<=1).length===1,"simplex false decode");
  const simplexWitness={a,b,c,v,y,decoded:c,staticDistance:4};
  const parity=Array.from({length:16},(_,i)=>i).filter(x=>pop(x)%2===0);
  const parityBad=parity.filter(x=>x!==0&&x!==15).reduce((m,x)=>m|(1<<x),0);
  check(pathDP(0,15,parityBad)===0,"parity schedule refusal");
  const ordinaryBad=1<<3;
  const scheduleWitness={a:0,b:15,c:3,safe:pathDP(0,15,ordinaryBad),total:paths(0,15).length,paritySafe:0};
  check(scheduleWitness.safe===20&&scheduleWitness.total===24,"path counts");
  // For all possible payload words, a fully disabled replicated guard
  // lies at distance g + payload distance from an enabled word.
  for(let g=1;g<=4;g++)for(let p=0;p<8;p++)for(let c=0;c<8;c++)for(let e=0;e<=2;e++)for(let t=0;t<=2;t++){
    const enabled=(((1<<g)-1)<<3)|c;
    const min=g+dist(p,c);
    let possible=false;for(let z=0;z<2**(g+3);z++)if(dist(z,p)<=e&&dist(z,enabled)<=t){possible=true;break}
    check(possible===(min<=e+t),"guard");counts.guardChecks++;
  }
  // Integer square-wave synthesis; deterministic, not an auditory study.
  function wav(words){
    const frames=words.length*800,buf=new Uint8Array(44+frames*2),d=new DataView(buf.buffer);
    const ascii=(off,s)=>{for(let j=0;j<s.length;j++)buf[off+j]=s.charCodeAt(j)};
    ascii(0,"RIFF");d.setUint32(4,buf.length-8,true);ascii(8,"WAVE");ascii(12,"fmt ");d.setUint32(16,16,true);d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,8000,true);d.setUint32(28,16000,true);d.setUint16(32,2,true);d.setUint16(34,16,true);ascii(36,"data");d.setUint32(40,frames*2,true);
    const periods=[40,32,25,20,16];
    for(let k=0;k<words.length;k++)for(let t=0;t<800;t++){let s=0;for(let i=0;i<5;i++)if(words[k]&(1<<i))s+=((t%periods[i])*2<periods[i]?1:-1)*1000;d.setInt16(44+2*(800*k+t),s,true)}
    return buf;
  }
  const fnv=buf=>{let h=2166136261;for(const b of buf)h=Math.imul(h^b,16777619);return (h>>>0).toString(16).padStart(8,"0")};
  const equal=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
  const scores={unsafe_transition:[0,1,3,7,15],scheduled_transition:[0,4,12,13,15],guarded_transition:[16,0,1,3,7,15,31],intentional_C:[3],transient_C:[3],enabled_C:[19],disabled_C:[3]};
  const recordings=Object.fromEntries(Object.entries(scores).map(([name,words])=>[name,wav(words)]));
  check(equal(recordings.intentional_C,recordings.transient_C),"unlabelled acoustic alias");
  check(!equal(recordings.enabled_C,recordings.disabled_C),"guard acoustic distinction");
  return {receipt:{scope:"synthetic exact combinatorics and original integer PCM; no participants",counts,census,designs,repeated,simplexWitness,scheduleWitness,audio:Object.entries(recordings).map(([name,buf])=>({name,words:scores[name],bytes:buf.length,fnv1a:fnv(buf)}))},recordings};
}
module.exports = laboratory;
if (require.main === module) {
  const fs = require("node:fs");
  const path = require("node:path");
  const result = laboratory();
  console.log(JSON.stringify(result.receipt, null, 2));
  if (process.argv[2]) {
    fs.mkdirSync(process.argv[2], {recursive:true});
    for (const [name, bytes] of Object.entries(result.recordings)) fs.writeFileSync(path.join(process.argv[2], name+".wav"), bytes);
  }
}
