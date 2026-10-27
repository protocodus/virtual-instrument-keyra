#!/usr/bin/env python3
"""Stdlib verification of stored pressure-SIMD evidence; no PCM or DSP rerun.

Numerical guards are recomputed from retained measured powers/statistics. This
does not repeat the FFT or independently measure omitted sample payloads.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import math
import re
import statistics

PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[2]
spec=importlib.util.spec_from_file_location('trusted_fusion_checks',ROOT/'tools/experiments/free_unison_fusion/check.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
reader=base.reader;require=base.require;equal=base.equal_values
ARMS=base.ARMS;CASES=base.CASES;ORDERS=base.ORDERS


def ratio_db(new,old):
    if old<=0:return None,'both_zero' if new==0 else 'old_zero'
    if new<=0:return None,'new_zero'
    return 10*(math.log10(new)-math.log10(old)),'defined'


def frozen_bytes(a,p,path):
    records=[r for r in p['bindings'] if r['path']==path]
    require(len(records)==1,'Unique source binding '+path)
    return a.resolve(path,records[0]['sha256'])


def check_quality(q,recipe,rate,frames):
    require(reader.finite_tree(q) and q['metrics']['sample_rate']==rate and q['metrics']['frames']==frames,'Finite stored quality inventory')
    m=q['metrics'];windows=m['windows'];require(len(windows)==4,'All four windows retained')
    boundaries=[(0,frames),(0,min(frames,round(.05*rate))),(min(frames,round(.05*rate)),min(frames,round(.20*rate))),(min(frames,round(.20*rate)),frames)]
    names=('whole','0_to_50ms','50_to_200ms','200ms_to_end');whole=windows[0]['old_power'];empty=0
    floor_factor=recipe['relative_power_floor']
    for w,name,(start,end) in zip(windows,names,boundaries):
        require((w['name'],w['start_frame'],w['end_frame'],w['frames'],w['empty'])==(name,start,end,end-start,start==end),'Fixed complete-window support')
        empty+=int(w['empty']);old,new,error=w['old_power'],w['new_power'],w['error_power']
        require(min(old,new,error,w['old_peak'],w['maximum_absolute_error'])>=0,'Nonnegative measured powers/errors')
        for key,power in (('old_rms',old),('new_rms',new),('error_rms',error)):equal(w[key],math.sqrt(power),'Stored RMS from power')
        null,status=ratio_db(error,old)
        if error==0:status='exact_zero_error' if old>0 else 'both_zero'
        equal(w['null_rms_db'],null,'Null dB arithmetic');require(w['null_rms_status']==status,'No fake null infinities')
        stereo=[w['old_stereo'],w['new_stereo']]
        for s,power in zip(stereo,(old,new)):
            require(len(s['channel_power'])==len(s['variance'])==2 and min(*s['channel_power'],*s['variance'],s['mono_power'])>=0,'Stored stereo powers')
            equal(sum(s['channel_power'])/2,power,'Stereo average power')
            lr,lr_status=ratio_db(*s['channel_power'])
            if lr is None:lr_status='both_channels_zero' if not any(s['channel_power']) else 'left_channel_zero' if s['channel_power'][0]==0 else 'right_channel_zero'
            equal(s['LR_db'],lr,'Stored L/R arithmetic');require(s['LR_status']==lr_status,'Defined L/R status')
            defined=all(v>0 for v in s['variance']);require((s['correlation'] is not None)==defined,'Zero-variance correlation handling')
            require(s['correlation_status']==('defined' if defined else 'zero_variance'),'Correlation status')
            if defined:require(abs(s['correlation'])<=1,'Correlation range')
        a,b=stereo;floor=old*floor_factor;equal(w['baseline_window_power_floor'],floor,'Window power floor')
        masks={'relative_null':old>0 and old>=whole*floor_factor,
               'LR':old>0 and all(p>0 and p>=floor for p in a['channel_power']),
               'correlation':old>0 and all(p>0 and p>=floor for p in a['variance']),
               'mono':a['mono_power']>0 and a['mono_power']>=floor}
        require(w['masks']==masks,'All baseline masks recomputed')
        lr=b['LR_db']-a['LR_db'] if a['LR_db'] is not None and b['LR_db'] is not None else None
        corr=b['correlation']-a['correlation'] if a['correlation'] is not None and b['correlation'] is not None else None
        mono,mono_status=ratio_db(b['mono_power'],a['mono_power'])
        for key,value in (('LR_shift_db',lr),('correlation_shift',corr),('mono_shift_db',mono)):equal(w[key],value,'Stereo change arithmetic')
        require(w['mono_shift_status']==mono_status,'Mono zero-power status')
        limit=recipe['maximum_absolute_error_factor']*(1+w['old_peak']);equal(w['absolute_error_limit'],limit,'Absolute error bound')
        gates={'absolute_error':w['maximum_absolute_error']<=limit,
               'relative_null':not masks['relative_null'] or error<=old*10**(recipe['maximum_null_rms_db']/10),
               'LR':not masks['LR'] or lr is not None and abs(lr)<=recipe['maximum_LR_shift_db'],
               'correlation':not masks['correlation'] or corr is not None and abs(corr)<=recipe['maximum_correlation_shift'],
               'mono':not masks['mono'] or mono is not None and abs(mono)<=recipe['maximum_mono_shift_db']}
        require(w['gates']==gates and w['pass'] is all(gates.values()),'Stored window gates recomputed')
    spectrum=m['spectrum'];bands=spectrum['bands'];require(len(bands)==7 and spectrum['normalization']==recipe['FFT_normalization'],'All seven fixed Hann bands')
    total=spectrum['old_total_power'];threshold=total*floor_factor;equal(spectrum['baseline_power_floor'],threshold,'Band power floor')
    edges=[*recipe['band_edges_hz'],rate/2];strong=0
    for i,row in enumerate(bands):
        require(row['index']==i and row['hz']==edges[i:i+2] and row['upper_inclusive'] is (i==6),'All-frequency band support')
        old,new,error=row['old_power'],row['new_power'],row['error_power'];require(min(old,new,error)>=0,'Finite nonnegative spectral powers')
        shift,status=ratio_db(new,old);null,null_status=ratio_db(error,old)
        if error==0 and old>0:null_status='exact_zero_error'
        for key,value in (('shift_db',shift),('null_rms_db',null),('error_rms',math.sqrt(error)),('signed_power_change',new-old),('absolute_power_change',abs(new-old))):equal(row[key],value,'Stored band arithmetic')
        require(row['shift_status']==status and row['null_rms_status']==null_status,'Weak/zero bands retained without fake dB')
        mask=total>0 and old>=threshold;passed=not mask or shift is not None and abs(shift)<=recipe['maximum_band_shift_db']
        require(row['baseline_power_mask'] is mask and row['gate_applied'] is mask and row['pass'] is passed,'Recomputed band mask/gate')
        strong+=int(mask)
    require(sum(r['bins'] for r in bands)==frames//2+1,'Every rFFT bin retained')
    for field,total_field in (('old_power','old_total_power'),('new_power','new_total_power'),('error_power','error_total_power')):equal(sum(r[field] for r in bands),spectrum[total_field],'All-band spectral sum')
    require(spectrum['pass'] is all(r['pass'] for r in bands),'Spectral family decision')
    silent=m['baseline_wholly_zero'];silent_exact=not silent or all(w['new_power']==0 and w['maximum_absolute_error']==0 for w in windows)
    gates={'finite_samples':True,'silent_baseline_exact':silent_exact,'window_comparisons':all(w['pass'] for w in windows),'all_spectral_bands':spectrum['pass']}
    require(q['gates']==gates and q['pass'] is all(gates.values()) and q['pass'] is True,'All stored numerical engineering gates pass')
    return {'windows':4,'bands':7,'strong':strong,'weak':7-strong,'empty':empty}


def timing(a,study,result,review,p,recipe):
    require(p['performance']['pairs']==[list(r) for r in ORDERS] and p['performance']['discard_warmup_trials'] is False,'Same frozen timing order/no discarded warmup')
    runs=result['runs'];wanted=[(rate,pair,arm) for rate in (48000,96000) for pair,order in enumerate(ORDERS) for arm in order]
    require([(r['sample_rate'],r['pair'],r['variant']) for r in runs]==wanted,'All AB/BA/AB trials retained in order')
    rows={};count=0;maximum_wall=maximum_cpu=0.;misses=0
    for run in runs:
        raw=reader.json_data(a.resolve(run['trace']['path'],run['trace']['sha256']));require(raw['cases']==run['cases'] and raw['sample_rate']==run['sample_rate'],'Full raw timing trace retained')
        for c in run['cases']:
            rate=run['sample_rate'];frames=30720 if c['name'] in CASES[:2] else 15360;cpu=c['callback_thread_cpu_seconds'];wall=c['callback_wall_seconds']
            require(c['frames']==frames and len(cpu)==len(wall)==len(c['events_per_callback'])==frames//64,'All64frame clocks retained')
            require(all(math.isfinite(x) and x>=0 for x in cpu+wall),'Finite raw clocks')
            equal(c['audio_seconds'],frames/rate,'Audio duration');equal(c['callback_cpu_seconds'],sum(cpu),'CPU sum');equal(c['cpu_seconds_per_audio_second'],sum(cpu)/(frames/rate),'CPU/audio')
            for name,values in (('cpu',cpu),('wall',wall)):
                for suffix,fraction in (('p50',.5),('p95',.95)):equal(c[f'callback_{name}_{suffix}'],base.percentile(values,fraction),'Ceil-index quantile')
                equal(c[f'callback_{name}_max'],max(values),'Observed maximum retained')
            require(c['wall_deadline_misses']==sum(x>64/rate for x in wall) and c['faults']==c['unsafe_launches']==0,'Deadline/fault records')
            rows[(rate,c['name'],run['pair'],run['variant'])]=c;count+=len(cpu);misses+=c['wall_deadline_misses'];maximum_wall=max(maximum_wall,max(wall));maximum_cpu=max(maximum_cpu,max(cpu))
    require(len(rows)==36 and count==14400,'All36 timing cases and14400 callbacks')
    groups={(g['sample_rate'],g['case']):g for g in review['groups']};summaries={(g['sample_rate'],g['case']):g for g in result['comparisons']};ratios=[];material=tail=0
    require(len(groups)==len(summaries)==6,'All six timing groups')
    for rate in (48000,96000):
        for name in CASES:
            values={arm:[rows[(rate,name,i,arm)]['cpu_seconds_per_audio_second'] for i in range(3)] for arm in ARMS}
            p95={arm:[rows[(rate,name,i,arm)]['callback_cpu_p95'] for i in range(3)] for arm in ARMS}
            med={arm:statistics.median(v) for arm,v in values.items()};med95={arm:statistics.median(v) for arm,v in p95.items()}
            reduction=1-med['candidate']/med['baseline'];change=med95['candidate']/med95['baseline']-1;speedups=[x/y for x,y in zip(values['baseline'],values['candidate'])]
            equal(summaries[(rate,name)],{'sample_rate':rate,'case':name,**values,'paired_speedups':speedups,'median_cpu_reduction_fraction':reduction},'All group summary arithmetic')
            g=groups[(rate,name)];equal(g['median_cpu_per_audio'],med,'Group medians');equal(g['median_p95_cpu_seconds'],med95,'Group p95 medians');equal(g['median_cpu_reduction_fraction'],reduction,'Material improvement');equal(g['median_p95_cpu_change_fraction'],change,'Tail change');equal(g['paired_speedups'],speedups,'All paired speedups')
            require(g['material_5percent_requirement_pass'] is (reduction>=.05) and g['p95_no_more_than_5percent_regression_pass'] is (change<=.05),'Original5percent policy')
            material+=int(reduction>=.05);tail+=int(change<=.05)
            for arm in ARMS:
                records=[rows[(rate,name,i,arm)] for i in range(3)]
                equal(g['retained_tails_and_misses'][arm],{'p95_cpu_seconds':p95[arm],'max_cpu_seconds':[c['callback_cpu_max'] for c in records],'max_wall_seconds':[c['callback_wall_max'] for c in records],'wall_deadline_misses':[c['wall_deadline_misses'] for c in records]},'Every tail/miss retained')
            for pair,speed in enumerate(speedups):ratios.append([rate,name,pair,speed])
    require(review['material_requirement_groups_passed']==material==6 and review['p95_requirement_groups_passed']==tail==6 and review['policy_pass'] is True,'All six fixed policy groups pass')
    require(review['runs']==12 and review['case_runs']==36 and review['paired_ratios']==18 and review['raw_callbacks_retained']==14400 and result['all_trials_retained'] is review['all_trials_retained'] is True,'No trial discarded')
    equal(review['fastest_candidate_pair'],max(ratios,key=lambda r:r[3]),'Fastest pair retained');equal(review['slowest_candidate_pair'],min(ratios,key=lambda r:r[3]),'Slowest pair retained');require(review['candidate_slower_paired_trials']==sum(r[3]<1 for r in ratios),'All ratio signs')
    totals={'windows':0,'bands':0,'strong':0,'weak':0,'empty':0};seen=set()
    for row in review['paired_timing_audio_checks']:
        rate,name,pair=row['sample_rate'],row['case'],row['pair'];seen.add((rate,name,pair));base.identities(a,row)
        require(row['byte_identical'] is (row['baseline']['sha256']==row['candidate']['sha256']),'Observer byte difference retained')
        stats=check_quality(row['quality'],recipe,rate,rows[(rate,name,pair,'baseline')]['frames'])
        for k in totals:totals[k]+=stats[k]
    require(len(seen)==18 and totals=={'windows':72,'bands':126,'strong':108,'weak':18,'empty':3},'All performance audio metrics including weak/empty support')
    require(review['all18_performance_audio_numerical_gates_pass'] is True and review['performance_audio_quality_recipe_unchanged'] is True,'Performance uses unchanged numerical recipe')
    return {'runs':12,'case_runs':36,'raw_callbacks':count,'paired_ratios':18,'material_groups_passed':material,'p95_groups_passed':tail,'audio_metrics':totals,'maximum_observed_cpu_seconds':maximum_cpu,'maximum_observed_wall_seconds':maximum_wall,'wall_deadline_misses':misses}


def integration_checks(a,index):
    rows=index.get('integration',[])
    if not rows:return None
    expected_tests={'native':3,'asan':2,'reason':12}
    require(len(rows)==3 and {r['id'] for r in rows}==set(expected_tests),'All native/sanitizer/Reason mock receipts retained')
    receipts=[]
    for row in rows:
        result=a.role(row['result_role']);frozen=a.role(row['freeze_role'])
        base.identities(a,result);base.identities(a,frozen)
        require(result['kind']==row['id'] and result['passed'] is True and result['error'] is None,'Stored integration passes')
        require(base.same_identity(result['freeze'],index['roles'][row['freeze_role']]),'Integration binds its exact input freeze')
        require(result['tests_are_host_approximations'] is True and result['Reason_SDK_or_Recon_run'] is False,'Host approximation/no SDK or Recon claim')
        require(len(result['commands'])==3 and all(c['exit_code']==0 for c in result['commands']),'Configure/build/test exit codes')
        tests=[c for c in result['commands'] if Path(c['command'][0]).name=='ctest'];require(len(tests)==1,'One bound test log')
        log=tests[0]['log'];text=a.resolve(log['path'],log['sha256']).decode();count=expected_tests[row['id']]
        require(row['expected_tests']==count and re.findall(r'100% tests passed(?:,\s*0 tests failed)? out of\s+(\d+)',text)==[str(count)]
                and len(re.findall(r'\bPassed\b',text))==count,'All declared stored tests passed')
        receipts.append({'kind':row['id'],'stored_tests_passed':count,'tests_are_host_approximations':True,'Reason_SDK_or_Recon_run':False})
    policy=a.role('integration_policy_result');base.identities(a,policy)
    expected={'default-parent-zero':(1,1),'free-optout':(1,0),'pressure-optout':(0,1),
              'cached-pressure-off-reconfigure':(0,1),'unsupported':(0,0),'confidence':(0,0),'confidence-pressure-optin':(1,0)}
    require(policy['passed'] is True and len(policy['cases'])==7 and {c['name'] for c in policy['cases']}==set(expected),'All seven build policy configurations')
    commands=0
    for case in policy['cases']:
        require(case['passed'] is True and len(case['checks'])==2
                and {c['target'] for c in case['checks']}=={'keyra_full_instrument.dir','keyra_full_sdk_compat.dir'},'Native and SDK-compatible targets retained')
        for check in case['checks']:
            pressure,free=expected[case['name']] if check['target']=='keyra_full_instrument.dir' else (0,0)
            require(check['effective_pressure']==pressure and check['effective_free']==free
                    and base.last_macro(check['command'],'KEYRA_FULL_PRESSURE_SIMD')==str(pressure)
                    and base.last_macro(check['command'],'KEYRA_FULL_FREE_UNISON_SIMD')==str(free),
                    'Actual last ordered -D/-U pressure/free settings')
            commands+=1
    require(commands==14,'All14 policy command records checked')
    return {'stored_test_receipts':receipts,'effective_compile_commands_checked':commands,
            'quality_qualification_scope':'Current OriginalControl/profile0 with free-unison ON; other build policies are not new numerical/performance qualification.',
            'new_tests_executed_by_checker':False}


def production_checks(a,index,recipe):
    if 'production_register_result' not in index['roles']:return None
    result=a.role('production_register_result');p=a.role('production_register_protocol')
    base.identities(a,result);base.identities(a,p)
    require(base.same_identity(result['protocol'],index['roles']['production_register_protocol'])
            and result['pass'] is result['all_production_payloads_exact_qualified_ON'] is True
            and result['case_count']==len(result['cases'])==len(p['cases'])==10,'Ten closed production CLI comparisons')
    require(p['quality_source_sha256']==index['roles']['quality_source']['sha256']
            and p['quality_recipe_unchanged'] is True and p['frames_per_case']==48000,'Unchanged production observer recipe')
    selections={'PRESSURE_SIMD':'1','FREE_UNISON_SIMD':'1','FAST_CONTACT':'1','MECHANISM_CACHE':'1','MODEL_PROFILE':'0'}
    require(p['compile_selections']=={'library':selections,'renderer':selections},'Library and CLI select qualified native controls')
    cases={r['id']:r for r in p['cases']};require(len(cases)==10 and {r['id'] for r in result['cases']}==set(cases),'Frozen production case inventory')
    for row in result['cases']:
        require(row['command']==cases[row['id']]['command'] and row['pass'] is row['qualified_ON_payload_byte_identical'] is True,'Actual production command and recorded ON equality')
        report=reader.json_data(a.resolve(row['report']['path'],row['report']['sha256']))
        require(all(report[k] is True for k in ('pressure_simd','free_unison_simd','fast_contact','mechanism_cache'))
                and report['model_profile']=='OriginalControl'
                and report['calibration_header_sha256']=='619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7',
                'Actual production renderer selections and calibration')
        require(report['sample_rate']==report['frames']==48000 and report['fault_flags']==report['unsafe_launches']==report['events_rejected']==0
                and report['topology']=={'strings':230,'string_modes':17778,'board_modes':475},'Production support/topology/faults')
        digest=row['actual_float32_payload_sha256'];require(len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'Recorded interleaved production payload digest')
        check_quality(row['quality_vs_OFF'],recipe,48000,48000)
    return {'cases':10,'stored_production_ON_payload_equality_comparisons':10,'unchanged_OFF_numerical_comparisons':10,
            'payload_identity_scope':'Bound recorded equality after layout conversion; interleaved WAV and planar reference digests are not compared as identical strings.',
            'new_CLI_or_PCM_execution':False}


def verify(index):
    a=reader.Archive(index);role=lambda name:a.role(name if name in index['roles'] else 'harness_'+name)
    study=index['study'];source=role('source_protocol');p=role('harness_protocol');build=role('build_receipt');correct=role('correctness_result');creview=role('correctness_review');perf=role('performance_result');preview=role('performance_review');recipe=p['observer_quality']
    for obj in (source,p,build,correct,creview,perf,preview):base.identities(a,obj)
    require(len(p['bindings'])==69 and all(base.same_identity(obj['protocol'],index['roles']['harness_protocol']) for obj in (build,correct,creview,perf,preview)),'All69 source bindings and exact protocol')
    manifest=role('source_manifest');base.identities(a,manifest);proof=role('source_compileproof');base.identities(a,proof)
    require(manifest['runtime_file_count']==len(manifest['files'])==10 and all(r['original']['sha256']==r['snapshot']['sha256'] for r in manifest['files']),'All ten runtime snapshots unchanged')
    require(source['model_source_modified'] is source['coefficients_changed'] is source['new_reassociation_or_fastmath'] is False,'Existing observer only')
    require(proof['both_existing_pressure_working_loops_vectorized'] is proof['all_three_fused_N_templates_vectorized'] is True and proof['model_constructed'] is False and proof['model_steps']==proof['timing_trials']==0,'Source compile proof scope')
    require(p['arm_flags']==source['arm_flags']=={'baseline':['-DKEYRA_FULL_PRESSURE_SIMD=0'],'candidate':['-DKEYRA_FULL_PRESSURE_SIMD=1']},'Only arm pressure macro differs')
    for arm in ARMS:
        prefix=study['harness_root']+'/build/'+arm+'/'
        selected={r['path'][len(prefix):]:r['sha256'] for r in p['bindings'] if r['path'].startswith(prefix)}
        if arm=='baseline':baseline=selected
        else:require(selected==baseline and selected,'Both arms source bytes identical')
    require(len(build['builds'])==4 and {(r['mode'],r['variant']) for r in build['builds']}=={(mode,arm) for mode in ('correctness','performance') for arm in ARMS},'Four distinct native binary identities')
    for b in build['builds']:
        command=b['command'];require(base.last_macro(command,'KEYRA_FULL_PRESSURE_SIMD')==str(int(b['variant']=='candidate')),'Pressure flag0/1')
        for macro,value in (('KEYRA_FULL_FREE_UNISON_SIMD',1),('KEYRA_FULL_FAST_CONTACT',1),('KEYRA_FULL_MECHANISM_CACHE',1),('KEYRA_FULL_MODEL_PROFILE',0)):require(base.last_macro(command,macro)==str(value),'Shared backend controls')
        require('-fopenmp-simd' in command and '-ffp-contract=off' in command and 'libgomp' not in b['dynamic_dependencies'] and 'libomp' not in b['dynamic_dependencies'],'SIMD-only compiler/no worker runtime')
    bindings={r['path']:r for r in p['bindings']};oldp=next(reader.json_data(a.resolve(r['path'],r['sha256'])) for r in p['bindings'] if r['path'].endswith('/full-free-unison-fusion/harness-v2/protocol.json'))
    oldroot=next(r['path'].rsplit('/',1)[0] for r in p['bindings'] if r['path'].endswith('/full-free-unison-fusion/harness-v2/protocol.json'))
    for name in ('ObserverCapture.h','inventory.inc'):require(frozen_bytes(a,p,study['harness_root']+'/'+name)==frozen_bytes(a,oldp,oldroot+'/'+name),'Unchanged qualified harness helper')
    require(frozen_bytes(a,p,study['harness_root']+'/harness.cpp')==frozen_bytes(a,oldp,oldroot+'/harness.cpp').replace(b'keyra_fusion_snapshot',b'keyra_pressure_snapshot'),'Same case/event harness')
    old=frozen_bytes(a,oldp,oldroot+'/state_snapshot.inc').decode().replace('keyra_fusion_snapshot','keyra_pressure_snapshot').replace('sequence(impl.previous);sequence(impl.highpass);','').replace('sequence(string.cachedRadiation);','')
    normalize=lambda text:'\n'.join(s for line in text.splitlines() if (s:=line.split('//',1)[0].strip()))
    require(normalize(old)==normalize(frozen_bytes(a,p,study['harness_root']+'/state_snapshot.inc').decode()),'Only three observer-memory families omitted')
    synthetic=role('quality_synthetic');require(synthetic['pass'] is True and all(synthetic['checks'].values()),'Manufactured numerical comparator checks retained')
    for key,value in synthetic['constants'].items():require(recipe[key]==value,'Same frozen numerical constants')
    for key,value in {'sample_rates':[44100,48000,88200,96000],'maximum_null_rms_db':-110.,'maximum_absolute_error_factor':1.e-4,'maximum_LR_shift_db':.001,'maximum_correlation_shift':1.e-5,'maximum_mono_shift_db':.001,'maximum_band_shift_db':.01,'relative_power_floor':1.e-10,'window_edges_seconds':[.05,.20],'band_edges_hz':[0.,31.25,250.,1000.,4000.,12000.,19000.]}.items():require(recipe[key]==value,'Approved pre-run recipe '+key)
    require(index['roles']['quality_source']['sha256']=='7023e7ca4984312ff72492a55267b630482762bc01a8369360dcd6fd657a6e9e','Frozen quality source, never executed')
    require(len(correct['comparisons'])==16 and {(r['sample_rate'],r['case']) for r in correct['comparisons']}=={(rate,name) for rate in recipe['sample_rates'] for name in (*CASES,'silent-reset')},'All16 correctness groups')
    totals={'windows':0,'bands':0,'strong':0,'weak':0,'empty':0};physical=payloads=0
    for row in correct['comparisons']:
        require(row['prepare_inventory']==base.INVENTORY and row['physical_state_exact'] is True and row['observer_quality_pass'] is True,'Actual full inventory and physical parity')
        rate,name=row['sample_rate'],row['case'];frames=round(rate*(.64 if name in CASES[:2] else .4))
        require(len(row['files'])==7 and sum(f['role']=='physical_state' for f in row['files'])==5,'Five physical checkpoints plus two observer payloads')
        reports={arm:base.json_at(a,f"{study['harness_root']}/correctness/{rate}/{arm}/stdout.json") for arm in ARMS}
        cases={arm:next(c for c in reports[arm]['cases'] if c['name']==name) for arm in ARMS}
        require({k:v for k,v in cases['baseline'].items() if k!='prepare_wall_seconds_excluded'}=={k:v for k,v in cases['candidate'].items() if k!='prepare_wall_seconds_excluded'},'Actual event/diagnostic reports exact')
        require(cases['baseline']['faults']==cases['baseline']['unsafe_launches']==0 and cases['baseline']['frames']==frames,'Authored frame count/zero faults')
        for f in row['files']:
            require(f['byte_identical'] is (f['baseline']['sha256']==f['candidate']['sha256']),'Recorded physical/observer equality distinction')
            left,right=(base.metadata(a,f[arm]['path'],f[arm]['sha256']) for arm in ARMS)
            require(left['bytes']==right['bytes'] and left['bytes']>0,'Paired payload lengths')
            if f['role']=='physical_state':require(f['byte_identical'] is True,'Exact physical checkpoint');physical+=1
            else:
                require(f['role']=='observer_output' and left['bytes']==frames*2*(8 if f['baseline']['path'].endswith('.f64le-pressure') else 4),'Observer payload frame support');payloads+=1
        for q in row['observer_quality'].values():
            stats=check_quality(q,recipe,rate,frames)
            for k in totals:totals[k]+=stats[k]
    require(physical==80 and payloads==32 and totals=={'windows':128,'bands':224,'strong':200,'weak':24,'empty':0},'All physical/payload/window/band evidence retained')
    require(correct['pass'] is creview['pass'] is True and creview['physical_state_pairs']==80 and creview['observer_payload_pairs']==32 and creview['raw_f64_and_f32_observer_gates_passed']==32,'Independent correctness review')
    require(base.same_identity(preview['decision_policy'],index['roles']['policy']),'Original5percent policy retained')
    policy=role('policy');require(policy['performance_outcomes_opened'] is False and 'Atleast5percent' in policy['requirements']['material_throughput'] and 'No morethan5percent' in policy['requirements']['callback_tail'],'Predeclared policy semantics')
    timing_summary=timing(a,study,perf,preview,p,recipe)
    historical=role('historical_pressure_regression');old_repeat=next(r for r in historical['current_timing']['rows'] if r['sample_rate']==48000 and r['case']=='repeats-pedal')
    old_reduction=1-statistics.median(old_repeat['on_cpu_seconds_per_audio_second'])/statistics.median(old_repeat['off_cpu_seconds_per_audio_second'])
    equal(old_repeat['median_cpu_reduction_fraction'],old_reduction,'Historical integrated repetition regression');require(old_reduction<-.12,'Prior negative result retained as history')
    register=None
    if 'register_result' in index['roles']:
        r=role('register_result');rp=role('register_protocol');rb=role('register_build_receipt')
        for obj in (r,rp,rb):base.identities(a,obj)
        require(base.same_identity(r['protocol'],index['roles']['register_protocol']) and rp['observer_quality_recipe']==recipe and r['pass'] is True and r['case_count']==len(r['comparisons'])==10,'Fixed register study and same numerical recipe')
        require(base.same_identity(rb['protocol'],index['roles']['register_protocol']) and base.same_identity(rp['parent_protocol'],index['roles']['harness_protocol']),'Register build and parent protocol bindings')
        require({(row['case']['note'],row['case']['velocity_MIDI']) for row in r['comparisons']}=={(note,velocity) for note in (21,36,60,84,108) for velocity in (14,124)},'All frozen extreme/register/velocity cases retained')
        for row in r['comparisons']:
            require(row['physical_final_state_exact'] is row['pass'] is True and row['state_files'][0]['sha256']==row['state_files'][1]['sha256'],'Register final physical state exact')
            require(all(row['case'][k]==0 for k in ('faults','unsafe_launches','nonfinite_output_faults','rejected_inputs')) and row['case']['requests']==row['case']['launches']==1,'Register finite output/one actual strike')
            for q in row['observer_quality'].values():check_quality(q,recipe,48000,48000)
        register={'cases':10,'numerical_payload_pairs':20,'exact_final_state_pairs':10,'recording_audio_access':r['recording_audio_access']}
    if 'validation' in index['roles']:
        validation=role('validation');base.identities(a,validation)
        require(validation['numerical_recipe']==recipe and all(validation[k] is False for k in ('realtime_qualified','production_goal_complete','recording_audio_access','inaudibility_proven','pitch_or_realism_improvement_claimed')),'Validation retains engineering/qualification limits')
    integration=integration_checks(a,index)
    production=production_checks(a,index,recipe)
    return {'verification_passed':True,'published_records_verified':a.checked,'correctness_physical_pairs':physical,'correctness_observer_payload_pairs':payloads,'correctness_metrics':totals,'performance':timing_summary,'historical_48k_repetition_cpu_reduction':old_reduction,'register':register,'integration':integration,'production_register':production,'PCM_native_DSP_or_archived_quality_executed':False,'quality_scope':'Stored engineering arithmetic; not fresh FFT/sample measurement, audibility or realtime qualification.','adopted_by_experiment':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=verify(reader.json_data((PACKAGE/'index.json').read_bytes()))
    if args.output:
        require(not args.output.exists(),'New output required');args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
