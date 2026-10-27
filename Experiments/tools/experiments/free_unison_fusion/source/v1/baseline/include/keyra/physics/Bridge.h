#pragma once
#include "ModalBank.h"
#include <array>
#include <algorithm>
#include <cmath>

namespace keyra::physics {
// Passive reciprocal viscous connectors. Each string port connects to one of
// three board ports. The full simultaneous midpoint solve has a 3x3 Schur
// complement; it is not three independent feed-forward filters.
template<std::size_t KeyCount> struct PassiveBridge {
  using Vector=std::array<double,3>;
  using Matrix=std::array<Vector,3>;
  std::array<unsigned,KeyCount> group{};
  std::array<double,KeyCount> resistance{},coefficient{},portNorm{};
  Matrix gram{},inverse{};
  double dt=1./48000;
  double maximumPositiveEnergyChange=0,maximumBalanceResidual=0,dissipatedEnergy=0;

  template<std::size_t S,std::size_t B>
  bool configure(const std::array<ModalBank<S>,KeyCount>& keys,const ModalBank<B>& board,double step,double scale,
                 const std::array<double,KeyCount>* resistanceWeights=nullptr) noexcept {
    dt=step;gram={};Vector beta{};
    for(std::size_t m=0;m<board.count;++m)for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)gram[g][k]+=board.modes[m].port[g]*board.modes[m].port[k];
    for(std::size_t key=0;key<KeyCount;++key){
      group[key]=key+21<45?0:key+21<72?1:2;
      double norm=0;for(std::size_t m=0;m<keys[key].count;++m)norm+=keys[key].modes[m].port[0]*keys[key].modes[m].port[0];
      const double weight=resistanceWeights?std::clamp((*resistanceWeights)[key],0.,8.):1.;
      portNorm[key]=norm;resistance[key]=norm>0?std::clamp(scale,0.,8.)*weight:0;
      coefficient[key]=resistance[key]/(1+.5*dt*resistance[key]*norm);beta[group[key]]+=coefficient[key];
    }
    Matrix a{};inverse={};
    for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k){a[g][k]=(g==k?1.:0.)+.5*dt*beta[g]*gram[g][k];inverse[g][k]=g==k?1.:0.;}
    // Matrix is similar to positive definite I+.5*h*sqrt(beta)*H*sqrt(beta).
    for(unsigned k=0;k<3;++k){unsigned pivot=k;for(unsigned row=k+1;row<3;++row)if(std::abs(a[row][k])>std::abs(a[pivot][k]))pivot=row;
      if(!std::isfinite(a[pivot][k])||std::abs(a[pivot][k])<1.e-18)return false;
      std::swap(a[k],a[pivot]);std::swap(inverse[k],inverse[pivot]);const double inv=1/a[k][k];
      for(unsigned j=0;j<3;++j){a[k][j]*=inv;inverse[k][j]*=inv;}
      for(unsigned row=0;row<3;++row)if(row!=k){const double factor=a[row][k];for(unsigned j=0;j<3;++j){a[row][j]-=factor*a[k][j];inverse[row][j]-=factor*inverse[k][j];}}
    }
    return true;
  }
  void clearMetrics() noexcept {maximumPositiveEnergyChange=maximumBalanceResidual=dissipatedEnergy=0;}
  template<std::size_t S,std::size_t B>
  void step(std::array<ModalBank<S>,KeyCount>& keys,ModalBank<B>& board) noexcept {
    const auto boardV=board.portVelocity();Vector sum{},total{},correction{};
    std::array<double,KeyCount> force{};
    for(std::size_t key=0;key<KeyCount;++key){const double u=keys[key].portVelocity()[0];force[key]=-coefficient[key]*(u-boardV[group[key]]);sum[group[key]]+=force[key];}
    for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)total[g]+=inverse[g][k]*sum[k];
    for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)correction[g]+=.5*dt*gram[g][k]*total[k];
    double work=0,loss=0;
    for(std::size_t key=0;key<KeyCount;++key){force[key]-=coefficient[key]*correction[group[key]];work+=keys[key].portImpulse({dt*force[key],0,0});if(resistance[key]>0)loss+=dt*force[key]*force[key]/resistance[key];}
    work+=board.portImpulse({-dt*total[0],-dt*total[1],-dt*total[2]});
    maximumPositiveEnergyChange=std::max(maximumPositiveEnergyChange,work);
    const double residual=work+loss;maximumBalanceResidual=std::max(maximumBalanceResidual,residual<0?-residual:residual);
    dissipatedEnergy+=loss;
  }
};
} // namespace keyra::physics
