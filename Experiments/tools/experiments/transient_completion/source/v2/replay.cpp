// Reuse the frozen v1 mechanical recurrence verbatim; its old main is unused.
#include <stdexcept>
#define main transient_v1_unused_main
#include "/workspace/virtual-instrument-keyra/out/full-transient-completion/v1/replay.cpp"
#undef main

struct FullBound {
  Stereo dynamic{},force{},combined{};
  double inverseFrobenius=0,matrixFrobenius=0;
  grand::Vec3 beta{};
};
FullBound fullBound(const grand::Piano& p) {
  FullBound result;grand::Vec3 D[2]{};std::vector<double> alpha(p.strings.size());
  for(size_t i=0;i<p.strings.size();++i){const auto& st=p.strings[i];const double r=st.resistance*p.opt.bridge;alpha[i]=r/(1+.5*p.dt*r*st.compliance);result.beta[st.group]+=alpha[i];}
  grand::Mat3 M{},inverse{};
  for(int g=0;g<3;++g)for(int h=0;h<3;++h){M[g][h]=(g==h?1.:0.)+.5*p.dt*result.beta[g]*p.boardGram[g][h];result.matrixFrobenius+=M[g][h]*M[g][h];}
  for(int col=0;col<3;++col){grand::Vec3 unit{},answer{};unit[col]=1;if(!grand::solve3(M,unit,answer))throw std::runtime_error("Cold full bound matrix failure");for(int row=0;row<3;++row){inverse[row][col]=answer[row];result.inverseFrobenius+=answer[row]*answer[row];}}
  result.matrixFrobenius=std::sqrt(result.matrixFrobenius);result.inverseFrobenius=std::sqrt(result.inverseFrobenius);
  for(const auto& st:p.strings){const auto& m=st.m;for(size_t j=0;j<m.size();++j){const double w=m.omega[j];result.dynamic[0]+=std::pow(double(m.radQL[j])/w,2)+std::pow(double(m.radPL[j])/w,2);result.dynamic[1]+=std::pow(double(m.radQR[j])/w,2)+std::pow(double(m.radPR[j])/w,2);}}
  for(const auto& z:p.board)for(int ch=0;ch<2;++ch){result.dynamic[ch]+=z.mic[ch]*z.mic[ch]*(z.w*z.w+4*z.sigma*z.sigma);for(int g=0;g<3;++g)D[ch][g]-=z.mic[ch]*z.port[g];}
  for(int ch=0;ch<2;++ch){
    grand::Vec3 a{};for(int h=0;h<3;++h)for(int g=0;g<3;++g)a[h]+=D[ch][g]*inverse[g][h];
    double norm2=0;
    for(size_t i=0;i<p.strings.size();++i){const auto& st=p.strings[i];const auto& m=st.m;for(size_t j=0;j<m.size();++j){const double value=-a[st.group]*alpha[i]*double(m.portOmega[j])/m.omega[j];norm2+=value*value;}}
    for(const auto& z:p.board){double value=0;for(int g=0;g<3;++g)value+=a[g]*result.beta[g]*z.port[g];norm2+=value*value;}
    result.dynamic[ch]=std::sqrt(result.dynamic[ch]);result.force[ch]=std::sqrt(norm2);result.combined[ch]=result.dynamic[ch]+result.force[ch];
  }
  return result;
}
Stereo forcePressure(const grand::Piano& p) {Stereo y{};for(const auto& z:p.board)for(int ch=0;ch<2;++ch)y[ch]+=z.force*z.mic[ch];return y;}
grand::Vec3 recoveredBridge(const grand::Piano& p) {
  grand::Vec3 rhs{},total{};for(const auto& z:p.board)for(int g=0;g<3;++g)rhs[g]-=z.port[g]*z.force;
  if(!grand::solve3(p.boardGram,rhs,total))throw std::runtime_error("Recover modal bridge force failed");return total;
}
std::vector<float> coordinates(const grand::Piano& p) {
  std::vector<float> out;for(const auto& st:p.strings){out.insert(out.end(),st.m.q.begin(),st.m.q.end());out.insert(out.end(),st.m.p.begin(),st.m.p.end());}for(const auto& z:p.board){out.push_back(z.q);out.push_back(z.p);}return out;
}
struct FullStats:Stats {
  uint64_t radDifferentBeforeV1=0,lateRadErrors=0;
  double maxRadAfterV1=0,maxZeroForcePressureOverBound=0;
};
double stepFull(grand::Piano& p,int note,double F,uint64_t frame,bool& active,FullStats& stats,double rho,double K,Stereo& rad,Stereo& body,Stereo& total,Stereo& force,double& preEnergy,double& zeroBound) {
  rad=body=total=force={};preEnergy=energy(p);zeroBound=2*K*std::sqrt(2*preEnergy);
  if(!active&&F!=0){active=true;++stats.wakes;}
  if(!active){++stats.skipped;return 0;}
  // This is a FUTURE zero-input bound. The preceding frame's actual force
  // feedthrough was already output; no current output is erased afterward.
  if(F==0&&zeroBound<=quietPressure){++stats.retirements;stats.retirementFrame=frame;stats.retiredEnergy=preEnergy;stats.discardedBound=zeroBound;clearCoordinates(p);active=false;++stats.skipped;return 0;}
  const double prior=scaleHistory(p,rho,stats);advance(p,note,F,frame);++stats.fastSteps;
  const double E=energy(p);rad=correction(p);body=board(p);total=full(p);force=forcePressure(p);
  if(F==0&&prior>0)stats.maxFreeEnergyRatio=std::max(stats.maxFreeEnergyRatio,E/prior);
  if(F==0&&zeroBound>0)for(double y:total)stats.maxZeroForcePressureOverBound=std::max(stats.maxZeroForcePressureOverBound,std::abs(y)/zeroBound);
  return E;
}
int main(int argc,char** argv) {
  if(argc!=3)return 2;grand::Options options;options.sampleRate=rate;grand::Piano fast(options);const auto bound=fullBound(fast);
  const double K=std::max(bound.combined[0],bound.combined[1]),rho=std::exp(-gammaFast/rate);
  if(fast.strings.size()!=230||fast.modeCount()!=17778||fast.board.size()!=475||!std::isfinite(K)||K<=0||!std::isfinite(bound.matrixFrobenius)||!std::isfinite(bound.inverseFrobenius)||bound.matrixFrobenius<=0||bound.inverseFrobenius<=0)return 2;
  for(double value:bound.beta)if(!std::isfinite(value)||value<0)return 2;
  for(int ch=0;ch<2;++ch)if(!std::isfinite(bound.dynamic[ch])||!std::isfinite(bound.force[ch])||!std::isfinite(bound.combined[ch])||bound.dynamic[ch]<=0||bound.force[ch]<0||bound.combined[ch]<=0)return 2;
  std::ofstream cold(std::string(argv[2])+"/bound.json");cold<<std::setprecision(17)<<"{\"dynamic_norm_LR\":["<<bound.dynamic[0]<<','<<bound.dynamic[1]<<"],\"force_norm_LR\":["<<bound.force[0]<<','<<bound.force[1]<<"],\"combined_norm_LR\":["<<bound.combined[0]<<','<<bound.combined[1]<<"],\"M_frobenius\":"<<bound.matrixFrobenius<<",\"M_inverse_frobenius\":"<<bound.inverseFrobenius<<",\"beta\":["<<bound.beta[0]<<','<<bound.beta[1]<<','<<bound.beta[2]<<"]}\n";cold.close();
  held(fast,60);bool active=false;FullStats synthetic;Stereo rad{},body{},total{},force{};double pre=0,future=0;
  stepFull(fast,60,1,event,active,synthetic,rho,K,rad,body,total,force,pre,future);
  const auto first=coordinates(fast);const auto firstOutput=total;uint64_t tick=1;
  while(active&&tick<100000){stepFull(fast,60,0,event+tick,active,synthetic,rho,K,rad,body,total,force,pre,future);++tick;}
  const bool retired=!active&&synthetic.retirements==1;
  for(int i=0;i<64;++i)stepFull(fast,60,0,event+tick+i,active,synthetic,rho,K,rad,body,total,force,pre,future);
  stepFull(fast,60,1,event+tick+64,active,synthetic,rho,K,rad,body,total,force,pre,future);const auto again=coordinates(fast);
  const bool wake=first.size()==again.size()&&!std::memcmp(first.data(),again.data(),first.size()*sizeof(float))&&firstOutput==total&&synthetic.wakes==2;
  std::ofstream syn(std::string(argv[2])+"/synthetic.json");syn<<std::setprecision(17)<<"{\"retired\":"<<(retired?"true":"false")<<",\"wake_identity\":"<<(wake?"true":"false")<<",\"max_free_energy_ratio\":"<<synthetic.maxFreeEnergyRatio<<",\"max_zero_force_pressure_over_bound\":"<<synthetic.maxZeroForcePressureOverBound<<",\"discarded_future_pressure_bound\":"<<synthetic.discardedBound<<",\"faults\":"<<fast.faultFlags<<"}\n";syn.close();
  if(!retired||!wake||synthetic.maxFreeEnergyRatio>1||synthetic.maxZeroForcePressureOverBound>1||fast.faultFlags)return 3;
  std::ifstream cases(argv[1]);std::string line;
  while(std::getline(cases,line)){
    if(line.empty())continue;std::istringstream row(line);std::string id,noteText,path,onsetText,proofPath,v1Path,retiredText,discardedText;
    std::getline(row,id,'\t');std::getline(row,noteText,'\t');std::getline(row,path,'\t');std::getline(row,onsetText,'\t');std::getline(row,proofPath,'\t');std::getline(row,v1Path,'\t');std::getline(row,retiredText,'\t');std::getline(row,discardedText,'\t');
    const int note=std::stoi(noteText),onset=std::stoi(onsetText),v1retired=std::stoi(retiredText);const double v1discard=std::stod(discardedText);
    std::ifstream input(path,std::ios::binary),proof(proofPath,std::ios::binary),v1(v1Path,std::ios::binary);const std::string folder=std::string(argv[2])+"/"+id;
    std::ofstream observer(folder+"/observer.f64le",std::ios::binary),baseline(folder+"/baseline.f32le",std::ios::binary),candidate(folder+"/candidate.f32le",std::ios::binary);
    if(!input||!proof||!v1||!observer||!baseline||!candidate)return 4;
    held(fast,note);active=false;FullStats stats;HP oldHP,newHP,counterHP;
    for(int frame=0;frame<frames;++frame){
      std::array<double,15> original{};std::array<double,16> oldComp{};std::array<uint64_t,3> sourceProof{};
      input.read(reinterpret_cast<char*>(original.data()),sizeof(original));v1.read(reinterpret_cast<char*>(oldComp.data()),sizeof(oldComp));proof.read(reinterpret_cast<char*>(sourceProof.data()),sizeof(sourceProof));if(!input||!proof||!v1)return 5;
      const double F=original[11];if(!std::isfinite(F)||F<0||(frame<event&&F!=0)||(frame>=event+1920&&F!=0))++stats.forceContractErrors;if(F!=0)stats.lastForceFrame=frame;
      const auto fh=forceHash(note,F,original);if(sourceProof[0]!=uint64_t(frame)||sourceProof[1]!=fh||sourceProof[2]!=fh)++stats.forceProofMismatch;
      const double E=stepFull(fast,note,F,frame,active,stats,rho,K,rad,body,total,force,pre,future);
      for(int ch=0;ch<2;++ch){if(frame<v1retired){if(std::memcmp(&rad[ch],&oldComp[2+ch],sizeof(double)))++stats.radDifferentBeforeV1;}else{stats.maxRadAfterV1=std::max(stats.maxRadAfterV1,std::abs(rad[ch]));if(std::abs(rad[ch])>v1discard)++stats.lateRadErrors;}}
      Stereo raw{{original[0],original[1]}},made{{original[0]-total[0],original[1]-total[1]}};auto before=oldHP.step(raw),after=newHP.step(made),counter=counterHP.step(total);
      std::array<float,2> b32{{float(before[0]),float(before[1])}},c32{{float(after[0]),float(after[1])}};
      grand::Vec3 bridge{};if(active)bridge=recoveredBridge(fast);
      std::array<double,23> data{{total[0],total[1],rad[0],rad[1],body[0],body[1],force[0],force[1],before[0],before[1],after[0],after[1],counter[0],counter[1],E,pre,future,F,made[0],made[1],bridge[0],bridge[1],bridge[2]}};
      for(double x:data)if(!std::isfinite(x))++stats.nonfinite;
      for(int ch=0;ch<2;++ch){stats.maxHPCommutation=std::max(stats.maxHPCommutation,std::abs(after[ch]-(before[ch]-counter[ch])));if(frame>=onset+12000)stats.maxFastHPAfterQuarter=std::max(stats.maxFastHPAfterQuarter,std::abs(counter[ch]));}
      observer.write(reinterpret_cast<const char*>(data.data()),sizeof(data));baseline.write(reinterpret_cast<const char*>(b32.data()),sizeof(b32));candidate.write(reinterpret_cast<const char*>(c32.data()),sizeof(c32));
    }
    char extra;if(input.read(&extra,1)||proof.read(&extra,1)||v1.read(&extra,1))return 6;
    std::ofstream report(folder+"/numeric.json");report<<std::setprecision(17)<<"{\"id\":\""<<id<<"\",\"frames\":"<<frames<<",\"gamma_per_second\":"<<gammaFast<<",\"mode_count\":"<<fast.modeCount()<<",\"board_modes\":"<<fast.board.size()<<",\"strings\":"<<fast.strings.size()<<",\"rad_nonidentical_samples_before_v1_retirement\":"<<stats.radDifferentBeforeV1<<",\"rad_post_v1_bound_errors\":"<<stats.lateRadErrors<<",\"max_rad_after_v1_retirement\":"<<stats.maxRadAfterV1<<",\"v1_retirement_frame\":"<<v1retired<<",\"v1_discarded_bound\":"<<v1discard<<",\"full_retirement_frame\":"<<stats.retirementFrame<<",\"discarded_future_pressure_bound\":"<<stats.discardedBound<<",\"max_zero_force_pressure_over_bound\":"<<stats.maxZeroForcePressureOverBound<<",\"max_free_energy_ratio\":"<<stats.maxFreeEnergyRatio<<",\"max_positive_scale_energy\":"<<stats.maxPositiveScaleEnergy<<",\"processed_frames\":"<<stats.fastSteps<<",\"skipped_frames\":"<<stats.skipped<<",\"retirements\":"<<stats.retirements<<",\"wakes\":"<<stats.wakes<<",\"nonfinite\":"<<stats.nonfinite<<",\"force_contract_errors\":"<<stats.forceContractErrors<<",\"force_proof_mismatches\":"<<stats.forceProofMismatch<<",\"HP_commutation_max_error\":"<<stats.maxHPCommutation<<",\"fast_HP_max_after_250ms\":"<<stats.maxFastHPAfterQuarter<<",\"faults\":"<<fast.faultFlags<<"}\n";
    std::cout<<id<<" full-pressure companion complete; pre-v1 rad mismatches="<<stats.radDifferentBeforeV1<<'\n'<<std::flush;
    if(stats.radDifferentBeforeV1||stats.lateRadErrors||stats.nonfinite||stats.forceContractErrors||stats.forceProofMismatch||stats.maxPositiveScaleEnergy>0||stats.maxFreeEnergyRatio>1||stats.maxZeroForcePressureOverBound>1||fast.faultFlags)return 7;
  }
  return 0;
}
