"""Mergedown #607: independently recount frozen deadline-clarification traces.
Synthetic symbolic transport, not wire audio or human evidence. Python stdlib.
"""
import collections as C
import hashlib, importlib.util, json, pathlib, sys, wave, struct

PIN = 'ec305bf677fb5c0c778dd6f3967c5bf4ed88fb01'
BLOBS = {'deadline-clarification.py':'e51bccbcdc4edfb9527f662b68fcdbfbcc324a07',
         'live-clarification.py':'76f1da836728419ba32054865a59acc44f169d3c',
         'uncertainty-repair.py':'7c99f122431cf32ad8e569eb43eeac1cd3580abe'}
RECEIPT = '8d1db0bfb48c9d473967842f140b1cda899f84716339651132dc64546571a60d'

def need(ok, why):
    if not ok: raise ValueError(why)

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit(rows, regime, policy):
    totals=C.Counter(); transit=C.Counter(); states=0; bound=policy.startswith('bound')
    for t, group in __import__('itertools').groupby(rows,key=lambda x:x['t']):
        need(t==states,'missing or unordered slot'); e,age=t//80+1,t%80
        if age==0: applied=known=issued=0; final=None; buf=set(); queries=set(); accepted=set(); sends=C.Counter(); credits=set(); live=[]
        arrivals=[]; expected=[]; receipt_options=[]; settlement_options=[]
        for x in group:
            event=x['event']; k=x.get('kind'); s=x.get('seq'); stamp=x.get('stamp'); n=x.get('nonce')
            if event in ('send','arrival'):
                key=(x['epoch'],k,s,stamp,n)
                if event=='send':
                    need(x['epoch']==e,'wrong sending epoch'); totals[k+'-sent']+=1
                    d=x['delay']
                    if d: transit[(t+d,key)]+=1
                    if d and k=='STATUS' and regime=='duplicate-status': transit[(t+d+3,key)]+=1
                    if k=='ACT':
                        need(age<48 and 0<=s<8 and s<=issued and s>=known,'invalid action transmission')
                        issued=max(issued,s+1); sends[s]+=1
                        need(sends[s]<=4+(s in credits),'action budget')
                    if k=='QUERY':
                        need(n==age and n not in queries,'query identity'); queries.add(n)
                        if age<48:
                            need(len(live)<6 and (not live or age-live[-1]>=6),'live query budget'); live.append(age); totals['live-query']+=1
                    if k in ('ACK','STATUS'):
                        need(s==applied-1 and stamp==age,'response not grounded in current state')
                        need(any(a[0]==('ACT' if k=='ACK' else 'QUERY') and (k!='STATUS' or a[3]==n) for a in arrivals),'response without request')
                else:
                    if transit[(t,key)]: transit[(t,key)]-=1
                    else: need(regime=='stale-status' and e==2 and age in (3,55) and key==(1,'STATUS',7,79,-1),'arrival without matching send')
                    if x['epoch']!=e: totals['stale-rejected']+=1; continue
                    arrivals.append((k,s,stamp,n))
                    if k=='ACT' and age<48 and applied<=s<applied+3 and s not in buf:
                        buf.add(s)
                        while applied+len(expected) in buf:
                            j=applied+len(expected); buf.remove(j); expected.append(j)
                    if k=='ACK': receipt_options.append(s)
            elif event=='apply':
                need(age<48 and expected and expected.pop(0)==s==applied,'effect not supported by ordered arrival'); applied+=1; totals['applied']+=1
            elif event=='status-accept':
                need(('STATUS',s,stamp,n) in arrivals,'accepted status without arrival')
                if bound: need(n in queries and n not in accepted and n<=stamp<=age<=n+8,'invalid query binding')
                accepted.add(n); totals['status-accepted']+=1; receipt_options.append(s)
                if stamp>=48: settlement_options.append(s)
            elif event=='status-reject': totals['status-rejected']+=1
            elif event=='receipt':
                a=x['ack']; need(a in receipt_options and known<=a<applied,'unsupported receipt'); known=a+1
            elif event=='credit':
                need(age<48 and s==known and sends[s]==4 and s not in credits and s-1 in receipt_options,'unsupported credit'); credits.add(s); totals['repair-credit']+=1
            elif event=='settled':
                final=x['prefix']; need(final in settlement_options and final==applied-1,'unsupported final settlement')
            elif event=='state':
                need(not expected and (x['applied'],x['known'],x['issued'],x['final'],x['buffer'])==(applied,known,issued,final,sorted(buf)),'state mismatch')
                need(0<=known<=applied<=issued<=8 and issued-known<=3,'state window'); states+=1
                if age==79:
                    totals.update({'complete':int(applied==8),'confirmed':int(known==8),'settled-incomplete':int(final is not None and final<7),'unknown-issued':0 if final is not None else issued-known,'not-issued':8-issued,'known-applied':known,'unknown-epochs':int(known<8 and final is None and issued>known)})
    need(states==160 and not any(v for (t,k),v in transit.items() if t<160),'missing states or arrivals')
    totals['missing']=16-totals['applied']; return totals

def main(root):
    for n,h in BLOBS.items():
        b=(root/n).read_bytes(); need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==h,'source blob mismatch: '+n)
    run=root/'run1'; receipt=(run/'receipt.json').read_bytes(); need(hashlib.sha256(receipt).hexdigest()==RECEIPT,'frozen receipt mismatch')
    manifest_bytes=(run/'manifest.json').read_bytes(); need(hashlib.sha256(manifest_bytes).hexdigest()=='e619850702050f6cc61091dd350244a67615bfec058ddd7c50540bd1a8f8e505','frozen manifest mismatch')
    manifest=json.loads(manifest_bytes); need(set(manifest)=={p.name for p in run.iterdir() if p.name!='manifest.json'},'manifest inventory')
    for n,h in manifest.items(): need(hashlib.sha256((run/n).read_bytes()).hexdigest()==h,'manifest hash: '+n)
    r=json.loads(receipt); spec=importlib.util.spec_from_file_location('candidate',root/'deadline-clarification.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    totals=C.defaultdict(C.Counter); checked=0
    for seed,regime,policy,h in r['hashes']:
        c,tr=m.run(seed,regime,policy); need(digest(tr)==h,'trace hash mismatch'); a=audit(tr,regime,policy)
        need(all(c.get(k,0)==v for k,v in a.items()),'independent metric mismatch'); totals[regime,policy].update(a); checked+=1
    need(checked==1536,'run count')
    for (regime,policy),a in totals.items(): need(all(r['totals'][regime][policy].get(k,0)==v for k,v in a.items()),'aggregate mismatch')
    peaks={}
    for p in sorted(run.glob('*.wav')):
        with wave.open(str(p),'rb') as w:
            need((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,8000,64000),'audio format'); b=w.readframes(w.getnframes()); peaks[p.name]=max(abs(x[0]) for x in struct.iter_unpack('<h',b))
    need(len(peaks)==4 and max(peaks.values())<=800,'audio bounds')
    print(json.dumps({'pin':PIN,'trace_hashes':checked,'audited_epochs':checked*2,'manifest_entries':len(manifest),'metric_fields':sorted(set().union(*(set(a) for a in totals.values()))),'wav_peaks_pcm16':peaks},sort_keys=True,indent=2))

if __name__=='__main__': main(pathlib.Path(sys.argv[1]))
