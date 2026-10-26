#!/usr/bin/env python3
"""Study a reciprocal mechanism/body cache on frozen full-API copies only.

Default phases build, audit local work and render bounded correctness cases.
Timing requires the explicit benchmark phase after host-load coordination.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,platform,re,shutil,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
INPUTS=['src/full_instrument/FullInstrument.cpp','src/full_instrument/PreparedModel.h',
'src/full_instrument/PreparedCalibration.h','include/keyra/FullInstrument.h',
'include/keyra/physics/MechanismExciter.h','include/keyra/physics/StrikeController.h',
'include/keyra/physics/ContactSolver.h']
CACHE=r'''
#pragma once
#include "PreparedModel.h"
#include "keyra/physics/MechanismExciter.h"
#include <array>
#include <vector>
namespace mechanism_cache {
constexpr std::array<unsigned,4> groups{{1,1,1,0}};
// Coefficients are owned separately from the mutable board. No alias assertion.
struct BodyCache {
  struct Node {std::array<double,2> impulse{},dampingObserver{};};
  std::vector<Node> nodes;
  std::array<std::array<double,2>,2> gram{},forceObserver{};
  std::array<double,2> velocity{},impulse{};
  void prepare(const grand::Piano& model) {
    nodes.resize(model.board.size());gram={};forceObserver={};
    for(unsigned g=0;g<2;++g)for(unsigned h=0;h<2;++h)gram[g][h]=model.boardGram[g][h];
    for(size_t i=0;i<nodes.size();++i){const auto& z=model.board[i];auto& n=nodes[i];
      for(unsigned g=0;g<2;++g)n.impulse[g]=z.port[g]/z.w;
      for(unsigned ch=0;ch<2;++ch){n.dampingObserver[ch]=-2*z.sigma*z.w*z.mic[ch];
        for(unsigned g=0;g<2;++g)forceObserver[g][ch]+=z.port[g]*z.mic[ch]/model.dt;}
    }
    velocity={};impulse={};
  }
  void begin(const grand::Piano& model) noexcept {
    velocity={};impulse={};
    for(const auto& z:model.board)for(unsigned g=0;g<2;++g)velocity[g]+=z.port[g]*z.w*z.p;
  }
  keyra::physics::MechanismBodyPort port(unsigned group) const noexcept {return {velocity[group],gram[group][group]};}
  void add(unsigned group,double value) noexcept {
    impulse[group]+=value;
    for(unsigned h=0;h<2;++h)velocity[h]+=gram[h][group]*value;
  }
  std::array<double,2> finish(grand::Piano& model) noexcept {
    std::array<double,2> out{};
    for(unsigned g=0;g<2;++g)for(unsigned ch=0;ch<2;++ch)out[ch]+=forceObserver[g][ch]*impulse[g];
    for(size_t i=0;i<nodes.size();++i){auto& z=model.board[i];const auto& n=nodes[i];
      const double old=z.p;
      z.p=old+n.impulse[0]*impulse[0]+n.impulse[1]*impulse[1];
      const double change=double(z.p)-old;
      for(unsigned ch=0;ch<2;++ch)out[ch]+=n.dampingObserver[ch]*change;
    }
    return out;
  }
};
inline keyra::physics::MechanismBodyPort originalPort(const grand::Piano& model,unsigned group) noexcept {
  keyra::physics::MechanismBodyPort port;
  for(const auto& z:model.board){port.velocity+=z.port[group]*z.w*z.p;port.inverseMass+=z.port[group]*z.port[group];}return port;
}
inline void originalImpulse(grand::Piano& model,unsigned group,double impulse) noexcept {
  for(auto& z:model.board)z.p+=z.port[group]*impulse/z.w;
}
inline double boardEnergy(const grand::Piano& model) noexcept {
  double out=0;for(const auto& z:model.board){const double q=z.q,p=z.p;out+=.5*z.w*z.w*(q*q+p*p);}return out;
}
}
'''
CANDIDATE_BLOCK=r'''    bodyCache.begin(*model);
    double direct=0;bool applied=false;
    for(unsigned i=0;i<4;++i){
      const auto result=mechanisms[i].step(bodyCache.port(bodyGroups[i]));
      if(result.bodyImpulse!=0){bodyCache.add(bodyGroups[i],result.bodyImpulse);applied=true;}
      direct+=mechanisms[i].directObservation();
    }
    if(applied){const auto delta=bodyCache.finish(*model);for(unsigned ch=0;ch<2;++ch)out[ch]+=delta[ch];}
    if(direct!=0)for(auto& value:out)value+=direct;
    return out;'''
SNAPSHOT=r'''
extern "C" bool mechanism_snapshot(const keyra::FullInstrument* piano,const char* prefix){
  const auto& impl=*piano->impl_;const auto& model=*impl.model;bool ok=true;
  auto save=[&](const char* kind,const auto& produce){
    const auto path=std::string(prefix)+"."+kind+".f64le";FILE* file=std::fopen(path.c_str(),"wb");if(!file){ok=false;return;}
    auto scalar=[&](const auto& v){const double x=double(v);if(std::fwrite(&x,sizeof(x),1,file)!=1)ok=false;};produce(scalar);
    if(std::fclose(file))ok=false;
  };
  save("strings",[&](const auto& add){for(const auto& s:model.strings)for(size_t j=0;j<s.m.size();++j){add(s.m.q[j]);add(s.m.p[j]);add(s.m.damp[j]);}});
  save("board",[&](const auto& add){for(const auto& z:model.board){add(z.q);add(z.p);add(z.force);}});
  save("hammers",[&](const auto& add){for(const auto& k:model.keys){add(k.hammerX);add(k.hammerV);add(k.K);add(k.age);add(k.hammerActive);}});
  save("mechanisms",[&](const auto& add){for(const auto& m:impl.mechanisms)for(const auto& z:m.modes_){add(z.x);add(z.v);}});
  save("controller",[&](const auto& add){for(int note=21;note<=108;++note){const auto& s=impl.controller.state(note);
    add(s.down);add(s.pending);add(s.hasLaunched);add(s.recovery);add(s.returnDepth);add(s.keyLift);add(s.returnVelocity);
    add(s.elapsedSinceLaunch);add(s.pendingAge);add(s.pendingVelocity);add(s.pendingLift);add(s.pendingVelocityFactor);add(s.pendingHardnessFactor);
    add(s.correlatedVelocity);add(s.correlatedHardness);add(s.random);add(s.requests);add(s.launches);add(s.pendingId);}});
  return ok;
}
'''
HARNESS=r'''
#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <string>
#include <vector>
extern "C" bool mechanism_snapshot(const keyra::FullInstrument*,const char*);
extern "C" const double* mechanism_pressure();
struct Event{unsigned frame;char kind;int note;double value;};
int main(int argc,char** argv){if(argc!=3)return 2;const std::string dir=argv[1];const unsigned rate=std::stoul(argv[2]);
 const unsigned frames=unsigned(rate*.35);bool first=true;std::printf("{\"sample_rate\":%u,\"cases\":[",rate);
 for(unsigned c=0;c<7;++c){
  const char* names[]={"C4","music","repeats","C4-source-off","C4-coupling-off","C4-direct-off","silent"};
  keyra::FullInstrumentConfig config;config.sampleRate=rate;config.seed=0x4b657972u;
  if(c==3)config.parameters.mechanicalLevel=0;if(c==4)config.mechanismBodyCoupling=false;if(c==5)config.mechanismObservation=false;
  keyra::FullInstrument piano;if(!piano.prepare(config))return 3;
  std::vector<Event> events;
  auto at=[&](double t,char kind,int n,double value){events.push_back({unsigned(std::llround(t*rate)),kind,n,value});};
  if(c!=6){at(0,'p',0,1);at(0,'+',60,.72);at(.15,'-',60,0);at(.22,'p',0,0);}
  if(c==1){at(0,'+',36,.5);at(0,'+',67,.64);at(.08,'+',64,.69);at(.18,'+',72,.63);at(.30,'-',36,0);at(.30,'-',67,0);at(.30,'-',64,0);at(.30,'-',72,0);}
  if(c==2){events.clear();at(0,'p',0,1);at(0,'+',60,.72);at(.005,'+',60,.72);at(.01,'+',60,.72);at(.10,'-',60,0);at(.10,'+',60,.72);at(.20,'-',60,0);at(.20,'+',60,.72);at(.30,'-',60,0);at(.30,'p',0,0);}
  std::stable_sort(events.begin(),events.end(),[](const auto& a,const auto& b){return a.frame<b.frame;});
  std::vector<float> left(frames),right(frames);std::vector<double> times;times.reserve(frames/64+events.size());size_t next=0;unsigned start=0;bool snapshot=false;
  while(start<frames){
   while(next<events.size()&&events[next].frame==start){const auto& e=events[next++];const bool ok=e.kind=='p'?piano.sustain(e.value):e.kind=='+'?piano.noteOn(e.note,e.value):piano.noteOff(e.note);if(!ok)return 4;}
   unsigned end=std::min(frames,start+64);if(next<events.size())end=std::min(end,events[next].frame);
   const auto before=std::clock();if(!piano.process(left.data()+start,right.data()+start,end-start))return 5;
   times.push_back(double(std::clock()-before)/CLOCKS_PER_SEC);start=end;
   if(!snapshot&&start>=frames/2){snapshot=true;if(!mechanism_snapshot(&piano,(dir+"/"+names[c]+"-mid").c_str()))return 6;}
  }
  if(!mechanism_snapshot(&piano,(dir+"/"+names[c]+"-end").c_str()))return 7;
  FILE* f=std::fopen((dir+"/"+names[c]+".f32le").c_str(),"wb");if(!f)return 8;
  for(unsigned i=0;i<frames;++i){const float x[2]={left[i],right[i]};if(!std::isfinite(x[0])||!std::isfinite(x[1])||std::fwrite(x,sizeof(float),2,f)!=2)return 9;}std::fclose(f);
  f=std::fopen((dir+"/"+names[c]+".pressure.f64le").c_str(),"wb");if(!f)return 10;
  if(std::fwrite(mechanism_pressure(),sizeof(double),2*frames,f)!=2*frames)return 11;std::fclose(f);
  const auto d=piano.diagnostics();if(d.faultFlags||d.unsafeLaunches||d.stringCount!=230||d.stringModes!=17778||d.boardModes!=475)return 12;
  if(!first)std::printf(",");first=false;
  std::printf("{\"name\":\"%s\",\"frames\":%u,\"requests\":%llu,\"launches\":%llu,\"deferred\":%llu,\"coalesced\":%llu,\"cancelled\":%llu,\"expired\":%llu,\"fault_flags\":%u,\"process_cpu_seconds\":[",names[c],frames,(unsigned long long)d.requests,(unsigned long long)d.launches,(unsigned long long)d.deferred,(unsigned long long)d.coalesced,(unsigned long long)d.cancelled,(unsigned long long)d.expired,d.faultFlags);
  for(size_t i=0;i<times.size();++i)std::printf("%s%.17g",i?",":"",times[i]);std::printf("]}");
 }
 std::printf("]}\n");return 0;
}
'''
PHYSICS=r'''
#include "BodyCache.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <random>
using keyra::physics::MechanismExciter;
int main(){bool all=true,first=true;std::printf("{\"cases\":[");
for(int rate:{48000,96000})for(double amplitude:{1.e-7,1.e-4,.1})for(bool trigger:{false,true})for(double resistance:{1.,1000.}){
 grand::Options options;options.sampleRate=rate;grand::Piano model(options);std::mt19937 random(412);std::normal_distribution<double> normal;
 for(auto& z:model.board){z.p=float(amplitude*normal(random)/z.w);z.q=0;}
 std::array<MechanismExciter,4> sources;for(unsigned i=0;i<4;++i){auto c=keyra::physics::mechanismPreset(static_cast<keyra::physics::MechanismKind>(i),rate);c.couplingResistanceKgPerSecond*=.025*resistance;if(!sources[i].prepare(c))return 2;}
 mechanism_cache::BodyCache cache;cache.prepare(model);
 const double initial=mechanism_cache::boardEnergy(model);double scale=initial,maximumRise=0,maximumWork=0,maxSourceResidual=0,external=0,previous=initial,maxSourceEnergy=0;bool valid=true;unsigned samples=1000;
 for(unsigned frame=0;frame<samples;++frame){
  if(trigger&&frame%97==0)for(auto& source:sources){const double w=source.trigger(.37);external+=w;scale+=std::abs(w);}
  const double bodyBefore=mechanism_cache::boardEnergy(model);double totalBefore=bodyBefore;for(const auto& s:sources)totalBefore+=s.energy();double bodyWork=0,loss=0;
#if KEYRA_MECHANISM_CACHE
  cache.begin(model);
#endif
  for(unsigned i=0;i<4;++i){const auto g=mechanism_cache::groups[i];
#if KEYRA_MECHANISM_CACHE
   const auto result=sources[i].step(cache.port(g));if(result.bodyImpulse!=0)cache.add(g,result.bodyImpulse);
#else
   const auto result=sources[i].step(mechanism_cache::originalPort(model,g));if(result.bodyImpulse!=0)mechanism_cache::originalImpulse(model,g,result.bodyImpulse);
#endif
   valid=valid&&result.valid;bodyWork+=result.bodyWork;loss+=result.internalDissipation+result.couplingDissipation+result.retirementDissipation;maxSourceResidual=std::max(maxSourceResidual,std::abs(result.balanceResidual));
  }
#if KEYRA_MECHANISM_CACHE
  (void)cache.finish(model);
#endif
  const double bodyAfter=mechanism_cache::boardEnergy(model);double totalAfter=bodyAfter,sourceEnergy=0;for(const auto& s:sources)sourceEnergy+=s.energy();totalAfter+=sourceEnergy;maxSourceEnergy=std::max(maxSourceEnergy,sourceEnergy);
  const double normalizer=std::max(scale,1.e-300);maximumRise=std::max(maximumRise,(totalAfter-totalBefore)/normalizer);maximumWork=std::max(maximumWork,std::abs(bodyAfter-bodyBefore-bodyWork)/normalizer);
  valid=valid&&std::isfinite(totalAfter)&&totalAfter>=0;previous=totalAfter;
 }
 const bool pass=valid&&maximumRise<=5.e-7&&maximumWork<=1.e-6&&maxSourceEnergy>0;all=all&&pass;
 if(!first)std::printf(",");first=false;
 std::printf("{\"rate\":%d,\"board_amplitude\":%.17g,\"triggered\":%s,\"resistance_multiplier\":%.17g,\"frames\":%u,\"initial_board_J\":%.17g,\"external_work_J\":%.17g,\"final_total_J\":%.17g,\"maximum_source_energy_J\":%.17g,\"max_step_rise_over_energy_scale\":%.17g,\"max_board_work_mismatch_over_energy_scale\":%.17g,\"max_source_balance_residual_J\":%.17g,\"valid\":%s,\"passed\":%s}",rate,amplitude,trigger?"true":"false",resistance,samples,initial,external,previous,maxSourceEnergy,maximumRise,maximumWork,maxSourceResidual,valid?"true":"false",pass?"true":"false");
}std::printf("],\"passed\":%s}\n",all?"true":"false");return all?0:3;}
'''
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def once(text,old,new):
 if text.count(old)!=1:raise RuntimeError('Nonunique transformation: '+old[:90])
 return text.replace(old,new,1)
def verify(out):
 expected=json.loads((out/'source-inputs.json').read_text())
 revisions=json.loads((out/'analysis-revisions.json').read_text()) if (out/'analysis-revisions.json').exists() else {}
 for name,digest in expected.items():
  if sha(out/'source-snapshot'/name)!=digest:raise RuntimeError('Snapshot changed: '+name)
  actual=sha(ROOT/name)
  if actual!=digest:
   row=revisions.get(name,{})
   if name in INPUTS or row.get('original_sha256')!=digest or row.get('current_sha256')!=actual or sha(row['snapshot'])!=actual:raise RuntimeError('Unrecorded source change: '+name)
def transformed(api):
 api=once(api,'#include "PreparedModel.h"','#include "PreparedModel.h"\n#include "BodyCache.h"\n#include <cstdio>\n#include <string>\nnamespace {std::array<double,100000> capturedPressure{};}\nextern "C" const double* mechanism_pressure(){return capturedPressure.data();}')
 api=once(api,'  double pole=0,gain=1,velocityExponent=1;','  double pole=0,gain=1,velocityExponent=1;\n#if KEYRA_MECHANISM_CACHE\n  mechanism_cache::BodyCache bodyCache;\n#endif')
 begin=api.index('    const auto original=boardObservation();');end=api.index('\n  }\n};',begin)
 block=api[begin:end]
 api=api[:begin]+'#if KEYRA_MECHANISM_CACHE\n'+CANDIDATE_BLOCK+'\n#else\n'+block+'\n#endif'+api[end:]
 api=once(api,'  impl_->pole=std::exp(-2*grand::pi*24/c.sampleRate);','''#if KEYRA_MECHANISM_CACHE
  impl_->bodyCache.prepare(*impl_->model);
#endif
  impl_->pole=std::exp(-2*grand::pi*24/c.sampleRate);''')
 api=once(api,'    auto x=impl_->step();','    auto x=impl_->step();\n    capturedPressure[2*impl_->frame]=x[0];capturedPressure[2*impl_->frame+1]=x[1];')
 return api+SNAPSHOT,block

def prepare(out):
 out.mkdir(parents=True,exist_ok=False);inputs=INPUTS+['tools/probe_full_mechanism_cache.py','docs/FULL_MECHANISM_CACHE.md'];hashes={name:sha(ROOT/name) for name in inputs}
 (out/'source-inputs.json').write_text(json.dumps(hashes,indent=2)+'\n')
 for name in inputs:
  dest=out/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
 include=out/'include'
 for name in INPUTS[3:]:
  dest=include/Path(name).relative_to('include');dest.parent.mkdir(parents=True,exist_ok=True);text=(ROOT/name).read_text()
  if name.endswith(('FullInstrument.h','MechanismExciter.h')):text=once(text,'private:','public: // snapshot diagnostic only')
  dest.write_text(text)
 for name in ['PreparedModel.h','PreparedCalibration.h']:shutil.copyfile(ROOT/'src/full_instrument'/name,out/name)
 api,block=transformed((ROOT/INPUTS[0]).read_text());(out/'FullInstrument.cpp').write_text(api);(out/'BodyCache.h').write_text(CACHE);(out/'harness.cpp').write_text(HARNESS);(out/'physics.cpp').write_text(PHYSICS)
 # The entire original mechanism stage survives unmodified in the baseline branch.
 assert block in api and block==(ROOT/INPUTS[0]).read_text().split('    const auto original=boardObservation();',1)[1].split('\n  }\n};',1)[0].join(['    const auto original=boardObservation();',''])
 flags=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-DKEYRA_FULL_PRESSURE_SIMD=0','-DKEYRA_FULL_FAST_CONTACT=1','-I'+str(include),'-I'+str(out)]
 builds={}
 for label,macro in [('baseline',0),('cached',1)]:
  folder=out/label;folder.mkdir();commands=[]
  for source,target in [('FullInstrument.cpp','api.o'),('harness.cpp','harness.o')]:
   command=['g++',*flags,'-DKEYRA_MECHANISM_CACHE='+str(macro),'-c',str(out/source),'-o',str(folder/target)];commands.append(command);subprocess.run(command,check=True,capture_output=True)
  command=['g++',str(folder/'api.o'),str(folder/'harness.o'),'-o',str(folder/'probe')];commands.append(command);subprocess.run(command,check=True,capture_output=True)
  command=['g++',*flags,'-DKEYRA_MECHANISM_CACHE='+str(macro),str(out/'physics.cpp'),'-o',str(folder/'physics')];commands.append(command);subprocess.run(command,check=True,capture_output=True)
  builds[label]={'commands':commands,'probe_sha256':sha(folder/'probe'),'physics_sha256':sha(folder/'physics')}
 (out/'build.json').write_text(json.dumps({'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],'platform':platform.platform(),'variants':builds,'original_mechanism_stage_verbatim_in_baseline':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n');verify(out)
 print('Frozen sources and both native variants compiled',flush=True)

def physics(out):
 verify(out);reports={}
 for label in ['baseline','cached']:
  call=subprocess.run([str(out/label/'physics')],capture_output=True,text=True);(out/label/'physics.json').write_text(call.stdout);(out/label/'physics.stderr').write_text(call.stderr)
  if call.returncode:raise RuntimeError(label+' physics failed: '+call.stdout[-600:]+call.stderr)
  reports[label]=json.loads(call.stdout)
 (out/'physics-summary.json').write_text(json.dumps(reports,indent=2)+'\n');verify(out);print('Local reciprocal work audit passed',flush=True)

def difference(a,b):
 rms=float(np.sqrt(np.mean(a*a)));delta=b-a;null=float(np.sqrt(np.mean(delta*delta)))
 return {'byte_identical':a.tobytes()==b.tobytes(),'rms_baseline':rms,'rms_difference':null,'null_db_relative_rms':20*np.log10(null/rms) if null and rms else None,'maximum_absolute_difference':float(np.max(np.abs(delta)))}

def render(out):
 verify(out);summary={};runs={}
 for rate in [48000,96000]:
  for label in ['baseline','cached']:
   folder=out/'renders'/str(rate)/label;folder.mkdir(parents=True,exist_ok=True)
   if (folder/'report.json').exists():
    # Reuse only the completed first-pass renders pinned before correcting the
    # overly strict continuous-state analysis guard. Never trust arbitrary files.
    receipt=json.loads((out/'v1-render-failure.json').read_text())
    for name,digest in receipt['raw_artifacts'].items():
     if sha(out/name)!=digest:raise RuntimeError('Pinned first-pass render changed: '+name)
    runs[(rate,label)]=json.loads((folder/'report.json').read_text())
   else:
    call=subprocess.run([str(out/label/'probe'),str(folder),str(rate)],text=True,capture_output=True);(folder/'report.json').write_text(call.stdout);(folder/'stderr.txt').write_text(call.stderr)
    if call.returncode:raise RuntimeError(f'{rate} {label} render failed{call.returncode}: '+call.stderr)
    runs[(rate,label)]=json.loads(call.stdout)
   print(f'{rate} {label} correctness renders finished',flush=True)
  baseline=out/'renders'/str(rate)/'baseline';cached=out/'renders'/str(rate)/'cached'
  for a,b in zip(runs[(rate,'baseline')]['cases'],runs[(rate,'cached')]['cases']):
   name=a['name'];fields=['requests','launches','deferred','coalesced','cancelled','expired','fault_flags'];assert all(a[k]==b[k] for k in fields),(rate,name)
   row={'diagnostics_identical':True,'diagnostics':{k:a[k] for k in fields},'pre_highpass_pressure':difference(np.fromfile(baseline/(name+'.pressure.f64le'),dtype='<f8'),np.fromfile(cached/(name+'.pressure.f64le'),dtype='<f8')),'api_output':difference(np.fromfile(baseline/(name+'.f32le'),dtype='<f4').astype(float),np.fromfile(cached/(name+'.f32le'),dtype='<f4').astype(float)),'states':{}}
   for checkpoint in ['mid','end']:
    row['states'][checkpoint]={}
    for part in ['strings','board','hammers','mechanisms','controller']:
     row['states'][checkpoint][part]=difference(np.fromfile(baseline/(name+'-'+checkpoint+'.'+part+'.f64le'),dtype='<f8'),np.fromfile(cached/(name+'-'+checkpoint+'.'+part+'.f64le'),dtype='<f8'))
    ca=np.fromfile(baseline/(name+'-'+checkpoint+'.controller.f64le'),dtype='<f8').reshape(88,19)
    cb=np.fromfile(cached/(name+'-'+checkpoint+'.controller.f64le'),dtype='<f8').reshape(88,19)
    assert np.array_equal(ca[:,[0,1,2,15,16,17,18]],cb[:,[0,1,2,15,16,17,18]]),(rate,name,'discrete controller')
    row['states'][checkpoint]['discrete_controller_identical']=True
    row['states'][checkpoint]['continuous_controller_1e10_guard_passed']=row['states'][checkpoint]['controller']['maximum_absolute_difference']<=1.e-10
   if name in ['C4-source-off','C4-coupling-off','silent']:
    assert row['pre_highpass_pressure']['byte_identical'] and row['api_output']['byte_identical'],(rate,name,'ablation')
    assert all(v['byte_identical'] for c in row['states'].values() for v in c.values() if isinstance(v,dict)),(rate,name,'ablation state')
   assert row['api_output']['maximum_absolute_difference']<=2.e-5,(rate,name,'audio guard')
   summary[f'{rate}-{name}']=row
 (out/'render-summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');verify(out)
 print('Bounded comparisons finished; discrete admissions/ablations/audio guards passed. Continuous controller1e-10 failures retained:',sum(not cp['continuous_controller_1e10_guard_passed'] for row in summary.values() for cp in row['states'].values()),flush=True)

def prepare_benchmark(out):
 verify(out);folder=out/'benchmark';folder.mkdir(exist_ok=False)
 api=(out/'FullInstrument.cpp').read_text()
 api=once(api,'    capturedPressure[2*impl_->frame]=x[0];capturedPressure[2*impl_->frame+1]=x[1];','    // No observer capture in the timed binary.')
 harness=(out/'harness.cpp').read_text()
 harness=once(harness,'for(unsigned c=0;c<7;++c){','for(unsigned selected:{1u,2u}){const unsigned c=selected;')
 harness=once(harness,'   if(!snapshot&&start>=frames/2){snapshot=true;if(!mechanism_snapshot(&piano,(dir+"/"+names[c]+"-mid").c_str()))return 6;}','   // No state snapshot between timed process calls.')
 harness=once(harness,'  if(!mechanism_snapshot(&piano,(dir+"/"+names[c]+"-end").c_str()))return 7;','  // No final state snapshot in timing harness.')
 first=harness.index('  f=std::fopen((dir+"/"+names[c]+".pressure.f64le")')
 last=harness.index('  const auto d=piano.diagnostics();',first)
 harness=harness[:first]+harness[last:]
 harness=once(harness,'#include <ctime>','#include <ctime>\n#include <chrono>')
 harness=once(harness,'std::vector<double> times;','std::vector<double> times,walls;')
 harness=once(harness,'const auto before=std::clock();if(!piano.process','const auto wall0=std::chrono::steady_clock::now();const auto before=std::clock();if(!piano.process')
 harness=once(harness,'times.push_back(double(std::clock()-before)/CLOCKS_PER_SEC);start=end;','times.push_back(double(std::clock()-before)/CLOCKS_PER_SEC);walls.push_back(std::chrono::duration<double>(std::chrono::steady_clock::now()-wall0).count());start=end;')
 harness=once(harness,'std::printf("]}");','std::printf(",WALLS_PLACEHOLDER");')
 harness=harness.replace('std::printf(",WALLS_PLACEHOLDER");','std::printf("],\\"process_wall_seconds\\":[");for(size_t i=0;i<walls.size();++i)std::printf("%s%.17g",i?",":"",walls[i]);std::printf("]}");')
 (folder/'FullInstrument.cpp').write_text(api);(folder/'harness.cpp').write_text(harness)
 flags=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-DKEYRA_FULL_PRESSURE_SIMD=0','-DKEYRA_FULL_FAST_CONTACT=1','-I'+str(out/'include'),'-I'+str(out)]
 builds={}
 for label,macro in [('baseline',0),('cached',1)]:
  target=folder/label;target.mkdir();commands=[]
  for source,obj in [('FullInstrument.cpp','api.o'),('harness.cpp','harness.o')]:
   command=['g++',*flags,'-DKEYRA_MECHANISM_CACHE='+str(macro),'-c',str(folder/source),'-o',str(target/obj)];commands.append(command);subprocess.run(command,check=True,capture_output=True)
  command=['g++',str(target/'api.o'),str(target/'harness.o'),'-o',str(target/'probe')];commands.append(command);subprocess.run(command,check=True,capture_output=True)
  builds[label]={'commands':commands,'binary_sha256':sha(target/'probe')}
 receipt={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':['music','repeats'],'sample_rates':[48000,96000],'balanced_orders':[['baseline','cached'],['cached','baseline'],['baseline','cached']],'audio_seconds_per_case':.35,'event_dispatch_prepare_compilation_file_io_excluded':True,'observer_capture_and_state_snapshot_removed_from_timed_binary':True,'full_core_dsp_math_unchanged_from_correctness_variants':True,'source_sha256':{str(p):sha(p) for p in [folder/'FullInstrument.cpp',folder/'harness.cpp',out/'BodyCache.h',out/'PreparedModel.h',out/'PreparedCalibration.h']},'builds':builds}
 (folder/'freeze.json').write_text(json.dumps(receipt,indent=2)+'\n');verify(out);print('Two-case benchmark frozen and compiled; no timings collected',flush=True)

def benchmark(out):
 # Caller must coordinate quiet host. Affinity constrains these child probes only.
 import os
 verify(out);freeze=json.loads((out/'benchmark/freeze.json').read_text())
 for name,digest in freeze['source_sha256'].items():assert sha(name)==digest
 for label,row in freeze['builds'].items():assert sha(out/'benchmark'/label/'probe')==row['binary_sha256']
 allowed=sorted(os.sched_getaffinity(0));cpu=allowed[0]
 schedule={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'affinity_supported':True,'available_cpus':allowed,'selected_cpu':cpu,'policy':'Same first available logical CPU for every child; host isolation and certified worst-case timing are not claimed.','freeze_sha256':sha(out/'benchmark/freeze.json')}
 (out/'benchmark/schedule.json').write_text(json.dumps(schedule,indent=2)+'\n');runs=[]
 for trial,order in enumerate(freeze['balanced_orders']):
  for rate in freeze['sample_rates']:
   for label in order:
    folder=out/'timings'/f'trial{trial}'/str(rate)/label;folder.mkdir(parents=True,exist_ok=True)
    call=subprocess.run(['taskset','-c',str(cpu),str(out/'benchmark'/label/'probe'),str(folder),str(rate)],text=True,capture_output=True);(folder/'report.json').write_text(call.stdout);(folder/'stderr.txt').write_text(call.stderr)
    if call.returncode:raise RuntimeError(call.stderr)
    data=json.loads(call.stdout)
    for row in data['cases']:
     # The streamlined timing harness must preserve its correctness render.
     original=out/'renders'/str(rate)/label/(row['name']+'.f32le')
     assert sha(folder/(row['name']+'.f32le'))==sha(original),(trial,rate,label,row['name'])
     cpu_times=np.array(row['process_cpu_seconds']);runs.append({'trial':trial,'rate':rate,'variant':label,'name':row['name'],'cpu_per_audio':float(cpu_times.sum()/(row['frames']/rate)),'peak_process_cpu_seconds':float(cpu_times.max()),'p95_process_cpu_seconds':float(np.quantile(cpu_times,.95)),'audio_exact_to_correctness_binary':True,'wall_per_audio':float(np.sum(row['process_wall_seconds'])/(row['frames']/rate)),'peak_process_wall_seconds':float(np.max(row['process_wall_seconds'])),'p95_process_wall_seconds':float(np.quantile(row['process_wall_seconds'],.95))})
    print(f'timing trial{trial} {rate} {label}',flush=True);verify(out)
 (out/'timing-summary.json').write_text(json.dumps(runs,indent=2)+'\n')

def report(out):
 verify(out)
 data={'schema_version':1,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Copied complete FullInstrument reciprocal mechanism/body cache research','canonical_sources_unchanged':True,'pressure_simd':False,'fast_contact':True,'default_adopted':False,'original_mechanism_stage_verbatim_in_baseline':True,'source_sha256':json.loads((out/'source-inputs.json').read_text()),'build':json.loads((out/'build.json').read_text()),'limits':['One cached board write changes float rounding and mechanical state; this is not an observer-only or bit-exact mechanical transformation.','Sequential Gram feedback is equivalent in real arithmetic; actual float energy/work mismatch is independently measured.','Correctness render CPU traces are not used as performance evidence; a quiet explicit benchmark phase is required.','No actual Reason host, SDK, realtime qualification or audibility approval.']}
 for name in ['physics-summary','render-summary','timing-summary','timing-analysis','absolute-stereo-controller-analysis','cache-contract-asan','findings']:
  p=out/(name+'.json')
  if p.exists():data[name.replace('-','_')]=json.loads(p.read_text())
 if (out/'analysis-revisions.json').exists():data['analysis_revisions']=json.loads((out/'analysis-revisions.json').read_text())
 if (out/'independent-cli/report.json').exists():data['independent_actual_api_baseline']=json.loads((out/'independent-cli/report.json').read_text())
 data['artifacts']={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p not in [out/'report.json',out/'artifact-manifest.json']}
 (out/'report.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');target=ROOT/'Validation/full-mechanism-cache.json';target.write_text((out/'report.json').read_text());print(target,flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'out/full-mechanism-cache');parser.add_argument('--phase',choices=['prepare','physics','render','prepare-benchmark','benchmark','report','correctness'],default='correctness');args=parser.parse_args();out=args.out.resolve()
 if args.phase in ['prepare','correctness']:prepare(out)
 if args.phase in ['physics','correctness']:physics(out)
 if args.phase in ['render','correctness']:render(out)
 if args.phase=='prepare-benchmark':prepare_benchmark(out)
 if args.phase=='benchmark':benchmark(out)
 if args.phase not in ['prepare','prepare-benchmark']:report(out)
if __name__=='__main__':main()
