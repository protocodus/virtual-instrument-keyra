#!/usr/bin/env python3
"""TRAIN26-only feasibility check for a shared complex stereo observation.

No fitting or default change. Holding out both velocities of each interior pitch
is a training cross-validation diagnostic, not a fresh recording test. Reserved
and historical held-out recordings are never opened.
"""
import argparse
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal.windows import hann

ROOT=Path(__file__).resolve().parents[1]
FEATURE=ROOT/'References/GrandExpanded/train_features.json'
D=json.loads(FEATURE.read_text()); samples=D['samples']
expected={f'{p}v{v}' for p in ['A1','C2','D#2','A2','C3','D#3','C4','D#4','A4','C5','D#5','A5','C6'] for v in (4,12)}
assert {s['id'] for s in samples}==expected and all(s['split']=='train' for s in samples)
WINDOWS=[(.05,.25),(.25,.75),(.75,1.5),(1.5,3.5)]

def load(s):
 path=ROOT/'References/GrandExpanded/recordings'/f"{s['id']}.wav"
 if not path.exists():path=ROOT/'Research/GrandPianoV2/reference/wav'/f"{s['id']}.wav"
 assert path.exists(),path
 sr,x=wavfile.read(path);assert sr==48000 and x.ndim==2 and x.shape[1]==2
 if x.dtype.kind in 'iu':x=x.astype(float)/(2.**(x.dtype.itemsize*8-1))
 else:x=x.astype(float)
 return sr,x[int(round(s['onset_seconds']*sr)):],str(path.relative_to(ROOT))

def cov_windows(s):
 sr,x,path=load(s); rows=[]
 for wi,(lo,hi) in enumerate(WINDOWS):
  y=x[int(lo*sr):int(hi*sr)]; n=len(y);nfft=1<<int(math.ceil(math.log2(n*2)))
  z=np.fft.rfft(y*hann(n,sym=False)[:,None],n=nfft,axis=0);f=np.fft.rfftfreq(nfft,1/sr);df=f[1]-f[0]
  scale=2/(nfft*np.sum(hann(n,sym=False)**2))
  pp=[]
  for p in s['partials']:
   center=p['frequency_hz'];width=min(.38*s['f1_hz'],max(3/(hi-lo),.004*center));a,b=center-width,center+width
   ilo=max(0,int(math.floor(a/df)) -1);ihi=min(len(f),int(math.ceil(b/df))+2)
   weight=np.clip((np.minimum(f[ilo:ihi]+df/2,b)-np.maximum(f[ilo:ihi]-df/2,a))/df,0,1)
   zz=z[ilo:ihi];pl=float(np.dot(weight,abs(zz[:,0])**2)*scale);pr=float(np.dot(weight,abs(zz[:,1])**2)*scale)
   c=complex(np.dot(weight,zz[:,0]*np.conj(zz[:,1]))*scale)
   tr=pl+pr;M=np.array([[pl,c],[np.conj(c),pr]],complex)/max(tr,1e-30)
   pp.append({'n':p['n'],'hz':center,'pl':pl,'pr':pr,'cross_real':c.real,'cross_imag':c.imag,'coherence_squared':min(1.,abs(c)**2/max(pl*pr,1e-60)),
    'phase_R_minus_L_deg':float(-np.angle(c)*180/np.pi),'right_minus_left_db':10*math.log10(max(pr,1e-30)/max(pl,1e-30)),
    'relative_total_power':tr/(2*s['early_rms']**2),'matrix':M})
  rows.append(pp)
 return {'id':s['id'],'midi':s['midi'],'layer':s['layer'],'path':path,'windows':rows}

def circular(a,b):return abs((a-b+180)%360-180)
def matrix(p):return p['matrix']
def coeff(M):
 l=math.sqrt(max(0,float(M[0,0].real)));r=math.sqrt(max(0,float(M[1,1].real)))*np.exp(-1j*np.angle(M[0,1]));return np.array([l,r])
def rank1(M):
 c=coeff(M);return np.outer(c,np.conj(c))/max(float(np.vdot(c,c).real),1e-30)
def aggregate(row):
 # Per-window trace normalization prevents louder strikes/windows from deciding
 # the geometry; only prominent observations can contribute.
 out={}
 for wi in (0,1):
  for p in row['windows'][wi]:
   if p['relative_total_power']<1e-4:continue
   out.setdefault(p['n'],[]).append(matrix(p))
 return {n:np.mean(M,axis=0) for n,M in out.items()}
def pannermatrix(note):
 pos=np.clip((note-64.5)/52,-.85,.85);v=np.array([1-.588*pos,1+.588*pos]);return np.outer(v,v)/np.dot(v,v)
def stats(v):
 a=np.asarray(v,float);return {'count':len(a),'mean':float(np.mean(a)),'median':float(np.median(a)),'p90':float(np.quantile(a,.9)),'p95':float(np.quantile(a,.95))}
def weighted_mean(v,w):return float(np.dot(v,w)/max(sum(w),1e-30))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'Validation/stereo-observation-feasibility.json')
    args=parser.parse_args()
    rows=[cov_windows(s) for s in sorted(samples,key=lambda x:(x['midi'],x['layer']))]
    byid={r['id']:r for r in rows}
    coh=[];phase=[];gain=[];weighted=[];weights=[];bad=[];velocity=[]
    for row in rows:
     for p in row['windows'][0]:
      if p['relative_total_power']>=1e-4:coh.append(p['coherence_squared'])
     a={p['n']:p for p in row['windows'][0]};z={p['n']:p for p in row['windows'][1]}
     for n in a.keys()&z.keys():
      x,y=a[n],z[n]
      if min(x['relative_total_power'],y['relative_total_power'])<1e-4:continue
      pd=circular(x['phase_R_minus_L_deg'],y['phase_R_minus_L_deg']);gd=abs(x['right_minus_left_db']-y['right_minus_left_db'])
      phase.append(pd);gain.append(gd);w=(x['pl']+x['pr']+y['pl']+y['pr']);weights.append(w);weighted.append(pd)
      if pd>60 or gd>6:bad.append({'id':row['id'],'n':n,'hz':x['hz'],'window_phase_difference_deg':pd,'window_gain_difference_db':gd,'coherence_early':x['coherence_squared'],'coherence_sustain':y['coherence_squared']})
    for note in sorted({r['midi'] for r in rows}):
     low=next(r for r in rows if r['midi']==note and r['layer']==4);high=next(r for r in rows if r['midi']==note and r['layer']==12)
     for wi in (0,1):
      a={p['n']:p for p in low['windows'][wi]};b={p['n']:p for p in high['windows'][wi]}
      for n in a.keys()&b.keys():
       x,y=a[n],b[n]
       if min(x['relative_total_power'],y['relative_total_power'])<1e-4:continue
       velocity.append({'midi':note,'n':n,'window':wi,'phase_difference_deg':circular(x['phase_R_minus_L_deg'],y['phase_R_minus_L_deg']),'gain_difference_db':abs(x['right_minus_left_db']-y['right_minus_left_db'])})
    # Train-only leave-one-pitch-out. Fit pooled covariance only from endpoint
    # training observations, target measurements remain excluded from prediction.
    notes=sorted({r['midi'] for r in rows}); pooled={}
    for note in notes:
     pieces=[aggregate(r) for r in rows if r['midi']==note]; pooled[note]={}
     for n in set(pieces[0])|set(pieces[1]):
      pooled[note][n]=np.mean([piece[n] for piece in pieces if n in piece],axis=0)
    cv=[]
    for i,note in enumerate(notes[1:-1],1):
     lo,hi=notes[i-1],notes[i+1];t=(note-lo)/(hi-lo);endpointA,endpointB=pooled[lo],pooled[hi]
     for target in [r for r in rows if r['midi']==note]:
      for wi in (0,1):
       for p in target['windows'][wi]:
        n=p['n']
        if p['relative_total_power']<1e-4 or n not in endpointA or n not in endpointB:continue
        A,B=endpointA[n],endpointB[n];M=matrix(p)
        covariance=(1-t)*A+t*B
        c=(1-t)*coeff(A)+t*coeff(B);cm=np.outer(c,np.conj(c))/max(float(np.vdot(c,c).real),1e-30)
        ratioA=np.log(max(float(A[1,1].real),1e-12)/max(float(A[0,0].real),1e-12));ratioB=np.log(max(float(B[1,1].real),1e-12)/max(float(B[0,0].real),1e-12))
        ratio=np.exp((1-t)*ratioA+t*ratioB);phaseA=-np.angle(A[0,1]);delta=np.angle(np.exp(1j*(-np.angle(B[0,1])-phaseA)));ph=phaseA+t*delta
        sc=np.array([math.sqrt(1/(1+ratio)),math.sqrt(ratio/(1+ratio))*np.exp(1j*ph)]);sm=np.outer(sc,np.conj(sc))
        predictions={'baseline_pan':pannermatrix(note),'linear_psd_covariance_rank2':covariance,'covariance_phase_rank1':rank1(covariance),'linear_complex_coeff_rank1':cm,'shortest_phase_log_ratio_rank1':sm,'nearest_neighbor_rank1':rank1(A if t<.5 else B)}
        cv.append({'id':target['id'],'midi':note,'n':n,'window':wi,'weight':p['relative_total_power'],
          'matrix_frobenius_error':{k:float(np.linalg.norm(v-M)) for k,v in predictions.items()},
          'gain_error_db':{k:abs(10*math.log10(max(float(v[1,1].real),1e-12)/max(float(v[0,0].real),1e-12))-p['right_minus_left_db']) for k,v in predictions.items()}})
    cvsummary={}
    for method in cv[0]['matrix_frobenius_error']:
     v=[x['matrix_frobenius_error'][method] for x in cv];w=[x['weight'] for x in cv];g=[x['gain_error_db'][method] for x in cv]
     cvsummary[method]={'weighted_matrix_error':weighted_mean(v,w),'unweighted_matrix_error':float(np.mean(v)),'weighted_gain_error_db':weighted_mean(g,w),'cases':len(v)}
    # Serialize measurements without native complex ndarray values.
    for row in rows:
     for win in row['windows']:
      for p in win:
       p.pop('matrix')
    report={'training_ids':sorted(expected),'heldout_cases_used':False,'training_source_sha256':hashlib.sha256(FEATURE.read_bytes()).hexdigest(),
     'method':'Hann FFT integrated per-partial covariance using same four windows/band widths as preserved benchmark; prominence at -40dB of early RMS squared.',
     'early_coherence_squared':stats(coh),'window_phase_difference_deg':stats(phase),'window_gain_difference_db':stats(gain),
     'window_phase_fraction_within_30deg':float(np.mean(np.array(phase)<=30)),
     'window_joint_fraction_phase30_gain3':float(np.mean((np.array(phase)<=30)&(np.array(gain)<=3))),
     'velocity_phase_difference_deg':stats([x['phase_difference_deg'] for x in velocity]),'velocity_gain_difference_db':stats([x['gain_difference_db'] for x in velocity]),
     'velocity_fraction_phase30_gain3':float(np.mean([(x['phase_difference_deg']<=30 and x['gain_difference_db']<=3) for x in velocity])),
     'leave_one_pitch_out_cv':cvsummary,'unstable_window_examples':sorted(bad,key=lambda x:x['window_phase_difference_deg'],reverse=True)[:30],
     'cv_rows':cv,'velocity_rows':velocity,'measurements':rows,
     'limits':'Training analysis only. Integrated covariance is not independent multi-realization statistical coherence. A rank-one observation cannot reproduce lower coherence; common coefficients do not identify microphone geometry or individual unisons.'}
    reliable=[]
    for row in rows:
     early={part['n']:part for part in row['windows'][0]}
     sustain={part['n']:part for part in row['windows'][1]}
     for partial in early.keys()&sustain.keys():
      a,z=early[partial],sustain[partial]
      def strong_cross_power(part):
       return (part['relative_total_power']>=1e-4 and part['coherence_squared']>=.5
               and min(part['pl'],part['pr'])/(part['pl']+part['pr'])>=.01)
      if strong_cross_power(a) and strong_cross_power(z):
       reliable.append((circular(a['phase_R_minus_L_deg'],z['phase_R_minus_L_deg']),
                        abs(a['right_minus_left_db']-z['right_minus_left_db'])))
    report['reliable_window_stability']={
     'gate':'Prominent partial, coherence-squared >=0.5, and each channel at least1%of partial power in both windows.',
     'phase_difference_deg':stats([row[0] for row in reliable]),
     'joint_fraction_phase30_gain3':float(np.mean([row[0]<=30 and row[1]<=3 for row in reliable]))}
    report['schema_version']=1
    report['analysis_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['engine_sha256']=hashlib.sha256((ROOT/'src/Piano.cpp').read_bytes()).hexdigest()
    report['training_recording_sha256']={row['id']:hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() for row in rows}
    residuals=[];registers={}
    for row in rows:
     values=[]
     for window in row['windows'][:2]:
      for part in window:
       if part['relative_total_power']<1e-4:continue
       pl,pr=part['pl'],part['pr'];cross=complex(part['cross_real'],part['cross_imag']);trace=pl+pr
       eigenvalue=max(0,float((1-np.sqrt(max(0,(pl-pr)**2+4*abs(cross)**2))/trace)/2))
       values.append(eigenvalue);residuals.append(eigenvalue)
     register='bass' if row['midi']<48 else 'middle' if row['midi']<72 else 'treble'
     registers.setdefault(register,[]).extend(values)
    report['rank_one_irreducible_eigenvalue_fraction']=stats(residuals)
    report['rank_one_residual_by_register']={name:stats(values) for name,values in registers.items()}
    by_note={}
    for row in cv:by_note.setdefault(row['midi'],[]).append(row)
    report['pitch_cv_summary']={str(note):{method:weighted_mean([row['matrix_frobenius_error'][method] for row in values],[row['weight'] for row in values]) for method in cvsummary} for note,values in by_note.items()}
    time=np.arange(24000)/48000;known_phase=.7
    signal=np.column_stack([np.sin(2*np.pi*261*time),np.sin(2*np.pi*261*time+known_phase)])
    transform=np.fft.rfft(signal*np.hanning(len(time))[:,None],axis=0)
    cross=np.sum(transform[:,0]*np.conj(transform[:,1]))
    phase_error=float(abs(np.angle(np.exp(1j*(-np.angle(cross)-known_phase)))))
    report['synthetic_csd_phase_sign_check']={'phase_radians':known_phase,'absolute_estimation_error_radians':phase_error,'passed':bool(phase_error<1e-7)}
    if not report['synthetic_csd_phase_sign_check']['passed']:raise AssertionError('Cross-phase convention failed')
    report['recommendation']='Leave the default unchanged: static rank-one complex interpolation is not supported by the training pitch cross-validation. A richer radiation/source model needs a separately controlled study.'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('cv_rows','velocity_rows','measurements','unstable_window_examples')},indent=2))


if __name__=='__main__':main()
