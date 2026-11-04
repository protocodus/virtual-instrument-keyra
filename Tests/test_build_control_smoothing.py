"""Native build-control smoothing, with independent state and audio oracles.

Only stdlib Python and a C++17 compiler are required. Tube calibration follows
a closed-form 12 ms one-pole; noise coherence follows a finite 12 ms angle
ramp. The reference engine is forced to each independently calculated mixing
gain before every sample, bypassing its own smoother. Audible-path mutations
must fail that same oracle even though their smoother states remain correct.
Numerical allowances cover bounded floating-point accumulation/output rounding,
not acoustic acceptability. Static controls compare exact waveform hashes.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DSP = ROOT / 'Source/DSP'

PROBE = r'''
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>
#define private public
#include "KeyraEngine.h"
#undef private
#include "KeyraEngine.cpp"
namespace {bool trap=false;std::size_t allocations=0;}
void* operator new(std::size_t n){if(trap)++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
void operator delete[](void* p,std::size_t) noexcept{std::free(p);}
void require(bool ok,const char* message){if(!ok){trap=false;throw std::runtime_error(message);}}
std::uint64_t hash(std::uint64_t h,float x){
  require(std::isfinite(x),"nonfinite audio");std::uint32_t b;std::memcpy(&b,&x,4);
  for(int k=0;k<4;++k){h^=(b>>(8*k))&255u;h*=1099511628211ull;}return h;
}
keyra::Parameters parameters(int model,bool noise){
  keyra::Parameters p;p.gain=.07f;p.mic=noise?0:1;p.mechanics=.175f;
  p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));return p;
}
void start(keyra::Engine& e,const keyra::Parameters& p){
  e.setParameters(p);e.reset();for(int n:{21,36,60,84,96})e.noteOn(n,1.f);
}
void warm(keyra::Engine& e,int frames){
  std::array<float,127> l{},r{};for(int at=0;at<frames;){const int n=std::min(127,frames-at);e.process(l.data(),r.data(),n);at+=n;}
}
struct Event{int at,choice;};
// A choice is an offset from the base piano, or both of its neighbours at once.
constexpr int mixedChoice=keyra::pianoCount;
std::array<Event,6> events(double sr){return {{{0,1},{3,1},{int(std::lround(.006*sr))+7,3},
  {int(std::lround(.019*sr))+13,mixedChoice},{int(std::lround(.041*sr))+29,keyra::pianoCount-1},{int(std::lround(.08*sr))+1,0}}};}
keyra::Mix selection(int base,int choice){
  keyra::Mix w{};if(choice==mixedChoice){w[(base+1)%keyra::pianoCount]=.5f;w[(base+keyra::pianoCount-1)%keyra::pianoCount]=.5f;}
  else w[(base+choice)%keyra::pianoCount]=1;return w;
}
void change(keyra::Parameters& p,int base,int choice,bool noise){
  if(noise)p.build.soundboard=selection(base,choice);else p.build.hammers=selection(base,choice);
}
double tubeTarget(const keyra::Parameters& p){
  double logarithm=0;for(int k=0;k<keyra::pianoCount;++k)logarithm+=p.build.hammers[k]*std::log(keyra::models[k].tubeScale);
  // Pure endpoint folding retains the model's original value exactly.
  for(int k=0;k<keyra::pianoCount;++k)if(p.build.hammers[k]==1)return keyra::models[k].tubeScale;
  return std::exp(logarithm);
}
double noiseTarget(const keyra::Parameters& p,int b){
  double coherence=0;for(int k=0;k<keyra::pianoCount;++k)coherence+=p.build.soundboard[k]*keyra::models[k].noiseBands[b].coherence;
  return .5*std::acos(std::max(0.f,std::min(1.f,static_cast<float>(coherence))));
}
void tubeTrajectory(int model,double sr){
  keyra::Engine tested(sr),reference(sr);auto p=parameters(model,false);start(tested,p);start(reference,p);warm(tested,269);warm(reference,269);
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  double oracle=tubeTarget(p),initial=oracle,target=oracle,maxState=0,maxError=0,peak=0;
  int since=0;std::size_t next=0;float al,ar,bl,br;trap=true;
  for(int i=0;i<total;++i){
    if(next<schedule.size()&&i==schedule[next].at){change(p,model,schedule[next++].choice,false);
      // Repeating an unchanged target must not restart an exponential path.
      const double requested=tubeTarget(p);if(requested!=target){initial=oracle;target=requested;since=0;}
      tested.setParameters(p);reference.setParameters(p);}
    ++since;oracle=target+(initial-target)*std::exp(-double(since)/(.012*sr));
    // Force both representations. Other smoothers retain their own native
    // trajectories.
    reference.impl->tubeScale=reference.impl->tubeScaleTarget=oracle;
    tested.process(&al,&ar,1);reference.process(&bl,&br,1);
    const double error=std::abs(tested.impl->tubeScale-oracle);maxState=std::max(maxState,error);
    const double tolerance=32*std::numeric_limits<double>::epsilon()*(i+2)*std::max({1.,initial,target});
    require(error<=tolerance,"tube closed-form trajectory mismatch");
    require(tested.impl->tubeScale>=std::min(initial,target)-tolerance&&tested.impl->tubeScale<=std::max(initial,target)+tolerance,"tube gain left endpoint bounds");
    maxError=std::max({maxError,std::abs(double(al)-bl),std::abs(double(ar)-br)});
    peak=std::max({peak,std::abs(double(al)),std::abs(double(ar)),std::abs(double(bl)),std::abs(double(br))});
    require(std::isfinite(al)&&std::isfinite(ar)&&std::isfinite(bl)&&std::isfinite(br),"nonfinite tube waveform");
  }
  trap=false;require(peak>0,"empty tube oracle");
  require(maxError<=8*std::numeric_limits<float>::epsilon()*peak,"tube audio oracle mismatch");
  std::cout<<"tube model="<<model<<" rate="<<sr<<" state_error="<<maxState<<" relative_audio="<<maxError/peak<<'\n';
}
struct Angle{double value=0,initial=0,target=0;int elapsed=0;bool moving=false;};
void noiseTrajectory(int model,double sr){
  keyra::Engine tested(sr),reference(sr);auto p=parameters(model,true);start(tested,p);start(reference,p);warm(tested,269);warm(reference,269);
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  const int duration=std::max(1,int(std::lround(.012*sr)));std::array<Angle,keyra::noiseBands> angles{};
  for(int b=0;b<keyra::noiseBands;++b)angles[b].value=angles[b].initial=angles[b].target=noiseTarget(p,b);
  std::size_t next=0,checks=0,movingChecks=0;double maxState=0,maxNorm=0,maxError=0,peak=0;float al,ar,bl,br;trap=true;
  for(int i=0;i<total;++i){
    if(next<schedule.size()&&i==schedule[next].at){change(p,model,schedule[next++].choice,true);
      for(int b=0;b<keyra::noiseBands;++b){auto& a=angles[b];const double target=noiseTarget(p,b);
        const bool active=tested.impl->hissing&&tested.impl->noise[b].live;
        if(!active){a.value=a.initial=a.target=target;a.moving=false;a.elapsed=0;}
        else if(target!=a.target){a.initial=a.value;a.target=target;a.elapsed=0;a.moving=true;}}
      tested.setParameters(p);reference.setParameters(p);}
    for(auto& a:angles)if(a.moving){++a.elapsed;a.value=a.initial+(a.target-a.initial)*std::min(1.,double(a.elapsed)/duration);
      if(a.elapsed>=duration){a.value=a.target;a.moving=false;}}
    tested.process(&al,&ar,1);
    for(int b=0;b<keyra::noiseBands;++b){auto& a=angles[b];const auto& band=tested.impl->noise[b];
      // A newly inactive band is inaudible and must snap, never leave a
      // half-glide to be replayed by a later burst. Its liveness depends on
      // unchanged burst amplitudes, not on the tested mixing trajectory.
      if(!band.live){a.value=a.initial=a.target;a.elapsed=0;a.moving=false;}
      const double c=std::cos(a.value),s=std::sin(a.value);
      const double error=std::max(std::abs(band.c-c),std::abs(band.s-s));maxState=std::max(maxState,error);
      const double tolerance=32*std::numeric_limits<double>::epsilon()*(i+2);
      require(error<=tolerance,"noise independent angle trajectory mismatch");
      const double norm=std::abs(band.c*band.c+band.s*band.s-1);maxNorm=std::max(maxNorm,norm);
      require(norm<=tolerance,"noise mixing loses unit power");
      require(std::atan2(band.s,band.c)>=std::min(a.initial,a.target)-tolerance&&std::atan2(band.s,band.c)<=std::max(a.initial,a.target)+tolerance,"noise angle left endpoint bounds");
      if(!a.moving)require(band.mixFrames==0&&band.c==band.targetC&&band.s==band.targetS,"noise endpoint is not exact");
      auto& ref=reference.impl->noise[b];ref.c=ref.targetC=c;ref.s=ref.targetS=s;ref.mixFrames=0;ref.mixStepC=1;ref.mixStepS=0;
      ++checks;movingChecks+=a.moving;
    }
    reference.process(&bl,&br,1);
    maxError=std::max({maxError,std::abs(double(al)-bl),std::abs(double(ar)-br)});
    peak=std::max({peak,std::abs(double(al)),std::abs(double(ar)),std::abs(double(bl)),std::abs(double(br))});
    require(std::isfinite(al)&&std::isfinite(ar)&&std::isfinite(bl)&&std::isfinite(br),"nonfinite noise waveform");
  }
  trap=false;require(peak>0&&movingChecks>0,"empty active noise oracle");
  require(maxError<=8*std::numeric_limits<float>::epsilon()*peak,"noise audio oracle mismatch");
  std::cout<<"noise model="<<model<<" rate="<<sr<<" checks="<<checks<<" moving="<<movingChecks<<" state_error="<<maxState<<" norm_error="<<maxNorm<<" relative_audio="<<maxError/peak<<'\n';
}
void onlyNoise(keyra::Engine& e){
  // A projection of already running native bursts, not synthetic amplitudes.
  // It isolates noise partitioning from the older body's pickup glide.
  for(auto& v:e.impl->voices)v.active=false;e.impl->silenceBody();e.impl->silenceStrings();
}
std::vector<float> partitioned(int model,double sr,bool noise,bool varied){
  keyra::Engine e(sr);auto p=parameters(model,noise);if(noise)p.resonance=0;start(e,p);warm(e,269);if(noise)onlyNoise(e);
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;std::size_t next=0;int block=0;
  std::vector<float> wave(static_cast<std::size_t>(total)*2);std::array<float,511> l{},r{};constexpr int sizes[]{1,7,31,32,127,511};trap=true;
  for(int at=0;at<total;){
    if(next<schedule.size()&&at==schedule[next].at){change(p,model,schedule[next++].choice,noise);e.setParameters(p);}
    const int end=next<schedule.size()?schedule[next].at:total;
    const int n=std::min({total-at,end-at,varied?sizes[block++%6]:1});e.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){wave[2*(at+i)]=l[i];wave[2*(at+i)+1]=r[i];}at+=n;
  }
  trap=false;return wave;
}
void checkSnapped(const keyra::Engine& e){
  require(e.impl->tubeScale==e.impl->tubeScaleTarget,"tube reset/idle is stale");
  for(const auto& b:e.impl->noise)require(b.mixFrames==0&&b.c==b.targetC&&b.s==b.targetS,"noise reset/idle is stale");
}
void lifecycle(int model,double sr){
  keyra::Engine e(sr);auto p=parameters(model,false);e.setParameters(p);checkSnapped(e);
  change(p,model,1,false);change(p,model,3,true);e.setParameters(p);checkSnapped(e);e.reset();checkSnapped(e);
  start(e,p);warm(e,269);change(p,model,5,false);change(p,model,6,true);
  const auto seed=e.impl->seed;const auto filters=e.impl->noise;trap=true;e.setParameters(p);
  require(e.impl->seed==seed,"build update consumed noise RNG");
  for(int b=0;b<keyra::noiseBands;++b)for(int j=0;j<keyra::noiseSections;++j)for(int k=0;k<2;++k){const auto& filter=filters[b];const auto& actual=e.impl->noise[b];
    require(actual.x1[j][k]==filter.x1[j][k]&&actual.x2[j][k]==filter.x2[j][k]&&actual.y1[j][k]==filter.y1[j][k]&&actual.y2[j][k]==filter.y2[j][k],"build update reset noise filter history");}
  std::array<float,127> l{},r{};e.process(l.data(),r.data(),17);e.reset();checkSnapped(e);
  // Exercise the idle-process sync independently from reset/setParameters.
  e.impl->tubeScale=1;for(auto& b:e.impl->noise){b.c=0;b.s=1;b.mixFrames=7;}
  e.process(l.data(),r.data(),127);checkSnapped(e);for(int i=0;i<127;++i)require(l[i]==0&&r[i]==0,"idle synchronization emitted sound");
  e.noteOn(60,1);e.process(l.data(),r.data(),127);change(p,model,2,false);change(p,model,2,true);e.setParameters(p);e.controlChange(120,0);checkSnapped(e);
  // A band whose last burst ends must settle even while other sound lives.
  e.noteOn(60,1);e.process(l.data(),r.data(),127);change(p,model,4,true);e.setParameters(p);
  for(auto& burst:e.impl->bursts)burst.active=false;e.impl->advanceNoise();
  for(const auto& b:e.impl->noise)if(!b.live)require(b.mixFrames==0&&b.c==b.targetC&&b.s==b.targetS,"inactive band retained glide");
  e.impl->advanceNoise();for(const auto& b:e.impl->noise)require(!b.live&&b.mixFrames==0&&b.c==b.targetC&&b.s==b.targetS,"ended noise did not settle");
  // Changing hammers with Mic0 still advances the gain for a later fade-in.
  e.reset();p.mic=0;e.setParameters(p);e.noteOn(60,1);e.process(l.data(),r.data(),127);
  const double old=e.impl->tubeScale;change(p,model,1,false);e.setParameters(p);e.process(l.data(),r.data(),17);
  if(old!=e.impl->tubeScaleTarget)require(e.impl->tubeScale!=old&&e.impl->tubeScale!=e.impl->tubeScaleTarget,"inaudible tube gain did not advance");
  p.mic=1;e.setParameters(p);e.process(l.data(),r.data(),127);for(int i=0;i<127;++i)require(std::isfinite(l[i])&&std::isfinite(r[i]),"Mic activation nonfinite");
  trap=false;
}
void staticAudio(){
  for(double sr:{44100.,48000.,192000.})for(int model=0;model<keyra::pianoCount;++model)for(float mic:{0.f,.35f,1.f})for(bool mixed:{false,true}){
    keyra::Engine e(sr);auto p=parameters(model,false);p.mic=mic;if(mixed)p.build=keyra::buildToward(static_cast<keyra::Piano>(model),static_cast<keyra::Piano>((model+1)%keyra::pianoCount),.5,.5,.5,.5,0,0,0);start(e,p);
    std::array<float,127> l{},r{};std::uint64_t h=14695981039346656037ull;trap=true;
    for(int block=0;block<64;++block){if(block==32)for(int n:{21,36,60,84,96})e.noteOff(n);
      e.process(l.data(),r.data(),127);for(int i=0;i<127;++i){h=hash(h,l[i]);h=hash(h,r[i]);}}
    trap=false;std::cout<<model<<' '<<sr<<' '<<mic<<' '<<mixed<<' '<<h<<'\n';
  }
}
int main(int argc,char**argv){try{
  std::cout<<std::setprecision(17);const std::string mode=argc>1?argv[1]:"all";
  if(mode=="static"){staticAudio();require(allocations==0,"static callbacks allocate");return 0;}
  for(double sr:{44100.,48000.,192000.})for(int model=0;model<keyra::pianoCount;++model){
    if(mode=="all"||mode=="tube")tubeTrajectory(model,sr);
    if(mode=="all"||mode=="noise")noiseTrajectory(model,sr);
    if(mode=="all"){lifecycle(model,sr);for(bool noise:{false,true})require(partitioned(model,sr,noise,false)==partitioned(model,sr,noise,true),"build smoother depends on block partition");}
  }
  require(allocations==0,"live callbacks allocate");std::cout<<"live_allocations="<<allocations<<" instance_bytes="<<sizeof(keyra::Engine::Impl)<<" noise_band_bytes="<<sizeof(keyra::NoiseBand)<<'\n';return 0;
}catch(const std::exception& e){trap=false;std::cerr<<e.what()<<'\n';return 1;}}
'''


class BuildControlSmoothingTests(unittest.TestCase):
    def test_build_trajectories_lifecycle_and_audio(self):
        source = (DSP / 'KeyraEngine.cpp').read_text()
        tube_token = 'const double heard=tubeScale*tubeHears'
        noise_token = 'const double mid=band.c*y[0],side=band.s*y[1];'
        self.assertEqual(source.count(tube_token), 1)
        self.assertEqual(source.count(noise_token), 1)
        mutations = [
            ('candidate', source),
            ('direct-tube', source.replace(tube_token, 'const double heard=tubeScaleTarget*tubeHears')),
            ('direct-noise', source.replace(noise_token, 'const double mid=band.targetC*y[0],side=band.targetS*y[1];')),
        ]
        with tempfile.TemporaryDirectory(prefix='keyra-build-controls-') as directory:
            root = Path(directory)
            probe = root / 'probe.cpp'
            probe.write_text(PROBE)
            binaries = []
            for name, text in mutations:
                include = root / name
                include.mkdir()
                (include / 'KeyraEngine.cpp').write_text(text)
                binary = root / (name + '-probe')
                subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-ffp-contract=off',
                                '-I', str(include), '-I', str(DSP), str(probe), '-o', str(binary)],
                               check=True, capture_output=True, text=True)
                binaries.append(binary)
            candidate = subprocess.run([str(binaries[0])], capture_output=True, text=True)
            self.assertEqual(candidate.returncode, 0, candidate.stdout + candidate.stderr)
            print(candidate.stdout.strip())
            for binary, mode in zip(binaries[1:], ['tube', 'noise']):
                mutation = subprocess.run([str(binary), mode], capture_output=True, text=True)
                self.assertNotEqual(mutation.returncode, 0, mode + ' raw target escaped the audio oracle')
                self.assertIn(mode + ' audio oracle mismatch', mutation.stderr)
            audio = [subprocess.check_output([str(binary), 'static'], text=True) for binary in binaries]
            self.assertEqual(len(audio[0].splitlines()), 90)
            self.assertEqual(audio[0], audio[1], 'static tube output changed')
            self.assertEqual(audio[0], audio[2], 'static noise output changed')
            print('both audible-path mutations rejected; static waveform hashes identical=90')


if __name__ == '__main__':
    unittest.main()
