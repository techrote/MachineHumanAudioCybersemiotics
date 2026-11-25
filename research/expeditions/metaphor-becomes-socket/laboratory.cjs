"use strict";
// Synthetic research model; run with node laboratory.cjs.
function laboratory(){
  const modes=["output","transport","bank"];
  const actions=["hold","tick","release","edit"];
  function trace(initial,mode,events){
    let bank=initial.slice(), phase=0, held=false, saved=null, captured=0;
    const value=()=>held&&mode==="output"?captured:(held&&mode==="bank"?saved:bank)[phase];
    let out=[value()];
    for(const event of events){
      if(event==="hold"&&!held){captured=value();saved=bank.slice();held=true;}
      else if(event==="release"){held=false;saved=null;}
      else if(event==="tick"&&!(held&&mode==="transport"))phase=(phase+1)%4;
      else if(event==="edit")bank[1]=(bank[1]+1)%4;
      out.push(value());
    }
    return out;
  }
  const signatures=(p,e)=>modes.map(m=>trace(p,m,e).join(","));
  const distinguishes=(p,e)=>new Set(signatures(p,e)).size===3;
  const assert=(condition,message)=>{if(!condition)throw new Error(message);};
  const sequences=[[]];
  for(let k=1;k<=4;k++){
    const prev=sequences.filter(s=>s.length===k-1);
    for(const s of prev)for(const a of actions)sequences.push([...s,a]);
  }
  const witness=["hold","tick","release"];
  const p=[0,1,2,3];
  const expected=["0,0,0,1","0,0,0,0","0,0,1,1"];
  assert(JSON.stringify(signatures(p,witness))===JSON.stringify(expected),"principal witness");
  const histogram={};
  let sequenceChecks=0, immediateChecks=0, adaptiveChecks=0, unheldChecks=0;
  for(let n=0;n<256;n++){
    const bank=Array.from({length:4},(_,i)=>(n>>(2*i))&3);
    assert(new Set(signatures(bank,["hold"])).size===1,"hold itself changes output");
    immediateChecks++;
    const adaptive=bank[0]===bank[1]?["edit",...witness]:witness;
    assert(distinguishes(bank,adaptive),"adaptive discriminator");
    adaptiveChecks++;
    let min=Infinity;
    for(const seq of sequences){
      const sig=signatures(bank,seq);
      const distinct=new Set(sig).size;
      if(distinct===3)min=Math.min(min,seq.length);
      if(!seq.includes("hold")){
        assert(distinct===1,"unheld implementations differ");
        unheldChecks++;
      }
      sequenceChecks++;
    }
    assert(min===(bank[0]===bank[1]?4:3),"sharp horizon");
    histogram[min]=(histogram[min]??0)+1;
  }
  assert(histogram[3]===192&&histogram[4]===64,"histogram");
  const editWitness=["hold","edit","tick","release"];
  const edited=signatures(p,editWitness);
  assert(JSON.stringify(edited)===JSON.stringify(["0,0,0,0,2","0,0,0,0,0","0,0,0,1,2"]),"edit witness");
  return {patterns:256,sequences:sequences.length,sequenceChecks,immediateChecks,adaptiveChecks,unheldChecks,shortestDiscriminatorHistogram:histogram,witness:{events:witness,modes,outputs:expected},editWitness:{events:editWitness,outputs:edited}};
}
console.log(JSON.stringify(laboratory(), null, 2));
