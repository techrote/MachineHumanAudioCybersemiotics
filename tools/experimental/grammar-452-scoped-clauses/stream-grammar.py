"""MHAC #452 / #453: framed melodic contours, synthetic PCM only.
python stream-grammar.py NEW_OUTPUT; Python 3.11+, NumPy.
No device I/O, human evidence, or authentication. Marker positions inferred from PCM.
"""
import itertools as it, json, hashlib, html, sys, wave, runpy
from pathlib import Path
from collections import Counter
import numpy as np
G=runpy.run_path(str(Path(__file__).with_name('polyphonic-depth.py')))
PIN='2715c38cf4d7dd2727d161a8020a46078d72b690'; REF='a012850105079a077848e29414ea8efef760c264'
RATE=16000; SLOT=.480; HEADER=.064; NOTE=.040; AMP=5500; SEED=452640
BOOK=((3,6,-6),(-6,3,6),(-6,-3,6),(3,-6,-3),(6,-3,3),(-6,6,6),(-3,3,-3),(6,-6,-6),(-3,6,-3),(6,6,3),(-6,-6,6),(-3,-3,-6),(-3,-6,3))
P=np.array([[0,a,a+b,a+b+c] for a,b,c in BOOK],float);P-=P.mean(axis=1,keepdims=True)
TM=np.array([[.04,.1625+.085*d,.5075+.085*d,.88] for d in range(4)])
MARKERS={'start':3000.,'node':3300.,'end':3600.}
T={}
for n in (3,4):
    rows=[(k,d,idx) for idx in it.combinations(range(4),n) for k in range(13) for d in range(4)]
    T[n]=(rows,np.array([TM[d,list(idx)] for k,d,idx in rows]),np.array([np.diff(P[k,list(idx)]) for k,d,idx in rows]))
def sha(x):return hashlib.sha256(x).hexdigest()
def tone(x,start,duration,f,rng):
    a=round(start*RATE);n=round(duration*RATE);t=np.arange(n)/RATE;fade=round(.004*RATE);w=np.minimum(1,np.minimum(np.arange(n),np.arange(n)[::-1])/fade);z=AMP*w*np.sin(2*np.pi*f*t+rng.uniform(0,2*np.pi));l=max(0,a);r=min(len(x),a+n)
    if r>l:x[l:r]+=z[l-a:r-a]
def render(rows,condition,seed):
    rng=np.random.default_rng(seed);lead=float(rng.uniform(.025,.225));tail=float(rng.uniform(.03,.14));target=int(rng.integers(len(rows))) if rows else 0
    scales=np.ones(len(rows));shifts=np.zeros(len(rows));jitter=np.zeros((len(rows),4));erasures=[-1]*len(rows)
    if condition in ('global','global_noise'):scales[:]=1.25;shifts[:]=4
    if condition in ('local','local_erase','local_noise','lost_marker','insert_marker','marker_drift','drift_noise','nonuniform_marker'):scales=rng.choice([.75,.9,1.15,1.35],len(rows));shifts=rng.choice([-5,-2,2,5],len(rows))
    if condition in ('local_erase','local_noise','jitter'):jitter[target]=rng.uniform(-.012,.012,4)
    if condition=='local_erase':erasures[target]=int(rng.integers(4))
    bounds=[round(lead*RATE)/RATE]
    for scale in scales:bounds.append(round((bounds[-1]+HEADER+SLOT*scale)*RATE)/RATE)
    x=np.zeros(round((bounds[-1]+HEADER+tail)*RATE));mark_shift=80 if condition in ('marker_drift','drift_noise','nonuniform_marker') else 0
    for i,(k,d) in enumerate(rows):
        if not(condition=='lost_marker' and i==min(1,len(rows)-1)):tone(x,bounds[i],.032,MARKERS['start' if i==0 else 'node']+mark_shift+(100 if condition=='nonuniform_marker' and i==0 else 0),rng)
        for j,(p,t) in enumerate(zip(P[k],TM[d])):
            if j==erasures[i]:continue
            tone(x,bounds[i]+HEADER+(t*SLOT+jitter[i,j])*scales[i],NOTE*scales[i],800*2**((p+shifts[i])/12),rng)
    if condition!='lost_end':tone(x,bounds[-1],.032,MARKERS['end']+mark_shift,rng)
    if condition=='insert_marker':tone(x,bounds[target]+.043,.012,MARKERS['node'],rng) # short burst in header guard
    if condition=='long_insert':tone(x,bounds[target]+.38,.032,MARKERS['node'],rng)
    if condition=='noise_only':x[:]=0
    sd=3500 if condition=='strong' else 1000 if condition in ('global_noise','local_noise','drift_noise','noise_only') else 0
    x+=rng.normal(0,sd,len(x));return np.rint(np.clip(x,-32768,32767)).astype('<i2'),bounds

def observe(x):
    y=x.astype(float);hop=64;n=len(y)//hop
    if not n:return []
    rms=np.sqrt(np.mean(y[:n*hop].reshape(n,hop)**2,axis=1));floor=float(np.quantile(rms,.2));threshold=max(500.,floor*1.24+150.)
    active=np.flatnonzero(rms>threshold);groups=np.split(active,np.where(np.diff(active)>1)[0]+1) if len(active) else [];ev=[]
    for g in groups:
        if len(g)<4:continue
        a=int(g[0])*hop;b=(int(g[-1])+1)*hop;z=y[a:b];s=np.abs(np.fft.rfft(z*np.hanning(len(z)),n=8192));lo,hi=round(180*8192/RATE),round(4000*8192/RATE);i=int(np.argmax(s[lo:hi])+lo);v=np.log(np.maximum(s[i-1:i+2],1e-12));den=v[0]-2*v[1]+v[2];frac=.5*(v[0]-v[2])/den if den else 0.;f=float((i+frac)*RATE/8192)
        label=min(MARKERS,key=lambda k:abs(MARKERS[k]-f));label=label if abs(MARKERS[label]-f)<=45 and .020<=len(z)/RATE<=.044 else 'note' if 180<=f<=2400 else 'unknown'
        ev.append(dict(t=a/RATE,f=f,kind=label,duration=len(z)/RATE))
    return ev

def candidates(events,a,b):
    n=len(events)
    if n not in T or not .34<=b-a<=.69:return []
    t=np.array([(e['t']-a)/(b-a) for e in events]);p=np.diff(12*np.log2([e['f']/800 for e in events]));rows,ts,ps=T[n]
    return [rows[i] for i in np.flatnonzero((np.max(abs(ts-t),axis=1)<=.04)&(np.max(abs(ps-p),axis=1)<=.85))]
def decode(events,policy,oracle=None):
    offset=None
    if policy=='calibrated':
        high=[e for e in events if e['f']>=2600 and .020<=e['duration']<=.044]
        if len(high)>=2:
            offsets=[high[0]['f']-MARKERS['start'],high[-1]['f']-MARKERS['end']]
            if max(map(abs,offsets))<=120 and abs(offsets[0]-offsets[1])<=20:
                offset=sum(offsets)/2;events=[dict(e) for e in events]
                for e in events:
                    if e['f']>=2600 and .020<=e['duration']<=.044:
                        k=min(MARKERS,key=lambda k:abs(MARKERS[k]+offset-e['f']));e['kind']=k if abs(MARKERS[k]+offset-e['f'])<=45 else 'unknown'
    marks=[e for e in events if e['kind'] in MARKERS];notes=[e for e in events if e['kind']=='note'];proof=dict(markers=marks,policy=policy,reason=None,frames=[],estimated_marker_offset_hz=offset)
    if policy=='calibrated' and offset is None:proof['reason']='marker-calibration';return None,proof
    if any(e['kind']=='unknown' for e in events):proof['reason']='unknown-event';return None,proof
    if policy=='oracle':bounds=oracle
    else:
        kinds=[e['kind'] for e in marks]
        if not 2<=len(kinds)<=5 or kinds!=['start']+['node']*(len(kinds)-2)+['end']:
            proof['reason']='marker-sequence';return None,proof
        bounds=[e['t'] for e in marks]
        if policy=='uniform':bounds=np.linspace(bounds[0],bounds[-1],len(bounds)).tolist()
    if not 2<=len(bounds)<=5 or any(not .34<=b-a-HEADER<=.69 for a,b in zip(bounds,bounds[1:])):proof['reason']='frame-duration';return None,proof
    rows=[];used=0
    for a,b in zip(bounds,bounds[1:]):
        obs=[e for e in notes if a<=e['t']<b];used+=len(obs);h=candidates(obs,a+HEADER,b);proof['frames'].append(dict(start=a,end=b,note_count=len(obs),candidates=h))
        if len(h)!=1:proof['reason']='local-ambiguity-or-loss';return None,proof
        rows.append(h[0][:2])
    if used!=len(notes):proof['reason']='unassigned-notes';return None,proof
    tree=G['decode'](rows,'poly');proof['reason']='admitted' if tree else 'grammar';return tree,proof
CONDITIONS=('clean','global','local','jitter','local_erase','global_noise','local_noise','strong','lost_marker','lost_end','insert_marker','long_insert','marker_drift','drift_noise','nonuniform_marker','noise_only')
MODES=('oracle','uniform','marked','calibrated')
def main(out):
    out=Path(out);out.mkdir();raw=Path(__file__).with_name('polyphonic-depth.py').read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==PIN
    rng=np.random.default_rng(SEED);trees=G['catalogue']();ids=[]
    for n in range(1,5):
        pool=[i for i,t in enumerate(trees) if len(G['encode'](t))==n];ids.extend(map(int,rng.choice(pool,min(20,len(pool)),replace=False)))
    traces=[];summary={c:{m:Counter() for m in MODES} for c in CONDITIONS};spec=[]
    for i in ids:
        tree=trees[i];rows=G['encode'](tree)
        for j,c in enumerate(CONDITIONS):
            seed=SEED*100000+i*100+j;x,bounds=render(rows,c,seed);ev=observe(x);outs={}
            for m in MODES:
                got,proof=decode(ev,m,bounds if m=='oracle' else None);s=G['classify'](got,tree);summary[c][m][s]+=1;outs[m]=dict(status=s,meaning=got,proof=proof)
            traces.append(dict(tree_index=i,tree=tree,condition=c,seed=seed,true_bounds=bounds,observations=ev,pcm_sha256=sha(x.tobytes()),outcomes=outs,samples=len(x)))
            if i==ids[-1] and c in ('clean','local','local_erase','lost_marker','lost_end','strong','long_insert','marker_drift','drift_noise','nonuniform_marker'):
                name=c+'.wav';save(out/name,x);spec.append((name,str(tree),str({m:v['status'] for m,v in outs.items()})))
    # Negative control: correctly framed alternative is not detectable as false by framing alone.
    original=('not',('fault',));alternate=('quote',('fault',));x,b=render(G['encode'](alternate),'clean',SEED);ev=observe(x);got,pr=decode(ev,'marked');assert got==alternate
    save(out/'coherent-alternate.wav',x);spec.append(('coherent-alternate.wav',str(original),'actual decoded '+str(got)))
    witness=dict(intended=original,rendered=alternate,decoded=got,observations=ev,proof=pr,pcm_sha256=sha(x.tobytes()))
    receipt=dict(seed=SEED,rate=RATE,source_commit=REF,source_blob=PIN,trees=ids,summary=summary,cases=len(traces),decisions=len(traces)*len(MODES),witness=witness,header_ms=64,nominal_body_ms=480)
    assert summary['clean']['marked']['correct']==len(ids),summary['clean']
    assert summary['noise_only']['marked']['withheld']==len(ids)
    assert summary['marker_drift']['calibrated']['correct']==len(ids)
    for name,obj in [('receipt.json',receipt),('traces.json',traces)]:(out/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    (out/'index.html').write_text('<!doctype html><meta charset=utf-8><title>MHAC stream grammar</title><h1>Framed melodic grammar</h1><p>Original synthetic audio. Start at low volume. No human evidence.</p>'+''.join(f'<section><h2>{html.escape(n)}</h2><p>{html.escape(t)} — {html.escape(s)}</p><audio controls preload="none" src="{n}"></audio></section>' for n,t,s in spec)+'<script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>\n')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},sort_keys=True,indent=2)+'\n');print(json.dumps(receipt,indent=2))
def save(path,x):
    with wave.open(str(path),'wb') as w:w.setparams((1,2,RATE,0,'NONE','not compressed'));w.writeframes(x.tobytes())
if __name__=='__main__':main(sys.argv[1])
