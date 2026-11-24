"use strict";
function experiment(){
  const assert=(x,msg)=>{if(!x)throw Error(msg)};
  const fact=n=>{let x=1;for(let i=2;i<=n;i++)x*=i;return x};
  const choose=(n,r)=>{if(r<0||n<r)return 0;let x=1;for(let i=1;i<=r;i++)x=x*(n-i+1)/i;return Math.round(x)};
  function* perm(a){if(!a.length){yield [];return}for(let i=0;i<a.length;i++)for(const t of perm(a.slice(0,i).concat(a.slice(i+1))))yield [a[i],...t]}
  function* comb(n,m,start=0,p=[]){if(!m){yield p;return}for(let i=start;i<=n-m;i++)yield* comb(n,m-1,i+1,p.concat(i))}
  const hist=(w,k)=>{const h=new Map();for(let i=0;i<=w.length-k;i++){let s=w.slice(i,i+k);h.set(s,(h.get(s)||0)+1)}return [...h].sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0)};
  const suffix=(w,k)=>w.slice(w.length-(k-1));
  const sig=(w,k)=>JSON.stringify([w.slice(0,k-1),suffix(w,k),hist(w,k)]);
  const allHist=(w,k)=>JSON.stringify(Array.from({length:k},(_,i)=>hist(w,i+1)));
  function desc(n,k,clusters,left,right){
    const span=clusters.reduce((a,c)=>a+c.length,0);
    const gaps=clusters.length+1-Number(!!left)-Number(!!right);
    const slack=n-span-(k-1)*gaps-(left?left[1]:0)-(right?right[1]:0);
    const fixed=new Set([left?.[0],right?.[0]].filter(Boolean)).size;
    const free=clusters.length-fixed;
    assert(slack>=0 && free>=0 && (gaps>0||slack===0),"infeasible descriptor");
    return {clusters:clusters.slice().sort(),left,right,slack,gaps,free,count:fact(free)*(gaps?choose(slack+gaps-1,gaps-1):1),orders:fact(free)};
  }
  function direct(w,k){
    const pos=[];for(let i=0;i<w.length;i++)if(w[i]!=="0")pos.push(i);
    let clusters=[],start=pos[0],last=start;
    for(const p of pos.slice(1)){if(p-last>=k){clusters.push(w.slice(start,last+1));start=p}last=p}
    clusters.push(w.slice(start,last+1));
    const lp=pos[0],rp=w.length-1-pos.at(-1);
    return desc(w.length,k,clusters,lp<k-1?[clusters[0],lp]:null,rp<k-1?[clusters.at(-1),rp]:null);
  }
  function infer(n,k,pre,post,h){
    const graph=new Map();
    for(const [s] of h){
      const p=[];for(let i=0;i<s.length;i++)if(s[i]!=="0"){p.push(i);if(!graph.has(s[i]))graph.set(s[i],new Map())}
      for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++){
        const a=s[p[i]],b=s[p[j]],d=p[j]-p[i];
        assert(!graph.get(a).has(b)||graph.get(a).get(b)===d,"contradictory local offset");
        graph.get(a).set(b,d);graph.get(b).set(a,-d)
      }
    }
    const visited=new Set(),clusters=[],byLabel=new Map();
    for(const a of graph.keys()){
      if(visited.has(a))continue;
      const q=[a],coords=new Map([[a,0]]);visited.add(a);
      for(let j=0;j<q.length;j++)for(const [b,d] of graph.get(q[j])){
        const x=coords.get(q[j])+d;
        if(coords.has(b)){assert(coords.get(b)===x,"inconsistent cycle");continue}
        coords.set(b,x);q.push(b);visited.add(b)
      }
      const lo=Math.min(...coords.values()),hi=Math.max(...coords.values()),arr=Array(hi-lo+1).fill("0");
      for(const [b,x] of coords){assert(arr[x-lo]==="0","collision");arr[x-lo]=b}
      const c=arr.join("");clusters.push(c);
      for(const [b,x] of coords)byLabel.set(b,[c,x-lo])
    }
    let left=null,right=null;
    for(let i=0;i<pre.length;i++)if(pre[i]!=="0"){
      const [c,x]=byLabel.get(pre[i]);const a=[c,i-x];assert(!left||JSON.stringify(left)===JSON.stringify(a),"left anchor inconsistent");left=a
    }
    for(let i=0;i<post.length;i++)if(post[i]!=="0"){
      const [c,x]=byLabel.get(post[i]),p=n-k+1+i;const a=[c,n-1-(p-x+c.length-1)];assert(!right||JSON.stringify(right)===JSON.stringify(a),"right anchor inconsistent");right=a
    }
    return desc(n,k,clusters,left,right)
  }
  let words=0,classes=0,paddedWords=0,paddedClasses=0,anchorClasses=0,fullOrderClasses=0,maxCount=0,rows=[],shortest={};
  for(let m=1;m<=4;m++){
    const ps=[...perm("ABCD".slice(0,m).split(""))];
    for(let n=m;n<=11;n++)for(let k=1;k<=Math.min(n,5);k++){
      const groups=new Map();let count=0,pad=0;
      for(const p of comb(n,m))for(const labels of ps){
        const arr=Array(n).fill("0");for(let j=0;j<m;j++)arr[p[j]]=labels[j];const w=arr.join("");
        const h=hist(w,k),pre=w.slice(0,k-1),post=suffix(w,k),key=JSON.stringify([pre,post,h]);
        const d=direct(w,k),e=infer(n,k,pre,post,h);
        assert(JSON.stringify(d)===JSON.stringify(e),"inference mismatch "+w+" k="+k);
        const hAll=allHist(w,k);
        if(!groups.has(key))groups.set(key,{d,n:0,orders:new Set(),all:hAll});
        const g=groups.get(key);assert(g.all===hAll&&JSON.stringify(g.d)===JSON.stringify(d),"equivalence mismatch");
        g.n++;g.orders.add(labels.join(""));count++;if(!d.left&&!d.right)pad++;
      }
      let pc=0,ac=0,fc=0,mc=0;
      for(const g of groups.values()){
        assert(g.n===g.d.count,"cardinality mismatch");assert(g.orders.size===g.d.orders,"order cardinality mismatch");
        if(!g.d.left&&!g.d.right)pc++;else ac++;
        if(m>=2&&g.orders.size===fact(m)){fc++;const sk=m+","+k;if(!(sk in shortest))shortest[sk]=n;assert(n>=(m+1)*k-1,"premature all-order class")}
        mc=Math.max(mc,g.n)
      }
      words+=count;classes+=groups.size;paddedWords+=pad;paddedClasses+=pc;anchorClasses+=ac;fullOrderClasses+=fc;maxCount=Math.max(maxCount,mc);
      rows.push({m,n,k,words:count,classes:groups.size,padded_classes:pc,anchored_classes:ac,all_order_classes:fc,max_class:mc});
    }
  }
  for(let m=2;m<=4;m++)for(let k=1;k<=5;k++){const n=(m+1)*k-1;if(n<=11)assert(shortest[m+","+k]===n,"threshold missing")}
  let constructive=0;
  for(let m=2;m<=6;m++)for(let k=1;k<=7;k++){
    const p=[...perm("ABCDEF".slice(0,m).split(""))],z="0".repeat(k-1);
    const base=z+p[0].join(z)+z,key=sig(base,k);
    assert(base.length===(m+1)*k-1,"construction length");
    for(const a of p){const w=z+a.join(z)+z;assert(sig(w,k)===key,"construction failed");constructive++}
  }
  let comparisonQueries=0,comparisonCertificates=0,nonadaptiveSets=0,sortRuns=0,sortWorst={};
  for(let c=2;c<=5;c++){
    const p=[...perm(Array.from({length:c},(_,i)=>i))],pairs=[];
    for(let a=0;a<c;a++)for(let b=a+1;b<c;b++)pairs.push([a,b]);
    for(let mask=0;mask<(1<<pairs.length);mask++){
      const buckets=new Map();
      const selected=pairs.filter((_,i)=>mask&(1<<i));
      for(const o of p){const key=selected.map(([a,b])=>Number(o.indexOf(a)<o.indexOf(b))).join("");if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(o)}
      assert((buckets.size===p.length)===(mask===(1<<pairs.length)-1),"nonadaptive criterion");
      nonadaptiveSets++;
      for(const bucket of buckets.values())for(const o of bucket){
        const adjacent=o.slice(1).every((b,i)=>selected.some(([x,y])=>(x===o[i]&&y===b)||(y===o[i]&&x===b)));
        assert((bucket.length===1)===adjacent,"certificate criterion");
        comparisonQueries++;if(adjacent)comparisonCertificates++;
      }
    }
  }
  for(let c=2;c<=8;c++){
    let worst=0;
    for(const order of perm(Array.from({length:c},(_,i)=>i))){
      const a=[];let q=0;
      for(let label=0;label<c;label++){
        let lo=0,hi=a.length;
        while(lo<hi){const mid=(lo+hi)>>1;q++;if(order.indexOf(label)<order.indexOf(a[mid]))hi=mid;else lo=mid+1}
        a.splice(lo,0,label)
      }
      assert(a.join()===order.join(),"sort failed");worst=Math.max(worst,q);sortRuns++
    }
    let bound=0;for(let j=2;j<=c;j++)bound+=Math.ceil(Math.log2(j));
    assert(worst===bound,"insertion bound");sortWorst[c]=worst
  }
  function pcm(w){
    const rate=8000,slot=320,buf=new Uint8Array(44+2*slot*w.length),v=new DataView(buf.buffer);
    const ascii=(i,s)=>{for(let j=0;j<s.length;j++)buf[i+j]=s.charCodeAt(j)};
    ascii(0,"RIFF");v.setUint32(4,buf.length-8,true);ascii(8,"WAVE");ascii(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);ascii(36,"data");v.setUint32(40,buf.length-44,true);
    for(let i=0;i<w.length;i++)for(let j=0;j<slot;j++){const f=w[i]==="0"?0:200+100*(w.charCodeAt(i)-65),x=f?(Math.floor(j*f*2/rate)%2?-6000:6000):0;v.setInt16(44+2*(i*slot+j),x,true)}
    return buf
  }
  const fp=b=>{let h=2166136261;for(const x of b)h=Math.imul(h^x,16777619);return (h>>>0).toString(16).padStart(8,"0")};
  const equal=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
  const a="00A00B00C00",b="00C00B00A00",k=3;
  assert(sig(a,k)===sig(b,k),"audio collision");
  const archive=w=>hist(w,k).flatMap(([s,n])=>Array(n).fill(s)).join("");
  const sounds={chronology_a:pcm(a),chronology_b:pcm(b),archive_a:pcm(archive(a)),archive_b:pcm(archive(b))};
  assert(!equal(sounds.chronology_a,sounds.chronology_b),"distinct chronology PCM");
  assert(equal(sounds.archive_a,sounds.archive_b),"archive PCM not identical");
  assert(JSON.stringify(hist("010",2))===JSON.stringify(hist("101",2))&&allHist("010",2)!==allHist("101",2),"boundary negative failed");
  assert(allHist("0010100",2)===allHist("0100010",2),"repeated label negative failed");
  return {receipt:{model:"distinct nonzero markers, finite words; k<=n; no empirical data",words,classes,paddedWords,paddedClasses,anchorClasses,fullOrderClasses,maxCount,shortest,constructive,comparisonQueries,comparisonCertificates,nonadaptiveSets,sortRuns,sortWorst,rows,pcm:Object.fromEntries(Object.entries(sounds).map(([n,v])=>[n,{bytes:v.length,fnv1a32:fp(v)}])),assertion_failures:0},sounds}
}
if (typeof module !== "undefined") module.exports = { experiment };
if (typeof require !== "undefined" && require.main === module) {
  const fs = require("node:fs"), path = require("node:path");
  const { receipt, sounds } = experiment();
  const dest = process.argv[2] || "results"; fs.mkdirSync(dest, { recursive: true });
  fs.writeFileSync(path.join(dest, "execution.json"), JSON.stringify(receipt, null, 2)+"\n");
  for (const [name, bytes] of Object.entries(sounds)) fs.writeFileSync(path.join(dest, name+".wav"), bytes);
  console.log(JSON.stringify({...receipt, rows: undefined}, null, 2));
}
