import { laboratory as L } from './memory.mjs';
import { extended as E } from './extension.mjs';
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const here = name => new URL(name, import.meta.url);
for (const [run,name] of [[L.run,'results.synthetic.txt'],[E.run,'extension.synthetic.txt']]) {
  assert.equal(JSON.stringify(run(),null,2)+'\n',readFileSync(here(name),'utf8'));
}
const m=L.model([0,0,1,1],[[1,1,0,0],[0,1,1,0],[1,0,0,1],[0,0,1,1]],[1,1,1,1]);
const s=L.surrogate(m);
const r=L.classify(m);
assert.equal(r.pairLags.equal,true);
assert.equal(r.strong,false);
assert.equal(r.reversible,false);
assert.equal(r.words.witness,'000');
assert.equal(r.words.p,'1/4');
assert.equal(r.words.q,'9/32');
const words=Array.from({length:8},(_,i)=>i.toString(2).padStart(3,'0')).map(w=>({word:w,micro:L.word(m,w),surrogate:L.word(s,w)}));
assert.deepEqual(words,[{"word":"000","micro":"1/4","surrogate":"9/32"},{"word":"001","micro":"1/8","surrogate":"3/32"},{"word":"010","micro":"1/16","surrogate":"1/32"},{"word":"011","micro":"1/16","surrogate":"3/32"},{"word":"100","micro":"1/8","surrogate":"3/32"},{"word":"101","micro":"0/1","surrogate":"1/32"},{"word":"110","micro":"1/16","surrogate":"3/32"},{"word":"111","micro":"5/16","surrogate":"9/32"}]);
for(const invalid of [
  ()=>L.model([0,1],[[1,0],[1,0]],[1,1]),
  ()=>L.model([0,1],[[1,1],[0,1]],[1,1]),
  ()=>L.model([0,1],[[2,-1],[0,1]],[1,1])
])assert.throws(invalid);
console.log('PASS: exact synthetic receipts, compact all-lag witness, malformed-model rejection');
console.log(JSON.stringify(words));
