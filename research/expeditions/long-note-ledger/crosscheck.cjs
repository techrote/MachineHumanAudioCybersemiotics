// Exact independent bit-rotation census. No external dependencies.
function run() {
  const profiles=[];
  let words=0, fibres=0, rectangles=0;
  for(let n=2;n<=12;n++) {
    const full=(1<<n)-1;
    const peak=(v)=>{
      if(!v)return 0;
      if(v===full)return n;
      let p=0;
      while(v){p++;v &= ((v<<1)|(v>>(n-1)))&full;}
      return p;
    };
    for(let k=1;k<=n;k++){
      const map=new Map(), mask=(1<<k)-1;
      for(let x=1;x<full;x++){
        let v=x;
        const counts=new Map();
        for(let j=0;j<n;j++){
          const w=v&mask;
          counts.set(w,(counts.get(w)||0)+1);
          v=((v<<1)|(v>>(n-1)))&full;
        }
        const key=JSON.stringify([...counts].sort((a,b)=>a[0]-b[0]));
        const p=peak(x),q=peak(full^x);
        if(!map.has(key))map.set(key,new Set());
        map.get(key).add(q*(n+1)+p);
        words++;
      }
      let width=0;
      for(const a of map.values()){
        const p=[...a].map(i=>i%(n+1)),q=[...a].map(i=>Math.floor(i/(n+1)));
        const dx=Math.max(...p)-Math.min(...p),dy=Math.max(...q)-Math.min(...q);
        width=Math.max(width,dx);
        if(k>=2){
          if(a.size!==(dx+1)*(dy+1))throw Error('rectangle');
          rectangles++;
        }
      }
      fibres+=map.size;
      profiles.push([n,k,map.size,width]);
    }
  }
  return {words_by_horizon:words,fibres,joint_rectangles:rectangles,profiles};
}
if(typeof module!=='undefined')console.log(JSON.stringify(run(),null,2));
