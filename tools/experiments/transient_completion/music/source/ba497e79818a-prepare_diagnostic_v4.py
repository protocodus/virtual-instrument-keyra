from pathlib import Path
import shutil,json,hashlib,datetime,py_compile
BASE=Path(__file__).resolve().parent;SRC=BASE/'v3';OUT=BASE/'v4';ROOT=BASE.parents[1]
if OUT.exists():raise ValueError('Preserve existing v4')
shutil.copytree(SRC,OUT)
# Retain inherited source-only preparation history without suggesting it froze v4.
for name in ['source-preparation.json','source-review.json','review-notes.json','protocol.json','freeze_sources.py']:
 p=OUT/name
 if p.exists():p.rename(OUT/('historical-v3-'+name))
def once(s,a,b):
 if s.count(a)!=1:raise ValueError(a[:80])
 return s.replace(a,b)
p=OUT/'run.py';s=p.read_text()
a=""" if confirmation['protocol']!=protocol['confirmation_protocol']:raise ValueError('Wrong confirmation family')
 assert confirmation['case_count']==confirmation['cases_passing_all_original_gates']==34 and confirmation['passes_all_original_gates']
 assert len(confirmation['cases'])==34 and all(c['passes_all_case_gates'] and all(c['numeric_guards'].values()) for c in confirmation['cases'])
"""
b=""" if confirmation['protocol']!=protocol['confirmation_protocol']:raise ValueError('Wrong confirmation family')
 # An explicitly rejected global candidate is rendered only for diagnosis on
 # the already observed musical score. Preserve the sole C8 failure verbatim.
 known=protocol['diagnostic_result']
 if auth['confirmation_result']['sha256']!=known['sha256'] or Path(auth['confirmation_result']['path']).resolve()!=Path(known['path']).resolve():raise ValueError('Wrong fixed diagnostic result')
 assert confirmation['case_count']==34 and confirmation['cases_passing_all_original_gates']==33 and not confirmation['passes_all_original_gates']
 assert len(confirmation['cases'])==34 and [c['id'] for c in confirmation['cases'] if not c['passes_all_case_gates']]==['C8v12']
 for case in confirmation['cases']:
  assert all(case['numeric_guards'].values())
  failed=[k for k,v in case['gates'].items() if not v]
  assert failed==(['each_early_window_band_MAE'] if case['id']=='C8v12' else [])
  for gate in ['late_harmonic_MAE','late_envelope_MAE','late_RMS_drift','stereo_LR_shift','mono_energy_shift']:assert case['gates'][gate]
"""
s=once(s,a,b)
s=once(s,"receipt={'passed':True,", "receipt={'passed':True,'musical_numeric_and_parity_only':True,'recording_global_acceptance':False,'recording_cases_passed':33,'recording_cases_total':34,'failed_recording_cases':['C8v12'],")
p.write_text(s)
p=OUT/'export.py';s=p.read_text();s=once(s,"'status':'PRIVATE diagnostic on observed score; no promotion or listener verdict'","'status':'EXPERIMENTAL DIAGNOSTIC; recording GLOBALFAIL33/34, C8v12earlyguard failed; no promotion or listener verdict'")
s=once(s,"'same_fixed_gains':True,","'recording_global_acceptance':False,'recording_cases_passed':33,'recording_cases_total':34,'failed_recording_cases':['C8v12'],'same_fixed_gains':True,")
p.write_text(s)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,bytes=True):
 p=Path(p).resolve();x={'path':str(p),'sha256':sha(p)}
 if bytes:x['bytes']=p.stat().st_size
 return x
for p in [OUT/'run.py',OUT/'export.py']:py_compile.compile(str(p),cfile='/tmp/keyra-music-v4-'+p.stem+'.pyc',doraise=True)
# The DSP and event driver are exactly identical to v3; only admission/reporting
# guard source and filesystem include paths change for this separate diagnostic.
unchanged=[OUT/'PitchMemoryCompanion.h',OUT/'ShadowMechanics.h',OUT/'filter.cpp',OUT/'music.cpp',*sorted((OUT/'sources').rglob('*')),*sorted((OUT/'shadow').rglob('*'))]
unchanged=[p for p in unchanged if p.is_file()]
for p in unchanged:assert p.read_bytes()==(SRC/p.relative_to(OUT)).read_bytes()
known=ROOT/'out/full-transient-completion/modal-train34/result.json'
assert sha(known)=='73fe50903aa4c0d9984d482d14afbf8328943d39cfa5b2a0577746f0c0ad7a6f'
original=json.loads((SRC/'protocol.json').read_text());protocol=dict(original)
protocol['frozen_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
protocol['scope']='EXPERIMENTAL DIAGNOSTIC ONLY: fixed rejected33/34modal transient candidate on observed9s score, not global acceptance or default promotion. Sourcefreeze only; separate root authorization required for ONErender and separatelyexport.'
protocol['strict_v3_protocol_preserved_unrun']=rec(SRC/'protocol.json')
protocol['diagnostic_result']=rec(known)
protocol['confirmation_requirement']='Exactfixed73fe5090… result,34cases33pass,soleC8v12each_early_window_band_MAEfailure; allnumerical andlateRMS/harmonic/envelope/stereo/monoguardspass. Do not relax or relabel originalglobalfailure.'
protocol['declaration_why_new_protocol']='Root explicitly stopped tuning before musical listening. Although globalacceptance failed, C3click improvement and first5/late preservation justify an experimentalcomparison on the observed score. No newfit, law, parameter, referencePCM or acceptance threshold; strictv3remainsunrun.'
protocol['diagnostic_global_acceptance']=False
protocol['build_flags']=[x.replace(str(SRC),str(OUT)) for x in original['build_flags']]
protocol['limitations']=['GLOBALFAIL retained:33/34recordingguards pass; C8v12 5–20ms bandMAE worsens1.1429885386924123dB against1dBbudget. No acceptance, promotion, listenerverdict or retuning.']+original['limitations']
protocol['authorization_schema']['render']['confirmation_result']={'path':str(known),'sha256':sha(known)}
protocol['authorization_schema']['export']['render_receipt']['path']=str(OUT/'render/receipt.json')
receipt={'at_utc':protocol['frozen_at_utc'],'v3_protocol':rec(SRC/'protocol.json'),'generator':rec(__file__),'scope':'SOURCEONLY diagnostic guard branch, no actualmodel or exportauthorization','dsp_and_event_driver_byteexact_to_v3':[rec(p) for p in unchanged],'only_new_python_semantics':['Permit exactknownrejected33/34result for oneexperimentaldiagnostic','Preservefailureinventoryinrenderreceiptandlisteningmanifest'],'new_model_steps':0,'new_audio_or_recording_access':False}
(OUT/'diagnostic-preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [Path(x['path']) for x in original['bindings'] if not Path(x['path']).is_relative_to(SRC)]
paths += [SRC/'protocol.json',known,BASE/'prepare_diagnostic_v4.py',ROOT/'out/full-transient-music-audit/v3/source-equivalence.json']
protocol['bindings']=[rec(p) for p in sorted(set(paths))]
(OUT/'protocol.json').write_text(json.dumps(protocol,indent=2,allow_nan=False)+'\n')
print(json.dumps({'protocol':rec(OUT/'protocol.json'),'bindings':len(protocol['bindings']),'source_only':True},indent=2))
