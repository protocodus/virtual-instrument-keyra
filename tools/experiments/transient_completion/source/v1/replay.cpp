#include "/workspace/virtual-instrument-keyra/tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument/PreparedModel.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>

// PRIVATE offline contact-driven transient companion. It never changes the
// captured physical trajectory and never consumes captured bridge forces.
constexpr int rate=48000,frames=182400,event=4800;
constexpr double gammaFast=100,quietPressure=1e-20;
using Stereo=std::array<double,2>;
struct Stats {
  uint64_t nonfinite=0,controlDifferent=0,boardDifferent=0,forceContractErrors=0,forceProofMismatch=0;
  uint64_t fastSteps=0,skipped=0,wakes=0,retirements=0;
  long long retirementFrame=-1,lastForceFrame=-1;
  double controlError=0,boardError=0,maxPositiveScaleEnergy=0;
  double maxFreeEnergyRatio=0;
  double maxBoundRatio=0,maxHPCommutation=0,maxFastHPAfterQuarter=0;
  double retiredEnergy=0,discardedBound=0,rhoLoss=0;
};
struct HP {
  Stereo state{},previous{};
  Stereo step(Stereo x) {
    const double pole=std::exp(-2*grand::pi*24/rate);
    for(int ch=0;ch<2;++ch){state[ch]=pole*(state[ch]+x[ch]-previous[ch]);previous[ch]=x[ch];}
    return state;
  }
};
double energy(const grand::Piano& p) {
  double value=0;
  for(const auto& st:p.strings)value+=st.m.energy();
  for(const auto& z:p.board)value+=.5*z.w*z.w*(double(z.q)*z.q+double(z.p)*z.p);
  return value;
}
uint64_t forceHash(int note,double F,const std::array<double,15>& trace) {
  std::array<double,91> values{};values[note-21]=F;for(int g=0;g<3;++g)values[88+g]=trace[12+g];
  uint64_t h=14695981039346656037ull;const auto* bytes=reinterpret_cast<const unsigned char*>(values.data());
  for(size_t i=0;i<sizeof(values);++i){h^=bytes[i];h*=1099511628211ull;}return h;
}
Stereo correction(const grand::Piano& p) {
  Stereo out{};for(const auto& st:p.strings){auto r=st.cachedRadiation;out[0]+=r[0];out[1]+=r[1];}return out;
}
Stereo board(const grand::Piano& p) {
  Stereo out{};for(const auto& z:p.board){const double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+z.force;for(int ch=0;ch<2;++ch)out[ch]+=acc*z.mic[ch];}return out;
}
Stereo full(const grand::Piano& p) {
  auto out=board(p);for(const auto& st:p.strings){auto r=st.cachedRadiation;out[0]+=r[0];out[1]+=r[1];}return out;
}
void clearCoordinates(grand::Piano& p) {
  for(auto& st:p.strings){std::fill(st.m.q.begin(),st.m.q.end(),0.f);std::fill(st.m.p.begin(),st.m.p.end(),0.f);st.cachedRadiation={};st.velocity=st.force=0;}
  for(auto& z:p.board){z.q=z.p=0;z.force=0;}
}
void held(grand::Piano& p,int note) {p.resetState();p.noteOn(note,64);p.keys[note-21].hammerActive=false;}
double scaleHistory(grand::Piano& p,double rho,Stats& stats) {
  const double before=energy(p);
  for(auto& st:p.strings){auto& m=st.m;for(size_t j=0;j<m.size();++j){m.q[j]=double(m.q[j])*rho;m.p[j]=double(m.p[j])*rho;}}
  for(auto& z:p.board){z.q=double(z.q)*rho;z.p=double(z.p)*rho;}
  const double after=energy(p);stats.rhoLoss+=before-after;
  stats.maxPositiveScaleEnergy=std::max(stats.maxPositiveScaleEnergy,after-before);
  return before;
}
void advance(grand::Piano& p,int note,double force,uint64_t frame) {
  if(frame%64==0){p.pedal+=(1-std::exp(-64*p.dt/.012))*(p.pedalTarget-p.pedal);p.setDamping();}
  for(int index=0;index<88;++index){auto& k=p.keys[index];
    if(index==note-21){
      for(int si:k.strings)p.strings[si].m.freeStep();
      for(int si:k.strings)p.strings[si].m.force(force);
      for(int si:k.strings)p.strings[si].m.finishDamping();
    }else for(int si:k.strings)p.strings[si].m.freeDampedStep();
  }
  for(auto& z:p.board){double v=z.p*z.damp,y=z.q;z.q=z.c*y+z.s*v;z.p=(z.c*v-z.s*y)*z.damp;}
  p.groupedUnisonStep();p.bridgeStep(p.dt,true);
}
bool sameCoordinates(const grand::Piano& a,const grand::Piano& b) {
  if(a.strings.size()!=b.strings.size()||a.board.size()!=b.board.size())return false;
  for(size_t i=0;i<a.strings.size();++i){const auto& x=a.strings[i].m;const auto& y=b.strings[i].m;
    if(std::memcmp(x.q.data(),y.q.data(),x.q.size()*sizeof(float))||std::memcmp(x.p.data(),y.p.data(),x.p.size()*sizeof(float)))return false;}
  for(size_t i=0;i<a.board.size();++i)if(std::memcmp(&a.board[i].q,&b.board[i].q,sizeof(float))||std::memcmp(&a.board[i].p,&b.board[i].p,sizeof(float)))return false;
  return true;
}
double fastStep(grand::Piano& p,int note,double force,uint64_t frame,bool& active,Stats& stats,double rho,double norm,Stereo& output) {
  output={};if(!active&&force!=0){active=true;++stats.wakes;}
  if(!active){++stats.skipped;return 0;}
  const double priorEnergy=scaleHistory(p,rho,stats);advance(p,note,force,frame);++stats.fastSteps;
  const double E=energy(p),bound=2*norm*std::sqrt(2*E);output=correction(p);
  if(force==0&&priorEnergy>0)stats.maxFreeEnergyRatio=std::max(stats.maxFreeEnergyRatio,E/priorEnergy);
  if(bound>0)for(double v:output)stats.maxBoundRatio=std::max(stats.maxBoundRatio,std::abs(v)/bound);
  if(force==0&&bound<=quietPressure){++stats.retirements;stats.retirementFrame=frame;stats.retiredEnergy=E;stats.discardedBound=bound;clearCoordinates(p);active=false;output={};return 0;}
  return E;
}
int main(int argc,char** argv) {
  if(argc!=3){std::cerr<<"usage: replay CASES_TSV OUTPUT_DIRECTORY\n";return 2;}
  grand::Options options;options.sampleRate=rate;grand::Piano control(options),fast(options);
  const double rho=std::exp(-gammaFast/rate);Stereo norm2{};size_t maxModes=0;
  for(const auto& st:fast.strings){const auto& m=st.m;maxModes=std::max(maxModes,m.size());for(size_t j=0;j<m.size();++j){double w=m.omega[j];norm2[0]+=std::pow(double(m.radQL[j])/w,2)+std::pow(double(m.radPL[j])/w,2);norm2[1]+=std::pow(double(m.radQR[j])/w,2)+std::pow(double(m.radPR[j])/w,2);}}
  Stereo norms{{std::sqrt(norm2[0]),std::sqrt(norm2[1])}};const double norm=std::max(norms[0],norms[1]);
  // A fixed synthetic force, retirement, silence and later force test uses no
  // captured pressure. Only the companion is cleared; fresh-state equality
  // after its later nonzero input verifies wake semantics.
  held(fast,60);held(control,60);Stats synthetic;bool active=false;Stereo z{};uint64_t t=0;
  do{fastStep(fast,60,t==0?1:0,event+t,active,synthetic,rho,norm,z);++t;}while(active&&t<100000);
  const bool retired=!active&&synthetic.retirements==1;
  for(int i=0;i<64;++i)fastStep(fast,60,0,event+t+i,active,synthetic,rho,norm,z);
  Stats freshStats;scaleHistory(control,rho,freshStats);advance(control,60,1,event+t+64);
  fastStep(fast,60,1,event+t+64,active,synthetic,rho,norm,z);
  const bool wake=sameCoordinates(fast,control)&&z==correction(control)&&synthetic.wakes==2;
  std::ofstream syn(std::string(argv[2])+"/synthetic.json");syn<<std::setprecision(17)<<"{\"retired\":"<<(retired?"true":"false")<<",\"wake_coordinate_identity\":"<<(wake?"true":"false")<<",\"retirement_frame\":"<<synthetic.retirementFrame<<",\"discarded_pressure_bound\":"<<synthetic.discardedBound<<",\"max_scale_energy_increase\":"<<synthetic.maxPositiveScaleEnergy<<",\"max_free_energy_ratio\":"<<synthetic.maxFreeEnergyRatio<<",\"max_pressure_over_bound\":"<<synthetic.maxBoundRatio<<",\"control_faults\":"<<control.faultFlags<<",\"companion_faults\":"<<fast.faultFlags<<"}\n";syn.close();
  if(!retired||!wake||synthetic.maxPositiveScaleEnergy>0||synthetic.maxFreeEnergyRatio>1||synthetic.maxBoundRatio>1||control.faultFlags||fast.faultFlags)return 3;
  std::ifstream cases(argv[1]);std::string line;
  while(std::getline(cases,line)){
    if(line.empty())continue;std::istringstream row(line);std::string id,midiText,path,onsetText,proofPath;
    std::getline(row,id,'\t');std::getline(row,midiText,'\t');std::getline(row,path,'\t');std::getline(row,onsetText,'\t');std::getline(row,proofPath,'\t');const int midi=std::stoi(midiText),onset=std::stoi(onsetText);
    std::ifstream input(path,std::ios::binary),proof(proofPath,std::ios::binary);const std::string folder=std::string(argv[2])+"/"+id;
    std::ofstream data(folder+"/observer.f64le",std::ios::binary),baseline(folder+"/baseline.f32le",std::ios::binary),candidate(folder+"/candidate.f32le",std::ios::binary);
    if(!input||!proof||!data||!baseline||!candidate)return 4;
    held(control,midi);held(fast,midi);Stats stats;active=false;HP oldHP,newHP,fastHP;
    for(int frame=0;frame<frames;++frame){
      std::array<double,15> trace{};input.read(reinterpret_cast<char*>(trace.data()),sizeof(trace));if(!input)return 5;
      const double F=trace[11];if(!std::isfinite(F)||F<0||(frame<event&&F!=0)||(frame>=event+1920&&F!=0))++stats.forceContractErrors;
      // Captured bridge values are authenticated here ONLY. They are never
      // supplied to advance(); each instance solves its own bridge junction.
      std::array<uint64_t,3> recorded{};proof.read(reinterpret_cast<char*>(recorded.data()),sizeof(recorded));if(!proof)return 5;
      const auto actualForceHash=forceHash(midi,F,trace);if(recorded[0]!=uint64_t(frame)||recorded[1]!=actualForceHash||recorded[2]!=actualForceHash)++stats.forceProofMismatch;
      if(F!=0)stats.lastForceFrame=frame;
      advance(control,midi,F,frame);const auto replay=full(control),replayBoard=board(control);
      for(int ch=0;ch<2;++ch){stats.controlError=std::max(stats.controlError,std::abs(replay[ch]-trace[ch]));stats.boardError=std::max(stats.boardError,std::abs(replayBoard[ch]-trace[2+ch]));if(std::memcmp(&replay[ch],&trace[ch],sizeof(double)))++stats.controlDifferent;if(std::memcmp(&replayBoard[ch],&trace[2+ch],sizeof(double)))++stats.boardDifferent;}
      const double E=fastStep(fast,midi,F,frame,active,stats,rho,norm,z);
      Stereo rawOld{{trace[0],trace[1]}},rawNew{{trace[0]-z[0],trace[1]-z[1]}};
      auto old=oldHP.step(rawOld),made=newHP.step(rawNew),counter=fastHP.step(z);
      std::array<float,2> old32{{float(old[0]),float(old[1])}},made32{{float(made[0]),float(made[1])}};
      const double bound=2*norm*std::sqrt(2*E);
      std::array<double,16> output{{replay[0],replay[1],z[0],z[1],old[0],old[1],made[0],made[1],counter[0],counter[1],E,stats.rhoLoss,bound,F,rawNew[0],rawNew[1]}};
      for(double v:output)if(!std::isfinite(v))++stats.nonfinite;
      for(int ch=0;ch<2;++ch){stats.maxHPCommutation=std::max(stats.maxHPCommutation,std::abs(made[ch]-(old[ch]-counter[ch])));if(frame>=onset+12000)stats.maxFastHPAfterQuarter=std::max(stats.maxFastHPAfterQuarter,std::abs(counter[ch]));}
      data.write(reinterpret_cast<char*>(output.data()),sizeof(output));baseline.write(reinterpret_cast<char*>(old32.data()),sizeof(old32));candidate.write(reinterpret_cast<char*>(made32.data()),sizeof(made32));
    }
    char extra;if(input.read(&extra,1)||proof.read(&extra,1))return 6;
    std::ofstream report(folder+"/numeric.json");report<<std::setprecision(17)<<"{\"id\":\""<<id<<"\",\"frames\":"<<frames<<",\"gamma_per_second\":"<<gammaFast<<",\"rho\":"<<rho<<",\"mode_count\":"<<fast.modeCount()<<",\"string_count\":"<<fast.strings.size()<<",\"board_modes\":"<<fast.board.size()<<",\"dual_norm_LR\":["<<norms[0]<<','<<norms[1]<<"],\"max_modes_per_string\":"<<maxModes<<",\"control_nonidentical_samples\":"<<stats.controlDifferent<<",\"control_max_error\":"<<stats.controlError<<",\"board_nonidentical_samples\":"<<stats.boardDifferent<<",\"board_max_error\":"<<stats.boardError<<",\"force_contract_errors\":"<<stats.forceContractErrors<<",\"force_proof_mismatches\":"<<stats.forceProofMismatch<<",\"last_nonzero_force_frame\":"<<stats.lastForceFrame<<",\"nonfinite\":"<<stats.nonfinite<<",\"fast_processed_frames\":"<<stats.fastSteps<<",\"fast_skipped_frames\":"<<stats.skipped<<",\"wakes\":"<<stats.wakes<<",\"retirements\":"<<stats.retirements<<",\"retirement_frame\":"<<stats.retirementFrame<<",\"retired_energy\":"<<stats.retiredEnergy<<",\"discarded_pressure_bound\":"<<stats.discardedBound<<",\"max_positive_scale_energy\":"<<stats.maxPositiveScaleEnergy<<",\"max_free_energy_ratio\":"<<stats.maxFreeEnergyRatio<<",\"scale_energy_removed\":"<<stats.rhoLoss<<",\"max_pressure_over_bound\":"<<stats.maxBoundRatio<<",\"HP_commutation_max_error\":"<<stats.maxHPCommutation<<",\"fast_HP_max_after_250ms\":"<<stats.maxFastHPAfterQuarter<<",\"control_faults\":"<<control.faultFlags<<",\"companion_faults\":"<<fast.faultFlags<<"}\n";
    std::cout<<id<<" companion replay complete; rho1 raw mismatches="<<stats.controlDifferent<<", force errors="<<stats.forceContractErrors<<'\n'<<std::flush;
    if(stats.nonfinite||stats.forceContractErrors||stats.forceProofMismatch||stats.controlDifferent||stats.boardDifferent||stats.maxPositiveScaleEnergy>0||stats.maxFreeEnergyRatio>1||stats.maxBoundRatio>1||control.faultFlags||fast.faultFlags)return 7;
  }
  return 0;
}
