// Diagnostic wrapper around a frozen full-model source/header copied under out/.
// Observation ablations are authored causal probes, never calibrated presets.
#define main keyraFrozenGrandMain
#include "grand.cpp"
#undef main
#include <cstring>

namespace {
uint64_t hashMechanical(const grand::Piano& p) {
  uint64_t h=1469598103934665603ULL;
  auto add=[&](const auto& value){unsigned char b[sizeof(value)];std::memcpy(b,&value,sizeof(value));
    for(unsigned char x:b){h^=x;h*=1099511628211ULL;}};
  for(const auto& st:p.strings){for(float q:st.m.q)add(q);for(float v:st.m.p)add(v);}
  for(const auto& z:p.board){add(z.q);add(z.p);}
  for(const auto& k:p.keys){add(k.hammerX);add(k.hammerV);add(k.hammerActive);}
  return h;
}
void observation(grand::Piano& p,const std::string& variant) {
  if(variant=="v4"||variant=="hardness-prior")return;
  for(auto& st:p.strings){auto& m=st.m;grand::Cal cal(st.note);
    for(size_t j=0;j<m.size();++j){
      if(variant=="analytic-observation" || (variant=="no-sub250-correction"&&m.omega[j]<2*grand::pi*250)){
        m.radQL[j]=m.radPL[j]=m.radQR[j]=m.radPR[j]=0;
      }else if(variant=="zero-H-phase-correction"){
        double target=std::pow(10.,cal.mode(m.partial[j],m.polarization[j]?
          &piano_calibration::Anchor::radiationAfterDb:&piano_calibration::Anchor::radiationDb)/20.);
        double ratio=std::clamp(target/std::max(double(m.radiationMagnitude[j]),1e-8),.025,40.);
        if(m.partial[j]>64)ratio=1+(ratio-1)*std::exp(-(m.partial[j]-64)/24.);
        const double sign=double(m.b[j])*(ratio-1);
        // Remove only the loaded-board H phase from the additive correction.
        // Keep each channel's existing correction magnitude and transformer sign.
        for(int ch=0;ch<2;++ch){float& q=ch?m.radQR[j]:m.radQL[j];float& v=ch?m.radPR[j]:m.radPL[j];
          double magnitude=std::hypot(double(q),double(v));q=0;v=static_cast<float>(std::copysign(magnitude,sign));}
      }
    }
  }
}
}
int main(int argc,char** argv) {
 try {
  if(argc!=4)throw std::runtime_error("variant velocity output-prefix required");
  const std::string variant=argv[1],prefix=argv[3];const int velocity=std::stoi(argv[2]);
  if(velocity!=40&&velocity!=93)throw std::runtime_error("Only locked A0 TRAIN velocity proxies40/93");
  const std::vector<std::string> variants={"v4","hardness-prior","analytic-observation","zero-H-phase-correction","no-sub250-correction"};
  if(std::find(variants.begin(),variants.end(),variant)==variants.end())throw std::runtime_error("Unknown variant");
  grand::Options opt;opt.sampleRate=48000;opt.captureStems=true;grand::Piano p(opt);
  auto& key=p.keys[0];if(variant=="hardness-prior")key.K/=.8;
  observation(p,variant);
  const size_t frames=16800,onset=4800;std::array<std::vector<float>,4> audio;
  for(auto& a:audio)a.resize(2*frames);
  std::array<std::array<double,2>,4> hp{},previous{};
  const double pole=std::exp(-2*grand::pi*24/48000);
  std::ofstream trace(prefix+"-trace.csv");if(!trace)throw std::runtime_error("Cannot open trace");
  trace<<std::setprecision(17)<<"frame,force_N,hammer_x_m,hammer_v_m_s,compression_m,hammer_active\n";
  std::vector<std::pair<size_t,uint64_t>> hashes;
  double impulse=0,firstForce=-1,lastForce=-1;size_t above=0;
  for(size_t frame=0;frame<frames;++frame){
    if(frame==onset)p.noteOn(21,velocity);
    const bool activeBefore=key.hammerActive;const double beforeV=key.hammerV;
    auto out=p.step(frame);
    const double force=activeBefore?(beforeV-key.hammerV)*key.mass/p.dt:0.;
    impulse+=force*p.dt;
    if(force>1e-4){if(firstForce<0)firstForce=double(frame)/48000;lastForce=double(frame)/48000;++above;}
    double y=0;for(int si:key.strings)y+=p.strings[si].m.displacement();
    trace<<frame<<','<<force<<','<<key.hammerX<<','<<key.hammerV<<','<<key.hammerX-y<<','<<key.hammerActive<<'\n';
    for(size_t channel=0;channel<2;++channel){
      const std::array<double,4> raw={out[channel],p.lastStems[0][channel],p.lastStems[1][channel],p.lastStems[2][channel]};
      for(size_t s=0;s<4;++s){hp[s][channel]=pole*(hp[s][channel]+raw[s]-previous[s][channel]);previous[s][channel]=raw[s];
        audio[s][2*frame+channel]=static_cast<float>(hp[s][channel]);}
    }
    if(frame==onset-1||frame==onset+143||frame==onset+999||frame==onset+4799||frame+1==frames)
      hashes.push_back({frame,hashMechanical(p)});
  }
  const std::array<std::string,4> suffix={".wav","-primary.wav","-secondary.wav","-transient.wav"};
  for(size_t s=0;s<4;++s)grand::wav(prefix+suffix[s],audio[s],48000);
  std::ofstream metrics(prefix+".json");if(!metrics)throw std::runtime_error("Cannot open metrics");
  metrics<<std::setprecision(17)<<"{\"variant\":\""<<variant<<"\",\"velocity\":"<<velocity
    <<",\"sample_rate\":48000,\"frames\":"<<frames<<",\"event_frame\":"<<onset
    <<",\"hammer_stiffness\":"<<key.K<<",\"hammer_mass_kg\":"<<key.mass
    <<",\"velocity_exponent\":"<<key.velocityExponent<<",\"max_force_N\":"<<p.maxForce
    <<",\"contact_seconds_above_1e_minus4_N\":"<<double(above)/48000
    <<",\"first_force_seconds\":"<<firstForce<<",\"last_force_seconds\":"<<lastForce
    <<",\"contact_impulse_N_s\":"<<impulse<<",\"contact_solves\":"<<p.forceSolves
    <<",\"contact_max_relative_residual\":"<<p.maxContactResidual
    <<",\"final_mechanical_energy_J\":"<<p.energy()<<",\"mechanical_hash_checkpoints\":[";
  for(size_t i=0;i<hashes.size();++i){if(i)metrics<<',';metrics<<"{\"frame\":"<<hashes[i].first<<",\"fnv1a64\":\""<<hashes[i].second<<"\"}";}
  metrics<<"]}\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
