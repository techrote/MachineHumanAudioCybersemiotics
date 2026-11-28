'use strict';
// Capability probe, not a durability proof. Frozen modules are called unchanged.
const fs=require('node:fs'), os=require('node:os'), path=require('node:path'), assert=require('node:assert/strict');
const role=require('./source/role-v29.cjs');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-dirprobe-'));
const report={platform:process.platform,node:process.version,scope:'temporary synthetic filesystem; no power-loss test',checks:{}};
function test(name,fn){try{fn();report.checks[name]={status:'PASS'}}catch(e){report.checks[name]={status:'FAIL',code:e.code??null,syscall:e.syscall??null,message:e.message};}}
try{
  test('file_fsync',()=>{const f=fs.openSync(path.join(tmp,'ordinary'),'wx');try{fs.writeFileSync(f,'probe');fs.fsyncSync(f)}finally{fs.closeSync(f)}});
  test('directory_open',()=>{const f=fs.openSync(tmp,'r');fs.closeSync(f)});
  test('directory_fsync',()=>{const f=fs.openSync(tmp,'r');try{fs.fsyncSync(f)}finally{fs.closeSync(f)}});
  test('frozen_role_provision_reopen',()=>{const d=path.join(tmp,'role');role.provision(d,true);const s=role.receiver(d).snapshot();assert.equal(s.durable,true);assert.equal(s.count,0);assert.equal(s.active,0)});
}finally{fs.rmSync(tmp,{recursive:true,force:true})}
report.status=Object.values(report.checks).every(x=>x.status==='PASS')?'CAPABILITY_PASS':'CAPABILITY_FAIL';
console.log(JSON.stringify(report,null,2));
// A failed capability is retained as evidence, not treated as runtime qualification.
