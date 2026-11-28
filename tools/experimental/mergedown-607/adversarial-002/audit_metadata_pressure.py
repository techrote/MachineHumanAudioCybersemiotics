"""Independent receipt and PCM auditor; standard library, no receiver imports."""
import hashlib, json, pathlib, sys, wave, struct
from collections import Counter
root=pathlib.Path(sys.argv[1]); r=json.loads((root/'receipt.json').read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
assert r['schema']=='mhac-607-metadata-pressure-v1' and r['rate']==16000
spec={(s['seed'],s['name']):s for s in r['specimens']}; assert len(spec)==len(r['specimens'])==10
seen=set(); targets={}; actual=Counter(); exact=0
for k,s in spec.items():
 p=root/s['file']; assert sha(p.read_bytes())==s['sha256']
 with wave.open(str(p),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,16000,150000); b=w.readframes(150000)
 assert sha(b)==s['pcmSha256']; peak=max(map(abs,struct.unpack('<150000h',b))); assert peak==s['peak']<=4096
 words=s['words']; assert words==[1,1,14,1,1,14,1,1] and sum(words)%17==sum((i+1)*x for i,x in enumerate(words))%17==0
 t=s['targetStart']; d=s['decoyEnd']; assert d==(s['starts'][-1]+10880 if s['starts'] else 0)
 if t is not None:
  assert d<=t and sha(b[2*t:2*(t+31360)])==s['targetSha256']
  assert not any(b[2*d:2*t]); targets.setdefault(k[0],set()).add(s['targetSha256'])
 else: assert not any(b[2*d:])
assert all(len(v)==1 for v in targets.values())
for x in r['rows']:
 k=(x['seed'],x['name']); mode=x['mode']; key=(*k,mode); assert key not in seen; seen.add(key)
 s=spec[k]; assert x['pcmSha256']==s['pcmSha256'] and x['atFinish']==0 and x['stats']['maxPending']<=8
 events=x['events']; assert [e['at'] for e in events]==sorted(e['at'] for e in events)
 ok=[e for e in events if e['status']=='ok']; ev=[e for e in events if e['status']=='evicted']; loss=[e for e in events if e['status']=='association-incomplete']; over=[e for e in events if e['status']=='overflow']
 for e in ok:
  assert s['targetStart'] is not None and e['at']>=s['targetStart']+31360-320
  assert e['packet']==dict(kind=0,source=1,version=2,actor=2,event=1,seq=1+x['seed']%16,tree=['verify',['fault']])
 for e in loss:
  assert e['packet'] is None and any(w['at']<=e['at'] and w['lossStart']<e['end'] and e['start']<w['lossEnd'] for w in ev)
 for e in events:
  if e['status']=='refused' and any(q['words'][:8]==s['words'] for q in e['evidence']): exact+=1
 assert len(ok)==x['correct'] and x['wrong']==0 and bool(over)==x['overflow']
 assert x['prefixChecks']==len(ok)+len(ev)+len(loss)+len(over)
 for name,v in [('correct',len(ok)),('overflow',len(over)),('evicted',len(ev)),('lossAbstentions',len(loss)),('prefixRefused',sum(e['status']=='prefix-refused' for e in events))]: actual[(k[1],mode,name)]+=v
assert len(seen)==30
for group in r['summary']:
 for mode,metrics in group['modes'].items():
  for name,v in metrics.items(): assert actual[group['name'],mode,name]==v
print(json.dumps({'specimens':len(spec),'rows':len(seen),'observed_refused_candidates_with_exact_metadata':exact,'prefix_checks_recorded':sum(x['prefixChecks'] for x in r['rows']),'result':'PASS'},sort_keys=True))
