'use strict';
// Refs #512. Receiver policy adapter for v23, not authentication or production persistence.
const {frame}=require('./relay.cjs');
const key=p=>frame(p).join(',');
function receiver(policy='highwater'){
 if(!['baseline','highwater'].includes(policy))throw Error('policy');
 const last=Array(17).fill(null);
 return {receive(e,version=1){
  if(e.status!=='receipt-candidate'||!e.packet||e.packet.kind!==0)return {decision:'no-receipt',ack:false,apply:false};
  const p=e.packet,g=e.generation;
  if(!Number.isInteger(p.source)||p.source<1||p.source>16||!Number.isInteger(g)||g<0||g>255||p.version!==version)return {decision:'context-refused',ack:false,apply:false};
  const k=key(p),prev=last[p.source];
  if(policy==='highwater'&&prev){
   if(g<prev.g)return {decision:'stale',ack:false,apply:false};
   if(g===prev.g)return prev.k===k?{decision:'duplicate',ack:true,apply:false}:{decision:'conflict',ack:false,apply:false};
  }
  last[p.source]={g,k};return {decision:'new',ack:true,apply:true};
 },snapshot(){return last.map(x=>x&&{...x});}};
}
module.exports={receiver};
