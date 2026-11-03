"""Native regressions for the post-guard Tube monitoring calibration.

No recordings or third-party Python packages. An otherwise identical live
engine with the calibration gain disabled is the full-wave control. A separate
FIFO oracle checks moving controls at both render block partitions; inherited
body-pickup float roundoff is reported, not attributed to the new gain path.
"""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
#include <array>
#include <memory>
#include <vector>
#include <deque>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <cstdlib>
#include <new>
#define private public
#include "KeyraEngine.h"
#undef private
#include "KeyraEngine.cpp"
namespace {bool trap=false;std::size_t allocations=0;}
void* operator new(std::size_t n){if(trap)++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept{std::free(p);}void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}void operator delete[](void* p,std::size_t) noexcept{std::free(p);}
void require(bool b,const char* m){if(!b)throw std::runtime_error(m);}
using Audio=std::vector<float>;
Audio render(keyra::Engine& e,int n,int block=257){Audio a(2*n);std::array<float,512> l{},r{};for(int i=0;i<n;){int k=std::min(block,n-i);e.process(l.data(),r.data(),k);for(int j=0;j<k;++j){a[2*(i+j)]=l[j];a[2*(i+j)+1]=r[j];}i+=k;}return a;}
void untrim(keyra::Engine& e){e.impl->tubeOutputTarget=1;e.impl->resetTubeOutput();}
keyra::Parameters params(int piano,float mic){keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(piano));p.mic=mic;p.gain=.7f;return p;}
void strike(keyra::Engine& e){for(int n:{45,52,57,60,64})e.noteOn(n,1.f);}
float scalar(const keyra::Parameters& p){const auto w=keyra::sharesOf(p.build.hammers);return static_cast<float>(1+p.mic*w[5]*(std::pow(10.,-keyra::belmontTubeOutputTrimDb/20)-1));}
void staticCase(double sr,const keyra::Parameters& p){keyra::Engine a(sr),b(sr);a.setParameters(p);b.setParameters(p);a.reset();b.reset();untrim(b);strike(a);strike(b);const auto x=render(a,16000),y=render(b,16000);const float g=scalar(p);for(std::size_t i=0;i<x.size();++i){require(x[i]==(g==1?y[i]:y[i]*g),"static full-wave scalar/parity mismatch");// The unchanged guard's float multiplication can land one ULP above
// kCeiling (also in the untrimmed reference); the trim must never raise it.
require(std::isfinite(x[i])&&std::abs(x[i])<=std::abs(y[i])&&std::abs(x[i])<=std::nextafter(protocodus::OutputStage<2>::kCeiling,1.f),"ceiling/finite failure");}}
keyra::Parameters at(int i,keyra::Parameters p){if(i==1003)p.mic=1;if(i==3001){p.build.hammers=keyra::only(keyra::Piano::grand);p.build.hammers[5]=1;}if(i==5003)p.mic=.25f;if(i==7001)p.mic=0;if(i==9003){p.build=keyra::measuredBuild(keyra::Piano::grand);p.mic=1;}return p;}
Audio moving(int block,bool disabled=false){keyra::Engine e;auto p=params(5,0);e.setParameters(p);e.reset();if(disabled)untrim(e);strike(e);Audio all;int previous=0;for(int end:{1003,3001,5003,7001,9003,12000}){auto a=render(e,end-previous,block);all.insert(all.end(),a.begin(),a.end());p=at(end,p);e.setParameters(p);if(disabled)untrim(e);previous=end;}return all;}
int main(){try{
 require(keyra::belmontTubeOutputTrimDb==.3216,"measured monitoring calibration changed");
 for(double sr:{44100.,48000.,192000.})for(int p=0;p<6;++p)for(float mic:{0.f,.5f,1.f})staticCase(sr,params(p,mic));
 auto mixed=params(0,.7f);mixed.build.hammers[5]=1;staticCase(48000,mixed);
 const auto segmented=moving(1),chunked=moving(257),oldSegmented=moving(1,true),oldChunked=moving(257,true);
 double inherited=0,observed=0;for(std::size_t i=0;i<segmented.size();++i){inherited=std::max(inherited,static_cast<double>(std::abs(oldSegmented[i]-oldChunked[i])));observed=std::max(observed,static_cast<double>(std::abs(segmented[i]-chunked[i])));}
 std::cout<<"moving_full_build_baseline_partition_peak="<<inherited<<" candidate="<<observed<<'\n';
 // Full-build pickup glides already have float roundoff across render blocks.
 // Require the new gain to remain exact against each partition's own control.

 // Independent FIFO oracle: observe the unmodified Mic path, smooth only
 // the new hammer-share calibration, and delay by the published latency.
 for(int block:{1,257}){
 keyra::Engine a,b;auto p=params(5,0);a.setParameters(p);b.setParameters(p);a.reset();b.reset();untrim(b);strike(a);strike(b);
 double monitor=std::pow(10.,-keyra::belmontTubeOutputTrimDb/20),mic=0;const double smooth=1-std::exp(-1/(.012*48000));std::deque<float> fifo(a.outputLatencySamples(),1.f);
 int previous=0;for(int end:{1003,3001,5003,7001,9003,12000}){
   const auto x=render(a,end-previous,block),y=render(b,end-previous,block);
   const auto w=keyra::sharesOf(p.build.hammers);const double target=1+w[5]*(std::pow(10.,-keyra::belmontTubeOutputTrimDb/20)-1);
   for(int i=previous;i<end;++i){if(mic>0||p.mic>0){mic+=smooth*(p.mic-mic);if(std::abs(p.mic-mic)<1e-6)mic=p.mic;}
     monitor+=smooth*(target-monitor);const float g=fifo.front();fifo.pop_front();fifo.push_back(static_cast<float>(1+mic*(monitor-1)));
     for(int ch=0;ch<2;++ch){const auto n=2*(i-previous)+ch;require(x[n]==(g==1?y[n]:y[n]*g),"moving trim is not aligned with input-frame latency");}}
   p=at(end,p);a.setParameters(p);b.setParameters(p);untrim(b);previous=end;
 }
 }
 // A hard reset, idle control changes, prepare and CC120 must not retain a
 // historical trim queue. Existing body reset behavior is exercised too.
 for(float mic:{0.f,.5f,1.f}){keyra::Engine history,fresh;auto old=params(5,1),now=params(5,mic);history.setParameters(old);history.reset();strike(history);render(history,107);history.setParameters(now);history.reset();fresh.setParameters(now);fresh.reset();strike(history);strike(fresh);require(render(history,8192)==render(fresh,8192),"reset retains historical monitoring gain");}
 keyra::Engine idle,fresh;auto final=params(5,1);idle.setParameters(params(0,0));idle.reset();render(idle,103);idle.setParameters(final);render(idle,117);fresh.setParameters(final);fresh.reset();strike(idle);strike(fresh);require(render(idle,8192)==render(fresh,8192),"sleeping control change retains old trim");
 keyra::Engine e;e.setParameters(final);e.reset();strike(e);render(e,1001);e.controlChange(120,0);require(e.impl->tubeOutputIndex==0,"CC120 did not clear trim delay");e.prepare(44100);require(e.outputLatencySamples()==keyra::ForteOutput::DelayFor(44100),"trim changes published latency");
 std::array<float,256> l{},r{};trap=true;e.setParameters(mixed);e.noteOn(60,.7f);e.process(l.data(),r.data(),256);e.controlChange(120,0);e.reset();trap=false;require(allocations==0,"monitoring calibration allocates in callbacks");
 std::cout<<"55 static cases: exact post-guard scalar, Mic0/other-five parity and ceiling; moving gain FIFO, block partitions, reset/idle/CC120/prepare and callback allocation passed\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''

class TubeOutputCalibration(unittest.TestCase):
    def test_native_controls(self):
        with tempfile.TemporaryDirectory(prefix="keyra-tube-output-") as folder:
            folder = Path(folder)
            source = folder / "probe.cpp"
            binary = folder / "probe"
            source.write_text(PROBE)
            command = shlex.split(os.environ.get("CXX", "c++")) + [
                "-O3", "-DNDEBUG", "-std=c++17",
                "-I" + str(ROOT / "Source/DSP"), str(source), "-o", str(binary)]
            subprocess.run(command, check=True)
            result = subprocess.run([str(binary)], check=True, text=True, capture_output=True)
            print(result.stdout, end="")
            self.assertIn("callback allocation passed", result.stdout)

if __name__ == "__main__":
    unittest.main()
