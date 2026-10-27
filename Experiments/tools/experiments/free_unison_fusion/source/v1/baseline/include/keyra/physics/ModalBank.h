#pragma once
#include <array>
#include <cmath>
#include <cstddef>

namespace keyra::physics {
// Mechanical coordinates: x=omega*q, v=qdot, with modal mass normalized to 1.
// Consequently E=.5*(x*x+v*v). Radiation weights never enter forces.
struct MechanicalMode {
  double x=0,v=0,omega=1,c=1,s=0,lossHalf=1,configuredLossHalf=1;
  double lossSigma=0,appliedForce=0,inverseStep=48000;
  unsigned partial=0,polarization=0;
  double contact=0,contactQ=0,forceX=0,forceV=0,forceCompliance=0;
  std::array<double,3> port{},portQ{};
  std::array<double,2> observation{},velocityObservation{},targetObservation{};
};
template<std::size_t Capacity> struct ModalBank {
  std::array<MechanicalMode,Capacity> modes{};
  std::size_t count=0;
  bool accelerationObserver=false;
  void clear() noexcept { for(std::size_t i=0;i<count;++i){modes[i].x=modes[i].v=0;modes[i].appliedForce=0;} }
  void freeStep(double extraHalf=1) noexcept {
    for(std::size_t i=0;i<count;++i){auto& m=modes[i];
      m.appliedForce=0;
      const double x=m.x,v=m.v*m.lossHalf*extraHalf;
      m.x=m.c*x+m.s*v;m.v=m.c*v-m.s*x;
    }
  }
  void finishLoss(double extraHalf=1) noexcept {
    for(std::size_t i=0;i<count;++i){auto& m=modes[i];m.v*=m.lossHalf*extraHalf;
      // Avoid subnormals without changing the caller's floating-point mode.
      if((m.x)<1.e-24&&(m.x)> -1.e-24&&(m.v)<1.e-24&&(m.v)> -1.e-24)m.x=m.v=0;
    }
  }
  double energy() const noexcept {double e=0;for(std::size_t i=0;i<count;++i){const auto& m=modes[i];e+=.5*(m.x*m.x+m.v*m.v);}return e;}
  double displacement() const noexcept {double q=0;for(std::size_t i=0;i<count;++i){const auto& m=modes[i];q+=m.contactQ*m.x;}return q;}
  double velocity() const noexcept {double v=0;for(std::size_t i=0;i<count;++i){const auto& m=modes[i];v+=m.contact*m.v;}return v;}
  double inverseMass() const noexcept {double a=0;for(std::size_t i=0;i<count;++i)a+=modes[i].contact*modes[i].contact;return a;}
  double forceCompliance() const noexcept {double a=0;for(std::size_t i=0;i<count;++i)a+=modes[i].forceCompliance;return a;}
  double contactImpulse(double impulse) noexcept {
    double work=0;for(std::size_t i=0;i<count;++i){auto& m=modes[i];const double d=m.contact*impulse;work+=m.v*d+.5*d*d;m.v+=d;}return work;
  }
  double contactForce(double force) noexcept {
    double work=0;for(std::size_t i=0;i<count;++i){auto& m=modes[i];const double dx=m.forceX*force,dv=m.forceV*force;work+=m.x*dx+m.v*dv+.5*(dx*dx+dv*dv);m.x+=dx;m.v+=dv;}return work;
  }
  std::array<double,3> portVelocity() const noexcept {
    std::array<double,3> v{};for(std::size_t i=0;i<count;++i)for(unsigned g=0;g<3;++g)v[g]+=modes[i].port[g]*modes[i].v;return v;
  }
  double portDisplacement(unsigned port) const noexcept {double q=0;if(port>=3)return q;for(std::size_t i=0;i<count;++i)q+=modes[i].portQ[port]*modes[i].x;return q;}
  double portImpulse(const std::array<double,3>& impulse) noexcept {
    double work=0;for(std::size_t i=0;i<count;++i){auto& m=modes[i];const double d=m.port[0]*impulse[0]+m.port[1]*impulse[1]+m.port[2]*impulse[2];work+=m.v*d+.5*d*d;m.v+=d;m.appliedForce+=d*m.inverseStep;}return work;
  }
  std::array<double,2> radiation() const noexcept {
    std::array<double,2> y{};
    if(accelerationObserver){for(std::size_t i=0;i<count;++i){const auto& m=modes[i];const double acceleration=-m.omega*m.x-2*m.lossSigma*m.v+m.appliedForce;y[0]+=m.observation[0]*acceleration;y[1]+=m.observation[1]*acceleration;}}
    else for(std::size_t i=0;i<count;++i){const auto& m=modes[i];y[0]+=m.observation[0]*m.x+m.velocityObservation[0]*m.v;y[1]+=m.observation[1]*m.x+m.velocityObservation[1]*m.v;}
    return y;
  }
};
} // namespace keyra::physics
