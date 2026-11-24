import { readFileSync } from "node:fs";
import { experiment, solve, metrics } from "./dial.mjs";
const actual = {...experiment(), relaxedFive:solve(5,2,13,30000000)};
const expected=readFileSync(new URL("./results.synthetic.txt",import.meta.url),"utf8");
if(JSON.stringify(actual,null,2)+"\n"!==expected)throw new Error("synthetic receipt drift");
const w5=[0,1,4,2,8,16,17,18,20,24,12,6,3,5,9,10,26,25,21,19,22,28,14,13,7,11,27,23,15,30,29,31];
const w6=[0,1,16,48,32,8,2,34,40,36,33,5,4,6,20,12,24,10,18,3,9,17,49,52,50,56,44,41,42,38,35,7,37,21,13,14,22,28,26,25,11,19,51,54,53,57,60,58,46,45,43,39,15,23,30,27,29,31,47,62,59,55,61,63];
for(const [w,b] of [[w5,13],[w6,23]]){const m=metrics(w);if(m.jump!==2||m.span!==b)throw new Error("witness mismatch");}
console.log("PASS: receipt and additional witnesses");
