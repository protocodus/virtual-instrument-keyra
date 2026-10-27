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
