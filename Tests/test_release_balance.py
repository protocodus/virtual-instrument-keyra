"""Native release-balance policy, source routing and diagnostic-bypass contracts.

Uses only the standard library and a C++17 compiler. The exact helper inequality
is a product policy. Audio tests assert causal attenuation and unchanged paths;
they do not choose an acoustic loudness tolerance or infer a physical stem.
"""
from pathlib import Path
import shutil, subprocess, tempfile, unittest
ROOT = Path(__file__).resolve().parents[1]
NATIVE = r"""#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <new>
#include <sstream>
#include <string>
#include <vector>
static bool tracking=false;static std::uint64_t allocations=0;
void* operator new(std::size_t n){if(tracking)++allocations;if(void*p=std::malloc(n))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void*p)noexcept{std::free(p);}void operator delete[](void*p)noexcept{std::free(p);}
#define private public
#include "DSP/KeyraEngine.h"
#include "DSP/OutputStage.h"
#undef private
#ifdef RELEASE_BASELINE
namespace release_audit {inline bool enabled=true,suppress=false;inline int eligible=0;inline double lastDb=0;}
#endif
#include "DSP/KeyraEngine.cpp"
int sr=48000,blockSize=127;
struct Case {std::string id,kind;int model,note,velocity,extra,steady;double held;std::uint32_t seed;};
struct Render {std::vector<float> audio;double cap[6]{},requested=0,requested2=0,compressor=1,limiter=0;int eligible=0;};
struct Event {int frame,kind,a,b,ch;};
std::uint64_t hash(const std::vector<float>&x){std::uint64_t h=14695981039346656037ull;for(float f:x){std::uint32_t b;std::memcpy(&b,&f,4);for(int i=0;i<4;++i){h^=(b>>(i*8))&255;h*=1099511628211ull;}}return h;}
Render render(keyra::Engine&e,const Case&c,bool enabled,bool suppress){
 keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(c.model));p.gain=.07f;p.mechanics=.175f;
 if(c.kind=="sustain")p.sustain=1;if(c.kind=="soft_pedal")p.soft=1;
 release_audit::enabled=enabled;release_audit::suppress=suppress;release_audit::eligible=0;
 tracking=true;e.setParameters(p);e.setSteadyStrikesForMeasurement(c.steady);e.reset();tracking=false;e.impl->touch=c.seed;
 const double duration=std::max(c.held+.5,.75);const int frames=std::lround(duration*sr),latency=e.outputLatencySamples();Render result;result.audio.resize(2*frames);
 std::vector<Event> events;const int off=std::lround(c.held*sr);
 if(c.kind!="pedal_only"){
  const int initial=c.kind=="repeat_soft_last"?127:c.kind=="repeat_hard_last"?8:c.velocity;
  events.push_back({0,0,c.note,initial,1});events.push_back({off,1,c.note,0,1});
 }
 if(c.kind=="repeat_soft_last"||c.kind=="repeat_hard_last"){
  events.push_back({int(std::lround(.05*sr)),0,c.note,c.kind=="repeat_soft_last"?8:127,1});events.push_back({int(std::lround(.25*sr)),1,c.note,0,1});
 }
 if(c.kind=="channels"){events.push_back({int(std::lround(.05*sr)),0,c.note,127,2});events.push_back({int(std::lround(.25*sr)),1,c.note,0,2});}
 if(c.kind=="mixed_after")events.push_back({int(std::lround(.1*sr)),4,0,0,1});
 if(c.kind=="toggle_on"||c.kind=="toggle_off")events.push_back({int(std::lround(.1*sr)),5,0,0,1});
 if(c.kind=="sustain")events.push_back({int(std::lround(.4*sr)),3,0,0,1});
 if(c.kind=="sostenuto"){events.push_back({int(std::lround(.1*sr)),2,66,127,1});events.push_back({int(std::lround(.4*sr)),2,66,0,1});}
 if(c.kind=="pedal_only"){events.push_back({int(std::lround(.1*sr)),2,64,127,1});events.push_back({int(std::lround(.2*sr)),2,64,0,1});}
 std::stable_sort(events.begin(),events.end(),[](auto&a,auto&b){return a.frame<b.frame;});std::array<float,257>l{},r{};int next=0;
 for(int frame=0;frame<frames+latency;){
  while(next<int(events.size())&&events[next].frame<=frame){const auto z=events[next++];tracking=true;
   if(z.kind==0)e.noteOn(z.a,z.b/127.f,z.ch);else if(z.kind==1)e.noteOff(z.a,z.ch);else if(z.kind==2)e.controlChange(z.a,z.b,z.ch);
   else if(z.kind==3){p.sustain=0;e.setParameters(p);}else if(z.kind==5){e.setSteadyStrikesForMeasurement(!c.steady);}else if(z.kind==4){p.build.action.fill(0);p.build.action[c.model]=.5f;p.build.action[c.extra]=.5f;e.setParameters(p);}tracking=false;
  }
  int count=std::min(blockSize,frames+latency-frame);if(next<int(events.size()))count=std::min(count,std::max(1,events[next].frame-frame));tracking=true;e.process(l.data(),r.data(),count);tracking=false;
  result.compressor=std::min({result.compressor,double(e.impl->output.from_),double(e.impl->output.to_)});result.limiter=std::max(result.limiter,double(e.impl->output.reduction_));
  for(int i=0;i<count;++i)if(frame+i>=latency){const int at=frame+i-latency;result.audio[2*at]=l[i];result.audio[2*at+1]=r[i];}frame+=count;
 }
#ifndef RELEASE_BASELINE
 for(int i=0;i<6;++i)result.cap[i]=e.impl->channels[0].releaseCapDb[i][c.note-21];

#endif
 result.eligible=release_audit::eligible;return result;
}
double power(const std::vector<float>&x,int start,int end){double e=0;for(int i=start;i<end;++i)e+=double(x[2*i])*x[2*i]+double(x[2*i+1])*x[2*i+1];return e/(2*(end-start));}
double diffPower(const std::vector<float>&x,const std::vector<float>&y,int start,int end){double e=0;for(int i=start;i<end;++i)for(int ch=0;ch<2;++ch){const double d=double(x[2*i+ch])-y[2*i+ch];e+=d*d;}return e/(2*(end-start));}

void require(bool x,const char* message){if(!x)throw std::runtime_error(message);}
double firstDraw(){std::uint32_t t=1;double d=0;for(int i=0;i<4;++i){t^=t<<13;t^=t>>17;t^=t<<5;d+=t*(1./4294967296.)-.5;}return d*std::sqrt(3.)*1.085;}
int main(){try{
 release_audit::enabled=true;int mathCases=0,audioCases=0,partitions=0;
 const double ref=keyra::responseDb(127*double(80/127.f));
 for(double distance:{-30.,-8.,0.,3.})for(double r:{.01,.25,1.,4.})for(double r80:{.1,1.,3.})for(double actual:{-12.,0.,12.})for(double reference:{-8.,0.,8.}){
  const double d=ref+distance,c=keyra::releaseBalanceCapDb(d,ref,r,r80,actual,reference);
  const double expected=distance>=0?0:std::min(0.,distance+reference-actual+20*std::log10(r80/r));
  require(std::isfinite(c)&&c<=0,"cap finite/nonpositive");
  require(std::abs(c-expected)<=128*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(expected)),"arbitrary-gain cap algebra");
  if(distance>=0)require(c==0,"above-reference exact identity");
  else require(r*std::pow(10.,(actual+c)/20)<=r80*std::pow(10.,(reference+distance)/20)*(1+256*std::numeric_limits<double>::epsilon()),"calibrated reference bound");
  ++mathCases;
 }
 for(int model=0;model<6;++model){
  keyra::Engine e(48000);keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));p.gain=.07f;
  release_audit::enabled=true;release_audit::suppress=false;
  e.setParameters(p);e.reset();e.noteOn(100,8/127.f,1);e.noteOn(100,127/127.f,2);
  const auto cap=e.impl->channels[0].releaseCapDb;require(e.impl->channels[0].presses[79]==1&&e.impl->channels[1].presses[79]==1,"channel press ownership");
  const double requested=keyra::responseDb(127*double(8/127.f))+firstDraw();
  for(int m=0;m<6;++m){const auto& md=keyra::models[m];const double v=e.impl->channels[0].velocity[m][79],v80=static_cast<float>(keyra::layerAt(md,ref)/127.);
   const double ratio=keyra::trackingGain(md.releaseTracking,v)/keyra::trackingGain(md.noteTracking,v),referenceRatio=keyra::trackingGain(md.releaseTracking,v80)/keyra::trackingGain(md.noteTracking,v80);
   const double expected=std::min(0.,requested-ref+20*std::log10(referenceRatio/ratio));
   require(std::abs(cap[m][79]-expected)<=4*std::numeric_limits<float>::epsilon()*std::max(1.,std::abs(expected)),"cached cap differs from independent strike oracle");
   require(e.impl->channels[1].releaseCapDb[m][79]==0,"hard other channel was capped");
  }
  p.build.action.fill(0);p.build.action[(model+1)%6]=1;e.setParameters(p);require(e.impl->channels[0].releaseCapDb==cap,"action change rewrote strike reference");
  release_audit::eligible=0;e.noteOff(100,1);require(release_audit::eligible==1&&e.impl->channels[1].presses[79]==1,"release crossed channel");e.noteOff(100,2);require(release_audit::eligible==2,"second channel missing release");
  e.reset();for(const auto& ch:e.impl->channels)for(const auto& caps:ch.releaseCapDb)for(float c:caps)require(c==0,"reset left stale cap");
  e.noteOn(100,1);e.noteOn(100,8/127.f);require(e.impl->channels[0].presses[79]==2&&e.impl->channels[0].releaseCapDb[model][79]<0,"latest soft strike not stored");
  release_audit::eligible=0;e.noteOff(100);require(release_audit::eligible==0,"first repeated release fired");e.noteOff(100);require(release_audit::eligible==1,"last repeated release missing");
 }
 for(int rate:{44100,48000,192000}){sr=rate;keyra::Engine e(rate);
  for(int m=0;m<6;++m)for(int n:{28,52,100})for(int v:{8,127}){
   Case c{"case","pure",m,n,v,0,0,.2,1};auto a=render(e,c,false,false),b=render(e,c,true,false),zero=render(e,c,false,true),cz=render(e,c,true,true);const int off=std::lround(c.held*sr),end=a.audio.size()/2;
   require(std::memcmp(a.audio.data(),b.audio.data(),off*2*sizeof(float))==0,"pre-release audio changed");require(zero.audio==cz.audio,"cap leaked outside release action");
   require(a.compressor==1&&b.compressor==1&&a.limiter==0&&b.limiter==0,"causal test output guard active");
   if(v==127)require(a.audio==b.audio,"above-reference audio changed");
   else {const double before=diffPower(a.audio,zero.audio,off,end),after=diffPower(b.audio,zero.audio,off,end);require(before>0&&after<before,"causal action did not attenuate");}
   for(float f:b.audio)require(std::isfinite(f),"nonfinite release audio");++audioCases;
  }
  for(int m=0;m<6;++m){Case c{"partition","pure",m,100,8,0,0,.2,1};blockSize=127;auto a=render(e,c,true,false);for(int block:{1,257}){blockSize=block;auto b=render(e,c,true,false);require(a.audio==b.audio,"block partition changed release");++partitions;}blockSize=127;}
 }
 sr=48000;keyra::Engine e(sr);
 for(int m=0;m<6;++m){
  for(const std::string kind:{"sustain","sostenuto","pedal_only","mixed_after","repeat_soft_last","repeat_hard_last","channels","toggle_on","toggle_off","steady"}){
   Case c{"semantics",kind,m,kind=="pedal_only"?52:100,8,(m+1)%6,kind=="steady"||kind=="toggle_off",.2,1};
   if(kind=="sustain"||kind=="sostenuto")c.note=52;
   auto a=render(e,c,false,false),b=render(e,c,true,false),zero=render(e,c,false,true),cz=render(e,c,true,true);
   require(zero.audio==cz.audio,"semantic cap leaked outside release");
   if(kind=="sustain"||kind=="sostenuto"||kind=="pedal_only"||kind=="steady"||kind=="toggle_off"||kind=="repeat_hard_last")require(a.audio==b.audio,"bypass/control changed audio");
   if(kind=="toggle_on")require(a.audio!=b.audio&&b.cap[m]<0,"later steady toggle bypassed stored cap");
   if(kind=="toggle_off")require(b.cap[m]==0,"later normal toggle altered steady strike");
   if(kind=="steady"){c.seed=3735928559u;auto another=render(e,c,true,false);require(b.audio==another.audio,"steady release depends on touch RNG");}
   ++audioCases;
  }
 }
 require(allocations==0,"callback allocation");
 std::cout<<"math="<<mathCases<<" audio="<<audioCases<<" partitions="<<partitions<<" allocations="<<allocations<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
"""

class ReleaseBalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="keyra-release-balance-")
        cls.work = Path(cls.temporary.name)
        cls.compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
        if not cls.compiler:
            raise RuntimeError("A C++17 compiler is required for release-balance tests")
        cls.original = (ROOT / "Source/DSP/KeyraEngine.cpp").read_text()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def build(self, name, disconnect=False):
        directory = self.work / name
        shutil.copytree(ROOT / "Source/DSP", directory / "Source/DSP")
        source = self.original
        token = "namespace keyra {"
        self.assertEqual(source.count(token), 1)
        source = source.replace(token, "namespace release_audit {inline bool enabled=true,suppress=false;inline int eligible=0;inline double lastDb=0;}\n" + token, 1)
        token = "double referenceCorrectionDb=0) noexcept {"
        self.assertEqual(source.count(token), 1)
        source = source.replace(token, token + "\n  if(!release_audit::enabled)return 0;", 1)
        token = "    actionKnock(sides);\n  }\n  // After anything that moves"
        self.assertEqual(source.count(token), 1)
        source = source.replace(token, "    ++release_audit::eligible;\n    if(!release_audit::suppress)actionKnock(sides);\n  }\n  // After anything that moves", 1)
        if disconnect:
            token = "+channel.releaseCapDb[p][key]"
            self.assertEqual(source.count(token), 1)
            source = source.replace(token, "", 1)
        (directory / "Source/DSP/KeyraEngine.cpp").write_text(source)
        (directory / "probe.cpp").write_text(NATIVE)
        binary = directory / "probe"
        build = subprocess.run([self.compiler, "-std=c++17", "-O3", "-I", str(directory / "Source"), str(directory / "probe.cpp"), "-o", str(binary)], text=True, capture_output=True)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        return subprocess.run([str(binary)], text=True, capture_output=True)

    def test_policy_and_native_paths(self):
        result = self.build("candidate")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("allocations=0", result.stdout)
        print(result.stdout.strip())

    def test_disconnected_release_is_rejected(self):
        result = self.build("disconnected", disconnect=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("causal action did not attenuate", result.stderr)

if __name__ == "__main__":
    unittest.main()
