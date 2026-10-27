#include "/workspace/virtual-instrument-keyra/out/full-transient-completion/train34/pitch_helpers.h"
int main(int argc,char** argv) {
  if(argc!=4)return 2;grand::Options options;options.sampleRate=rate;grand::Piano fast(options);
  const auto bound=fullBound(fast);const double K=std::max(bound.combined[0],bound.combined[1]);const double bodyRho=std::exp(-100./rate),reference=fast.keys[48-21].f0;
  if(fast.modeCount()!=17778||fast.strings.size()!=230||fast.board.size()!=475||!std::isfinite(K)||K<=0||!std::isfinite(reference)||reference<=0)return 2;
  for(int ch=0;ch<2;++ch)if(!std::isfinite(bound.dynamic[ch])||!std::isfinite(bound.force[ch])||!std::isfinite(bound.combined[ch])||bound.dynamic[ch]<=0||bound.force[ch]<0||bound.combined[ch]<=0)return 2;
  for(double value:bound.beta)if(!std::isfinite(value)||value<0)return 2;
  if(!std::isfinite(bound.matrixFrobenius)||!std::isfinite(bound.inverseFrobenius)||bound.matrixFrobenius<=0||bound.inverseFrobenius<=0)return 2;
  std::array<double,88> gamma{},keyRho{};std::vector<double> rhos,uniformRhos(fast.strings.size(),bodyRho);
  for(int i=0;i<88;++i){gamma[i]=100*std::max(1.,fast.keys[i].f0/reference);keyRho[i]=std::exp(-gamma[i]/rate);if(!std::isfinite(gamma[i])||gamma[i]<100||!std::isfinite(keyRho[i])||keyRho[i]<=0||keyRho[i]>bodyRho)return 2;}
  for(const auto& st:fast.strings)rhos.push_back(keyRho[st.note-21]);
  std::ofstream cold(std::string(argv[2])+"/bound-and-gamma.json");cold<<std::setprecision(17)<<"{\"f0_reference_C3\":"<<reference<<",\"body_gamma\":100,\"K_LR\":["<<bound.combined[0]<<','<<bound.combined[1]<<"],\"M_frobenius\":"<<bound.matrixFrobenius<<",\"M_inverse_frobenius\":"<<bound.inverseFrobenius<<",\"key_fields\":[";
  for(int i=0;i<88;++i){if(i)cold<<',';cold<<"{\"note\":"<<i+21<<",\"f0\":"<<fast.keys[i].f0<<",\"gamma\":"<<gamma[i]<<",\"rho\":"<<keyRho[i]<<'}';}cold<<"]}\n";cold.close();
  held(fast,60);bool active=false;FullStats synStats;Stereo rad{},body{},total{},force{};double pre=0,future=0;
  stepPitch(fast,60,1,event,active,synStats,rhos,bodyRho,K,rad,body,total,force,pre,future);const auto first=coordinates(fast);const auto firstOut=total;uint64_t tick=1;
  while(active&&tick<100000){stepPitch(fast,60,0,event+tick,active,synStats,rhos,bodyRho,K,rad,body,total,force,pre,future);++tick;}
  const bool retired=!active&&synStats.retirements==1;for(int i=0;i<64;++i)stepPitch(fast,60,0,event+tick+i,active,synStats,rhos,bodyRho,K,rad,body,total,force,pre,future);
  stepPitch(fast,60,1,event+tick+64,active,synStats,rhos,bodyRho,K,rad,body,total,force,pre,future);const auto again=coordinates(fast);
  const bool wake=first.size()==again.size()&&!std::memcmp(first.data(),again.data(),first.size()*sizeof(float))&&firstOut==total&&synStats.wakes==2;
  std::ofstream syn(std::string(argv[2])+"/synthetic.json");syn<<std::setprecision(17)<<"{\"retired\":"<<(retired?"true":"false")<<",\"wake_identity\":"<<(wake?"true":"false")<<",\"max_free_energy_ratio\":"<<synStats.maxFreeEnergyRatio<<",\"max_zero_force_pressure_over_bound\":"<<synStats.maxZeroForcePressureOverBound<<",\"discarded_future_bound\":"<<synStats.discardedBound<<",\"faults\":"<<fast.faultFlags<<"}\n";syn.close();
  if(!retired||!wake||synStats.maxFreeEnergyRatio>1||synStats.maxZeroForcePressureOverBound>1||fast.faultFlags)return 3;
  // Compare the prepared 88-key field and full pressure bound against the
  // qualified pilot BEFORE opening any new force/pressure input.
  std::ifstream actualCold(std::string(argv[2])+"/bound-and-gamma.json",std::ios::binary),expectedCold(argv[3],std::ios::binary);
  const std::string actualBytes((std::istreambuf_iterator<char>(actualCold)),{}),expectedBytes((std::istreambuf_iterator<char>(expectedCold)),{});
  if(actualBytes!=expectedBytes||actualBytes.empty())return 8;
  std::ifstream cases(argv[1]);std::string line;
  while(std::getline(cases,line)){
    if(line.empty())continue;std::istringstream row(line);std::string id,noteText,path,onsetText,proofPath;
    std::getline(row,id,'\t');std::getline(row,noteText,'\t');std::getline(row,path,'\t');std::getline(row,onsetText,'\t');std::getline(row,proofPath,'\t');
    const int note=std::stoi(noteText);const std::string folder=std::string(argv[2])+"/"+id;
    std::ifstream input(path,std::ios::binary),proof(proofPath,std::ios::binary);std::ofstream data(folder+"/fast.f64le",std::ios::binary);if(!input||!proof||!data)return 4;
    held(fast,note);active=false;FullStats stats;
    for(int frame=0;frame<frames;++frame){
      std::array<double,15> original{};std::array<uint64_t,3> sourceProof{};input.read(reinterpret_cast<char*>(original.data()),sizeof(original));proof.read(reinterpret_cast<char*>(sourceProof.data()),sizeof(sourceProof));if(!input||!proof)return 5;
      const double F=original[11];if(!std::isfinite(F)||F<0||(frame<event&&F!=0)||(frame>=event+1920&&F!=0))++stats.forceContractErrors;
      const auto fh=forceHash(note,F,original);if(sourceProof[0]!=uint64_t(frame)||sourceProof[1]!=fh||sourceProof[2]!=fh)++stats.forceProofMismatch;
      const double E=stepPitch(fast,note,F,frame,active,stats,rhos,bodyRho,K,rad,body,total,force,pre,future);grand::Vec3 own{};if(active)own=recoveredBridge(fast);
      const std::array<double,15> values{{total[0],total[1],rad[0],rad[1],body[0],body[1],force[0],force[1],E,pre,future,F,own[0],own[1],own[2]}};
      for(double x:values)if(!std::isfinite(x))++stats.nonfinite;data.write(reinterpret_cast<const char*>(values.data()),sizeof(values));
    }
    char extra;if(input.read(&extra,1)||proof.read(&extra,1))return 6;
    std::ofstream report(folder+"/numeric.json");report<<std::setprecision(17)<<"{\"id\":\""<<id<<"\",\"frames\":"<<frames<<",\"mode_count\":"<<fast.modeCount()<<",\"strings\":"<<fast.strings.size()<<",\"board_modes\":"<<fast.board.size()<<",\"max_positive_scale_energy\":"<<stats.maxPositiveScaleEnergy<<",\"max_free_energy_ratio\":"<<stats.maxFreeEnergyRatio<<",\"max_zero_force_pressure_over_bound\":"<<stats.maxZeroForcePressureOverBound<<",\"retirements\":"<<stats.retirements<<",\"retirement_frame\":"<<stats.retirementFrame<<",\"discarded_future_bound\":"<<stats.discardedBound<<",\"processed_frames\":"<<stats.fastSteps<<",\"skipped_frames\":"<<stats.skipped<<",\"nonfinite\":"<<stats.nonfinite<<",\"force_contract_errors\":"<<stats.forceContractErrors<<",\"force_proof_mismatches\":"<<stats.forceProofMismatch<<",\"faults\":"<<fast.faultFlags<<",\"new_uniform_prefix_control_run\":false,\"new_rho1_control_run\":false}\n";
    std::cout<<id<<" confirmation force replay complete\n"<<std::flush;
    if(stats.maxPositiveScaleEnergy>0||stats.maxFreeEnergyRatio>1||stats.maxZeroForcePressureOverBound>1||stats.nonfinite||stats.forceContractErrors||stats.forceProofMismatch||fast.faultFlags)return 7;
  }
  return 0;
}
