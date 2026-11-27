'use strict';
// Refs #512. One reporter session; volatile bounded queue, public fixture authentication.
const {frame}=require('./relay.cjs');
function queue(policy){const list=[],cap=policy==='overwrite'?1:2;let peak=0;return {list,cap,get peak(){return peak;},add(z){const key=JSON.stringify([z.decoded.generation,frame(z.decoded.packet)]),n=z.decoded.queryChallenge,j={key,n,pcm:z.pcm};let decision;if(policy==='overwrite'){decision=list.length?'overwrite':'enqueue';list.splice(0,list.length,j);}else if(policy==='coalesce'&&list.some(x=>x.key===key)){const i=list.findIndex(x=>x.key===key);if(n>list[i].n){list[i]=j;decision='replace-pending-older';}else decision=n===list[i].n?'duplicate-coalesced':'older-query-refused';}else if(list.length>=cap)decision='capacity-refused';else{list.push(j);decision='enqueue';}peak=Math.max(peak,list.length);return {decision,n,key};},take(){return list.shift();},snapshot(){return list.map(({key,n})=>({key,n}));}};}
module.exports={queue};
