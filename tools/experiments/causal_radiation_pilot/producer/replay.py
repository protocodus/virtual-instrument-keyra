#!/usr/bin/env python3
"""Compile/replay the frozen failed causal-radiation pilot without out-only source.

This launcher is portable orchestration; all DSP, instrumentation and original
model files remain byte-identical to the archived source index. It changes no
production target, default, calibration or reference recording.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[4]

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_sources():
 if digest(PACKAGE/'cases.json')!='9c2ad31818dd63c3aa4cbcf870ce76d70e4c1c9b21551514ec88c606b6576c3f':raise ValueError('Fixed portable case table changed')
 index=json.loads((PACKAGE/'source-index.json').read_text())
 for row in index['files']:
  path=ROOT/row['package_path']
  if digest(path)!=row['sha256']:raise ValueError('Frozen package input changed: '+str(path))
 if sum(row['candidate_freeze_source_input'] for row in index['files'])!=22:raise ValueError('Expected22 original producer inputs')
 return index

def run(command,log,stdout_json=False):
 call=subprocess.run(command,text=True,capture_output=True)
 Path(log).write_text(call.stdout if stdout_json else call.stdout+call.stderr)
 Path(str(log)+'.stderr').write_text(call.stderr)
 if call.returncode:raise RuntimeError(f'Command failed({call.returncode}): '+shlex.join(map(str,command))+'\n'+call.stderr[-3000:])
 return call.stdout

def build(output,cxx):
 output.mkdir(parents=True,exist_ok=True);original=PACKAGE/'original_core';actual=PACKAGE/'instrumented_core';observer=PACKAGE/'observer'
 common=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off'];steps=[]
 def compile_one(source,obj,includes):
  command=[*cxx,*common,*['-I'+str(p) for p in includes],'-c',str(source),'-o',str(output/obj)];run(command,output/(obj+'.log'));steps.append(command)
 compile_one(actual/'src/full_instrument/FullInstrument.cpp','producer-api.o',[actual/'include',actual/'src/full_instrument',observer])
 compile_one(PACKAGE/'frozen_driver/producer.cpp','producer-harness.o',[actual/'include',actual/'src/full_instrument',observer])
 command=[*cxx,str(output/'producer-api.o'),str(output/'producer-harness.o'),'-o',str(output/'producer')];run(command,output/'producer-link.log');steps.append(command)
 for name in ['math_probe','export_static']:
  shutil.copyfile(PACKAGE/'math_source'/(name+'.cpp'),output/(name+'.cpp'))
  command=[*cxx,*common,'-I'+str(original/'include'),'-I'+str(original/'src/full_instrument'),'-I'+str(observer),str(output/(name+'.cpp')),'-o',str(output/name)];run(command,output/(name+'-build.log'));steps.append(command)
 for name in ['frequency_analysis.py','validate_math.py']:shutil.copyfile(PACKAGE/'math_source'/name,output/name)
 # Frozen math scripts record these source-byte hashes in their own outputs.
 shutil.copyfile(observer/'CausalRadiation.h',output/'CausalRadiation.h')
 shutil.copyfile(PACKAGE/'evidence/static.json',output/'static.json')
 receipt={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':steps,'compiler':subprocess.check_output([*cxx,'--version'],text=True).splitlines()[0],'frozen_source_index_sha256':digest(PACKAGE/'source-index.json'),'binaries':{name:digest(output/name) for name in ['producer','math_probe','export_static']},'limits':'Fresh binaries/paths are new evidence; historical source bytes remain exact. Cross-compiler/architecture byte identity is not promised.'}
 (output/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def math(output):
 run([str(output/'export_static'),str(output)],output/'static-metadata.json',True)
 run([sys.executable,str(output/'frequency_analysis.py')],output/'frequency-analysis.log')
 run([str(output/'math_probe'),str(output)],output/'math-probe.json',True)
 run([sys.executable,str(output/'validate_math.py')],output/'validate-math.log')
 result=json.loads((output/'math-validation.json').read_text())
 if not result['passed']:raise RuntimeError('Observer math validation failed')
 return {'passed':True,'math_validation':{'path':str(output/'math-validation.json'),'sha256':digest(output/'math-validation.json')}}

def synth(output,selected,jobs):
 import numpy as np
 from scipy.io import wavfile
 controls=json.loads((PACKAGE/'cases.json').read_text())['cases']
 archived=json.loads((PACKAGE/'evidence/producer-receipt.json').read_text())['cases']
 expected={row['id']:(row['midi'],row['velocity'],row['frames']) for row in archived}
 if len(controls)!=6 or {row['id']:(row['midi'],row['velocity'],row['frames']) for row in controls}!=expected:raise ValueError('Fixed case table differs from indexed original producer receipt')
 allowed={row['id']:row for row in controls}
 if selected and any(name not in allowed for name in selected):raise ValueError('Choose only the six frozen case IDs')
 cases=[row for row in controls if not selected or row['id'] in selected]
 def render(case):
  folder=output/'cases'/case['id'];folder.mkdir(parents=True,exist_ok=False)
  command=[str(output/'producer'),str(folder),str(case['midi']),str(case['velocity'])];text=run(command,folder/'render.json',True);info=json.loads(text)
  fields={}
  for name in ['baseline','candidate','primary','secondary','transient']:
   raw=folder/(name+'.f32le');array=np.fromfile(raw,'<f4').reshape(-1,2)
   if array.shape!=(182400,2) or not np.isfinite(array).all():raise ValueError('Unexpected model output '+str(raw))
   wavfile.write(folder/(name+'.wav'),48000,array);fields[name]={'path':str(folder/(name+'.wav')),'sha256':digest(folder/(name+'.wav')),'float_payload_sha256':digest(raw)}
  states=np.fromfile(folder/'state-proof.u64le','<u8').reshape(-1,3);forces=np.fromfile(folder/'force-proof.u64le','<u8').reshape(-1,3)
  parity=bool(len(states)==714 and len(forces)==182400 and np.array_equal(states[:,1],states[:,2]) and np.array_equal(forces[:,1],forces[:,2]))
  if not parity or info['parity_mismatches'] or info['new_observer_faults'] or info['original_fault_flags']:raise ValueError('Observer changed physical state/force or raised a fault')
  return {'id':case['id'],'outputs':fields,'physical_force_checkpoint_parity':parity,'historical_baseline_payload_identical':digest(folder/'baseline.f32le')==case['historical_baseline_float32_sha256'],'historical_candidate_payload_identical':digest(folder/'candidate.f32le')==case['historical_candidate_float32_sha256'],'diagnostics':info}
 results=[]
 with ThreadPoolExecutor(max_workers=jobs) as pool:
  for future in as_completed([pool.submit(render,case) for case in cases]):results.append(future.result())
 results.sort(key=lambda row:list(allowed).index(row['id']))
 report={'scope':'Fresh synthesis of the fixed failed research pilot; no new fit, reference acquisition, metrics or default promotion','cases':results,'original_global_result':'Four of six passed; both C6 cases failed early band guards. Retain that result.','controls':'0.1snoteon,3.8sheld,pedal0,humanization0,mechanisms0,repetitionOFF,gain0,width1,sample_rate48000','new_reference_audio_read':False}
 (output/'synthesis-receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--phase',choices=['verify','build','math','synth'],default='verify');parser.add_argument('--output',type=Path,default=ROOT/'out/causal-radiation-replay');parser.add_argument('--cxx',default=os.environ.get('CXX','g++'));parser.add_argument('--case',action='append',dest='cases');parser.add_argument('--jobs',type=int,choices=[1,2],default=1);args=parser.parse_args();index=verify_sources()
 if args.phase=='verify':print(json.dumps({'verified_frozen_files':len(index['files']),'original_producer_inputs':22}));return
 output=args.output.resolve()
 for name in ['src','Research','References','include','tools','.git','plugin','vst3','third_party','Audio']:
  protected=(ROOT/name).resolve()
  if output==protected or protected in output.parents:raise ValueError('Output must be outside protected source/reference trees: '+str(output))
 if output.exists() and (not output.is_dir() or any(output.iterdir())):raise ValueError('Choose a fresh, empty output directory; existing artifacts are never overwritten: '+str(output))
 build(output,shlex.split(args.cxx));os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
 if args.phase=='math':print(json.dumps(math(output),indent=2))
 elif args.phase=='synth':print(json.dumps(synth(output,args.cases,args.jobs),indent=2))
 else:print(output/'build-receipt.json')
 verify_sources()
if __name__=='__main__':main()
