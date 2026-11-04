"""Native live-control trajectories and their connection to rendered audio.

Stdlib Python and a C++17 compiler only; no recordings or waveform fixtures.
Resonance uses an independent closed-form 12 ms trajectory. A second native
engine is forced to that instantaneous gain before each sample, bypassing its
own smoother. State checks alone would miss a disconnected output path, so a
temporary raw-parameter output mutation must fail the SAME audio oracle.
Static parameter renders remain bit-identical to that direct-mix control.

The audio comparison permits float-output rounding, not an acoustic margin.
This bounded native panel is not a universal cancellation-error certificate.
Brightness uses an independent per-partial linear-amplitude trajectory and
forces reference pickup gains through the stable renderer at every sample.
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
#include <map>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <tuple>
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
keyra::Parameters parameters(int model,float resonance=.25f){
  keyra::Parameters p;p.gain=.07f;p.resonance=resonance;p.sustain=1;
  p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));return p;
}
void start(keyra::Engine& e,const keyra::Parameters& p){
  e.setParameters(p);e.reset();for(int n:{48,60,64,67})e.noteOn(n,80/127.f);
}
void warm(keyra::Engine& e,int frames){
  std::array<float,127> l{},r{};for(int at=0;at<frames;){const int n=std::min(127,frames-at);e.process(l.data(),r.data(),n);at+=n;}
}
struct Event{int at;float target;};
std::array<Event,5> events(double sr){return {{{0,1.f},{int(std::lround(.006*sr))+7,0.f},
  {int(std::lround(.019*sr))+13,.4f},{int(std::lround(.041*sr))+29,1.f},{int(std::lround(.08*sr))+1,.25f}}};}
void trajectory(int model,double sr){
  keyra::Engine tested(sr),reference(sr);auto p=parameters(model);start(tested,p);start(reference,p);
  warm(tested,1024);warm(reference,1024);
  // Other smoothed controls remain at their reset values throughout. Only
  // the reference's resonance is prescribed; no engine recurrence supplies it.
  reference.impl->smooth=0;
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  double oracle=p.resonance,initial=oracle,target=oracle,maxState=0,maxError=0,peak=0;
  int since=0;std::size_t next=0;float al,ar,bl,br;
  trap=true;
  for(int i=0;i<total;++i){
    if(next<schedule.size()&&i==schedule[next].at){
      initial=oracle;target=schedule[next].target;since=0;p.resonance=schedule[next++].target;
      tested.setParameters(p);reference.setParameters(p);
    }
    ++since;oracle=target+(initial-target)*std::exp(-double(since)/(.012*sr));
    reference.impl->resonance=oracle;
    // Prescribe both representations so the oracle remains independent even
    // in the raw-target output mutation. Its float conversion is covered by
    // the output-rounding allowance; the state oracle stays double precision.
    reference.impl->parameters.resonance=static_cast<float>(oracle);
    tested.process(&al,&ar,1);reference.process(&bl,&br,1);
    const double error=std::abs(tested.impl->resonance-oracle);maxState=std::max(maxState,error);
    // Forward accumulation allowance for bounded double one-pole arithmetic;
    // independent of the signal level and not an audible error tolerance.
    const double tolerance=32*std::numeric_limits<double>::epsilon()*(i+2);
    require(error<=tolerance,"resonance closed-form state trajectory mismatch");
    require(tested.impl->resonance>=std::min(initial,target)-tolerance
      &&tested.impl->resonance<=std::max(initial,target)+tolerance,"resonance trajectory leaves endpoint bounds");
    require(std::isfinite(al)&&std::isfinite(ar)&&std::isfinite(bl)&&std::isfinite(br),"nonfinite oracle waveform");
    maxError=std::max({maxError,std::abs(double(al)-bl),std::abs(double(ar)-br)});
    peak=std::max({peak,std::abs(double(al)),std::abs(double(ar)),std::abs(double(bl)),std::abs(double(br))});
  }
  trap=false;
  require(peak>0,"empty oracle waveform");
  require(maxError<=8*std::numeric_limits<float>::epsilon()*peak,"resonance audio oracle mismatch");
  std::cout<<"trajectory model="<<model<<" rate="<<sr<<" state_error="<<maxState
           <<" audio_relative_peak_error="<<maxError/peak<<'\n';
}
std::vector<float> partitioned(int model,double sr,bool varied){
  keyra::Engine e(sr);auto p=parameters(model);start(e,p);warm(e,1024);
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  std::vector<float> wave(static_cast<std::size_t>(total)*2);std::array<float,511> l{},r{};
  constexpr int sizes[]{1,7,31,32,127,511};std::size_t next=0;int block=0;
  trap=true;
  for(int at=0;at<total;){
    if(next<schedule.size()&&at==schedule[next].at){p.resonance=schedule[next++].target;e.setParameters(p);}
    const int end=next<schedule.size()?schedule[next].at:total;
    const int n=std::min({total-at,end-at,varied?sizes[block++%6]:1});
    e.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){wave[2*(at+i)]=l[i];wave[2*(at+i)+1]=r[i];}at+=n;
  }
  trap=false;return wave;
}
void lifecycle(int model,double sr){
  keyra::Engine e(sr);auto p=parameters(model,0.f);p.sustain=0;
  // This is the sleeping-state contract, not a pedal-edge sound event.
  // The trajectory scenes separately reset after setting sustain down.
  e.setParameters(p);
  require(e.impl->sleeping&&e.impl->resonance==0,"silent setParameters did not snap resonance");
  std::array<float,127> l{},r{};trap=true;e.process(l.data(),r.data(),127);
  require(e.impl->resonance==0,"idle process did not preserve target");
  p.resonance=1;e.setParameters(p);require(e.impl->resonance==1,"silent endpoint one did not snap");
  e.noteOn(60,.7f);e.process(l.data(),r.data(),127);p.resonance=0;e.setParameters(p);
  require(e.impl->resonance==1,"live edit snapped instead of gliding");
  e.process(l.data(),r.data(),17);require(e.impl->resonance>0&&e.impl->resonance<1,"live trajectory did not move");
  e.reset();require(e.impl->resonance==0&&e.impl->sleeping,"reset did not snap current target");
  e.impl->resonance=.75; // Exercise idle synchronization, independently of set/reset.
  e.process(l.data(),r.data(),127);require(e.impl->resonance==0,"sleeping process failed to synchronize resonance");
  for(int i=0;i<127;++i)require(l[i]==0&&r[i]==0,"idle control synchronization emitted audio");
  trap=false;
}
using TintKey=std::tuple<std::uint64_t,double,double>;
TintKey tintKey(const keyra::Voice& v,const keyra::Partial& p){return {v.serial,p.frequency,p.hz[0]};}
struct TintOracle{double current,initial,target,scale;int since=0;};
void brightnessTrajectory(int model,double sr){
  keyra::Engine tested(sr),reference(sr);auto p=parameters(model);start(tested,p);start(reference,p);
  warm(tested,1024);warm(reference,1024);reference.impl->smooth=0;
  std::map<TintKey,TintOracle> states;
  for(const auto& v:tested.impl->voices)if(v.active)for(int k=0;k<v.count;++k){const auto& t=v.partials[k];
    require(states.emplace(tintKey(v,t),TintOracle{t.tint,t.tint,t.tint,t.tintScale,0}).second,"duplicate tint oracle identity");}
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  float applied=p.brightness;std::size_t next=0,checked=0;double maxState=0,maxError=0,peak=0;
  float al,ar,bl,br;trap=true;
  for(int i=0;i<total;++i){
    if(next<schedule.size()&&i==schedule[next].at){p.brightness=schedule[next++].target;tested.setParameters(p);reference.setParameters(p);}
    // The established control scope accepts targets at the next chunk;
    // interpolation AFTER that acceptance must advance at every sample.
    if(tested.impl->frame%keyra::chunk==0&&applied!=p.brightness){
      applied=p.brightness;
      for(auto& item:states){auto& s=item.second;s.initial=s.current;
        s.target=static_cast<float>(std::pow(2.,(static_cast<double>(applied)-.5)*s.scale));s.since=0;}
    }
    for(auto& item:states){auto& s=item.second;++s.since;
      s.current=s.target+(s.initial-s.target)*std::exp(-double(s.since)/(.012*sr));
      // Existing declared endpoint snap, not a fitted acoustic tolerance.
      if(std::abs(s.target-s.current)<1e-9*s.target)s.current=s.target;
    }
    // Force the reference's instantaneous physical pickup gains. Disable its
    // boundary target update and its gain smoother; neither computes the oracle.
    reference.impl->previousBrightness=reference.impl->parameters.brightness;
    for(auto& v:reference.impl->voices)if(v.active)for(int k=0;k<v.count;++k){auto& t=v.partials[k];
      const auto it=states.find(tintKey(v,t));require(it!=states.end(),"reference tint identity changed");
      t.tintState=it->second.current;t.tint=static_cast<float>(t.tintState);t.targetTint=t.tint;
      // Make the reference use its stable rendering path at the oracle gain.
      t.tintState=t.targetTint;reference.impl->updateWeights(t);
    }
    tested.process(&al,&ar,1);reference.process(&bl,&br,1);
    for(const auto& v:tested.impl->voices)if(v.active)for(int k=0;k<v.count;++k){const auto& t=v.partials[k];
      const auto it=states.find(tintKey(v,t));require(it!=states.end(),"tested tint identity changed");const auto& s=it->second;
      const double error=std::abs(t.tintState-s.current);maxState=std::max(maxState,error);
      const double tolerance=32*std::numeric_limits<double>::epsilon()*(i+2)*std::max({1.,s.initial,s.target});
      require(error<=tolerance,"brightness closed-form state trajectory mismatch");
      require(t.tintState>=std::min(s.initial,s.target)-tolerance&&t.tintState<=std::max(s.initial,s.target)+tolerance,
              "brightness gain leaves endpoint bounds");++checked;
    }
    require(std::isfinite(al)&&std::isfinite(ar)&&std::isfinite(bl)&&std::isfinite(br),"nonfinite brightness audio");
    maxError=std::max({maxError,std::abs(double(al)-bl),std::abs(double(ar)-br)});
    peak=std::max({peak,std::abs(double(al)),std::abs(double(ar)),std::abs(double(bl)),std::abs(double(br))});
  }
  trap=false;require(checked>0&&peak>0,"empty brightness oracle");
  require(maxError<=8*std::numeric_limits<float>::epsilon()*peak,"brightness audio oracle mismatch");
  std::cout<<"brightness model="<<model<<" rate="<<sr<<" states="<<checked<<" state_error="<<maxState
           <<" audio_relative_peak_error="<<maxError/peak<<'\n';
}
std::vector<float> brightnessPartitioned(int model,double sr,bool varied){
  keyra::Engine e(sr);auto p=parameters(model);start(e,p);warm(e,1024);
  const auto schedule=events(sr);const int total=int(std::lround(.12*sr))+128;
  std::vector<float> wave(static_cast<std::size_t>(total)*2);std::array<float,511> l{},r{};
  constexpr int sizes[]{1,7,31,32,127,511};std::size_t next=0;int block=0;trap=true;
  for(int at=0;at<total;){
    if(next<schedule.size()&&at==schedule[next].at){p.brightness=schedule[next++].target;e.setParameters(p);}
    const int end=next<schedule.size()?schedule[next].at:total;
    const int n=std::min({total-at,end-at,varied?sizes[block++%6]:1});e.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){wave[2*(at+i)]=l[i];wave[2*(at+i)+1]=r[i];}at+=n;
  }
  trap=false;return wave;
}
void brightnessLifecycle(int model,double sr){
  keyra::Engine e(sr);auto p=parameters(model);p.brightness=0;start(e,p);warm(e,64);
  p.brightness=1;e.setParameters(p);
  // The brightness law spans .25..4. This duration follows the declared
  // relative endpoint snap for the largest possible initial/target ratio,
  // plus two chunks for target acceptance; no acoustic time limit is fitted.
  warm(e,int(std::ceil(.012*sr*std::log(16./1e-9)))+2*keyra::chunk);
  for(const auto& v:e.impl->voices)if(v.active)for(int k=0;k<v.count;++k){const auto& t=v.partials[k];
    require(t.tintState==t.targetTint&&t.tint==t.targetTint,"brightness never reaches its stable path");}
  p.brightness=0;e.setParameters(p);warm(e,17);
  p.brightness=1;e.setParameters(p);
  e.reset();require(e.impl->sleeping,"brightness reset did not sleep");
  // Reuses the same voice/partial storage at the new target. A stale gain
  // from the interrupted glide must not enter the next strike.
  trap=true;e.noteOn(60,.7f);
  for(const auto& v:e.impl->voices)if(v.active)for(int k=0;k<v.count;++k){const auto& t=v.partials[k];
    const float expected=static_cast<float>(std::pow(2.,.5*t.tintScale));
    require(t.tint==expected&&t.targetTint==expected&&t.tintState==expected,"reused voice retained stale brightness");}
  e.reset();p.brightness=.5f;e.setParameters(p);e.noteOn(60,.7f);
  for(const auto& v:e.impl->voices)if(v.active)for(int k=0;k<v.count;++k){const auto& t=v.partials[k];
    require(t.tint==1&&t.targetTint==1&&t.tintState==1,"silent brightness default is not neutral");}
  trap=false;
}
void staticAudio(){
  for(double sr:{44100.,48000.,192000.})for(int model=0;model<keyra::pianoCount;++model)for(float v:{0.f,.25f,1.f})for(float brightness:{0.f,.5f,1.f}){
    keyra::Engine e(sr);auto p=parameters(model,v);p.brightness=brightness;start(e,p);
    std::array<float,127> l{},r{};std::uint64_t h=14695981039346656037ull;
    trap=true;
    for(int block=0;block<64;++block){if(block==32)for(int n:{48,60,64,67})e.noteOff(n);
      e.process(l.data(),r.data(),127);for(int i=0;i<127;++i){h=hash(h,l[i]);h=hash(h,r[i]);}}
    trap=false;std::cout<<model<<' '<<sr<<' '<<v<<' '<<brightness<<' '<<h<<'\n';
  }
}
int main(int argc,char**argv){try{
  std::cout<<std::setprecision(17);
  if(argc>1&&std::string(argv[1])=="static"){staticAudio();require(allocations==0,"static callbacks allocate");return 0;}
  if(argc>1&&std::string(argv[1])=="brightness"){
    for(double sr:{44100.,48000.,192000.})for(int model=0;model<keyra::pianoCount;++model){
      brightnessTrajectory(model,sr);brightnessLifecycle(model,sr);
      require(brightnessPartitioned(model,sr,false)==brightnessPartitioned(model,sr,true),"brightness automation depends on block partition");
    }
    require(allocations==0,"brightness callbacks allocate");std::cout<<"brightness_models_rates=18 live_allocations="<<allocations<<'\n';return 0;
  }
  for(double sr:{44100.,48000.,192000.})for(int model=0;model<keyra::pianoCount;++model){
    trajectory(model,sr);lifecycle(model,sr);
    const auto a=partitioned(model,sr,false),b=partitioned(model,sr,true);
    require(a==b,"resonance automation depends on block partition");
  }
  require(allocations==0,"live event/render/reset APIs allocate");
  std::cout<<"models_rates=18 static_endpoints=162 block_partitions=18 live_allocations="<<allocations<<'\n';return 0;
}catch(const std::exception& e){trap=false;std::cerr<<e.what()<<'\n';return 1;}}
'''


class LiveControlSmoothingTests(unittest.TestCase):
    def test_live_control_trajectories_lifecycle_and_audio_integration(self):
        source = (DSP / 'KeyraEngine.cpp').read_text()
        # The mutation intentionally leaves the new state and lifecycle code
        # intact. Only the actual audible mix bypasses it.
        token = '*resonance*.35'
        self.assertEqual(source.count(token), 2)
        direct = source.replace(token, '*parameters.resonance*.35')
        tint_token = 'return splat(static_cast<float>(state)*audible);'
        self.assertEqual(source.count(tint_token), 1)
        direct_tint = source.replace(tint_token, 'return splat(static_cast<float>(target)*audible);')
        with tempfile.TemporaryDirectory(prefix='keyra-live-controls-') as directory:
            root = Path(directory)
            probe = root / 'probe.cpp'
            probe.write_text(PROBE)
            binaries = []
            for name, text in [('candidate', source), ('direct-mix', direct), ('direct-tint', direct_tint)]:
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
            brightness = subprocess.run([str(binaries[0]), 'brightness'], capture_output=True, text=True)
            self.assertEqual(brightness.returncode, 0, brightness.stdout + brightness.stderr)
            print(brightness.stdout.strip())
            mutation = subprocess.run([str(binaries[1])], capture_output=True, text=True)
            self.assertNotEqual(mutation.returncode, 0, 'raw-target mix escaped the audio oracle')
            self.assertIn('resonance audio oracle mismatch', mutation.stderr)
            tint_mutation = subprocess.run([str(binaries[2]), 'brightness'], capture_output=True, text=True)
            self.assertNotEqual(tint_mutation.returncode, 0, 'raw tint target escaped the audio oracle')
            self.assertIn('brightness audio oracle mismatch', tint_mutation.stderr)
            audio = [subprocess.check_output([str(b), 'static'], text=True) for b in binaries]
            self.assertEqual(len(audio[0].splitlines()), 135)
            self.assertEqual(audio[0], audio[1], 'static Resonance endpoint audio changed')
            self.assertEqual(audio[0], audio[2], 'static Brightness endpoint audio changed')
            print('both raw-target mutations rejected; static endpoint waveform hashes identical=135')


if __name__ == '__main__':
    unittest.main()
