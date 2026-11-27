"""Adversarial #448/#449: stage-specific acoustic gates, exploratory synthetic PCM.
Run: OPENBLAS_NUM_THREADS=1 python stage-gates.py RUN060_PACKAGE NEW_OUT
AI-assisted, no human evidence, no action authorization.
"""
import inspect, pathlib, runpy, sys
import numpy as np
PARENT='d8e76708b79ff15badfdac90127b2bb28f2d1cc8'
PIN='0242cc0c8ea52c84b24b89f9eac9f200f805e04a'
MODES=('absolute','preamble-relative','joint-relative','terminal-hybrid','all-hybrid')
EXTRA=('payload-tone','terminal-tone','false-preamble-load','terminal-erasure','payload-two-tone','terminal-two-tone')
def stage_observe(slot,scale,seen,mode):
    a,b=round(80*scale),round(480*scale); x=slot[a:b]; n=len(x)
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(n)/16000/scale)
    scores=abs(basis@x)*2/n; k=int(scores.argmax()); rms=np.sqrt(np.mean(x.astype(float)**2))
    relative=scores[k]>=max(40,1.1*rms)
    terminal=k==17 and (len(seen) in (13,18) or (len(seen) in (14,19) and seen[-1]==18))
    absolute=scores[k]>=200
    accept=relative or (absolute and (mode=='all-hybrid' or (mode=='terminal-hybrid' and terminal)))
    return (18 if k==17 else k) if accept else None

def run(root,out):
    h=runpy.run_path(str(root/'gain-boundary.py')); assert h['blob'](root/'gain-boundary.py')==PIN
    src=inspect.getsource(h['run'])
    def patch(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    patch("    env=dict(d);", "    needle=\"    g['MODES']=MODES;\"\n    assert prefix.count(needle)==1\n    prefix=prefix.replace(needle,\"    src=src.replace('observe(pcm[a:b],z,True,True)', 'observe(pcm[a:b],z,True,True,seen)'); \"+needle.strip())\n    env=dict(d);")
    patch("obs=p['observe_scaled'] if mode in MODES[:2] else lambda x,z,t,f:observe(x,z,t,f,mode=='joint-contrast')", "obs=(lambda x,z,t,f,seen:p['observe_scaled'](x,z,t,f)) if mode in MODES[:2] else lambda x,z,t,f,seen:stage_observe(x,z,seen,mode)")
    patch("            pcm=np.rint(mix).astype('<i2');", "            if case in EXTRA:\n                if case=='false-preamble-load':\n                    cc=np.zeros_like(aa); v['put'](cc,s['preamble'](b),lead-640); mix+=.5*cc\n                elif case=='terminal-erasure':\n                    mix[ends[1]-2*S:ends[1]]=0\n                else:\n                    lo,hi=(off+3*S,off+9*S) if case.startswith('payload-') else (ends[1]-2*S,ends[1])\n                    t=np.arange(hi-lo); mix[lo:hi]+=900*np.sin(2*np.pi*1100*t/16000)\n                    if case.endswith('two-tone'): mix[lo:hi]+=1100*np.sin(2*np.pi*1200*t/16000)\n            pcm=np.rint(mix).astype('<i2');")
    patch("rows[i:i+4]", "rows[i:i+len(MODES)]")
    patch("range(0,len(rows),4)", "range(0,len(rows),len(MODES))")
    patch("result=dict(parent=PARENT,pins=PINS,", "result=dict(parent=PARENT,pins={**PINS,'gain-boundary.py':PIN},")
    env=dict(h,MODES=MODES,CASES=h['CASES']+EXTRA,EXTRA=EXTRA,SEED=4480611,PARENT=PARENT,PIN=PIN,stage_observe=stage_observe)
    exec(src,env); env['run'](root,out)
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
