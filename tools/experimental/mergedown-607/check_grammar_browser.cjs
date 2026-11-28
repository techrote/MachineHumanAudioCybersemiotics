// Refs #607. Ordinary file navigation and DOM interactions; no playback.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {spawn} = require('node:child_process');
const assert = require('node:assert/strict');
const pause = ms => new Promise(r => setTimeout(r, ms));
async function until(fn) {
  for (let i=0;i<200;i++) { const r=await fn(); if(r) return r; await pause(100); }
  throw Error('Timed out waiting for browser');
}
async function main() {
  const root=path.resolve(process.argv[2]), exe=process.argv[3] || 'google-chrome';
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-browser-'));
  let stderr='', ws, chrome=spawn(exe,['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{stdio:['ignore','ignore','pipe']});
  let launchError; chrome.on('error',e=>launchError=e); chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-8000));
  const errors=[], checks=[];
  try {
    const port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null)throw Error('Chrome exit '+chrome.exitCode);try{return fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]}catch{return null}});
    const page=await until(async()=>{const a=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();return a.find(x=>x.type==='page')});
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true})});
    let seq=0; const pending=new Map();
    ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text+' '+(x.params.exceptionDetails.exception?.description||''))});
    const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},30000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
    await call('Runtime.enable'); await call('Page.enable');
    async function evalJS(expression) {const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
    async function nav(name) {const url=pathToFileURL(path.join(root,name)).href;const r=await call('Page.navigate',{url});if(r.errorText)throw Error(r.errorText);await until(async()=>{try{return await evalJS(`location.href===${JSON.stringify(url)} && document.readyState==='complete'`)}catch{return false}});assert.equal(await evalJS('location.protocol'),'file:');checks.push('file navigation '+name)}
    async function check(label,expr) {assert.ok(await evalJS(expr),label);checks.push(label)}
    const change=(id,value)=>`(()=>{const x=document.getElementById('${id}');x.value='${value}';x.dispatchEvent(new Event('change',{bubbles:true}));return x.value==='${value}'})()`;
    await nav('index.html');
    await check('24 buttons and one paused audio element', "document.querySelectorAll('button[data-src]').length===24 && document.querySelectorAll('audio').length===1 && player.paused && !player.autoplay && player.volume===.2");
    await check('select erased marker without playback', "(()=>{document.querySelector('button[data-src=\"bound-reproduced/marker-erased.wav\"]').click();return player.getAttribute('src')==='bound-reproduced/marker-erased.wav' && player.paused && document.querySelector('#selection').textContent==='marker-erased.wav'})()");
    await check('adjust digital gain', "(()=>{gain.value='.07';gain.dispatchEvent(new Event('input',{bubbles:true}));return Math.abs(player.volume-.07)<1e-7 && document.querySelector('#level').textContent==='7%'})()");
    await check('select erased polynomial and retain gain', "(()=>{document.querySelector('button[data-src=\"bound-reproduced/polynomial-erased.wav\"]').click();return player.getAttribute('src')==='bound-reproduced/polynomial-erased.wav' && player.paused && Math.abs(player.volume-.07)<1e-7})()");
    for(const group of ['prefix1','bridge-reproduced','bound-reproduced']){
      await nav(group+'/index.html');
      await check(group+' eight opt-in controls', "document.querySelectorAll('audio').length===8 && Array.from(document.querySelectorAll('audio')).every(a=>a.controls && !a.autoplay && a.paused && a.volume===.2)");
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({status:'PASS',browser:await (await fetch(`http://127.0.0.1:${port}/json/version`)).json(),checks,errors,scope:'ordinary file navigation, DOM controls, no actual playback or download validation'},null,2));
  } catch(e) {console.error(JSON.stringify({status:'FAIL',error:String(e),checks,errors,stderr},null,2));process.exitCode=1}
  finally {if(ws)ws.close();chrome.kill();await pause(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
main().catch(e=>{console.error(e);process.exitCode=1});
