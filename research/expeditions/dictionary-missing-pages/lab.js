'use strict';
// Synthetic only. Run: node lab.js
function run(){
  const assert=(p,msg)=>{if(!p)throw Error(msg)};
  function C(n,k){if(k<0||k>n)return 0n;let a=1n;for(let i=1;i<=k;i++)a=a*BigInt(n-i+1)/BigInt(i);return a}
  function synd(z,m){let s=0;for(let i=0;i<m;i++)if((z>>>i)&1)s^=i;return s}
  function pop(z){let n=0;while(z){z&=z-1;n++}return n}
  let results=[], dpTransitions=0, spectrumChecks=0, mixtureChecks=0, directMasks=0, decoderCells=0;
  for(const m of [8,16,32,64,128]){
    let d=Array.from({length:m},()=>Array(m+1).fill(0n));d[0][0]=1n;
    for(let i=0;i<m;i++){
      let e=Array.from({length:m},()=>Array(m+1).fill(0n));
      for(let s=0;s<m;s++)for(let w=0;w<=i;w++)if(d[s][w]){
        e[s][w]+=d[s][w];e[s^i][w+1]+=d[s][w];dpTransitions+=2;
      }d=e;
    }
    const size=(1n<<BigInt(m))/BigInt(m), denom=1n<<BigInt(m);
    const base=BigInt(m)*C(m,m/2);
    const an=4n*C(m-2,m/2-1)*C(m/2-1,m/4-1), ad=C(m-2,m/2-2);
    assert(an%ad===0n,"Fourier numerator integral");
    const a=an/ad;
    const totals=d.map(row=>row.reduce((acc,n,w)=>acc+n*BigInt(Math.abs(m-2*w)),0n));
    for(let s=0;s<m;s++){
      assert(d[s].reduce((x,y)=>x+y,0n)===size,"syndrome mass");
      assert(totals[s]*denom===size*(base+a*BigInt(s===0?1-m:1)),"syndrome score");
      spectrumChecks++;
    }
    for(const kind of ["point","uniform","ramp","two","missing-one"]){
      let weights=Array.from({length:m},(_,s)=>BigInt(kind==="point"?(s===0?1:0):kind==="uniform"?1:kind==="ramp"?s+1:kind==="two"?(s<2?1:0):s===0?0:1));
      let W=weights.reduce((x,y)=>x+y,0n);
      for(let t=0;t<m;t++){
        let score=weights.reduce((v,n,s)=>v+n*totals[s^t],0n);
        assert(score*denom===size*(W*base+a*(W-BigInt(m)*weights[t])),"mixture exact score");
        mixtureChecks++;
      }
    }
    results.push({m,labels:size.toString(),omitted:1-1/m,baseline:.5+Number(C(m,m/2))/Number(denom)/2,excess:Number(a)/Number(denom)/(2*m),aNumerator:a.toString()});
  }
  const m=8, words=Array.from({length:1<<m},(_,z)=>z).filter(z=>synd(z,m)===0);
  for(let i=0;i<m;i++)assert(words.filter(z=>(z>>i)&1).length===words.length/2,"uniform prior");
  let max=0;
  for(let t=0;t<(1<<(2*m));t++)if(pop(t)===m){
    let score=0;
    for(const z of words){
      let signed=0;
      for(let i=0;i<m;i++)signed+=((t>>(2*i+((z>>i)&1)))&1)?1:-1;
      score+=Math.abs(signed);
    }
    max=Math.max(max,score);directMasks++;
  }
  assert(max===72,"direct all balanced target maximum");
  for(let action=0;action<m;action++)for(const z of words){
    const seen=new Map();
    for(let i=0;i<m;i++){
      const x=2*i+((z>>i)&1), obs=i===action?2*i:x;
      assert(!seen.has(obs),"decoder collision");seen.set(obs,x);decoderCells++;
    }
  }
  return {results,dpTransitions,spectrumChecks,mixtureChecks,directMasks,decoderCells,directMax:max};
}
console.log(JSON.stringify(run(),null,2));
