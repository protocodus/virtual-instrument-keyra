#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,datetime,math,statistics
ROOT=Path('/workspace/virtual-instrument-keyra')
OUT=ROOT/'out/full-transient-completion/modal-train34'
AUDIT=ROOT/'out/full-transient-completion-audit/modal-train34'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p)}
j=read(OUT/'result.json');p=read(OUT/'protocol.json');m=read(OUT/'manifest.json')
bad=[]
for rel,v in m.items():
 f=OUT/rel
 if sha(f)!=v['sha256'] or f.stat().st_size!=v['bytes']:bad.append(rel)
if bad:raise ValueError('Manifest failed'+str(bad))
for x in p['sources']+p['inputs']:
 if sha(Path(x['path']))!=x['sha256']:raise ValueError('Frozen input changed'+x['path'])
refs={c['id']:c for c in read(ROOT/'out/full-radiation-crossover/train34/reference-control.json')['cases']}
pilot={c['id']:c for c in read(ROOT/'out/full-transient-completion/modal-scaled-v1/result.json')['cases']}
for c in j['cases']:
 if c['id'] in pilot and c!=pilot[c['id']]:raise ValueError('Pilot reuse changed'+c['id'])
if sha(OUT/'renders/bound-and-gamma.json')!=sha(ROOT/'out/full-transient-completion/modal-scaled-v1/renders/bound-and-gamma.json'):raise ValueError('Cold field mismatch')
if not all(all(c['numeric_guards'].values()) for c in j['cases']):raise ValueError('Numerical guard failure')
aggregates={}
for name,cases in [('all34',j['cases']),('non_C8_32',[c for c in j['cases'] if not c['id'].startswith('C8')])]:
 def mean(values):return statistics.mean(values)
 old=[refs[c['id']]['baseline'] for c in cases];new=[c['candidate'] for c in cases]
 metrics={}
 for label,fn in [('early_pooled_four_window_five_band_MAE_db',lambda x:mean([w['five_band_MAE_db'] for w in x['early']])),('late_harmonic_MAE_db',lambda x:x['late_harmonic_MAE_db']),('late_envelope_MAE_db',lambda x:x['late_envelope']['MAE_db'])]:
  a,b=mean(map(fn,old)),mean(map(fn,new));metrics[label]={'old':a,'candidate':b,'candidate_minus_old':b-a}
 metrics['early_windows']=[{'window_seconds':old[0]['early'][i]['window_seconds'],'old_mean_MAE_db':mean(x['early'][i]['five_band_MAE_db'] for x in old),'candidate_mean_MAE_db':mean(x['early'][i]['five_band_MAE_db'] for x in new),'improved_cases':sum(b['early'][i]['five_band_MAE_db']<a['early'][i]['five_band_MAE_db'] for a,b in zip(old,new)),'worsened_cases':sum(b['early'][i]['five_band_MAE_db']>a['early'][i]['five_band_MAE_db'] for a,b in zip(old,new))} for i in range(4)]
 aggregates[name]={'case_count':len(cases),'case_and_window_weighting':'Uniform cases; uniform four early windows, each window equally weights five frozen bands. No fresh-data claim.',**metrics}
stereo={}
for region in ['sustain','whole_note','early_0','early_1','early_2','early_3']:
 stereo[region]={}
 for metric in ['LR_db','mono_energy_db']:
  pairs=[(c['id'],c['changes']['stereo'][region][metric]) for c in j['cases']]
  lo=min(pairs,key=lambda x:x[1]);hi=max(pairs,key=lambda x:x[1]);stereo[region][metric]={'min':{'id':lo[0],'change_db':lo[1]},'max':{'id':hi[0],'change_db':hi[1]}}
c8=[]
for c in j['cases']:
 if not c['id'].startswith('C8'):continue
 old=refs[c['id']]['baseline'];new=c['candidate']
 c8.append({'id':c['id'],'pass':c['passes_all_case_gates'],'failed_gates':[k for k,v in c['gates'].items() if not v],'windows':[{'window_seconds':a['window_seconds'],'old_five_band_MAE_db':a['five_band_MAE_db'],'candidate_five_band_MAE_db':b['five_band_MAE_db'],'change_db':b['five_band_MAE_db']-a['five_band_MAE_db'],'old_band_signed_errors_db':a['band_signed_errors_db'],'candidate_band_signed_errors_db':b['band_signed_errors_db'],'old_broad_signed_error_db':a['broad_signed_error_db'],'candidate_broad_signed_error_db':b['broad_signed_error_db']} for a,b in zip(old['early'],new['early'])],'support':c['support'],'changes':c['changes']})
summary={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':rec(OUT/'result.json'),'manifest':rec(OUT/'manifest.json'),'protocol':rec(OUT/'protocol.json'),'manifest_records_checked':len(m),'manifest_bad':bad,'source_input_bindings_checked':len(p['sources'])+len(p['inputs']),'six_modal_pilot_objects_exact':True,'cold_field_exact':True,'cases_passing':sum(c['passes_all_case_gates'] for c in j['cases']),'case_count':len(j['cases']),'failed_cases':[{'id':c['id'],'failed_gates':[k for k,v in c['gates'].items() if not v]} for c in j['cases'] if not c['passes_all_case_gates']],'all_numeric_guards_pass':True,'wall_seconds':j['wall_seconds'],'aggregates_paired_recording_errors':aggregates,'stereo_changes':stereo,'max_absolute_late_RMS_drift_db':max(abs(c['changes']['late_RMS_db']) for c in j['cases']),'C8':c8,'scope':'Posthoc already observed TRAIN, old five-anchor48k/mechanics0/human0/repetition-bypassed. Full companion is offline proof, no runtime/default/realtime/generalization/physical-part assignment claim.'}
path=AUDIT/'post-run-summary.json';path.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'summary':rec(path),'result':summary['result'],'manifest_records_checked':len(m),'cases_passing':summary['cases_passing'],'failed_cases':summary['failed_cases'],'aggregates':aggregates},indent=2))
