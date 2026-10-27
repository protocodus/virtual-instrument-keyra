#!/usr/bin/env python3
"""Snapshot current fused full API and compile pressure0/1 arms without model execution."""
from pathlib import Path
import json,hashlib,shutil,subprocess,datetime,re
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent
COMMIT='863391a5b7cf4112f6dcaa3535339fa6e488efeb'
FILES=['src/full_instrument/FullInstrument.cpp','src/full_instrument/PreparedModel.h','src/full_instrument/PreparedCalibration.h','src/full_instrument/SelectedModel.h','src/full_instrument/MechanismBodyCache.h','src/full_instrument/FreeUnisonFusion.h','include/keyra/FullInstrument.h','include/keyra/physics/ContactSolver.h','include/keyra/physics/MechanismExciter.h','include/keyra/physics/StrikeController.h']
FLAGS=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-fopenmp-simd','-DKEYRA_FULL_FREE_UNISON_SIMD=1','-DKEYRA_FULL_FAST_CONTACT=1','-DKEYRA_FULL_MECHANISM_CACHE=1','-DKEYRA_FULL_MODEL_PROFILE=0']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':str(Path(p).resolve()),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
 if p.exists():raise ValueError('Preserve existing '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,allow_nan=False)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert sha(ROOT/'src/full_instrument/PreparedModel.h')=='325a6eff65c8caffda65ebd803bcc44894a27ca85d2a7e7f018e60efaa29bd80'
assert sha(ROOT/'src/full_instrument/FreeUnisonFusion.h')=='58c56ffdf7981ae4ce15c7e8c950013e0834ed5f1a51fa6eea6ceab870795581'
for name in FILES:
 source=ROOT/name;target=OUT/'sources'/name
 if target.exists():raise ValueError('Snapshot exists '+str(target))
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
manifest=[{'relative_path':name,'original':rec(ROOT/name),'snapshot':rec(OUT/'sources'/name)} for name in FILES]
write(OUT/'source-manifest.json',{'runtime_file_count':len(FILES),'files':manifest})
inputs=[rec(ROOT/name) for name in FILES]+[rec(ROOT/'src/full_instrument/prepared_model_provenance.json'),rec(ROOT/'CMakeLists.txt'),rec(ROOT/'out/full-free-unison-fusion/harness-v2/protocol.json'),rec(ROOT/'out/full-free-unison-fusion/harness-v2/performance-result.json')]
source=OUT/'sources/src/full_instrument/FullInstrument.cpp';builds=[]
for arm,value in [('baseline',0),('candidate',1)]:
 build=OUT/'build'/arm;build.mkdir(parents=True,exist_ok=False)
 flags=[*FLAGS,'-DKEYRA_FULL_PRESSURE_SIMD='+str(value),'-I'+str(OUT/'sources/include')]
 cmd=['g++',*flags,'-fopt-info-vec-all='+str(build/'vectorization.txt'),'-c',str(source),'-o',str(build/'api.o')]
 subprocess.run(cmd,check=True,capture_output=True,text=True)
 symbols=subprocess.check_output(['nm','-u',str(build/'api.o')],text=True);(build/'undefined-symbols.txt').write_text(symbols)
 assert not re.search(r'\b(?:GOMP\w*|omp_\w*|pthread\w*|cuda\w*)\b',symbols)
 builds.append({'arm':arm,'pressure_macro':value,'flags':flags,'command':cmd,'object':rec(build/'api.o'),'actual_API_vectorization_report':rec(build/'vectorization.txt'),'undefined_symbols':rec(build/'undefined-symbols.txt'),'runtime_OMP_or_worker_symbols':False})
header=(OUT/'sources/src/full_instrument/PreparedModel.h').read_text();lines=header.splitlines();pressure=[]
for i,line in enumerate(lines):
 if '#pragma omp simd reduction(+:l,r) simdlen(4)' in line:
  j=i+1
  assert 'for(size_t i=0;i<count;++i)' in lines[j]
  pressure.append({'pragma_line':i+1,'for_line':j+1,'first_body_line':j+2,'body_first_text':lines[j+1].strip()})
assert len(pressure)==2
report=(OUT/'build/candidate/vectorization.txt').read_text();actual_pressure_lines=[line for line in report.splitlines() if 'PreparedModel.h:' in line and 'optimized: loop vectorized' in line and any('PreparedModel.h:'+str(n)+':' in line for row in pressure for n in [row['for_line'],row['first_body_line']])]
assert len(actual_pressure_lines)>=2,actual_pressure_lines
fusion=[line for line in report.splitlines() if 'FreeUnisonFusion.h:' in line and 'optimized: loop vectorized' in line]
assert len([line for line in fusion if '16 byte vectors' in line and 'FreeUnisonFusion.h:38:' in line])==3
# Existing pressure loop float reductions change observer rounding only. The
# per-mode bridge impulse remains a float multiply/add in exactly the old order.
write(OUT/'compile-proof.json',{'at_utc':now(),'builds':builds,'pressure_loop_source_locations':pressure,'actual_pressure_loop_vectorization_lines':actual_pressure_lines,'fused_row_actual_vectorization_lines':fusion,'all_three_fused_N_templates_vectorized':True,'both_existing_pressure_working_loops_vectorized':True,'model_constructed':False,'model_steps':0,'timing_trials':0})
p={'schema_version':1,'frozen_at_utc':now(),'scope':'SOURCEONLY currentfusedbackend pressureSIMDobserver OFFvsON, no newalgorithm/modelsourcechanges or actualmodels. Frozencompilerproofonly; separate rootreview+authorization beforeactualcorrectness andquiettiming.','source_commit':COMMIT,'source_manifest':rec(OUT/'source-manifest.json'),'sources':[rec(OUT/'prepare.py')]+[row['snapshot'] for row in manifest],'inputs':inputs,'flags_common_both_arms':FLAGS,'arm_flags':{'baseline':['-DKEYRA_FULL_PRESSURE_SIMD=0'],'candidate':['-DKEYRA_FULL_PRESSURE_SIMD=1']},'only_build_difference':'Existingpressureobservermacro0versus1. BothsamecurrentOriginalControlpreparedsource/FreeUnisonSIMD1/fastcontact1/mechcache1/profile0/-fopenmp-simd. Nootherflags/FPcoefficient/statechanges.','compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],'compile_proof':rec(OUT/'compile-proof.json'),'model_source_modified':False,'coefficients_changed':False,'new_reassociation_or_fastmath':False,'existing_pressure_reassociation':'Onlyexistingfloatl/robserverreductionsinModes::portImpulseRadiation/radiation useomp simd reduction +simdlen4. Per-mode impulse arithmeticidentical; stringsaddedafterboardinoriginalorder. No globalfastmath/FMA/reassoc orFreeUnisonbodychange.','physical_state_exact_requirements':['q/pallstrings andboard','contactforces/hammer/repetition/controller/RNG/pedals','allmechanismstates/energyledgers/bodycoupling','pre-observationandpost-observationphysicalfields sameframe','allactualeventdiagnostics/faults/no unsafe/nonfinite'],'observer_comparison_policy':'Rawf64pressure/f32audio MAYdifferbyexistingobserverreductionrounding; separatefrozenquantitativeallowances/comparatorrequired inindependentharness. Physicaldeepstate muststayexact; observerpayloadstrictidentitynotanappropriateacceptancegate.','all_current_runtime_dependencies':'10runtimefiles includingnewFreeUnisonhelper,SelectedModel,MechanismBodyCache andallfacade/physics headers; no profile1selected.','planned_validation':'Independentharnessadaptsv2currentAPI4rates×4cases including5deepcheckpoints; physical/observerboundary separatelyqualified. Fresh6timinggroups48/96k×music/repeats/dense3pairs, alltrialsretainedaftercorrectness.','historical_caution':'EarlierpressureSIMD48krepetitionregressed12.2%beforethisfusedbackend; retainedasnegativeevidence, not erasedorusedasfreshcurrentbaseline. No newCPUorreal-timeclaimfromvectorization.','adopted':False,'actual_model_constructed':False,'actual_model_steps':0,'actual_benchmarks':0,'public_runtime_or_default_changes':False}
write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'protocol':rec(OUT/'protocol.json'),'sources':p['sources'],'inputs':p['inputs'],'compile_proof':p['compile_proof'],'no_actual_model_execution':True})
print(json.dumps({'protocol':rec(OUT/'protocol.json'),'compile_proof':rec(OUT/'compile-proof.json'),'pressure_loop_vectorization_lines':actual_pressure_lines,'fused_all3_N_vectorized':True,'actual_models':0},indent=2))
