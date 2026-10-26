#!/usr/bin/env python3
"""Post-fit pole-aligned diagnostics; never refits or edits frozen candidates."""
from pathlib import Path
import hashlib,importlib.util,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'out/waveguide-radiation'
spec=importlib.util.spec_from_file_location('fixed_radiation',ROOT/'tools/fit_waveguide_radiation.py');fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def loop(d,z):return fit.transfer(d['left'],z)*fit.transfer(d['to_bridge'],z)*fit.transfer(d['from_bridge'],z)
def derivative(d,z,epsilon=1e-7):return (loop(d,z+epsilon)-loop(d,z-epsilon))/(2*epsilon)
def wg_pole(d,guess):
 f,sigma=guess;z=np.exp(complex(-sigma,2*np.pi*f)/fit.FS)
 for step in range(30):
  error=loop(d,z)-1
  if abs(error)<2e-12:break
  delta=error/derivative(d,z)
  if abs(delta)>.002:delta*=.002/abs(delta)
  z-=delta
 residual=float(abs(loop(d,z)-1));assert residual<2e-10,(guess,residual)
 return z,residual,step

def target_residue(m):
 c,s,d=m['c'],m['s'],m['damp'];A=np.array([[c,s*d],[-s*d,c*d*d]])
 eigen=np.linalg.eigvals(A);z=next(x for x in eigen if x.imag>0)
 projector=(A-np.conj(z)*np.eye(2))/(z-np.conj(z));B=np.array([m['force_q'],m['force_p']*d])
 C=np.array(m['rad']).reshape(2,2);return z,C@projector@B

def observer_residue(d,model,z):
 p=fit.transfer(d['left'],z);q=fit.transfer(d['to_bridge'],z);r=fit.transfer(d['from_bridge'],z)
 numerator=np.array([[q*(1-p)/d['choir_count'],(1-p)*(1-q*r)/(2*d['impedance']*d['choir_count'])]],complex)
 values=np.loadtxt(ROOT/model['coefficient_path'],skiprows=1+model['pole_pairs_per_input'])
 weights=values.T;features=fit.feature_response(numerator[:,:model['inputs']],np.array([z]),fit.poles(model['pole_pairs_per_input']))
 return (features@weights)[0]/(-z*derivative(d,z))

def highpass(z):return (1-1/z)/(1-fit.HP_POLE/z)
def phase(x):return float(np.angle(x)*180/np.pi)
def read_coeff(model):return np.loadtxt(ROOT/model['coefficient_path'],skiprows=1+model['pole_pairs_per_input']).T

def envelope(a,b):
 n=min(len(a),len(b))//240*240;aa=a[:n].reshape(-1,240,2);bb=b[:n].reshape(-1,240,2)
 ea=np.sqrt(np.mean(aa*aa,axis=(1,2)));eb=np.sqrt(np.mean(bb*bb,axis=(1,2)));gate=eb>eb.max()*1e-3
 difference=20*np.log10(np.maximum(ea[gate],1e-30)/eb[gate]);t=(np.arange(len(ea))+.5)*.005
 def slope(e):
  keep=(t>=.2)&(t<=.8)&(e>e.max()*1e-3)
  return float(np.polyfit(t[keep],20*np.log10(e[keep]),1)[0])
 return {'bin_ms':5,'reference_gate_db_relative_peak':-60,'scored_bins':int(gate.sum()),
 'MAE_db':float(np.mean(abs(difference))),'median_absolute_db':float(np.median(abs(difference))),
 'maximum_absolute_db':float(np.max(abs(difference))),'reference_200_800ms_slope_db_s':slope(eb),
 'prediction_200_800ms_slope_db_s':slope(ea)}

def main():
 frozen=json.loads((OUT/'freeze.json').read_text());report=json.loads((OUT/'report.json').read_text());source_before={f:sha(ROOT/f) for f in frozen['source_sha256']};assert source_before==frozen['source_sha256']
 rows=[];poles_by_name={};maximum_residual=0;maximum_derivative_disagreement=0
 for name in ['C2','C4']:
  d=json.loads((OUT/'data'/f'{name}-model.json').read_text());_,estimates=fit.pole_rows(d);pairs=[]
  for m in d['modes'][:20]:
   zt,kt=target_residue(m);ft=np.angle(zt)*fit.FS/(2*np.pi)
   guess=min(estimates,key=lambda x:abs(x[0]-ft));zw,residual,iterations=wg_pole(d,guess);fw=np.angle(zw)*fit.FS/(2*np.pi)
   de1=derivative(d,zw);de2=derivative(d,zw,5e-8);dd=abs(de1-de2)/abs(de2)
   maximum_residual=max(maximum_residual,residual);maximum_derivative_disagreement=max(maximum_derivative_disagreement,float(dd))
   pairs.append((m['n'],zt,kt,zw,ft,fw))
  strength=max(float(np.max(abs(p[2]*highpass(p[1])))) for p in pairs)
  poles_by_name[name]=[{'n':n,'reference_hz':ft,'WG_hz':fw,'cents':float(1200*np.log2(fw/ft)),
   'reference_sigma_per_second':float(-fit.FS*np.log(abs(zt))),'WG_sigma_per_second':float(-fit.FS*np.log(abs(zw))),
   'expected_phase_drift_100ms_degrees':float(360*(fw-ft)*.1)} for n,zt,kt,zw,ft,fw in pairs]
  for model in (x for x in report['models'] if x['name']==name):
   mode_rows=[]
   for n,zt,kt,zw,ft,fw in pairs:
    actual=kt*highpass(zt)*zt**(-model['target_delay_samples']);predicted=observer_residue(d,model,zw)*highpass(zw)
    gate=bool(np.min(abs(kt*highpass(zt)))>strength*10**(-50/20))
    lr_target=actual[0]/actual[1];lr_prediction=predicted[0]/predicted[1]
    mode_rows.append({'n':n,'reference_hz':ft,'WG_hz':fw,'cents':float(1200*np.log2(fw/ft)),
     'both_reference_channels_above_minus50db_gate':gate,
     'reference_mode_energy_weight':float(np.sum(abs(kt*highpass(zt))**2)/(2*(-fit.FS*np.log(abs(zt))))),
     'target_L_R_gain_db':fit.db(abs(lr_target)),'prediction_L_R_gain_db':fit.db(abs(lr_prediction)),
     'L_R_gain_error_db':fit.db(abs(lr_prediction/lr_target)),
     'L_R_phase_error_deg':phase(lr_prediction/lr_target),
     'absolute_mode_gain_errors_db':[fit.db(abs(predicted[ch]/actual[ch])) for ch in range(2)],
     'absolute_mode_phase_errors_deg':[phase(predicted[ch]/actual[ch]) for ch in range(2)]})
   scored=[x for x in mode_rows if x['both_reference_channels_above_minus50db_gate']]
   row={'id':model['id'],'mode_rows':mode_rows,'scored_L_R_modes':len(scored),
    'L_R_gain_MAE_db':float(np.mean([abs(x['L_R_gain_error_db']) for x in scored])),
    'L_R_phase_MAE_deg':float(np.mean([abs(x['L_R_phase_error_deg']) for x in scored])),
    'energy_weighted_L_R_gain_MAE_db':float(np.average([abs(x['L_R_gain_error_db']) for x in scored],weights=[x['reference_mode_energy_weight'] for x in scored])),
    'energy_weighted_L_R_phase_MAE_deg':float(np.average([abs(x['L_R_phase_error_deg']) for x in scored],weights=[x['reference_mode_energy_weight'] for x in scored])),
    'absolute_mode_gain_MAE_db':float(np.mean([abs(v) for x in scored for v in x['absolute_mode_gain_errors_db']])),
    'absolute_mode_phase_MAE_deg':float(np.mean([abs(v) for x in scored for v in x['absolute_mode_phase_errors_deg']]))}
   if model['target_delay_samples']==0 and model['ridge']==.0001 and (model['inputs'],model['pole_pairs_per_input']) in [(1,8),(2,8),(2,16)]:
    fixtures=[];weights=read_coeff(model);bank=fit.poles(model['pole_pairs_per_input'])
    for i in [1,2,3]:
     data=np.fromfile(OUT/'data'/f'{name}-fixture{i}.f64',dtype='<f8').reshape(-1,6)
     prediction=fit.hp(fit.time_features(data[:,[2,1]][:,:model['inputs']],bank)@weights);target=fit.hp(data[:,3:5])
     fixtures.append({'fixture':i,'envelope':envelope(prediction,target),'attack_0_5ms_relative_error':fit.relative(prediction[:240],target[:240]),
      'attack_5_20ms_relative_error':fit.relative(prediction[240:960],target[240:960]),
      'attack_20_100ms_relative_error':fit.relative(prediction[960:4800],target[960:4800]),
      'attack_0_100ms_third_octave_MAE_db':fit.band_error(prediction,target),
      'reference_stereo':fit.stereo(target),'prediction_stereo':fit.stereo(prediction)})
    row['selected_time_diagnostics']=fixtures
   rows.append(row)
 result={'schema_version':1,'passed':True,'source_sha256':sha(Path(__file__)),'source_and_frozen_inputs_unchanged':source_before=={f:sha(ROOT/f) for f in source_before},
  'frozen_fit_report_sha256':sha(OUT/'report.json'),'maximum_WG_loop_pole_residual':maximum_residual,
  'maximum_WG_derivative_two_epsilon_relative_disagreement':maximum_derivative_disagreement,
  'scope':'Post-fit diagnostics only. No refit. First20 exact complexWG/modal poles matched by nearest frequency; mode residues factor out each own denominator. L/Rnatural mode gain/phase errors separate spatial observation from highQ pitch/decay decorrelation. Not a listening/audibility or full-piano fidelity verdict.',
  'caveats':['Pointwise complex-frequency and raw waveform error can grow substantially from small high-Q pole shifts.','Per-mode residue comparison uses first20 isolated primary modes, fixedbridge and original calibration; additional observer poles and arbitrary bridge excitation are not made equivalent.','Absolute residue phases are evaluated at corresponding different natural poles; they do not repair pitch or delay.','Five-ms RMSenvelope metrics retain full signal levels; no peak/gain fitting.'],
  'partial_poles':poles_by_name,'models':rows}
 fit.write(OUT/'pole-aligned-diagnostics.json',result)
 print(json.dumps({'passed':True,'models':len(rows),'maximum_pole_residual':maximum_residual,'maximum_derivative_disagreement':maximum_derivative_disagreement,'report_sha256':sha(OUT/'pole-aligned-diagnostics.json')},indent=2))
if __name__=='__main__':main()
