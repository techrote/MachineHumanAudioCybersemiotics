"""Independent fixed-fixture audit. No receiver imports; not a decoder proof."""
import hashlib
import json
import math
import pathlib
import struct
import sys
import wave
from collections import Counter

REF = '3637529f313949d31e55d66d04bb119547c1e29a'
PINS = dict(zip(('relay.cjs','bound-v2.cjs','stream-v4.cjs','parity-v11.cjs','ledger-v12.cjs','continuity-v13.cjs'),
    ('3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','2aa2905d4f4d756276814d5ca941c02c51e63f97','31769f808469b4416412be25a41eb238bfc1fdde','4d1ad5ead8f94ce219bc879fe05269bb1ce1f7df','538bf2e28da108bfe9751cab6720e21325c55be1','53291ce6dace840075b18d8db79ba481329ca509')))
CASES = {'clean':(0,50000),'eight':(8,50000),'nine-near':(9,50000),'nine-far':(9,90000),'nine-only':(9,None)}
SEEDS = (71,113)
MODES = ('base','parity','reserve')
DECOY = [1,1,14,1,1,14,1,1]
sha = lambda b: hashlib.sha256(b).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def protect(data):
    # Solve the two parity equations directly in GF(17).
    a = sum(data)
    b = sum(i*x for i,x in enumerate(data,1))
    q = (7*a-b)%17
    return list(data)+[(-a-q)%17,q]


def tone(f, n, active, phase):
    return [math.floor(4096*min(1,i/32,(active-1-i)/32)*math.sin(2*math.pi*f*i/16000+phase)+.5) if i<active else 0 for i in range(n)]


def encoded(seed):
    phase=seed/997
    header=tone(2300,320,320,phase)+tone(2700,320,320,phase)
    def symbols(words):
        return [s for v in words for s in tone(400+100*v,1280,960,phase)]
    body=protect([0,1,2,2,1,1+seed%16])+protect([1,7,0,13,13,13])
    n=int.from_bytes(hashlib.sha256(b'MHAC-relay-v2\0'+bytes(body)).digest()[:4],'big')%17**6
    tag=[]
    for _ in range(6):
        n,v=divmod(n,17)
        tag.append(v)
    return header+symbols(DECOY),header+symbols(body+protect(tag))


def pcm(seed,name):
    n,t=CASES[name]
    starts=[1024+3840*i for i in range(n)]
    end=starts[-1]+10880 if starts else 0
    decoy,target=encoded(seed)
    data=[0]*150000
    for s in starts:
        data[s+640:s+10880]=decoy[640:]
    for s in starts:
        data[s:s+640]=decoy[:640]
    if t is not None:
        data[t:t+31360]=target
    return struct.pack('<150000h',*data),starts,end,t,None if t is None else sha(struct.pack('<31360h',*target))


def expected_events(name,mode):
    if name=='clean': return ['ok']
    if name=='eight': return ['refused']*8+['ok']
    if mode!='reserve': return ['overflow']
    return ['evicted']+['refused']*8+({'nine-near':['association-incomplete'],'nine-far':['ok'],'nine-only':[]}[name])


def audit(root):
    require(__debug__, 'do not run with assertions disabled')
    r=json.loads((root/'receipt.json').read_text())
    require((r['schema'],r['ref'],r['pins'],r['rate'],r['samples'],r['seeds'],r['chunkSizes'])==('mhac-607-metadata-pressure-v1',REF,PINS,16000,150000,list(SEEDS),[511,127]), 'fixture identity')
    expected={(s,n) for s in SEEDS for n in CASES}
    specs={(s['seed'],s['name']):s for s in r['specimens']}
    require(set(specs)==expected and len(r['specimens'])==10,'specimen matrix')
    for (seed,name),s in specs.items():
        b,starts,end,t,target=pcm(seed,name)
        file=f'{seed}-{name}.wav'
        require((s['file'],s['starts'],s['decoyEnd'],s['targetStart'],s['targetSha256'],s['words'],s['peak'])==(file,starts,end,t,target,DECOY,4096),'specimen geometry or signal')
        p=root/file
        require(sha(p.read_bytes())==s['sha256'] and sha(b)==s['pcmSha256'],'specimen digest')
        with wave.open(str(p),'rb') as w:
            require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,16000,150000),'WAV format')
            require(w.readframes(150000)==b,'independent PCM reconstruction')
    rows={(x['seed'],x['name'],x['mode']):x for x in r['rows']}
    require(set(rows)=={(*k,m) for k in expected for m in MODES} and len(r['rows'])==30,'receiver matrix')
    totals={}; prefixes=0; exact=0
    for (seed,name,mode),x in rows.items():
        events=x['events']; statuses=[e['status'] for e in events]; t=CASES[name][1]
        require(statuses==expected_events(name,mode),'fixed outcome matrix')
        counts=Counter(statuses); times=[e['at'] for e in events]
        require(times==sorted(times) and all(type(a) is int and 0<a<=150000 for a in times),'event sample bounds/order')
        for e in events:
            status=e['status']; at=e['at']
            if status in ('overflow','evicted'):
                require(at==32778,'pressure witness timing')
            if status in ('ok','association-incomplete'):
                require(t is not None and at>=t+31360-320,'premature release')
            if status=='ok':
                require(e['packet']==dict(kind=0,source=1,version=2,actor=2,event=1,seq=1+seed%16,tree=['verify',['fault']]),'wrong packet')
            elif status!='overflow':
                require(e['packet'] is None,'non-release packet')
            if status=='association-incomplete':
                require(any(w['status']=='evicted' and w['at']<=at and w['lossStart']<e['end'] and e['start']<w['lossEnd'] for w in events),'unwitnessed loss abstention')
            if status=='refused':
                require(any(q['words'][:8]==DECOY for q in e['evidence']),'missing feasible metadata observation')
                exact+=1
        p=sum(counts[k] for k in ('ok','overflow','evicted','association-incomplete'))
        require((x['correct'],x['wrong'],x['overflow'],x['atFinish'],x['prefixChecks'],x['stats']['maxPending'],x['pcmSha256'])==(counts['ok'],0,bool(counts['overflow']),0,p,1 if name=='clean' else 8,specs[seed,name]['pcmSha256']),'row counters')
        require(x['stats'].get('evicted',0)==counts['evicted'] and x['stats'].get('lossAbstentions',0)==counts['association-incomplete'] and x['stats'].get('prefixCandidatesRejected',0)==0,'runtime counters')
        prefixes+=p
        agg=totals.setdefault((name,mode),Counter())
        agg.update(dict(correct=counts['ok'],overflow=counts['overflow'],evicted=counts['evicted'],lossAbstentions=counts['association-incomplete'],prefixRefused=0))
    groups={g['name']:g['modes'] for g in r['summary']}
    require(set(groups)==set(CASES) and len(r['summary'])==len(CASES),'summary coverage')
    for name,modes in groups.items():
        require(set(modes)==set(MODES),'summary mode coverage')
        for mode,metrics in modes.items():
            require(metrics==dict(totals[name,mode]),'summary counters')
    require((prefixes,exact)==(34,96),'fixed witness totals')
    return dict(result='PASS',specimens=len(specs),rows=len(rows),prefix_checks_recorded=prefixes,observed_refused_candidates_with_exact_metadata=exact,independent_pcm_samples=150000*len(specs))


if __name__=='__main__':
    print(json.dumps(audit(pathlib.Path(sys.argv[1])),sort_keys=True))
