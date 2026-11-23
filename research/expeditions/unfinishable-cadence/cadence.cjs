// MHAC #211. Node.js 18+; no dependencies. Exact exponential cut oracle, not a receiver.
function gcd(a,b){while(b)[a,b]=[b,a%b];return a}

function validate(p,q,ticks){if(!Number.isSafeInteger(p)||!Number.isSafeInteger(q)||p<1||q<1||p+q>24||!Array.isArray(ticks)||ticks.some(t=>!Number.isSafeInteger(t)||t<0)||new Set(ticks).size!==ticks.length)throw Error("positive periods, total <=24, distinct nonnegative integer ticks required")}

function cut(p,q,ticks){
 validate(p,q,ticks);const g=gcd(p,q);let best=Infinity,witness=null;
 for(let r=0;r<g;r++){
  const vertices=[];for(let i=r;i<p;i+=g)vertices.push(i);for(let j=r;j<q;j+=g)vertices.push(p+j);
  const loc=new Map(vertices.map((v,i)=>[v,i]));const edges=ticks.filter(t=>t%g===r).map(t=>[loc.get(t%p),loc.get(p+t%q)]);
  // Fix first vertex to zero; omit all-zero labeling. Complement symmetry.
  for(let m=1;m<2**(vertices.length-1);m++){
   const bits=m*2;let d=0;for(const [a,b] of edges)d+=((bits>>a)^(bits>>b))&1;
   if(d<best){best=d;const labels=Array(p+q).fill(0);vertices.forEach((v,i)=>labels[v]=(bits>>i)&1);witness={left:labels.slice(0,p),right:labels.slice(p),residue:r};}
  }
 }
 return {distance:best,...witness};
}

function brute(p,q,ticks){let best=Infinity;const cycle=p*q/gcd(p,q);for(let a=0;a<2**p;a++)for(let b=0;b<2**q;b++){let different=false;for(let t=0;t<cycle;t++)if(((a>>(t%p))^(b>>(t%q)))&1){different=true;break}if(!different)continue;let d=0;for(const t of ticks)d+=((a>>(t%p))^(b>>(t%q)))&1;best=Math.min(best,d)}return best}

function prefix(n){return Array.from({length:n},(_,i)=>i)}

function mismatch(w,t){return w.left[t%w.left.length]!==w.right[t%w.right.length]}

function render(w,n){const frames=1200,rate=8000,buffer=new Uint8Array(44+n*frames*4),v=new DataView(buffer.buffer);function tag(at,s){for(let i=0;i<s.length;i++)buffer[at+i]=s.charCodeAt(i)}tag(0,"RIFF");v.setUint32(4,buffer.length-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,2,true);v.setUint32(24,rate,true);v.setUint32(28,rate*4,true);v.setUint16(32,4,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,buffer.length-44,true);for(let t=0;t<n;t++)for(let i=0;i<frames;i++)for(let c=0;c<2;c++){const word=c?w.right:w.left,bit=word[t%word.length],period=bit?16:24;const amp=i<640?Math.floor(6000*Math.min(i,640-i,40)/40):0;v.setInt16(44+4*(t*frames+i)+2*c,(i%period<period/2?amp:-amp),true)}return buffer}

function verify(){let cases=0,prefixCases=0;for(let p=1;p<=5;p++)for(let q=1;q<=5;q++){const n=p+q-gcd(p,q);for(let mask=0;mask<2**n;mask++){const ts=prefix(n).filter(t=>(mask>>t)&1),w=cut(p,q,ts);if(w.distance!==brute(p,q,ts)||ts.filter(t=>mismatch(w,t)).length!==w.distance||!prefix(p*q/gcd(p,q)).some(t=>mismatch(w,t)))throw Error("oracle mismatch");cases++}}for(let p=1;p<=10;p++)for(let q=1;q<=10;q++){const n=p+q-gcd(p,q);if(cut(p,q,prefix(n-1)).distance!==0||cut(p,q,prefix(n)).distance!==1)throw Error("Fine-Wilf mismatch");prefixCases++}const w=cut(5,7,prefix(10));const wav=render(w,22),v=new DataView(wav.buffer);let first=null;for(let i=0;i<22*1200;i++)if(v.getInt16(44+i*4,true)!==v.getInt16(46+i*4,true)){first=Math.floor(i/1200);break}if(first!==10)throw Error("audio mismatch");const robust=[];for(let r=0;r<=3;r++){let n=0;while(cut(5,7,prefix(n)).distance<=2*r)n++;robust.push({errors:r,ticks:n,distance:cut(5,7,prefix(n)).distance})}let invalid=false;try{cut(2,3,[0,0])}catch{invalid=true}if(!invalid)throw Error("duplicate tick accepted");return {mask_cases:cases,sharp_prefix_cases:prefixCases,witness:w,first_audio_difference_tick:first,robust}}

const result=verify(); console.log(JSON.stringify(result,null,2));
if(process.argv[2]) require('node:fs').writeFileSync(process.argv[2],render(cut(5,7,prefix(10)),22));
