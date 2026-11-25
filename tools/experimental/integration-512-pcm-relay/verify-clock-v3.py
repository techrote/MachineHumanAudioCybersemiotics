"""Compare native C++ DSP output against JS trace, verify exported PCM hashes."""
import hashlib, json, pathlib, subprocess, sys, wave
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'clock-v3-output')
exe=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else 'clock-v3-host').resolve()
report=json.loads((root/'receipt.json').read_text())
count=0; hypotheses=0; max_error=0.; result_bytes=0
for row in report['rows']:
    p=root/row['file']; data=p.read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256'],row['name']
    with wave.open(str(p),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,16000,row['samples'])
        assert max(abs(x) for x in __import__('struct').unpack('<'+'h'*row['samples'],w.readframes(row['samples'])))<=4096
    got=json.loads(subprocess.check_output([str(exe),str(p)])); ref=row['clock']
    assert got['onsetSpan']==ref['onsetSpan'] and len(got['evidence'])==len(ref['evidence']),row['name']
    for a,b in zip(got['evidence'],ref['evidence']):
        assert all(a[k]==b[k] for k in ('s','scale','complete','words')),(row['name'],a,b)
        max_error=max(max_error,abs(a['q']-b['q']));assert abs(a['q']-b['q'])<1e-9
        hypotheses+=1
    result_bytes=got['resultBytes'];count+=1
summary=dict(wavs=count,hypotheses=hypotheses,max_quality_difference=max_error,result_bytes=result_bytes,pcm_limit_bytes=76800)
(root/'native-dsp.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
