#!/usr/bin/env python3
"""Bounded layout experiments on copies of the complete reference model.

Only unison-port storage/iteration changes. All 230 strings, 17,778 string modes,
475 board modes, nonlinear contact and reciprocal/radiation operators remain.
Candidates must preserve float WAV AND canonical double-state snapshot bytes.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'Research/GrandPianoV2'
_spec=importlib.util.spec_from_file_location('keyra_profile_reference',ROOT/'tools/profile_reference.py')
profile=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(profile)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


GROUP_CLASS=r'''
// Setup-only cache of contiguous unison rows. Every source row remains present;
// detuned upper-partial membership changes start a new run rather than dropping
// a participant. Canonical double states retain their original q/p storage.
struct UnisonGroup {
  int count=0;
  std::array<double*,3> velocity{};
  std::array<std::vector<double>,3> omega,inverse;
  std::vector<double> coefficient;
  template<int N> void scalarStep(){
    double *__restrict p0=velocity[0],*__restrict p1=velocity[1],*__restrict p2=velocity[2];
    const double *__restrict w0=omega[0].data(),*__restrict w1=omega[1].data(),*__restrict w2=omega[2].data();
    const double *__restrict r0=inverse[0].data(),*__restrict r1=inverse[1].data(),*__restrict r2=inverse[2].data();
    const double *__restrict c=coefficient.data();
    for(size_t i=0;i<coefficient.size();++i){
      double sum=w0[i]*p0[i];
      if constexpr(N>1)sum+=w1[i]*p1[i];
      if constexpr(N>2)sum+=w2[i]*p2[i];
      double impulse=c[i]*sum;
      p0[i]-=impulse*r0[i];
      if constexpr(N>1)p1[i]-=impulse*r1[i];
      if constexpr(N>2)p2[i]-=impulse*r2[i];
    }
  }
  template<int N> void vectorStep(){
    // Explicit independent rows, not a reassociated floating reduction. The
    // extension survives no-auto-vectorization host/SDK-style compilation.
    typedef double Pair __attribute__((vector_size(16),aligned(8),may_alias));
    double *__restrict p0=velocity[0],*__restrict p1=velocity[1],*__restrict p2=velocity[2];
    const double *__restrict w0=omega[0].data(),*__restrict w1=omega[1].data(),*__restrict w2=omega[2].data();
    const double *__restrict r0=inverse[0].data(),*__restrict r1=inverse[1].data(),*__restrict r2=inverse[2].data();
    const double *__restrict c=coefficient.data();
    size_t i=0;
    for(;i+1<coefficient.size();i+=2){
      Pair sum=*reinterpret_cast<const Pair*>(w0+i)* *reinterpret_cast<const Pair*>(p0+i);
      if constexpr(N>1)sum+=*reinterpret_cast<const Pair*>(w1+i)* *reinterpret_cast<const Pair*>(p1+i);
      if constexpr(N>2)sum+=*reinterpret_cast<const Pair*>(w2+i)* *reinterpret_cast<const Pair*>(p2+i);
      const Pair impulse=*reinterpret_cast<const Pair*>(c+i)*sum;
      *reinterpret_cast<Pair*>(p0+i)-=impulse* *reinterpret_cast<const Pair*>(r0+i);
      if constexpr(N>1)*reinterpret_cast<Pair*>(p1+i)-=impulse* *reinterpret_cast<const Pair*>(r1+i);
      if constexpr(N>2)*reinterpret_cast<Pair*>(p2+i)-=impulse* *reinterpret_cast<const Pair*>(r2+i);
    }
    for(;i<coefficient.size();++i){
      double sum=w0[i]*p0[i];
      if constexpr(N>1)sum+=w1[i]*p1[i];
      if constexpr(N>2)sum+=w2[i]*p2[i];
      double impulse=c[i]*sum;
      p0[i]-=impulse*r0[i];
      if constexpr(N>1)p1[i]-=impulse*r1[i];
      if constexpr(N>2)p2[i]-=impulse*r2[i];
    }
  }
};
'''


def grouped_unisons(source,explicit_vector=False):
    source=profile.replace_once(source,'class Piano {',GROUP_CLASS+'\nclass Piano {')
    source=profile.replace_once(source,'  std::vector<UnisonPort> unisonPorts;',
                              '  std::vector<UnisonPort> unisonPorts;\n  std::vector<UnisonGroup> unisonGroups;')
    source=profile.replace_once(source,'    setDamping();\n    if(opt.calibrated)buildRadiation();',
                              '    setDamping();\n    if(opt.calibrated)buildRadiation();\n    buildUnisonGroups();')
    start=source.index('  void unisonStep(){')
    end=source.index('\n  void noteOn(',start)
    method='vectorStep' if explicit_vector else 'scalarStep'
    replacement=r'''  void buildUnisonGroups(){
    unisonGroups.clear();
    for(const auto& port:unisonPorts){
      bool contiguous=!unisonGroups.empty()&&unisonGroups.back().count==port.count;
      if(contiguous){const auto& group=unisonGroups.back();
        for(int lane=0;lane<port.count;++lane)
          contiguous=contiguous&&port.velocityState[lane]==group.velocity[lane]+group.coefficient.size();
      }
      if(!contiguous){unisonGroups.emplace_back();auto& group=unisonGroups.back();group.count=port.count;group.velocity=port.velocityState;}
      auto& group=unisonGroups.back();group.coefficient.push_back(port.coefficient);
      for(int lane=0;lane<port.count;++lane){group.omega[lane].push_back(port.omega[lane]);group.inverse[lane].push_back(port.inverseOmega[lane]);}
    }
  }
  void unisonStep(){
    for(auto& group:unisonGroups){
      if(group.count==1)group.METHOD<1>();
      else if(group.count==2)group.METHOD<2>();
      else group.METHOD<3>();
    }
  }
'''.replace('METHOD',method)
    return source[:start]+replacement+source[end:]


def stage_profiled(source):
    old='    oscillators();unisonStep();bridgeStep(dt,cachedRadiation);'
    temporary=profile.replace_once(source,old,'    oscillators();unisonStep();bridgeStep(dt);')
    instrumented=profile.profiled(temporary)
    return profile.replace_once(instrumented,'    bridgeStep(dt);auto profile4=',
                                '    bridgeStep(dt,cachedRadiation);auto profile4=')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-source',type=Path,default=ROOT/'out/reference-optimization/impulse-radiation.cpp')
    p.add_argument('--output-dir',type=Path,default=ROOT/'out/full-layout-optimization')
    p.add_argument('--duration',type=float,default=.35)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--compiler',default='g++')
    p.add_argument('--scalar',action='store_true')
    p.add_argument('--avx2',action='store_true',help='Native x86 AVX2 ceiling probe only; not a Reason/SDK result')
    p.add_argument('--extra-parity',action='store_true')
    a=p.parse_args()
    if not .1<=a.duration<=2 or not 1<=a.repeats<=5:p.error('Use bounded duration.1..2 and repeats1..5')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    original=(REFERENCE/'src/grand.cpp').read_text();base=a.base_source.read_text()
    sources={'original':original,'impulse_radiation':base,
             'grouped_unison':grouped_unisons(base),
             'explicit_vector_unison':grouped_unisons(base,True)}
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    if a.scalar:flags+=['-fno-builtin','-fno-tree-vectorize']
    if a.avx2:flags+=['-mavx2']
    events=a.output_dir/'events.txt'
    events.write_text('0 pedal 0 1\n0.01 on 36 40\n0.025 on 60 93\n0.04 on 84 127\n0.075 off 60 0\n0.09 on 60 61\n0.12 pedal 0 .55\n0.15 off 36 0\n0.18 off 84 0\n0.21 pedal 0 0\n0.24 on 48 80\n0.28 off 60 0\n0.3 off 48 0\n')
    result={'schema_version':1,'source_sha256':sha(REFERENCE/'src/grand.cpp'),'base_source_sha256':sha(a.base_source),
            'tool_sha256':sha(Path(__file__)),'compiler':subprocess.check_output([a.compiler,'--version'],text=True).splitlines()[0],
            'platform':platform.platform(),'flags':flags,'audio_seconds':a.duration,'sample_rate':48000,
            'variants':{},'limits':'Exact topology and per-row arithmetic; local shared-host process CPU evidence only, no Jukebox/Reason certification. No modal truncation, altered coefficients, skipped operators or quality reductions.'}
    for label,source in sources.items():
        source_path=a.output_dir/(label+'.cpp');source_path.write_text(source)
        compiled=a.output_dir/(label+'.compiled.cpp');compiled.write_text(profile.cpu_clock(source))
        binary=a.output_dir/label;vector_log=a.output_dir/(label+'-vectorization.txt')
        subprocess.run([a.compiler,*flags,'-fopt-info-vec-all='+str(vector_log),'-I'+str(REFERENCE/'src'),str(compiled),'-o',str(binary)],check=True)
        self_test=json.loads(subprocess.check_output([str(binary),'--self-test'],text=True))
        if not self_test['passed']:raise AssertionError((label,self_test))
        result['variants'][label]={'source_sha256':sha(source_path),'compiled_sha256':sha(compiled),'binary_sha256':sha(binary),'physical_self_test':self_test,'runs':[]}
        (a.output_dir/(label+'.patch')).write_text(''.join(difflib.unified_diff(base.splitlines(True),source.splitlines(True),fromfile='passing-impulse-radiation.cpp',tofile=label+'.cpp')))
    # Profile before timing candidate runs; do not mix its clock instrumentation
    # into performance medians or permit its output to silently change.
    instrumented=a.output_dir/'profile.compiled.cpp';instrumented.write_text(profile.cpu_clock(stage_profiled(base)))
    subprocess.run([a.compiler,*flags,'-I'+str(REFERENCE/'src'),str(instrumented),'-o',str(a.output_dir/'profile')],check=True)
    call=subprocess.run([str(a.output_dir/'profile'),'--events',str(events),'--output',str(a.output_dir/'profile.wav'),'--sample-rate','48000','--duration',str(a.duration)],check=True,text=True,capture_output=True)
    result['passing_base_stage_profile']=json.loads(next(x[8:] for x in call.stderr.splitlines() if x.startswith('PROFILE ')))
    baseline=None
    for repeat in range(a.repeats):
        for label in sources:
            output=a.output_dir/f'{label}-{repeat}.wav'
            call=subprocess.run([str(a.output_dir/label),'--events',str(events),'--output',str(output),'--sample-rate','48000','--duration',str(a.duration)],check=True,text=True,capture_output=True)
            metrics=json.loads(call.stdout);hashes={'audio':sha(output),'state':sha(str(output)+'.state')}
            if baseline is None:baseline=hashes
            if hashes!=baseline:raise AssertionError((label,'exact audio/state parity failed',hashes,baseline))
            metrics['hashes']=hashes;result['variants'][label]['runs'].append(metrics)
    for label,row in result['variants'].items():
        row['median_process_cpu_seconds']=statistics.median(x['process_cpu_seconds'] for x in row['runs'])
        row['speedup_vs_original']=result['variants']['original']['median_process_cpu_seconds']/row['median_process_cpu_seconds']
        row['speedup_vs_passing_base']=statistics.median(x['process_cpu_seconds'] for x in result['variants']['impulse_radiation']['runs'])/row['median_process_cpu_seconds']
    result['all_audio_and_double_state_bytes_identical']=True
    if a.extra_parity:
        result['extra_cases']={}
        cases={'96k_stems':(96000,['--stem-prefix']),'no_sympathetic':(48000,['--no-sympathetic']),
               'bridge_zero':(48000,['--bridge','0']),'uncalibrated':(48000,['--uncalibrated'])}
        for case,(rate,arguments) in cases.items():
            expected=None;result['extra_cases'][case]={}
            for label in sources:
                output=a.output_dir/f'{case}-{label}.wav';args=list(arguments)
                if '--stem-prefix' in args:args.append(str(output.with_suffix('')))
                call=subprocess.run([str(a.output_dir/label),'--events',str(events),'--output',str(output),'--sample-rate',str(rate),'--duration',str(a.duration),*args],check=True,text=True,capture_output=True)
                hashes={'audio':sha(output),'state':sha(str(output)+'.state')}
                if case=='96k_stems':
                    for stem in ('primary','secondary','transient'):hashes[stem]=sha(output.with_suffix('').with_name(output.stem+'-'+stem+'.wav'))
                if expected is None:expected=hashes
                if hashes!=expected:raise AssertionError((case,label,'exact extra-case parity failed'))
                result['extra_cases'][case][label]={'hashes':hashes,'metrics':json.loads(call.stdout)}
    report=a.output_dir/'report.json';report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'all_audio_and_double_state_bytes_identical':True,'profile':result['passing_base_stage_profile'],
                      'variants':{k:{field:r[field] for field in ('median_process_cpu_seconds','speedup_vs_original','speedup_vs_passing_base')} for k,r in result['variants'].items()}},indent=2))


if __name__=='__main__':main()
