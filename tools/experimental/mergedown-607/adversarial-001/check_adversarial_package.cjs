// Refs #607. Native filesystem checks and ordinary local-file Chrome qualification.
// No audio playback, external navigation, or participant data.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const assert = require('node:assert/strict');
const {createHash} = require('node:crypto');
const {pathToFileURL} = require('node:url');
const {spawn} = require('node:child_process');
const sha = b => createHash('sha256').update(b).digest('hex');
const root = path.resolve(process.argv[2]);
const galleries = {'binding/boundary1/index.html':16,'overlap/overlap1/index.html':18};
function walk(dir) {
  return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{
    const p=path.join(dir,e.name);
    assert.ok(e.isFile()||e.isDirectory(),'nonregular entry '+p);
    return e.isDirectory()?walk(p):[path.relative(root,p).split(path.sep).join('/')];
  });
}
function verify(manifest) {
  const names=walk(root).filter(x=>x!=='manifest.json').sort();
  assert.equal(names.length,68);
  assert.deepEqual(Object.keys(manifest).sort(),names);
  for(const n of names) assert.equal(sha(fs.readFileSync(path.join(root,n))),manifest[n],n);
  assert.equal(manifest['audit.json'],'7305352143d2ebe6fd91e9e2d0630a470a8ab1edd575efd6e4c33b63bb0b92d2');
  for(const [g,count] of Object.entries(galleries)) {
    const prefix=g.slice(0,-'index.html'.length);
    assert.equal(names.filter(n=>n.startsWith(prefix)&&n.endsWith('.wav')).length,count);
  }
  return names.length;
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn) {
  for(let i=0;i<100;i++){const x=await fn();if(x)return x;await sleep(150)}
  throw Error('browser readiness/navigation timed out');
}
async function browser(exe) {
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-adv-browser-'));
  const flags=['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
  if(process.platform==='linux'&&process.getuid?.()===0) flags.unshift('--no-sandbox');
  const chrome=spawn(exe,flags,{stdio:['ignore','ignore','pipe']});
  let stderr='',launchError,ws; const errors=[],checks=[];
  chrome.on('error',e=>launchError=e);chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-4000));
  try {
    const port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null)throw Error('Chrome exit '+chrome.exitCode);try{return fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0].trim()}catch{return null}});
    const get=async p=>(await fetch(`http://127.0.0.1:${port}${p}`,{signal:AbortSignal.timeout(3000)})).json();
    const page=await until(async()=>{try{return (await get('/json/list')).find(x=>x.type==='page')}catch{return null}});
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CDP open timeout')),5000);ws.addEventListener('open',()=>{clearTimeout(t);resolve()},{once:true});ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP open error'))},{once:true})});
    let seq=0;const pending=new Map();
    ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text)});
    const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
    const evalJS=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
    const url=n=>pathToFileURL(path.join(root,n)).href;
    const ready=async n=>until(async()=>{try{return await evalJS(`location.href===${JSON.stringify(url(n))} && document.readyState==='complete'`)}catch{return false}});
    const nav=async n=>{const r=await call('Page.navigate',{url:url(n)});assert.ok(!r.errorText,r.errorText);await ready(n)};
    await call('Runtime.enable');await call('Page.enable');
    for(const [g,count] of Object.entries(galleries)) {
      await nav('index.html');
      assert.equal(await evalJS(`document.querySelectorAll('a[href="${g}"]').length`),1);
      // Click the real anchor; the scheduled callback avoids navigation destroying the evaluation context.
      await evalJS(`setTimeout(()=>document.querySelector('a[href="${g}"]').click(),50);true`);
      await ready(g); checks.push('root link '+g);
      const actual=await evalJS(`Array.from(document.querySelectorAll('audio'),a=>({src:a.getAttribute('src'),controls:a.controls,autoplay:a.autoplay,paused:a.paused,volume:a.volume}))`);
      assert.equal(actual.length,count);
      const expected=fs.readdirSync(path.dirname(path.join(root,g))).filter(n=>n.endsWith('.wav')).sort();
      assert.deepEqual(actual.map(a=>a.src).sort(),expected);
      assert.ok(actual.every(a=>a.controls&&!a.autoplay&&a.paused&&a.volume===.2));checks.push(`${count} opt-in local audio controls at 20%`);
      assert.ok(await evalJS(`(()=>{const a=document.querySelector('audio');a.volume=.07;return a.paused&&Math.abs(a.volume-.07)<1e-7})()`));checks.push('gain change without playback '+g);
    }
    assert.deepEqual(errors,[]);
    return {status:'PASS',browser:await get('/json/version'),checks,errors};
  }catch(e){console.error(JSON.stringify({status:'FAIL',error:String(e),checks,errors,stderr}));throw e}
  finally{if(ws)ws.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
async function main(){
  const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
  const entries=verify(m);
  const missing={...m};delete missing['audit.json'];assert.throws(()=>verify(missing));
  assert.throws(()=>verify({...m,'audit.json':'0'.repeat(64)}));
  assert.throws(()=>verify({...m,'unexpected.txt':'0'.repeat(64)}));
  const receipt={schema:'mhac.adv-package-qualification/1',platform:process.platform,node:process.version,entries,negative_controls:3,browser:{status:'NOT_RUN'}};
  if(process.argv[3]!=='--static-only')receipt.browser=await browser(process.argv[3]||'google-chrome');
  console.log(JSON.stringify(receipt,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
