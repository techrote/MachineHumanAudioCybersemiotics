"use strict";
// Original synthetic finite oracle; no human data.
function laboratory(){
  const episodes=[["hum",12],["tap",1],["gap",1],["tap",1],["gap",1],["tap",1],["gap",1],["chime",2]];
  const names=["hum","tap","gap","chime"];
  const frames=episodes.flatMap(([label,len])=>Array(len).fill(label));
  const choose=(n,k)=>{if(k<0||k>n)return 0;let c=1;for(let i=1;i<=k;i++)c=c*(n-i+1)/i;return c};
  let assertions=0;
  function check(c,msg){assertions++;if(!c)throw Error(msg)}
  function enumerate(items,k){
    let total=0;const inclusion=Object.fromEntries(names.map(x=>[x,0])),counts={...inclusion};
    function visit(start,s){
      if(s.length===k){total++;for(const x of s)counts[x]++;for(const x of new Set(s))inclusion[x]++;return}
      for(let i=start;i<=items.length-(k-s.length);i++)visit(i+1,[...s,items[i]]);
    }
    visit(0,[]);
    check(total===choose(items.length,k),"total");
    for(const x of names){
      const n=items.filter(v=>v===x).length;
      check(inclusion[x]===total-choose(items.length-n,k),"inclusion");
      check(counts[x]*items.length===total*k*n,"mean");
    }
    return {N:items.length,k,total,inclusion,counts};
  }
  const t=enumerate(frames,3),e=enumerate(episodes.map(x=>x[0]),3),cat=enumerate(names,3);
  const variants=[];
  for(let mask=0;mask<4096;mask++){
    const refined=[];let bit=0;
    for(const [label,len] of episodes){
      let d=1;
      for(let j=1;j<len;j++){
        if(mask&(1<<bit)){refined.push([label,d]);d=1}else d++;
        bit++;
      }
      refined.push([label,d]);
    }
    check(bit===12,"refinement bits");
    check(JSON.stringify(refined.flatMap(([l,n])=>Array(n).fill(l)))===JSON.stringify(frames),"time stream changed");
    const m=enumerate(refined.map(x=>x[0]),3);
    variants.push(m.inclusion.hum/m.total);
    if(mask===4095)check(JSON.stringify(m)===JSON.stringify(t),"all-unit split must equal time sampling");
  }
  check(t.inclusion.hum*t.N>0,"nonempty hum");
  check(e.inclusion.hum/e.total!==t.inclusion.hum/t.total,"episode vs time difference");
  const equal=["hum","tap","gap","chime"];
  check(JSON.stringify(enumerate(equal,3))===JSON.stringify(cat),"equal-duration negative control");
  check(Math.min(...variants)<Math.max(...variants),"segmentation sensitivity");
  return {episodes,time:t,episode:e,category:cat,refinements:variants.length,humEpisodeInclusionRange:[Math.min(...variants),Math.max(...variants)],assertions};
}
console.log(JSON.stringify(laboratory(),null,2));
