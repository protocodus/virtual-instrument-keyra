#!/usr/bin/env python3
"""Verify archived fusion evidence and recompute every retained timing summary.

Standard library only. Native binaries, PCM and deep-state payloads remain
external identities: this checks their recorded sizes/hashes and independent
review receipts, without decoding or rerunning them. Archived Python is not run.
"""
from pathlib import Path
import argparse
import ast
import importlib.util
import json
import math
import re
import shlex
import statistics
import sys

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[2]
spec=importlib.util.spec_from_file_location('fusion_archive_reader',ROOT/'tools/experiments/body_radiation_basis/check.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
require=reader.require
CASES=('music','repeats-pedal','dense-88-tail')
ARMS=('baseline','candidate')
ORDERS=(('baseline','candidate'),('candidate','baseline'),('baseline','candidate'))
COMMON_FLAGS=('-DKEYRA_FULL_PRESSURE_SIMD=0','-DKEYRA_FULL_FAST_CONTACT=1',
              '-DKEYRA_FULL_MECHANISM_CACHE=1','-DKEYRA_FULL_MODEL_PROFILE=0','-ffp-contract=off')
INVENTORY={'candidate':True,'valid':True,'mode_count':17778,'fused_modes':12507,'fallback_modes':5271,
           'original_rows':6168,'scheduled_rows':6168,'group_count':89,'keys_owned':88,'strings_owned':230,
           'unique_mode_updates':True,'unique_row_membership':True,'original_grouped_rows_exact':True,
           'added_cache_bytes':42328}


def close(a,b):
    return math.isclose(a,b,rel_tol=128*sys.float_info.epsilon,abs_tol=128*sys.float_info.epsilon)


def equal_values(actual,expected,label):
    if isinstance(expected,dict):
        require(isinstance(actual,dict) and actual.keys()==expected.keys(),label)
        for key,value in expected.items():equal_values(actual[key],value,label+'.'+key)
    elif isinstance(expected,(list,tuple)):
        require(isinstance(actual,(list,tuple)) and len(actual)==len(expected),label)
        for i,value in enumerate(expected):equal_values(actual[i],value,label+f'[{i}]')
    elif isinstance(expected,float):require(close(actual,expected),label)
    else:require(actual==expected,label)


def identities(archive,value):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
            archive.identity(value['path'],value['sha256'],value.get('bytes'))
        for child in value.values():identities(archive,child)
    elif isinstance(value,list):
        for child in value:identities(archive,child)


def same_identity(a,b):
    return (a['path']==b['path'] and a['sha256']==b['sha256']
            and ('bytes' not in a or 'bytes' not in b or a['bytes']==b['bytes']))


def published(archive,path):
    items=archive.by_path.get(path,[])
    require(len({r['sha256'] for r,_ in items})==1,'Unique published identity '+path)
    return items[0][1]


def json_at(archive,path):return reader.json_data(published(archive,path))


def source_bytes(archive,protocol,path):
    records=[r for r in protocol['sources'] if r['path']==path]
    require(len(records)==1,'Unique frozen source binding '+path)
    record=records[0]
    return archive.resolve(path,record['sha256'])


def source_json(archive,protocol,path):return reader.json_data(source_bytes(archive,protocol,path))


def metadata(archive,path,sha=None):
    items=[r for r,_ in archive.by_path.get(path,[])]+archive.external.get(path,[])
    if sha is not None:items=[r for r in items if r['sha256']==sha]
    require(items and len({(r['sha256'],r['bytes']) for r in items})==1,'Unique metadata '+path)
    return items[0]


def percentile(values,fraction):
    ordered=sorted(values)
    return ordered[math.ceil(fraction*(len(ordered)-1))]


def correctness(archive,study,result,review,protocol):
    root=study['harness_root'];comparisons=result['comparisons']
    expected={(rate,name) for rate in (44100,48000,88200,96000) for name in (*CASES,'silent-reset')}
    require(len(comparisons)==16 and {(c['sample_rate'],c['case']) for c in comparisons}==expected,'All16 correctness groups')
    files=states=frames=0
    summaries={(c['sample_rate'],c['name']):c for c in review['case_summaries']}
    require(set(summaries)==expected,'All16 independent-review case summaries')
    for row in comparisons:
        rate,name=row['sample_rate'],row['case']
        raw={arm:json_at(archive,f'{root}/correctness/{rate}/{arm}/stdout.json') for arm in ARMS}
        for arm in ARMS:require(raw[arm]['sample_rate']==rate,'Correctness source rate')
        cases={arm:next(c for c in raw[arm]['cases'] if c['name']==name) for arm in ARMS}
        for arm in ARMS:
            require({c['name'] for c in raw[arm]['cases']}==set((*CASES,'silent-reset')),'All authored correctness cases')
        comparable=lambda c:{k:v for k,v in c.items() if k!='prepare_wall_seconds_excluded'}
        require(comparable(cases['baseline'])==comparable(cases['candidate']),'Same correctness event/diagnostic/checkpoint report')
        case=cases['baseline'];length=round(rate*(.64 if name in CASES[:2] else .4))
        require(case['frames']==length and close(case['audio_seconds'],length/rate),'Correctness frame support')
        require(case['faults']==case['unsafe_launches']==0,'Zero correctness faults and unsafe launches')
        checkpoints=case['physical_state_checkpoints']
        expected_checkpoints=([64,4096,round(.20*rate),round(.20*rate)+64,length] if name=='silent-reset'
                              else [64,512,4096,8192,length])
        require(checkpoints==expected_checkpoints,'Five exact authored checkpoints including reset boundary')
        expected_files={name+'.f64le-pressure',name+'.f32le-planar',*[name+'-'+str(f)+'.state' for f in checkpoints]}
        require(len(row['files'])==7 and {Path(f['baseline']['path']).name for f in row['files']}==expected_files,'Seven paired payload identities')
        for pair in row['files']:
            a,b=pair['baseline'],pair['candidate'];identities(archive,pair)
            require(pair['byte_identical'] is True and a['sha256']==b['sha256'],'Recorded paired SHA/byte equality')
            require(Path(a['path']).name==Path(b['path']).name,'Paired file identity')
            ma,mb=metadata(archive,a['path'],a['sha256']),metadata(archive,b['path'],b['sha256'])
            require(ma['bytes']==mb['bytes'] and ma['bytes']>0,'Paired payload lengths')
            if a['path'].endswith('.f64le-pressure'):require(ma['bytes']==length*2*8,'Raw stereo pressure length')
            elif a['path'].endswith('.f32le-planar'):require(ma['bytes']==length*2*4,'Float stereo output length')
            else:states+=1
            files+=1
        require(row['prepare_inventory']==INVENTORY,'Actual prepared candidate inventory')
        require(json_at(archive,f'{root}/correctness/{rate}/candidate/{name}.prepare.json')==INVENTORY,'Independent inventory artifact')
        for key,value in summaries[(rate,name)].items():
            require(value==(rate if key=='sample_rate' else cases['candidate'][key]),'Review summary candidate source '+key)
        frames+=length
    require(files==112 and states==80 and frames==574704,'Paired correctness totals')
    require(review['paired_file_comparisons']==112 and review['paired_deep_snapshots']==80
            and review['paired_f64_pressure_values']==review['paired_f32_output_values']==frames*2
            and review['total_frames_per_arm']==frames,'Independent correctness review totals')
    require(review['actual_candidate_prepare_inventory_same_all16']==INVENTORY,'Common inventory review')
    require(result['pass'] is review['pass'] is True and review['f64_f32_all_finite_both_arms'] is True
            and review['all_diagnostics_faults_and_unsafe_zero'] is True,'Recorded native correctness and independent review pass')
    require(review['performance_runs']==0 and review['adopted'] is result['adopted'] is False,'Correctness review is not timing/adoption')
    return {'paired_payload_metadata':files,'paired_deep_snapshot_metadata':states,'frames_per_arm':frames}


def performance(archive,study,result,review,protocol):
    root=study['harness_root'];runs=result['runs']
    wanted=[(rate,pair,arm) for rate in (48000,96000) for pair,order in enumerate(ORDERS) for arm in order]
    require([(r['sample_rate'],r['pair'],r['variant']) for r in runs]==wanted,'All AB/BA/AB trials in frozen order')
    require(protocol['performance']['pairs']==[list(p) for p in ORDERS]
            and protocol['performance']['all_trials_retained'] is True
            and protocol['performance']['discard_warmup_trials'] is False,'No discarded runs or warmups')
    rows={};callbacks=0
    for run in runs:
        identities(archive,run['trace']);raw=reader.json_data(archive.resolve(run['trace']['path'],run['trace']['sha256']))
        require(raw['sample_rate']==run['sample_rate'] and raw['cases']==run['cases'],'Full unmodified raw timing trace retained')
        require([c['name'] for c in raw['cases']]==list(CASES),'Three timing cases in source order')
        for case in raw['cases']:
            rate,name=run['sample_rate'],case['name'];count=30720 if name in CASES[:2] else 15360
            require(case['frames']==count and close(case['audio_seconds'],count/rate),'Frozen performance frame count/audio rate')
            cpu,wall=case['callback_thread_cpu_seconds'],case['callback_wall_seconds']
            require(len(cpu)==len(wall)==len(case['events_per_callback'])==count//64,'Every64frame callback retained')
            require(all(math.isfinite(x) and x>=0 for x in cpu+wall),'Finite nonnegative raw clocks')
            total=sum(cpu);equal_values(case['callback_cpu_seconds'],total,'Callback CPU sum')
            equal_values(case['cpu_seconds_per_audio_second'],total/(count/rate),'CPU/audio rate')
            for label,values in (('cpu',cpu),('wall',wall)):
                for suffix,fraction in (('p50',.5),('p95',.95)):
                    equal_values(case[f'callback_{label}_{suffix}'],percentile(values,fraction),'Ceil-index quantile')
                equal_values(case[f'callback_{label}_max'],max(values),'Maximum callback clock')
            require(case['wall_deadline_misses']==sum(x>64/rate for x in wall),'Wall deadline misses')
            require(case['faults']==case['unsafe_launches']==0,'Zero performance faults/unsafe launches')
            require(sum(case['events_per_callback'])==case['events_dispatched']==len(case['events']),'All timing events dispatched')
            rows[(rate,name,run['pair'],run['variant'])]=case;callbacks+=len(cpu)
    require(len(runs)==12 and len(rows)==36 and callbacks==14400,'All12/36/14400 timing records')
    summary_rows={(r['sample_rate'],r['case']):r for r in result['comparisons']}
    review_rows={(r['sample_rate'],r['case']):r for r in review['groups']}
    wanted_groups={(rate,name) for rate in (48000,96000) for name in CASES}
    require(set(summary_rows)==set(review_rows)==wanted_groups,'All6 timing groups')
    groups=[];ratios=[];material=tail=0
    for rate in (48000,96000):
        for name in CASES:
            by_arm={arm:[rows[(rate,name,pair,arm)] for pair in range(3)] for arm in ARMS}
            values={arm:[c['cpu_seconds_per_audio_second'] for c in by_arm[arm]] for arm in ARMS}
            p95={arm:[c['callback_cpu_p95'] for c in by_arm[arm]] for arm in ARMS}
            med={arm:statistics.median(v) for arm,v in values.items()};med95={arm:statistics.median(v) for arm,v in p95.items()}
            reduction=1-med['candidate']/med['baseline'];p95change=med95['candidate']/med95['baseline']-1
            speedups=[a/b for a,b in zip(values['baseline'],values['candidate'])]
            material_ok=reduction>=.05;tail_ok=p95change<=.05
            expected_summary={'sample_rate':rate,'case':name,**values,'paired_speedups':speedups,'median_cpu_reduction_fraction':reduction}
            equal_values(summary_rows[(rate,name)],expected_summary,'Recomputed group summary')
            retained={arm:{'p95_cpu_seconds':p95[arm],
                           'max_cpu_seconds':[c['callback_cpu_max'] for c in by_arm[arm]],
                           'max_wall_seconds':[c['callback_wall_max'] for c in by_arm[arm]],
                           'wall_deadline_misses':[c['wall_deadline_misses'] for c in by_arm[arm]]} for arm in ARMS}
            expected_group={'sample_rate':rate,'case':name,'median_cpu_per_audio':med,'median_cpu_reduction_fraction':reduction,
                            'median_p95_cpu_seconds':med95,'median_p95_cpu_change_fraction':p95change,
                            'material_5percent_requirement_pass':material_ok,'p95_no_more_than_5percent_regression_pass':tail_ok,
                            'paired_speedups':speedups,'retained_tails_and_misses':retained}
            equal_values(review_rows[(rate,name)],expected_group,'Recomputed policy group')
            groups.append(expected_group);material+=int(material_ok);tail+=int(tail_ok)
            for pair,speedup in enumerate(speedups):
                ratios.append([rate,name,pair,speedup])
                a,b=(rows[(rate,name,pair,arm)] for arm in ARMS)
                stable=('name','frames','audio_seconds','events_dispatched','faults','unsafe_launches','requests','launches',
                        'deferred','coalesced','cancelled','expired','events','events_per_callback')
                require(all(a[k]==b[k] for k in stable),'Paired timing event/diagnostic equality')
    require(len(review['paired_timing_audio_checks'])==18,'All18 paired audio metadata checks')
    for row in review['paired_timing_audio_checks']:
        rate,name,pair=row['sample_rate'],row['case'],row['pair']
        require((rate,name) in wanted_groups and pair in range(3) and row['byte_identical'] is True,'Paired timing audio identity')
        for arm in ARMS:
            path=f'{root}/performance/{rate}/pair{pair}/{arm}/{name}.f32le-planar'
            record=metadata(archive,path,row['sha256'])
            require(record['bytes']==rows[(rate,name,pair,arm)]['frames']*2*4,'Timing audio length/hash metadata')
    passed=material==tail==6
    require(review['runs']==12 and review['case_runs']==36 and review['paired_ratios']==18
            and review['raw_callbacks_retained']==callbacks,'Retained performance review counts')
    require(review['material_requirement_groups_passed']==material and review['p95_requirement_groups_passed']==tail
            and review['policy_pass'] is passed and passed is study['expected_policy_pass'],'Recomputed predeclared decision')
    require(review['all_trials_retained'] is result['all_trials_retained'] is True
            and review['adopted'] is result['adopted'] is False,'No timing selection or adoption')
    if 'candidate_slower_paired_trials' in review:
        require(review['candidate_slower_paired_trials']==sum(row[3]<1 for row in ratios),'All18 paired ratio signs')
        equal_values(review['fastest_candidate_pair'],max(ratios,key=lambda r:r[3]),'Fastest retained pair')
        equal_values(review['slowest_candidate_pair'],min(ratios,key=lambda r:r[3]),'Slowest retained pair')
    return {'raw_callback_rows':callbacks,'paired_ratios':18,'groups':6,'material_groups_passed':material,
            'p95_groups_passed':tail,'policy_pass':passed,'median_cpu_reductions':[g['median_cpu_reduction_fraction'] for g in groups]}


def last_macro(command,name):
    """Apply -D/-U options in actual command order, including split options."""
    tokens=shlex.split(command) if isinstance(command,str) else command
    value=None;i=0
    while i<len(tokens):
        token=tokens[i];operation=token[:2]
        if operation in ('-D','-U'):
            argument=token[2:]
            if not argument:
                i+=1;require(i<len(tokens),'Complete -D/-U argument');argument=tokens[i]
            macro,separator,definition=argument.partition('=')
            if macro==name:value=None if operation=='-U' else definition if separator else '1'
        i+=1
    return value


def format_checks(archive,index,reproduction):
    if 'integration_format_receipt' not in index['roles']:return None
    receipt=archive.role('integration_format_receipt');identities(archive,receipt)
    require(all(receipt[k] is True for k in ('CXX_tokens_including_comments_and_quoted_literals_identical',
        'SETUP_METHODS_CXX_tokens_identical','auxiliary_module_only_four_requested_newlines',
        'frozen_runtime_header_and_calibration_unchanged')) and receipt['tests_or_compiles_reexecuted'] is False,
        'Stored format-only scope and predicates')
    require(receipt['old_model']['sha256']==reproduction['canonical_model_sha256']
            and receipt['new_model']['sha256']=='325a6eff65c8caffda65ebd803bcc44894a27ca85d2a7e7f018e60efaa29bd80',
            'Original integration source linked to final formatted source')
    require(receipt['helper_hot_bytes_exact']['sha256']==reproduction['canonical_helper_sha256'],
            'Hot helper unchanged by formatting')
    changes=archive.role('integration_format_requested_changes')['changes'];require(len(changes)==4,'Only four requested replacements')
    old,new=receipt['old_model'],receipt['new_model']
    text=archive.resolve(old['path'],old['sha256']).decode()
    for change in changes:
        require(text.count(change['before'])==1,'Unique requested cold statement pair')
        text=text.replace(change['before'],change['after'],1)
    require(text.encode()==archive.resolve(new['path'],new['sha256']),'Four exact newlines reproduce final source')
    native=archive.role('integration_native_post_format_result')
    reason=archive.role('integration_reason_post_format_result')
    require(native['passed'] is reason['passed'] is True and native['compile_warnings']==[],
            'Bound final native/Reason rebuild receipts pass')
    require(native['format_receipt_sha256']==index['roles']['integration_format_receipt']['sha256'],
            'Native addendum binds original format receipt')
    archive.by_hash(native['log_sha256'])
    before=archive.role('integration_native_pre_format_binaries');identities(archive,before)
    old_binaries={r['path']:r['sha256'] for r in before['files']}
    require(len(native['comparisons'])==4 and len(reason['checks'])==3,'All seven already-tested native executable identities')
    for item in native['comparisons']:
        require(item['exact'] is True and item['before_sha256']==item['after_sha256']==old_binaries[item['path']],
                'Already-tested native executable unchanged')
        archive.identity(item['path'],item['after_sha256'])
    reason_root=str(Path(index['roles']['integration_reason_post_format_result']['path']).parent)
    for item in reason['checks']:
        require(item['before_sha256']==item['after_sha256'],'Already-tested Reason mock executable unchanged')
        archive.identity(reason_root+'/build/'+item['name'],item['after_sha256'])
    return {'four_exact_source_replacements_verified':True,'final_model_sha256':new['sha256'],
            'already_tested_executable_hash_metadata_equal':7,'new_ASAN_or_Reason_tests_claimed':False}


def integration_checks(archive,index):
    rows=index.get('integration',[])
    if not rows:return []
    expected={'native':3,'asan':2,'reason':12}
    require(len(rows)==3 and {r['id'] for r in rows}==set(expected),'All three integration result receipts')
    equivalence=archive.role('integration_source_equivalence')
    reproduction=archive.role('integration_source_reproduction')
    policy=archive.role('integration_policy_result')
    renderer=archive.role('integration_renderer_report')
    for obj in (equivalence,reproduction,policy,renderer):identities(archive,obj)
    require(all(equivalence[k] is True for k in (
        'enabled_original_control_matches_qualified_v2_nonblank_lines_exact',
        'disabled_undefined_unsupported_original_storage_setup_step_matches_baseline_nonblank_lines_exact',
        'qualified_v2_helper_bytes_exact')) and equivalence['provenance_coefficients_changed'] is False,
        'Recorded selective source equivalence and unchanged coefficients')
    require(all(reproduction[k] is True for k in ('fresh_control_all4_files_exact',
        'fresh_confidence_runtime_2_files_exact','confidence_provenance_refreshed_only','source_only'))
        and reproduction['Piano_constructed'] is False and reproduction['model_steps']==0,
        'Recorded fresh-generation reproduction has no model run')
    qualified=next(s for s in index['studies'] if s['id']=='v2')
    source=archive.role(qualified['source_role_prefix']+'_protocol')
    helper=source_bytes(archive,source,qualified['source_root']+'/FreeUnisonFusion.h')
    require(archive.by_hash(reproduction['canonical_helper_sha256'])==helper,'Integrated helper bytes equal qualified v2')
    bound={Path(r['path']).name:r['sha256'] for r in equivalence['bindings']}
    for field,name in (('canonical_model_sha256','PreparedModel.h'),('canonical_helper_sha256','FreeUnisonFusion.h'),
                       ('canonical_generator_sha256','generate_prepared_model.py'),('canonical_transform_sha256','free_unison_transform.py')):
        require(reproduction[field]==bound[name],'Reproduction tied to frozen integration '+name)
    require(renderer['free_unison_simd'] is True and renderer['pressure_simd'] is False
            and renderer['fast_contact'] is renderer['mechanism_cache'] is True
            and renderer['fault_flags']==renderer['unsafe_launches']==renderer['events_rejected']==0,
            'Recorded connected native renderer flags/faults')
    require(renderer['model_profile']=='OriginalControl'
            and renderer['topology']=={'strings':230,'string_modes':17778,'board_modes':475},'Renderer original topology')
    expected_policy={'default-parent-zero':1,'optout-parent-one':0,'unsupported-parent-one':0,'confidence-parent-one':0}
    require(policy['passed'] is True and len(policy['cases'])==4
            and {c['name'] for c in policy['cases']}==set(expected_policy),'All four compiler policy cases')
    macro_checks=0
    for case in policy['cases']:
        require(case['passed'] is True and {r['target'] for r in case['checks']}
                =={'keyra_full_instrument.dir','keyra_full_sdk_compat.dir'},'Both native/SDK compile policies retained')
        for check in case['checks']:
            native=check['target']=='keyra_full_instrument.dir'
            want=expected_policy[case['name']] if native else 0
            effective=last_macro(check['command'],'KEYRA_FULL_FREE_UNISON_SIMD')
            require(effective==str(want) and check['effective_macro']==want,'Last ordered fusion -D/-U overrides parent')
            for name,value in (('KEYRA_FULL_PRESSURE_SIMD',0),('KEYRA_FULL_FAST_CONTACT',1),('KEYRA_FULL_MECHANISM_CACHE',1),
                               ('KEYRA_FULL_MODEL_PROFILE',int(case['name']=='confidence-parent-one'))):
                require(last_macro(check['command'],name)==str(value),'Effective compile policy '+name)
            macro_checks+=1
    require(macro_checks==8,'All eight effective compile commands checked')
    summaries=[]
    for row in rows:
        result=archive.role(row['result_role']);frozen=archive.role(row['freeze_role'])
        identities(archive,result);identities(archive,frozen)
        require(result['kind']==row['id'] and result['passed'] is True and result['error'] is None,
                'Successful stored integration result '+row['id'])
        require(same_identity(result['freeze'],index['roles'][row['freeze_role']]),'Exact integration input freeze')
        require(result['tests_are_host_approximations'] is True and result['Reason_SDK_or_Recon_run'] is False,
                'Host approximation, no SDK or Recon claim')
        require(row['expected_tests']==expected[row['id']] and len(result['commands'])==3,'Configure/build/test sequence')
        for command in result['commands']:require(command['exit_code']==0,'Stored integration command exit status')
        tests=[c for c in result['commands'] if Path(c['command'][0]).name=='ctest']
        require(len(tests)==1,'One bound CTest command')
        record=tests[0]['log'];log=archive.resolve(record['path'],record['sha256']).decode()
        counts=re.findall(r'100% tests passed(?:,\s*0 tests failed)? out of\s+(\d+)',log)
        require(counts==[str(row['expected_tests'])],'Stored complete CTest count')
        require(len(re.findall(r'\bPassed\b',log))==row['expected_tests'],'Every recorded test passed')
        # These historical checks intentionally bind the pre-format source.
        # A later formatting receipt may provide another hash for the same path.
        models=[r for r in frozen if r['path'].endswith('/src/full_instrument/PreparedModel.h')]
        require(len(models)==1 and models[0]['sha256']==reproduction['canonical_model_sha256'],
                'Integration uses its original source freeze, not mutable current files')
        summaries.append({'kind':row['id'],'stored_tests_passed':row['expected_tests'],
                          'tests_are_host_approximations':True,'Reason_SDK_or_Recon_run':False})
    if 'validation' in index['roles']:
        validation=archive.role('validation');identities(archive,validation)
        require(validation['reason_sdk_or_recon_validated'] is False and validation['realtime_qualified'] is False
                and validation['production_goal_complete'] is False,'Validation keeps qualification limits explicit')
        require(validation['policy']['minimum_median_callback_cpu_reduction_each_of_six_groups']==.05
                and validation['policy']['maximum_median_of_three_p95_callback_cpu_regression_any_group']==.05
                and validation['policy']['discarded_trials']==0,'Validation preserves declared performance policy')
        require([v['timing']['native_policy_pass'] for v in validation['variants']]==[False,True],
                'Validation keeps rejected scalar and successful native SIMD results')
    formatted=format_checks(archive,index,reproduction)
    return {'stored_test_receipts':summaries,'effective_compile_commands_checked':macro_checks,
            'source_equivalence_and_reproduction_receipts_verified':True,'qualified_v2_helper_bytes_exact':True,
            'native_renderer_flags_and_topology_verified':True,'format_only_addendum':formatted,
            'new_tests_executed_by_checker':False}


def verify(index):
    archive=reader.Archive(index);policy=archive.role('policy')
    require(policy['performance_outcomes_opened'] is False,'Policy predates timing outcomes')
    require('Atleast5percent' in policy['requirements']['material_throughput']
            and 'No morethan5percent' in policy['requirements']['callback_tail'],'Same predeclared5percent policy')
    studies=index['studies'];require([s['id'] for s in studies]==['v1','v2'],'Failed scalar and SIMD successor both retained')
    summaries=[];prior=None;protocols={};sources={};builds={};source_manifests={}
    for study in studies:
        prefix=study['role_prefix'];source_prefix=study['source_role_prefix'];role=lambda suffix:archive.role(prefix+'_'+suffix)
        p=role('protocol');build=role('build_receipt');correct=role('correctness_result');creview=role('correctness_review')
        perf=role('performance_result');preview=role('performance_review');auth=role('performance_authorization')
        source=archive.role(source_prefix+'_protocol')
        for obj in (p,build,correct,creview,perf,preview,auth,source):identities(archive,obj)
        require(all(same_identity(r,index['roles'][prefix+'_protocol']) for r in (build['protocol'],correct['protocol'],perf['protocol'],preview['protocol'],auth['protocol'])), 'Common frozen harness protocol')
        require(same_identity(p['candidate_source_protocol'],index['roles'][source_prefix+'_protocol']),'Source-only candidate binding')
        require(same_identity(creview['result'],index['roles'][prefix+'_correctness_result'])
                and same_identity(preview['performance_result'],index['roles'][prefix+'_performance_result'])
                and same_identity(auth['correctness_result'],index['roles'][prefix+'_correctness_result']),'Independent review/auth outcome bindings')
        require(same_identity(preview['decision_policy'],auth['decision_policy'])
                and same_identity(auth['decision_policy'],index['roles']['policy']),'Exact predeclared policy binding')
        cauth=json_at(archive,study['harness_root']+'/correctness-authorization.json');identities(archive,cauth)
        require('performance' in auth['actions'] and 'correctness' in cauth['actions']
                and same_identity(cauth['protocol'],index['roles'][prefix+'_protocol']),'Recorded exact execution authorizations')
        frozen_role=source_prefix+'_freeze'
        if frozen_role in index['roles']:
            frozen=archive.role(frozen_role)
        else:
            candidates=[reader.json_data(data) for _,data in archive.by_path.get(study['source_root']+'/freeze.json',[])]
            candidates=[f for f in candidates if same_identity(f['protocol'],index['roles'][source_prefix+'_protocol'])]
            require(candidates and all(f==candidates[0] for f in candidates),'Unambiguous final frozen source version')
            frozen=candidates[0]
        identities(archive,frozen)
        require(same_identity(frozen['protocol'],index['roles'][source_prefix+'_protocol']) and frozen['sources']==source['sources'],
                'Source freeze exact protocol and sources')
        manifest=reader.json_data(archive.resolve(source['snapshots_manifest']['path'],source['snapshots_manifest']['sha256']))
        for name,record in manifest.items():archive.identity(study['source_root']+'/'+name,record['sha256'],record['bytes'])
        source_manifests[study['id']]=manifest
        require(source['candidate_count']==1 and source['actual_Piano_constructed'] is False
                and source['actual_model_steps']==0 and source['sampling_rates_or_cases_executed']==[], 'Source preparation is not model qualification')
        kernel=source_json(archive,source,study['source_root']+'/kernel-parity.json')
        require(kernel['passed'] is True and kernel['Piano_constructed'] is False and kernel['bit_mismatches']==0
                and kernel['row_updates']==363600 and kernel['paired_state_fixtures']==16800
                and kernel['fallback_fixtures']==6720,'Manufactured paired kernel fixtures')
        compile_receipt=source_json(archive,source,study['source_root']+'/source-compile.json');identities(archive,compile_receipt)
        require(source['compile_and_synthetic']==compile_receipt,'Inline compile/synthetic evidence equals frozen receipt')
        if study['id']=='v2':
            require(compile_receipt['all_three_N_templates_vectorized_16byte_and_8byte'] is True
                    and compile_receipt['runtime_OMP_or_worker_symbols_emitted'] is False
                    and compile_receipt['actual_Piano_constructed'] is False and compile_receipt['actual_model_steps']==0,
                    'Recorded actual-API vectorization scope/no worker runtime')
            lines=compile_receipt['specific_fused_body_vectorization_lines']
            require(len(lines)==6 and sum('16 byte vectors' in s for s in lines)==3
                    and sum('8 byte vectors' in s for s in lines)==3,'All three template vectorization excerpts retained')
        else:
            require(compile_receipt['fused_row_loop_auto_vectorized_in_actual_API'] is False
                    and compile_receipt['fallback_uncovered_loop_vectorized'] is True,'Scalar predecessor vectorization failure retained')
        require(source['pressure_SIMD']==0 and source['fast_contact']==source['mechanism_cache']==1 and source['profile']==0,'Original scalar-pressure full model options')
        require(p['adopted'] is False and p['runtime_or_public_source_changes'] is False,'Private experiment status')
        require(p['correctness']['sample_rates']==[44100,48000,88200,96000]
                and p['correctness']['cases']==[*CASES,'silent-reset']
                and p['performance']['sample_rates']==[48000,96000]
                and p['performance']['cases']==list(CASES)
                and p['performance']['frame_counts']==[30720,30720,15360],'Unchanged frozen case/rate recipes')
        require(all(flag in p['flags'] for flag in COMMON_FLAGS),'Same full model build controls')
        if study['id']=='v2':require('-fopenmp-simd' in p['flags'] and '-DKEYRA_FULL_FREE_UNISON_SIMD=1' in p['flags'],'Common SIMD-only compiler controls')
        else:require('-fopenmp-simd' not in p['flags'] and '-DKEYRA_FULL_FREE_UNISON_SIMD=1' not in p['flags'],'Scalar predecessor retained')
        require(build['models_constructed']==build['model_frames']==build['model_timings']==0,'Build-only receipt has no model execution')
        require({(b['mode'],b['variant']) for b in build['builds']}=={(m,a) for m in ('correctness','performance') for a in ARMS},'Four native build identities')
        for b in build['builds']:
            require(all(flag in b['command'] for flag in p['flags']) and b['no_model_execution'] is True,'Both arms share frozen compiler flags')
            require('libgomp' not in b['dynamic_dependencies'] and 'libomp' not in b['dynamic_dependencies'],'No OpenMP worker runtime linked')
        c=correctness(archive,study,correct,creview,p);t=performance(archive,study,perf,preview,p)
        if prior:
            a,b=source_manifests[prior['id']],source_manifests[study['id']]
            require(a.keys()==b.keys() and [name for name in a if (a[name]['sha256'],a[name]['bytes'])!=(b[name]['sha256'],b[name]['bytes'])]
                    ==['candidate/src/full_instrument/FreeUnisonFusion.h'],'Only guarded pragma changes source snapshots')
            first=source_bytes(archive,sources[prior['id']],prior['source_root']+'/FreeUnisonFusion.h')
            second=source_bytes(archive,source,study['source_root']+'/FreeUnisonFusion.h')
            delta=(b'#if defined(KEYRA_FULL_FREE_UNISON_SIMD) && KEYRA_FULL_FREE_UNISON_SIMD && (defined(__GNUC__) || defined(__clang__))\n'
                   b'    #pragma omp simd\n#endif\n')
            require(second.count(delta)==1 and second.replace(delta,b'',1)==first,'No floating-point body or cache-layout delta')
            for name in ('harness.cpp','ObserverCapture.h','state_snapshot.inc','inventory.inc'):
                require(published(archive,study['harness_root']+'/'+name)==published(archive,prior['harness_root']+'/'+name),'Unchanged cross-study harness '+name)
            runners=[published(archive,s['harness_root']+'/run.py').decode() for s in (prior,study)]
            lines=[runner.splitlines(keepends=True) for runner in runners]
            prefixes=('CANDIDATE=','FLAGS=',"    if sha(CANDIDATE/'protocol.json')!=")
            for text,s,proto in zip(lines,(prior,study),(protocols[prior['id']],p)):
                for start in prefixes:require(sum(line.startswith(start) for line in text)==1,'Exactly three declared runner substitutions')
                flags=ast.literal_eval(next(line for line in text if line.startswith('FLAGS='))[6:])
                require(flags==proto['flags'],'Runner frozen flag list')
                require(next(line for line in text if line.startswith('CANDIDATE='))==f"CANDIDATE=OUT.parent/'{s['id']}'\n",'Runner source path change only')
                target=next(line for line in text if line.startswith(prefixes[2]))
                require(index['roles'][s['source_role_prefix']+'_protocol']['sha256'] in target,'Runner exact frozen source SHA')
            normalize=lambda text:[line for line in text if not line.startswith(prefixes)]
            require(normalize(lines[0])==normalize(lines[1]),'Runner differs only at three declared lines')
            for mode in ('correctness','performance'):
                a=next(b for b in builds[prior['id']]['builds'] if b['mode']==mode and b['variant']=='baseline')
                b=next(b for b in build['builds'] if b['mode']==mode and b['variant']=='baseline')
                require(a['binary']['sha256']==b['binary']['sha256'],'Cross-study baseline native binary identical')
        protocols[study['id']]=p;sources[study['id']]=source;builds[study['id']]=build;prior=study
        summaries.append({'study':study['id'],**c,**t})
    integration=integration_checks(archive,index)
    return {'verification_passed':True,'published_records_verified':archive.checked,'studies':summaries,
            'integration':integration,
            'native_binary_PCM_or_snapshot_decoded':False,'DSP_or_experiment_executed':False,
            'correctness_scope':'Recorded paired identity metadata and bound independent native-review receipts; omitted payload bytes are not reread.',
            'experiment_auto_adopted':False,
            'canonical_native_integration_verified':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=verify(reader.json_data((PACKAGE/'index.json').read_bytes()))
    if args.output:
        require(not args.output.exists(),'New output path required');args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
