#!/usr/bin/env python3
"""Ten fixed register cases through the actual CMake-built, uninstrumented CLI."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,math,shlex,struct,subprocess,time
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent;NATIVE=OUT.parent/'integration/native';REG=OUT.parent/'register-v1';QUALITY=REG/'quality.py'
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
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def macro(tokens,name):
 value=None
 for token in tokens:
  if token=='-U'+name:value=None
  elif token.startswith('-D'+name+'='):value=token.split('=',1)[1]
 return value

def prepare():
 if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
 native=read(NATIVE/'result.json');assert native['passed'] and native['kind']=='native'
 verify(read(NATIVE/'freeze.json'))
 qualified=read(REG/'result.json');assert qualified['pass'] and qualified['case_count']==10
 assert sha(QUALITY)=='7023e7ca4984312ff72492a55267b630482762bc01a8369360dcd6fd657a6e9e'
 compiled=read(NATIVE/'build/compile_commands.json');selections={}
 for row in compiled:
  command=row.get('arguments') or shlex.split(row['command'])
  if 'keyra_full_instrument.dir' in row.get('command',''):
   selections['library']={k:macro(command,'KEYRA_FULL_'+k) for k in ['PRESSURE_SIMD','FREE_UNISON_SIMD','FAST_CONTACT','MECHANISM_CACHE','MODEL_PROFILE']}
  if 'keyra_full_render.dir' in row.get('command',''):
   selections['renderer']={k:macro(command,'KEYRA_RENDER_'+k) for k in ['PRESSURE_SIMD','FREE_UNISON_SIMD','FAST_CONTACT','MECHANISM_CACHE','MODEL_PROFILE']}
 expected={'PRESSURE_SIMD':'1','FREE_UNISON_SIMD':'1','FAST_CONTACT':'1','MECHANISM_CACHE':'1','MODEL_PROFILE':'0'}
 assert selections=={'library':expected,'renderer':expected}
 binary=NATIVE/'build/keyra_full_render';cases=[];bindings=[rec(__file__),rec(binary),rec(QUALITY),rec(NATIVE/'result.json'),rec(NATIVE/'freeze.json'),rec(NATIVE/'build/compile_commands.json'),rec(NATIVE/'build/CMakeCache.txt'),rec(REG/'protocol.json'),rec(REG/'result.json'),*read(NATIVE/'freeze.json')]
 for name,note in [('A0',21),('C2',36),('C4',60),('C6',84),('C8',108)]:
  for velocity in [14,124]:
   ident=name+'v'+str(velocity);score=OUT/'events'/(ident+'.events');score.parent.mkdir(exist_ok=True);score.write_text(f'0 pedal 0 0.75\n0.05 on {note} {velocity}\n0.65 off {note} 0\n')
   wav=OUT/'renders'/(ident+'.wav');report=wav.with_suffix('.json');command=[str(binary),'--output',str(wav),'--report',str(report),'--events',str(score),'--rate','48000','--seconds','1','--block','64','--seed',str(0x4b657972),'--param','dynamics=.5','--param','humanization=.65','--param','mechanicalLevel=0','--param','width=1','--param','gain=0','--mechanism-body','1','--mechanism-direct','1','--repetition','1']
   baseline=REG/'results/baseline'/(ident+'.f32le-planar');on=REG/'results/candidate'/(ident+'.f32le-planar');bindings += [rec(score),rec(baseline),rec(on)]
   cases.append({'id':ident,'note':note,'velocity_MIDI':velocity,'command':command,'wav':str(wav),'report':str(report),'off_baseline':rec(baseline),'qualified_on':rec(on)})
 protocol={'frozen_at_utc':now(),'scope':'TenfixedactualCMakeCLIregisterrenders; no recordingreferencePCM, fit, normalization, timingbenchmark or newlisteningclip. Parentauthorizedafterpassednativeintegration.','binary':rec(binary),'passed_native_integration':rec(NATIVE/'result.json'),'compile_selections':selections,'bindings':bindings,'cases':cases,'frames_per_case':48000,'quality_source_sha256':sha(QUALITY),'quality_recipe_unchanged':True,'quality_gate':'Exactlyfrozenquality.compare onproductionf32WAVversusqualifiedOFFf32baseline; noalignment/gain/onsetfit.','qualified_ON_payload_bit_identity':'Measuredandretained, notadditionalacceptancegate.','execution_authorization':'Parenttask authorizesONEten-caseactualCLIrunoncepassednativeintegrationandpre-runplan/binaryhashfrozen. Conditionsverifiedbyprepareandrun.','adopted':False}
 write(OUT/'protocol.json',protocol);print(json.dumps({'protocol':rec(OUT/'protocol.json'),'source_only':True,'cases':10},indent=2))

def wav32(path):
 import numpy as np
 content=Path(path).read_bytes();assert content[:4]==b'RIFF' and content[8:12]==b'WAVE';offset=12;fmt=data=None
 while offset+8<=len(content):
  kind=content[offset:offset+4];length=struct.unpack_from('<I',content,offset+4)[0];block=content[offset+8:offset+8+length]
  if kind==b'fmt ':assert fmt is None;fmt=struct.unpack_from('<HHIIHH',block)
  if kind==b'data':assert data is None;data=block
  offset+=8+length+(length&1)
 assert fmt==(3,2,48000,384000,8,32) and data is not None and len(data)==48000*8
 result=np.frombuffer(data,dtype='<f4').reshape(48000,2);assert np.isfinite(result).all();return result

def run():
 protocol=read(OUT/'protocol.json');verify(protocol['bindings']);assert read(NATIVE/'result.json')['passed'];write(OUT/'opening-started.json',{'at_utc':now(),'protocol':rec(OUT/'protocol.json'),'authorization_condition':'Passedfrozenactualnativeintegration+parenttaskauthorization'});started=time.monotonic();(OUT/'renders').mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('actual_cli_frozen_quality',QUALITY);quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality);import numpy as np
 cases=[]
 for case in protocol['cases']:
  call=subprocess.run(case['command'],capture_output=True,text=True,timeout=90);(OUT/'renders'/(case['id']+'.stdout')).write_text(call.stdout);(OUT/'renders'/(case['id']+'.stderr')).write_text(call.stderr)
  if call.returncode:raise ValueError('Actual CLI failed '+case['id']+' '+str(call.returncode))
  report=read(case['report']);expected={'model_profile':'OriginalControl','calibration_header_sha256':'619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7','sample_rate':48000,'frames':48000,'block_frames':64,'seed':0x4b657972,'pressure_simd':True,'free_unison_simd':True,'fast_contact':True,'mechanism_cache':True,'events_applied':3,'events_after_render':0,'events_rejected':0,'requests':1,'launches':1,'fault_flags':0,'unsafe_launches':0,'topology':{'strings':230,'string_modes':17778,'board_modes':475},'parameters':{'dynamics':.5,'humanization':.65,'mechanicalLevel':0,'width':1,'gain_db':0},'isolation':{'mechanism_body_coupling':True,'direct_mechanism_observation':True,'repetition_controller':True}}
  for key,value in expected.items():
   if report[key]!=value:raise ValueError('Actual CLI metadata mismatch '+case['id']+' '+key)
  actual=wav32(case['wav']);old=np.fromfile(case['off_baseline']['path'],dtype='<f4').reshape(2,-1).T;qualified=np.fromfile(case['qualified_on']['path'],dtype='<f4').reshape(2,-1).T
  compared=quality.compare(old,actual,48000);identity=actual.tobytes()==qualified.tobytes()
  entry={'id':case['id'],'command':case['command'],'report':rec(case['report']),'wav_external':rec(case['wav']),'actual_float32_payload_sha256':hashlib.sha256(actual.tobytes()).hexdigest(),'qualified_ON_payload_byte_identical':identity,'quality_vs_OFF':compared,'pass':compared['pass']};cases.append(entry);write(OUT/(case['id']+'-quality.json'),entry)
 verify(protocol['bindings']);result={'at_utc':now(),'protocol':rec(OUT/'protocol.json'),'pass':all(c['pass'] for c in cases),'case_count':len(cases),'cases':cases,'all_production_payloads_exact_qualified_ON':all(c['qualified_ON_payload_byte_identical'] for c in cases),'wall_seconds':time.monotonic()-started,'scope':'ActualCMakeproductionCLI path, numericalengineeringbounds not inaudibility/pitch/ReasonSDKorproductionreadiness; onefixedmatrix/no variants, privateWAVsexternal.'};write(OUT/'result.json',result);print(json.dumps({'result':rec(OUT/'result.json'),'pass':result['pass'],'cases':len(cases),'all_production_payloads_exact_qualified_ON':result['all_production_payloads_exact_qualified_ON']},indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','run']);args=parser.parse_args();{'prepare':prepare,'run':run}[args.action]()
