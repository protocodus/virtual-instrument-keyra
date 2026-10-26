#!/usr/bin/env python3
"""Reproduce tracked build profiles and null their private model against the CLI.

Phase A verifies generation, numeric structure, topology and original event/HP
arithmetic. FullInstrument/controller/Reason integration is a separate phase.
Only stdlib Python is required; generation never imports/executes the fitter.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'src/full_instrument'
CONFIDENCE=HERE/'profiles/confidence_grand'
ORIGINAL_MODEL='edae57fb1bad84a9e632961726d3ab60b3c5c27474b0f1194bcc89462384ee36'
ORIGINAL_CAL='619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7'
FRAMES=8192
EVENTS=((0,'on',60,96),(63,'pedal',0,1),(64,'on',21,40),(65,'off',60,0),
        (96,'off',21,0),(127,'on',108,93),(128,'pedal',0,.6),(129,'off',108,0),
        (4096,'on',60,87),(4097,'off',60,0),(6000,'pedal',0,0))
HARNESS=r'''
#include "PreparedModel.h"
#include <cstdio>
struct Event {uint32_t frame;int kind,note;double value;};
constexpr Event events[]={@EVENTS@};
int main(int argc,char** argv){
  if(argc!=2)return1;
  grand::Options options;options.sampleRate=@RATE@;grand::Piano piano(options);
  if(piano.strings.size()!=230||piano.modeCount()!=17849||piano.board.size()!=475)return2;
  constexpr unsigned partitions[]={1,63,64,65,7,129};
  std::vector<float> output(2*@FRAMES@);unsigned frame=0,next=0,partition=0;
  std::array<double,2> previous{},hp{};
  const double pole=std::exp(-2*grand::pi*24/@RATE@);
  while(frame<@FRAMES@){
    while(next<sizeof(events)/sizeof(events[0])&&events[next].frame==frame){const auto& e=events[next++];
      if(e.kind==2)piano.pedalTarget=e.value;else if(e.kind==1)piano.noteOn(e.note,e.value);else piano.noteOff(e.note);}
    unsigned count=std::min<unsigned>(partitions[partition++%6],@FRAMES@-frame);
    if(next<sizeof(events)/sizeof(events[0]))count=std::min(count,events[next].frame-frame);
    if(!count)return3;
    for(unsigned j=0;j<count;++j){auto raw=piano.step(frame+j);for(unsigned ch=0;ch<2;++ch){
      hp[ch]=pole*(hp[ch]+raw[ch]-previous[ch]);previous[ch]=raw[ch];
      if(!std::isfinite(hp[ch]))return4;output[2*(frame+j)+ch]=static_cast<float>(hp[ch]);}}
    frame+=count;
  }
  if(piano.faultFlags)return5;
  std::FILE* file=std::fopen(argv[1],"wb");if(!file)return6;
  if(std::fwrite(output.data(),sizeof(float),output.size(),file)!=output.size())return7;
  std::fclose(file);return0;
}
'''.replace('return1','return 1').replace('return2','return 2').replace('return3','return 3').replace('return4','return 4').replace('return5','return 5').replace('return6','return 6').replace('return7','return 7').replace('return0','return 0')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def verify(rows):
    for row in rows:
        if sha(row['path'])!=row['sha256']:raise ValueError('Frozen input changed:'+row['path'])
def run(command):
    result=subprocess.run(list(map(str,command)),capture_output=True,text=True)
    if result.returncode:raise RuntimeError('Command failed: '+str(command)+'\n'+result.stdout+result.stderr)
    return result

def wav_payload(path,rate):
    data=Path(path).read_bytes()
    if data[:4]!=b'RIFF' or data[8:12]!=b'WAVE':raise ValueError('Not WAVE')
    offset=12;fmt=None;payload=None
    while offset+8<=len(data):
        kind,count=struct.unpack_from('<4sI',data,offset);chunk=data[offset+8:offset+8+count]
        if len(chunk)!=count:raise ValueError('Truncated WAVE')
        if kind==b'fmt ':fmt=struct.unpack_from('<HHIIHH',chunk)
        elif kind==b'data':payload=chunk
        offset+=8+count+(count&1)
    if not fmt or fmt[:3]!=(3,2,rate) or fmt[5]!=32 or payload is None or len(payload)!=FRAMES*8:
        raise ValueError('Unexpected float stereo payload')
    return payload


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',default='g++')
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-profile-phase-a/v2')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-profile-phase-a.json')
    args=parser.parse_args();out=args.output.resolve()
    if (ROOT/'out').resolve() not in out.parents:parser.error('Output must be under out/')
    if args.report.resolve().parent not in ((ROOT/'Validation').resolve(),out):parser.error('Report must be Validation/ or output root')
    out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('keyra_profile_generator',HERE/'generate_prepared_model.py')
    gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    paths=[Path(__file__),HERE/'generate_prepared_model.py',ROOT/'tests/full_profile_tests.cpp',HERE/'SelectedModel.h',
        HERE/'PreparedModel.h',HERE/'PreparedCalibration.h',HERE/'prepared_model_provenance.json',
        ROOT/'src/full_reference/grand.cpp',ROOT/'src/full_reference/calibration.h',
        ROOT/'tools/probe_full_precision.py',ROOT/'tools/fit_full_calibration.py',ROOT/'include/keyra/physics/ContactSolver.h']
    paths += [CONFIDENCE/n for n in ('calibration.json','PreparedCalibration.h','PreparedModel.h','profile_provenance.json','prepared_model_provenance.json')]
    config={'schema_version':1,'frozen_at_utc':now(),'inputs':[record(p) for p in paths],
        'compiler':run([args.compiler,'--version']).stdout.splitlines()[0],
        'phase':'A: generator and private prepared-model/CLI validation, not FullInstrument or Reason integration.',
        'rates':[48000,96000],'frames_per_parity_case':FRAMES,'numeric_fit_or_acquisition':False,
        'default_profile':'OriginalControl','candidate_promoted':False}
    freeze_path=out/'freeze.json'
    if freeze_path.exists():
        old=read(freeze_path);config.pop('frozen_at_utc');old.pop('frozen_at_utc')
        if old!=config:raise ValueError('Existing phase-A study inputs differ; choose a new output')
    else:write(freeze_path,config)
    frozen=read(freeze_path);verify(frozen['inputs'])
    if sha(HERE/'PreparedModel.h')!=ORIGINAL_MODEL or sha(HERE/'PreparedCalibration.h')!=ORIGINAL_CAL:
        raise ValueError('Original runtime model/calibration bytes changed')
    generation=[]
    for name,target in (('OriginalControl',HERE),('FrozenConfidenceGrand',CONFIDENCE)):
        folder=out/name;folder.mkdir(exist_ok=True)
        command=[sys.executable,'-S',HERE/'generate_prepared_model.py','--profile',name,'--output-dir',folder]
        run(command)
        for file in ('PreparedModel.h','PreparedCalibration.h','prepared_model_provenance.json'):
            if (folder/file).read_bytes()!=(target/file).read_bytes():raise ValueError(name+' generated '+file+' differs')
        generation.append({'profile':name,'command':list(map(str,command)),
            'matches_tracked_model_calibration_and_provenance_exact':True,
            'stdlib_only_python_S':True,'outputs':[record(folder/f) for f in ('PreparedModel.h','PreparedCalibration.h','prepared_model_provenance.json')]})
    profile=read(CONFIDENCE/'calibration.json');invalid=[]
    mutations={
        'wrong_anchor_inventory':lambda p:p['keys'].reverse(),
        'short_array':lambda p:p['keys'][0]['sigma_late'].pop(),
        'nonfinite_radiation':lambda p:p['keys'][0]['radiation_db'].__setitem__(0,float('nan')),
        'nonpositive_scalar':lambda p:p['keys'][0].__setitem__('hardness',0),
        'prompt_below_late':lambda p:p['keys'][0]['sigma_prompt'].__setitem__(0,p['keys'][0]['sigma_late'][0]*.5),
        'boolean_numeric':lambda p:p['keys'][0].__setitem__('f1_hz',True)}
    for name,mutation in mutations.items():
        candidate=copy.deepcopy(profile);mutation(candidate)
        try:gen.confidence_calibration(candidate)
        except ValueError:invalid.append(name)
        else:raise ValueError('Invalid profile accepted:'+name)
    for source in ('absent token','site site'):
        try:gen.replace(source,'site','replacement')
        except ValueError:pass
        else:raise ValueError('Source match-count guard failed')
    before=sha(HERE/'PreparedModel.h')
    blocked=subprocess.run([sys.executable,'-S',str(HERE/'generate_prepared_model.py'),
        '--profile','FrozenConfidenceGrand','--output-dir',str(HERE)],capture_output=True,text=True)
    if not blocked.returncode or sha(HERE/'PreparedModel.h')!=before:raise ValueError('Candidate could overwrite control')
    candidate_double,calibration,_=gen.frozen_confidence_inputs()
    reference=out/'reference';reference.mkdir(exist_ok=True)
    (reference/'grand.cpp').write_text(gen.hot_precision(candidate_double.decode()))
    (reference/'calibration.h').write_bytes(calibration)
    if sha(reference/'grand.cpp')!=gen.PINNED_CANDIDATE_HOT:raise ValueError('Frozen hot source differs')
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    constrained=['-fno-exceptions','-fno-rtti','-fno-builtin','-DKEYRA_FULL_FAST_CONTACT=0','-DKEYRA_FULL_PRESSURE_SIMD=0']
    commands=[]
    def compile(command):commands.append(list(map(str,command)));return run(command)
    compile([args.compiler,*flags,reference/'grand.cpp','-o',reference/'render'])
    structural=[]
    for name,anchors,modes in (('OriginalControl',5,17778),('FrozenConfidenceGrand',17,17849)):
        folder=out/name
        executable=folder/'profile-tests'
        command=[args.compiler,*flags,*constrained,'-I'+str(ROOT/'include'),
            '-DKEYRA_PROFILE_MODEL_HEADER="'+str(folder/'PreparedModel.h')+'"',
            '-DKEYRA_PROFILE_EXPECT_ANCHORS='+str(anchors),'-DKEYRA_PROFILE_EXPECT_STRING_MODES='+str(modes),
            ROOT/'tests/full_profile_tests.cpp','-o',executable]
        compile(command);result=run([executable])
        structural.append({'profile':name,'passed':True,'stdout':result.stdout,'binary':record(executable)})
    parity=[]
    event_code=','.join('{'+f'{frame},{2 if kind=="pedal" else 1 if kind=="on" else 0},{note},{value}'+'}' for frame,kind,note,value in EVENTS)
    for rate in (48000,96000):
        folder=out/str(rate);folder.mkdir(exist_ok=True)
        (folder/'events.txt').write_text(''.join(f'{frame/rate:.17g} {kind} {note} {value}\n' for frame,kind,note,value in EVENTS))
        (folder/'private.cpp').write_text(HARNESS.replace('@EVENTS@',event_code).replace('@RATE@',str(rate)).replace('@FRAMES@',str(FRAMES)))
        compile([args.compiler,*flags,*constrained,'-I'+str(ROOT/'include'),'-I'+str(out/'FrozenConfidenceGrand'),folder/'private.cpp','-o',folder/'private'])
        run([folder/'private',folder/'private.f32'])
        cli=run([reference/'render','--events',folder/'events.txt','--output',folder/'reference.wav',
            '--sample-rate',str(rate),'--duration',format((FRAMES-.5)/rate,'.17g')])
        payload=wav_payload(folder/'reference.wav',rate);private=(folder/'private.f32').read_bytes()
        if payload!=private:raise ValueError('Candidate private model/CLI null failed at'+str(rate))
        metrics=json.loads(cli.stdout)
        if metrics['string_modes']!=17849 or metrics['nonfinite_samples']:raise ValueError('Candidate CLI topology/finiteness')
        parity.append({'rate':rate,'frames':FRAMES,'bit_identical_float32':True,
            'audio_sha256':hashlib.sha256(payload).hexdigest(),'cli_metrics':metrics,
            'outputs':[record(folder/'reference.wav'),record(folder/'private.f32')]})
    verify(frozen['inputs'])
    result={'schema_version':1,'passed':True,'completed_at_utc':now(),'freeze':record(freeze_path),
        'generation':generation,'invalid_profile_guards_passed':invalid,
        'source_match_count_guards_passed':True,'candidate_cannot_overwrite_control':True,
        'original_model_and_calibration_exact':True,'structural_tests':structural,'candidate_cli_parity':parity,
        'reference_source':record(reference/'grand.cpp'),'reference_calibration':record(reference/'calibration.h'),
        'compiler':frozen['compiler'],'compile_commands':commands,
        'full_instrument_reason_native_scalar_asan_integration':'Pending Phase B after cache source ownership release.',
        'numeric_fit_or_acquisition':False,'candidate_promoted':False}
    write(out/'report.json',result);write(args.report,result)
    print(json.dumps({'passed':True,'generator_profiles':2,'invalid_profiles_rejected':len(invalid),
        'private_cli_exact_rates':[r['rate'] for r in parity],'phase':'A only; public API/Reason PhaseB pending'},indent=2))


if __name__=='__main__':main()
