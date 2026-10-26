from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent;SOURCE=ROOT/'out/full-render-validation/sources';PRIVATE=OUT/'producer-sources';MODEL=PRIVATE/'src/full_instrument';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=json.loads((ROOT/'out/full-performance/renderer-validation.json').read_text());protocol=ROOT/'out/full-causal-radiation-metrics/v1/protocol.json';assert sha(protocol)=='5ec7ace5cffb6655fb017430d328dc784762beb9ff5460eb5c63a07e606b96fa';math=OUT/'math-validation.json';assert json.loads(math.read_text())['passed']
for name,digest in proof['source_sha256'].items():
 assert sha(SOURCE/name)==digest,name
 target=PRIVATE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/name,target)
def once(text,old,new):
 assert text.count(old)==1,old[:80]
 return text.replace(old,new,1)
trace=r'''
#pragma once
#include <array>
namespace causal_trace {inline std::array<double,88> force{};inline std::array<double,3> bridge{};}
'''
capture=r'''
#pragma once
#include "Trace.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
namespace causal_capture {
inline size_t count=0;inline int note=48;
inline std::vector<std::array<float,2>> candidate;
inline std::array<std::vector<std::array<float,2>>,3> stems;
inline std::vector<std::array<double,3>> driver;
// rawold2,rawboard2,newcorrection2,energy,freeLoss,loadLoss,work,balance,forceNote,bridge3.
inline std::vector<std::array<double,15>> trace;
inline std::vector<std::array<uint64_t,3>> stateProof,forceProof;
inline uint64_t mismatch=0,candidateFaults=0;
inline void begin(size_t n,int midi){count=n;note=midi;candidate.resize(n);driver.resize(n);trace.resize(n);forceProof.resize(n);stateProof.clear();stateProof.reserve(n/256+2);for(auto& stem:stems)stem.resize(n);mismatch=candidateFaults=0;}
inline void reset() noexcept {mismatch=candidateFaults=0;stateProof.clear();}
inline void bytes(uint64_t& h,const void* p,size_t size) noexcept {const auto* data=static_cast<const unsigned char*>(p);for(size_t i=0;i<size;++i){h^=data[i];h*=1099511628211ull;}}
template<class T> inline void scalar(uint64_t& h,const T& x) noexcept {bytes(h,&x,sizeof(x));}
inline uint64_t forceHash() noexcept {uint64_t h=14695981039346656037ull;bytes(h,causal_trace::force.data(),sizeof(causal_trace::force));bytes(h,causal_trace::bridge.data(),sizeof(causal_trace::bridge));return h;}
inline uint64_t stateHash(const grand::Piano& p) noexcept {
 uint64_t h=14695981039346656037ull;
 for(const auto& st:p.strings){for(const auto* a:{&st.m.q,&st.m.p,&st.m.damp})bytes(h,a->data(),a->size()*sizeof(float));scalar(h,st.velocity);scalar(h,st.force);}
 for(const auto& z:p.board){scalar(h,z.q);scalar(h,z.p);scalar(h,z.force);}
 for(const auto& k:p.keys){scalar(h,k.hammerX);scalar(h,k.hammerV);scalar(h,k.age);scalar(h,k.K);scalar(h,k.down);scalar(h,k.hammerActive);scalar(h,k.everStruck);scalar(h,k.damperPosition);scalar(h,k.cachedContact);scalar(h,k.cachedLoss);}
 scalar(h,p.pedal);scalar(h,p.pedalTarget);scalar(h,p.maxForce);scalar(h,p.contactTime);scalar(h,p.maxContactResidual);scalar(h,p.forceSolves);scalar(h,p.faultFlags);return h;
}
template<class T> bool write(const char* folder,const char* name,const T& data){char path[4096];const int n=std::snprintf(path,sizeof(path),"%s/%s",folder,name);if(n<0||size_t(n)>=sizeof(path))return false;FILE* f=std::fopen(path,"wb");if(!f)return false;const bool ok=std::fwrite(data.data(),sizeof(data[0]),data.size(),f)==data.size();return std::fclose(f)==0&&ok;}
}
'''
(MODEL/'Trace.h').write_text(trace);(MODEL/'Capture.h').write_text(capture)
model=(MODEL/'PreparedModel.h').read_text();model=once(model,'#include "PreparedCalibration.h"','#include "PreparedCalibration.h"\n#include "Trace.h"')
model=once(model,'  void oscillators(){','  void oscillators(){\n    causal_trace::force={};')
model=once(model,'        double F=contact(k,d0,xf-yf);','        double F=contact(k,d0,xf-yf);\n        causal_trace::force[size_t(&k-keys.data())]=F;')
model=once(model,'  void bridgeStep(double step,bool cacheRadiation=false){','  void bridgeStep(double step,bool cacheRadiation=false){\n    causal_trace::bridge={};')
model=once(model,'    for(int g=0;g<3;++g)for(int h=0;h<3;++h)correction[g]+=.5*step*boardGram[g][h]*total[h];','    causal_trace::bridge=total;\n    for(int g=0;g<3;++g)for(int h=0;h<3;++h)correction[g]+=.5*step*boardGram[g][h]*total[h];');(MODEL/'PreparedModel.h').write_text(model)
api=(MODEL/'FullInstrument.cpp').read_text();api=once(api,'#include "PreparedModel.h"','#include "PreparedModel.h"\n#include "CausalRadiation.h"\n#include "Capture.h"')
api=once(api,'  double pole=0,gain=1,velocityExponent=1;','  double pole=0,gain=1,velocityExponent=1;\n  keyra_causal::Observer causal;\n  std::array<double,2> causalPrevious{},causalHighpass{};\n  std::array<std::array<double,2>,3> stemPrevious{},stemHighpass{};')
api=once(api,'    for (auto& source:mechanisms) source.reset();','    for (auto& source:mechanisms) source.reset();\n    causal.reset();causalPrevious={};causalHighpass={};stemPrevious={};stemHighpass={};causal_capture::reset();')
api=once(api,'  impl_->model=std::move(model);impl_->config=c;','  impl_->model=std::move(model);impl_->config=c;\n  impl_->model->opt.captureStems=true;\n  if(!impl_->causal.prepare(*impl_->model))return false;')
api=once(api,'    auto x=impl_->step();',r'''    auto x=impl_->step();
    const size_t frame=size_t(impl_->frame);
    const auto beforeForce=causal_capture::forceHash();
    const bool checkpoint=(frame%256==0||frame+1==causal_capture::count);
    const auto beforeState=checkpoint?causal_capture::stateHash(*impl_->model):0;
    const auto observed=impl_->causal.step();
    const auto afterForce=causal_capture::forceHash();const auto afterState=checkpoint?causal_capture::stateHash(*impl_->model):0;
    if(beforeForce!=afterForce||(checkpoint&&beforeState!=afterState))++causal_capture::mismatch;
    if(frame<causal_capture::count){
      causal_capture::forceProof[frame]={uint64_t(frame),beforeForce,afterForce};
      if(checkpoint)causal_capture::stateProof.push_back({uint64_t(frame),beforeState,afterState});
      const auto board=impl_->boardObservation();causal_capture::driver[frame]=observed.input;
      causal_capture::trace[frame]={x[0],x[1],board[0],board[1],observed.pressure[0],observed.pressure[1],observed.energyAfter,
        observed.freeDissipation,observed.loadDissipation,observed.externalWork,observed.balanceResidual,causal_trace::force[causal_capture::note-21],
        causal_trace::bridge[0],causal_trace::bridge[1],causal_trace::bridge[2]};
      if(!observed.valid)++causal_capture::candidateFaults;
      std::array<double,2> y{{board[0]+observed.pressure[0],board[1]+observed.pressure[1]}};
      if(impl_->config.parameters.stereoWidth!=1){const double mid=.5*(y[0]+y[1]),side=.5*(y[0]-y[1])*impl_->config.parameters.stereoWidth;y={mid+side,mid-side};}
      for(unsigned ch=0;ch<2;++ch){impl_->causalHighpass[ch]=impl_->pole*(impl_->causalHighpass[ch]+y[ch]-impl_->causalPrevious[ch]);impl_->causalPrevious[ch]=y[ch];
        const double value=impl_->causalHighpass[ch]*impl_->gain;if(!std::isfinite(value)||std::abs(value)>std::numeric_limits<float>::max())++causal_capture::candidateFaults;
        causal_capture::candidate[frame][ch]=float(value);
      }
      for(unsigned s=0;s<3;++s)for(unsigned ch=0;ch<2;++ch){const double value=impl_->model->lastStems[s][ch];impl_->stemHighpass[s][ch]=impl_->pole*(impl_->stemHighpass[s][ch]+value-impl_->stemPrevious[s][ch]);impl_->stemPrevious[s][ch]=value;causal_capture::stems[s][frame][ch]=float(impl_->stemHighpass[s][ch]*impl_->gain);}
    }''')
api+=r'''
extern "C" void causal_capture_begin(unsigned frames,int note){causal_capture::begin(frames,note);}
extern "C" bool causal_capture_write(const char* folder){
 return causal_capture::write(folder,"candidate.f32le",causal_capture::candidate)&&causal_capture::write(folder,"primary.f32le",causal_capture::stems[0])&&
 causal_capture::write(folder,"secondary.f32le",causal_capture::stems[1])&&causal_capture::write(folder,"transient.f32le",causal_capture::stems[2])&&
 causal_capture::write(folder,"driver.f64le",causal_capture::driver)&&causal_capture::write(folder,"trace.f64le",causal_capture::trace)&&
 causal_capture::write(folder,"state-proof.u64le",causal_capture::stateProof)&&causal_capture::write(folder,"force-proof.u64le",causal_capture::forceProof);
}
extern "C" uint64_t causal_capture_mismatches(){return causal_capture::mismatch;}
extern "C" uint64_t causal_capture_faults(){return causal_capture::candidateFaults;}
''';(MODEL/'FullInstrument.cpp').write_text(api)
harness=r'''
#include "keyra/FullInstrument.h"
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <string>
#include <vector>
extern "C" void causal_capture_begin(unsigned,int);
extern "C" bool causal_capture_write(const char*);
extern "C" uint64_t causal_capture_mismatches();extern "C" uint64_t causal_capture_faults();
int main(int argc,char**argv){if(argc!=4)return 2;const std::string dir=argv[1];const int note=std::atoi(argv[2]);const double velocity=std::strtod(argv[3],nullptr);constexpr unsigned frames=182400;
 causal_capture_begin(frames,note);keyra::FullInstrumentConfig config;config.sampleRate=48000;config.seed=123456;config.repetitionController=false;config.parameters.humanization=0;config.parameters.mechanicalLevel=0;config.parameters.gainDb=0;config.parameters.stereoWidth=1;
 keyra::FullInstrument piano;if(!piano.prepare(config))return 3;std::vector<float>l(frames),r(frames);
 for(unsigned first=0;first<frames;first+=64){if(first==4800&&!piano.noteOn(note,velocity/127.))return 4;if(!piano.process(l.data()+first,r.data()+first,64))return 5;}
 FILE*f=std::fopen((dir+"/baseline.f32le").c_str(),"wb");if(!f)return 6;for(unsigned i=0;i<frames;++i){const float x[2]={l[i],r[i]};if(!std::isfinite(x[0])||!std::isfinite(x[1])||std::fwrite(x,sizeof(float),2,f)!=2)return 7;}std::fclose(f);
 if(!causal_capture_write(dir.c_str()))return 8;const auto d=piano.diagnostics();const auto mismatch=causal_capture_mismatches(),fault=causal_capture_faults();
 std::printf("{\"frames\":182400,\"sample_rate\":48000,\"midi\":%d,\"velocity\":%.17g,\"note_on_frame\":4800,\"launches\":%llu,\"original_fault_flags\":%u,\"parity_mismatches\":%llu,\"new_observer_faults\":%llu}\n",note,velocity,(unsigned long long)d.launches,d.faultFlags,(unsigned long long)mismatch,(unsigned long long)fault);
 return d.faultFlags||d.launches!=1||d.unsafeLaunches||mismatch||fault?9:0;}
''';(OUT/'producer.cpp').write_text(harness)
flags=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-I'+str(PRIVATE/'include'),'-I'+str(MODEL),'-I'+str(OUT)]
commands=[['g++',*flags,'-c',str(MODEL/'FullInstrument.cpp'),'-o',str(OUT/'producer-api.o')],['g++',*flags,'-c',str(OUT/'producer.cpp'),'-o',str(OUT/'producer-harness.o')],['g++',str(OUT/'producer-api.o'),str(OUT/'producer-harness.o'),'-o',str(OUT/'producer')]]
for command in commands:
 call=subprocess.run(command,text=True,capture_output=True)
 if call.returncode:raise RuntimeError(call.stderr)
sources=[{'path':str(SOURCE/name),'sha256':digest,'role':'immutable_old_demo_provenance'} for name,digest in proof['source_sha256'].items()]
sources += [{'path':str(p),'sha256':sha(p),'role':'actual_compiled_or_instrumented_source'} for p in sorted(PRIVATE.rglob('*')) if p.is_file()]
sources += [{'path':str(p),'sha256':sha(p),'role':'actual_final_observer_or_driver'} for p in [OUT/'CausalRadiation.h',OUT/'producer.cpp',OUT/'make_producer.py']]
freeze={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':{'path':str(protocol),'sha256':sha(protocol)},'binary':{'path':str(OUT/'producer'),'sha256':sha(OUT/'producer')},'source_inputs':sources,'readout_method':'DC-stationary-corrected endpoint; actual stored damped-rotation determinant d0; one fixed readout','math_validation':{'path':str(math),'sha256':sha(math)},'commands':commands,'configuration':{'sample_rate':48000,'frames':182400,'note_on_frame':4800,'pedal_initial':0,'humanization':0,'mechanical_level':0,'repetition_controller':False,'gain_db':0,'stereo_width':1},'observation':'Candidate=actualuncorrectedrawboard+independentcausalcorrection; actualphysicalmodel/emission remains baseline unchanged.','parity_proof':'Observer ownsdoublecopiedstates, readsmodelonlythroughconstfloatp pointers, nofeedback. Everyframecontact88/Schur3forcebitFNVhashbefore/after; every256frames+last fullphysicalq/p/damp,board,hammer/pedal/force/counterhashbefore/after. Allrows emitted; booleansderivefromrowcomparisons andexactcachedoldbaselinepayload.'}
(OUT/'candidate-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n');print('producerfrozen',sha(OUT/'candidate-freeze.json'),'binary',freeze['binary']['sha256'])
