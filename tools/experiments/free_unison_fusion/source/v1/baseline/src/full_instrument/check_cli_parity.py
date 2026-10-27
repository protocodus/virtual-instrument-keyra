#!/usr/bin/env python3
"""Optional full-backend null test against the actual hot-float reference CLI.

Builds a temporary full CLI using the exact checked-in hot_precision transform,
invokes its event/WAV path (including the original 24 Hz high-pass), and compares
its float payload byte-for-byte with irregular facade blocks. No recording,
Research source, immutable control source or calibration is modified.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FRAMES = 8192
EVENTS = [
    (0, 'on', 60, 96), (63, 'pedal', 0, 1), (64, 'on', 21, 32),
    (65, 'off', 60, 0), (96, 'off', 21, 0), (127, 'on', 96, 110),
    (128, 'pedal', 0, .6), (129, 'off', 96, 0),
    (4096, 'on', 60, 87), (4097, 'off', 60, 0), (6000, 'pedal', 0, 0),
]

HARNESS = r'''
#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdint>
#include <vector>
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
  std::FILE* file=std::fopen(argv[1],"wb");if(!file)return 3;
  constexpr uint32_t partitions[]={1,63,64,65,7,129};
  std::array<float,129> left{},right{};
  uint32_t frame=0;unsigned next=0,partition=0;
  while(frame<@FRAMES@){
    while(next<sizeof(events)/sizeof(events[0])&&events[next].frame==frame){
      const auto& e=events[next++];bool ok=e.kind==2?piano.sustain(e.value):
        e.kind==1?piano.noteOn(e.note,e.value/127.):piano.noteOff(e.note);
      if(!ok)return 4;
    }
    uint32_t count=std::min<uint32_t>(partitions[partition++%6],@FRAMES@-frame);
    if(next<sizeof(events)/sizeof(events[0]))count=std::min(count,events[next].frame-frame);
    if(!piano.process(left.data(),right.data(),count))return 5;
    for(uint32_t i=0;i<count;++i){float stereo[]={left[i],right[i]};
      if(std::fwrite(stereo,sizeof(float),2,file)!=2)return 6;}
    frame+=count;
  }
  std::fclose(file);const auto d=piano.diagnostics();
  if(d.frames!=@FRAMES@||d.faultFlags||d.unsafeLaunches||d.rejectedInputs||
      d.stringCount!=230||d.stringModes!=17778||d.boardModes!=475)return 7;
  return 0;
}
'''

FAULT_HARNESS = r'''
#include "PreparedModel.h"
#include <limits>
int main(){
  grand::Options options;options.sampleRate=48000;grand::Piano piano(options);
  auto& key=piano.keys[39];
  key.K=std::numeric_limits<double>::quiet_NaN();key.hammerActive=true;key.hammerV=1;
  if(piano.contact(key,.001,.001)!=0||key.hammerActive||
      piano.faultFlags!=grand::Piano::FaultContact||piano.contactFaults!=1)return 1;
  piano.boardGram[0][0]=std::numeric_limits<double>::quiet_NaN();
  piano.bridgeStep(piano.dt,true);
  if(piano.faultFlags!=(grand::Piano::FaultBridge|grand::Piano::FaultContact)||
      piano.bridgeFaults!=1)return 2;
  for(const auto& string:piano.strings){
    if(string.force||string.velocity)return 3;
    for(float value:string.m.q)if(value!=0)return 4;
    for(float value:string.m.p)if(value!=0)return 5;
    for(double value:string.cachedRadiation)if(value!=0)return 6;
  }
  for(const auto& mode:piano.board)if(mode.force||mode.q||mode.p)return 7;
  auto* pointer=piano.unisonPorts.front().velocityState[0];
  piano.resetState();
  if(piano.faultFlags||piano.bridgeFaults||piano.contactFaults||
      pointer!=piano.unisonPorts.front().velocityState[0])return 8;
  return 0;
}
'''


def run(command):
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError('Command failed: '+shlex.join(str(x) for x in command)+
                           '\n'+result.stdout+result.stderr)
    return result.stdout, result.stderr


def wav_payload(path, rate):
    data = path.read_bytes()
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError('Reference output is not a RIFF WAVE')
    offset, payload, fmt = 12, None, None
    while offset+8<=len(data):
        kind, count = struct.unpack_from('<4sI', data, offset)
        chunk = data[offset+8:offset+8+count]
        if len(chunk)!=count:
            raise ValueError('Truncated WAV chunk')
        if kind==b'fmt ':
            fmt=struct.unpack_from('<HHIIHH',chunk)
        elif kind==b'data':
            payload=chunk
        offset+=8+count+(count&1)
    if not fmt or fmt[0:3]!=(3,2,rate) or fmt[5]!=32:
        raise ValueError('Expected float32 stereo reference WAV')
    if payload is None or len(payload)!=FRAMES*2*4:
        raise ValueError('Reference WAV frame count differs')
    return payload


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',default='c++')
    parser.add_argument('--sample-rate',type=int,choices=(48000,96000),default=48000)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'out/full-backend-parity')
    args=parser.parse_args();folder=args.output_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('prepared_model_generator',HERE/'generate_prepared_model.py')
    generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
    source=(ROOT/'src/full_reference/grand.cpp').read_bytes()
    calibration=(ROOT/'src/full_reference/calibration.h').read_bytes()
    if hashlib.sha256(source).hexdigest()!=generator.PINNED_SOURCE or \
       hashlib.sha256(calibration).hexdigest()!=generator.PINNED_CALIBRATION:
        raise ValueError('Pinned control hashes differ')
    (folder/'reference.cpp').write_text(generator.hot_precision(source.decode()))
    (folder/'calibration.h').write_bytes(calibration)
    (folder/'events.txt').write_text(''.join(f'{frame/args.sample_rate:.17g} {kind} {note} {value}\n'
                                          for frame,kind,note,value in EVENTS))
    event_code=','.join('{'+f'{frame},{2 if kind=="pedal" else 1 if kind=="on" else 0},{note},{value}'+'}'
                        for frame,kind,note,value in EVENTS)
    (folder/'facade.cpp').write_text(HARNESS.replace('@EVENTS@',event_code)
        .replace('@RATE@',str(args.sample_rate)).replace('@FRAMES@',str(FRAMES)))
    (folder/'faults.cpp').write_text(FAULT_HARNESS)
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    constrained=['-fno-exceptions','-fno-rtti','-fno-builtin']
    compiler=shlex.split(args.compiler)
    run(compiler+flags+[str(folder/'reference.cpp'),'-o',str(folder/'reference')])
    run(compiler+flags+constrained+['-I'+str(ROOT/'include'),str(folder/'facade.cpp'),
        str(HERE/'FullInstrument.cpp'),'-o',str(folder/'facade')])
    run(compiler+flags+constrained+['-I'+str(HERE),str(folder/'faults.cpp'),'-o',str(folder/'faults')])
    cli_stdout,cli_stderr=run([str(folder/'reference'),'--events',str(folder/'events.txt'),
        '--output',str(folder/'reference.wav'),'--sample-rate',str(args.sample_rate),
        '--duration',format((FRAMES-.5)/args.sample_rate,'.17g')])
    run([str(folder/'facade'),str(folder/'facade.f32')]);run([str(folder/'faults')])
    reference=wav_payload(folder/'reference.wav',args.sample_rate)
    facade=(folder/'facade.f32').read_bytes()
    if facade!=reference:
        first=next((i for i,(a,b) in enumerate(zip(reference,facade)) if a!=b),None)
        raise ValueError(f'Audio null failed; first differing byte {first}; lengths {len(reference)}/{len(facade)}')
    report={'passed':True,'frames':FRAMES,'sample_rate':args.sample_rate,
        'bit_identical_float32':True,'audio_sha256':hashlib.sha256(reference).hexdigest(),
        'source_sha256':hashlib.sha256(source).hexdigest(),
        'calibration_sha256':hashlib.sha256(calibration).hexdigest(),
        'reference':'actual hot_precision full CLI event/WAV path, original 24 Hz high-pass',
        'facade':'controller bypass; humanization/mechanical/gain zero; dynamics .5; width 1; body coupling/observation false',
        'irregular_blocks':[1,63,64,65,7,129],'event_frames':[e[0] for e in EVENTS],
        'private_fault_and_reset_checks':True,'flags':flags,'facade_flags':flags+constrained,
        'cli_metrics':json.loads(cli_stdout),'compiler':run(compiler+['--version'])[0].splitlines()[0]}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
