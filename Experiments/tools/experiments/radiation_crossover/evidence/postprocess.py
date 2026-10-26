#!/usr/bin/env python3
"""One frozen400Hz TRAIN-reuse compatibility experiment; private only.
No source DSP rendering, fitting, retiming, reference recalculation or promotion.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,io,json,math,sys,textwrap
import numpy as np
from scipy.io import wavfile
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent
RATE=48000;CUTOFF=400.;IDS=('C3v4','C3v12','C4v4','C4v12','C6v4','C6v12')
METRIC_SHA='14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd'
OLD_PROTOCOL_SHA='5ec7ace5cffb6655fb017430d328dc784762beb9ff5460eb5c63a07e606b96fa'
REFERENCE_SHA='4675d46574d65063d63ce9266ef4caa3d30c4880e4fac6fbabd11e6ff9747faf'

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def record(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,value):Path(p).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def coefficients():
 k=math.tan(math.pi*CUTOFF/RATE);return (1-k)/(1+k),k/(1+k)

def block(old,new,state):
 old=np.asarray(old,dtype=np.float64);new=np.asarray(new,dtype=np.float64)
 if old.shape!=new.shape or old.ndim!=2 or old.shape[1]!=2 or state.shape!=(2,):raise ValueError('Invalid stereo/state shape')
 if not np.isfinite(old).all() or not np.isfinite(new).all() or not np.isfinite(state).all():raise ValueError('Nonfinite input/state')
 a,b=coefficients();out=np.empty_like(new)
 for i in range(len(new)):
  for ch in range(2):
   delta=old[i,ch]-new[i,ch];bd=b*delta;correction=bd+state[ch];state[ch]=bd+a*correction
   # A zero correction preserves same-input sample bits, including signedzero.
   out[i,ch]=new[i,ch]+correction if correction!=0. else new[i,ch]
 if not np.isfinite(out).all() or not np.isfinite(state).all():raise ValueError('Nonfinite postprocessor output/state')
 return out

def process(old,new,partitions):
 if not partitions or any(n<1 for n in partitions):raise ValueError('Invalid partitions')
 state=np.zeros(2,dtype=np.float64);result=np.empty(np.asarray(new).shape,dtype=np.float64);frame=0;index=0
 while frame<len(new):
  end=min(len(new),frame+partitions[index%len(partitions)]);result[frame:end]=block(old[frame:end],new[frame:end],state);frame=end;index+=1
 return result,state

def selftests():
 a,b=coefficients();assert 0<a<1 and abs(2*b/(1-a)-1)<1e-14
 rng=np.random.default_rng(4002026);old=rng.normal(size=(4096,2));new=rng.normal(size=(4096,2))
 baseline,s1=process(old,new,[64]);partitioned,s2=process(old,new,[1,3,17,64,129,7]);assert baseline.tobytes()==partitioned.tobytes() and s1.tobytes()==s2.tobytes()
 identical=old.astype(np.float32);identical[0]=[-0.,0.];same,zero=process(identical,identical,[1,7,64]);assert same.astype('<f4').tobytes()==identical.astype('<f4').tobytes() and np.array_equal(zero,[0.,0.])
 dc,dcstate=process(np.ones((4096,2)),np.zeros((4096,2)),[64]);assert np.max(abs(dc[-1]-1))<1e-13
 # Independent analytic impulse kernel, not a second recurrence implementation.
 impulse=np.zeros((512,2));impulse[0]=1;observed,_=process(impulse,np.zeros_like(impulse),[3,7,1]);kernel=np.r_[b,b*(1+a)*a**np.arange(511)];err=float(np.max(abs(observed-kernel[:,None])));assert err<1e-14
 rejected=0
 for value in [np.nan,np.inf,-np.inf]:
  bad=np.zeros((3,2));bad[1,0]=value
  try:process(bad,np.zeros_like(bad),[1])
  except ValueError:rejected+=1
 assert rejected==3
 return {'passed':True,'pole':a,'b0_b1':b,'DC_gain':2*b/(1-a),'Nyquist_gain':0.,'zero_difference_bit_identity':True,'partition_byte_identity':True,
 'canonical_partition':[64],'alternate_partitions':[1,3,17,64,129,7],'analytic_impulse_max_absolute_error':err,'nonfinite_inputs_rejected':rejected,
 'scope':'Synthetic data only. One fixed coefficient set; no pilot PCM opened.'}

def frozen():
 f=read(OUT/'freeze.json');assert f['postprocessor_source']['sha256']==sha(__file__) and f['protocol']['sha256']==sha(OUT/'protocol.json')
 p=read(OUT/'protocol.json');assert p['cutoff_hz']==CUTOFF and p['sample_rate']==RATE and tuple(x['id'] for x in p['cases'])==IDS
 return p,f

def load_snapshot(row):
 path=Path(row['path']);data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if digest!=row['sha256']:raise ValueError('Input SHA changed:'+str(path))
 sr,x=wavfile.read(io.BytesIO(data))
 if sr!=RATE or x.dtype.kind!='f' or x.dtype.itemsize!=4 or x.shape!=(182400,2) or not np.isfinite(x).all():raise ValueError('Invalid frozen pilot audio:'+str(path))
 return x,{'path':str(path),'sha256':digest,'float32_payload_sha256':hashlib.sha256(np.asarray(x,dtype='<f4').tobytes()).hexdigest()}

def gate_function(metric,metric_source):
 # Execute the EXACT original evaluate() gate-arithmetic block. No copied
 # thresholds or reinterpretation of the original scorer are introduced.
 start="        base=old['baseline'];floor=old['reference']['sustain_power']*1e-10\n";end='        optional=None\n'
 if metric_source.count(start)!=1:raise ValueError('Nonunique original gate start')
 begin=metric_source.index(start);finish=metric_source.index(end,begin);body=textwrap.dedent(metric_source[begin:finish])
 tail="return {'changes':{'first5_positive_excess_reduction_db':first_b-first_c,'ring5_20_positive_excess_reduction_db':ring_b-ring_c,'late_harmonic_MAE_db':harmonic,'late_envelope_MAE_db':envelope,'late_RMS_db':drift,'early_window_band_MAE_db':window_changes,'stereo':shifts},'gates':gates,'passes_all_case_gates':all(gates.values())}\n"
 source='def original_gates(old,candidate,ident,baseline_exact,proof):\n'+textwrap.indent(body+tail,'    ');space={'math':math,'power_db':metric.power_db};exec(compile(source,'frozen-original-gate-block','exec'),space)
 return space['original_gates'],hashlib.sha256(body.encode()).hexdigest()

def run():
 p,freeze=frozen()
 if (OUT/'opening-started.json').exists() or (OUT/'result.json').exists():raise ValueError('One run already started: inspect existing artifacts; no silent rerun/rescore')
 write(OUT/'opening-started.json',{'started_at_utc':now(),'freeze':record(OUT/'freeze.json'),'candidate_PCM_opened_before_this_marker':False,
 'scope':'ThisexperimenthasnotopenedpilotcandidatePCM. Previouscausalpilotresultswereobserved andmotivatedthisposthocTRAINreuse.'})
 checks=selftests();write(OUT/'postprocessor-checks.json',checks)
 metric_path=Path(p['original_metric_tool']['path']);metric_bytes=metric_path.read_bytes();assert hashlib.sha256(metric_bytes).hexdigest()==METRIC_SHA
 assert sha(p['reference_control']['path'])==REFERENCE_SHA and sha(p['original_protocol']['path'])==OLD_PROTOCOL_SHA
 spec=importlib.util.spec_from_file_location('frozen_causal_metrics',metric_path);metric=importlib.util.module_from_spec(spec);spec.loader.exec_module(metric)
 original_protocol,rows=metric.locked();reference=read(p['reference_control']['path']);references={x['id']:x for x in reference['cases']}
 assert original_protocol['gates']==p['unchanged_original_gates']
 gate,gate_sha=gate_function(metric,metric_bytes.decode())
 capture_record=p['upstream_capture'];producer_record=p['upstream_producer'];metric.verify([capture_record,producer_record]);capture=read(capture_record['path']);producer=read(producer_record['path'])
 proof,producer_sources=metric.producer_evidence(producer,original_protocol,capture);results=[]
 for case in p['cases']:
  ident=case['id'];old=references[ident]
  assert old['baseline']['fixed_gain']==case['fixed_old_gain'] and old['baseline']['fixed_onset_frame']==case['fixed_old_onset_frame']
  baseline,bid=load_snapshot(case['old_audio']);causal,cid=load_snapshot(case['causal_audio']);cached,kid=load_snapshot(case['cached_control_audio']);baseline_exact=baseline.tobytes()==cached.tobytes()
  output,state=process(baseline,causal,[64]);alternate,altstate=process(baseline,causal,[1,3,17,64,129,7]);partition_exact=output.tobytes()==alternate.tobytes() and state.tobytes()==altstate.tobytes()
  if not partition_exact:raise ValueError('Actual input chunk partition changed output:'+ident)
  output32=output.astype('<f4');assert np.isfinite(output32).all()
  destination=OUT/ident;destination.mkdir(exist_ok=False);audio=destination/'compatibility.wav';wavfile.write(audio,RATE,output32)
  # Score exactly the emitted float32 payload with the OLD fixed gain/onset.
  features=metric.observation_features(output32.astype(np.float64),case['fixed_old_onset_frame'],case['fixed_old_gain'],old['reference'],rows[ident])
  scored=gate(old,features,ident,baseline_exact,proof)
  row={'id':ident,'old_audio':bid,'causal_audio':cid,'cached_control_audio':kid,'output_audio':record(audio),'output_float32_payload_sha256':hashlib.sha256(output32.tobytes()).hexdigest(),
   'postprocessor_contract':{'partitions_byte_identical':True,'finite_output_and_final_state':True,'final_LP_state':state.tolist(),'sample_peak':float(np.max(abs(output32)))},
   'upstream_state_force_lineage':{'producer_case':ident,'mechanical_state_bit_parity':proof[ident]['mechanical_state_bit_parity'],'force_bit_parity':proof[ident]['force_bit_parity'],'new_faults':proof[ident]['new_faults'],'scope':'Inherited sourcepairproof only; no mechanicaltrajectorywasrerendered or modifiedbythispostprocessor.'},
   'candidate':features,**scored};results.append(row);write(destination/'result.json',row)
  print(ident,'PASS' if row['passes_all_case_gates'] else 'FAIL',row['gates'],flush=True)
 metric.locked();metric.verify([p['upstream_capture'],p['upstream_producer'],*producer_sources])
 for case in p['cases']:metric.verify([case['old_audio'],case['causal_audio'],case['cached_control_audio']])
 frozen()
 result={'schema_version':1,'completed_at_utc':now(),'status':'ONEprivatefixed400HzTRAINcompatibilityexperiment_completed','protocol':record(OUT/'protocol.json'),'freeze':record(OUT/'freeze.json'),'opening':record(OUT/'opening-started.json'),
  'original_metric_tool':p['original_metric_tool'],'exact_original_gate_arithmetic_block_sha256':gate_sha,'reference_control':p['reference_control'],'upstream_capture':p['upstream_capture'],'upstream_producer':p['upstream_producer'],
  'postprocessor_checks':record(OUT/'postprocessor-checks.json'),'cases':results,'passes_all_unchanged_pilot_gates':all(x['passes_all_case_gates'] for x in results),
  'physical_state_force_proof':'Inherited from unchangedauthenticatedold/causalinputpairs; postprocessingproducesnogeneralizedforcesandupdatesnomechanicalstate. Not anewDSPkernelparityrun.',
  'full_DSP_renders':0,'candidate_cutoff_variants':1,'gain_or_onset_changes':False,'gate_changes':False,'rescore_after_failure':False,'recording_fit_or_acquisition':False,
  'TRAIN_reuse':'Posthoccompatibilitycandidate motivatedbyfailedC6LFcausalpilot; these sixTRAINcasesandtheirpriorresultswerealreadyobserved. No freshvalidation/generalizationclaim.',
  'default_promoted':False,'published':False,'limits':['Engineeringobservercrossover,notphysicalpianopart/materialmodel orLFsourceidentification.','ComplementaryfiltersretainoldLFprojectionandnewHFobserver; transitionphase/cancellationcanstillregress.','Apositiveexcessreductionmetriccanrewardoverattenuation; allsignederrorsretained.','NoactualSDK/Reasonhost/realtimeorextendedTRAIN34qualification.']}
 write(OUT/'result.json',result);print('ALL UNCHANGED GATES',result['passes_all_unchanged_pilot_gates'],flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--selftest',action='store_true');parser.add_argument('--run',action='store_true');args=parser.parse_args()
 if args.selftest:print(json.dumps(selftests(),indent=2))
 elif args.run:
  try:run()
  except Exception as error:
   write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(error).__name__,'message':str(error),'no_silent_restart':True});raise
 else:raise SystemExit('Select --selftest or --run; one frozen processingrun only')
