// Synthetic finite Fourier alias-block laboratory; Node >=18, no dependencies.
function check(q,C) {
  if (!Number.isInteger(q)||q<2||q>256||!Array.isArray(C)||!C.length||
      C.some(c=>!Number.isInteger(c)||c<0||c>=q)||new Set(C).size!==C.length)
    throw new RangeError("invalid grid or lane set");
}
export function primes(q) {
  const a=[]; for(let p=2;p<=q;p++) if(q%p===0){a.push(p);while(q%p===0)q/=p;}
  return a;
}
export function certificate(q,C) {
  check(q,C);
  let best={size:0};
  for(const p of primes(q)) for(let residue=0;residue<p;residue++){
    const keep=C.filter(c=>c%p===residue);
    if(keep.length>best.size)best={size:keep.length,p,residue,keep};
  }
  return {...best,erase:C.filter(c=>!best.keep.includes(c)),
    failGap:q/best.p, guaranteedErasures:C.length-best.size-1};
}
// Columns normalized by surviving lane count, not full acquisition count.
export function floor(q,C) {
  check(q,C);
  let coherence=-1,gap=0;
  for(let d=1;d<q;d++){
    let re=0,im=0;
    for(const c of C){const a=2*Math.PI*((c*d)%q)/q;re+=Math.cos(a);im+=Math.sin(a);}
    const mu=Math.hypot(re,im)/C.length;
    if(mu>coherence+1e-14){coherence=mu;gap=d;}
  }
  return {sigma:certificate(q,C).guaranteedErasures<0?0:Math.sqrt(Math.max(0,1-coherence)),gap,coherence};
}
export function* choose(a,k,start=0,prefix=[]) {
  if(k===0){yield prefix;return;}
  for(let i=start;i<=a.length-k;i++)yield* choose(a,k-1,i+1,[...prefix,a[i]]);
}
export function robustFloor(q,C,e) {
  check(q,C);
  if(!Number.isInteger(e)||e<0||e>=C.length)throw new RangeError("invalid erasure count");
  let best={sigma:Infinity};
  for(const keep of choose(C,C.length-e)){
    const f=floor(q,keep);
    if(f.sigma<best.sigma-1e-14)best={...f,keep};
  }
  return best;
}
export function search(q,m,e) {
  if(!Number.isInteger(q)||q<2||q>16||!Number.isInteger(m)||m<2||m>q||
     !Number.isInteger(e)||e<0||e>=m)throw new RangeError("search budget/domain");
  let best=-1,witness=null,ties=0,count=0;
  for(const C of choose(Array.from({length:q},(_,i)=>i),m)){
    const v=robustFloor(q,C,e).sigma;count++;
    if(v>best+1e-12){best=v;witness=C;ties=1;}
    else if(Math.abs(v-best)<=1e-12)ties++;
  }
  return {q,m,e,count,best,witness,ties,consecutive:robustFloor(q,Array.from({length:m},(_,i)=>i),e).sigma};
}
