"use strict";
// Exact finite integer checks, no dependencies. Run: node lab.js
const check=(ok,label)=>{if(!ok)throw Error(label);};
const sum=a=>a.reduce((s,x)=>s+x,0);
const pc=x=>{let n=0;while(x){x&=x-1;n++;}return n;};
const chi=x=>pc(x)%2?-1:1;
const eq=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
const counts={cases:0,properMarginalCells:0,conditionalChannelCells:0,sourceErrorCells:0,wordErrorCells:0,pairContrastCells:0,groupOutputCells:0,endpointAssignments:0,balancedTargetAudits:0};
const results=[];
for(const k of [3,5,7])for(const [r,D] of [[0,1],[1,10],[1,4],[1,3],[1,2]]){
  const L=2**k,m=k+1,words=Array.from({length:L},(_,i)=>i);
  const f=(i,w)=>i<4?((([27,53,71,141][i]>>(w&7))&1)?1:-1):((w>>(i-1))&1)?-1:1;
  const Q=2*D**k;
  check(Number.isSafeInteger(Q*L*m),"safe exact integer range");
  const ind=words.map(e=>2*r**pc(e)*(D-r)**(k-pc(e)));
  const even=Math.min(...ind.filter((_,e)=>chi(e)===1));
  const odd=Math.min(...ind.filter((_,e)=>chi(e)===-1));
  check(even+odd===2*D*r**(k-1),"closed form endpoint width");
  const offset=(odd-even)/2,radius=(odd+even)/2;
  const mid=ind.map((p,e)=>p+offset*chi(e));
  const law=z=>mid.map((p,e)=>p+radius*z*chi(e));
  const plus=law(1),minus=law(-1);
  for(const p of [mid,plus,minus]){
    check(sum(p)===Q&&p.every(x=>x>=0&&Number.isInteger(x)),"probability law");
    for(let b=0;b<k;b++)for(const e of words)if(!(e&(1<<b))){
      check(p[e]+p[e^(1<<b)]===ind[e]+ind[e^(1<<b)],"proper marginal");counts.properMarginalCells++;
    }
  }
  const signs=new Set();
  for(const w of words){
    let z=0;for(let i=0;i<m;i++)if(f(i,w)>0)z|=1<<i;
    check(!signs.has(z)&&!signs.has(z^((1<<m)-1)),"antipodal orientation");signs.add(z);
  }
  const base=[],signal=[],wordE=words.map(()=>Array(L).fill(0)),baseWordE=words.map(()=>Array(L).fill(0));
  for(let i=0;i<m;i++)for(const s of [-1,1]){
    const h=i<m/2?1:-1,allowed=words.filter(w=>f(i,w)===s);
    check(allowed.length===L/2&&sum(allowed.map(chi))===0,"balanced word parity within original");
    const rows=[Array(L).fill(0),Array(L).fill(0),Array(L).fill(0)],err=Array(L).fill(0);
    for(const w of allowed){
      const p=h*chi(w)===1?plus:minus;
      for(const e of words){
        rows[0][w^e]+=ind[e];rows[1][w^e]+=mid[e];rows[2][w^e]+=p[e];
        err[e]+=p[e];wordE[w][e]+=p[e];baseWordE[w][e]+=mid[e];counts.conditionalChannelCells++;
      }
    }
    for(const e of words){
      check(err[e]===L/2*mid[e],"complete error histogram conditional on original");counts.sourceErrorCells++;
    }
    check(eq(rows[0],rows[1]),"centering invisible for low-degree dictionary");
    base.push(rows[1]);signal.push(rows[2]);
  }
  for(const w of words)for(const e of words){
    check(wordE[w][e]===baseWordE[w][e],"complete error histogram conditional on word");counts.wordErrorCells++;
  }
  const den=L/2*Q;
  for(let i=0;i<m;i++)for(const y of words){
    check(signal[2*i+1][y]-signal[2*i][y]===base[2*i+1][y]-base[2*i][y],"unchanged full pair contrast");counts.pairContrastCells++;
  }
  const bRows=[0,1].map(g=>words.map(y=>sum(signal.slice(g*m,(g+1)*m).map(row=>row[y]))));
  const priorRows=[0,1].map(g=>words.map(y=>sum(base.slice(g*m,(g+1)*m).map(row=>row[y]))));
  for(const y of words){
    check(priorRows[0][y]===priorRows[1][y],"group independence baseline");
    check(bRows[0][y]-bRows[1][y]===m*L*radius*chi(y),"sharp group contrast");
    check(bRows[0][y]+bRows[1][y]===2*priorRows[0][y],"identical pooled received words");counts.groupOutputCells++;
  }
  const groupGuess=sum(words.map(y=>Math.max(bRows[0][y],bRows[1][y])))/(2*m*den);
  check(Math.abs(groupGuess-(.5+(2*r/D)**(k-1)/2))<1e-14,"sharp probability");
  const pairGuess=rows=>Math.min(...Array.from({length:m},(_,i)=>sum(words.map(y=>Math.max(rows[2*i][y],rows[2*i+1][y])))/(2*den)));
  check(pairGuess(base)===pairGuess(signal),"same worst-pair Bayes accuracy");
  if(k===3){
    let maxAbs=0;
    for(let mask=0;mask<2**L;mask++){
      let z=0;for(const w of words)z+=chi(w)*(((mask>>w)&1)?odd:-even);
      maxAbs=Math.max(maxAbs,Math.abs(z));counts.endpointAssignments++;
    }
    check(maxAbs===L*radius,"independent corner bound");
    const audit=rows=>{
      let best=0;
      for(let mask=0;mask<2**(2*m);mask++)if(pc(mask)===m){
        let total=0;for(const y of words){let a=0,b=0;for(let x=0;x<2*m;x++)if((mask>>x)&1)a+=rows[x][y];else b+=rows[x][y];total+=Math.max(a,b);}
        best=Math.max(best,total);counts.balancedTargetAudits++;
      }return best/(2*m*den);
    };
    results.push({k,q:r/D,groupGuess,pairGuess:pairGuess(signal),worstTargetBaseline:audit(base),worstTargetSignal:audit(signal)});
  }
  counts.cases++;
}
console.log(JSON.stringify({counts,results},null,2));
