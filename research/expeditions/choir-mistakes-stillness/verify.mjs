import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve} from "node:path";
import {run,audioCases} from "./laboratory.mjs";
import {microCensus} from "./microcheck.mjs";
import {countingCensus} from "./arithmetic.mjs";

const expected=name=>JSON.parse(readFileSync(new URL(name,import.meta.url),"utf8"));
const check=(actual,name)=>{
  if(JSON.stringify(actual)!==JSON.stringify(expected(name)))throw Error("receipt mismatch: "+name);
};
const args=process.argv.slice(2);
if(args.length!==0&&(args.length!==2||args[0]!=="--audio-dir"))throw Error("usage: node verify.mjs [--audio-dir DIRECTORY]");
const main=run(),micro=microCensus(),arithmetic=countingCensus();
check(main,"execution.json");
check(micro,"micro-execution.json");
check(arithmetic,"arithmetic-execution.json");
for(const row of micro.rows){
  if(BigInt(row.orderErasure)!==BigInt(arithmetic.rows.find(v=>v.n===row.n).orderErasure))throw Error("cross-check mismatch");
}
if(args.length){
  const dir=resolve(args[1]);mkdirSync(dir,{recursive:true});
  for(const [name,w] of Object.entries(audioCases()))writeFileSync(resolve(dir,name+".wav"),w,{flag:"wx"});
}
console.log(JSON.stringify({result:"pass",tables:main.totals,expandedInputs:micro.initialVectors,arithmeticTables:arithmetic.tables},null,2));
