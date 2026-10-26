#!/usr/bin/env python3
"""Measure the actual full-piano block API; profile only snapshotted copies.

No model, calibration, mode-count, floating-point environment or runtime
parameter change is made. Recordings and training features are not read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    'src/full_instrument/FullInstrument.cpp',
    'src/full_instrument/PreparedModel.h',
    'src/full_instrument/PreparedCalibration.h',
    'include/keyra/FullInstrument.h',
    'include/keyra/physics/MechanismExciter.h',
    'include/keyra/physics/StrikeController.h',
]

PROFILE_HEADER = r'''
#pragma once
#include <array>
#include <cstdint>
#include <ctime>
namespace keyra_budget {
enum Stage {controls,oscillators,contact,unison,bridgeRadiation,observation,controller,mechanisms,count};
inline std::array<uint64_t,count> elapsed{};
inline std::array<uint64_t,count> calls{};
inline uint64_t now() noexcept {
  timespec value{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&value);
  return uint64_t(value.tv_sec)*1000000000u+uint64_t(value.tv_nsec);
}
struct Timer {
  Stage stage;uint64_t begin;
  explicit Timer(Stage value) noexcept:stage(value),begin(now()){}
  ~Timer() noexcept {elapsed[stage]+=now()-begin;++calls[stage];}
};
}
'''

HARNESS = r'''
#include "keyra/FullInstrument.h"
#ifdef KEYRA_BUDGET_PROFILE
#include "BudgetProfile.h"
#endif
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <string>
#include <vector>

uint64_t threadNow(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000u+t.tv_nsec;}
using Clock=std::chrono::steady_clock;
double seconds(Clock::time_point a,Clock::time_point b){return std::chrono::duration<double>(b-a).count();}
struct Event {unsigned frame;char kind;int note;double value;};
bool event(keyra::FullInstrument& piano,const Event& e){
  if(e.kind=='p')return piano.sustain(e.value);
  if(e.kind=='+')return piano.noteOn(e.note,e.value);
  return piano.noteOff(e.note);
}
double percentile(std::vector<double> a,double p){std::sort(a.begin(),a.end());return a[static_cast<size_t>(std::ceil(p*(a.size()-1)))];}
int main(int argc,char** argv){
  if(argc!=2)return 2;
  const std::string directory=argv[1];
  // Every event is intentionally at an actual 64-frame callback boundary.
  std::vector<Event> music{{0,'p',0,1},{0,'+',36,.5},{0,'+',60,.73},{0,'+',67,.64},
    {1024,'-',60,0},{2048,'+',64,.69},{8192,'-',36,0},{10240,'+',72,.63},
    {16384,'p',0,.4},{24576,'p',0,0},{25600,'-',64,0},{25600,'-',67,0},{25600,'-',72,0}};
  std::vector<Event> repeats{{0,'p',0,1},{0,'+',60,.7},{256,'+',60,.7},{512,'+',60,.7},
    {768,'+',60,.7},{1024,'+',60,.7},{2048,'-',60,0},{3072,'+',60,.7},
    {4096,'-',60,0},{5120,'+',60,.7},{6144,'-',60,0},{8192,'+',60,.7},
    {10240,'-',60,0},{12288,'p',0,.5},{14336,'+',60,.7},{16384,'-',60,0},
    {18432,'+',60,.7},{20480,'-',60,0},{24576,'p',0,0}};
  std::vector<Event> dense{{0,'p',0,1}};
  for(int note=21;note<=108;++note)dense.push_back({0,'+',note,.7});
  for(int note=21;note<=108;++note)dense.push_back({512,'-',note,0});
  dense.push_back({8192,'p',0,0});
  const std::array<std::vector<Event>,3> scores{{music,repeats,dense}};
  const std::array<const char*,3> names{{"music","repeats-pedal","dense-88-tail"}};
  const std::array<unsigned,3> lengths{{30720,30720,15360}};
  std::printf("{\"cases\":[");
  for(unsigned c=0;c<scores.size();++c){
    keyra::FullInstrument piano;keyra::FullInstrumentConfig config;config.sampleRate=48000;config.seed=0x4b657972u;
    const auto prepareStart=Clock::now();
    if(!piano.prepare(config))return 3;
    const double prepareWall=seconds(prepareStart,Clock::now());
    const unsigned frames=lengths[c];std::vector<float> left(frames),right(frames);
    std::vector<double> walls,cpus;walls.reserve(frames/64);cpus.reserve(frames/64);
    std::vector<unsigned> eventsPerBlock;eventsPerBlock.reserve(frames/64);
    size_t next=0;uint64_t misses=0;
#ifdef KEYRA_BUDGET_PROFILE
    keyra_budget::elapsed={};keyra_budget::calls={};
#endif
    const auto wallStart=Clock::now();const auto cpuStart=std::clock();
    for(unsigned start=0;start<frames;start+=64){
      const auto wall0=Clock::now();const auto cpu0=threadNow();unsigned n=0;
      while(next<scores[c].size()&&scores[c][next].frame==start){if(!event(piano,scores[c][next++]))return 4;++n;}
      if(!piano.process(left.data()+start,right.data()+start,64))return 5;
      const double cpu=double(threadNow()-cpu0)*1.e-9,wall=seconds(wall0,Clock::now());
      walls.push_back(wall);cpus.push_back(cpu);eventsPerBlock.push_back(n);
      if(wall>64./48000.)++misses;
    }
    const double processCpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC,totalWall=seconds(wallStart,Clock::now());
    const auto diagnostics=piano.diagnostics();
    if(next!=scores[c].size()||diagnostics.faultFlags||diagnostics.unsafeLaunches||
       diagnostics.stringCount!=230||diagnostics.stringModes!=17778||diagnostics.boardModes!=475)return 6;
    const auto audioPath=directory+"/"+names[c]+".f32le-planar";
    FILE* audio=std::fopen(audioPath.c_str(),"wb");if(!audio)return 7;
    if(std::fwrite(left.data(),sizeof(float),frames,audio)!=frames||std::fwrite(right.data(),sizeof(float),frames,audio)!=frames)return 8;
    std::fclose(audio);
    if(c)std::printf(",");
    std::printf("{\"name\":\"%s\",\"sample_rate\":48000,\"block_frames\":64,\"frames\":%u,\"audio_seconds\":%.17g,\"prepare_wall_seconds_excluded\":%.17g,\"process_cpu_seconds\":%.17g,\"total_wall_seconds\":%.17g,\"wall_deadline_misses\":%llu,\"string_count\":%u,\"string_modes\":%u,\"board_modes\":%u,\"requests\":%llu,\"launches\":%llu,\"deferred\":%llu,\"coalesced\":%llu,\"cancelled\":%llu,\"expired\":%llu,\"fault_flags\":%u,\"events\":[",
      names[c],frames,frames/48000.,prepareWall,processCpu,totalWall,(unsigned long long)misses,
      diagnostics.stringCount,diagnostics.stringModes,diagnostics.boardModes,
      (unsigned long long)diagnostics.requests,(unsigned long long)diagnostics.launches,
      (unsigned long long)diagnostics.deferred,(unsigned long long)diagnostics.coalesced,
      (unsigned long long)diagnostics.cancelled,(unsigned long long)diagnostics.expired,diagnostics.faultFlags);
    bool first=true;for(const auto& e:scores[c]){if(!first)std::printf(",");first=false;std::printf("{\"frame\":%u,\"kind\":\"%c\",\"note\":%d,\"value\":%.17g}",e.frame,e.kind,e.note,e.value);}
    std::printf("],\"callback_wall_seconds\":[");first=true;for(double t:walls){if(!first)std::printf(",");first=false;std::printf("%.17g",t);}
    std::printf("],\"callback_thread_cpu_seconds\":[");first=true;for(double t:cpus){if(!first)std::printf(",");first=false;std::printf("%.17g",t);}
    std::printf("],\"events_per_block\":[");first=true;for(unsigned n:eventsPerBlock){if(!first)std::printf(",");first=false;std::printf("%u",n);}
#ifdef KEYRA_BUDGET_PROFILE
    constexpr std::array<const char*,keyra_budget::count> stages{{"controls","oscillators_including_contact","contact_subset","grouped_unison","bridge_fused_radiation","observation","controller","mechanisms"}};
    std::printf("],\"stages\":{");first=true;
    for(unsigned j=0;j<stages.size();++j){if(!first)std::printf(",");first=false;std::printf("\"%s\":{\"thread_cpu_seconds\":%.17g,\"calls\":%llu}",stages[j],keyra_budget::elapsed[j]*1.e-9,(unsigned long long)keyra_budget::calls[j]);}
    std::printf("}}");
#else
    std::printf("]}");
#endif
  }
#ifdef KEYRA_BUDGET_PROFILE
  constexpr unsigned timerTrials=100000;const auto emptyStart=threadNow();
  for(unsigned i=0;i<timerTrials;++i){keyra_budget::Timer scope(keyra_budget::controls);}
  std::printf("],\"empty_timer_cpu_seconds_per_pair\":%.17g}\n",double(threadNow()-emptyStart)*1.e-9/timerTrials);
#else
  std::printf("]}\n");
#endif
}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Expected exactly one instrumentation target: '+old[:70])
    return text.replace(old, new, 1)


def profile_sources(model, api):
    model = replace_once(model, '#include "PreparedCalibration.h"',
                         '#include "PreparedCalibration.h"\n#include "BudgetProfile.h"')
    model = replace_once(model, '  double contact(Key &k,double delta0,double freeDelta){',
                         '  double contact(Key &k,double delta0,double freeDelta){\n    keyra_budget::Timer timer(keyra_budget::contact);')
    model = replace_once(model, '    if(frame%64==0){pedal+=',
                         '    {keyra_budget::Timer timer(keyra_budget::controls);\n    if(frame%64==0){pedal+=')
    model = replace_once(model, '    // The adjacent bridge half steps coalesce',
                         '    }\n    // The adjacent bridge half steps coalesce')
    model = replace_once(model, '    oscillators();groupedUnisonStep();bridgeStep(dt,cachedRadiation);',
                         '    {keyra_budget::Timer timer(keyra_budget::oscillators);oscillators();}\n'
                         '    {keyra_budget::Timer timer(keyra_budget::unison);groupedUnisonStep();}\n'
                         '    {keyra_budget::Timer timer(keyra_budget::bridgeRadiation);bridgeStep(dt,cachedRadiation);}\n'
                         '    keyra_budget::Timer timer(keyra_budget::observation);')
    api = replace_once(api, '  std::array<double,2> step() noexcept {\n',
                       '  std::array<double,2> step() noexcept {\n    {keyra_budget::Timer timer(keyra_budget::controller);\n')
    api = replace_once(api, '    auto out=model->step(frame);',
                       '    }\n    auto out=model->step(frame);\n    keyra_budget::Timer timer(keyra_budget::mechanisms);')
    return model, api


def summarize(case):
    import numpy as np
    deadline = case['block_frames']/case['sample_rate']
    for kind in ('wall', 'thread_cpu'):
        values = np.asarray(case['callback_'+kind+'_seconds'])
        case['callback_'+kind+'_summary'] = {
            'p50_ms': float(np.percentile(values, 50)*1000),
            'p95_ms': float(np.percentile(values, 95)*1000),
            'max_ms': float(values.max()*1000),
            'p95_deadline_multiple': float(np.percentile(values,95)/deadline),
            'max_deadline_multiple': float(values.max()/deadline),
            'misses': int(np.count_nonzero(values>deadline)),
            'callbacks': len(values),
        }
    case['cpu_seconds_per_audio_second'] = case['process_cpu_seconds']/case['audio_seconds']
    if 'stages' in case:
        exclusive = sum(v['thread_cpu_seconds'] for k,v in case['stages'].items()
                        if k!='contact_subset')
        for name,item in case['stages'].items():
            item['fraction_of_profiled_exclusive_stages'] = item['thread_cpu_seconds']/exclusive
        case['stage_exclusive_cpu_seconds'] = exclusive
        case['untimed_process_residual_seconds'] = case['process_cpu_seconds']-exclusive


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-backend-budget')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-backend-budget.json')
    args=parser.parse_args();out=args.output.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('Use a new empty output directory; completed evidence is not overwritten.')
    out.mkdir(parents=True,exist_ok=True)
    original={name:sha(ROOT/name) for name in INPUTS}
    verify=lambda: all(sha(ROOT/name)==value for name,value in original.items())
    api=(ROOT/INPUTS[0]).read_text();model=(ROOT/INPUTS[1]).read_text()
    compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
    common=['-O3','-DNDEBUG','-std=c++17','-Wall','-Wextra','-Wpedantic',
            '-ffp-contract=off','-fno-exceptions','-fno-rtti','-fno-builtin']
    result={'schema_version':1,'purpose':__doc__,'platform':platform.platform(),
            'compiler':compiler,'input_sha256':original,'tool_sha256':sha(__file__),
            'sample_rate':48000,'block_frames':64,'callback_deadline_ms':64/48,
            'parameters':'FullInstrumentConfig defaults, seed0x4b657972, original control calibration; no limiter, resampling or room.',
            'timing_scope':'One serialized instance on one thread. Callback timing includes event dispatch and process, excludes prepare, final audio write and report generation. ProcessCPU also includes timing/output-vector bookkeeping.',
            'limits':'Bounded shared-Linux-host evidence; no SDK, Reason, multicore/multivoice scaling, supported-host qualification or realtime claim. Stage profile uses CLOCK_THREAD_CPUTIME_ID on copied sources and has measured clock overhead. The contact stage is a subset of oscillator time, not an additional exclusive stage.',
            'variants':{}}
    for label in ('native','scalar','profile'):
        if not verify():raise RuntimeError('Input changed before compilation')
        folder=out/label;folder.mkdir()
        include=folder/'include'
        for name in INPUTS[3:]:
            target=include/Path(name).relative_to('include');target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)
        source=api;prepared=model
        flags=common.copy()
        if label=='scalar':flags+=['-fno-tree-vectorize']
        if label=='profile':
            prepared,source=profile_sources(prepared,source)
            (folder/'BudgetProfile.h').write_text(PROFILE_HEADER)
            flags+=['-DKEYRA_BUDGET_PROFILE']
        (folder/'FullInstrument.cpp').write_text(source)
        (folder/'PreparedModel.h').write_text(prepared)
        shutil.copyfile(ROOT/INPUTS[2],folder/'PreparedCalibration.h')
        (folder/'harness.cpp').write_text(HARNESS)
        command=['g++',*flags,'-I'+str(include),'-I'+str(folder),str(folder/'FullInstrument.cpp'),str(folder/'harness.cpp'),'-o',str(folder/'probe')]
        subprocess.run(command,check=True)
        print(label+': compiled',flush=True)
        call=subprocess.run([str(folder/'probe'),str(folder)],capture_output=True,text=True)
        (folder/'stdout.json').write_text(call.stdout)
        (folder/'stderr.txt').write_text(call.stderr)
        if call.returncode:raise RuntimeError(f'{label} probe failed: exit{call.returncode}: {call.stderr}')
        data=json.loads(call.stdout)
        for case in data['cases']:
            summarize(case)
            audio=folder/(case['name']+'.f32le-planar')
            case['audio']={'path':str(audio),'sha256':sha(audio),'format':'float32 native little-endian planar L then R'}
            if label=='profile':
                baseline=out/'native'/(case['name']+'.f32le-planar')
                case['audio']['byte_identical_to_native']=sha(audio)==sha(baseline)
                if not case['audio']['byte_identical_to_native']:
                    raise RuntimeError('Stage instrumentation changed actual audio: '+case['name'])
            print(label+': '+case['name']+' CPU/audio='+format(case['cpu_seconds_per_audio_second'],'.3f'),flush=True)
        data['flags']=flags;data['binary_sha256']=sha(folder/'probe')
        data['compiled_source_sha256']={name:sha(folder/name) for name in ('FullInstrument.cpp','PreparedModel.h','PreparedCalibration.h','harness.cpp')}
        result['variants'][label]=data
        if not verify():raise RuntimeError('Input changed during benchmark')
    for c in result['variants']['profile']['cases']:
        native=next(r for r in result['variants']['native']['cases'] if r['name']==c['name'])
        c['instrumentation_process_cpu_ratio']=c['process_cpu_seconds']/native['process_cpu_seconds']
    result['all_profile_audio_byte_identical_to_native']=True
    result['inputs_unchanged_after_measurements']=verify()
    cpu=Path('/proc/cpuinfo')
    if cpu.exists():result['cpu_model']=next((s.split(':',1)[1].strip() for s in cpu.read_text().splitlines() if s.startswith('model name')),'unknown')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (out/'report.json').write_text(args.report.read_text())
    print(args.report,flush=True)


if __name__=='__main__':main()
