#include "/workspace/virtual-instrument-keyra/out/full-transient-completion/pitch-scaled-v1/mechanics_v2_prefix.h"

double scalePitch(grand::Piano& p,const std::vector<double>& rhos,double bodyRho,Stats& stats) {
  const double before=energy(p);
  for(size_t i=0;i<p.strings.size();++i){auto& m=p.strings[i].m;const double rho=rhos[i];for(size_t j=0;j<m.size();++j){m.q[j]=double(m.q[j])*rho;m.p[j]=double(m.p[j])*rho;}}
  for(auto& z:p.board){z.q=double(z.q)*bodyRho;z.p=double(z.p)*bodyRho;}
  const double after=energy(p);stats.rhoLoss+=before-after;stats.maxPositiveScaleEnergy=std::max(stats.maxPositiveScaleEnergy,after-before);return before;
}
double stepPitch(grand::Piano& p,int note,double F,uint64_t frame,bool& active,FullStats& stats,const std::vector<double>& rhos,double bodyRho,double K,Stereo& rad,Stereo& body,Stereo& total,Stereo& force,double& pre,double& future) {
  rad=body=total=force={};pre=future=0;
  // Inactive coordinates were initialized/cleared to exactly zero. Avoid the
  // unnecessary full energy scan; the uniform compatibility check covers this.
  if(!active&&F==0){++stats.skipped;return 0;}
  pre=energy(p);future=2*K*std::sqrt(2*pre);
  if(!active&&F!=0){active=true;++stats.wakes;}
  if(F==0&&future<=quietPressure){++stats.retirements;stats.retirementFrame=frame;stats.retiredEnergy=pre;stats.discardedBound=future;clearCoordinates(p);active=false;++stats.skipped;return 0;}
  const double prior=scalePitch(p,rhos,bodyRho,stats);advance(p,note,F,frame);++stats.fastSteps;
  const double E=energy(p);rad=correction(p);body=board(p);total=full(p);force=forcePressure(p);
  if(F==0&&prior>0)stats.maxFreeEnergyRatio=std::max(stats.maxFreeEnergyRatio,E/prior);
  if(F==0&&future>0)for(double y:total)stats.maxZeroForcePressureOverBound=std::max(stats.maxZeroForcePressureOverBound,std::abs(y)/future);
  return E;
}
