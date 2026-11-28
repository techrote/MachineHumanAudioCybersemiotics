'use strict';
// Refs #607: ordinary local Chrome, no playback or network stimuli.
const fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const assert=require('node:assert/strict'), {createHash}=require('node:crypto');
const {spawn}=require('node:child_process'), {pathToFileURL}=require('node:url');
const root=path.resolve(process.argv[2]);
const sha=b=>createHash('sha256').update(b).digest('hex');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{
  const p=path.join(dir,e.name); assert.ok(e.isDirectory()||e.isFile(),'nonregular '+p);
  return e.isDirectory()?walk(p):[path.relative(root,p).split(path.sep).join('/')];
});}
function verify(m){
  const files=walk(root).filter(n=>n!=='manifest.json').sort();
  assert.deepEqual(Object.keys(m).sort(),files);
  for(const n of files) assert.equal(sha(fs.readFileSync(path.join(root,n))),m[n],n);
  assert.equal(m['bound-v2-output/receipt.json'],'8fc53c22966b27e3ec62519271471431fe3b10b0f404c93f9ed9a57121ca450a');
  return files.length;
}
async function until(fn){for(let i=0;i<80;i++){const v=await fn();if(v)return v;await sleep(150);}throw Error('browser readiness timed out');}
async function browser(exe){
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-binding-'));
  const flags=['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
  if(process.platform==='linux'&&process.getuid?.()===0)flags.unshift('--no-sandbox');
  const chrome=spawn(exe,flags,{stdio:['ignore','ignore','pipe']});
  let stderr='',launchError,ws;const errors=[];
  chrome.on('error',e=>launchError=e);chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-4000));
  try{
    const port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null)throw Error('Chrome exit '+chrome.exitCode);try{return fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0].trim()}catch{return null}});
    const get=async p=>(await fetch(`http://127.0.0.1:${port}${p}`,{signal:AbortSignal.timeout(3000)})).json();
    const page=await until(async()=>{try{return (await get('/json/list')).find(x=>x.type==='page')}catch{return null}});
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CDP open timeout')),5000);ws.addEventListener('open',()=>{clearTimeout(t);resolve()},{once:true});ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP open error'))},{once:true})});
    let seq=0;const pending=new Map();
    ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text)});
    const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
    const evalJS=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
    await call('Runtime.enable');await call('Page.enable');
    const url=pathToFileURL(path.join(root,'index.html')).href;
    const nav=await call('Page.navigate',{url});assert.ok(!nav.errorText,nav.errorText);
    await until(async()=>{try{return await evalJS(`location.href===${JSON.stringify(url)} && document.readyState==='complete'`)}catch{return false}});
    const receipt=JSON.parse(fs.readFileSync(path.join(root,'bound-v2-output/receipt.json'),'utf8'));
    const actual=await evalJS(`Array.from(document.querySelectorAll('#witness tr'),tr=>[tr.cells[0].textContent,tr.cells[1].textContent])`);
    const expected=receipt.rows.map(r=>[r.name,(r.v1.length?'accept':'reject')+(r.name==='splice'||r.name==='recomputed-hybrid'?' hybrid':'')+' / '+(r.v2.length?'accept':'reject')+(r.name==='recomputed-hybrid'?' hybrid':'')]);
    assert.deepEqual(actual,expected);
    const players=await evalJS(`Array.from(document.querySelectorAll('audio'),a=>({src:a.getAttribute('src'),controls:a.controls,paused:a.paused,autoplay:a.autoplay,volume:a.volume}))`);
    assert.deepEqual(players.map(a=>a.src).sort(),receipt.stimuli.map(s=>'bound-v2-output/'+s.file).sort());
    assert.ok(players.every(a=>a.controls&&a.paused&&!a.autoplay&&Math.abs(a.volume-.12)<1e-7));
    for(const gain of [0,.07,.25]){
      assert.ok(await evalJS(`(()=>{const g=document.querySelector('#gain');g.value=${gain};g.dispatchEvent(new Event('input',{bubbles:true}));return document.querySelector('#gainOut').textContent===${JSON.stringify(Math.round(gain*100)+'%')}&&Array.from(document.querySelectorAll('audio')).every(a=>a.paused&&Math.abs(a.volume-${gain})<1e-7)})()`));
    }
    assert.ok(await evalJS(`(()=>{document.querySelector('#stop').click();return Array.from(document.querySelectorAll('audio')).every(a=>a.paused&&a.currentTime===0)})()`));
    assert.deepEqual(errors,[]);
    return {status:'PASS',browser:await get('/json/version'),witness_rows:actual.length,players:players.length,gain_controls:3,stop_controls:1,errors,playback:'NOT_RUN'};
  }catch(e){console.error(JSON.stringify({status:'FAIL',error:String(e),errors,stderr}));throw e}
  finally{if(ws)ws.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
async function main(){
  const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
  const entries=verify(m);const bad={...m};delete bad['index.html'];assert.throws(()=>verify(bad));
  assert.throws(()=>verify({...m,'index.html':'0'.repeat(64)}));assert.throws(()=>verify({...m,'extra.txt':'0'.repeat(64)}));
  const receipt={schema:'mhac.integration-browser/1',node:process.version,platform:process.platform,entries,negative_controls:3,browser:{status:'NOT_RUN'}};
  if(process.argv[3]!=='--static-only')receipt.browser=await browser(process.argv[3]||'google-chrome');
  console.log(JSON.stringify(receipt,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
