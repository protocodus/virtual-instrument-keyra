"""Native regression for transporting una-corda bias with physical lanes.

No recordings or third-party Python packages. A temporary engine copy adds
only test coordinates and a switch between its transported multiplier and the
legacy rank multiplier. The real candidate cache/single/blend/combine/strike
and renderer are exercised. No legacy mode is added to production.

Exact controls compare launched states at every stored anchor/edge and native
layer for soft0/.5/1, and every keyboard key/native layer at soft0. Short full
renders check selected anchor and neutral-pedal controls. Five previously
frozen rank crossings use a fixed carrier and exact layer, avoiding ordinary
pitch change and the unrelated nearest-anchor phase switch at t=.5.

Continuity is a numerical contraction test, not an audibility threshold:
shrinking coordinate separation1000-fold must reduce normalized waveform L2
difference at least10-fold, plus a declared float allowance of4*chunk*epsilon.
That allowance is not a proven error bound under arbitrary cancellation or
render lengths. Every measured distance and the allowance are printed. The
legacy mutation must fail this SAME assertion in all four selected grands;
the upright's distinct action remains a passing negative control. No claim
covers every interval or mixed-string builds, whose cross-piano pairing still
uses sorted rank. No current PCM hashes are stored as fixtures.

For the staged candidate:
KEYRA_SOFT_TEST_DSP=/path/to/candidate/Source/DSP python3 this_file.py -v
Once promoted, the default is the repository's current Source/DSP.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p/'CMakeLists.txt').is_file() and (p/'Source/DSP').is_dir())
DSP = Path(os.environ.get('KEYRA_SOFT_TEST_DSP', ROOT/'Source/DSP')).resolve()

PROBE = r'''
#include <array>
#include <memory>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <vector>
#define private public
#include "KeyraEngine.h"
#undef private
#include "KeyraEngine.cpp"
void require(bool ok,const std::string& message){if(!ok)throw std::runtime_error(message);}
constexpr double sr=48000.;
const char* names[]={"grand","upright","kawai","hamburg","newyork"};
std::string context(int model,int note,double velocity,double soft){return std::string(names[model])+" note="+std::to_string(note)+" velocity="+std::to_string(velocity)+" soft="+std::to_string(soft);}
template<class T>void append(std::vector<std::uint64_t>& out,T value){static_assert(sizeof(T)<=8,"scalar state only");std::uint64_t bits=0;std::memcpy(&bits,&value,sizeof(T));out.push_back(bits);}
void launch(keyra::Engine& engine,int model,int note,float velocity,float soft,bool legacy,double pitch=-1,double layer=-1){
 keyra::testLegacySoftRank=legacy;keyra::testPitchCoordinate=pitch;keyra::testLayerCoordinate=layer;
 keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));p.gain=.07f;p.soft=soft;
 // Reset before changing builds, so a previous sounding body cannot start
 // a pickup glide into the next independent case. Reset again captures the
 // new controls at their initial values. No private state is patched.
 engine.reset();engine.setParameters(p);engine.reset();engine.setSteadyStrikesForMeasurement(true);
 engine.noteOn(note,velocity/127.f);
}
std::vector<std::uint64_t> state(keyra::Engine& engine){
 const auto& voices=engine.impl->voices;auto found=std::find_if(voices.begin(),voices.end(),[](const auto&v){return v.active;});require(found!=voices.end(),"no launched voice");
 const auto&v=*found;std::vector<std::uint64_t> out;append(out,v.count);
 for(int i=0;i<v.count;++i){const auto&p=v.partials[i];
  append(out,p.frequency);append(out,p.riseDecay);append(out,p.riseLeap);append(out,p.riseStep);append(out,p.tint);append(out,p.tintScale);
  append(out,p.damperScale);append(out,p.slowShare);append(out,p.slowScale);
  for(int k=0;k<keyra::lanes;++k){append(out,p.decay[k]);append(out,p.hz[k]);append(out,p.baseLeftRe[k]);append(out,p.baseLeftIm[k]);append(out,p.baseRightRe[k]);append(out,p.baseRightIm[k]);
   append(out,p.step[k].re);append(out,p.step[k].im);append(out,p.leap[k].re);append(out,p.leap[k].im);
   append(out,keyra::lane(p.c,k));append(out,keyra::lane(p.s,k));append(out,keyra::lane(p.leftRe,k));append(out,keyra::lane(p.leftIm,k));append(out,keyra::lane(p.rightRe,k));append(out,keyra::lane(p.rightIm,k));
  }
 }
 return out;
}
std::vector<float> render(keyra::Engine& engine,int model,int note,float velocity,float soft,bool legacy,double pitch=-1,double layer=-1,int frames=38400){
 launch(engine,model,note,velocity,soft,legacy,pitch,layer);
 std::vector<float> out;out.reserve(2*frames);std::array<float,64> l{},r{};const int latency=engine.outputLatencySamples();
 for(int first=0;first<frames+latency;){const int n=std::min(64,frames+latency-first);engine.process(l.data(),r.data(),n);
  for(int j=0;j<n;++j)if(first+j>=latency){require(std::isfinite(l[j])&&std::isfinite(r[j]),"non-finite native waveform");out.push_back(l[j]);out.push_back(r[j]);}first+=n;}
 require(out.size()==static_cast<std::size_t>(2*frames),"wrong render length");return out;
}
bool bitEqual(const std::vector<float>&a,const std::vector<float>&b){return a.size()==b.size()&&std::memcmp(a.data(),b.data(),a.size()*sizeof(float))==0;}
double distance(const std::vector<float>&a,const std::vector<float>&b){require(a.size()==b.size(),"waveform shape mismatch");double difference=0,reference=0;
 for(std::size_t i=0;i<a.size();++i){const double x=a[i],y=b[i];difference+=(x-y)*(x-y);reference+=(x*x+y*y)*.5;}
 require(std::isfinite(reference)&&reference>0&&std::isfinite(difference),"invalid waveform normalization");return std::sqrt(difference/reference);
}
void identity(){
 keyra::Engine engine(sr);std::size_t anchors=0,neutral=0,shortWaves=0;
 auto compare=[&](int model,int note,float velocity,float soft){launch(engine,model,note,velocity,soft,false);const auto candidate=state(engine);launch(engine,model,note,velocity,soft,true);require(candidate==state(engine),"legacy launched-state mismatch: "+context(model,note,velocity,soft));};
 for(int model=0;model<keyra::pianoCount;++model){const auto&m=keyra::models[model];std::vector<int> notes{21,108};for(int a=0;a<m.anchorCount;++a)notes.push_back(m.anchors[a].note);std::sort(notes.begin(),notes.end());notes.erase(std::unique(notes.begin(),notes.end()),notes.end());
  for(int note:notes)for(int layer=0;layer<m.layers;++layer)for(float soft:{0.f,.5f,1.f}){compare(model,note,m.layerVelocity[layer],soft);++anchors;}
  for(int note=21;note<=108;++note)for(int layer=0;layer<m.layers;++layer){compare(model,note,m.layerVelocity[layer],0);++neutral;}
  const int middle=m.anchorCount/2;
  // Actual measured-key context for the soft control; interior neutral
  // control demonstrates the new bias cannot leak into soft=0 rendering.
  for(int k=0;k<2;++k){const int note=k?(m.anchors[middle].note+m.anchors[middle+1].note)/2:m.anchors[middle].note;const float soft=k?0:1;const float velocity=k?80:m.layerVelocity[m.layers-1];
   const auto a=render(engine,model,note,velocity,soft,false,-1,-1,6144),b=render(engine,model,note,velocity,soft,true,-1,-1,6144);
   require(bitEqual(a,b),"short full-waveform identity failed: "+context(model,note,velocity,soft));++shortWaves;}
 }
 require(anchors>0&&neutral>0&&shortWaves==2*keyra::pianoCount,"identity coverage missing");
 std::cout<<"anchor_edge_states="<<anchors<<" all_key_native_layer_soft0_states="<<neutral<<" short_full_waveform_controls="<<shortWaves<<'\n';
}
struct Crossing{int model,left,right,order;double velocity,root;};
// Frozen selection: largest baseline partial soft-power change relative to
// midpoint ordinary energy per model. Each root is the pitch coordinate at
// which the partial's blended lanes change which one decays fastest or
// slowest, so the legacy rank multiplier jumps there: a diagnostic
// coordinate, not stored PCM or asserted acoustic truth. Lane rates have
// been mixed in 1/s rather than in their logarithm since 2026-11-04, which
// moved every crossing (the grand's from .0738 to .0384); the roots were
// recomputed then for the same selection and the same pairs of lanes, each
// interval's first crossing as before.
constexpr Crossing cases[]{
 {0,102,105,1,14,.038431191265448056},
 {1,68,70,1,15,.075080330333073431},
 {2,99,105,1,27,.001117318313440504},
 {3,38,45,2,123,.95958703206468776},
 {4,99,104,1,117,.0067451579922411208}
};
void continuity(){
 keyra::Engine engine(sr);std::size_t rejectedLegacy=0,negativeControls=0;
 constexpr double coarse=1e-6,fine=1e-9;
 // A numerical allowance tied to the float oscillator's32-sample double
 // re-anchoring cadence, not a formal whole-render error bound or an
 // audible tolerance. Three decades of coordinate contraction must give
 // at least one decade of waveform contraction before this allowance.
 constexpr double allowance=4*keyra::chunk*std::numeric_limits<float>::epsilon();
 std::cout<<"model,soft,mode,coarse_distance,fine_distance,limit,passes\n";
 for(const auto&c:cases){const auto&m=keyra::models[c.model];const int note=(c.left+c.right)/2,upper=keyra::upperAnchor(m,note);
  require(m.anchors[upper-1].note==c.left&&m.anchors[upper].note==c.right,"frozen crossing no longer matches anchor interval");require(std::abs(c.root-.5)>coarse,"crossing confounded by phase midpoint");
  for(int soft:{0,1}){std::vector<float> candidate[2][2];double candidateDelta[2]{};
   for(int size=0;size<2;++size){const double epsilon=size?fine:coarse;for(int side=0;side<2;++side)candidate[size][side]=render(engine,c.model,note,80,soft,false,c.root+(side?epsilon:-epsilon),c.velocity);candidateDelta[size]=distance(candidate[size][0],candidate[size][1]);}
   const double candidateLimit=.1*candidateDelta[0]+allowance;const bool candidatePass=candidateDelta[1]<=candidateLimit;
   require(candidatePass,"transported native waveform continuity failed: "+context(c.model,note,c.velocity,soft));
   std::cout<<names[c.model]<<','<<soft<<",transported,"<<candidateDelta[0]<<','<<candidateDelta[1]<<','<<candidateLimit<<','<<candidatePass<<'\n';
   double legacyDelta[2]{};
   for(int size=0;size<2;++size){const double epsilon=size?fine:coarse;auto a=render(engine,c.model,note,80,soft,true,c.root-epsilon,c.velocity),b=render(engine,c.model,note,80,soft,true,c.root+epsilon,c.velocity);legacyDelta[size]=distance(a,b);
    if(soft==0){require(bitEqual(a,candidate[size][0])&&bitEqual(b,candidate[size][1]),"soft0 crossing waveform changed");}
   }
   const double legacyLimit=.1*legacyDelta[0]+allowance;const bool legacyPass=legacyDelta[1]<=legacyLimit;
   std::cout<<names[c.model]<<','<<soft<<",legacy,"<<legacyDelta[0]<<','<<legacyDelta[1]<<','<<legacyLimit<<','<<legacyPass<<'\n';
   if(soft==0||!m.unaCorda){require(legacyPass,"neutral/upright continuity control failed");if(soft==1)++negativeControls;}
   else {require(!legacyPass,"legacy rank mutation escaped continuity assertion: "+context(c.model,note,c.velocity,soft));++rejectedLegacy;}
  }
 }
 require(rejectedLegacy==4&&negativeControls==1,"mutation/negative-control coverage missing");
 std::cout<<"legacy_grand_mutations_rejected="<<rejectedLegacy<<" upright_negative_controls="<<negativeControls<<" declared_numerical_allowance="<<allowance<<'\n';
}
int main(int argc,char**argv){try{std::cout<<std::setprecision(17);require(argc==2,"mode required");if(std::string(argv[1])=="identity")identity();else if(std::string(argv[1])=="continuity")continuity();else throw std::runtime_error("unknown mode");return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''


class SoftLaneContinuity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='keyra-soft-test-')
        cls.addClassCleanup(cls.temporary.cleanup)
        work = Path(cls.temporary.name)
        source = (DSP/'KeyraEngine.cpp').read_text()
        needle = 'std::pow(10.,l.level/20)*felt*(1+soft*l.softBias)'
        if source.count(needle) != 1:
            raise AssertionError('candidate transported soft multiplier missing or ambiguous')
        source = source.replace(needle, 'std::pow(10.,l.level/20)*felt*(testLegacySoftRank?'
                                '(k==0?1-.28*soft:k==lanes-1?1+.08*soft:1.):(1+soft*l.softBias))')
        source = source.replace('namespace {\n', 'namespace {\n'
                                'bool testLegacySoftRank=false;\n'
                                'double testPitchCoordinate=-1,testLayerCoordinate=-1;\n', 1)
        layer = '      channel.velocity[p][note-21]=static_cast<float>(x.v/127);'
        pitch = '      x.t=std::max(0.,std::min(1.,static_cast<double>(note-x.a->note)/(x.b->note-x.a->note)));'
        if source.count(layer) != 1 or source.count(pitch) != 1:
            raise AssertionError('native strike coordinate hooks changed')
        source = source.replace(layer, '      if(testLayerCoordinate>=0)x.v=testLayerCoordinate;\n'+layer)
        source = source.replace(pitch, pitch+'\n      if(testPitchCoordinate>=0)x.t=testPitchCoordinate;')
        (work/'KeyraEngine.cpp').write_text(source)
        (work/'probe.cpp').write_text(PROBE)
        cls.binary = work/'probe'
        subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-DNDEBUG', '-ffp-contract=off',
                        '-I', str(work), '-I', str(DSP), str(work/'probe.cpp'), '-o', str(cls.binary)],
                       check=True, capture_output=True, text=True)

    def run_native(self, mode):
        result = subprocess.run([str(self.binary), mode], capture_output=True, text=True)
        print(result.stdout.strip())
        self.assertEqual(result.returncode, 0, result.stderr.strip())

    def test_actual_anchor_edge_and_soft0_identity(self):
        self.run_native('identity')

    def test_full_native_waveform_continuity_and_legacy_mutation(self):
        self.run_native('continuity')


if __name__ == '__main__':
    unittest.main()
