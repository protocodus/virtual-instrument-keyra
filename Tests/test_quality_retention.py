"""Brightness-aware quality retention, using the real native types and audio.

The analytic check enumerates line-envelope breakpoints independently of the
implementation's interval intersection, and also checks a dense float-tint
oracle. An interior-only synthetic slot rejects an endpoint-union mutation.
The audio check rejects the former strike-tint pruning on the SAME supported
band assertion. Full histories have exact parity with that test-only mutation;
no legacy path or PCM fixture is added to production.
"""
import csv
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
LEGACY=r'''  void keepAudible(Voice& voice,double dropDb) noexcept {
    double peak[maxPartials],energy[maxPartials],peakTop=0,energyTop=0;
    for(int k=0;k<voice.count;++k){const auto& x=voice.partials[k];double p=0,e=0;
      for(int j=0;j<lanes;++j){p+=std::sqrt(x.energyWeight[j]);e+=x.energyWeight[j]/(1-x.decay[j]*x.decay[j]);}
      peak[k]=p*x.tint;energy[k]=e*x.tint*x.tint;
      peakTop=std::max(peakTop,peak[k]);energyTop=std::max(energyTop,energy[k]);}
    const double peakFloor=peakTop*std::pow(10.,-dropDb/20),energyFloor=energyTop*std::pow(10.,-dropDb/10);
    int kept=0;for(int k=0;k<voice.count;++k)
      if(peak[k]>=peakFloor||energy[k]>=energyFloor){if(kept!=k)voice.partials[kept]=voice.partials[k];++kept;}
    voice.count=kept;
  }'''

PROBE=r'''
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <fstream>
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
using Values=std::array<double,keyra::maxPartials>;
using Mask=std::array<bool,keyra::maxPartials>;
struct Proxies{Values p{},e{},s{};int n=0;};
Proxies proxies(const keyra::Voice& v){Proxies a;a.n=v.count;
  for(int k=0;k<a.n;++k){const auto& x=v.partials[k];a.s[k]=x.tintScale;
    for(int j=0;j<keyra::lanes;++j){a.p[k]+=std::sqrt(x.energyWeight[j]);a.e[k]+=x.energyWeight[j]/(1-x.decay[j]*x.decay[j]);}}
  return a;
}
Mask native(keyra::Engine& engine,keyra::Voice v,double drop){
  const int n=v.count;for(int k=0;k<n;++k)v.partials[k].frequency=1000+k;
  trap=true;engine.impl->keepAudible(v,drop);trap=false;Mask result{};
  for(int k=0;k<v.count;++k){const int id=int(v.partials[k].frequency)-1000;require(id>=0&&id<n,"slot correspondence");result[id]=true;}return result;
}
// Independent oracle: the upper envelope of lines can change only at a
// pairwise crossing. Evaluate every such point plus both endpoints.
Values bestMargins(const Values& level,const Values& slope,int n,double exponent){
  Values best;best.fill(-std::numeric_limits<double>::infinity());
  std::vector<double> points{0,1};
  for(int i=0;i<n;++i)if(level[i]>0)for(int j=i+1;j<n;++j)if(level[j]>0&&slope[i]!=slope[j]){
    const double b=.5+(std::log(level[j])-std::log(level[i]))/(exponent*std::log(2.)*(slope[i]-slope[j]));
    if(b>=0&&b<=1)points.push_back(b);}
  for(double b:points){Values logs;double top=-std::numeric_limits<double>::infinity();
    for(int k=0;k<n;++k){logs[k]=level[k]>0?std::log(level[k])+exponent*std::log(2.)*slope[k]*(b-.5):-std::numeric_limits<double>::infinity();top=std::max(top,logs[k]);}
    for(int k=0;k<n;++k)if(level[k]>0)best[k]=std::max(best[k],logs[k]-top);
  }return best;
}
void interior(){keyra::Engine e;keyra::Voice v;v.count=3;
  const double amp[]{1,1.05e-3,1};
  for(int k=0;k<3;++k){v.partials[k].energyWeight[0]=amp[k]*amp[k];v.partials[k].tintScale=2*k;v.partials[k].tint=static_cast<float>(std::pow(2.,-.5*2*k));}
  const auto selected=native(e,v,60);require(selected[1],"interior-only eligible slot was removed");
  // Both endpoint masks really exclude it, so their union is an invalid fix.
  for(double b:{0.,1.}){double p[3],top=0;for(int k=0;k<3;++k){p[k]=amp[k]*std::pow(2.,(b-.5)*2*k);top=std::max(top,p[k]);}
    require(p[1]<top*1e-3,"synthetic case is not interior-only");}
}
void oracle(){interior();std::size_t denseChecks=0,analyticChecks=0;
  for(int model=0;model<6;++model){keyra::Engine e;keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));
    for(int note:{21,36,60,84,108})for(int velocity:{40,100}){
      e.setParameters(p);e.reset();e.noteOn(note,velocity/127.f);const auto v=e.impl->voices[0];const auto a=proxies(v);
      const auto peak=bestMargins(a.p,a.s,a.n,1),energy=bestMargins(a.e,a.s,a.n,2);
      for(double drop:{50.,60.}){const auto kept=native(e,v,drop);
        const double pt=-drop*std::log(10.)/20-4*std::numeric_limits<float>::epsilon();
        const double et=-drop*std::log(10.)/10-8*std::numeric_limits<float>::epsilon();
        for(int k=0;k<a.n;++k){const double margin=std::max(peak[k]-pt,energy[k]-et);
          if(margin>1e-10)require(kept[k],"analytic breakpoint oracle found removed slot");
          if(margin< -1e-10)require(!kept[k],"interval implementation retained an impossible slot");++analyticChecks;}
        for(int step=0;step<=2048;++step){const double b=step/2048.;Values pv{},ev{};double ptop=0,etop=0;
          for(int k=0;k<a.n;++k){const float tint=static_cast<float>(std::pow(2.,(b-.5)*a.s[k]));pv[k]=a.p[k]*tint;ev[k]=a.e[k]*tint*tint;ptop=std::max(ptop,pv[k]);etop=std::max(etop,ev[k]);}
          for(int k=0;k<a.n;++k){if(pv[k]>=ptop*std::pow(10.,-drop/20)||ev[k]>=etop*std::pow(10.,-drop/10))require(kept[k],"dense float-tint oracle found removed slot");++denseChecks;}
        }
      }
    }
  }require(allocations==0,"allocation in retention callback");
  std::cout<<"analytic_slots="<<analyticChecks<<" dense_slot_tests="<<denseChecks<<'\n';
}
struct Event{int frame;float brightness;};
std::vector<Event> events(int history){
  if(history<2)return {};
  if(history==2)return {{5760,1}};
  if(history==3)return {{5760,1},{6049,.2f},{6591,.85f},{8167,0},{19201,1}};
  return {{5760,0},{6049,.8f},{6591,.15f},{8167,1},{19201,0}};
}
std::vector<float> audio(int model,int quality,int history,bool varied){
  constexpr int total=36000;keyra::Engine e;keyra::Parameters p;p.gain=.07f;p.mechanics=.175f;
  p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));p.quality=static_cast<keyra::Quality>(quality);
  p.brightness=history==1||history==4?1.f:0.f;
  e.setParameters(p);e.reset();const auto schedule=events(history);
  std::vector<float> wave(2*total);std::array<float,257> l{},r{};std::size_t next=0;int block=0;
  constexpr int blocks[]{1,7,31,32,127,257};
  trap=true;e.noteOn(60,100/127.f);
  for(int frame=0;frame<total;){
    if(next<schedule.size()&&frame==schedule[next].frame){p.brightness=schedule[next++].brightness;e.setParameters(p);}
    const int end=next<schedule.size()?schedule[next].frame:total;
    const int n=std::min({total-frame,end-frame,varied?blocks[block++%6]:1});
    e.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){require(std::isfinite(l[i])&&std::isfinite(r[i]),"nonfinite quality audio");wave[2*(frame+i)]=l[i];wave[2*(frame+i)+1]=r[i];}frame+=n;
  }trap=false;return wave;
}
void render(const std::string& dir){
  for(int model=0;model<6;++model)for(int quality=0;quality<3;++quality)for(int history=0;history<5;++history)for(int varied=0;varied<2;++varied){
    const auto x=audio(model,quality,history,varied!=0);
    std::ofstream out(dir+"/m"+std::to_string(model)+"q"+std::to_string(quality)+"h"+std::to_string(history)+"p"+std::to_string(varied)+".f32",std::ios::binary);
    out.write(reinterpret_cast<const char*>(x.data()),static_cast<std::streamsize>(x.size()*sizeof(float)));require(bool(out),"wave write");
  }require(allocations==0,"allocation in note/control/audio callback");
  std::cout<<"render_cases=180 callback_allocations="<<allocations<<'\n';
}
void future(){std::array<float,128> al{},ar{},bl{},br{};
  for(int model=0;model<6;++model){keyra::Engine a,b;keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));p.gain=.07f;
    a.setParameters(p);b.setParameters(p);a.reset();b.reset();a.noteOn(60,.8f);b.noteOn(60,.8f);
    a.process(al.data(),ar.data(),128);b.process(bl.data(),br.data(),128);
    p.quality=keyra::Quality::light;a.setParameters(p);
    for(int block=0;block<20;++block){a.process(al.data(),ar.data(),128);b.process(bl.data(),br.data(),128);
      require(al==bl&&ar==br,"Quality change affected an already launched strike");}
  }
}
int main(int argc,char**argv){try{require(argc>=2,"mode");const std::string mode=argv[1];
  if(mode=="oracle")oracle();else if(mode=="interior")interior();else if(mode=="audio"){require(argc==3,"output folder");render(argv[2]);future();}else require(false,"unknown mode");return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''


def replace_function(source,body):
    start=source.index('  void keepAudible(');begin=source.index('{',start);depth=1;end=begin+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[:start]+body+source[end:]


class QualityRetention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='keyra-quality-retention-');cls.folder=Path(cls.temp.name)
        cls.binaries={}
        for variant in ('candidate','legacy'):
            p=cls.folder/variant;shutil.copytree(ROOT/'Source/DSP',p);cpp=p/'KeyraEngine.cpp'
            if variant=='legacy':cpp.write_text(replace_function(cpp.read_text(),LEGACY))
            (p/'probe.cpp').write_text(PROBE);exe=p/'probe'
            subprocess.run([os.environ.get('CXX','c++'),'-std=c++17','-O3','-DNDEBUG','-I',str(p),str(p/'probe.cpp'),'-o',str(exe)],check=True)
            cls.binaries[variant]=exe

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_interval_envelope_and_dense_float_oracle(self):
        subprocess.run([str(self.binaries['candidate']),'oracle'],check=True)
        mutation=subprocess.run([str(self.binaries['legacy']),'interior'],capture_output=True,text=True)
        self.assertNotEqual(mutation.returncode,0)
        self.assertIn('interior-only eligible slot was removed',mutation.stderr)

    def test_native_audio_full_identity_partition_and_live_band_recovery(self):
        for variant in ('candidate','legacy'):
            p=self.folder/variant/'waves';p.mkdir()
            subprocess.run([str(self.binaries[variant]),'audio',str(p)],check=True)
        path=lambda v,m,q,h,p:self.folder/v/'waves'/f'm{m}q{q}h{h}p{p}.f32'
        for model in range(6):
            for history in range(5):
                for partition in range(2):
                    self.assertEqual(path('candidate',model,0,history,partition).read_bytes(),
                                     path('legacy',model,0,history,partition).read_bytes())
                for quality in range(3):
                    errors=[]
                    for variant in ('candidate','legacy'):
                        x=np.fromfile(path(variant,model,quality,history,0),'<f4').astype(float)
                        y=np.fromfile(path(variant,model,quality,history,1),'<f4').astype(float)
                        self.assertTrue(np.all(np.isfinite(x))&np.all(np.isfinite(y)))
                        peak=max(np.max(np.abs(x)),np.max(np.abs(y)));self.assertGreater(peak,0)
                        errors.append((np.max(np.abs(x-y)),peak))
                    # Same inherited partition behavior, plus an explicitly
                    # numerical float-output allowance (not an acoustic margin).
                    self.assertLessEqual(errors[0][0],errors[1][0]+8*np.finfo(np.float32).eps*max(errors[0][1],errors[1][1]))
        # The causal measured witness: a formerly discarded harmonic band
        # becomes supported after brightening. Rectified zero/floor shortcuts
        # would fail this real stereo waveform comparison.
        def band(variant,quality):
            x=np.fromfile(path(variant,1,quality,2,1),'<f4').reshape(-1,2)
            # Native raw Engine timeline contains96samples lookahead.
            x=x[round(.15*48000)+96:round(.3*48000)+96].astype(float)
            w=np.hanning(len(x));nfft=1<<(len(x)-1).bit_length();z=np.fft.rfft(x*w[:,None],n=nfft,axis=0)
            hz=np.fft.rfftfreq(nfft,1/48000);center=1000*2**(8/3)
            mask=(hz>=center*2**(-1/6))&(hz<center*2**(1/6))
            return np.sum(abs(z[mask])**2)
        full=band('candidate',0);self.assertGreater(full,0)
        error=lambda v:abs(10*np.log10(band(v,2)/full))
        self.assertLess(error('candidate'),1.)
        self.assertGreater(error('legacy'),1.)


if __name__=='__main__':unittest.main()
