#!/usr/bin/env python3
"""Null the opt-in confidence FullInstrument API against its frozen full CLI.

Only stdlib Python is used. No recording, fit, acquisition or runtime audio
loading is involved. Existing original-control parity tooling remains untouched.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT/'src/full_instrument'
PROFILE = CORE/'profiles/confidence_grand'
FRAMES = 8192
RATES = (48000, 96000)
EVENTS = (
    (0, 'on', 60, 96), (63, 'pedal', 0, 1), (64, 'on', 21, 40),
    (65, 'off', 60, 0), (96, 'off', 21, 0), (127, 'on', 108, 93),
    (128, 'pedal', 0, .6), (129, 'off', 108, 0),
    (4096, 'on', 60, 87), (4097, 'off', 60, 0), (6000, 'pedal', 0, 0),
)
PARTITIONS = (1, 63, 64, 65, 7, 129)

HARNESS = r'''
#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdint>
struct Event { uint32_t frame;int kind,note;double value; };
constexpr Event events[]={ @EVENTS@ };
int main(int argc,char** argv){
  if(argc!=2)return 1;
  keyra::FullInstrument piano;keyra::FullInstrumentConfig config;
  config.sampleRate=@RATE@;config.repetitionController=false;
  config.mechanismBodyCoupling=false;config.mechanismObservation=false;
  config.parameters.humanization=0;config.parameters.dynamics=.5;
  config.parameters.mechanicalLevel=0;config.parameters.gainDb=0;
  config.parameters.stereoWidth=1;
  if(!piano.prepare(config))return 2;
  auto topology=piano.diagnostics();
  if(topology.stringCount!=230||topology.stringModes!=17849||topology.boardModes!=475)return 3;
  std::FILE* file=std::fopen(argv[1],"wb");if(!file)return 4;
  constexpr uint32_t partitions[]={1,63,64,65,7,129};
  std::array<float,129> left{},right{};
  uint32_t frame=0;unsigned next=0,partition=0;
  while(frame<@FRAMES@){
    while(next<sizeof(events)/sizeof(events[0])&&events[next].frame==frame){
      const auto& e=events[next++];bool ok=e.kind==2?piano.sustain(e.value):
        e.kind==1?piano.noteOn(e.note,e.value/127.):piano.noteOff(e.note);
      if(!ok)return 5;
    }
    uint32_t count=std::min<uint32_t>(partitions[partition++%6],@FRAMES@-frame);
    if(next<sizeof(events)/sizeof(events[0]))count=std::min(count,events[next].frame-frame);
    if(!count||!piano.process(left.data(),right.data(),count))return 6;
    for(uint32_t i=0;i<count;++i){
      if(!std::isfinite(left[i])||!std::isfinite(right[i]))return 7;
      float stereo[]={left[i],right[i]};
      if(std::fwrite(stereo,sizeof(float),2,file)!=2)return 8;
    }
    frame+=count;
  }
  if(std::fclose(file))return 9;
  const auto d=piano.diagnostics();
  if(d.frames!=@FRAMES@||d.requests!=4||d.launches!=4||d.faultFlags||
      d.bridgeFaults||d.contactFaults||d.nonfiniteOutputFaults||d.unsafeLaunches||
      d.rejectedInputs||d.stringCount!=230||d.stringModes!=17849||d.boardModes!=475)return 10;
  std::printf("{\"frames\":%llu,\"requests\":%llu,\"launches\":%llu,"
    "\"fault_flags\":%u,\"bridge_faults\":%llu,\"contact_faults\":%llu,"
    "\"output_faults\":%llu,\"unsafe_launches\":%llu,\"rejected_inputs\":%llu,"
    "\"strings\":%u,\"string_modes\":%u,\"board_modes\":%u}\n",
    static_cast<unsigned long long>(d.frames),static_cast<unsigned long long>(d.requests),
    static_cast<unsigned long long>(d.launches),d.faultFlags,
    static_cast<unsigned long long>(d.bridgeFaults),static_cast<unsigned long long>(d.contactFaults),
    static_cast<unsigned long long>(d.nonfiniteOutputFaults),static_cast<unsigned long long>(d.unsafeLaunches),
    static_cast<unsigned long long>(d.rejectedInputs),d.stringCount,d.stringModes,d.boardModes);
  return 0;
}
'''


def now(): return datetime.now(timezone.utc).isoformat()
def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def record(path): return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def write(path, value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def verify(records):
    for row in records:
        if sha(row['path'])!=row['sha256']:
            raise ValueError('Frozen input changed: '+row['path'])
def run(command, log):
    result=subprocess.run(list(map(str,command)),capture_output=True,text=True)
    Path(str(log)+'.stdout.txt').write_text(result.stdout)
    Path(str(log)+'.stderr.txt').write_text(result.stderr)
    if result.returncode:
        raise RuntimeError('Command failed: '+str(command)+'; see '+str(log)+'.stderr.txt')
    return result


def wav_payload(path, rate):
    data=Path(path).read_bytes()
    if data[:4]!=b'RIFF' or data[8:12]!=b'WAVE':raise ValueError('Expected RIFF WAVE')
    offset=12;fmt=None;payload=None
    while offset+8<=len(data):
        kind,count=struct.unpack_from('<4sI',data,offset)
        chunk=data[offset+8:offset+8+count]
        if len(chunk)!=count:raise ValueError('Truncated WAVE chunk')
        if kind==b'fmt ':fmt=struct.unpack_from('<HHIIHH',chunk)
        elif kind==b'data':payload=chunk
        offset+=8+count+(count&1)
    if not fmt or fmt[:3]!=(3,2,rate) or fmt[5]!=32 or payload is None or len(payload)!=FRAMES*8:
        raise ValueError('Unexpected float32 stereo WAVE dimensions')
    return payload


def null_metrics(reference, candidate):
    if len(reference)!=len(candidate) or len(reference)%4:raise ValueError('Null payload size differs')
    a=struct.unpack('<'+'f'*(len(reference)//4),reference)
    b=struct.unpack('<'+'f'*(len(candidate)//4),candidate)
    if not all(math.isfinite(v) for v in (*a,*b)):raise ValueError('Nonfinite null payload')
    reference_square=math.fsum(v*v for v in a)
    error_square=math.fsum((x-y)*(x-y) for x,y in zip(a,b))
    peak=max(abs(v) for v in a)
    error_peak=max(abs(x-y) for x,y in zip(a,b))
    ratio=math.sqrt(error_square/reference_square) if reference_square else (0. if error_square==0 else None)
    return {'bit_identical_float32':reference==candidate,
        'maximum_absolute_difference':error_peak,
        'reference_peak':peak,
        'maximum_difference_relative_to_reference_peak':error_peak/peak if peak else (0. if error_peak==0 else None),
        'rms_difference_relative_to_reference':ratio,
        'null_db_relative_to_reference_rms':None if ratio in (None,0) else 20*math.log10(ratio),
        'zero_error':error_square==0,
        'reference_payload_sha256':hashlib.sha256(reference).hexdigest(),
        'facade_payload_sha256':hashlib.sha256(candidate).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',default='g++')
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-profile-api-parity/v1')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-profile-api-parity.json')
    args=parser.parse_args();out=args.output.resolve();report=args.report.resolve()
    if (ROOT/'out').resolve() not in out.parents:parser.error('Output must be under out/')
    if report.parent not in ((ROOT/'Validation').resolve(),out):parser.error('Report must be Validation/ or output root')
    if '#include "SelectedModel.h"' not in (CORE/'FullInstrument.cpp').read_text():
        raise ValueError('Phase B selector is not yet connected to FullInstrument.cpp; do not freeze this source')
    out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('keyra_confidence_api_generator',CORE/'generate_prepared_model.py')
    gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    paths=[Path(__file__),CORE/'FullInstrument.cpp',ROOT/'include/keyra/FullInstrument.h',
        CORE/'MechanismBodyCache.h',CORE/'SelectedModel.h',CORE/'generate_prepared_model.py',
        CORE/'PreparedModel.h',CORE/'PreparedCalibration.h',
        ROOT/'include/keyra/physics/StrikeController.h',ROOT/'include/keyra/physics/MechanismExciter.h',
        ROOT/'include/keyra/physics/ContactSolver.h',ROOT/'src/full_reference/grand.cpp',
        ROOT/'src/full_reference/calibration.h',ROOT/'tools/probe_full_precision.py',ROOT/'tools/fit_full_calibration.py']
    paths += [PROFILE/name for name in ('calibration.json','PreparedModel.h','PreparedCalibration.h',
                                      'profile_provenance.json','prepared_model_provenance.json')]
    compiler_result=run([args.compiler,'--version'],out/'compiler-version')
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    facade_flags=['-fno-exceptions','-fno-rtti','-fno-builtin',
                  '-UKEYRA_FULL_MODEL_PROFILE','-DKEYRA_FULL_MODEL_PROFILE=1',
                  '-UKEYRA_FULL_MECHANISM_CACHE','-DKEYRA_FULL_MECHANISM_CACHE=1',
                  '-UKEYRA_FULL_PRESSURE_SIMD','-DKEYRA_FULL_PRESSURE_SIMD=0']
    config={'schema_version':1,'frozen_at_utc':now(),'inputs':[record(p) for p in paths],
        'compiler':compiler_result.stdout.splitlines()[0],'compiler_command':args.compiler,
        'flags':flags,'facade_flags':facade_flags,'fast_contact_branches':[0,1],
        'rates':list(RATES),'frames_per_case':FRAMES,'event_frames':[e[0] for e in EVENTS],
        'events':[{'frame':f,'kind':k,'note':n,'value':v} for f,k,n,v in EVENTS],
        'irregular_block_frames':list(PARTITIONS),
        'configuration':{'repetition_controller':False,'humanization':0,'mechanical_level':0,
            'mechanism_body_coupling':False,'mechanism_observation':False,'dynamics':.5,'width':1,'gain_db':0},
        'strict_parity':'FAST0 must produce byte-identical float32 against the actual frozen hot CLI event/WAV path.',
        'fast1_diagnostic_bounds':{'maximum_relative_rms_error':1e-5,'maximum_difference_relative_to_reference_peak':1e-5,
            'interpretation':'Conservative numerical regression bounds; no audibility or perceptual-parity claim.'},
        'profile':'FrozenConfidenceGrand','profile_default_promoted':False,
        'scope':'Actual FullInstrument facade with isolation controls against frozen offline fitted source; no recording decode, fitting or acquisition.'}
    freeze_path=out/'freeze.json'
    if freeze_path.exists():
        old=read(freeze_path);old.pop('frozen_at_utc');compare=dict(config);compare.pop('frozen_at_utc')
        if old!=compare:raise ValueError('Frozen inputs/protocol differ; choose a new output directory')
    else:write(freeze_path,config)
    frozen=read(freeze_path);verify(frozen['inputs'])
    double_source,calibration,metadata=gen.frozen_confidence_inputs()
    hot_source=gen.hot_precision(double_source.decode())
    if hashlib.sha256(hot_source.encode()).hexdigest()!=gen.PINNED_CANDIDATE_HOT:
        raise ValueError('Frozen candidate hot source differs')
    reference=out/'reference';reference.mkdir(exist_ok=True)
    (reference/'grand.cpp').write_text(hot_source)
    (reference/'calibration.h').write_bytes(calibration)
    commands=[]
    def compile(command,log):
        commands.append(list(map(str,command)));return run(command,log)
    compile([args.compiler,*flags,reference/'grand.cpp','-o',reference/'render'],reference/'compile')
    cases=[]
    event_code=','.join('{'+f'{frame},{2 if kind=="pedal" else 1 if kind=="on" else 0},{note},{value}'+'}'
                        for frame,kind,note,value in EVENTS)
    for rate in RATES:
        folder=out/str(rate);folder.mkdir(exist_ok=True)
        events=folder/'events.txt'
        events.write_text(''.join(f'{frame/rate:.17g} {kind} {note} {value}\n' for frame,kind,note,value in EVENTS))
        cli_command=[reference/'render','--events',events,'--output',folder/'reference.wav',
            '--sample-rate',str(rate),'--duration',format((FRAMES-.5)/rate,'.17g')]
        cli=run(cli_command,folder/'reference-run');cli_metrics=json.loads(cli.stdout)
        if cli_metrics['string_count']!=230 or cli_metrics['string_modes']!=17849 or cli_metrics['board_modes']!=475 or cli_metrics['nonfinite_samples']:
            raise ValueError('Frozen CLI topology/finiteness differs')
        payload=wav_payload(folder/'reference.wav',rate)
        harness=folder/'facade.cpp';harness.write_text(HARNESS.replace('@EVENTS@',event_code)
            .replace('@RATE@',str(rate)).replace('@FRAMES@',str(FRAMES)))
        for fast in (0,1):
            prefix=folder/('fast'+str(fast))
            command=[args.compiler,*flags,*facade_flags,
                '-UKEYRA_FULL_FAST_CONTACT','-DKEYRA_FULL_FAST_CONTACT='+str(fast),
                '-I'+str(ROOT/'include'),harness,CORE/'FullInstrument.cpp','-o',prefix]
            compile(command,str(prefix)+'-compile')
            facade=run([prefix,str(prefix)+'.f32'],str(prefix)+'-run')
            diagnostics=json.loads(facade.stdout)
            raw=Path(str(prefix)+'.f32').read_bytes();null=null_metrics(payload,raw)
            if fast==0 and not null['bit_identical_float32']:
                raise ValueError('FAST0 actual API/CLI float32 null failed at '+str(rate)+': '+str(null))
            if fast==1 and (null['rms_difference_relative_to_reference'] is None or
                    null['rms_difference_relative_to_reference']>1e-5 or
                    null['maximum_difference_relative_to_reference_peak']>1e-5):
                raise ValueError('FAST1 exceeded frozen numerical regression bounds at '+str(rate)+': '+str(null))
            cases.append({'rate':rate,'fast_contact':fast,'null':null,'facade_diagnostics':diagnostics,
                'cli_metrics':cli_metrics,'reference_command':list(map(str,cli_command)),
                'events':record(events),'harness':record(harness),'facade_binary':record(prefix),
                'outputs':[record(folder/'reference.wav'),record(str(prefix)+'.f32')]})
            print(str(rate)+' FAST'+str(fast)+' exact='+str(null['bit_identical_float32']),flush=True)
    verify(frozen['inputs'])
    result={'schema_version':1,'passed':True,'completed_at_utc':now(),'freeze':record(freeze_path),
        'profile':metadata,'generator_input_identities_verified':True,
        'reference_source':record(reference/'grand.cpp'),'reference_calibration':record(reference/'calibration.h'),
        'reference_binary':record(reference/'render'),'cases':cases,'compile_commands':commands,
        'all_fast0_float_payloads_exact':all(r['null']['bit_identical_float32'] for r in cases if r['fast_contact']==0),
        'all_fast1_float_payloads_exact':all(r['null']['bit_identical_float32'] for r in cases if r['fast_contact']==1),
        'original_control_bytes_preserved':sha(CORE/'PreparedModel.h')=='edae57fb1bad84a9e632961726d3ab60b3c5c27474b0f1194bcc89462384ee36' and sha(CORE/'PreparedCalibration.h')==gen.PINNED_CALIBRATION,
        'scope':frozen['scope'],'native_scalar_asan_reason_validation':'Separate integration checks; not established by this parity tool.',
        'numeric_fit_or_acquisition_or_recording_decode':False,'default_promoted':False,
        'audibility_or_perceptual_qualification':False}
    if not result['original_control_bytes_preserved']:raise ValueError('Original control bytes changed')
    write(out/'report.json',result);write(report,result)
    print(json.dumps({'passed':True,'strict_rates':list(RATES),
        'FAST1_exact':result['all_fast1_float_payloads_exact'],'report':str(report)},indent=2))


if __name__=='__main__':main()
