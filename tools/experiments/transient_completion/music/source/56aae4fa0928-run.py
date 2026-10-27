#!/usr/bin/env python3
"""ONE authorized fixed 9s source/shadow diagnostic; never export listening audio."""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,subprocess,time
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def record(p):return {'path':str(Path(p).resolve()),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def verify(row):
 p=Path(row['path'])
 if sha(p)!=row['sha256'] or ('bytes' in row and p.stat().st_size!=row['bytes']):raise ValueError('Changed frozen file: '+str(p))
def check_authorization(path,action):
 auth=read(path);protocol=read(OUT/'protocol.json')
 if auth['protocol_sha256']!=sha(OUT/'protocol.json') or action not in auth['actions']:raise ValueError('Root authorization/protocol mismatch')
 for row in protocol['bindings']:verify(row)
 return auth,protocol

def process_filter(library,old,fast,blocks):
 fn=library.keyra_protect_counter;ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
 fn.argtypes=[ptr,ptr,ptr,ctypes.c_size_t,ptr];fn.restype=ctypes.c_int
 old=np.ascontiguousarray(old,dtype=np.float64);fast=np.ascontiguousarray(fast,dtype=np.float64)
 result=np.empty((len(old),10),np.float64);state=np.zeros(16,np.float64);cursor=step=0
 while cursor<len(old):
  size=min(blocks[step%len(blocks)],len(old)-cursor)
  if fn(old[cursor:cursor+size],fast[cursor:cursor+size],result[cursor:cursor+size],size,state):raise ValueError('Nonfinite filter')
  cursor+=size;step+=1
 return result,state

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--authorization',required=True);args=parser.parse_args()
 auth,protocol=check_authorization(args.authorization,'render')
 verify(auth['confirmation_result']);confirmation=read(auth['confirmation_result']['path'])
 if confirmation['protocol']!=protocol['confirmation_protocol']:raise ValueError('Wrong confirmation family')
 assert confirmation['case_count']==confirmation['cases_passing_all_original_gates']==34 and confirmation['passes_all_original_gates']
 assert len(confirmation['cases'])==34 and all(c['passes_all_case_gates'] and all(c['numeric_guards'].values()) for c in confirmation['cases'])
 cold=read(protocol['cold_field']['path'])
 if confirmation['cold_bound_gamma']!=cold:raise ValueError('Confirmation rho field differs')
 destination=OUT/'render';build=OUT/'build'
 if destination.exists() or build.exists():raise ValueError('Attempt already exists; preserve it, no silent retry')
 destination.mkdir();build.mkdir();write(destination/'opening-started.json',{'at_utc':now(),'protocol':record(OUT/'protocol.json'),'authorization':record(args.authorization),'confirmation':auth['confirmation_result']})
 expected=np.array([m['rho'] for s in cold['string_fields'] for m in s['modes']]+[m['rho'] for m in cold['board_fields']],dtype='<f8')
 assert expected.shape==(18253,) and np.isfinite(expected).all() and np.all((expected>0)&(expected<1));expected.tofile(destination/'expected-rhos.f64le')
 flags=protocol['build_flags'];commands=[]
 for name,path in [('api',OUT/'sources/src/full_instrument/FullInstrument.cpp'),('music',OUT/'music.cpp'),('filter',OUT/'filter.cpp')]:
  cmd=['g++',*flags,'-c',str(path),'-o',str(build/(name+'.o'))];subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['g++',str(build/'api.o'),str(build/'music.o'),str(build/'filter.o'),'-o',str(build/'producer')];subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['g++',*flags,'-shared','-fPIC',str(OUT/'filter.cpp'),'-o',str(build/'filter.so')];subprocess.run(cmd,check=True);commands.append(cmd)
 write(destination/'producer-freeze.json',{'at_utc':now(),'protocol':record(OUT/'protocol.json'),'commands':commands,'binary':record(build/'producer'),'filter_binary':record(build/'filter.so'),'expected_rhos':record(destination/'expected-rhos.f64le')})
 started=time.monotonic();call=subprocess.run([str(build/'producer'),str(destination),protocol['score']['path'],str(destination/'expected-rhos.f64le')],capture_output=True,text=True,timeout=420)
 (destination/'producer.stdout').write_text(call.stdout);(destination/'producer.stderr').write_text(call.stderr)
 if call.returncode:raise ValueError('Producer failed '+str(call.returncode)+'; retained artifacts')
 info=json.loads(call.stdout);companion=read(destination/'companion.json')
 assert info['frames']==432000 and info['events_applied']==24 and info['launches']==info['requests']==11
 assert info['original_fault_flags']==info['parity_mismatches']==info['new_observer_faults']==0
 baseline=np.fromfile(destination/'baseline.f32le','<f4').reshape(-1,2);candidate=np.fromfile(destination/'candidate.f32le','<f4').reshape(-1,2)
 old_filtered=np.fromfile(destination/'filter-baseline.f32le','<f4').reshape(-1,2)
 assert baseline.shape==candidate.shape==old_filtered.shape==(432000,2) and np.isfinite(candidate).all()
 assert sha(destination/'baseline.f32le')==protocol['expected_baseline_f32_sha256'] and baseline.tobytes()==old_filtered.tobytes()
 assert sha(destination/'prepared-rhos.f64le')==sha(destination/'expected-rhos.f64le')
 pressure=np.memmap(destination/'pressure.f64le','<f8',mode='r',shape=(432000,6))
 assert np.isfinite(pressure).all() and np.array_equal(pressure[:,:2].view('<u8'),pressure[:,4:6].view('<u8'))
 state=np.fromfile(destination/'state-proof.u64le','<u8').reshape(-1,3);forceproof=np.fromfile(destination/'force-proof.u64le','<u8').reshape(-1,3)
 assert state.shape==(1689,3) and np.array_equal(state[:,0],np.r_[np.arange(0,432000,256),431999]) and np.array_equal(state[:,1],state[:,2])
 assert forceproof.shape==(432000,3) and np.array_equal(forceproof[:,0],np.arange(432000)) and np.array_equal(forceproof[:,1],forceproof[:,2])
 forces=np.memmap(destination/'forces-and-bridge.f64le','<f8',mode='r',shape=(432000,91));branches=np.memmap(destination/'active-branches.u8','u1',mode='r',shape=(432000,88))
 assert np.isfinite(forces).all() and np.all(forces[:,:88]>=0) and np.all((branches==0)|(branches==1)) and not np.any((branches==0)&(forces[:,:88]!=0))
 for key in ['unity_raw_nonidentical_samples','unity_coordinate_mismatch_checkpoints','input_errors','fast_faults','unity_faults']:assert companion[key]==0
 assert companion['unity_steps']==432000 and companion['max_positive_scale_energy']<=0 and companion['max_free_energy_ratio']<=1 and companion['max_zero_input_pressure_over_bound']<=1
 assert companion['memory_law']=='pitch-and-modal-frequency' and companion['K_LR']==cold['K_LR']
 library=ctypes.CDLL(str(build/'filter.so'));canonical,canonicalstate=process_filter(library,pressure[:,:2],pressure[:,2:4],[64]);partitioned,partitionstate=process_filter(library,pressure[:,:2],pressure[:,2:4],[1,3,17,64,129,7])
 assert canonical.tobytes()==partitioned.tobytes() and canonicalstate.tobytes()==partitionstate.tobytes()
 assert canonical[:,2:4].astype('<f4').tobytes()==baseline.tobytes() and canonical[:,4:6].astype('<f4').tobytes()==candidate.tobytes()
 for row in protocol['bindings']:verify(row)
 receipt={'passed':True,'at_utc':now(),'protocol':record(OUT/'protocol.json'),'authorization':record(args.authorization),'confirmation':auth['confirmation_result'],'producer':info,'companion':companion,'wall_seconds_render_and_checks':time.monotonic()-started,'full9s_baseline_f32_bitexact':True,'full9s_rho1_raw_and_checkpoint_bitexact':True,'prepared_field_bitexact_before_first_musical_frame':True,'primary_before_after_state_and_force_hashes_equal':True,'filter_partitions_output_and_final_state_bitexact':True,'source_force_rows':432000,'state_checkpoints':1689,'outputs':[record(p) for p in sorted(destination.iterdir()) if p.is_file()],'limitations':protocol['limitations']}
 write(destination/'receipt.json',receipt);print(json.dumps({'receipt':record(destination/'receipt.json'),'passed':True,'diagnostic_cpu':info['process_cpu_seconds_diagnostic']},indent=2))
if __name__=='__main__':main()
