#pragma once
#include "PreparedModel.h"
#include <array>
#include <cmath>
#include <vector>

namespace keyra_causal {
using Vec=std::array<double,3>;using Mat=std::array<Vec,3>;
struct Result {
 bool valid=true;std::array<double,2> pressure{};Vec input{},force{},midpointVelocity{};
 double energyBefore=0,energyAfter=0,freeDissipation=0,loadDissipation=0,externalWork=0,balanceResidual=0;
};
// Separate linear observer. Original model states are read through const pointers;
// no state, force, damper, event or bridge feedback enters the physical instrument.
class Observer {
public:
 struct Node {double w=0,sigma=0,c=1,s=0,damp=1,readoutForce=1,x=0,v=0;Vec port{};std::array<double,2> mic{};};
 struct Driver {const float* state=nullptr;double coefficient=0;unsigned group=0;};
 std::vector<Node> nodes;std::vector<Driver> drivers;Vec resistance{};Mat gram{},inverse{};double h=0;uint64_t frames=0,faults=0;
 bool prepare(const grand::Piano& model) {
  h=model.dt;if(!std::isfinite(h)||h<=0)return false;
  nodes.clear();drivers.clear();nodes.reserve(model.board.size());drivers.reserve(model.modeCount());resistance={};gram={};
  for(const auto& st:model.strings){const double r=st.resistance*model.opt.bridge;if(r<0||!std::isfinite(r))return false;resistance[st.group]+=r;}
  for(const auto& z:model.board){Node n;n.w=z.w;n.sigma=z.sigma;n.c=z.c;n.s=z.s;n.damp=z.damp;n.port=z.port;n.mic=z.mic;
   const double sd=n.s*n.damp;const double den=(1-n.c)*(1-n.c*n.damp*n.damp)+sd*sd;
   if(!(den>0)||!std::isfinite(den)||!(n.w>0)||n.sigma<0)return false;
   const double staticX=h*sd/den,staticV=h*(1-n.c)/den;
   n.readoutForce=n.w*staticX+2*n.sigma*staticV;
   if(!std::isfinite(n.readoutForce))return false;nodes.push_back(n);
   for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)gram[g][k]+=n.port[g]*n.port[k];
  }
  for(const auto& st:model.strings){const double r=st.resistance*model.opt.bridge;const auto& m=st.m;grand::Cal cal(st.note);
   for(size_t j=0;j<m.size();++j){const auto H=model.radiationTransfer(m.omega[j],st.group);const double magnitude=std::sqrt((std::norm(H[0])+std::norm(H[1]))*.5);
    const double target=std::pow(10.,cal.mode(m.partial[j],m.polarization[j]?&piano_calibration::Anchor::radiationAfterDb:&piano_calibration::Anchor::radiationDb)/20.);
    double ratio=std::clamp(target/std::max(magnitude,1.e-8),.025,40.);if(m.partial[j]>64)ratio=1+(ratio-1)*std::exp(-(m.partial[j]-64)/24.);
    const double weight=r*double(m.b[j])*double(m.omega[j])*(ratio-1);if(!std::isfinite(weight))return false;
    drivers.push_back({&m.p[j],weight,unsigned(st.group)});
   }
  }
  if(!buildInverse())return false;reset();return true;
 }
 bool buildInverse() noexcept {
  Mat a{};for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)a[g][k]=(g==k?1.:0.)+.5*h*resistance[g]*gram[g][k];
  for(unsigned col=0;col<3;++col){Vec rhs{},answer{};rhs[col]=1;if(!grand::solve3(a,rhs,answer))return false;for(unsigned row=0;row<3;++row)inverse[row][col]=answer[row];}return true;
 }
 void reset() noexcept {for(auto& n:nodes)n.x=n.v=0;frames=faults=0;}
 Vec input() const noexcept {Vec u{};for(const auto& d:drivers)u[d.group]+=d.coefficient*double(*d.state);return u;}
 double energy() const noexcept {double e=0;for(const auto& n:nodes)e+=.5*(n.x*n.x+n.v*n.v);return e;}
 Result step() noexcept {return stepDriven(input());}
 Result stepDriven(const Vec& input) noexcept {
  Result out;out.input=input;for(double u:input)if(!std::isfinite(u)){out.valid=false;++faults;return out;}
  out.energyBefore=energy();Vec freeVelocity{};
  for(auto& n:nodes){const double x=n.x,v=n.v*n.damp;n.x=n.c*x+n.s*v;n.v=(n.c*v-n.s*x)*n.damp;
   for(unsigned g=0;g<3;++g)freeVelocity[g]+=n.port[g]*n.v;}
  const double freeEnergy=energy();out.freeDissipation=out.energyBefore-freeEnergy;
  Vec rhs{};for(unsigned g=0;g<3;++g)rhs[g]=input[g]-resistance[g]*freeVelocity[g];
  for(unsigned g=0;g<3;++g)for(unsigned k=0;k<3;++k)out.force[g]+=inverse[g][k]*rhs[k];
  for(unsigned g=0;g<3;++g){out.midpointVelocity[g]=freeVelocity[g];for(unsigned k=0;k<3;++k)out.midpointVelocity[g]+=.5*h*gram[g][k]*out.force[k];
   out.externalWork+=h*input[g]*out.midpointVelocity[g];out.loadDissipation+=h*resistance[g]*out.midpointVelocity[g]*out.midpointVelocity[g];}
  for(auto& n:nodes){double f=0;for(unsigned g=0;g<3;++g)f+=n.port[g]*out.force[g];n.v+=h*f;
   // Stationary-corrected endpoint acceleration. d0 uses ACTUAL stored F,
   // making a constant modal force give zero pressure at equilibrium.
   const double pressure=-n.w*n.x-2*n.sigma*n.v+n.readoutForce*f;
   for(unsigned ch=0;ch<2;++ch)out.pressure[ch]+=n.mic[ch]*pressure;}
  out.energyAfter=energy();out.balanceResidual=out.energyAfter-freeEnergy+out.loadDissipation-out.externalWork;
  for(double y:out.pressure)out.valid=out.valid&&std::isfinite(y);out.valid=out.valid&&std::isfinite(out.energyAfter)&&out.energyAfter>=0;
  ++frames;if(!out.valid)++faults;return out;
 }
};
}
