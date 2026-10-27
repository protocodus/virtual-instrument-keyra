#!/usr/bin/env python3
"""Fixed isolated-register pressure check: source/compile first; root-authorized run only."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,subprocess,sys,time
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent;CORE=OUT.parent/'harness-v1'
CORE_PROTOCOL='f886a11d36e5c79d8b5ebb22411a86e439338c84d3fdfc9579b01f4d76228646'
QUALITY='7023e7ca4984312ff72492a55267b630482762bc01a8369360dcd6fd657a6e9e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
 p=Path(p)
 if p.exists():raise ValueError('Preserve prior artifact '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def verify(rows):
 for row in rows:
  if sha(row['path'])!=row['sha256']:raise ValueError('Changed frozen input '+row['path'])
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def prepare():
 if (OUT/'protocol.json').exists() or (OUT/'build').exists():raise ValueError('Preparation already exists; preserve it')
 if sha(CORE/'protocol.json')!=CORE_PROTOCOL or sha(CORE/'quality.py')!=QUALITY:raise ValueError('Expected final core harness identities')
 parent=read(CORE/'protocol.json');verify(parent['bindings'])
 core=load('register_parent_harness',CORE/'run.py')
 for name in ['ObserverCapture.h','state_snapshot.inc','inventory.inc','quality.py']:(OUT/name).write_bytes((CORE/name).read_bytes())
 driver=(CORE/'harness.cpp').read_bytes();anchor=b'int main(int argc,char** argv){';assert driver.count(anchor)==1
 prefix=driver[:driver.index(anchor)];(OUT/'FrozenHarnessHelpers.h').write_bytes(prefix)
 quality=load('register_frozen_quality',OUT/'quality.py')
 if json.loads(json.dumps(quality.RECIPE))!=parent['observer_quality']:raise ValueError('Quality recipe differs')
 shared=[]
 for variant in ['baseline','candidate']:
  for name in core.FILES:shared.append(rec(CORE/'build'/variant/name))
 bindings=[rec(OUT/name) for name in ['run.py','register.cpp','FrozenHarnessHelpers.h','ObserverCapture.h','state_snapshot.inc','inventory.inc','quality.py']]+[rec(CORE/'protocol.json'),rec(CORE/'harness.cpp'),rec(CORE/'run.py')]+shared
 protocol={'schema_version':1,'frozen_at_utc':now(),'scope':'SOURCE ONLY fixed10isolatedMIDIcases, not acousticreferencePCM or freshrecording evidence. No Piano constructed/steps/listening/fit.','parent_protocol':rec(CORE/'protocol.json'),'bindings':bindings,'configuration':{'sample_rate':48000,'frames_per_case':48000,'notes':[21,36,60,84,108],'velocity_MIDI':[14,124],'seed':0x4b657972,'humanization':.65,'dynamics':.5,'width':1,'gain_db':0,'mechanical_level':0,'repetition_controller':True,'mechanism_body_coupling':True,'mechanism_observation':True,'events':[{'frame':0,'kind':'pedal','value':.75},{'frame':2400,'kind':'note_on','velocity':'velocity_MIDI/127'},{'frame':31200,'kind':'note_off'}],'one_new_piano_per_case':True},'helpers_exact_frozen_prefix':{'source':rec(CORE/'harness.cpp'),'prefix_bytes':len(prefix),'prefix_sha256':hashlib.sha256(prefix).hexdigest()},'observer_quality_recipe':parent['observer_quality'],'quality_source_sha256':QUALITY,'physical_requirement':'One finalpadding-free deepstatecheckpoint percase, ONLY3approvedobservermemoryfamiliesomitted; commonfullsource/currentRNG/couplings, finiteoutput/zerofaults/oneactualrequestandlaunch.','arm_flags':parent['arm_flags'],'flags_common':parent['flags'],'gate_changes_or_parameter_variants':False,'required_execution_authorization':'Rootreceiptbindingthisprotocol +passedcorecorrectnessresult +reviewedcoreperformance; no modelrun fromprepare.','budget':'20one-secondsyntheticperformances, approximately1minuteCPU; maximum180wallsecondsperarm.','recording_audio_access':False,'adopted':False}
 write(OUT/'protocol.json',protocol);builds=[]
 for variant in ['baseline','candidate']:
  directory=OUT/'build'/variant;directory.mkdir(parents=True,exist_ok=False);source=CORE/'build'/variant;binary=directory/'register-probe'
  command=['g++',*parent['flags'],'-DKEYRA_FUSION_CORRECTNESS=1','-DKEYRA_FUSION_CANDIDATE=1','-DKEYRA_FULL_PRESSURE_SIMD='+str(int(variant=='candidate')),'-I'+str(source/'include'),'-I'+str(source/'src/full_instrument'),'-I'+str(OUT),str(source/'src/full_instrument/FullInstrument.cpp'),str(OUT/'register.cpp'),'-o',str(binary)]
  call=subprocess.run(command,capture_output=True,text=True);(directory/'compile.stdout').write_text(call.stdout);(directory/'compile.stderr').write_text(call.stderr)
  if call.returncode:raise ValueError('Compilation failed '+variant+': '+call.stderr)
  linked=subprocess.check_output(['ldd',str(binary)],text=True)
  if 'libgomp' in linked or 'libomp' in linked:raise ValueError('Unexpected OpenMP runtime')
  builds.append({'variant':variant,'command':command,'binary':rec(binary),'dynamic_dependencies':linked})
 verify(bindings);write(OUT/'build-receipt.json',{'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'builds':builds,'model_constructions':0,'model_frames':0});print('SOURCE ONLY register sources frozen and compiled; no models run',flush=True)
def run():
 protocol=read(OUT/'protocol.json');verify(protocol['bindings']);build=read(OUT/'build-receipt.json');verify([build['protocol']]+[r['binary'] for r in build['builds']]);auth=read(OUT/'authorization.json')
 if auth['protocol']!=rec(OUT/'protocol.json') or 'register' not in auth['actions'] or auth['core_timing_accepted_for_register'] is not True:raise ValueError('Root authorization required')
 for role,name in [('core_correctness_result','correctness-result.json'),('core_performance_result','performance-result.json')]:
  verify([auth[role]])
  if Path(auth[role]['path']).resolve()!=(CORE/name).resolve():raise ValueError('Wrong core result')
 if read(CORE/'correctness-result.json')['pass'] is not True:raise ValueError('Core quality not passed')
 write(OUT/'opening-started.json',{'at_utc':now(),'protocol':rec(OUT/'protocol.json'),'authorization':rec(OUT/'authorization.json')});started=time.monotonic();reports={}
 for row in build['builds']:
  directory=OUT/'results'/row['variant'];directory.mkdir(parents=True,exist_ok=False)
  call=subprocess.run([row['binary']['path'],str(directory)],capture_output=True,text=True,timeout=180);(directory/'stdout.json').write_text(call.stdout);(directory/'stderr.txt').write_text(call.stderr)
  if call.returncode:raise ValueError('Register producer failed '+row['variant']+' '+str(call.returncode))
  reports[row['variant']]=read(directory/'stdout.json')
 if reports['baseline']!=reports['candidate']:raise ValueError('Register event/diagnostic mismatch')
 quality=load('register_frozen_quality',OUT/'quality.py');import numpy as np
 comparisons=[]
 for case in reports['baseline']['cases']:
  name=case['name'];dirs={v:OUT/'results'/v for v in ['baseline','candidate']};states={v:dirs[v]/(name+'-final.state') for v in dirs}
  if states['baseline'].read_bytes()!=states['candidate'].read_bytes():raise ValueError('Physical register state differs '+name)
  observer={}
  for label,suffix,dtype in [('raw_f64','.f64le-pressure','<f8'),('output_f32','.f32le-planar','<f4')]:
   arrays={v:np.fromfile(dirs[v]/(name+suffix),dtype=dtype) for v in dirs}
   arrays={v:x.reshape(-1,2) if label=='raw_f64' else x.reshape(2,-1).T for v,x in arrays.items()}
   if any(x.shape!=(48000,2) or not np.isfinite(x).all() for x in arrays.values()):raise ValueError('Invalid observer payload '+name)
   observer[label]=quality.compare(arrays['baseline'],arrays['candidate'],48000)
  for v in dirs:
   if read(dirs[v]/(name+'.prepare.json'))['valid'] is not True:raise ValueError('Invalid mode inventory '+name)
  passed=all(x['pass'] for x in observer.values());entry={'case':case,'physical_final_state_exact':True,'observer_quality':observer,'pass':passed,'state_files':[rec(p) for p in states.values()],'observer_files':[rec(dirs[v]/(name+suffix)) for v in dirs for suffix in ['.f64le-pressure','.f32le-planar']]};comparisons.append(entry)
  write(OUT/'results'/(name+'-quality.json'),entry)
 verify(protocol['bindings']);result={'at_utc':now(),'protocol':rec(OUT/'protocol.json'),'pass':all(x['pass'] for x in comparisons),'case_count':len(comparisons),'comparisons':comparisons,'wall_seconds':time.monotonic()-started,'numeric_engineering_bounds_not_audibility':True,'recording_audio_access':False,'adopted':False};write(OUT/'result.json',result);print(json.dumps({'result':rec(OUT/'result.json'),'pass':result['pass'],'case_count':len(comparisons)},indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','run']);args=parser.parse_args();{'prepare':prepare,'run':run}[args.action]()
