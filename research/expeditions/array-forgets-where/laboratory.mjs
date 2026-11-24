// MHAC #308 — standalone Node 18+; no dependencies.
function laboratory(){
  const check=(v,msg)=>{if(!v)throw Error(msg)};
  const gcd=(a,b)=>{a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b]}return a};
  const mod=(a,p)=>((a%p)+p)%p;
  const grid=a=>a.flatMap(x=>a.map(y=>[x,y]));
  const range=n=>Array.from({length:n},(_,i)=>i);
  const prime=n=>n>=2&&range(Math.floor(Math.sqrt(n))-1).every(i=>n%(i+2)!==0);
  const pop=m=>{let n=0;while(m){m&=m-1;n++}return n};
  function index(S){
    if(S.length<3)return 0;
    const [x,y]=S[0],d=S.slice(1).map(([a,b])=>[a-x,b-y]);
    let g=0;
    for(let i=0;i<d.length;i++)for(let j=0;j<i;j++){
      g=gcd(g,d[i][0]*d[j][1]-d[i][1]*d[j][0]);if(g===1)return 1;
    }
    return g;
  }
  function lines(S,p){
    const result=new Set();
    for(let a=0;a<=p;a++){
      const masks=Array(p).fill(0);
      S.forEach(([x,y],i)=>{const c=mod(a===p?x:y-a*x,p);masks[c]|=1<<i});
      masks.forEach(m=>result.add(m));
    }
    return [...result];
  }
  function census(n){
    const S=grid(range(n)),N=S.length;
    const ps=range(2*(n-1)**2+1).filter(prime);
    const masks=[...new Set(ps.flatMap(p=>lines(S,p)))];
    // Subset closure of modular line masks, not determinant computation.
    const bad=new Uint8Array(1<<N);
    for(const l of masks){let m=l;while(m){bad[m]=1;m=(m-1)&l}}
    let max=0,badCount=0,checks=0;
    for(let m=1;m<(1<<N);m++){
      const A=S.filter((_,i)=>m&(1<<i)),b=index(A)!==1;
      check(b===Boolean(bad[m]),"modular versus determinant mismatch");
      if(b){max=Math.max(max,A.length);badCount++}checks++;
    }
    check(max===n*Math.ceil(n/2),"square distance");
    return {n,N,primes:ps,subset_checks:checks,nonidentifying_subsets:badCount,largest_bad:max,distance:N-max};
  }
  function sparse(M){
    const S=grid([0,M,M+2,2*M+2]),N=S.length;
    let tests=0;
    for(let mask=1;mask<(1<<N);mask++)if(pop(mask)===9){
      check(index(S.filter((_,i)=>mask&(1<<i)))===1,"sparse 9-subset");
      tests++;
    }
    const bad=S.filter(([x])=>x%2===0);
    check(bad.length===8&&index(bad)!==1,"parity certificate");
    const q=2*M,a=M-1;
    const residues=S.map(([x])=>mod(x*a,q));
    check(residues.every(t=>t===0||t===q-2),"near alias residues");
    check(residues.filter(t=>t===0).length===8,"near alias balance");
    // Choose common phase +1/(2M): all errors are +/-1/(2M) cycles.
    return {M,aperture:2*M+2,subset_checks:tests,distance:8,spatial_separation:a/q,phase_error_cycles:1/q,max_chord_error:2*Math.sin(Math.PI/q)};
  }
  function finiteGrid(n,q){
    const S=grid(range(n));
    let max=0;
    for(let u=0;u<q;u++)for(let v=0;v<q;v++)if(u||v){
      const counts=Array(q).fill(0);
      for(const [x,y] of S)counts[mod(x*u+y*v,q)]++;
      max=Math.max(max,...counts);
    }
    return {n,q,distance:S.length-max};
  }
  // Original deterministic phase sonification, one tone per sensor, serial
  // slots. Exact integer phases before trigonometry. WAV PCM mono 8 kHz.
  function wav(S,q,a,phase){
    const frames=400*S.length,buf=new Uint8Array(44+2*frames),v=new DataView(buf.buffer);
    const str=(i,s)=>{for(let j=0;j<s.length;j++)buf[i+j]=s.charCodeAt(j)};
    str(0,"RIFF");v.setUint32(4,buf.length-8,true);str(8,"WAVE");str(12,"fmt ");
    v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
    v.setUint32(24,8000,true);v.setUint32(28,16000,true);v.setUint16(32,2,true);
    v.setUint16(34,16,true);str(36,"data");v.setUint32(40,2*frames,true);
    for(let i=0;i<S.length;i++)for(let j=0;j<400;j++){
      const angle=2*Math.PI*(j/20+mod(S[i][0]*a+phase,q)/q);
      const env=Math.min(1,j/20,(399-j)/20);
      v.setInt16(44+2*(400*i+j),Math.round(10000*env*Math.sin(angle)),true);
    }
    return buf;
  }
  const equal=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);
  const hash=a=>{let h=2166136261;for(const b of a)h=Math.imul(h^b,16777619)>>>0;return h.toString(16).padStart(8,"0")};
  const pcmDiff=(a,b)=>{check(a.length===b.length,"PCM length");const av=new DataView(a.buffer),bv=new DataView(b.buffer);let m=0;for(let i=44;i<a.length;i+=2)m=Math.max(m,Math.abs(av.getInt16(i,true)-bv.getInt16(i,true)));return m};
  const S=grid([0,101,103,204]),E=S.filter(([x])=>x%2===0);
  const a=wav(S,2,0,0),b=wav(S,2,1,0),c=wav(E,2,0,0),d=wav(E,2,1,0);
  check(!equal(a,b)&&equal(c,d),"parity audio witness");
  const e=wav(S,202,0,0),f=wav(S,202,100,1);
  check(!equal(e,f)&&pcmDiff(e,f)<=Math.ceil(20000*Math.sin(Math.PI/202))+1,"near alias PCM bound");
  const square=[2,3,4].map(census),sparseCases=[3,5,11,101,1001,10001].map(sparse);
  const finite=[2,3,4].flatMap(n=>[2,3,4,5,6,7,8,9].map(q=>finiteGrid(n,q)));
  for(const x of finite)check(x.distance>=square.find(s=>s.n===x.n).distance,"finite grid lower bound");
  return {model:"synthetic projective phase, exact integer lattice",square,sparse:sparseCases,finite_phase_grids:finite,
    audio:{full_distinct:!equal(a,b),erased_identical:equal(c,d),near_distinct:!equal(e,f),near_max_pcm_difference:pcmDiff(e,f),
      full_bytes:a.length,erased_bytes:c.length,fnv1a:[a,b,c,d,e,f].map(hash)},assertion_failures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
