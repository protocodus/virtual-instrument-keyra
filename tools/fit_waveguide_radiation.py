#!/usr/bin/env python3
"""C2/C4 observation-only, phase-aware fixed stable IIR feasibility study.

No recording is read, no note IR is a runtime asset, and no plugin/header or
canonical calibration is changed. All models and adverse results are retained.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, subprocess, time
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1]
FS=48000.; HP_POLE=math.exp(-2*math.pi*24/FS)
SOURCES=['tools/probe_waveguide_radiation.cpp','tools/probe_waveguide_radiation_cost.cpp',
 'tools/fit_waveguide_radiation.py','include/keyra/physics/WaveguideString.h',
 'src/full_reference/grand.cpp','src/full_reference/calibration.h',
 'tests/data/coupled-waveguide/C2-s32.cfg','tests/data/coupled-waveguide/C4-s32.cfg']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def transfer(path,z):
 zi=1/z;h=zi**path['delay']
 for c in path['allpass']:h=h*(c+zi)/(1+c*zi)
 fir=1-path['mix']+path['mix']*zi
 if path['dc_shelf']:
  shelf=path['gain']+(1-path['gain'])*(1-path['dc_pole'])/(1-path['dc_pole']*zi)
  return h*fir*shelf
 return h*fir*path['gain']

def wg_response(d,z):
 p=transfer(d['left'],z);q=transfer(d['to_bridge'],z);r=transfer(d['from_bridge'],z);den=1-p*q*r
 velocity=(1-p)*(1-q*r)/(2*d['impedance']*den)/d['choir_count']
 reaction=q*(1-p)/den/d['choir_count']
 return np.column_stack([reaction,velocity])

def modal_response(d,z):
 zi=1/z;out=np.zeros((len(z),2),complex);velocity=np.zeros(len(z),complex)
 for m in d['modes']:
  c,s,damp=m['c'],m['s'],m['damp'];bq,bp=m['force_q'],m['force_p']*damp
  den=1-c*(1+damp*damp)*zi+damp*damp*zi*zi
  q=((1-c*damp*damp*zi)*bq+s*damp*zi*bp)/den
  p=(-s*damp*zi*bq+(1-c*zi)*bp)/den
  for ch in range(2):out[:,ch]+=m['rad'][2*ch]*q+m['rad'][2*ch+1]*p
  velocity+=m['hammer']*m['omega']*p
 return out,velocity

def path_phase(p,w):
 phase=p['delay']*w
 for c in p['allpass']:phase=phase+2*np.arctan2((1-c)*np.sin(w/2),(1+c)*np.cos(w/2))
 zi=np.exp(-1j*w);phase=phase-np.angle(1-p['mix']+p['mix']*zi)
 if p['dc_shelf']:phase=phase-np.angle(p['gain']+(1-p['gain'])*(1-p['dc_pole'])/(1-p['dc_pole']*zi))
 return phase

def pole_rows(d):
 modal=[]
 for m in d['modes']:
  A=np.array([[m['c'],m['s']*m['damp']],[-m['s']*m['damp'],m['c']*m['damp']**2]])
  p=np.linalg.eigvals(A)[0]
  modal.append([abs(np.angle(p))*FS/(2*np.pi),-FS*math.log(abs(p))])
 def ph(w):return path_phase(d['left'],w)+path_phase(d['to_bridge'],w)+path_phase(d['from_bridge'],w)
 maximum=float(ph(2*np.pi*19000/FS));wg=[]
 for n in range(1,int(maximum/(2*np.pi))+1):
  w=brentq(lambda w:float(ph(w)-2*np.pi*n),1e-8,2*np.pi*19000/FS)
  eps=1e-7;gd=float((ph(w+eps)-ph(w-eps))/(2*eps));z=np.exp(1j*w)
  loop=transfer(d['left'],z)*transfer(d['to_bridge'],z)*transfer(d['from_bridge'],z)
  wg.append([w*FS/(2*np.pi),-FS*math.log(abs(loop))/gd])
 return modal,wg

def grid(d,validation=False):
 modal,wg=pole_rows(d)
 f=list(np.linspace(20.123 if validation else 20,19000,1301 if validation else 1025))
 f+=list(np.geomspace(21.137 if validation else 20.1,18998.6,1001 if validation else 769))
 offsets=[-.9,-.2,.2,.9,3.,9.] if validation else [-8.,-2.,-.5,0,.5,2.,8.]
 for centre,decay in modal+wg:
  for offset in offsets:
   x=centre+offset*decay/(2*np.pi)
   if 20<x<19000:f.append(x)
 f=np.unique(f);w=np.empty(len(f));w[1:-1]=(f[2:]-f[:-2])/2;w[0]=(f[1]-f[0])/2;w[-1]=(f[-1]-f[-2])/2
 return f,w

def poles(count):
 f=np.geomspace(60,14000,count);q=np.full(count,2.)
 r=np.exp(-np.pi*f/(FS*q));theta=2*np.pi*f/FS
 return np.column_stack([r*np.cos(theta),r*np.sin(theta),1-r])

def feature_response(x,z,bank):
 zi=1/z;one=[np.ones(len(z),complex)]
 for a,b,g in bank:
  den=1-2*a*zi+(a*a+b*b)*zi*zi
  one.extend([g*(1-a*zi)/den,g*b*zi/den])
 return np.column_stack([basis*x[:,j] for j in range(x.shape[1]) for basis in one])

def time_features(x,bank):
 one=[]
 for j in range(x.shape[1]):
  one.append(x[:,j])
  for a,b,g in bank:
   den=[1,-2*a,a*a+b*b]
   one.extend([signal.lfilter([g,-g*a],den,x[:,j]),signal.lfilter([0,g*b],den,x[:,j])])
 return np.column_stack(one)

def hp(x):return signal.lfilter([1,-1],[1,-HP_POLE],x,axis=0)
def delay(x,count):return np.pad(x,((count,0),(0,0)))[:len(x)] if count else x

def relative(a,b):return float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-30))
def db(x):return float(20*np.log10(max(float(x),1e-30)))
def stereo(x):
 l,r=x[:,0],x[:,1];mid=(l+r)/2;side=(l-r)/2
 return {'channel_correlation':float(np.dot(l,r)/max(np.linalg.norm(l)*np.linalg.norm(r),1e-30)),
 'side_mid_db':db(np.linalg.norm(side)/max(np.linalg.norm(mid),1e-30)),
 'left_right_db':db(np.linalg.norm(l)/max(np.linalg.norm(r),1e-30))}
def band_error(a,b):
 n=8192;aa=np.fft.rfft(a[:4800],n=n,axis=0);bb=np.fft.rfft(b[:4800],n=n,axis=0);f=np.fft.rfftfreq(n,1/FS)
 values=[]
 for centre in 62.5*2**(np.arange(25)/3):
  mask=(f>=centre/2**(1/6))&(f<centre*2**(1/6));pa=np.sum(abs(aa[mask])**2);pb=np.sum(abs(bb[mask])**2)
  if pb>1e-20:values.append(abs(10*np.log10(max(pa,1e-30)/pb)))
 return float(np.mean(values))

def selfcheck(out,models):
 rows=[]
 for name,d in models.items():
  data=np.fromfile(out/'data'/f'{name}-fixture0.f64',dtype='<f8').reshape(-1,6)
  f=np.geomspace(30.73,18011,32);sigma=30.;z=np.exp((sigma+2j*np.pi*f)/FS)
  weights=np.exp(-(sigma+2j*np.pi*f[:,None])*np.arange(len(data))/FS)
  actual=weights@data[:,[2,1,3,4,5]];wg=wg_response(d,z);modal,velocity=modal_response(d,z)
  expected=np.column_stack([wg,modal,velocity]);err=np.abs(actual-expected)/np.maximum(np.abs(expected),1e-14)
  # Extremely small transfer channels are assessed with a global scale floor.
  norm=np.max(np.abs(actual-expected))/max(np.max(abs(expected)),1e-30)
  assert norm<1e-9,(name,norm)
  bank=poles(4);pred=feature_response(wg,z,bank)
  actual_features=weights@time_features(data[:,[2,1]],bank)
  ferr=np.max(abs(pred-actual_features))/max(np.max(abs(pred)),1e-30);assert ferr<1e-9
  rows.append({'name':name,'maximum_absolute_transfer_error':float(np.max(abs(actual-expected))),
   'maximum_transfer_error_relative_global_peak':float(norm),'maximum_relative_per_channel_error':float(np.max(err)),
   'filter_feature_transfer_relative_global_error':float(ferr),'dlt_sigma_per_second':sigma,'samples':len(data)})
 return {'passed':True,'rows':rows,'scope':'Actual C++ impulse traces vs exact discrete modal/WG path formula, including DC shelf/allpasses; feature time recurrence vs complex transfer. No recording read.'}

def write_coeff(path,bank,coeff,ni):
 with path.open('w') as f:
  f.write(f'{ni} {len(bank)}\n')
  for row in bank:f.write(' '.join(f'{x:.17g}' for x in row)+'\n')
  for ch in range(2):f.write(' '.join(f'{x:.17g}' for x in coeff[:,ch])+'\n')

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'out/waveguide-radiation');parser.add_argument('--selfcheck-only',action='store_true');args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 models={n:json.loads((out/'data'/f'{n}-model.json').read_text()) for n in ['C2','C4']}
 check=selfcheck(out,models);write(out/'selfchecks.json',check)
 if args.selfcheck_only:print(json.dumps(check,indent=2));return
 configs=[(ni,k,d,ridge) for ni in [1,2] for k in [2,4,8] for d in [0,256] for ridge in [1e-4,1e-2]]+[(2,16,0,1e-4)]
 source={f:sha(ROOT/f) for f in SOURCES};data={str(p.relative_to(ROOT)):sha(p) for p in sorted((out/'data').glob('*'))}
 freeze={'schema_version':2,'previous_setup_negative':'out/waveguide-radiation/v1-closed-damper/scope-correction.json','damping_condition':'Target uses original intrinsic held-string loss with dampers open; constructor closed-damper run is archived separately.','frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source_sha256':source,'data_sha256':data,
  'configuration_matrix':[{'inputs':ni,'pole_pairs':k,'target_delay_samples':d,'ridge':r} for ni,k,d,r in configs],
  'target':'One original first-choir primary string: radQ*q+radP*p correction ONLY, driven by generalized key force. Waveguide receives key force divided by choir count, fixed bridge. Original board observer is excluded rather than counted twice.',
  'fit':'Real fixed stable parallel IIR residue fit to weighted complex forward responses; shared conjugate poles geometrically60..14000Hz,Q2, feedthrough; no target/input division, no magnitude-only fit.',
  'weight':'Frequency quadrature, common24Hz high-pass squared, force power prior1/(1+(f/5000)^4).','new_recording_reads':False,
  'target_delay':'0primary;256sample(5.333ms) delayed-reference fit. This bank has no enforced pure runtime delay; pretarget leakage is measured and no host latency implementation is claimed.','no_default_adoption':True}
 write(out/'freeze.json',freeze)
 snap=out/'source-snapshot'
 for f in SOURCES:
  p=snap/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 (out/'coefficients').mkdir(exist_ok=True);results=[];pole_diagnostics=[]
 for name,d in models.items():
  f,quad=grid(d);z=np.exp(2j*np.pi*f/FS);x=wg_response(d,z);target,_=modal_response(d,z)
  h=(1-1/z)/(1-HP_POLE/z);weight=quad*abs(h)**2/(1+(f/5000)**4);weight/=weight.sum()
  fv,qv=grid(d,True);zv=np.exp(2j*np.pi*fv/FS);xv=wg_response(d,zv);yv,_=modal_response(d,zv);hv=(1-1/zv)/(1-HP_POLE/zv)
  wv=qv*abs(hv)**2/(1+(fv/5000)**4);wv/=wv.sum()
  traces={i:np.fromfile(out/'data'/f'{name}-fixture{i}.f64',dtype='<f8').reshape(-1,6) for i in range(4)}
  modal,wgp=pole_rows(d);pole_diagnostics.append({'name':name,'modal_primary_modes':len(modal),'waveguide_phase_resonances_below19k':len(wgp),
    'first20_nearest_resonance_cents':[float(1200*np.log2(min(wgp,key=lambda p:abs(p[0]-m[0]))[0]/m[0])) for m in modal[:20]],
    'bridge_earliest_integer_samples':d['to_bridge']['delay'],'bridge_earliest_integer_ms':1000*d['to_bridge']['delay']/FS,
    'original_correction_first_frame':traces[0][0,3:5].tolist(),'modal_poles_hz_sigma':modal,'WG_phase_resonances_hz_sigma_estimate':wgp})
  cache={}
  for ni,k,latency,ridge in configs:
   bank=poles(k);A=feature_response(x[:,:ni],z,bank);shift=np.exp(-2j*np.pi*f*latency/FS);y=target*shift[:,None]
   ww=np.sqrt(weight);Aw=A*ww[:,None];Yw=y*ww[:,None];scales=np.sqrt(np.sum(abs(Aw)**2,axis=0));scales=np.maximum(scales,1e-30)
   normalized=Aw/scales
   realA=np.row_stack([normalized.real,normalized.imag]);realY=np.row_stack([Yw.real,Yw.imag])
   coeff=np.linalg.solve(realA.T@realA+ridge*np.eye(A.shape[1]),realA.T@realY)/scales[:,None]
   pred=feature_response(xv[:,:ni],zv,bank)@coeff;truth=yv*np.exp(-2j*np.pi*fv*latency/FS)[:,None]
   error=relative(pred*np.sqrt(wv)[:,None],truth*np.sqrt(wv)[:,None])
   active=abs(truth)>np.max(abs(truth))*10**(-50/20)
   mag=np.abs(20*np.log10(np.maximum(abs(pred[active]),1e-30)/abs(truth[active])))
   phase=np.abs(np.angle(pred[active]*np.conj(truth[active])))*180/np.pi
   ident=f'{name}-i{ni}-k{k}-d{latency}-r{ridge:g}';path=out/'coefficients'/f'{ident}.cfg';write_coeff(path,bank,coeff,ni)
   fixture_rows=[]
   for i,t in traces.items():
    key=(ni,k,i)
    if key not in cache:cache[key]=time_features(t[:,[2,1]][:,:ni],bank)
    audio=hp(cache[key]@coeff);reference=hp(delay(t[:,3:5],latency));reference_aligned=hp(t[:,3:5]);audio_aligned=audio[latency:] if latency else audio
    ref_aligned=reference_aligned[:len(audio_aligned)]
    fixture_rows.append({'fixture':i,'whole_second_relative_error':relative(audio,reference),'whole_second_null_db':db(relative(audio,reference)),
     'first100ms_relative_error_after_target_delay_alignment':relative(audio_aligned[:4800],ref_aligned[:4800]),
     'first100ms_third_octave_MAE_db':band_error(audio_aligned,ref_aligned),
     'aligned_window_relative_error':{label:relative(audio_aligned[int(start*FS):int(end*FS)],ref_aligned[int(start*FS):int(end*FS)]) for label,start,end in [('0_5ms',0,.005),('5_20ms',.005,.02),('20_100ms',.02,.1),('100_900ms',.1,.9)]},
     'pretarget_output_energy_fraction_of_reference':float(np.sum(audio[:latency]**2)/max(np.sum(reference**2),1e-30)) if latency else 0,
     'pretarget_output_peak_relative_reference_peak':float(np.max(abs(audio[:latency]))/max(np.max(abs(reference)),1e-30)) if latency else 0,
     'reference_stereo':stereo(reference),'prediction_stereo':stereo(audio),
     'mono_relative_error':relative(np.sum(audio,axis=1),np.sum(reference,axis=1)),
     'raw_prediction_peak':float(np.max(abs(audio))),'raw_reference_peak':float(np.max(abs(reference)))})
   row={'id':ident,'name':name,'inputs':ni,'input_names':['bridge_reaction','contact_velocity'][:ni],'pole_pairs_per_input':k,
    'target_delay_samples':latency,'target_delay_ms':1000*latency/FS,'ridge':ridge,'numeric_coefficient_count':int(3*k+coeff.size),
    'runtime_real_states':2*k*ni,'maximum_pole_radius':float(np.max(np.hypot(bank[:,0],bank[:,1]))),
    'validation_weighted_complex_relative_error':error,'validation_weighted_complex_null_db':db(error),
    'validation_prominent_frequency_magnitude_MAE_db':float(np.mean(mag)),
    'validation_prominent_frequency_phase_MAE_deg':float(np.mean(phase)),
    'coefficient_path':str(path.relative_to(ROOT)),'coefficient_sha256':sha(path),'fixtures':fixture_rows}
   results.append(row);print(json.dumps({k:row[k] for k in ['id','validation_weighted_complex_relative_error','validation_weighted_complex_null_db']}),flush=True)
 report={'schema_version':1,'passed':'study_complete_not_fidelity_gate','freeze_sha256':sha(out/'freeze.json'),'selfchecks':check,
  'pole_diagnostics':pole_diagnostics,'models':results,'no_default_adoption':True,'recordings_read':False,
  'limits':['First choir line primary polarization only, fixed bridge, original authored calibration, C2/C4 only.','No arbitrary board-input radiation equivalence, secondary polarization, unison or complete-note sound match.','Fixed-pole residue fitting is one bounded method; poor fits do not prove every compact observer impossible.','Coefficients are compact numeric stable IIR parameters, never stored note/impulse audio playback.','Existing board acceleration observation must remain separate; this target is additive string correction only.']}
 assert source=={f:sha(ROOT/f) for f in SOURCES}
 assert data=={str(p.relative_to(ROOT)):sha(p) for p in sorted((out/'data').glob('*'))}
 report['source_and_data_unchanged']=True;write(out/'report.json',report)
 print(json.dumps({'models':len(results),'report_sha256':sha(out/'report.json'),'source_and_data_unchanged':True}),flush=True)
if __name__=='__main__':main()
