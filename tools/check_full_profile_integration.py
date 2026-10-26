#!/usr/bin/env python3
"""Build/test actual FullInstrument profiles; keep original control as default.

Runs focused native/scalar API and private profile tests, plus the candidate's
actual API/private-profile ASAN/UBSAN checks. Original control ASAN coverage is
retained from the unchanged mechanism-cache validation and is not repeated.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text())
def write(p,value):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def verify(rows):
    for row in rows:
        if sha(row['path'])!=row['sha256']:raise ValueError('Frozen source changed:'+row['path'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmake',default='/home/agent/.local/bin/cmake')
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-profile-integration')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-profile-integration.json')
    args=parser.parse_args();out=args.output.resolve()
    if (ROOT/'out').resolve() not in out.parents:parser.error('Output must be under out/')
    out.mkdir(parents=True,exist_ok=True)
    paths=[Path(__file__),ROOT/'CMakeLists.txt',ROOT/'include/keyra/FullInstrument.h',
        ROOT/'include/keyra/physics/StrikeController.h',ROOT/'include/keyra/physics/MechanismExciter.h',
        ROOT/'include/keyra/physics/ContactSolver.h',ROOT/'tests/full_instrument_tests.cpp',
        ROOT/'tests/full_profile_tests.cpp',ROOT/'tools/render_full.cpp']
    paths += [ROOT/'src/full_instrument'/n for n in ('FullInstrument.cpp','SelectedModel.h','FullModelProfile.cmake',
        'MechanismBodyCache.h','PreparedModel.h','PreparedCalibration.h','prepared_model_provenance.json',
        'generate_prepared_model.py')]
    paths += [ROOT/'src/full_instrument/profiles/confidence_grand'/n for n in
        ('calibration.json','PreparedModel.h','PreparedCalibration.h','prepared_model_provenance.json','profile_provenance.json')]
    config={'schema_version':1,'frozen_at_utc':now(),'inputs':[record(p) for p in paths],
        'profiles':['OriginalControl','FrozenConfidenceGrand'],'fast_contact':True,'mechanism_cache':True,'pressure_simd':False,
        'plan':'Native/scalar actual API and private profile tests for both; candidate actual API/private profile ASAN/UBSAN once; build both offline renderers.',
        'fit_acquisition_or_reference_decode':False,'default_profile':'OriginalControl','candidate_promoted':False}
    freeze=out/'freeze.json'
    if freeze.exists():
        old=read(freeze);old.pop('frozen_at_utc');new=dict(config);new.pop('frozen_at_utc')
        if old!=new:raise ValueError('Study inputs changed; choose a new output folder')
    else:
        write(freeze,config)
        copies=[]
        for row in config['inputs']:
            target=out/'source_snapshot'/Path(row['path']).relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(row['path'],target);copies.append({'original':row,'snapshot':record(target)})
        write(out/'source-snapshot.json',{'files':copies})
    frozen=read(freeze);verify(frozen['inputs']);results=[]
    common=['-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=ON','-DKEYRA_BUILD_REFERENCE=OFF',
        '-DKEYRA_BUILD_FULL_REFERENCE=OFF','-DKEYRA_BUILD_PHYSICAL=OFF','-DKEYRA_BUILD_CLAP=OFF',
        '-DKEYRA_BUILD_VST3=OFF','-DKEYRA_BUILD_FULL_BACKEND=ON','-DKEYRA_FULL_FAST_CONTACT=ON',
        '-DKEYRA_FULL_MECHANISM_CACHE=ON','-DKEYRA_FULL_PRESSURE_SIMD=OFF']
    for name,profile,asan in (('control','OriginalControl',False),('confidence','FrozenConfidenceGrand',False),
                              ('confidence-asan','FrozenConfidenceGrand',True)):
        folder=out/name;receipt=out/(name+'-result.json')
        if receipt.exists():
            old=read(receipt);verify(old['artifacts']);results.append(old);continue
        commands=[]
        def run(cmd,label,env=None):
            verify(frozen['inputs']);print(name+' '+label,flush=True)
            call=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,env=env)
            log=out/(name+'-'+label+'.log');log.write_text(call.stdout+call.stderr);commands.append({'command':list(map(str,cmd)),'log':record(log),'exit_code':call.returncode})
            if call.returncode:raise RuntimeError('Failed '+str(log))
            verify(frozen['inputs']);return call
        configure=[args.cmake,'-S',ROOT,'-B',folder,*common]
        if profile!='OriginalControl':configure.append('-DKEYRA_FULL_MODEL_PROFILE='+profile)
        configure.append('-DKEYRA_SANITIZERS='+('ON' if asan else 'OFF'))
        run(configure,'configure')
        targets=['keyra_full_instrument_tests','keyra_full_profile_tests']
        if not asan:targets+=['keyra_full_sdk_compat_tests','keyra_full_render']
        run([args.cmake,'--build',folder,'--target',*targets,'-j','2'],'build')
        env=os.environ.copy()
        if asan:
            env['ASAN_OPTIONS']='detect_leaks=1:strict_string_checks=1'
            env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
        regex='^(full_instrument|full_model_profile)$' if asan else '^(full_instrument|full_model_profile|full_sdk_portable)$'
        run(['ctest','--test-dir',folder,'--output-on-failure','-R',regex],'tests',env)
        result={'profile':profile,'default_profile_option_omitted':name=='control','asan_ubsan':asan,
            'passed':True,'commands':commands,'artifacts':[record(folder/t) for t in targets],
            'native_scalar_api_tests':not asan,'private_profile_tests':True,
            'expected_topology':{'strings':230,'string_modes':17778 if profile=='OriginalControl' else 17849,'board_modes':475}}
        write(receipt,result);results.append(result)
    verify(frozen['inputs'])
    result={'schema_version':1,'passed':True,'completed_at_utc':now(),'freeze':record(freeze),
        'source_snapshot':record(out/'source-snapshot.json'),'cases':results,
        'default_profile':'OriginalControl','candidate_opt_in':True,'candidate_promoted':False,
        'fast_contact':True,'mechanism_cache':True,'pressure_simd':False,
        'coverage':'Actual block API validation, block partitions, reset/independence, seeded humanization, repetitions/touching notes, virgin hammer, allocations, four rates, mechanism isolation and cache reprepare/reset; private topology/anchors and reset/no-fault checks.',
        'unchanged_control_asan':'Covered by the preserved actual API mechanism-cache matrix before the header-selector-only edit; candidate dimensions/paths receive new ASAN coverage here.',
        'limits':['Engineering build profile; no listening approval, new fit, acquisition or reference decode.',
            'No realtime/Reason SDK-host qualification; sibling SDK-free wrapper results recorded separately.',
            'Calibration retains known A0/C2/C8 recording-agreement problems.']}
    write(out/'report.json',result);write(args.report,result)
    print(json.dumps({'passed':True,'native_scalar_profiles':2,'candidate_asan':True,
        'control_renderer':str(out/'control/keyra_full_render'),
        'candidate_renderer':str(out/'confidence/keyra_full_render')},indent=2))


if __name__=='__main__':main()
