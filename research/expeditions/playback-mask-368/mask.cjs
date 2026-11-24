// Synthetic/formal expedition #368. No dependencies.
function checkSize(n) {
  if (!Number.isInteger(n)||n<3||n>128) throw Error("cycle length must be 3..128");
}
function tick(x) {
  if (!Number.isInteger(x)||x<0||x>10000) throw Error("gain ticks must be integers 0..10000");
}
function compile(n, anchors) {
  checkSize(n);
  if (!Array.isArray(anchors)||!anchors.length) throw Error("need anchors");
  let a=anchors.map(([i,v])=>{
    if(!Number.isInteger(i)||i<0||i>=n) throw Error("bad anchor index");
    tick(v);return [i,v];
  }).sort((x,y)=>x[0]-y[0]);
  if(new Set(a.map(x=>x[0])).size!==a.length) throw Error("duplicate anchor");
  let g=Array(n), arcs=[];
  for(let j=0;j<a.length;j++){
    let [i,v]=a[j], [k,w]=a[(j+1)%a.length];
    let L=(k-i+n)%n||n, delta=w-v, q=Math.floor(Math.abs(delta)/L), rem=Math.abs(delta)%L;
    for(let t=0;t<L;t++) g[(i+t)%n]=v+Math.sign(delta)*Math.floor(t*Math.abs(delta)/L);
    arcs.push({start:i,length:L,delta,minimumSquaredJumpSum:(L-rem)*q*q+rem*(q+1)**2,minimumMaxJump:q+Number(rem>0)});
  }
  let diffs=g.map((v,i)=>v-g[(i+1)%n]);
  return {g,arcs,energyTimes4:diffs.reduce((s,x)=>s+x*x,0),operatorNormTimes2:Math.max(...diffs.map(Math.abs))};
}
// Independent plus/minus gain ticks: 16 * squared Frobenius leakage.
function leakage16(pairs){
  checkSize(pairs.length);
  for(const p of pairs){if(p.length!==2)throw Error("need two gains");p.forEach(tick);}
  return pairs.reduce((s,p,i)=>s+p.reduce((a,x)=>a+pairs[(i+1)%pairs.length].reduce((b,y)=>b+(x-y)**2,0),0),0);
}
function analyze(x) {
  checkSize(x.length);
  return x.flatMap((v,i)=>[(v+x[(i+1)%x.length])/2,(v-x[(i+1)%x.length])/2]);
}
function synthesize(c){
  const n=c.length/2;checkSize(n);
  return Array.from({length:n},(_,i)=>{
    let j=(i+n-1)%n;return (c[2*i]+c[2*i+1]+c[2*j]-c[2*j+1])/2;
  });
}
function apply(x,pairs) {
  if(x.length!==pairs.length)throw Error("size mismatch");
  leakage16(pairs);
  const target=analyze(x).map((v,i)=>v*pairs[i>>1][i%2]);
  const signal=synthesize(target), projected=analyze(signal);
  return {target,signal,projected,residual:target.map((v,i)=>v-projected[i])};
}
if(typeof module!=="undefined") module.exports={compile,leakage16,analyze,synthesize,apply};
