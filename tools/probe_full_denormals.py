#!/usr/bin/env python3
"""Diagnose late float denormals in one pinned extended-calibration full solver.

Only synthesized C8 notes are generated. No reference recording/features are
opened. FTZ/DAZ is a standalone diagnostic with CSR restoration, not a proposed
production host environment. Source and calibration are copied under out/.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/full-calibration/v2/mechanics/float-solver/grand.cpp'
SOURCE_SHA='8d6abcd41d89a32b54366106c54ebb62a9b52de21dc21402a7c179c55af88e56'
CAL_SHA='45935c2fbe67e1916ba1bf6eeb22f676f04639e70f5aa1e53e3bd5196c01a529'

HARNESS=r'''#define main keyra_denormal_original_main
#include "@SOURCE@"
#undef main
#include <ctime>
#include <cstring>
#if defined(__SSE__)
#include <xmmintrin.h>
#endif
bool subnormal(float value){uint32_t bits;std::memcpy(&bits,&value,4);return (bits&0x7f800000u)==0&&(bits&0x007fffffu)!=0;}
using Counts=std::array<uint64_t,13>;
const char* labels[]={"q","p","board_qp","port_velocity_float","force_float","impulse_float","port_products","radiation_products","rotation_products","unison_sum","unison_impulse","unison_update","radiation_reduction"};
Counts counts(const grand::Piano& p){
  Counts n{};
  for(const auto& st:p.strings){const auto& m=st.m;
    float velocity=0,l=0,r=0,force=float(st.force),impulse=float(p.dt*st.force);
    n[4]+=subnormal(force);n[5]+=subnormal(impulse);
    for(size_t j=0;j<m.size();++j){
      n[0]+=subnormal(m.q[j]);n[1]+=subnormal(m.p[j]);
      float port=m.portOmega[j]*m.p[j];velocity+=port;
      n[6]+=subnormal(port)+subnormal(m.portInverse[j]*impulse);
      float a=m.radQL[j]*m.q[j],b=m.radPL[j]*m.p[j],c=m.radQR[j]*m.q[j],d=m.radPR[j]*m.p[j];
      n[7]+=subnormal(a)+subnormal(b)+subnormal(c)+subnormal(d);
      l+=a+b;r+=c+d;n[12]+=subnormal(l)+subnormal(r);
      n[8]+=subnormal(m.c[j]*m.q[j])+subnormal(m.s[j]*m.p[j])+subnormal(m.damp[j]*m.p[j]);
    }
    n[3]+=subnormal(velocity);
  }
  for(const auto& b:p.board)n[2]+=subnormal(b.q)+subnormal(b.p);
  for(const auto& g:p.unisonGroups)for(size_t j=0;j<g.coefficient.size();++j){
    float sum=g.omega[0][j]*g.velocity[0][j];
    if(g.count>1)sum+=g.omega[1][j]*g.velocity[1][j];
    if(g.count>2)sum+=g.omega[2][j]*g.velocity[2][j];
    float impulse=g.coefficient[j]*sum;n[9]+=subnormal(sum);n[10]+=subnormal(impulse);
    for(int k=0;k<g.count;++k)n[11]+=subnormal(impulse*g.inverse[k][j]);
  }
  return n;
}
double energy(const grand::Piano& p){
  double e=0;for(const auto& st:p.strings)for(size_t j=0;j<st.m.size();++j){double q=st.m.q[j],v=st.m.p[j],w=st.m.omega[j];e+=.5*w*w*(q*q+v*v);}
  for(const auto& b:p.board){double q=b.q,v=b.p;e+=.5*b.w*b.w*(q*q+v*v);}return e;
}
struct Row{double start,end,cpu,wall,energy;Counts counts;};
int main(int argc,char**argv){try{
  if(argc!=5)throw std::runtime_error("mode prefix duration rate");
  bool ftz=std::string(argv[1])=="ftz";std::string prefix=argv[2];double duration=std::stod(argv[3]);int rate=std::stoi(argv[4]);
  unsigned caller=0,during=0,after=0;bool available=false;
#if defined(__SSE__)
  caller=_mm_getcsr();available=true;
#endif
  grand::Options options;options.sampleRate=rate;grand::Piano p(options);
  double observationL1[2]{};
  for(const auto& st:p.strings)for(size_t j=0;j<st.m.size();++j){observationL1[0]+=std::abs(double(st.m.radQL[j]))+std::abs(double(st.m.radPL[j]));observationL1[1]+=std::abs(double(st.m.radQR[j]))+std::abs(double(st.m.radPR[j]));}
  for(const auto& b:p.board)for(int ch=0;ch<2;++ch)observationL1[ch]+=std::abs(b.w*b.w*b.mic[ch])+std::abs(2*b.sigma*b.w*b.mic[ch]);
  size_t frames=size_t(std::llround(duration*rate)),quarter=size_t(rate/4);std::vector<float> audio(frames*2);std::vector<double> precise(frames*2);std::vector<Row> rows;
  double pole=std::exp(-2*grand::pi*24/rate),previous[2]{},hp[2]{};double cpu435=0,total=0;bool finite=true;
  {
#if defined(__SSE__)
    struct Restore{unsigned value;~Restore(){_mm_setcsr(value);}} restore{caller};
    _mm_setcsr(ftz?(caller|0x8040u):(caller&~0x8040u));during=_mm_getcsr();
#endif
    for(size_t begin=0;begin<frames;begin+=quarter){
      size_t end=std::min(frames,begin+quarter);auto start=std::clock();auto wall0=std::chrono::steady_clock::now();
      for(size_t frame=begin;frame<end;++frame){
        if(frame==size_t(std::llround(.1*rate)))p.noteOn(108,93);
        if(frame==size_t(std::llround(4.15*rate)))p.noteOff(108);
        auto x=p.step(frame);
        for(int ch=0;ch<2;++ch){hp[ch]=pole*(hp[ch]+x[ch]-previous[ch]);previous[ch]=x[ch];finite=finite&&std::isfinite(hp[ch]);precise[frame*2+ch]=hp[ch];audio[frame*2+ch]=float(hp[ch]);}
        if(frame+1==size_t(std::llround(4.35*rate)))cpu435=total+double(std::clock()-start)/CLOCKS_PER_SEC;
      }
      double cpu=double(std::clock()-start)/CLOCKS_PER_SEC;double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-wall0).count();total+=cpu;
      // Diagnostics are explicitly outside the timed solver window.
      rows.push_back({double(begin)/rate,double(end)/rate,cpu,wall,energy(p),counts(p)});
    }
  }
#if defined(__SSE__)
  after=_mm_getcsr();
#endif
  grand::wav(prefix+".wav",audio,rate);std::ofstream raw(prefix+".f64",std::ios::binary);raw.write(reinterpret_cast<const char*>(precise.data()),precise.size()*sizeof(double));raw.close();
  std::cout<<std::boolalpha<<std::setprecision(17)<<"{\"mode\":\""<<argv[1]<<"\",\"sample_rate\":"<<rate<<",\"duration_seconds\":"<<duration<<",\"cpu_to4p35_seconds\":"<<cpu435<<",\"process_cpu_seconds\":"<<total
    <<",\"finite_audio\":"<<finite<<",\"keys\":"<<p.keys.size()<<",\"strings\":"<<p.strings.size()<<",\"string_modes\":"<<p.modeCount()<<",\"board_modes\":"<<p.board.size()
    <<",\"ftz_daz_available\":"<<available<<",\"csr_before\":"<<caller<<",\"csr_during\":"<<during<<",\"csr_after\":"<<after<<",\"caller_csr_restored\":"<<(caller==after)
    <<",\"state_floor1e_33_instantaneous_pressure_bound\":"<<std::max(observationL1[0],observationL1[1])*1e-33<<",\"windows\":[";
  bool first=true;for(const auto& row:rows){if(!first)std::cout<<',';first=false;std::cout<<"{\"start_seconds\":"<<row.start<<",\"end_seconds\":"<<row.end<<",\"cpu_seconds\":"<<row.cpu<<",\"wall_seconds\":"<<row.wall<<",\"mechanical_energy_J\":"<<row.energy<<",\"subnormal_counts\":{";
    for(size_t i=0;i<row.counts.size();++i){if(i)std::cout<<',';std::cout<<'\"'<<labels[i]<<"\":"<<row.counts[i];}std::cout<<"}}";
  }
  std::cout<<"]}\n";return finite?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def run(command,log):
    c=subprocess.run([str(x) for x in command],capture_output=True,text=True)
    log.with_suffix('.stdout.txt').write_text(c.stdout);log.with_suffix('.stderr.txt').write_text(c.stderr)
    if c.returncode:raise RuntimeError(f'Command failed; see {log}.stderr.txt')
    return c.stdout

def replace(source,old,new):
    if source.count(old)!=1:raise ValueError('Pinned transform mismatch: '+old[:80])
    return source.replace(old,new,1)

def portable(source):
    source=replace(source,'#include <chrono>','#include <chrono>\n#include <cstring>')
    source=replace(source,'namespace grand {',r'''namespace grand {
// Explicit portable numerical floor, independent of the caller's FP environment.
inline float tinyState(float value){uint32_t bits;std::memcpy(&bits,&value,4);return (bits&0x7fffffffu)<0x08a6274cu?0.0f:value;}
inline float tinyStateDouble(double value){return std::abs(value)<1e-33?0.0f:static_cast<float>(value);}
inline float tinyImpulse(double value){return std::abs(value)<1e-30?0.0f:static_cast<float>(value);}
''')
    source=source.replace('const float forceValue=static_cast<float>(f);','const float forceValue=tinyImpulse(f);')
    source=source.replace('const float impulseValue=static_cast<float>(impulse);','const float impulseValue=tinyImpulse(impulse);')
    source=source.replace('yq[i]=yc[i]*y+ys[i]*v;', 'yq[i]=tinyState(yc[i]*y+ys[i]*v);')
    source=source.replace('yp[i]=yc[i]*v-ys[i]*y;', 'yp[i]=tinyState(yc[i]*v-ys[i]*y);')
    source=source.replace('yp[i]=rotated*yd[i];','yp[i]=tinyState(rotated*yd[i]);')
    source=source.replace('yp[i]*=yd[i];','yp[i]=tinyState(yp[i]*yd[i]);')
    source=source.replace('yq[i]+=fq[i]*forceValue;yp[i]+=fp[i]*forceValue;',
                           'yq[i]=tinyState(yq[i]+fq[i]*forceValue);yp[i]=tinyState(yp[i]+fp[i]*forceValue);')
    source=source.replace('yp[i]+=bi[i]*impulseValue;', 'yp[i]=tinyState(yp[i]+bi[i]*impulseValue);')
    source=source.replace('float sum=w0[i]*p0[i];','double sum=double(w0[i])*p0[i];')
    source=source.replace('sum+=w1[i]*p1[i];','sum+=double(w1[i])*p1[i];')
    source=source.replace('sum+=w2[i]*p2[i];','sum+=double(w2[i])*p2[i];')
    source=source.replace('float impulse=c[i]*sum;','float impulse=tinyImpulse(double(c[i])*sum);')
    source=source.replace('p0[i]-=impulse*r0[i];','p0[i]=tinyState(p0[i]-impulse*r0[i]);')
    source=source.replace('p1[i]-=impulse*r1[i];','p1[i]=tinyState(p1[i]-impulse*r1[i]);')
    source=source.replace('p2[i]-=impulse*r2[i];','p2[i]=tinyState(p2[i]-impulse*r2[i]);')
    source=source.replace('z.q=z.c*y+z.s*v;z.p=(z.c*v-z.s*y)*z.damp;',
                           'z.q=tinyStateDouble(z.c*y+z.s*v);z.p=tinyStateDouble((z.c*v-z.s*y)*z.damp);')
    source=source.replace('z.p+=step*force/z.w;', 'z.p=tinyStateDouble(double(z.p)+step*force/z.w);')
    return source

def analyze(rows):
    windows=rows['windows']
    early=[w for w in windows if .25<=w['start_seconds']<1.25]
    late=[w for w in windows if 5<=w['start_seconds']]
    return {'cpu_to4p35_seconds':rows['cpu_to4p35_seconds'],'total_cpu_seconds':rows['process_cpu_seconds'],
        'early_cpu_seconds_per_audio_second':sum(w['cpu_seconds'] for w in early)/sum(w['end_seconds']-w['start_seconds'] for w in early),
        'late_cpu_seconds_per_audio_second':sum(w['cpu_seconds'] for w in late)/sum(w['end_seconds']-w['start_seconds'] for w in late),
        'maximum_state_subnormal_components':max(sum(w['subnormal_counts'][x] for x in ('q','p','board_qp')) for w in windows),
        'maximum_port_product_subnormals':max(w['subnormal_counts']['port_products'] for w in windows)}

def compare(folder,label,baseline,candidate):
    a=np.fromfile(folder/'baseline.f64',dtype=np.float64).reshape(-1,2)
    b=np.fromfile(folder/f'{label}.f64',dtype=np.float64).reshape(-1,2)
    d=b-a;energy=np.mean(a*a);maxdiff=float(np.max(abs(d)))
    delta=[v['mechanical_energy_J']-u['mechanical_energy_J'] for u,v in zip(baseline['windows'],candidate['windows'])]
    return {'maximum_absolute_pressure_difference':maxdiff,'maximum_difference_below1e_20':maxdiff<1e-20,
        'float64_pressure_samples_identical':bool(np.array_equal(a,b)),
        'null_rms_db_relative_baseline':None if maxdiff==0 else float(10*np.log10(np.mean(d*d)/max(energy,1e-300))),
        'maximum_absolute_mechanical_energy_delta_J':float(max(abs(x) for x in delta)),
        'energy_delta_relative_maximum_sampled_baseline_energy':float(max(abs(x) for x in delta)/max(w['mechanical_energy_J'] for w in baseline['windows'])),
        'speedup_to4p35':baseline['cpu_to4p35_seconds']/candidate['cpu_to4p35_seconds'],
        'speedup_total':baseline['process_cpu_seconds']/candidate['process_cpu_seconds']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'out/full-denormal-study')
    p.add_argument('--compiler',default='g++');p.add_argument('--duration',type=float,default=8.35);p.add_argument('--rate',type=int,default=48000)
    p.add_argument('--portable',action='store_true',help='Add one explicit portable-floor trial after the baseline/FTZ diagnostic')
    args=p.parse_args()
    if not 5<=args.duration<=10 or args.rate not in (48000,192000):p.error('Bounded duration5..10s and rate48/192k')
    assert sha(SOURCE)==SOURCE_SHA and sha(SOURCE.parent/'calibration.h')==CAL_SHA
    folder=args.output_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    if not args.portable:
        shutil.copyfile(SOURCE,folder/'source.cpp');shutil.copyfile(SOURCE.parent/'calibration.h',folder/'calibration.h')
        (folder/'tool-diagnostic-input.py').write_bytes(Path(__file__).read_bytes())
        harness=folder/'diagnostic.cpp';harness.write_text(HARNESS.replace('@SOURCE@','source.cpp'));binary=folder/'diagnostic'
        run([args.compiler,*flags,harness,'-o',binary],folder/'diagnostic-compile')
        report={'schema_version':1,'source_sha256':SOURCE_SHA,'calibration_sha256':CAL_SHA,'tool_sha256':sha(Path(__file__)),
            'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],'flags':flags,'platform':platform.platform(),
            'duration_seconds':args.duration,'sample_rate':args.rate,'events':'Synthetic C8/MIDI108 velocity93 at0.1s; release4.15s; no pedal. No recording/features read.',
            'cpu_policy':'0.25s solver windows, diagnostic scans and file I/O excluded; exact cumulative4.35s checkpoint.',
            'subnormal_policy':'IEEE754 binary32 exponent/mantissa bit classification (FP_SUBNORMAL equivalent), independent of DAZ; double return values are classified after conversion back to their original float precision.',
            'binary_sha256':sha(binary),'harness_sha256':sha(harness),'variants':{},
            'limits':'One sequential long synthesized-note trial per variant; CPU timing reduces scheduling noise but shared-host frequency/contention remains possible. Instantaneous deletion bound is not a coupled-trajectory proof.'}
        for label,mode in [('baseline','baseline'),('ftz','ftz')]:
            rows=json.loads(run([binary,mode,folder/label,args.duration,args.rate],folder/f'{label}-run'))
            assert rows['caller_csr_restored'] and rows['finite_audio']
            report['variants'][label]={'metrics':rows,'summary':analyze(rows),'wav_sha256':sha(folder/f'{label}.wav'),'precise_pressure_sha256':sha(folder/f'{label}.f64')}
            print(label,json.dumps(report['variants'][label]['summary']),flush=True)
        report['variants']['ftz']['comparison']=compare(folder,'ftz',report['variants']['baseline']['metrics'],report['variants']['ftz']['metrics'])
    else:
        report=json.loads((folder/'report.json').read_text());assert report['source_sha256']==SOURCE_SHA and report['calibration_sha256']==CAL_SHA
        assert report['duration_seconds']==args.duration and report['sample_rate']==args.rate
        (folder/'tool-portable-input.py').write_bytes(Path(__file__).read_bytes())
        source=portable((folder/'source.cpp').read_text());candidate=folder/'portable.cpp';candidate.write_text(source)
        (folder/'portable.patch').write_text(''.join(difflib.unified_diff((folder/'source.cpp').read_text().splitlines(True),source.splitlines(True),fromfile='pinned/source.cpp',tofile='portable.cpp')))
        harness=folder/'portable-harness.cpp';harness.write_text(HARNESS.replace('@SOURCE@','portable.cpp'));binary=folder/'portable'
        run([args.compiler,*flags,harness,'-o',binary],folder/'portable-compile')
        rows=json.loads(run([binary,'baseline',folder/'portable',args.duration,args.rate],folder/'portable-run'))
        assert rows['caller_csr_restored'] and rows['finite_audio']
        report['portable_tool_sha256']=sha(Path(__file__))
        report['variants']['portable']={'source_sha256':sha(candidate),'harness_sha256':sha(harness),'binary_sha256':sha(binary),
            'metrics':rows,'summary':analyze(rows),'wav_sha256':sha(folder/'portable.wav'),'precise_pressure_sha256':sha(folder/'portable.f64'),
            'comparison':compare(folder,'portable',report['variants']['baseline']['metrics'],rows),
            'policy':'Explicit1e-33 q/p floor,1e-30 incoming double force/impulse floor, double unison impulse calculation; no production FP-environment assumption.'}
        print('portable',json.dumps(report['variants']['portable']['summary']),flush=True)
    report['pinned_inputs_unchanged']=sha(SOURCE)==SOURCE_SHA and sha(SOURCE.parent/'calibration.h')==CAL_SHA
    report['portable_trial_run']='portable' in report['variants']
    write(folder/'report.json',report)
    print(folder/'report.json')

if __name__=='__main__':main()
