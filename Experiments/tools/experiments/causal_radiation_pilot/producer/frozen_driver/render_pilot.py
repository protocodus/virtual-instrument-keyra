from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import datetime,hashlib,json,subprocess
import numpy as np
from scipy.io import wavfile
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
freeze_path=OUT/'candidate-freeze.json';freeze=json.loads(freeze_path.read_text());protocol=json.loads(Path(freeze['protocol']['path']).read_text());assert sha(freeze['protocol']['path'])=='5ec7ace5cffb6655fb017430d328dc784762beb9ff5460eb5c63a07e606b96fa'
assert json.loads(Path(freeze['math_validation']['path']).read_text())['passed']
def guard():
 assert sha(freeze['binary']['path'])==freeze['binary']['sha256']
 for row in freeze['source_inputs']:assert sha(row['path'])==row['sha256'],row['path']
 assert sha(freeze['math_validation']['path'])==freeze['math_validation']['sha256']
 assert sha(freeze_path)==freeze_hash
freeze_hash=sha(freeze_path);guard();started=now();(OUT/'render-start.json').write_text(json.dumps({'render_started_at_utc':started,'candidate_freeze_sha256':freeze_hash,'fixed_cases':[c['id'] for c in protocol['cases']],'max_parallel_processes':2},indent=2)+'\n')
def render(case):
 guard();folder=OUT/'pilot'/case['id'];folder.mkdir(parents=True,exist_ok=False);command=[freeze['binary']['path'],str(folder),str(case['midi']),str(case['midi_velocity'])];case_start=now();call=subprocess.run(command,text=True,capture_output=True);(folder/'render.json').write_text(call.stdout);(folder/'stderr.txt').write_text(call.stderr)
 if call.returncode:raise RuntimeError(case['id']+' failedexit'+str(call.returncode)+call.stderr)
 info=json.loads(call.stdout);assert info['midi']==case['midi'] and info['velocity']==case['midi_velocity'] and info['frames']==182400
 baseline=np.fromfile(folder/'baseline.f32le','<f4').reshape(-1,2);candidate=np.fromfile(folder/'candidate.f32le','<f4').reshape(-1,2);assert baseline.shape==(182400,2) and candidate.shape==baseline.shape and np.isfinite(baseline).all() and np.isfinite(candidate).all()
 cached=Path(case['cached_control_audio']['path']);assert sha(cached)==case['cached_control_audio']['sha256'];rate,original=wavfile.read(cached);assert rate==48000 and original.dtype==np.float32 and len(original)>=len(baseline)
 baseline_match=baseline.tobytes()==original[:len(baseline)].tobytes()
 states=np.fromfile(folder/'state-proof.u64le','<u8').reshape(-1,3);forces=np.fromfile(folder/'force-proof.u64le','<u8').reshape(-1,3)
 state_parity=bool(np.array_equal(states[:,1],states[:,2]) and len(states)==714);force_parity=bool(np.array_equal(forces[:,1],forces[:,2]) and len(forces)==182400 and np.array_equal(forces[:,0],np.arange(182400)))
 assert baseline_match,(case['id'],'baselinepayload mismatch');assert state_parity and force_parity and info['parity_mismatches']==0 and info['new_observer_faults']==0 and info['original_fault_flags']==0
 for name,array in [('baseline',baseline),('candidate',candidate)]:wavfile.write(folder/(name+'.wav'),48000,array)
 stems={}
 for name in ['primary','secondary','transient']:
  data=np.fromfile(folder/(name+'.f32le'),'<f4').reshape(-1,2);assert data.shape==baseline.shape and np.isfinite(data).all();wavfile.write(folder/(name+'.wav'),48000,data);stems[name]={'path':str(folder/(name+'.wav')),'sha256':sha(folder/(name+'.wav'))}
 row={'id':case['id'],'midi':case['midi'],'velocity':case['midi_velocity'],'frames':182400,'render_started_at_utc':case_start,'command':command,'baseline':{'path':str(folder/'baseline.wav'),'sha256':sha(folder/'baseline.wav')},'candidate':{'path':str(folder/'candidate.wav'),'sha256':sha(folder/'candidate.wav')},'mechanical_state_bit_parity':state_parity,'force_bit_parity':force_parity,'new_faults':0,'baseline_float32_payload_identical_to_cached_control':baseline_match,'cached_control_audio':case['cached_control_audio'],'stems':stems,'diagnostics':info,'parity_proof':{'scope':'Oneintactphysicaltrajectory, observerread-only. Physicalq/p/damp,board,hammer,pedal/counters hashesbefore/afterevery256samples+last; contact88+Schur3forcehashesbefore/afterEVERYsample. CorrectstandardFNV1a64 bit-wordbytes; no cryptographiccollision guarantee. Sourcehasnophysicalfeedback/constp-onlydriver.','state_checkpoints':len(states),'state_rows':{'path':str(folder/'state-proof.u64le'),'sha256':sha(folder/'state-proof.u64le')},'force_rows':{'path':str(folder/'force-proof.u64le'),'sha256':sha(folder/'force-proof.u64le')}}}
 (folder/'case-receipt.json').write_text(json.dumps(row,indent=2)+'\n');guard();print(case['id'],'baselinebytes exact, physical/forceparity passed',flush=True);return row
results=[]
# Firstofficialcase establishes producer/cachedbaseline/parity before the rest;
# no parameter or analysis choices may change after looking at any output.
results.append(render(protocol['cases'][0]))
with ThreadPoolExecutor(max_workers=2) as pool:
 futures=[pool.submit(render,case) for case in protocol['cases'][1:]]
 for task in as_completed(futures):results.append(task.result())
results.sort(key=lambda row:[c['id'] for c in protocol['cases']].index(row['id']));guard()
producer={'protocol':freeze['protocol'],'binary':freeze['binary'],'source_inputs':freeze['source_inputs'],'configuration':freeze['configuration'],'readout_method':freeze['readout_method'],'math_validation':freeze['math_validation'],'candidate_freeze':{'path':str(freeze_path),'sha256':freeze_hash},'render_started_at_utc':started,'render_finished_at_utc':now(),'cases':results,'passed':True,'limits':['Onefixedcausalobserver, no parameter/audio-basedselection; oldendpoint/finite-differencemathnegatives archived withoutaudio.','Allbaseline/candidate/stems shareoneoriginalphysicalrun percase; onlyobserverpressure changes.','SameHP24Hz/output0dB/stereowidth1, no room, fades, normalization or sourcepresetmodification.','No realreferenceaudio openedbyproducer; only authenticatedpreviousmodelcontrol usedforbitparity.']}
producer_path=OUT/'producer-receipt.json';producer_path.write_text(json.dumps(producer,indent=2)+'\n');capture={'protocol_sha256':freeze['protocol']['sha256'],'producer_receipt':{'path':str(producer_path),'sha256':sha(producer_path)},'cases':results};(OUT/'capture.json').write_text(json.dumps(capture,indent=2)+'\n');print('producer',sha(producer_path),'capture',sha(OUT/'capture.json'),flush=True)
