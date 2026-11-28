'use strict';
const fs=require('node:fs'),p=require('node:path'),P=require('./intent-history-069.cjs');
const [cmd,dirArg,op,idArg,seqArg='1',prevArg='0',mode='normal',wav]=process.argv.slice(2);
if(!dirArg||!['init','show','send','reopen','forget','abandon'].includes(cmd))throw Error('Usage: node playground-069.cjs init DIR [terminal|completed-only]; show|reopen|abandon DIR; forget DIR ID; send DIR OP ID SEQ PREV normal|drop-request|drop-reply [WAV]');
const dir=p.resolve(dirArg),q=p.join(dir,'requester'),r=p.join(dir,'reporter'),show=()=>({requester:P.recover(q),reporter:P.recover(r)});let result;
if(cmd==='init'){fs.mkdirSync(dir);P.init(q,'requester',op||'terminal');P.init(r,'reporter',op||'terminal');}
else if(cmd==='reopen')P.reopen(r);
else if(cmd==='forget')P.forget(q,Number(op));
else if(cmd==='abandon')P.abandon(q);
else if(cmd==='send'){
 if(!['normal','drop-request','drop-reply'].includes(mode))throw Error('mode');if(wav&&fs.existsSync(wav))throw Error('choose a new WAV path');const m=P.begin(q,op,Number(idArg),Number(seqArg),Number(prevArg)),x=P.encode(m);let clips=[x];
 if(mode==='drop-request'){P.abandon(q);result='request lost';}else{const rr=P.receive(r,x);result={reporter:rr.result,requester:'unmatched'};if(rr.reply){const y=P.encode(rr.reply,1.12);clips.push(y);if(mode==='normal')result.requester=P.accept(q,y);else result.requester='reply lost';}if(mode==='drop-reply'||!rr.reply)P.abandon(q);}
 if(wav)fs.writeFileSync(wav,P.D.R.wav(P.D.R.join(...clips)),{flag:'wx'});
}
console.log(JSON.stringify({result,...show()},null,2));
