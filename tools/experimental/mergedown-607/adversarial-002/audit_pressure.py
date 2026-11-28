"""Independent receipt and PCM audit for #607 synthetic preamble pressure."""
import hashlib, json, pathlib, struct, sys, wave
from collections import Counter

root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'out')
r=json.loads((root/'receipt.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
assert r['schema']=='mhac-607-independent-preamble-pressure-v1'
assert len(r['rows'])==48 and len(r['specimens'])==16
rows={(x['seed'],x['name'],x['mode']):x for x in r['rows']}
assert len(rows)==48
cases={'clean':0,'four':4,'eight':8,'nine':9,'twelve':12,'twenty-four':24,'long-gap':24,'decoy-only':24}
assert set(rows)=={(s,c,m) for s in (71,113) for c in cases for m in ('base','parity','reserve')}
clean={}; accepted=Counter(); overflow=Counter(); prefixes=0
for spec in r['specimens']:
    seed,name=spec['file'].removesuffix('.wav').split('-',1); seed=int(seed)
    p=root/spec['file']; assert sha(p.read_bytes())==spec['sha256']
    with wave.open(str(p),'rb') as f:
        assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes(),f.getcomptype())==(1,2,16000,150000,'NONE')
        pcm=f.readframes(f.getnframes())
    assert sha(pcm)==spec['pcmSha256']
    peak=max(map(abs,struct.unpack('<150000h',pcm))); assert peak==spec['peak']<=4096
    decoys=spec['decoyStarts']; t=spec['targetStart']; assert len(decoys)==cases[name]
    assert decoys==[1024+i*1280 for i in range(cases[name])]
    assert spec['decoyEnd']==(decoys[-1]+640 if decoys else 0)
    if t is None: assert name=='decoy-only' and spec['targetSha256'] is None
    else:
        assert t==(80000 if name=='long-gap' else 40000)
        assert spec['decoyEnd']<=t
        b=pcm[2*t:2*(t+31360)]; assert sha(b)==spec['targetSha256']
        if name=='clean': clean[seed]=b
        assert b==clean[seed]
        assert all(pcm[2*d:2*(d+640)]==b[:1280] for d in decoys)
    # Every sample outside declared fixture intervals must be zero.
    intervals=[(d,d+640) for d in decoys]+([] if t is None else [(t,t+31360)])
    last=0
    for a,b in intervals:
        assert last<=a and not any(pcm[2*last:2*a]); last=b
    assert not any(pcm[2*last:])
    for mode in ('base','parity','reserve'):
        row=rows[seed,name,mode]; assert row['pcmSha256']==spec['pcmSha256']; assert row['targetStart']==t and row['decoyEnd']==spec['decoyEnd']
        events=row['events']; ok=[e for e in events if e['status']=='ok']; over=[e for e in events if e['status']=='overflow']
        assert all(0<=e['at']<=150000 for e in events)
        assert all(a['at']<=b['at'] for a,b in zip(events,events[1:]))
        good=bool(t is not None and (mode!='base' or cases[name]<=8))
        assert len(ok)==int(good)==row['correct'] and row['wrong']==0
        assert all(e['packet']==row['expected'] and e['at']>=t+31360-320 for e in ok)
        assert bool(over)==row['overflow']==(mode=='base' and cases[name]>=9)
        assert all(e['reason']=='pending-cap' and e['at']==12298 and (t is None or e['at']<t) for e in over)
        assert row['stats']['maxPending']<=8 and row['eventsAtFinish']==0
        if mode!='base': assert row['stats']['maxPending']<=3 and row['stats']['prefixCandidatesRejected']==cases[name]
        accepted[mode]+=len(ok); overflow[mode]+=len(over); prefixes+=row['causalPrefixChecked']
assert prefixes==44
for s in r['summary']:
    for m,q in s['modes'].items():
        group=[x for x in r['rows'] if x['name']==s['name'] and x['mode']==m]
        expected=dict(correct=sum(x['correct'] for x in group),wrong=sum(x['wrong'] for x in group),overflow=sum(x['overflow'] for x in group),maxPending=max(x['stats']['maxPending'] for x in group),scans=sum(x['stats']['scans'] for x in group),prefixRefused=sum(x['stats'].get('prefixCandidatesRejected',0) for x in group))
        assert q==expected
print(json.dumps({'status':'PASS','waveforms':16,'matched_rows':48,'reported_prefix_checks':prefixes,'accepted':dict(accepted),'overflow':dict(overflow)},sort_keys=True))
