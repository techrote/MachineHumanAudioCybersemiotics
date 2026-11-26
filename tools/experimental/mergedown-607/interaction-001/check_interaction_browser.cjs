// #607: native filesystem and local-file Chrome replay qualification; no playback.
const fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const assert=require('node:assert/strict'), {spawn}=require('node:child_process');
const {pathToFileURL}=require('node:url'), {createHash}=require('node:crypto');
const root=path.resolve(process.argv[2]), run=path.join(root,'run1');
const sha=b=>createHash('sha256').update(b).digest('hex');
const receipt=JSON.parse(fs.readFileSync(path.join(run,'receipt.json')));
assert.equal(sha(fs.readFileSync(path.join(run,'receipt.json'))),'8d1db0bfb48c9d473967842f140b1cda899f84716339651132dc64546571a60d');
const m=JSON.parse(fs.readFileSync(path.join(run,'manifest.json')));
assert.equal(sha(fs.readFileSync(path.join(run,'manifest.json'))),'e619850702050f6cc61091dd350244a67615bfec058ddd7c50540bd1a8f8e505');
assert.deepEqual(Object.keys(m).sort(),fs.readdirSync(run).filter(n=>n!=='manifest.json').sort());
for(const [n,h] of Object.entries(m)) assert.equal(sha(fs.readFileSync(path.join(run,n))),h,n);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn){for(let i=0;i<100;i++){const x=await fn();if(x)return x;await sleep(150)}throw Error('readiness timeout')}
async function browser(exe){
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-int-browser-')), downloads=path.join(profile,'downloads');
  fs.mkdirSync(downloads); const flags=['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
  if(process.platform==='linux'&&process.getuid?.()===0)flags.unshift('--no-sandbox');
  const chrome=spawn(exe,flags,{stdio:['ignore','ignore','pipe']}); let stderr='',launchError,ws; const errors=[];
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
    const js=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
    await call('Runtime.enable');await call('Page.enable');
    const url=pathToFileURL(path.join(run,'index.html')).href, nav=await call('Page.navigate',{url});assert.ok(!nav.errorText,nav.errorText);
    await until(async()=>{try{return await js(`location.href===${JSON.stringify(url)} && document.readyState==='complete' && document.querySelectorAll('#case option').length>0`)}catch{return false}});
    const keys=Object.keys(receipt.witnesses);assert.equal(keys.length,48);
    assert.deepEqual((await js(`Array.from(document.querySelectorAll('#case option'),o=>o.value)`)).sort(),keys.sort());
    let selections=0;
    for(const key of keys){
      const bySlot=Array.from({length:160},()=>[]);for(const row of receipt.witnesses[key])bySlot[row.t].push(row);
      for(const slot of [0,25,29,47,48,79,80,159]){
        const actual=await js(`(()=>{const c=document.getElementById('case'),s=document.getElementById('slot');c.value=${JSON.stringify(key)};c.dispatchEvent(new Event('change'));s.value=${slot};s.dispatchEvent(new Event('input'));return {rows:JSON.parse(document.getElementById('events').textContent),applied:document.getElementById('applied').value,known:document.getElementById('known').value}})()`);
        const expected=bySlot[slot],state=expected.find(x=>x.event==='state');assert.deepEqual(actual,{rows:expected,applied:state.applied,known:state.known});selections++;
      }
    }
    assert.deepEqual(await js(`(()=>{const s=document.getElementById('slot'),p=document.getElementById('prev'),n=document.getElementById('next');s.value=0;p.click();const a=+s.value;n.click();const b=+s.value;s.value=159;n.click();const c=+s.value;p.click();return [a,b,c,+s.value]})()`),[0,1,159,158]);
    const audio=await js(`Array.from(document.querySelectorAll('audio'),a=>({src:a.getAttribute('src'),controls:a.controls,autoplay:a.autoplay,paused:a.paused,volume:a.volume}))`);
    assert.deepEqual(audio.map(a=>a.src).sort(),Object.keys(m).filter(n=>n.endsWith('.wav')).sort());assert.ok(audio.every(a=>a.controls&&!a.autoplay&&a.paused&&a.volume===.2));
    assert.ok(await js(`(()=>{const a=document.querySelector('audio');a.volume=.07;return a.paused&&Math.abs(a.volume-.07)<1e-7})()`));
    await call('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
    const key='forward-edge/bound-priority';await js(`(()=>{const c=document.getElementById('case');c.value=${JSON.stringify(key)};c.dispatchEvent(new Event('change'));document.getElementById('export').click();return true})()`);
    const exported=path.join(downloads,'trace.json');await until(()=>fs.existsSync(exported)&&fs.statSync(exported).size>0);assert.deepEqual(JSON.parse(fs.readFileSync(exported)),receipt.witnesses[key]);
    assert.deepEqual(errors,[]);return {status:'PASS',version:await get('/json/version'),selections,button_boundaries:4,audio_controls:audio.length,export_rows:receipt.witnesses[key].length,export_sha256:sha(fs.readFileSync(exported)),errors};
  }catch(e){console.error(JSON.stringify({status:'FAIL',error:String(e),stderr,errors}));throw e}
  finally{if(ws)ws.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
async function main(){const result={schema:'mhac.interaction-browser/1',platform:process.platform,node:process.version,manifest_entries:Object.keys(m).length,browser:{status:'NOT_RUN'}};if(process.argv[3]!=='--static-only')result.browser=await browser(process.argv[3]||'google-chrome');console.log(JSON.stringify(result,null,2))}
main().catch(e=>{console.error(e);process.exitCode=1});
