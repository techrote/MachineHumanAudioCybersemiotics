// Extract and run the exact model from the standalone HTML. Node.js, no dependencies.
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"index.html"),"utf8");
const source=html.slice(html.indexOf("function makeModel(){"),html.indexOf("const model=makeModel()"));
const m=vm.runInNewContext(source+"\nmakeModel()");
let checks=0;
function check(v,msg){if(!v)throw Error(msg);checks++}
const baseline=m.pcm(),same=m.pcm();let peak=0,nonzero=0,checksum=2166136261;
for(let i=0;i<baseline.length;i++){check(baseline[i]===same[i],"repeat");peak=Math.max(peak,Math.abs(baseline[i]));if(baseline[i])nonzero++;checksum=Math.imul(checksum^(baseline[i]&65535),16777619)>>>0; const active=m.times.some(t=>i>=t*m.rate&&i<t*m.rate+.35*m.rate);if(!active)check(baseline[i]===0,"silence outside events")}
let scenes=0;
for(const mode of m.modes)for(const lag of [-.3,-.15,0,.15,.3])for(let omit=-1;omit<6;omit++){const c=m.contacts(mode,lag,omit);check(c.length===(mode==="absent"?0:omit===-1?6:5),"count");for(const t of c)check(t>=0&&t<m.duration,"bounds");check(c.every((t,i)=>i===0||t>c[i-1]),"ordered");scenes++;}
check(peak<32767&&peak>0,"peak");
for(const args of [["bad",0,-1],["lever",.31,-1],["lever",0,6],["lever",NaN,-1]]){let rejected=false;try{m.contacts(...args)}catch(e){rejected=true}check(rejected,"reject")}
console.log(JSON.stringify({assertions:checks,scenes,frames:baseline.length,peak,nonzero,fnv1a_words:checksum.toString(16).padStart(8,"0")},null,2));
