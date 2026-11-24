import {census} from "./decay.mjs";
import {readFileSync} from "node:fs";
const actual=JSON.stringify(census(),null,2)+"\n";
if(process.argv.includes("--check")){if(actual!==readFileSync(new URL("./results.synthetic.txt",import.meta.url),"utf8"))throw Error("receipt mismatch");console.log("PASS: exact receipt");}else process.stdout.write(actual);
