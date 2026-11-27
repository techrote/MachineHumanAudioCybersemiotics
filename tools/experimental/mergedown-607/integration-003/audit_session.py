"""Independent frame/HMAC and trace accounting for the frozen v40 fixtures."""
import argparse
import collections
import hashlib
import hmac
import json
import subprocess
import wave
from pathlib import Path
from struct import iter_unpack

VOCAB = 'fault open stopped overload not quote question verify pump-reports relay-reports uncertain and if end'.split()
CASES = ('clean', 'forged-data', 'forged-confirm', 'authorized-lie')
STEPS = {0: 55936, 32: 70272, 64: 77440}
OFFERS = [('B', 1, 1, 7, 2, 'stopped'), ('A', 1, 0, 7, 1, 'open'),
          ('C', 2, 0, 8, 1, 'fault'), ('D', 2, 1, 8, 2, 'open')]


def require(condition, label):
    if not condition:
        raise ValueError(label)


def protect(data):
    require(len(data) == 6 and all(0 <= x < 17 for x in data), 'field input')
    # Solve the two parity equations, rather than use the encoder formula.
    a = -sum(data) % 17
    b = -sum((i+1)*v for i, v in enumerate(data)) % 17
    y = (b - 7*a) % 17
    return data + [(a-y) % 17, y]


def frame(packet):
    def walk(tree):
        i = VOCAB.index(tree[0])
        require(i < 13 and len(tree) == 1 + (0 if i < 4 else 1 if i < 11 else 2), 'AST')
        return [i] + [v for child in tree[1:] for v in walk(child)]
    tokens = walk(packet['tree'])
    require(1 <= len(tokens) <= 4, 'AST limit')
    return protect([packet[k] for k in ('kind','source','version','actor','event','seq')]) + protect([len(tokens)-1] + tokens + [13]*(5-len(tokens)))


def expected_tag(bits, role, source, code, generation, status, revision, challenge, session):
    require(bits in (32, 64) and role in ('data','outcome','confirm'), 'domain')
    key = hashlib.sha256(f'PUBLIC-TEST-KEY:{source}:{role}:1'.encode()).digest()
    message = f'MHAC-v40:{bits}:{role}\0'.encode() + bytes.fromhex(session) + bytes(code + [generation, 0, status, revision]) + challenge.to_bytes(4, 'big')
    return hmac.new(key, message, hashlib.sha256).hexdigest()[:bits//4]


def vector(v, role, nonce_field, status, revision):
    source = v['frame'][1]
    require(v[nonce_field] == 65536*source+v['generation' if nonce_field == 'challenge' else 'g']+1, 'fixture nonce')
    g = v['generation' if nonce_field == 'challenge' else 'g']
    require(v['session'] == '01'*16, 'fixture session')
    require(v['tag'] == expected_tag(v['bits'], role, source, v['frame'], g, status, revision, v[nonce_field], v['session']), 'HMAC vector')


def audit(root, seed):
    data = json.loads((root/'receipt.json').read_bytes())
    require(data['schema'] == 'mhac-session-v40' and data['rate'] == 16000 and data['horizon'] == 1120000, 'receipt contract')
    rows = data['rows']
    require(len(rows) == 12 and {(r['name'],r['bits']) for r in rows} == {(c,b) for c in CASES for b in STEPS}, 'session inventory')
    require(len(data['vectors']) == 2 and {v['bits'] for v in data['vectors']} == {32,64}, 'vector inventory')
    for v in data['vectors']:
        vector(v, 'data', 'n', 0, 0)
        require(v['duplicate'] == 'suppressed' and v['rollback'] == 'new-again' and v['rotation'] == 'mac-refusal', 'rollback receipt labels')
    totals = {b: collections.Counter() for b in STEPS}
    liars = []
    rescans = 0
    for r in rows:
        bits, name = r['bits'], r['name']
        require(r['seed'] == seed and r['step'] == STEPS[bits], 'seed or slot length')
        filename = f'{seed}-{name}-{bits}.wav'
        require(r['file'] == filename, 'specimen name')
        raw = (root/filename).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == r['sha256'], 'WAV hash')
        with wave.open(str(root/filename),'rb') as w:
            require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,16000,1120000), 'PCM format')
            pcm = w.readframes(w.getnframes())
        trace = r['trace']; n = 1120000//STEPS[bits]
        require(len(trace) == n and not any(pcm[n*STEPS[bits]*2:]), 'budget or trailing silence')
        require(max(abs(x[0]) for x in iter_unpack('<h',pcm)) <= 4096, 'digital peak')
        rescans += n
        for i,t in enumerate(trace):
            require((t['t'],t['start']) == (i,i*STEPS[bits]), 'chronology')
            require(len(t['state']['records']) <= 4 and len(t['pending']) <= 4, 'record bound')
            if t['fault'] == 'authorized-lie' and t['beliefs']['B'] and t['beliefs']['B']['outcome'] == 'applied' and t['state']['semantic']['status'].get('1:1') == 'buffered':
                if bits:
                    require(t['decoded'].get('authenticated') is True, 'liar authentication')
                liars.append((name,bits,i))
        state = trace[-1]['state']; last = trace[-1]
        metrics = collections.Counter()
        expected = []
        for ident,source,g,event,seq,value in OFFERS:
            packet = dict(kind=0,source=source,version=1,actor=9,event=event,seq=seq,tree=['verify' if event==7 else 'pump-reports',[value]])
            rec = next((x for x in state['records'] if x['p']['source']==source and x['g']==g),None)
            exact = rec is not None and frame(rec['p']) == frame(packet)
            actual = state['semantic']['status'][f'{source}:{g}'] if exact else None
            belief = last['beliefs'][ident]
            delivery = next((p['confirmed'] for p in last['pending'] if p['id']==ident),False)
            correct = bool(actual and belief and belief['outcome']==actual and not belief.get('conflict'))
            expected.append(dict(id=ident,exact=exact,actual=actual,belief=belief,correct=correct,delivery=delivery))
            metrics.update(dict(correct=correct,exact=exact,confirmed=delivery))
        require(expected == r['result'], 'final result')
        metrics.update(dict(used=sum(t['job'] is not None for t in trace),wrong=sum(k[0]==name and k[1]==bits for k in liars),unauthorizedAccepted=sum(t['fault']=='unauthorized' and t['decoded']['status']=='receipt-candidate' for t in trace),falseDelivery=sum(t['decision']=='confirmed' and t['fault']=='unauthorized' for t in trace)))
        require(all(r['metrics'][k]==v for k,v in metrics.items()), 'metric mismatch')
        totals[bits].update(metrics)
    require(rescans == data['rescans'], 'rescan count')
    require(len(liars)==3 and {x[1] for x in liars}==set(STEPS), 'authorized liar witness')
    require({b:(m['exact'],m['correct'],m['confirmed'],m['unauthorizedAccepted'],m['falseDelivery'],m['used']) for b,m in totals.items()} == {0:(15,14,15,2,1,55),32:(16,16,14,0,0,55),64:(16,16,13,0,0,54)}, 'headline metrics')
    return dict(seed=seed,sessions=len(rows),slots=rescans,totals=totals,liars=liars)


def self_test(relay):
    data = relay.read_bytes()
    require(hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest() == '3ba457f85f496e4d57d9789a2dc3b7d68fe2c071','relay blob')
    inputs = [dict(kind=int(role!='data'),source=source,version=1,actor=9,event=8,seq=1,tree=['pump-reports',['fault']]) for source in (1,2) for role in ('data','outcome','confirm')]
    js = "const R=require(process.argv[1]);const p=JSON.parse(process.argv[2]);console.log(JSON.stringify(p.map(R.frame)))"
    actual = json.loads(subprocess.check_output(['node','-e',js,str(relay.resolve()),json.dumps(inputs)]))
    require(actual == [frame(p) for p in inputs], 'independent frame agreement')
    # RFC 4231 test case 1; tests the Python library, not v40 PCM.
    require(hmac.new(bytes([11])*20,b'Hi There',hashlib.sha256).hexdigest()=='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7','HMAC known answer')
    return dict(frame_vectors=len(inputs),hmac_known_answer=1,relay_blob='3ba457f85f496e4d57d9789a2dc3b7d68fe2c071')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',type=Path)
    p.add_argument('--seed71',type=Path)
    p.add_argument('--seed113',type=Path)
    p.add_argument('--controls',type=Path)
    a=p.parse_args(); receipt={}
    if a.self_test: receipt['self_test']=self_test(a.self_test)
    if a.seed71 and a.seed113:
        x,y=audit(a.seed71,71),audit(a.seed113,113)
        require(x['totals']==y['totals'] and x['liars']==y['liars'],'seed decision equivalence')
        receipt['seeds']=[x,y]
    if a.controls:
        c=json.loads(a.controls.read_bytes()); rows=c['rows']
        require(len(rows)==6 and {(v['bits'],v['role']) for v in rows}=={(b,r) for b in (32,64) for r in ('data','outcome','confirm')},'role control inventory')
        for v in rows: vector(v,v['role'],'challenge',v['statusIndex'],v['revision'])
        receipt['role_tags']=len(rows)
    require(bool(receipt),'nothing to audit')
    print(json.dumps(receipt,sort_keys=True,indent=2))
