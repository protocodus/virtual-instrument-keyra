#!/usr/bin/env python3
"""One private frozen TRAIN34 producer:28 fresh pairs,6 unchanged prior outcomes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse, ast, hashlib, importlib.util, json, resource, subprocess, time
import numpy as np
from scipy.io import wavfile
OUT=Path(__file__).resolve().parent; ROOT=Path('/workspace/virtual-instrument-keyra'); TOP=OUT.parent
ORIGINAL_OPERATOR=ROOT/'out/full-radiation-crossover/v1/postprocess.py'
OP_SHA='636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e'
FRAMES=182400

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text())
def write(p,value):
 p=Path(p)
 if p.exists() or OUT not in p.resolve().parents:raise ValueError('Fresh private output required: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def verify(records):
 for r in records:
  if record(r['path'])!=r:raise ValueError('Changed frozen input: '+r['path'])
def module():
 spec=importlib.util.spec_from_file_location('fixed400_exact',OUT/'compat400.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def plan():
 if (OUT/'producer-plan.json').exists():raise ValueError('Plan already frozen')
 manifest=read(OUT/'build-manifest.json');verify([manifest['binary'],*manifest['source_inputs']])
 inventory=read(OUT/'inventory.json');operator=record(ORIGINAL_OPERATOR);assert operator['sha256']==OP_SHA
 original=ast.parse(ORIGINAL_OPERATOR.read_text());extracted=ast.parse((OUT/'compat400.py').read_text())
 names=['coefficients','block','process','selftests'];checks={}
 for name in names:
  x=next(n for n in original.body if isinstance(n,ast.FunctionDef) and n.name==name);y=next(n for n in extracted.body if isinstance(n,ast.FunctionDef) and n.name==name)
  a=ast.get_source_segment(ORIGINAL_OPERATOR.read_text(),x);b=ast.get_source_segment((OUT/'compat400.py').read_text(),y)
  assert a==b;checks[name]=hashlib.sha256(a.encode()).hexdigest()
 tests=module().selftests();tests['fixed400_operator']=operator;tests['exact_function_source_sha256']=checks
 write(OUT/'postprocessor-synthetic-checks.json',tests)
 provenance=ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core'
 inputs=manifest['source_inputs']+[record(OUT/'run_batch.py'),record(OUT/'inventory.json'),record(OUT/'build-manifest.json'),record(OUT/'postprocessor-synthetic-checks.json'),operator,*[record(p) for p in sorted(provenance.rglob('*')) if p.is_file()]]
 seen=set();inputs=[r for r in inputs if not(r['path'] in seen or seen.add(r['path']))]
 cases=[{'id':r['id'],'midi':r['midi'],'velocity':r['velocity'],'frames':r['frames'],'baseline_cache':r['baseline_cache'],'expected_outputs':r['proposed_outputs']} for r in inventory['cases'] if not r['reused_existing_six']]
 value={'prepared_at_utc':now(),'source_inputs':inputs,'binary':manifest['binary'],'configuration':manifest['configuration'],'inventory':record(OUT/'inventory.json'),'fixed400_operator':operator,'cases':cases,'reused_frozen_six':[{k:r[k] for k in ['id','midi','velocity','frames','reuse_source']} for r in inventory['cases'] if r['reused_existing_six']], 'observer_header_sha256':sha(OUT/'CausalRadiation.h'),'math_validation':manifest['math_validation'],'postprocessor_synthetic_checks':record(OUT/'postprocessor-synthetic-checks.json'),'max_parallel_processes':2,'budget':{'free_disk_bytes_at_plan':__import__('shutil').disk_usage(OUT).free,'reserve_bytes':2*1024**3,'new_rendered_audio_seconds':106.4,'estimated_CPU_seconds':900,'estimated_wall_seconds':600,'not_a_realtime_benchmark':True},'scope':'No-stem readonly observer on exact historical original mechanics; six previous400Hz outcomes reused unchanged;28 new confirmation pairs. No real recording PCM opened by producer; no gain/onset/gate/cutoff search.'}
 assert len(cases)==28 and len(value['reused_frozen_six'])==6
 write(OUT/'producer-plan.json',value);print(json.dumps(record(OUT/'producer-plan.json')))

def frozen():
 p=read(OUT/'producer-plan.json');f=read(OUT/'candidate-freeze.json');protocol=record(TOP/'protocol.json')
 if f['protocol']!=protocol or f['producer_plan']!=record(OUT/'producer-plan.json'):raise ValueError('Protocol/plan freeze mismatch')
 for key in ['source_inputs','binary','configuration','fixed400_operator']:
  if p[key]!=f[key]:raise ValueError('Plan/freeze differs: '+key)
 verify([p['binary'],*p['source_inputs'],f['protocol'],f['producer_plan']]);return p,f

def freeze():
 p=read(OUT/'producer-plan.json');verify([p['binary'],*p['source_inputs']]);protocol=read(TOP/'protocol.json');protocol_freeze=read(TOP/'protocol-freeze.json')
 assert protocol['producer_contract']['producer_plan']==record(OUT/'producer-plan.json')
 assert protocol_freeze['protocol']==record(TOP/'protocol.json')
 value={k:p[k] for k in ['source_inputs','binary','configuration','fixed400_operator']};value.update({'frozen_at_utc':now(),'protocol':record(TOP/'protocol.json'),'producer_plan':record(OUT/'producer-plan.json'),'protocol_freeze':record(TOP/'protocol-freeze.json')})
 write(OUT/'candidate-freeze.json',value);print(json.dumps(record(OUT/'candidate-freeze.json')))

def render(case,p,f):
 frozen();folder=Path(case['expected_outputs']['folder']);folder.mkdir(parents=True,exist_ok=False);command=[p['binary']['path'],str(folder),str(case['midi']),str(case['velocity'])];started=now();call=subprocess.run(command,text=True,capture_output=True)
 (folder/'render.stdout.json').write_text(call.stdout);(folder/'render.stderr.txt').write_text(call.stderr)
 if call.returncode:raise RuntimeError(case['id']+' producer failed exit '+str(call.returncode))
 info=json.loads(call.stdout)
 if (info['midi'],info['velocity'],info['frames'],info['sample_rate'],info['note_on_frame'])!=(case['midi'],case['velocity'],FRAMES,48000,4800):raise ValueError('Producer request mismatch')
 baseline=np.fromfile(folder/'baseline.f32le','<f4').reshape(-1,2);causal=np.fromfile(folder/'candidate.f32le','<f4').reshape(-1,2)
 if baseline.shape!=(FRAMES,2) or causal.shape!=baseline.shape or not np.isfinite(baseline).all() or not np.isfinite(causal).all():raise ValueError('Invalid producer PCM')
 verify([{k:v for k,v in case['baseline_cache'].items() if k!='float32_payload_sha256'}]);rate,cached=wavfile.read(case['baseline_cache']['path']);baseline_exact=rate==48000 and cached.dtype==np.float32 and cached.shape==baseline.shape and cached.tobytes()==baseline.tobytes()
 if not baseline_exact:raise ValueError('Historical baseline bytes differ: '+case['id'])
 states=np.fromfile(folder/'state-proof.u64le','<u8').reshape(-1,3);forces=np.fromfile(folder/'force-proof.u64le','<u8').reshape(-1,3);schedule=np.r_[np.arange(0,FRAMES,256),FRAMES-1].astype(np.uint64)
 if states.shape!=(714,3) or forces.shape!=(FRAMES,3) or not np.array_equal(states[:,0],schedule) or not np.array_equal(forces[:,0],np.arange(FRAMES,dtype=np.uint64)):raise ValueError('Incomplete parity proof')
 sp=bool(np.array_equal(states[:,1],states[:,2]));fp=bool(np.array_equal(forces[:,1],forces[:,2]));faults=int(info['original_fault_flags'])|int(info['new_observer_faults'])
 if not sp or not fp or info['parity_mismatches'] or faults:raise ValueError('Physical/force/fault proof failed')
 op=module();candidate,final=op.process(baseline,causal,[64]);alternate,alternate_final=op.process(baseline,causal,[1,3,17,64,129,7]);partition=candidate.tobytes()==alternate.tobytes() and final.tobytes()==alternate_final.tobytes();finite=bool(np.isfinite(candidate).all() and np.isfinite(final).all());out=candidate.astype('<f4');finite=finite and bool(np.isfinite(out).all())
 if not partition or not finite:raise ValueError('Fixed400 output/partition/finiteness failed')
 for name,array in [('baseline',baseline),('causal',causal),('candidate',out)]:wavfile.write(case['expected_outputs'][name],48000,array)
 row={'id':case['id'],'midi':case['midi'],'velocity':case['velocity'],'frames':FRAMES,'baseline':record(case['expected_outputs']['baseline']),'causal':record(case['expected_outputs']['causal']),'candidate':record(case['expected_outputs']['candidate']),'mechanical_state_bit_parity':sp,'force_bit_parity':fp,'mechanical_state_force_bit_parity':sp and fp,'new_faults':faults,'diagnostics':info,'render_started_at_utc':started,'render_finished_at_utc':now(),'command':command,'baseline_float32_payload_identical_to_cached_control':baseline_exact,'cached_control':case['baseline_cache'],'float32_payload_sha256':{name:hashlib.sha256(array.tobytes()).hexdigest() for name,array in [('baseline',baseline),('causal',causal),('candidate',out)]},'parity_proof':{'state_rows':record(folder/'state-proof.u64le'),'force_rows':record(folder/'force-proof.u64le'),'state_checkpoints':714,'force_frames':FRAMES,'scope':'One physical trajectory before/after readonly observer; sampled q/p/damp/board/hammer/pedal/counters and every-frame88contact+3Schur force FNV1a64. No cryptographic collision guarantee; not all internal fields.'},'postprocessor_contract':{'fixed400_operator':p['fixed400_operator'],'canonical_partition':[64],'alternate_partitions':[1,3,17,64,129,7],'partitions_byte_identical':partition,'finite_output_and_final_state':finite,'final_LP_state':final.tolist(),'sample_peak':float(np.max(abs(out))),'cutoff_hz':400,'gain_or_retiming_applied':False}}
 write(folder/'case-receipt.json',row);frozen();print(case['id'],'baseline exact; state/force/fault/partition checks PASS',flush=True);return row

def run():
 p,f=frozen()
 if (OUT/'render-started.json').exists():raise ValueError('One batch already started; no silent restart')
 started=now();wall=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN);write(OUT/'render-started.json',{'render_started_at_utc':started,'candidate_freeze':record(OUT/'candidate-freeze.json'),'max_parallel_processes':2,'new_cases':28,'existing_six_rerendered_or_reprocessed':False})
 results=[];failures=[]
 with ThreadPoolExecutor(max_workers=2) as pool:
  pending={pool.submit(render,c,p,f):c['id'] for c in p['cases']}
  for future in as_completed(pending):
   try:results.append(future.result())
   except Exception as error:
    failure={'id':pending[future],'failed_at_utc':now(),'error_type':type(error).__name__,'error':str(error),'retried':False};write(OUT/'failures'/(pending[future]+'.json'),failure);failures.append(failure);print('FAILURE',failure,flush=True)
 frozen();results.sort(key=lambda r:[c['id'] for c in p['cases']].index(r['id']));endcpu=resource.getrusage(resource.RUSAGE_CHILDREN)
 value={k:p[k] for k in ['source_inputs','binary','configuration','fixed400_operator']};value.update({'protocol':f['protocol'],'producer_plan':f['producer_plan'],'candidate_freeze':record(OUT/'candidate-freeze.json'),'render_started_at_utc':started,'render_finished_at_utc':now(),'cases':results,'failures':failures,'passed':not failures and len(results)==28,'reused_frozen_six':[c['id'] for c in p['reused_frozen_six']],'reused_six_rerendered_reprocessed_or_rescored':False,'wall_seconds_diagnostic':time.monotonic()-wall,'children_cpu_seconds_diagnostic':endcpu.ru_utime+endcpu.ru_stime-cpu.ru_utime-cpu.ru_stime,'not_a_CPU_benchmark':True})
 write(OUT/'producer-receipt.json',value);write(OUT/'capture.json',{'protocol':f['protocol'],'producer_receipt':record(OUT/'producer-receipt.json'),'cases':results});print('producer',record(OUT/'producer-receipt.json'),'capture',record(OUT/'capture.json'),flush=True)
 if failures:raise SystemExit(1)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--phase',required=True,choices=['plan','freeze','run']);args=parser.parse_args();globals()[args.phase]()
