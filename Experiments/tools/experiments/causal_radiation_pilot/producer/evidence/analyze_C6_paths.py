"""Posthoc source-path diagnosis only; fixed pilot/gates/source unchanged."""
from pathlib import Path
import datetime,hashlib,json
import numpy as np
from scipy import signal
OUT=Path(__file__).resolve().parent;RATE=48000;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pole=np.exp(-2*np.pi*24/RATE)
def hp(x):return signal.lfilter([pole,-pole],[1,-pole],x,axis=0)
def project(x,a,b):
 n=len(x);win=signal.windows.hann(n,sym=False);Y=np.fft.rfft(x*win[:,None],axis=0);freq=np.fft.rfftfreq(n,1/RATE);mask=(freq>=a)&(freq<b);z=Y[mask];norm=2/(n*np.sum(win*win)*2);return z,norm
rms=lambda x:float(np.sqrt(np.mean(x*x)));cases=[]
for name in ['C6v4','C6v12']:
 folder=OUT/'pilot'/name;raw=np.fromfile(folder/'trace.f64le','<f8').reshape(-1,15);old=np.fromfile(folder/'baseline.f32le','<f4').reshape(-1,2).astype(float);new=np.fromfile(folder/'candidate.f32le','<f4').reshape(-1,2).astype(float)
 B=hp(raw[:,2:4]);Cnew=hp(raw[:,4:6]);Cold=old-B;rows=[]
 for lo,hi in [(.005,.02),(.02,.05),(.05,.1)]:
  first=4800+round(lo*RATE);last=4800+round(hi*RATE);segments={key:x[first:last] for key,x in [('old',old),('new',new),('raw_B',B),('old_instant_C',Cold),('new_causal_C',Cnew)]};bands={}
  for band in [(31.25,250.),(250.,500.),(500.,1000.),(1000.,2000.),(4000.,8000.)]:
   spectra={key:project(x,*band)[0] for key,x in segments.items()};norm=project(segments['old'],*band)[1];E={key:float(np.sum(abs(z)**2)) for key,z in spectra.items()};metrics={}
   for key,z in spectra.items():
    own_rms=float(np.sqrt(E[key]*norm));metrics[key]={'band_rms_model_units':own_rms,'band_rms_db_reference1':float(20*np.log10(own_rms)) if own_rms else None,'power_db_relative_old':float(10*np.log10(E[key]/E['old'])) if E[key]*E['old'] else None,'coherent_projection_on_old':float(np.real(np.sum(z*np.conj(spectra['old'])))/E['old']) if E['old'] else None,'coherent_projection_on_new':float(np.real(np.sum(z*np.conj(spectra['new'])))/E['new']) if E['new'] else None}
   inner=np.sum(spectra['raw_B']*np.conj(spectra['new_causal_C']));metrics['raw_B_vs_new_C']={'phase_degrees':float(np.angle(inner,deg=True)),'normalized_squared_coherence':float(abs(inner)**2/(E['raw_B']*E['new_causal_C'])) if E['raw_B']*E['new_causal_C'] else None,'two_cross_over_B_plus_C_own_power':float(2*inner.real/(E['raw_B']+E['new_causal_C'])) if E['raw_B']+E['new_causal_C'] else None}
   bands[f'{band[0]:g}-{band[1]:g}Hz']=metrics
  rows.append({'window_seconds':[lo,hi],'native_FFT_resolution_Hz':1/(hi-lo),'bands':bands})
 case={'id':name,'new_raw_reconstruction_max_error_after_HP':float(np.max(abs(B+Cnew-new))),'windows':rows,'artifacts':{str(p):sha(p) for p in [folder/'baseline.f32le',folder/'candidate.f32le',folder/'trace.f64le']}};cases.append(case)
 for row in rows:
  m=row['bands']['31.25-250Hz'];print(name,row['window_seconds'],'Bvsold_dB',m['raw_B']['power_db_relative_old'],'Coldvsold_dB',m['old_instant_C']['power_db_relative_old'],'Cnewvsold_dB',m['new_causal_C']['power_db_relative_old'],'newvsold_dB',m['new']['power_db_relative_old'],'B_Cnew_phase',m['raw_B_vs_new_C']['phase_degrees'],'B_Cnewcross',m['raw_B_vs_new_C']['two_cross_over_B_plus_C_own_power'])
report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'PosthocC6source-path diagnosis fromexisting6pilottraces only. No rendering/fitting/gate changes.','components':{'raw_B':'Originaluncorrectedphysicalboardobserver,HP24sameasAPI','old_instant_C':'OldAPIoutput minusraw_B; instantaneousmodalradiationcorrection includingoriginalfloatobserverroundoff','new_causal_C':'Independentloadedobservercorrection, HP24same','old':'Exactold3.8control APIoutput','new':'Exactpilotcandidate APIoutput'},'cases':cases,'limits':['Force/subsystemidentity ofreferenceLF remainsUNASSIGNED. Theseprojections explainmodelpaths only.','Shortwindow nativebins cancontain highcarrier leakage; allrecordedcomponentpowers/crossphases retained.','Pressurecomponentscoherentlycancel, so ownpowers do notadd. Largepositive/negativeprojection shares are valid.','Reconstructiondifferenceincludes APIfloat32 rounding and independentdoubleHP accumulation; notmechanicalchanges.','GlobalpilotFAILandbothC6regressions remain unchanged.'],'source_sha256':sha(OUT/'analyze_C6_paths.py')}
(OUT/'C6-path-attribution.json').write_text(json.dumps(report,indent=2)+'\n');print('reportsha',sha(OUT/'C6-path-attribution.json'))
