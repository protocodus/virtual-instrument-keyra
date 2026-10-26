#!/usr/bin/env python3
"""Profile the full preserved mechanical piano and grade exact optimization copies.

The frozen research source is never modified. Every compiler input is snapshotted
under out/, all mode counts remain unchanged, and each candidate must emit the
same float WAV bytes as the baseline. Timings describe this host, not Reason.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'Research/GrandPianoV2'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source,old,new):
    if source.count(old)!=1: raise ValueError('Frozen-source transform does not match exactly once: '+old[:60])
    return source.replace(old,new,1)


def fused_free(source):
    source=replace_once(source,'  void finishDamping(){', '''  // Exact-order free/damping fusion only while this key has no active hammer.
  void freeDampedStep(){
    double *__restrict yq=q.data(),*__restrict yp=p.data();
    const double *__restrict yc=c.data(),*__restrict ys=s.data(),*__restrict yd=damp.data();
    for(size_t i=0;i<size();++i){
      double v=yp[i]*yd[i],y=yq[i];
      yq[i]=yc[i]*y+ys[i]*v;
      double rotated=yc[i]*v-ys[i]*y;yp[i]=rotated*yd[i];
    }
  }
  void finishDamping(){''')
    return replace_once(source,'    for(auto &k:keys){\n      double y0=0;',
        '    for(auto &k:keys){\n      if(!k.hammerActive){for(int i:k.strings)strings[i].m.freeDampedStep();continue;}\n      double y0=0;')


def cpu_clock(source):
    source=replace_once(source,'#include <chrono>','#include <chrono>\n#include <ctime>')
    source=replace_once(source,'auto start=std::chrono::steady_clock::now();size_t next=0;',
                        'auto cpuStart=std::clock();auto start=std::chrono::steady_clock::now();size_t next=0;')
    source=replace_once(source,'double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();',
        '''double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();double processCpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  // Snapshot canonical runtime state after timing; exclude optimization caches.
  // Matching float output alone would hide differences below float32 precision.
  std::ofstream stateFile(output+".state",std::ios::binary);
  auto stateScalar=[&](const auto &value){stateFile.write(reinterpret_cast<const char*>(&value),sizeof(value));};
  auto stateVector=[&](const std::vector<double> &values){stateFile.write(reinterpret_cast<const char*>(values.data()),values.size()*sizeof(double));};
  stateScalar(p.dt);stateScalar(p.pedal);stateScalar(p.pedalTarget);
  stateScalar(p.maxForce);stateScalar(p.contactTime);stateScalar(p.maxContactResidual);stateScalar(p.forceSolves);
  for(const auto &st:p.strings){stateVector(st.m.q);stateVector(st.m.p);stateVector(st.m.damp);stateScalar(st.velocity);stateScalar(st.force);}
  for(const auto &k:p.keys){stateScalar(k.hammerX);stateScalar(k.hammerV);stateScalar(k.age);stateScalar(k.maxForce);stateScalar(k.contactSeconds);stateScalar(k.damperPosition);stateScalar(k.cachedContact);stateScalar(k.cachedLoss);stateScalar(k.down);stateScalar(k.hammerActive);stateScalar(k.everStruck);}
  for(const auto &z:p.board){stateScalar(z.q);stateScalar(z.p);stateScalar(z.force);}
  for(int ch=0;ch<2;++ch){stateScalar(previous[ch]);stateScalar(hp[ch]);}
  for(const auto &stem:p.lastStems)for(double value:stem)stateScalar(value);
  if(!stateFile)throw std::runtime_error("state snapshot write failed");''')
    return replace_once(source,'<<p.energy()<<"}";',
                         '<<p.energy()<<",\\\"process_cpu_seconds\\\":"<<processCpu<<"}";')


def profiled(source):
    source=replace_once(source,'namespace grand {','''namespace grand {
struct StageProfile {double controls=0,oscillators=0,unisons=0,bridge=0,radiation=0;uint64_t frames=0;};
StageProfile stageProfile;
using ProfileClock=std::chrono::steady_clock;
double profileSeconds(ProfileClock::time_point a,ProfileClock::time_point b){return std::chrono::duration<double>(b-a).count();}
''')
    source=replace_once(source,'    if(frame%64==0){pedal+=(1-std::exp(-64*dt/.012))*(pedalTarget-pedal);setDamping();}',
        '''    auto profile0=ProfileClock::now();
    if(frame%64==0){pedal+=(1-std::exp(-64*dt/.012))*(pedalTarget-pedal);setDamping();}
    auto profile1=ProfileClock::now();stageProfile.controls+=profileSeconds(profile0,profile1);''')
    source=replace_once(source,'    oscillators();unisonStep();bridgeStep(dt);',
        '''    oscillators();auto profile2=ProfileClock::now();stageProfile.oscillators+=profileSeconds(profile1,profile2);
    unisonStep();auto profile3=ProfileClock::now();stageProfile.unisons+=profileSeconds(profile2,profile3);
    bridgeStep(dt);auto profile4=ProfileClock::now();stageProfile.bridge+=profileSeconds(profile3,profile4);''')
    source=replace_once(source,'    return out;\n  }\n  double energy()const{',
        '''    auto profile5=ProfileClock::now();stageProfile.radiation+=profileSeconds(profile4,profile5);++stageProfile.frames;
    return out;
  }
  double energy()const{''')
    return replace_once(source,"if(!metrics.empty()){std::ofstream f(metrics);f<<report.str()<<'\\n';}",
        '''std::cerr<<"PROFILE "<<std::setprecision(12)<<"{\\\"frames\\\":"<<stageProfile.frames<<",\\\"controls\\\":"<<stageProfile.controls<<",\\\"oscillators\\\":"<<stageProfile.oscillators<<",\\\"unisons\\\":"<<stageProfile.unisons<<",\\\"bridge\\\":"<<stageProfile.bridge<<",\\\"radiation\\\":"<<stageProfile.radiation<<"}\\n";
  if(!metrics.empty()){std::ofstream f(metrics);f<<report.str()<<'\\n';}''')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--duration',type=float,default=.35)
    p.add_argument('--sample-rate',type=int,default=48000)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--compiler',default='g++')
    p.add_argument('--scalar',action='store_true',help='Host scalar/no-builtin approximation; not the Jukebox compiler')
    p.add_argument('--extra-parity-cases',action='store_true',help='Also compare 96kHz stems, disabled sympathetic coupling, bridge zero, and uncalibrated output')
    p.add_argument('--candidate-source',action='append',default=[],metavar='LABEL=PATH')
    p.add_argument('--output-dir',type=Path,default=ROOT/'out/reference-optimization/profile-run')
    p.add_argument('--report',type=Path,default=ROOT/'Validation/reference-optimization.json')
    a=p.parse_args()
    if not .1<=a.duration<=10 or not 48000<=a.sample_rate<=384000 or not 1<=a.repeats<=10:p.error('Invalid bounded profiling configuration')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    original=(REFERENCE/'src/grand.cpp').read_text()
    inputs={'baseline':original,'free_damping_fusion':fused_free(original),'profile':profiled(original)}
    for value in a.candidate_source:
        label,separator,path=value.partition('=')
        if not separator or not re.fullmatch(r'[a-zA-Z0-9_-]+',label) or label in inputs:p.error('Candidate must be a unique LABEL=PATH')
        inputs[label]=Path(path).read_text()
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    if a.scalar:flags+=['-fno-builtin','-fno-tree-vectorize']
    event_path=a.output_dir/'events.txt'
    event_path.write_text('0 pedal 0 1\n0.01 on 36 40\n0.025 on 60 93\n0.04 on 84 127\n0.075 off 60 0\n0.09 on 60 61\n0.12 pedal 0 .55\n0.15 off 36 0\n0.18 off 84 0\n0.21 pedal 0 0\n0.24 on 48 80\n0.28 off 60 0\n0.3 off 48 0\n')
    result={'schema_version':1,'platform':platform.platform(),
            'compiler':subprocess.check_output([a.compiler,'--version'],text=True).splitlines()[0],
            'flags':flags,'reference_source_sha256':sha(REFERENCE/'src/grand.cpp'),
            'calibration_sha256':sha(REFERENCE/'src/calibration.h'),'tool_sha256':sha(Path(__file__)),
            'sample_rate':a.sample_rate,'audio_seconds':a.duration,'events_sha256':sha(event_path),
            'repeats':a.repeats,'variants':{},
            'limits':'Full preserved topology. Identical compiler flags and float-WAV byte comparison. Process CPU timing reduces scheduling noise but remains shared-host evidence, not real-time/SDK/DAW certification. No physics or modal truncation is authorized by this probe.'}
    cpu_model=Path('/proc/cpuinfo')
    if cpu_model.exists():result['cpu']=next((line.split(':',1)[1].strip() for line in cpu_model.read_text().splitlines() if line.startswith('model name')),'unknown')
    for label,source in inputs.items():
        snapshot=a.output_dir/(label+'.input.cpp');snapshot.write_text(source)
        compiled=a.output_dir/(label+'.compiled.cpp');compiled.write_text(cpu_clock(source))
        binary=a.output_dir/label
        subprocess.run([a.compiler,*flags,'-I'+str(REFERENCE/'src'),str(compiled),'-o',str(binary)],check=True)
        result['variants'][label]={'source_sha256':sha(snapshot),'compiled_source_sha256':sha(compiled),'binary_sha256':sha(binary),
            'source_diff':''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='frozen/grand.cpp',tofile=label+'/grand.cpp')),'runs':[]}
        if label!='profile':
            self_test=json.loads(subprocess.check_output([str(binary),'--self-test'],text=True));
            if not self_test['passed']:raise AssertionError(self_test)
            result['variants'][label]['physical_self_test']=self_test
    baseline_hash=None;baseline_state_hash=None
    # Interleave variants so one scheduling/thermal episode cannot coincide
    # with every run of a single implementation.
    for repeat in range(a.repeats):
        for label in inputs:
            if label=='profile' and repeat:continue
            output=a.output_dir/f'{label}-{repeat}.wav'
            command=[str(a.output_dir/label),'--events',str(event_path),'--output',str(output),
                     '--sample-rate',str(a.sample_rate),'--duration',str(a.duration)]
            call=subprocess.run(command,check=True,text=True,capture_output=True)
            metrics=json.loads(call.stdout)
            metrics['wav_sha256']=sha(output)
            metrics['final_state_sha256']=sha(Path(str(output)+'.state'))
            if baseline_hash is None:baseline_hash=metrics['wav_sha256']
            if baseline_state_hash is None:baseline_state_hash=metrics['final_state_sha256']
            metrics['byte_identical_to_baseline']=metrics['wav_sha256']==baseline_hash
            metrics['double_state_byte_identical_to_baseline']=metrics['final_state_sha256']==baseline_state_hash
            if not metrics['byte_identical_to_baseline']:raise AssertionError(label+' changed float WAV bytes')
            if not metrics['double_state_byte_identical_to_baseline']:raise AssertionError(label+' changed canonical runtime state bytes')
            if label=='profile':
                line=next(line for line in call.stderr.splitlines() if line.startswith('PROFILE '))
                stages=json.loads(line[len('PROFILE '):]);total=sum(value for key,value in stages.items() if key!='frames')
                result['baseline_stage_profile']={'seconds':stages,'fractions':{key:value/total for key,value in stages.items() if key!='frames'}}
            result['variants'][label]['runs'].append(metrics)
    for value in result['variants'].values():
        value['median_process_cpu_seconds']=statistics.median(run['process_cpu_seconds'] for run in value['runs'])
        value['median_wall_seconds']=statistics.median(run['wall_seconds'] for run in value['runs'])
    baseline_cpu=result['variants']['baseline']['median_process_cpu_seconds']
    for value in result['variants'].values():value['process_cpu_reduction_fraction']=1-value['median_process_cpu_seconds']/baseline_cpu
    parity_failures=[]
    if a.extra_parity_cases:
        result['extra_parity_cases']={}
        cases={'96k_stems':(96000,['--stem-prefix']),
               'no_sympathetic':(a.sample_rate,['--no-sympathetic']),
               'bridge_zero':(a.sample_rate,['--bridge','0']),
               'uncalibrated':(a.sample_rate,['--uncalibrated'])}
        for case,(rate,arguments) in cases.items():
            baseline_files=None;rows={}
            for label in inputs:
                if label=='profile':continue
                output=a.output_dir/f'{case}-{label}.wav'
                args=list(arguments)
                if '--stem-prefix' in args:args.append(str(a.output_dir/f'{case}-{label}'))
                call=subprocess.run([str(a.output_dir/label),'--events',str(event_path),'--output',str(output),
                    '--sample-rate',str(rate),'--duration',str(a.duration),*args],check=True,text=True,capture_output=True)
                files={'audio':sha(output),'state':sha(Path(str(output)+'.state'))}
                if case=='96k_stems':
                    for stem in ('primary','secondary','transient'):files[stem]=sha(a.output_dir/f'{case}-{label}-{stem}.wav')
                if baseline_files is None:baseline_files=files
                changed=[key for key in files if files[key]!=baseline_files[key]]
                if changed:parity_failures.append({'case':case,'variant':label,'changed_files':changed})
                rows[label]={'hashes':files,'all_bytes_identical':not changed,'changed_files':changed,'metrics':json.loads(call.stdout)}
            result['extra_parity_cases'][case]={'sample_rate':rate,'variants':rows}
    result['parity_failures']=parity_failures
    result['all_audio_byte_identical']=not any(any(key!='state' for key in row['changed_files']) for row in parity_failures)
    result['all_final_double_states_byte_identical']=not any('state' in row['changed_files'] for row in parity_failures)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'all_audio_byte_identical':result['all_audio_byte_identical'],
        'all_final_double_states_byte_identical':result['all_final_double_states_byte_identical'],
        'parity_failures':parity_failures,
        'variants':{key:{field:row[field] for field in ('median_process_cpu_seconds','median_wall_seconds','process_cpu_reduction_fraction')} for key,row in result['variants'].items()},'stages':result.get('baseline_stage_profile')},indent=2))
    if parity_failures:raise SystemExit(1)


if __name__=='__main__':main()
