"""Negative controls against a real generated receipt; mutations are scratch only."""
import copy
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import wave

from audit_metadata_pressure_strict import audit

sha=lambda b:hashlib.sha256(b).hexdigest()


def erase_events(r):
    for row in r['rows']:
        row.update(events=[],correct=0,wrong=0,overflow=False,prefixChecks=0)
        for field in ('evicted','lossAbstentions','prefixCandidatesRejected'):
            if field in row['stats']: row['stats'][field]=0
    for group in r['summary']:
        for metrics in group['modes'].values():
            for key in metrics: metrics[key]=0


def rewrite_pcm(root,r,s,pcm):
    p=root/s['file']
    with wave.open(str(p),'wb') as w:
        w.setparams((1,2,16000,150000,'NONE','not compressed'))
        w.writeframes(pcm)
    s.update(sha256=sha(p.read_bytes()),pcmSha256=sha(pcm))
    for row in r['rows']:
        if (row['seed'],row['name'])==(s['seed'],s['name']): row['pcmSha256']=sha(pcm)


def all_silent(root,r):
    erase_events(r)
    for s in r['specimens']:
        rewrite_pcm(root,r,s,bytes(300000))
        s.update(peak=0,targetSha256=sha(bytes(62720)) if s['targetStart'] is not None else None)


def decoy_pcm(root,r):
    s=next(s for s in r['specimens'] if s['name']=='eight')
    with wave.open(str(root/s['file']),'rb') as w: b=bytearray(w.readframes(150000))
    b[2*s['starts'][0]]^=1
    rewrite_pcm(root,r,s,b)


def late_event(r):
    r['rows'][0]['events'][0]['at']=150001


def wrong_mode(r):
    r['rows'][0]['mode']='unexpected'
    r['summary'][0]['modes'].pop('base')


def run(source):
    if not __debug__: raise RuntimeError('do not run with assertions disabled')
    if audit(source)['result']!='PASS': raise RuntimeError('positive receipt failed')
    prior=pathlib.Path(__file__).with_name('audit_metadata_pressure.py')
    original=json.loads((source/'receipt.json').read_text())
    cases={'all_silent':all_silent,'erased_outcomes':lambda p,r:erase_events(r),
           'omitted_summary':lambda p,r:r.update(summary=[]),'wrong_mode':lambda p,r:wrong_mode(r),
           'past_end_event':lambda p,r:late_event(r),'altered_decoy_pcm':decoy_pcm}
    for name,mutate in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)/'case'
            shutil.copytree(source,root)
            r=copy.deepcopy(original);mutate(root,r)
            (root/'receipt.json').write_text(json.dumps(r))
            old=subprocess.run([sys.executable,str(prior),str(root)],capture_output=True,text=True)
            if old.returncode!=0: raise RuntimeError(f'{name}: legacy negative control not reproduced: {old.stderr}')
            try: audit(root)
            except ValueError as e: print(f'{name}: legacy PASS, strict refused ({e})')
            else: raise RuntimeError(f'{name}: strict audit accepted mutation')
    print(f'PASS {len(cases)}/{len(cases)} negative controls; real receipt accepted')


if __name__=='__main__':
    run(pathlib.Path(sys.argv[1]))
