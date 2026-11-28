"""Independent causal ledger audit of the frozen scheduled-v2 synthetic corpus."""
import collections
import hashlib
import json
import sys
import wave
from pathlib import Path
from struct import iter_unpack

PIN = '0ac5726c7ef1c52212d3910da5d636ffe6abe422801f2d7b5486aa0ba9344bad'
CASES = 'clean data-loss ack-loss persistent-loss interference drift interrupt splice noise delayed expiry revision forged wrong-actor replay'.split()
POLICIES = ('data-first', 'ack-first', 'reserve')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def key(p):
    return tuple(p[k] for k in ('source','version','actor','event','seq')) + (json.dumps(p['tree'], separators=(',',':')),)

def audit(s):
    name, policy = s['name'], s['policy']
    cfg = s['config']
    current, records, pending, received, confirmed = {}, {}, [], set(), set()
    counts = collections.Counter()
    require(len(s['trace']) == 10 and s['samples'] == 320000, 'channel budget')
    continuous = []
    for slot, t in enumerate(s['trace']):
        require((t['slot'], t['atSamples']) == (slot, slot*32000), 'slot chronology')
        events = []
        for at, p in cfg['offers']:
            if at == slot:
                current[str(p['source'])] = p['version']
                records[key(p)] = [p, 0, slot]
                counts['offered'] += 1
                events.append(dict(type='offer', packet=p))
        for entry in pending[::-1]:
            if slot >= entry['expires']:
                pending.remove(entry)
                counts['expiredAck'] += 1
                events.append(dict(type='return-expired', packet=entry['packet']))
        data = [r for k,r in records.items() if k not in confirmed and r[1]<2 and r[2]<=slot and current[str(r[0]['source'])]==r[0]['version']]
        returns = [r for r in pending if r['ready']<=slot]
        fixture = (name in ('forged','wrong-actor') and slot==1) or (name=='replay' and slot==4)
        tx = t['tx']
        if fixture:
            require(t['origin']=='fixture-return' and tx['kind']==1, 'fixture placement')
        elif returns and (policy=='ack-first' or (policy=='reserve' and slot%3==2) or not data):
            require(t['origin']=='return' and tx==returns[0]['packet'], 'return scheduling')
            pending.remove(returns[0])
        elif data:
            require(t['origin']=='data' and tx==data[0][0], 'data scheduling')
            data[0][1]+=1
            data[0][2]=slot+3
            counts['dataAttempts']+=1
            counts['retries']+=data[0][1]>1
        else:
            require(tx is None and t['origin']=='idle', 'idle scheduling')
        counts['idleSlots']+=tx is None
        counts['acks']+=tx is not None and tx['kind']==1
        hits=[h for h in t['hits'] if h['status']=='ok']
        counts['noDecodedPacket']+=tx is not None and not hits
        for h in hits:
            p=h['packet']; k=key(p)
            continuous.append(p)
            fresh=current.get(str(p['source']))==p['version']
            if p['kind']==0:
                allowed=fresh and (p['actor'],p['event'])=={1:(2,1),2:(3,2)}.get(p['source'])
                events.append(dict(type='data-receipt',accepted=allowed,packet=p))
                if not allowed:
                    counts['refusedData']+=1
                    continue
                counts['duplicates']+=k in received
                counts['uniqueReceipts']+=k not in received
                received.add(k)
                if not any(key(x['packet'])==k for x in pending):
                    if len(pending)>=4:
                        counts['droppedAck']+=1
                        events.append(dict(type='return-overflow',packet=p))
                    else:
                        pending.append(dict(packet=dict(p,kind=1),ready=slot+cfg['delay'],expires=slot+cfg['ttl']))
            else:
                require(p['kind']==1,'packet kind')
                allowed=k in records and records[k][1]>0 and k not in confirmed
                genuine=k in received
                events.append(dict(type='ack-receipt',accepted=allowed,fresh=fresh,evaluatorGenuine=genuine,packet=p))
                if allowed:
                    confirmed.add(k)
                    counts['confirmations']+=1
                    counts['freshAtAck']+=fresh
                    counts['staleAtAck']+=not fresh
                    counts['genuineConfirmations']+=genuine
                    counts['genuineFreshAtAck']+=genuine and fresh
                    counts['invalid']+=not genuine
                else:
                    counts['replayAck']+=k in confirmed
                    counts['unmatchedAck']+=k not in confirmed
        require(events==t['events'] and pending==t['returnQueue'] and current==t['current'], 'causal trace mismatch')
    require(continuous==[h['packet'] for h in s['continuous'] if h['status']=='ok'] and s['continuousMatch'] is True,'continuous packet sequence')
    now={k for k in confirmed if current[str(records[k][0]['source'])]==records[k][0]['version']}
    counts['currentConfirmed']=len(now)
    counts['genuineCurrentConfirmed']=len(now & received)
    counts['unconfirmed']=len(records)-len(confirmed)
    counts['returnBacklog']=len(pending)
    require(all(counts[k]==v for k,v in s['metrics'].items()) and not set(counts)-set(s['metrics']), 'metric mismatch')
    return s['metrics']

def main(root):
    raw=(root/'manifest.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest()==PIN,'frozen manifest mismatch')
    manifest=json.loads(raw)
    require(len(manifest['rows'])==45 and {(r['name'],r['policy']) for r in manifest['rows']}=={(c,p) for c in CASES for p in POLICIES},'fixture inventory')
    totals={p:collections.Counter() for p in POLICIES}
    for row in manifest['rows']:
        stem=row['name']+'-'+row['policy']
        wav=root/(stem+'.wav')
        require(hashlib.sha256(wav.read_bytes()).hexdigest()==row['sha256'],'WAV digest '+stem)
        with wave.open(str(wav),'rb') as w:
            require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,16000,320000),'PCM format')
            peak=max(abs(x[0]) for x in iter_unpack('<h',w.readframes(w.getnframes())))
            require(peak==row['peak'] and peak<=8192,'PCM peak')
        s=json.loads((root/(stem+'.json')).read_text())
        require((s['name'],s['policy'])==(row['name'],row['policy']),'session identity')
        m=audit(s)
        require(m==row['metrics'],'manifest metrics')
        totals[row['policy']].update(m)
    return dict(sessions=45,slots=450,wavs=45,metrics_per_session=len(manifest['rows'][0]['metrics']),totals=totals)

if __name__=='__main__':
    print(json.dumps(main(Path(sys.argv[1])),indent=2,sort_keys=True))
