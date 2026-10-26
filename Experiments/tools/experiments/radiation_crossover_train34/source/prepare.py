from pathlib import Path
import ast,datetime,hashlib,json,shutil,subprocess
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent;PKG=ROOT/'tools/experiments/causal_radiation_pilot/producer';OLD=ROOT/'out/full-causal-radiation/v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
split=ROOT/'References/GrandFullRange/split.json';feature=ROOT/'References/GrandFullRange/combined_train_features.json';ids=json.loads(split.read_text())['combined_training_ids'];rows={r['id']:r for r in json.loads(feature.read_text())['samples']};assert len(ids)==34 and set(ids)==set(rows)
previous=ROOT/'out/full-radiation-crossover/v1/result.json';prev=json.loads(previous.read_text());prior={r['id']:r for r in prev['cases']};assert len(prior)==6 and prev['passes_all_unchanged_pilot_gates'];original=ROOT/'out/full-calibration/v3/control-renders'
from scipy.io import wavfile
import numpy as np
inventory=[]
for ident in ids:
 row=rows[ident];midi=int(row['midi']);vel=int(row['midi_velocity']);assert vel in [40,93] and row['split']=='train'
 audio=original/(ident+'.wav');events=audio.with_suffix('.events');receipt=audio.with_suffix('.json');old=json.loads(receipt.read_text());rate,x=wavfile.read(audio);assert rate==48000 and x.dtype==np.float32 and x.shape==(182400,2);assert old['inputs']['calibration_sha256']=='619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7'
 folder=OUT/'renders'/ident
 entry={'id':ident,'midi':midi,'velocity':vel,'frames':182400,'role':'train','reused_existing_six':ident in prior,'baseline_cache':{'path':str(audio),'sha256':sha(audio),'float32_payload_sha256':hashlib.sha256(x.tobytes()).hexdigest()},'cache_events':{'path':str(events),'sha256':sha(events)},'cache_receipt':{'path':str(receipt),'sha256':sha(receipt)},'cache_lineage':old['inputs']}
 if ident in prior:entry['reuse_source']={'result':{'path':str(previous),'sha256':sha(previous)},'prior_case':prior[ident]}
 else:entry['proposed_outputs']={'folder':str(folder),'baseline':str(folder/'baseline.wav'),'causal':str(folder/'causal.wav'),'candidate':str(folder/'compatibility.wav'),'state_proof':str(folder/'state-proof.u64le'),'force_proof':str(folder/'force-proof.u64le')}
 inventory.append(entry)
(OUT/'inventory.json').write_text(json.dumps({'split':{'path':str(split),'sha256':sha(split)},'features':{'path':str(feature),'sha256':sha(feature)},'reference_or_eval_audio_opened':False,'cases':inventory,'configuration':{'sample_rate':48000,'frames':182400,'note_on_frame':4800,'pedal_initial':0,'humanization':0,'mechanical_level':0,'repetition_controller':False,'gain_db':0,'stereo_width':1,'seed':123456}},indent=2)+'\n')
source=OUT/'sources';shutil.copytree(OLD/'music/sources',source);observer=OUT/'CausalRadiation.h';shutil.copyfile(PKG/'observer/CausalRadiation.h',observer)
harness=(PKG/'frozen_driver/producer.cpp').read_text()
(OUT/'producer.cpp').write_text(harness)
operator=ROOT/'out/full-radiation-crossover/v1/postprocess.py';assert sha(operator)=='636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e';text=operator.read_text();tree=ast.parse(text);wanted=['coefficients','block','process','selftests'];segments=[]
for name in wanted:
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);segments.append(ast.get_source_segment(text,node))
module='"""Byte-preserved functions from the frozen single400Hz operator. No fitting."""\nimport math\nimport numpy as np\nRATE=48000;CUTOFF=400.\n\n'+'\n\n'.join(segments)+'\n';(OUT/'compat400.py').write_text(module)
# Compile-only preparation. No new candidate output is opened or generated.
model=source/'src/full_instrument';flags=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-I'+str(source/'include'),'-I'+str(model),'-I'+str(OUT)];commands=[['g++',*flags,'-c',str(model/'FullInstrument.cpp'),'-o',str(OUT/'api.o')],['g++',*flags,'-c',str(OUT/'producer.cpp'),'-o',str(OUT/'harness.o')],['g++',str(OUT/'api.o'),str(OUT/'harness.o'),'-o',str(OUT/'producer')]]
for command in commands:
 call=subprocess.run(command,text=True,capture_output=True)
 if call.returncode:raise RuntimeError(call.stderr)
inputs=[{'path':str(p),'sha256':sha(p)} for p in [observer,OUT/'producer.cpp',OUT/'prepare.py',OUT/'compat400.py',*sorted(p for p in source.rglob('*') if p.is_file())]]
build={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Newno-stem diagnostics-only producer; held old/control/causal pair, same frozen observer. NO synthesis yet.','binary':{'path':str(OUT/'producer'),'sha256':sha(OUT/'producer')},'source_inputs':inputs,'commands':commands,'configuration':json.loads((OUT/'inventory.json').read_text())['configuration'],'inventory':{'path':str(OUT/'inventory.json'),'sha256':sha(OUT/'inventory.json')},'operator':{'original_path':str(operator),'original_sha256':sha(operator),'extracted_module':str(OUT/'compat400.py'),'module_sha256':sha(OUT/'compat400.py'),'function_source_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in zip(wanted,segments)}},'math_validation':{'path':str(OLD/'math-validation.json'),'sha256':sha(OLD/'math-validation.json')},'pilot_observer_header_sha256':sha(PKG/'observer/CausalRadiation.h'),'source_lineage':'Originaloldsource5c8/619/6b4 withreadonlyinstrumentation; disabledexpensivecaptureStems only, sameasbytevalidated9smusic. Before/after714physicalstatehashcheckpoints+182400contact/Schurforcehashrows percase.','source_protocol_pending':True}
(OUT/'build-manifest.json').write_text(json.dumps(build,indent=2)+'\n');print('inventory',sha(OUT/'inventory.json'),'newcases',sum(not r['reused_existing_six'] for r in inventory));print('build',sha(OUT/'build-manifest.json'),'binary',build['binary']['sha256'])
