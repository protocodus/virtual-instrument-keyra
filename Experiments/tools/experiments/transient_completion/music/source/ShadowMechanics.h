#pragma once
#include "shadow/PreparedModel.h"
#include <array>
#include <cmath>
#include <vector>
namespace pitch_music {using Stereo=std::array<double,2>;
struct Stats {uint64_t nonfinite=0,fastSteps=0,skipped=0,wakes=0,retirements=0;long long retirementFrame=-1;double rhoLoss=0,maxPositiveScaleEnergy=0,maxFreeEnergyRatio=0,maxZeroForcePressureOverBound=0,retiredEnergy=0,discardedBound=0;};
double energy(const pitch_shadow::Piano& p) {
  double value=0;
  for(const auto& st:p.strings)value+=st.m.energy();
  for(const auto& z:p.board)value+=.5*z.w*z.w*(double(z.q)*z.q+double(z.p)*z.p);
  return value;
}
Stereo correction(const pitch_shadow::Piano& p) {
  Stereo out{};for(const auto& st:p.strings){auto r=st.cachedRadiation;out[0]+=r[0];out[1]+=r[1];}return out;
}
Stereo board(const pitch_shadow::Piano& p) {
  Stereo out{};for(const auto& z:p.board){const double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+z.force;for(int ch=0;ch<2;++ch)out[ch]+=acc*z.mic[ch];}return out;
}
Stereo full(const pitch_shadow::Piano& p) {
  auto out=board(p);for(const auto& st:p.strings){auto r=st.cachedRadiation;out[0]+=r[0];out[1]+=r[1];}return out;
}
void clearCoordinates(pitch_shadow::Piano& p) {
  for(auto& st:p.strings){std::fill(st.m.q.begin(),st.m.q.end(),0.f);std::fill(st.m.p.begin(),st.m.p.end(),0.f);st.cachedRadiation={};st.velocity=st.force=0;}
  for(auto& z:p.board){z.q=z.p=0;z.force=0;}
}
struct FullBound {
  Stereo dynamic{},force{},combined{};
  double inverseFrobenius=0,matrixFrobenius=0;
  pitch_shadow::Vec3 beta{};
};
FullBound fullBound(const pitch_shadow::Piano& p) {
  FullBound result;pitch_shadow::Vec3 D[2]{};std::vector<double> alpha(p.strings.size());
  for(size_t i=0;i<p.strings.size();++i){const auto& st=p.strings[i];const double r=st.resistance*p.opt.bridge;alpha[i]=r/(1+.5*p.dt*r*st.compliance);result.beta[st.group]+=alpha[i];}
  pitch_shadow::Mat3 M{},inverse{};
  for(int g=0;g<3;++g)for(int h=0;h<3;++h){M[g][h]=(g==h?1.:0.)+.5*p.dt*result.beta[g]*p.boardGram[g][h];result.matrixFrobenius+=M[g][h]*M[g][h];}
  for(int col=0;col<3;++col){pitch_shadow::Vec3 unit{},answer{};unit[col]=1;if(!pitch_shadow::solve3(M,unit,answer))return FullBound{};for(int row=0;row<3;++row){inverse[row][col]=answer[row];result.inverseFrobenius+=answer[row]*answer[row];}}
  result.matrixFrobenius=std::sqrt(result.matrixFrobenius);result.inverseFrobenius=std::sqrt(result.inverseFrobenius);
  for(const auto& st:p.strings){const auto& m=st.m;for(size_t j=0;j<m.size();++j){const double w=m.omega[j];result.dynamic[0]+=std::pow(double(m.radQL[j])/w,2)+std::pow(double(m.radPL[j])/w,2);result.dynamic[1]+=std::pow(double(m.radQR[j])/w,2)+std::pow(double(m.radPR[j])/w,2);}}
  for(const auto& z:p.board)for(int ch=0;ch<2;++ch){result.dynamic[ch]+=z.mic[ch]*z.mic[ch]*(z.w*z.w+4*z.sigma*z.sigma);for(int g=0;g<3;++g)D[ch][g]-=z.mic[ch]*z.port[g];}
  for(int ch=0;ch<2;++ch){
    pitch_shadow::Vec3 a{};for(int h=0;h<3;++h)for(int g=0;g<3;++g)a[h]+=D[ch][g]*inverse[g][h];
    double norm2=0;
    for(size_t i=0;i<p.strings.size();++i){const auto& st=p.strings[i];const auto& m=st.m;for(size_t j=0;j<m.size();++j){const double value=-a[st.group]*alpha[i]*double(m.portOmega[j])/m.omega[j];norm2+=value*value;}}
    for(const auto& z:p.board){double value=0;for(int g=0;g<3;++g)value+=a[g]*result.beta[g]*z.port[g];norm2+=value*value;}
    result.dynamic[ch]=std::sqrt(result.dynamic[ch]);result.force[ch]=std::sqrt(norm2);result.combined[ch]=result.dynamic[ch]+result.force[ch];
  }
  return result;
}
double scalePitch(pitch_shadow::Piano& p,const std::vector<double>& rhos,double bodyRho,Stats& stats) {
  const double before=energy(p);
  for(size_t i=0;i<p.strings.size();++i){auto& m=p.strings[i].m;const double rho=rhos[i];for(size_t j=0;j<m.size();++j){m.q[j]=double(m.q[j])*rho;m.p[j]=double(m.p[j])*rho;}}
  for(auto& z:p.board){z.q=double(z.q)*bodyRho;z.p=double(z.p)*bodyRho;}
  const double after=energy(p);stats.rhoLoss+=before-after;stats.maxPositiveScaleEnergy=std::max(stats.maxPositiveScaleEnergy,after-before);return before;
}
// Diagonal paired q/p loss. The order matches scalePitch exactly when fields
// are uniform within each string/body; no modal rotation or input B changes.
template<class PianoLike>
double scaleField(PianoLike& p,const std::vector<std::vector<double>>& rhos,
                  const std::vector<double>& bodyRhos,Stats& stats) {
  const double before=energy(p);
  for(size_t i=0;i<p.strings.size();++i){auto& m=p.strings[i].m;
    for(size_t j=0;j<m.size();++j){const double rho=rhos[i][j];
      m.q[j]=double(m.q[j])*rho;m.p[j]=double(m.p[j])*rho;}}
  for(size_t i=0;i<p.board.size();++i){auto& z=p.board[i];
    const double rho=bodyRhos[i];z.q=double(z.q)*rho;z.p=double(z.p)*rho;}
  const double after=energy(p);stats.rhoLoss+=before-after;
  stats.maxPositiveScaleEnergy=std::max(stats.maxPositiveScaleEnergy,after-before);
  return before;
}

}
