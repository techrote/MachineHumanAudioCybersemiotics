// Independent path enumeration and aperiodic extension for MHAC #240.
import { laboratory } from './memory.mjs';
function extension(L){
  const assert=(x,m)=>{if(!x)throw Error(m)};
  function mixed(k){
    const states=[];
    for(const len of [k,k+1])for(let p=0;p<len;p++)for(let z=0;z<2**(len-1);z++)states.push({len,p,z});
    const d=2**(k+1),labels=states.map(({len,p,z})=>p===len-1?z.toString(2).split("").reduce((x,y)=>x^Number(y),0):(z>>p)&1);
    const rows=states.map(({len,p,z})=>states.map(t=>p<len-1?(t.len===len&&t.p===p+1&&t.z===z?d:0):(t.p===0?2**(k+1-t.len):0)));
    const weights=states.map(s=>2**(k+1-s.len));
    return L.model(labels,rows,weights);
  }
  function perms(a){if(!a.length)return [[]];return a.flatMap((v,i)=>perms(a.filter((_,j)=>j!==i)).map(p=>[v,...p]))}
  // Independent probability calculation by explicit hidden-path traversal
  // for small models. No matrix advance or row-span pruning.
  function pathWord(m,s){
    function visit(i,t){if(t===s.length)return 1n;if(m.labels[i]!==Number(s[t]))return 0n;let out=0n;for(let j=0;j<m.n;j++)if(m.A[i][j])out+=m.A[i][j]*visit(j,t+1);return out}
    let num=0n;for(let i=0;i<m.n;i++)num+=m.w[i]*visit(i,0);
    return [num,m.W*m.d**BigInt(s.length)]
  }
  function brute(m,s){
    const bound=m.n+s.n-1;
    for(let n=1;n<=bound;n++)for(let i=0;i<2**n;i++){
      const w=i.toString(2).padStart(n,"0"),[a,b]=pathWord(m,w),[c,d]=pathWord(s,w);
      if(a*d!==b*c)return {equal:false,length:n,witness:w};
    }
    return {equal:true};
  }
  function run(){
    const aperiodic=[3,4].map(k=>{const m=mixed(k),r=L.classify(m);assert(r.pairLags.equal&&!r.words.equal&&r.words.witness.length===k,"mixed parity");return {minimum_block:k,...r}});
    const cross=[];
    for(let n=2;n<=4;n++){
      const ps=perms(Array.from({length:n},(_,i)=>i));let total=0,eq=0,pairOnly=0,weakOnly=0,rev=0;
      for(const p of ps)for(const q of ps){
        const A=p.map((x,i)=>p.map((_,j)=>Number(x===j)+Number(q[i]===j)));
        for(let mask=2;mask<2**n;mask+=2){
          const b=Array.from({length:n},(_,i)=>(mask>>i)&1),m=L.model(b,A,Array(n).fill(1)),s=L.surrogate(m),e=L.equivalence(m,s),v=brute(m,s),lag=L.allLags(m,s);
          assert(e.equal===v.equal&&(e.equal||e.witness.length===v.length),"independent shortest word");
          assert(!e.equal||lag.equal,"word equality entails pair equality");
          if(L.reversible(m)){rev++;assert(L.strong(m)===e.equal,"reversible equivalence")}
          total++;if(e.equal){eq++;if(!L.strong(m))weakOnly++;}else if(lag.equal)pairOnly++;
        }
      }
      cross.push({states:n,total,word_equivalent:eq,weak_only:weakOnly,all_pair_lags_but_not_words:pairOnly,reversible:rev});
    }
    return {aperiodic,cross};
  }
  return {mixed,pathWord,brute,run};
}
export const extended = extension(laboratory);
