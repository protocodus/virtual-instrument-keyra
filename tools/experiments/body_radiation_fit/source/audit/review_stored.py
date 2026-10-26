from pathlib import Path
import json,hashlib,math,datetime,collections,importlib.util
R=Path('/workspace/virtual-instrument-keyra');P=R/'out/full-body-fit/v2';O=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest();j=lambda x:json.loads(Path(x).read_text())
r=j(P/'result.json');f=j(P/'fit-result.json');p=j(P/'protocol.json');z=j(P/'freeze.json');m=j(P/'manifest.json');old=j(R/'out/full-radiation-crossover/train34/reference-control.json');refs={c['id']:c for c in old['cases']};g=j(P/'gram-receipt.json')
assert r['protocol']==z['protocol'] and r['fit_result']['sha256']==sha(P/'fit-result.json') and r['gram_receipt']['sha256']==sha(P/'gram-receipt.json');assert sha(P/'protocol.json')==z['protocol']['sha256']
for q in p['sources']+p['inputs']:assert sha(q['path'])==q['sha256'],q['path']
manifest_bytes=0;exceptions=[]
for rel,q in m.items():
 x=P/rel
 if rel=='run.log':
  data=x.read_bytes();assert len(data)>q['bytes'];assert hashlib.sha256(data[:q['bytes']]).hexdigest()==q['sha256']
  suffix=json.loads(data[q['bytes']:].decode());expected={k:v for k,v in r.items() if k not in ['cases','limits']};assert suffix==expected
  exceptions.append({'path':rel,'original_manifest':q,'current_bytes':len(data),'current_sha256':sha(x),'original_prefix_sha256_matches':True,'appended_final_summary_matches_result':True,'reason':'Manifest hashes tee log before finalprint appends summary; original manifest preserved, no result/source/audio changed.'})
 else:assert x.stat().st_size==q['bytes'] and sha(x)==q['sha256'],rel
 manifest_bytes+=q['bytes']
for c in p['cases']:assert sha(c['basis']['path'])==c['basis']['sha256']
assert len(r['cases'])==r['case_count']==34 and set(c['id'] for c in r['cases'])==set(refs)
assert f['success'] and f['iterations']==13 and f['evaluations']==len(f['trace'])==14 and f['fit_count']==32 and f['same_alpha_all34'];assert f['excluded_fit_cases']==['C8v4','C8v12']
assert [t['evaluation'] for t in f['trace']]==list(range(14))
assert all(abs(a-10**(t/20))<1e-14 for a,t in zip(f['alpha'],f['theta_dB'])) and all(.025<=a<=40 for a in f['alpha'])
assert not r['passed'] and not r['passes_all_preservation_gates'] and r['final_forecast_checks_pass'] and r['optimizer_converged'] and r['adopted'] is False
assert r['physical_synthesis_runs']==0 and r['reference_PCM_opened'] is False
spec=importlib.util.spec_from_file_location('private_fit_audit_only',P/'fit.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);metric,helper,gate,gate_sha=mod.tools();assert gate_sha==p['gate_arithmetic_sha256']
failed=collections.Counter();fitids=[];forecast_double=[];forecast_float=[];psd=[]
for c in r['cases']:
 ident=c['id'];prev=refs[ident];features=c['candidate'];proof=c['source_proof']
 assert c['used_in_fit'] is (not ident.startswith('C8'));assert not c['passes_all_case_gates'];assert c['historical_proof_lineage']==('original_six_producer_receipt' if ident in ['C3v4','C3v12','C4v4','C4v12','C6v4','C6v12'] else 'full_train34_history')
 assert features['fixed_onset_frame']==prev['baseline']['fixed_onset_frame'] and features['fixed_gain']==prev['baseline']['fixed_gain']
 assert [q['window_seconds'] for q in features['late_harmonics']]==prev['support']['late_windows_seconds']
 assert features['late_envelope']['times_seconds']==prev['reference']['late_envelope']['times_seconds'] and features['late_envelope']['included']==prev['reference']['late_envelope']['included']
 assert proof['mechanical_state_bit_parity'] is True and proof['force_bit_parity'] is True and proof['new_faults']==0
 score=gate(prev,features,ident,True,{ident:proof});assert score['changes']==c['changes'] and score['gates']==c['gates'] and score['passes_all_case_gates']==c['passes_all_case_gates']
 for k,v in c['gates'].items():
  if not v:failed[k]+=1
 assert c['final_double_gram_forecast']['pass'] and c['final_float32_gram_forecast']['pass'];assert c['final_double_gram_forecast']['test_alpha']==f['alpha']==c['final_float32_gram_forecast']['alpha']
 forecast_double+=list(c['final_double_gram_forecast']['coherent_feature_checks'].values());forecast_float+=list(c['final_float32_gram_forecast']['checks'].values());psd+=c['final_double_gram_forecast']['psd']
 if c['used_in_fit']:fitids.append(ident)
assert len(fitids)==32 and len(r['failed_case_ids'])==34 and len(g['all34_direct_parity'])==34 and all(c['pass'] for c in g['all34_direct_parity'])
assert all(c['pass'] for c in forecast_double+forecast_float+psd)
mean=lambda x:sum(x)/len(x);aggregates={}
for key,ids in [('fit32',set(fitids)),('all34',set(refs))]:
 cs=[c for c in r['cases'] if c['id'] in ids];agg={}
 for name,fn in [('early_five_band_MAE_db',lambda v:mean([w['five_band_MAE_db'] for w in v['early']])),('late_harmonic_MAE_db',lambda v:v['late_harmonic_MAE_db']),('late_envelope_MAE_db',lambda v:v['late_envelope']['MAE_db'])]:
  a=mean([fn(refs[c['id']]['baseline']) for c in cs]);bb=mean([fn(c['candidate']) for c in cs]);agg[name]={'old_final':a,'new_body_only':bb,'change':bb-a}
 aggregates[key]=agg
c3={c['id']:{k:c['changes'][k] for k in ['first5_positive_excess_reduction_db','ring5_20_positive_excess_reduction_db','late_RMS_db']} for c in r['cases'] if c['id'].startswith('C3')}
report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent storedJSON + artifactHASH + unchangedgate arithmetic review only. No audio/PCM numericaldecode, feature/Gram recomputation, optimizer rerun, physicalsynthesis or canonicaledit.','decision':'NumericalPASS; acousticFAIL0of34; rejectcandidate/defaultunchanged','review_source_sha256':sha(__file__),'reviewed_sha256':{x:sha(P/x) for x in ['fit.py','protocol.json','freeze.json','result.json','fit-result.json','gram-receipt.json','manifest.json']},'verified_manifest_files':len(m)-len(exceptions),'verified_manifest_bytes':manifest_bytes,'manifest_append_only_log_exception':exceptions,'one_solve':{'iterations':f['iterations'],'evaluations':f['evaluations'],'trace_entries':len(f['trace']),'converged':True,'alpha':f['alpha'],'theta_dB':f['theta_dB'],'same_alpha_all34':True,'fit_count':32,'excluded_fit_only':['C8v4','C8v12']},'case_count':34,'preservation_pass_count':0,'preservation_failed_gate_counts':dict(failed),'zero_new_numerical_faults':True,'historical_physical_fault_proof':'Original6producer and28fullTRAIN34 collectiontime true/true/0. Not independentlyrerendered or nativepluginqualification.','all34_direct_fixed_gain_onset_support_masks':True,'all34_exact_original_gate_arithmetic_rechecked':True,'all34_final_double_float32_forecast_checks_pass':True,'max_double_forecast_error_over_bound':max(c['maximum_error_over_bound'] for c in forecast_double),'max_float32_forecast_error_over_bound':max(c['maximum_error_over_bound'] for c in forecast_float),'max_psd_negative_error_over_bound':max(c['negative_eigenvalue_over_bound'] for c in psd),'old_final_vs_new_body_only_aggregates':aggregates,'C3_click_changes':c3,'wall_seconds':r['wall_seconds'],'adopted':False,'limits':['Improvementrelativealpha1uncalibratedbodyobjective is NOT improvementrelativeoldfinalbaseline.','Earlybandmeanimproves, butlateharmonic/envelope fidelityworsenandall34RMSguardsfail.','C3first5broadexcessdropsbut5–20msringworsensbothlayers; noauditionclaim.','Localnonconvexsinglefitfailure doesnotproveallbody-onlyweightsgloballyinfeasible.','All34previouslyobservedTRAIN; noholdoutgeneralization/realtime/SDKproof.']}
(O/'post-run-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'report_sha256':sha(O/'post-run-review.json'),'manifest_files':len(m),'unmodified_verified_files':len(m)-len(exceptions),'gates':dict(failed),'aggregates':aggregates,'C3':c3,'max_double_forecast':report['max_double_forecast_error_over_bound'],'max_f32forecast':report['max_float32_forecast_error_over_bound']},indent=2))
