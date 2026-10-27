// Private-model profile tests; select exactly one prepared header per executable.
// Public FullInstrument/repetition/Reason integration is verified separately.
#ifndef KEYRA_PROFILE_MODEL_HEADER
#error Define KEYRA_PROFILE_MODEL_HEADER to the prepared model being tested
#endif
#include KEYRA_PROFILE_MODEL_HEADER
#include <cstdio>
#include <cstdlib>
#include <new>

#ifndef KEYRA_PROFILE_EXPECT_ANCHORS
#define KEYRA_PROFILE_EXPECT_ANCHORS 17
#endif
#ifndef KEYRA_PROFILE_EXPECT_STRING_MODES
#define KEYRA_PROFILE_EXPECT_STRING_MODES 17849
#endif
namespace {
bool track=false;unsigned allocations=0;
void* allocate(size_t size){if(track)++allocations;if(void* p=std::malloc(size?size:1))return p;std::abort();}
void check(bool value,const char* reason){if(!value){std::fprintf(stderr,"FAIL full profile: %s\n",reason);std::exit(1);}}
void zero(const grand::Piano& p){
  for(const auto& st:p.strings){for(float v:st.m.q)check(v==0,"reset q");for(float v:st.m.p)check(v==0,"reset p");}
  for(const auto& z:p.board)check(z.q==0&&z.p==0&&z.force==0,"reset board");
  check(!p.faultFlags&&!p.forceSolves&&!p.bridgeFaults&&!p.contactFaults,"reset diagnostics");
}
}
void* operator new(size_t size){return allocate(size);}
void* operator new[](size_t size){return allocate(size);}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete[](void* p)noexcept{std::free(p);}
void operator delete(void* p,size_t)noexcept{std::free(p);}
void operator delete[](void* p,size_t)noexcept{std::free(p);}
int main(){
  check(piano_calibration::anchors.size()==KEYRA_PROFILE_EXPECT_ANCHORS,"anchor inventory");
  for(int rate:{44100,48000,88200,96000}){
    grand::Options options;options.sampleRate=rate;grand::Piano piano(options);
    check(piano.strings.size()==230&&piano.modeCount()==KEYRA_PROFILE_EXPECT_STRING_MODES&&piano.board.size()==475,"complete topology");
    for(int note=21;note<=108;++note){
      grand::Cal cal(note);check(cal.lo>=0&&cal.hi>cal.lo&&cal.hi<int(piano_calibration::anchors.size()),"anchor bracketing");
      check(std::isfinite(cal.t),"finite anchor interpolation");
      const auto& key=piano.keys[note-21];check(key.f0>0&&key.B>0&&key.K>0&&std::isfinite(key.contactCompliance),"physical key fields");
    }
    if(KEYRA_PROFILE_EXPECT_ANCHORS==17){
      check(piano_calibration::anchors.front().note==21&&piano_calibration::anchors.back().note==108,"measured extremes retained");
      for(const auto& anchor:piano_calibration::anchors){
        const auto& key=piano.keys[anchor.note-21];
        check(std::abs(key.f0-anchor.f1)<=1e-12*anchor.f1,"anchor fundamental or cents bound mismatch");
        check(std::abs(key.B-anchor.B)<=1e-12*anchor.B,"anchor stiffness extrapolated inside support");
        check(std::abs(key.velocityExponent-anchor.velocityExponent)<1e-14,"anchor velocity response");
      }
    }
    zero(piano);
    auto* pointer=piano.unisonPorts.front().velocityState[0];
    piano.noteOn(21,40);piano.noteOn(60,93);piano.noteOn(108,93);
    track=true;
    double pressure=0;
    for(unsigned frame=0;frame<1024;++frame){auto value=piano.step(frame);check(std::isfinite(value[0])&&std::isfinite(value[1]),"finite model output");pressure+=value[0]*value[0]+value[1]*value[1];}
    check(!piano.faultFlags&&!piano.bridgeFaults&&!piano.contactFaults,"normal excitation raised a solver fault");
    piano.resetState();track=false;
    check(pressure>0,"profile excitation silent");check(allocations==0,"model render/reset allocated");
    check(pointer==piano.unisonPorts.front().velocityState[0],"reset invalidated unison pointers");zero(piano);
  }
  std::puts("Full profile topology, anchor, four-rate finite excitation and allocation-free reset checks passed");
  return 0;
}
