#!/usr/bin/env python3
"""Review frozen TRAIN34 evidence. No PCM, DSP, filter or scoring is executed."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ast, gzip, hashlib, json
PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[2]
FAILED=('A0v4','A0v12','D#5v4','D#5v12','C7v4','C7v12','C8v4','C8v12')

def require(value,message):
 if not value:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def timestamp(value):return datetime.fromisoformat(value)
def check():
 index_path=PACKAGE/'index.json';initial=index_path.read_bytes();index=json.loads(initial);mapping={};snapshots=[]
 for row in index['artifacts']:
  path=ROOT/row['package_path'];stored=path.read_bytes();require(digest(stored)==row['stored_sha256'],'Stored archive changed: '+str(path))
  require(row['encoding'] in ['identity','gzip'],'Unknown encoding')
  data=gzip.decompress(stored) if row['encoding']=='gzip' else stored
  require(digest(data)==row['sha256'] and len(data)==row['bytes'],'Decoded archive changed: '+str(path))
  for alias in row['archived_paths']:mapping[(alias,row['sha256'])]=(row,data)
  snapshots.append((path,row['stored_sha256']))
 def bound(record):
  key=(record['path'],record['sha256']);require(key in mapping,'Metadata/source not archived: '+record['path']);return mapping[key][1]
 def load(record):return json.loads(bound(record))
 oldroot='/workspace/virtual-instrument-keyra/out/full-radiation-crossover/train34/'
 def named(name):
  rows=[(key,data) for key,(row,data) in mapping.items() if key[0]==oldroot+name]
  require(len(rows)==1,'Missing/ambiguous receipt: '+name);return json.loads(rows[0][1])
 protocol=named('protocol.json');freeze=named('protocol-freeze.json');reference=named('reference-control.json');result=named('result.json');summary=named('summary.json')
 plan=load(protocol['producer_contract']['producer_plan']);producer=named('producer/producer-receipt.json');capture=named('producer/capture.json');candidate_freeze=load(producer['candidate_freeze']);build=named('producer/build-manifest.json')
 require(result['protocol']==summary['protocol']==freeze['protocol']==producer['protocol']==capture['protocol']==candidate_freeze['protocol'],'Protocol descriptor mismatch')
 require(summary['result']=={'path':oldroot+'result.json','sha256':digest(bound(summary['result']))},'Result descriptor mismatch')
 require(load(result['reference_control'])==reference and load(result['protocol_freeze'])==freeze,'Reference/freeze mismatch')
 require(bound(protocol['consumer_source'])==bound(result['consumer_source']) and protocol['consumer_source']==freeze['consumer_source'],'Consumer source mismatch')
 require(protocol['reference_source']==freeze['reference_source'],'Reference source mismatch')
 require(producer['producer_plan']==candidate_freeze['producer_plan']==protocol['producer_contract']['producer_plan'],'Producer plan mismatch')
 for key in ['source_inputs','binary','configuration']:
  require(producer[key]==candidate_freeze[key]==plan[key],'Source/config/binary descriptor mismatch: '+key)
 require(producer['configuration']==protocol['producer_contract']['configuration'],'Protocol configuration mismatch')
 require(producer['configuration']=={'sample_rate':48000,'frames':182400,'note_on_frame':4800,'pedal_initial':0,'humanization':0,'mechanical_level':0,'repetition_controller':False,'gain_db':0,'stereo_width':1,'seed':123456},'Frozen controls changed')
 require(producer['binary']==build['binary'],'Compiled binary descriptor changed')
 for source in plan['source_inputs']:bound(source)
 require(len(plan['source_inputs'])==len(index['frozen_source_bindings'])==27,'Source inventory changed')
 for binding,source in zip(index['frozen_source_bindings'],plan['source_inputs']):
  require((binding['original_path'],binding['sha256'])==(source['path'],source['sha256']),'Source binding order changed')
  row,data=mapping[(source['path'],source['sha256'])];require(row['package_path']==binding['package_path'] and row['encoding']==binding['encoding'],'Source archive pointer changed')
 operator=bound(protocol['fixed400_operator']).decode();extract=next(bound(r).decode() for r in plan['source_inputs'] if r['path'].endswith('/compat400.py'))
 for name in ['coefficients','block','process','selftests']:
  def segment(text):return ast.get_source_segment(text,next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name))
  require(segment(operator)==segment(extract),'Fixed operator function changed: '+name)
 require(producer['fixed400_operator']==candidate_freeze['fixed400_operator']==plan['fixed400_operator']==protocol['fixed400_operator'],'Operator descriptor mismatch')
 times=[protocol['frozen_at_utc'],candidate_freeze['frozen_at_utc'],producer['render_started_at_utc'],producer['render_finished_at_utc'],named('candidate-opening-started.json')['started_at_utc'],result['completed_at_utc']]
 require(list(map(timestamp,times))==sorted(map(timestamp,times)),'Protocol/source/render/scoring chronology changed')
 require(producer['passed'] is True and producer['failures']==[] and len(producer['cases'])==28,'Producer batch incomplete')
 require(capture['cases']==producer['cases'],'Capture and producer rows differ')
 new=[c for c in protocol['cases'] if c['role']=='new_confirmation'];require([c['id'] for c in new]==[c['id'] for c in producer['cases']],'New28 inventory/order changed')
 require(result['new_cases_scored_once']==28 and result['source_DSP_renders_by_consumer']==0,'Single consumer scope changed')
 prior={c['id']:c for c in load(protocol['existing_six_result'])['cases']};cases={c['id']:c for c in result['cases']};requests={c['id']:c for c in protocol['cases']}
 require(len(cases)==len(result['cases'])==34 and set(cases)==set(requests),'TRAIN34 inventory changed')
 for ident,old in prior.items():require(cases[ident]==old==requests[ident]['reused_outcome'],'Original six outcome changed: '+ident)
 for entry in producer['cases']:
  ident=entry['id'];request=requests[ident]
  require((entry['midi'],entry['velocity'],entry['frames'])==(request['midi'],request['midi_velocity'],182400),'Requested event changed')
  require(entry['baseline_float32_payload_identical_to_cached_control'] is True,'Baseline parity claim failed')
  require(entry['mechanical_state_bit_parity'] is True and entry['force_bit_parity'] is True and entry['new_faults']==0,'Source integrity claim failed')
  require(entry['diagnostics']['original_fault_flags']==entry['diagnostics']['new_observer_faults']==entry['diagnostics']['parity_mismatches']==0,'Fault/mismatch claim failed')
  require(entry['parity_proof']['state_checkpoints']==714 and entry['parity_proof']['force_frames']==182400,'Proof cardinality changed')
  post=entry['postprocessor_contract'];require(post['canonical_partition']==[64] and post['alternate_partitions']==[1,3,17,64,129,7] and post['partitions_byte_identical'] is True and post['finite_output_and_final_state'] is True,'Partition/finiteness claim failed')
  require(post['fixed400_operator']==protocol['fixed400_operator'],'Per-case operator changed')
  require(cases[ident]['source_proof']['mechanical_state_bit_parity'] is True and cases[ident]['source_proof']['force_bit_parity'] is True and cases[ident]['source_proof']['new_faults']==0,'Consumer proof differs')
 failed=tuple(c['id'] for c in result['cases'] if not c['passes_all_case_gates'])
 require(failed==FAILED and result['failed_case_ids']==list(FAILED),'Preserved eight failures changed')
 require(summary['pass_count']==26 and summary['fail_count']==8 and [c['id'] for c in summary['all_failures']]==list(FAILED),'Summary counts/failures changed')
 for case in result['cases']:
  flags=case['gates'];require(case['passes_all_case_gates']==all(flags.values()),'Stored decision differs from stored flags')
  if case['id'] in FAILED:require([k for k,v in flags.items() if not v]==['each_early_window_band_MAE'],'Failure category changed')
 require(result['passes_all_preservation_gates'] is False and result['adopted'] is False and result['gain_onset_gate_or_operator_changes'] is False,'Failure/non-adoption scope changed')
 require(summary['C8_weak_H1_and_unassigned_component_diagnostics'][0]['fixed_old_gain']==451.7466016699404,'C8v4 old gain changed')
 require(summary['C8_weak_H1_and_unassigned_component_diagnostics'][1]['fixed_old_gain']==26.889749619113974,'C8v12 old gain changed')
 for path,expected in snapshots:require(digest(path.read_bytes())==expected,'Archive changed during read')
 require(index_path.read_bytes()==initial,'Index changed during read')
 return {'passed':True,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'index_sha256':digest(initial),'published_records_verified':len(snapshots),'producer_source_bindings':27,'preserved_result':{'passed_cases':26,'failed_cases':list(FAILED),'adopted':False},'scope':'Stored source/receipt/hash/chronology/outcome consistency only. No external binaries, PCM or rawproof rows verified; no compilation, rendering, filtering, feature measurement or rescoring.'},(index,mapping,plan,build)

def assemble(destination,context):
 index,mapping,plan,build=context;destination=Path(destination).expanduser().resolve()
 require(not destination.exists() and destination!=ROOT and ROOT not in destination.parents,'Assembly requires a NEW directory outside this checkout')
 destination.mkdir(parents=True);prefix='/workspace/virtual-instrument-keyra/out/full-radiation-crossover/train34/producer/'
 for n,binding in enumerate(index['frozen_source_bindings']):
  data=mapping[(binding['original_path'],binding['sha256'])][1];old=binding['original_path']
  relative=old[len(prefix):] if old.startswith(prefix) else 'provenance/'+str(n)+'-'+Path(old).name
  path=destination/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 commands=[[arg.replace(prefix[:-1],str(destination)) for arg in command] for command in build['commands']]
 require(all(prefix[:-1] not in arg for command in commands for arg in command),'Private compile path remains')
 (destination/'compile-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 (destination/'ASSEMBLED.txt').write_text('Source only. Nothing compiled/rendered. Run compile-commands.json manually with GNU/Clang C++17, then invoke producer NEW_CASE_DIR MIDI VELOCITY. For historical evidence, authenticate the external bundle and keep fixed protocol/controls. Archived orchestration keeps old absolute paths; do not run it as a portable launcher.\n')
 return str(destination)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);parser.add_argument('--assemble',type=Path,help='Copy source only to a NEW external directory; never compile/render.');args=parser.parse_args()
 require(args.output is None or not args.output.exists(),'Preserve old output receipts')
 report,context=check()
 if args.assemble:report['assembled_source_only']=assemble(args.assemble,context)
 text=json.dumps(report,indent=2)+'\n'
 if args.output:args.output.write_text(text)
 print(text,end='')
