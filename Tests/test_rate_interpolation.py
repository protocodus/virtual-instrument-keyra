"""Native checks for pitch interpolation of an unidentified fitted decay.

Uses no recordings or third-party Python packages. The audio control disables
only pitchRate's confidence coordinate in a temporary copy of the current
engine, so other accepted DSP changes remain present on both sides.
"""
import ast
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DSP = ROOT/'Source/DSP'

PROBE = r'''
#include <array>
#include <memory>
#include <cstdlib>
#include <new>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <stdexcept>
#define private public
#include "KeyraEngine.h"
#undef private
#include "KeyraEngine.cpp"
namespace {bool trap=false;std::size_t allocations=0;}
void* operator new(std::size_t size){if(trap)++allocations;if(void* p=std::malloc(size?size:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t size){return ::operator new(size);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
void operator delete[](void* p,std::size_t) noexcept{std::free(p);}
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
bool sameLane(const keyra::LaneData& a,const keyra::LaneData& b){
  return a.rate==b.rate&&a.offset==b.offset&&a.level==b.level&&a.ratio==b.ratio&&a.angle==b.angle
    &&a.phase.re==b.phase.re&&a.phase.im==b.phase.im&&a.left.re==b.left.re&&a.left.im==b.left.im
    &&a.right.re==b.right.re&&a.right.im==b.right.im;
}
bool samePartial(const keyra::PartialData& a,const keyra::PartialData& b){
  if(a.order!=b.order||a.cents!=b.cents||a.rise!=b.rise)return false;
  for(int j=0;j<keyra::lanes;++j)if(!sameLane(a.lane[j],b.lane[j]))return false;
  return true;
}
std::uint64_t hashSample(std::uint64_t hash,float value){
  require(std::isfinite(value),"non-finite rendered sample");
  std::uint32_t bits;std::memcpy(&bits,&value,sizeof(bits));
  for(int i=0;i<4;++i){hash^=(bits>>(8*i))&255u;hash*=1099511628211ull;}
  return hash;
}
int main(int argc,char** argv){try{
  const bool audio=argc>1&&std::strcmp(argv[1],"audio")==0;
  keyra::Engine engine(48000);
  std::array<float,64> left{},right{};
  if(audio){
    // Low, middle and high recorded pitches, three ordinary MIDI velocities,
    // held and released through the complete native engine and output stage.
    for(int p=0;p<keyra::pianoCount;++p){const auto& m=keyra::models[p];
      for(int index:{0,m.anchorCount/2,m.anchorCount-1})for(int velocity:{32,80,120}){
        keyra::Parameters parameters;parameters.build=keyra::measuredBuild(static_cast<keyra::Piano>(p));parameters.gain=.07f;
        engine.setParameters(parameters);engine.reset();
        const int note=m.anchors[index].note;std::uint64_t hash=14695981039346656037ull;
        trap=true;engine.noteOn(note,velocity/127.f);
        for(int block=0;block<240;++block){
          if(block==120)engine.noteOff(note);
          engine.process(left.data(),right.data(),64);
          for(int i=0;i<64;++i){hash=hashSample(hash,left[i]);hash=hashSample(hash,right[i]);}
        }
        engine.reset();trap=false;
        std::cout<<p<<' '<<note<<' '<<velocity<<' '<<hash<<'\n';
      }
    }
    require(allocations==0,"anchor live API allocation");return 0;
  }
  std::size_t lanes=0,bound=0,mixed=0,known=0,morphs=0,guardedSeries=0;
  for(int p=0;p<keyra::pianoCount;++p){const auto& m=keyra::models[p];
    const int count=m.anchors[m.anchorCount-1].first+m.anchors[m.anchorCount-1].count;
    for(int i=0;i<count;++i)for(int j=0;j<keyra::lanes;++j){
      const auto& measured=m.partials[i].lanes[j];
      require(std::isfinite(measured.rate)&&measured.rate>=keyra::fittedRateLowerBound,"fitted lane violates documented rate bound");
      const auto lane=keyra::laneAt(m,measured,engine.impl->partialLanes[m.partialFirst+i][j],64);
      require(lane.rateIdentified==(measured.rate!=keyra::fittedRateLowerBound),"support must use original stored float");
      ++lanes;if(!lane.rateIdentified)++bound;
    }
    for(int anchor=1;anchor<m.anchorCount;++anchor){const auto& aa=m.anchors[anchor-1];const auto& bb=m.anchors[anchor];
      int i=aa.first,j=bb.first;
      while(i<aa.first+aa.count&&j<bb.first+bb.count){
        if(m.partials[i].order<m.partials[j].order){++i;continue;}
        if(m.partials[j].order<m.partials[i].order){++j;continue;}
        const auto& ca=engine.impl->partialLanes[m.partialFirst+i];const auto& cb=engine.impl->partialLanes[m.partialFirst+j];
        const auto pair=keyra::pairing(ca,cb);
        const auto a=keyra::single(m,m.partials[i],ca,64),b=keyra::single(m,m.partials[j],cb,64);
        for(int lane=0;lane<keyra::lanes;++lane){const auto& x=a.lane[lane];const auto& y=b.lane[pair[lane]];
          if(x.rateIdentified!=y.rateIdentified)++mixed;else ++known;
          for(double t:{0.,1e-9,1e-6,.125,.5,.875,1-1e-6,1-1e-9,1.}){
            // The rates mix in 1/s between the pitches; the endpoints are the
            // measured rates exactly, as stored (their logarithms).
            const double rate=keyra::pitchRate(x,y,t);
            const double linear=t==0||t==1?keyra::mix(x.rate,y.rate,t):std::log(keyra::mix(std::exp(x.rate),std::exp(y.rate),t));
            const double tolerance=64*std::numeric_limits<double>::epsilon()*std::max({1.,std::abs(x.rate),std::abs(y.rate)});
            require(rate>=std::min(x.rate,y.rate)-tolerance&&rate<=std::max(x.rate,y.rate)+tolerance,"pitch pole leaves endpoint bounds");
            if(x.rateIdentified==y.rateIdentified||t==0||t==1)require(rate==linear,"same-support lane or measured endpoint changed");
            // The quadratic coordinate has derivative magnitude at most two,
            // so the rate in 1/s, which it mixes, moves at most twice as far.
            const double rx=std::exp(x.rate),ry=std::exp(y.rate),r=std::exp(rate);
            const double rateTolerance=64*std::numeric_limits<double>::epsilon()*std::max({1.,rx,ry});
            if(t<1e-5)require(std::abs(r-rx)<=2*t*std::abs(ry-rx)+rateTolerance,"left pole discontinuity");
            if(t>1-1e-5)require(std::abs(r-ry)<=2*(1-t)*std::abs(ry-rx)+rateTolerance,"right pole discontinuity");
          }
        }
        // Confidence applies to pitch gaps, never to the between-piano path.
        auto markedA=a,markedB=b;
        for(int k=0;k<keyra::lanes;++k){markedA.lane[k].rateIdentified=false;markedB.lane[k].rateIdentified=true;}
        for(double t:{0.,.2,.5,.8,1.}){
          require(samePartial(keyra::combine(a,b,t,1-t),keyra::combine(markedA,markedB,t,1-t)),"support leaked into piano morph");++morphs;
        }
        // Exercise the real single -> guarded velocity -> pitch blend path,
        // which series() plays wherever the keyboard network's table holds
        // none of the key, not just pitchRate in isolation. A disconnected
        // helper would still preserve every recorded-anchor audio hash.
        bool mixedSupport=false;
        for(int k=0;k<keyra::lanes;++k)mixedSupport|=a.lane[k].rateIdentified!=b.lane[pair[k]].rateIdentified;
        const int note=(aa.note+bb.note)/2;
        if(mixedSupport&&note>aa.note&&note<bb.note)for(int layer=0;layer<m.layers-1;++layer){
          if(!((ca.velocityMask|cb.velocityMask)&(1u<<layer)))continue;
          const double velocity=(m.layerVelocity[layer]+m.layerVelocity[layer+1])*.5;
          const auto va=keyra::single(m,m.partials[i],ca,velocity),vb=keyra::single(m,m.partials[j],cb,velocity);
          auto supportedA=va,supportedB=vb;
          for(int k=0;k<keyra::lanes;++k){
            require(va.lane[k].rateIdentified==(m.partials[i].lanes[k].rate>keyra::fittedRateLowerBound)
                    &&vb.lane[k].rateIdentified==(m.partials[j].lanes[k].rate>keyra::fittedRateLowerBound),
                    "guarded velocity lost fitted-rate support");
            supportedA.lane[k].rateIdentified=supportedB.lane[k].rateIdentified=true;
          }
          const double t=static_cast<double>(note-aa.note)/(bb.note-aa.note);
          keyra::Side side;side.m=&m;side.a=&aa;side.b=&bb;side.v=velocity;side.t=t;
          const int count=engine.impl->blended(side,p);const keyra::PartialData* played=nullptr;
          for(int k=0;k<count;++k)if(engine.impl->seriesData[p][k].order==va.order)played=&engine.impl->seriesData[p][k];
          require(played!=nullptr,"shared partial missing from series");
          std::array<double,keyra::lanes> expected{},linearExpected{};
          for(int k=0;k<keyra::lanes;++k){const auto& x=va.lane[k];const auto& y=vb.lane[pair[k]];
            linearExpected[k]=std::log(keyra::mix(std::exp(x.rate),std::exp(y.rate),t));
            // Bernstein form independently states the quadratic contract in
            // 1/s: its middle control point is the identified endpoint.
            const double control=x.rateIdentified?x.rate:y.rate;
            expected[k]=x.rateIdentified==y.rateIdentified?linearExpected[k]
              :std::log((1-t)*(1-t)*std::exp(x.rate)+2*t*(1-t)*std::exp(control)+t*t*std::exp(y.rate));
          }
          std::sort(expected.begin(),expected.end(),std::greater<double>());
          std::sort(linearExpected.begin(),linearExpected.end(),std::greater<double>());
          const auto linear=keyra::blend(supportedA,supportedB,t,pair);bool changed=false;
          for(int k=0;k<keyra::lanes;++k){
            const double tolerance=64*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(expected[k]));
            require(std::abs(played->lane[k].rate-expected[k])<=tolerance,"blend bypasses supported pitch interpolation");
            require(std::abs(linear.lane[k].rate-linearExpected[k])<=tolerance,"equal-support blend changed");
            changed|=std::abs(played->lane[k].rate-linear.lane[k].rate)>tolerance;
          }
          require(changed,"guarded interior blend did not apply support prior");
          for(double edge:{0.,1.})require(samePartial(keyra::blend(va,vb,edge,pair),keyra::blend(supportedA,supportedB,edge,pair)),
                                        "support changed pitch endpoint");
          ++guardedSeries;
        }
        ++i;++j;
      }
    }
    // Exercise every actual pitch gap through note start and render while
    // trapping allocations; preparation happened before the trap.
    keyra::Parameters parameters;parameters.build=keyra::measuredBuild(static_cast<keyra::Piano>(p));
    trap=true;engine.setParameters(parameters);
    for(int note=21;note<=108;++note){engine.noteOn(note,.63f);engine.process(left.data(),right.data(),64);engine.noteOff(note);engine.reset();}
    trap=false;
  }
  require(bound>0&&mixed>0&&known>0&&guardedSeries>0,"support test has no coverage");
  require(allocations==0,"pitch interpolation live API allocation");
  // A concrete unsupported/supported pair: the supported endpoint is the
  // middle Bezier control, giving quarter/three-quarter weights at halfway.
  keyra::LaneData unknown,supported;unknown.rate=std::log(.003);unknown.rateIdentified=false;supported.rate=std::log(2.);supported.rateIdentified=true;
  require(std::abs(keyra::pitchRate(unknown,supported,.5)-std::log(.25*.003+.75*2.))<1e-14,"support prior is inactive");
  std::cout<<"lanes="<<lanes<<" bound_lanes="<<bound<<" mixed_pairs="<<mixed<<" equal_support_pairs="<<known<<" morph_checks="<<morphs<<" guarded_series_checks="<<guardedSeries<<" live_allocations="<<allocations<<'\n';
  return 0;
}catch(const std::exception& e){trap=false;std::cerr<<e.what()<<'\n';return 1;}}
'''


class RateInterpolation(unittest.TestCase):
    def test_fitter_bound_contract(self):
        module = ast.parse((ROOT/'Tools/piano_analysis.py').read_text())
        bounds = [ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == 'SLOWEST_RATE' for target in node.targets)]
        self.assertEqual(len(bounds), 1)
        source = (DSP/'KeyraEngine.cpp').read_text()
        match = re.search(r'constexpr float fittedRateLowerBound=([.\deE+-]+)f;', source)
        self.assertIsNotNone(match)
        self.assertEqual(float(match.group(1)), bounds[0])

    def test_native_support_continuity_morph_and_anchor_audio(self):
        source = (DSP/'KeyraEngine.cpp').read_text()
        candidate = 'coordinate=t+t*(1-t)*confidence;'
        self.assertEqual(source.count(candidate), 1)
        control = source.replace(candidate, 'coordinate=t;(void)confidence;')
        with tempfile.TemporaryDirectory(prefix='keyra-rate-test-') as directory:
            root = Path(directory)
            probe = root/'probe.cpp'
            probe.write_text(PROBE)
            binaries = []
            for name, text in (('candidate', source), ('linear-control', control)):
                include = root/name
                include.mkdir()
                (include/'KeyraEngine.cpp').write_text(text)
                binary = root/(name+'-probe')
                subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-ffp-contract=off',
                                '-I', str(include), '-I', str(DSP), str(probe), '-o', str(binary)],
                               check=True, capture_output=True, text=True)
                binaries.append(binary)
            print(subprocess.check_output([str(binaries[0])], text=True).strip())
            audio = [subprocess.check_output([str(binary), 'audio'], text=True) for binary in binaries]
            # Three recorded pitches at three velocities for each of the five pianos.
            self.assertEqual(len(audio[0].splitlines()), 45)
            self.assertEqual(audio[0], audio[1], 'native recorded-anchor audio changed')
            print('bit-identical native anchor renders=45')


if __name__ == '__main__':
    unittest.main()
