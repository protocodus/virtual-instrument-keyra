#!/usr/bin/env python3
"""Read-only independent source/output checks; never construct/step a piano or export audio."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,hashlib,re,datetime,math,subprocess,ctypes
import numpy as np
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=ROOT/'out/full-transient-music/v4';D=OUT/'render';A=ROOT/'out/full-transient-music-audit/v4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def rec(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def verify(x):
 p=Path(x['path']);assert sha(p)==x['sha256'],p
 if 'bytes' in x:assert p.stat().st_size==x['bytes'],p
p=read(OUT/'protocol.json');receipt=read(D/'receipt.json');verify(receipt['protocol']);verify(receipt['authorization']);verify(receipt['confirmation'])
for x in p['bindings']+receipt['outputs']:verify(x)
assert receipt['passed'] and receipt['musical_numeric_and_parity_only'] and not receipt['recording_global_acceptance']
assert receipt['recording_cases_passed']==33 and receipt['recording_cases_total']==34 and receipt['failed_recording_cases']==['C8v12']
assert not (OUT.parent/'v3/render').exists()
# Independently apply reversible identifier-only transform, preserving literals/comments.
pattern=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[A-Za-z_]\w*')
namespace_checks=[]
for name in ['PreparedModel.h','PreparedCalibration.h']:
 original=ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument'/name
 text=original.read_text();mapping={'grand':'pitch_shadow','piano_calibration':'pitch_shadow_calibration'}
 transformed=pattern.sub(lambda m:mapping.get(m.group(),m.group()),text)
 target=OUT/'shadow'/name
 assert transformed.encode()==target.read_bytes()
 assert not any(x in target.read_text() for x in ['causal_trace','causal_capture','Capture.h','Trace.h'])
 namespace_checks.append({'original':rec(original),'shadow':rec(target),'generated_bytes_match':True})
primary=OUT/'sources/src/full_instrument/PreparedModel.h';normalized=primary.read_text()
for line in ['#include "Trace.h"\n','    causal_trace::force={};\n','      causal_trace::activeBefore[size_t(&k-keys.data())]=k.hammerActive?1:0;\n','        causal_trace::force[size_t(&k-keys.data())]=F;\n','    causal_trace::bridge={};\n','    causal_trace::bridge=total;\n']:
 assert normalized.count(line)==1,line
 normalized=normalized.replace(line,'')
assert normalized.encode()==(ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument/PreparedModel.h').read_bytes()
prep=read(OUT/'diagnostic-preparation.json')
for row in prep['dsp_and_event_driver_byteexact_to_v3']:
 verify(row);q=Path(row['path']);relative=q.relative_to(OUT);assert q.read_bytes()==(OUT.parent/'v3'/relative).read_bytes()
# Frozen modal rho field itself is the source of truth, not a new coefficient render.
cold=read(Path(p['cold_field']['path']));expected=np.array([x['rho'] for s in cold['string_fields'] for x in s['modes']]+[x['rho'] for x in cold['board_fields']],dtype='<f8')
assert expected.shape==(18253,) and expected.tobytes()==(D/'expected-rhos.f64le').read_bytes()==(D/'prepared-rhos.f64le').read_bytes()
baseline=np.fromfile(D/'baseline.f32le','<f4').reshape(432000,2);candidate=np.fromfile(D/'candidate.f32le','<f4').reshape(432000,2)
assert sha(D/'baseline.f32le')==p['expected_baseline_f32_sha256'] and baseline.tobytes()==(D/'filter-baseline.f32le').read_bytes()
pressure=np.memmap(D/'pressure.f64le','<f8',mode='r',shape=(432000,6))
assert np.isfinite(pressure).all() and np.isfinite(baseline).all() and np.isfinite(candidate).all()
assert pressure[:,:2].copy().tobytes()==pressure[:,4:6].copy().tobytes()
state=np.fromfile(D/'state-proof.u64le','<u8').reshape(-1,3);assert state.shape==(1689,3)
assert np.array_equal(state[:,0],np.r_[np.arange(0,432000,256),431999]) and np.array_equal(state[:,1],state[:,2])
forces=np.memmap(D/'forces-and-bridge.f64le','<f8',mode='r',shape=(432000,91));branches=np.memmap(D/'active-branches.u8','u1',mode='r',shape=(432000,88))
assert np.all((branches==0)|(branches==1)) and not np.any((branches==0)&(forces[:,:88]!=0))
# Dedicated read-only checker recomputes every actual force+bridge FNV row.
cmd=['g++','-std=c++17','-O3',str(A/'force-check.cpp'),'-o',str(A/'force-check')];subprocess.run(cmd,check=True)
force_check=json.loads(subprocess.check_output([str(A/'force-check'),str(D/'forces-and-bridge.f64le'),str(D/'force-proof.u64le')],text=True))
assert force_check['rows']==432000 and force_check['hash_mismatches']==force_check['row_mismatches']==force_check['invalid_forces']==0
companion=read(D/'companion.json')
for key in ['unity_raw_nonidentical_samples','unity_coordinate_mismatch_checkpoints','input_errors','fast_faults','unity_faults']:assert companion[key]==0
assert companion['unity_steps']==432000 and companion['max_positive_scale_energy']<=0 and companion['max_free_energy_ratio']<=1 and companion['max_zero_input_pressure_over_bound']<=1 and companion['K_LR']==cold['K_LR']
# Recompute fixed HP200/HP24 independently with Python float arithmetic; no piano or gain fit.
k=math.tan(math.pi*200/48000);a=(1-k)/(1+k);b=1/(1+k);pole=math.exp(-2*math.pi*24/48000)
manual_old=np.empty((432000,2));manual_new=np.empty((432000,2))
for ch in range(2):
 hp=previous_fast=old_hp=old_previous=new_hp=new_previous=0.
 for n in range(432000):
  x=float(pressure[n,ch]);z=float(pressure[n,2+ch]);hp=a*hp+b*(z-previous_fast);previous_fast=z;y=x-hp
  old_hp=pole*(old_hp+x-old_previous);old_previous=x;new_hp=pole*(new_hp+y-new_previous);new_previous=y
  manual_old[n,ch]=old_hp;manual_new[n,ch]=new_hp
assert manual_old.astype('<f4').tobytes()==baseline.tobytes() and manual_new.astype('<f4').tobytes()==candidate.tobytes()
# Independently exercise saved pure postprocessor library at two arbitrary partitions.
lib=ctypes.CDLL(str(OUT/'build/filter.so'));fn=lib.keyra_protect_counter;ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');fn.argtypes=[ptr,ptr,ptr,ctypes.c_size_t,ptr];fn.restype=ctypes.c_int
old=np.ascontiguousarray(pressure[:,:2]);fast=np.ascontiguousarray(pressure[:,2:4])
def process(blocks):
 result=np.empty((432000,10));s=np.zeros(16);offset=i=0
 while offset<432000:
  end=min(432000,offset+blocks[i%len(blocks)]);assert fn(old[offset:end],fast[offset:end],result[offset:end],end-offset,s)==0;offset=end;i+=1
 return result,s
u,us=process([64]);v,vs=process([1,3,17,64,129,7]);assert u.tobytes()==v.tobytes() and us.tobytes()==vs.tobytes()
assert u[:,2:4].astype('<f4').tobytes()==baseline.tobytes() and u[:,4:6].astype('<f4').tobytes()==candidate.tobytes()
assert np.array_equal(u[:,2:4],manual_old) and np.array_equal(u[:,4:6],manual_new)
assert p['presentation']['candidate_RMS_matching'] is False and p['presentation']['order']=='old9s,0.5szeros,new9s'
assert p['presentation']['fixed_shared_safety']==0.786203420103643 and p['presentation']['room_gain']==0.88993492917923 and p['presentation']['dry_gain']==0.9376616126301774
for row in p['bindings']+receipt['outputs']:verify(row)
result={'passed':True,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only independent source and existing-output audit. No model construction/steps, new recordings, audio export, listening verdict, gain fit or runtime changes.','protocol':rec(OUT/'protocol.json'),'render_receipt':rec(D/'receipt.json'),'frozen_bindings_checked':len(p['bindings']),'closed_output_records_checked':len(receipt['outputs']),'namespace_checks':namespace_checks,'primary_model_observation_hooks_only':True,'all_v4_DSP_driver_bytes_equal_strict_v3':True,'strict_v3_unrun':True,'modal_rho_values_bitexact':18253,'historical_baseline_f32_bitexact':True,'rho1_raw_stereo_samples_bitexact':864000,'rho1_coordinate_checkpoints_exact':1689,'all_actual_force_bridge_FNV_rows':force_check,'pre_post_primary_state_witnesses_equal':True,'inactive_branch_nonzero_force_rows':0,'manual_python_HP200_HP24_f32_exact':True,'manual_python_filter_double_exact':True,'streaming_filter_output_and_final_state_byteexact':True,'companion_energy_and_future_force_feedthrough_bound_guards_pass':True,'presentation_source_review_same_fixed_LR_gains_no_RMS_matching':True,'filter_final_state':us.tolist(),'global_recording_acceptance':False,'recording_pass_count':33,'recording_case_count':34,'failed_recording_cases':['C8v12'],'limitations':p['limitations']}
path=A/'independent-render-review.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'review':rec(path),'passed':True,'force_check':force_check},indent=2))
