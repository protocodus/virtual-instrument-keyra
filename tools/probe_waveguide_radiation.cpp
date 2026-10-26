// Offline observation-only C2/C4 study; never linked into a plugin/backend.
#define main keyra_waveguide_radiation_control_main
#include "../src/full_reference/grand.cpp"
#undef main
#include "keyra/physics/WaveguideString.h"
#include <filesystem>
#include <ctime>
#include <cstring>

namespace {
using WG=keyra::physics::WaveguideString;
WG::Config readConfig(const std::filesystem::path& path) {
  std::ifstream in(path);std::string name;double f1,b,z,position;
  WG::Config c;if(!(in>>name>>f1>>b>>z>>position))throw std::runtime_error("configuration header");c.impedance=z;
  auto read=[&](WG::PathConfig& p){
    if(!(in>>p.delaySamples>>p.lossGain>>p.lossMix>>p.allpassCount)||p.allpassCount>WG::allpassCapacity)throw std::runtime_error("configuration path");
    for(unsigned i=0;i<p.allpassCount;++i)if(!(in>>p.allpass[i]))throw std::runtime_error("configuration allpass");
    p.dcPreservingLoss=true;p.dcLossPole=std::exp(-2*grand::pi*2/WG::sampleRate);
  };read(c.left);read(c.toBridge);c.fromBridge=c.toBridge;
  WG validate;if(!validate.prepare(c))throw std::runtime_error("invalid configuration");return c;
}
void pathJson(std::ostream& o,const WG::PathConfig& p) {
  o<<"{\"delay\":"<<p.delaySamples<<",\"gain\":"<<p.lossGain<<",\"mix\":"<<p.lossMix
   <<",\"dc_shelf\":"<<(p.dcPreservingLoss?"true":"false")<<",\"dc_pole\":"<<p.dcLossPole<<",\"allpass\":[";
  for(unsigned i=0;i<p.allpassCount;++i){if(i)o<<',';o<<p.allpass[i];}o<<"]}";
}
double pulse(unsigned frame,unsigned start,unsigned length,double amplitude) {
  if(frame<start||frame>=start+length)return 0;
  const double s=std::sin(grand::pi*(frame-start+.5)/length);return amplitude*s*s;
}
double force(unsigned frame,unsigned kind) {
  if(kind==0)return frame==0?1:0;
  if(kind==1)return pulse(frame,0,96,1);
  if(kind==2)return pulse(frame,0,24,1);
  if(kind==3)return pulse(frame,0,72,1)+pulse(frame,4800,96,.8)+pulse(frame,5100,24,.5)+pulse(frame,9600,72,.9);
  return 0;
}
void dump(grand::Piano& piano,int note,const std::filesystem::path& dir,const std::filesystem::path& profiles) {
  const auto& key=piano.keys[note-21];auto& m=piano.strings[key.strings.front()].m;
  // Isolate a held string: constructor state has closed dampers. Use the
  // original intrinsic modal losses, not released-key damper attenuation.
  for(unsigned i=0;i<m.size();++i)m.damp[i]=std::exp(-m.loss[i]*piano.dt);
  const auto cfg=readConfig(profiles/(note==36?"C2-s32.cfg":"C4-s32.cfg"));
  const std::string name=note==36?"C2":"C4";
  std::ofstream j(dir/(name+"-model.json"));j<<std::setprecision(17);
  j<<"{\"note\":"<<note<<",\"sample_rate\":48000,\"string_index\":"<<key.strings.front()<<",\"choir_count\":"<<key.strings.size()
   <<",\"original_f0_hz\":"<<key.f0<<",\"original_B\":"<<key.B<<",\"impedance\":"<<cfg.impedance<<",\"left\":";pathJson(j,cfg.left);
  j<<",\"to_bridge\":";pathJson(j,cfg.toBridge);j<<",\"from_bridge\":";pathJson(j,cfg.fromBridge);j<<",\"damping_condition\":\"intrinsic held key, damper open\",\"modes\":[";
  std::vector<unsigned> modes;
  for(unsigned i=0;i<m.size();++i)if(m.polarization[i]==0)modes.push_back(i);
  for(unsigned k=0;k<modes.size();++k){const auto i=modes[k];if(k)j<<',';
    j<<"{\"n\":"<<m.partial[i]<<",\"omega\":"<<m.omega[i]<<",\"c\":"<<m.c[i]<<",\"s\":"<<m.s[i]<<",\"damp\":"<<m.damp[i]<<",\"intrinsic_loss_per_second\":"<<m.loss[i]
     <<",\"hammer\":"<<m.hammer[i]<<",\"bridge_port\":"<<m.b[i]<<",\"force_q\":"<<m.forceQ[i]<<",\"force_p\":"<<m.forceP[i]
     <<",\"rad\":["<<m.radQL[i]<<','<<m.radPL[i]<<','<<m.radQR[i]<<','<<m.radPR[i]<<"]}";
  }j<<"],\"columns\":[\"generalized_key_force_N\",\"WG_contact_velocity_m_s\",\"WG_reaction_on_fixed_bridge_N\",\"target_correction_L\",\"target_correction_R\",\"modal_contact_velocity\"]}\n";
  for(unsigned kind=0;kind<4;++kind) {
    WG wg;if(!wg.prepare(cfg))throw std::runtime_error("WG prepare");
    std::vector<double> q(m.size(),0),p(m.size(),0),data;data.reserve(48000*6);
    for(unsigned f=0;f<48000;++f) {
      const double input=force(f,kind);const auto w=wg.step(input/key.strings.size(),0);
      double l=0,r=0,v=0;
      for(auto i:modes){
        const double old=q[i],pv=p[i]*m.damp[i];
        q[i]=m.c[i]*old+m.s[i]*pv+m.forceQ[i]*input;
        p[i]=(m.c[i]*pv-m.s[i]*old+m.forceP[i]*input)*m.damp[i];
        l+=m.radQL[i]*q[i]+m.radPL[i]*p[i];r+=m.radQR[i]*q[i]+m.radPR[i]*p[i];
        v+=m.hammer[i]*m.omega[i]*p[i];
      }
      for(double x:{input,w.contactVelocity,-w.bridgeForce,l,r,v}){if(!std::isfinite(x))throw std::runtime_error("nonfinite");data.push_back(x);}
    }
    std::ofstream b(dir/(name+"-fixture"+std::to_string(kind)+".f64"),std::ios::binary);
    b.write(reinterpret_cast<const char*>(data.data()),data.size()*sizeof(double));if(!b)throw std::runtime_error("trace write");
  }
}
}
int main(int argc,char** argv)try {
  if(argc!=3){std::cerr<<"usage: probe_waveguide_radiation OUTPUT_DIR PROFILE_DIR\n";return 1;}
  std::filesystem::path dir=argv[1];std::filesystem::create_directories(dir);
  grand::Options opt;opt.sampleRate=48000;grand::Piano piano(opt);
  for(int note:{36,60})dump(piano,note,dir,argv[2]);
  std::cout<<"Exported two isolated primary-string modal controls and WG state traces; correction radiation only.\n";
  return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
