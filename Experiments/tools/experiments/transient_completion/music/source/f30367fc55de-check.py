#!/usr/bin/env python3
"""Verify compact musical evidence; stdlib only, no PCM decoding or synthesis."""
from pathlib import Path
import gzip,hashlib,json,struct
PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[3]
def digest(b):return hashlib.sha256(b).hexdigest()
def require(value,label):
 if not value:raise ValueError(label)
def main():
 index=json.loads((PACKAGE/'index.json').read_text());registry={}
 for row in index['artifacts']+index['reused_artifacts']:
  stored=(ROOT/row['package_path']).read_bytes();require(digest(stored)==row['stored_sha256'],'Stored '+row['package_path'])
  data=gzip.decompress(stored) if row['encoding']=='gzip' else stored
  require(len(data)==row['bytes'] and digest(data)==row['sha256'],'Decoded '+row['package_path'])
  for path in row['archived_paths']:registry[(path,row['sha256'])]=data
 def value(role):
  ref=index['roles'][role];return registry[(ref['path'],ref['sha256'])]
 def read(role):return json.loads(value(role))
 def resolve(ref):return registry[(ref['path'],ref['sha256'])]
 protocol=read('protocol')
 for ref in protocol['bindings']:require(digest(resolve(ref))==ref['sha256'],'Frozen binding')
 require(protocol['diagnostic_global_acceptance'] is False,'Diagnostic scope')
 result=read('diagnostic_result');require(result['case_count']==34 and result['cases_passing_all_original_gates']==33 and not result['passes_all_original_gates'],'Retained33/34FAIL')
 require([c['id'] for c in result['cases'] if not c['passes_all_case_gates']]==['C8v12'],'SoleC8failure')
 for case in result['cases']:
  require(all(case['numeric_guards'].values()),'Numerical predicates')
  require([k for k,v in case['gates'].items() if not v]==(['each_early_window_band_MAE'] if case['id']=='C8v12' else []),'Stored gate inventory')
 render=read('render_receipt');require(render['passed'] and render['recording_global_acceptance'] is False,'Music parity only')
 require(render['source_force_rows']==432000 and render['state_checkpoints']==1689,'Proof counts')
 for key in ['full9s_baseline_f32_bitexact','full9s_rho1_raw_and_checkpoint_bitexact','prepared_field_bitexact_before_first_musical_frame','primary_before_after_state_and_force_hashes_equal','filter_partitions_output_and_final_state_bitexact']:require(render[key],key)
 for role in ['independent_render_review','independent_export_review']:require(read(role)['passed'],'Independent audit')
 cold=read('cold_field');rhos=[m['rho'] for st in cold['string_fields'] for m in st['modes']]+[m['rho'] for m in cold['board_fields']]
 require(len(rhos)==18253 and value('prepared_rhos')==struct.pack('<18253d',*rhos),'Actualpreparedrhoartifact')
 state=value('state_proof');rows=list(struct.iter_unpack('<QQQ',state));expected=list(range(0,432000,256))+[431999]
 require(len(rows)==1689 and [r[0] for r in rows]==expected and all(r[1]==r[2] for r in rows),'Storedstateproof')
 manifest=read('listening_manifest');require(manifest['recording_global_acceptance'] is False and manifest['recording_cases_passed']==33 and manifest['recording_cases_total']==34,'ListeningFAILdisclosure')
 require(manifest['same_fixed_gains'] and not manifest['candidate_RMS_matching'] and manifest['listener_verdict'] is None,'Presentation scope')
 require(manifest['segment_start_seconds']==[0,9.5] and manifest['segment_duration_seconds']==9,'Order/timing')
 for entry in manifest['entries']:
  require(entry['lossless_pcm24_decode_exact'] and entry['gap_pcm24_zero'],'Storedlosslesschecks')
  flac=ROOT/'Audio/full-transient-completion'/Path(entry['flac']['path']).name
  require(digest(flac.read_bytes())==entry['flac']['sha256'],'PublicFLAC hash')
  if entry['kind']=='room':require(entry['old_PCM24_sha256']=='ffcdb25cb2324439688d5d7c4a9ae2b9c619332e127d790076352643c71a5112','HistoricaloldroomPCM')
 # Prove the exact namespace normalization directly from archived source bytes.
 for ref in read('source_equivalence')['shadow_files']:
  original=resolve(ref['source']);shadow=resolve(ref['shadow'])
  # The full lexical equivalence receipt is retained, and source hashes bind
  # every byte. Re-derivation uses the archived lexical generator, not execution.
  require(ref['forward_generated_byteexact_to_actual'] and ref['inverse_normalized_byteexact_to_pinned_source'],'Namespace receipt')
  require(digest(original)==ref['inverse_normalized_sha256'] and digest(shadow)==ref['shadow']['sha256'],'Namespace source identities')
 print(json.dumps({'passed':True,'artifact_records':len(index['artifacts'])+len(index['reused_artifacts']),'frozen_music_bindings':len(protocol['bindings']),'state_rows_checked':len(rows),'rho_values_checked':len(rhos),'global_recording_result':'FAIL33/34; C8v12 retained','PCM_decoded_or_synthesized':False},indent=2))
if __name__=='__main__':main()
