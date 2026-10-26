#!/usr/bin/env python3
"""Bounded training-only waveguide study; writes candidate paths, no source/audio reads."""
import argparse,hashlib,json,math,pathlib
import numpy as np
from scipy.optimize import least_squares,brentq
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--sections',type=int,choices=[16,32],default=16)
parser.add_argument('--output',type=pathlib.Path,default=ROOT/'out/waveguide-study')
args=parser.parse_args();SECTIONS=args.sections
BASE=args.output.resolve();BASE.mkdir(parents=True,exist_ok=True)
OUT=BASE/('sections'+str(SECTIONS));OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'References/GrandFullRange/combined_train_features.json'
source=json.loads(SOURCE.read_text())
assert source['fresh_reserved_recordings_opened'] is False
rows={s['id']:s for s in source['samples']}
FS=48000.

def phase(w,D,cs,alpha=0):
    w=np.asarray(w)
    return D*w+np.sum(2*np.arctan2((1-np.asarray(cs)[:,None])*np.sin(w/2),(1+np.asarray(cs)[:,None])*np.cos(w/2)),axis=0)-np.angle((1-alpha)+alpha*np.exp(-1j*w))

def fitpath(f,n,f1,B,fraction,count):
    w=2*np.pi*f/FS;target=2*np.pi*n*fraction
    L=FS/f1
    d=max(1.001,L*(1.5*B/(np.pi**2*SECTIONS))**(1/3))
    guess=int(round(fraction*L-count*d))
    best=None
    # At least one sample of delay makes all ports explicit/causal.
    for D in range(max(1,guess-25),max(1,guess+25)+1):
        group=np.array([count//2,count-count//2])
        def residual(x):
            ds=np.exp(x)
            cs=np.repeat((1-ds)/(1+ds),group)
            return (phase(w,D,cs)-target)/target
        for initial in ([d*.75,d*1.25],[d,d],[1.001,d*2]):
            x=least_squares(residual,np.log(np.maximum(initial,1)),bounds=(np.log([1,1]),np.log([2000,2000])),max_nfev=160)
            score=float(np.mean(residual(x.x)**2))
            if best is None or score<best[0]:
                ds=np.exp(x.x);best=(score,D,np.repeat((1-ds)/(1+ds),group).tolist())
    return dict(delay=best[1],allpass=best[2],gain=1.,mix=0.,fit_fraction=fraction)

def anchor(midi,a,b,c):
    return math.exp(math.log(a)+(math.log(b)-math.log(a))*(midi-36)/24) if midi<=60 else math.exp(math.log(b)+(math.log(c)-math.log(b))*(midi-60)/36)

def totalphase(w,l,r):return phase(np.atleast_1d(w),l['delay'],l['allpass'],l['mix'])+2*phase(np.atleast_1d(w),r['delay'],r['allpass'],r['mix'])

def frequencies(l,r,N):
    return np.array([brentq(lambda w:float(totalphase(w,l,r)[0]-2*np.pi*n),1e-10,np.pi-1e-8)*FS/(2*np.pi) for n in N])

report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'training_ids':['C2v4','C4v4','C6v4'],'reserved_audio_opened':False,'cases':[]}
for ident in report['training_ids']:
    row=rows[ident];assert row['split']=='train' and row['layer']==4
    f1=row['f1_hz'];B=row['B'];N=np.arange(1,21)
    target=N*f1*np.sqrt((1+B*N*N)/(1+B));N=N[target<19000];target=target[:len(N)]
    left=fitpath(target,N,f1,B,.12,SECTIONS//8);right=fitpath(target,N,f1,B,.44,7*SECTIONS//16)
    actual=frequencies(left,right,N)
    lossless_error=1200*np.log2(actual/target)
    # Fit positive contraction to the original authored isolated-string loss,
    # not to ambiguous microphone-band decays or common-unison prompt loss.
    desired_sigma=.11+.21*(f1/440)**.6+.000012*target**1.30+.00000000035*target**2
    w=2*np.pi*target/FS
    eps=1e-6
    gd=(totalphase(w+eps,left,right)-totalphase(w-eps,left,right))/(2*eps)
    def loss_residual(x):
        g=math.exp(-x[0]);alpha=x[1]
        mag=g*np.abs((1-alpha)+alpha*np.exp(-1j*w))
        sigma=-FS*3*np.log(mag)/gd
        return np.log(sigma/desired_sigma)
    lossfit=least_squares(loss_residual,[.00002,.0001],bounds=([1e-9,0],[.2,.49]))
    g=math.exp(-lossfit.x[0]);mix=float(lossfit.x[1])
    # Same loss filter on each path: preserve reciprocity; later quantify
    # extra loss phase instead of silently declaring the pitch fit unchanged.
    for p in (left,right):p['gain']=g;p['mix']=mix
    lossy_actual=frequencies(left,right,N)
    mu=min(.075,max(.004,anchor(row['midi'],.0184,.0063,.0052)))
    length=min(2.03,anchor(row['midi'],1.90,.62,.09))
    Z=mu*2*length*f1/math.sqrt(1+B)
    name=ident[:-2]+'-s'+str(SECTIONS)
    cfg=OUT/(name+'.cfg')
    with cfg.open('w') as out:
        out.write(f'{name} {f1:.17g} {B:.17g} {Z:.17g} .12\n')
        for p in (left,right):out.write(f"{p['delay']} {p['gain']:.17g} {p['mix']:.17g} {len(p['allpass'])} "+' '.join(f'{x:.17g}' for x in p['allpass'])+'\n')
    case={'id':ident,'f1_hz':f1,'B':B,'impedance_kg_s':Z,'length_m':length,'mu_kg_m':mu,'left':left,'right':right,
          'integer_roundtrip_samples':left['delay']+2*right['delay'],'allpass_roundtrip_sections':SECTIONS,
          'lossless_max_abs_cents':float(np.max(np.abs(lossless_error))),'lossless_rms_cents':float(np.sqrt(np.mean(lossless_error**2))),
          'partials':[dict(n=int(n),target_hz=float(t),lossless_hz=float(a),lossy_phase_hz=float(b),lossless_cents=float(e),lossy_phase_cents=float(1200*np.log2(b/t)),target_sigma_per_second=float(s)) for n,t,a,b,e,s in zip(N,target,actual,lossy_actual,lossless_error,desired_sigma)]}
    report['cases'].append(case)
    print(name,'partials',len(N),'D',case['integer_roundtrip_samples'],'lossless max/rms cents',case['lossless_max_abs_cents'],case['lossless_rms_cents'],'loss g,mix',g,mix,flush=True)
(OUT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
