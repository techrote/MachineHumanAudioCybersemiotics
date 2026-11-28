'use strict';
// Measurement #442. Native regression for the v2 receipt repair; no human data.
// Expected hashes captured from the blob-verified v1 CLI at 92db2601aae859f0860eecb0acd03f44049688db.
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const {verifyDevelopment}=require('./onset-calibration.cjs');
const script=path.join(__dirname,'onset-calibration.cjs'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const expected={rows:'330160537d828c75afcd0b6848e639519577502071830a6cd8cea43cfaf37cde',summary:'a80116191498cd8227dcfc76127a39bc01989b145aaeb8fc7bb76507ea70eaa8',overall:'2d7d5da62602f757ff975ace55059fe71b9c7c449cd0ee5a1efe9c99b1a21100',calibration:'f0a9a1ccbf97c31b1cb73594faee2ff617da3ef769d2c3ff9c8e6593be2721dd',witnessHash:'1db23bd7d511339ba3ee37f65dcb842c5799a7a64b230da2be2937df305f19b2'};
const files={'index.html':'1fffb2a9120d803785cca9ea833f1544820389716ccc46d8bf22f8ce01555791','clean.wav':'e5944abc7056302540dff902078214b4c266c667fa825ac32ad58187faf522a0','noisy.wav':'843f4efeb89d2641de784721835706edae8925f1bb666d5563b3f4dbd7154491','alias-clean.wav':'66ed57a89d2d13c7f5ce7378cf71133d4bf9fed09d4b53ebbefc617d7c037373','alias-noisy.wav':'c30acec49d0c913fe6beb567a262fdeb70c4c3e09d1a1f77539d88592444f896'};
const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-onset-v2-')),a=path.join(root,'a'),b=path.join(root,'b');
function cli(...args){return cp.execFileSync(process.execPath,[script,...args],{encoding:'utf8'})}
function json(dir,n){return JSON.parse(fs.readFileSync(path.join(dir,n),'utf8'))}
try{
 cli(a);cli(b);
 const d=json(a,'receipt.json'),m=json(a,'manifest.json');
 assert.equal(d.schema,'mhac-onset-calibration-v2');assert.equal(m.schema,d.schema);assert.equal(m.scriptSHA256,hash(fs.readFileSync(script)));
 assert.equal(d.rows.length,960);assert.equal(d.development.length,144);
 for(const [k,h] of Object.entries(expected))assert.equal(hash(JSON.stringify(d[k])),h,k);
 for(const [n,h] of Object.entries(files))assert.equal(hash(fs.readFileSync(path.join(a,n))),h,n);
 assert.deepEqual(Object.keys(m.files).sort(),['receipt.json',...Object.keys(files)].sort());
 for(const [n,h] of Object.entries(m.files))assert.equal(hash(fs.readFileSync(path.join(a,n))),h,n);
 for(const n of fs.readdirSync(a))assert(fs.readFileSync(path.join(a,n)).equals(fs.readFileSync(path.join(b,n))),n);
 assert.deepEqual(JSON.parse(cli('--verify-development',path.join(a,'receipt.json'))),d.developmentAudit);
 const corruptions=[r=>delete r.development[0].templateScore,r=>r.development[0].templateScore+=.001,r=>r.development[0].wavSHA256='0'.repeat(64),r=>r.development[0]=r.development[1],r=>r.development.pop(),r=>r.calibration[8000].template+=.001,r=>r.development[0].templateEstimate=0,r=>r.developmentAudit[0].templateMaxWitnesses=[]];
 for(const corrupt of corruptions){const r=structuredClone(d);corrupt(r);assert.throws(()=>verifyDevelopment(r),assert.AssertionError)}
 console.log(JSON.stringify({status:'PASS',evaluationRows:d.rows.length,developmentRows:d.development.length,priorPayloadHashes:Object.keys(expected).length,priorGalleryHashes:Object.keys(files).length,manifestFiles:Object.keys(m.files).length,negativeControls:corruptions.length,repeatFiles:fs.readdirSync(a).length,receiptSHA256:m.files['receipt.json']},null,2));
}finally{fs.rmSync(root,{recursive:true,force:true})}
