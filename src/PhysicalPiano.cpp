#include "keyra/PhysicalPiano.h"
#include "keyra/AnchorLookup.h"
#include "keyra/physics/ModalBank.h"
#include "keyra/physics/Bridge.h"
#include "keyra/physics/Materials.h"
#include "LiveCalibration.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>

namespace keyra {
namespace {
constexpr double pi=3.14159265358979323846;
bool validNote(int note) noexcept {return note>=21&&note<=108;}
double mix(double a,double b,double t) noexcept {return a+(b-a)*t;}
double logmix(double a,double b,double t) noexcept {return std::exp(mix(std::log(std::max(a,1.e-12)),std::log(std::max(b,1.e-12)),t));}
double anchor(int note,double a,double b,double c) noexcept {return note<=60?logmix(a,b,(note-36)/24.):logmix(b,c,(note-60)/36.);}
}
struct PhysicalPiano::Impl {
  using Strings=physics::ModalBank<modeCapacityPerKey>;
  using Board=physics::ModalBank<boardModeCapacity>;
  struct Hammer {double position=0,velocity=0,previous=0,free=0;uint32_t age=0;bool active=false;};
  std::array<Strings,keyCount> strings{};
  std::array<Hammer,keyCount> hammers{};
  Board board{};physics::PassiveBridge<keyCount> bridge{};
  std::array<double,keyCount> previous{},damperHalf{},hammerMass{};
  std::array<double,keyCount> resistanceWeights{};
  std::array<bool,keyCount> down{};
  double sampleRate=48000,dt=1./48000,pedal=0,resonance=.3;
  int soundboardWood=0;
  bool coupling=true,radiation=true,frameOpen=false,nonlinearHammer=false,mechanicalLoss=true,complexRadiation=true,referenceBoard=false;
  physics::ContactLaw hammerLaw{};
  ContactMetrics contactLedger{};

  void damping(std::size_t key) noexcept {
    const int note=int(key)+21;const double contact=down[key]||note>=89?0:1-pedal;
    const double sigma=(32.+.35*(note-21))*contact*contact;
    damperHalf[key]=std::exp(-sigma*dt);
  }
  void configureBridge() noexcept {(void)bridge.configure(strings,board,dt,coupling?.85*resonance*resonance*4:0,&resistanceWeights);buildRadiation();}
  std::array<std::complex<double>,2> radiationTransfer(double w,unsigned group,const std::array<double,3>& R) const noexcept {
    using C=std::complex<double>;using V=std::array<C,3>;using M=std::array<V,3>;
    M Y{},A{};std::array<V,2> T{};const C iw(0,w);
    for(std::size_t i=0;i<board.count;++i){const auto& mode=board.modes[i];const double sigma=mode.lossSigma;
      const C inverse=1./C(mode.omega*mode.omega-w*w,2*sigma*w);
      for(unsigned g=0;g<3;++g){for(unsigned h=0;h<3;++h)Y[g][h]+=iw*mode.port[g]*mode.port[h]*inverse;
        for(unsigned channel=0;channel<2;++channel)T[channel][g]+=(board.accelerationObserver?-w*w:mode.omega)*mode.observation[channel]*mode.port[g]*inverse;}
    }
    for(unsigned g=0;g<3;++g)for(unsigned h=0;h<3;++h)A[g][h]=(g==h?1.:0.)+R[g]*Y[g][h];
    V rhs{};rhs[group]=1.;
    for(unsigned k=0;k<3;++k){unsigned pivot=k;for(unsigned row=k+1;row<3;++row)if(std::norm(A[row][k])>std::norm(A[pivot][k]))pivot=row;
      if(std::norm(A[pivot][k])<1.e-28)return {};
      std::swap(A[k],A[pivot]);std::swap(rhs[k],rhs[pivot]);
      for(unsigned row=k+1;row<3;++row){const C ratio=A[row][k]/A[k][k];for(unsigned h=k;h<3;++h)A[row][h]-=ratio*A[k][h];rhs[row]-=ratio*rhs[k];}
    }
    V solution{};for(int k=2;k>=0;--k){C value=rhs[k];for(unsigned h=unsigned(k)+1;h<3;++h)value-=A[k][h]*solution[h];solution[k]=value/A[k][k];}
    std::array<C,2> out{};for(unsigned channel=0;channel<2;++channel)for(unsigned g=0;g<3;++g)out[channel]+=T[channel][g]*solution[g];return out;
  }
  void buildRadiation() noexcept {
    using C=std::complex<double>;std::array<double,3> R{};double totalR=0;
    for(std::size_t i=0;i<keyCount;++i){R[bridge.group[i]]+=bridge.resistance[i];totalR+=bridge.resistance[i];}
    // For an isolated-string ablation retain a fixed nominal board phase as
    // an observation only. Its actual base response is zero when disconnected.
    if(totalR==0)for(std::size_t i=0;i<keyCount;++i)if(strings[i].count)R[bridge.group[i]]+=.85*resistanceWeights[i];
    for(std::size_t key=0;key<keyCount;++key)for(std::size_t i=0;i<strings[key].count;++i){auto& mode=strings[key].modes[i];
      mode.velocityObservation={};if(!complexRadiation){mode.observation=mode.targetObservation;continue;}
      const auto H=radiationTransfer(mode.omega,bridge.group[key],R);
      const double actualR=bridge.resistance[key],phaseR=totalR>0?actualR:.85*resistanceWeights[key];
      std::array<C,2> phase{},base{};double norm=0;
      for(unsigned channel=0;channel<2;++channel){phase[channel]=C(0,phaseR*mode.port[0])*H[channel];base[channel]=C(0,actualR*mode.port[0])*H[channel];norm+=std::norm(phase[channel])*.5;}
      const double magnitude=std::sqrt(norm),target=.5*(mode.targetObservation[0]+mode.targetObservation[1]);
      for(unsigned channel=0;channel<2;++channel){const C desired=magnitude>1.e-14?phase[channel]*(target/magnitude):C(mode.targetObservation[channel],0);
        // The real board is observed once; replace only its modal steady-state
        // projection, retaining its driven transient and stereo complex phase.
        const C correction=desired-base[channel];mode.observation[channel]=correction.real();mode.velocityObservation[channel]=correction.imag();}
    }
  }
  void build() noexcept {
    for(int note=21;note<=108;++note){const std::size_t index=note-21;auto& bank=strings[index];bank.count=0;
      const auto bracket=anchorBracket(note,calibration::anchors.data(),calibration::anchors.size());
      const auto& a=calibration::anchors[bracket.lower];const auto& z=calibration::anchors[bracket.upper];
      const double t=(note-a.note)/double(z.note-a.note),u=std::clamp(t,0.,1.);
      const double ca=1200*std::log2(a.f1/(440*std::pow(2.,(a.note-69)/12.))),cz=1200*std::log2(z.f1/(440*std::pow(2.,(z.note-69)/12.)));
      const double f1=440*std::pow(2.,(note-69+std::clamp(mix(ca,cz,t),-40.,40.)/100)/12.);
      const double B=std::clamp(logmix(a.B,z.B,t),1.e-5,.04);
      const double length=std::min(2.03,anchor(note,1.90,.62,.09));
      double density=std::clamp(anchor(note,.0184,.0063,.0052),.004,.075);if(note<36)density*=std::pow(2.,(36-note)/19.);
      const unsigned choir=note<=31?1:note<=43?2:3;
      resistanceWeights[index]=referenceBoard?double(choir):1.;
      const double invMassScale=std::sqrt(2/(choir*density*length));
      const double strike=.116+.003*std::sin(note*.173),footprint=.008/length;
      hammerMass[index]=std::clamp(density*length*anchor(note,.14,.75,4.71),.0028,.012);
      for(unsigned j=1;j<=partialsPerKey;++j){const double fundamental=f1*j*std::sqrt((1+B*j*j)/(1+B));
        if(fundamental>=sampleRate*.44||fundamental>19000)break;
        for(unsigned polarization=0;polarization<2;++polarization){
          const double hz=fundamental*(polarization?std::pow(2.,.23/1200.):1.);
          if(hz>=sampleRate*.44||hz>19000)continue;
          auto& m=bank.modes[bank.count++];m={};m.partial=j-1;m.polarization=polarization;
          m.inverseStep=sampleRate;
          m.omega=2*pi*hz;m.c=std::cos(m.omega*dt);m.s=std::sin(m.omega*dt);
          const double sigma=polarization?
            std::clamp(logmix(a.decayLateHard[j-1],z.decayLateHard[j-1],u),.03,40.):
            std::clamp(logmix(a.decayHard[j-1],z.decayHard[j-1],u),.03,100.);
          m.configuredLossHalf=std::exp(-.85*sigma*dt);m.lossHalf=mechanicalLoss?m.configuredLossHalf:1.;m.lossSigma=mechanicalLoss?.85*sigma:0;
          m.contact=std::sin(pi*j*strike)*std::exp(-.5*std::pow(pi*j*footprint*.34,2))*invMassScale*(polarization?.035:1.);
          m.forceX=m.contact*(1-m.c)/m.omega;m.forceV=m.contact*m.s/m.omega;
          m.contactQ=m.contact/m.omega;m.forceCompliance=m.contact*m.forceX/m.omega;
          m.port[0]=(j&1?1.:-1.)*std::sqrt(2*.15*sigma/.85)*(polarization?.17:1.)/(referenceBoard?std::sqrt(double(choir)):1.);
        }
      }
      const double G=bank.inverseMass(),referenceSpeed=.22+5.6*std::pow(93./127.,.8);
      const double impulse=referenceSpeed/(1/hammerMass[index]+G);
      const double position=std::clamp((note-64.5)/52.,-.85,.85);
      for(std::size_t indexMode=0;indexMode<bank.count;++indexMode){auto& m=bank.modes[indexMode];const auto j=m.partial;
        // Fixed empirical observation is separate from force/energy. Positive
        // weights avoid manufacturing a hole when fitted branches trade mass.
        const double target=m.polarization?mix(a.amplitudeLateHard[j],z.amplitudeLateHard[j],u):mix(a.amplitudeHard[j],z.amplitudeHard[j],u);
        const double excitation=std::abs(m.contact*impulse);
        const double weight=std::min(300.,target/std::max(excitation,1.e-8));
        m.targetObservation={weight*(1-.35*position),weight*(1+.35*position)};
      }
    }
    board.count=0;board.accelerationObserver=referenceBoard;
    constexpr double xp[3]={.28,.51,.72},yp[3]={.42,.49,.56};
    const auto& wood=physics::materials::soundboard(static_cast<physics::materials::SoundboardWood>(soundboardWood));
    const auto plate=physics::materials::plateStiffness(wood,.0095);
    const double portMassScale=std::sqrt(4/(plate.massPerArea*2.02*1.32));
    // Published bulk wood moduli enter the orthotropic plate equation directly.
    // Thickness, boundaries, geometry and the positive 70Hz foundation proxy
    // remain authored; this is not a measured complete piano soundboard.
    const auto addBoardMode=[&](double hz,unsigned a,unsigned b,bool original) noexcept {
      if(hz>=sampleRate*.44||board.count>=boardModeCapacity)return;
      auto& m=board.modes[board.count++];m={};m.inverseStep=sampleRate;m.omega=2*pi*hz;m.c=std::cos(m.omega*dt);m.s=std::sin(m.omega*dt);
      const double sigma=(.018+.010*std::sqrt(hz/5000.))*m.omega*.5;
      m.configuredLossHalf=std::exp(-sigma*dt);m.lossHalf=mechanicalLoss?m.configuredLossHalf:1.;m.lossSigma=mechanicalLoss?sigma:0;
      for(unsigned g=0;g<3;++g){m.port[g]=(original?.55:portMassScale)*std::sin(pi*a*xp[g])*std::sin(pi*b*yp[g]);m.portQ[g]=m.port[g]/m.omega;}
      const double radiation=original?std::pow(hz/(hz+140),.7)/std::sqrt(1+std::pow(hz/8500.,4)):1.;
      for(unsigned ch=0;ch<2;++ch){const double ox=ch?.63:.37,oy=ch?.60:.39;
        m.observation[ch]=original?radiation*(.58*std::sin(pi*a*ox)*std::sin(pi*b*oy)+.42*((a&1)&&(b&1)?1.:0.)):.15*std::sin(pi*a*ox)*std::sin(pi*b*oy);}
    };
    if(referenceBoard){
      // Exact authored selector from immutable Research/GrandPianoV2/src/grand.cpp
      // (board build, imported by import-provenance.json). No source is modified.
      struct PlateMode {double frequency=0;unsigned a=0,b=0;};
      std::array<PlateMode,60*48> candidates{};std::size_t count=0;
      for(unsigned a=1;a<=60;++a)for(unsigned b=1;b<=48;++b){const double x=(a+.55)/2.02,y=(b+.55)/1.32;
        double hz=pi*.5*std::sqrt((1800*std::pow(x,4)+600*x*x*y*y+180*std::pow(y,4))/3.65);
        hz=std::sqrt(hz*hz+70*70);hz*=1+.018*std::sin(a*3.17+b*1.37);
        if(hz<13000)candidates[count++]={hz,a,b};
      }
      std::sort(candidates.begin(),candidates.begin()+count,[](const PlateMode& a,const PlateMode& b){return a.frequency<b.frequency;});
      double lastBand=-1;
      for(std::size_t i=0;i<count;++i){const auto& mode=candidates[i];const double band=std::floor((mode.frequency-1200)/32);
        if(mode.frequency<1200||band!=lastBand){addBoardMode(mode.frequency,mode.a,mode.b,true);lastBand=band;}}
    }else for(unsigned a=1;a<=8;++a)for(unsigned b=1;b<=6;++b){
      const double x=(a+.55)/2.02,y=(b+.55)/1.32;
      double hz=pi*.5*std::sqrt((plate.d11*x*x*x*x+2*(plate.d12+2*plate.d66)*x*x*y*y+plate.d22*y*y*y*y)/plate.massPerArea);hz=std::sqrt(hz*hz+70*70);
      addBoardMode(hz,a,b,false);
    }
    configureBridge();
  }
  double hammerStored(std::size_t index) const noexcept {
    const auto& hammer=hammers[index];if(!hammer.active)return 0;
    return .5*hammerMass[index]*hammer.velocity*hammer.velocity+
      physics::contactPotential(hammer.position-strings[index].displacement(),hammerLaw);
  }
  void hammerContacts() noexcept {
    for(std::size_t index=0;index<keyCount;++index){auto& hammer=hammers[index];if(!hammer.active)continue;
      auto& bank=strings[index];const double oldCompression=hammer.previous-previous[index];
      const double freeCompression=hammer.free-bank.displacement();
      const double hammerCompliance=.5*dt*dt/hammerMass[index];
      const auto result=physics::solveContact(oldCompression,freeCompression,
        hammerCompliance+bank.forceCompliance(),dt,hammerLaw);
      if(!result.valid){++contactLedger.invalidContacts;contactLedger.retiredHammerEnergy+=hammerStored(index);hammer.active=false;continue;}
      const double oldKinetic=.5*hammerMass[index]*hammer.velocity*hammer.velocity;
      const double oldPotential=physics::contactPotential(oldCompression,hammerLaw);
      const double stringWork=bank.contactForce(result.force);
      hammer.position=hammer.free-hammerCompliance*result.force;
      hammer.velocity-=dt*result.force/hammerMass[index];
      const double newKinetic=.5*hammerMass[index]*hammer.velocity*hammer.velocity;
      const double newPotential=physics::contactPotential(hammer.position-bank.displacement(),hammerLaw);
      const double residual=stringWork+newKinetic-oldKinetic+newPotential-oldPotential+result.dissipatedEnergy;
      contactLedger.maximumEnergyResidual=std::max(contactLedger.maximumEnergyResidual,residual<0?-residual:residual);
      const double forceResidual=result.residual<0?-result.residual:result.residual;
      contactLedger.maximumForceResidual=std::max(contactLedger.maximumForceResidual,forceResidual);
      contactLedger.dissipatedEnergy+=result.dissipatedEnergy;
      if(result.force>0)++contactLedger.contactFrames;
      ++hammer.age;
      if((hammer.velocity<0&&hammer.position<bank.displacement()-.002)||hammer.age>static_cast<uint32_t>(sampleRate*.05)){
        contactLedger.retiredHammerEnergy+=hammerStored(index);hammer.active=false;
      }
    }
  }
};
PhysicalPiano::PhysicalPiano():impl_(std::make_unique<Impl>()){(void)prepare(48000);}
PhysicalPiano::~PhysicalPiano()=default;
bool PhysicalPiano::prepare(double rate) noexcept {if(!std::isfinite(rate)||rate<8000||rate>384000)return false;impl_->sampleRate=rate;impl_->dt=1/rate;impl_->build();reset();return true;}
bool PhysicalPiano::setSoundboardMaterial(int material) noexcept {if(material<0||material>1)return false;if(impl_->soundboardWood==material)return true;impl_->soundboardWood=material;impl_->build();reset();return true;}
int PhysicalPiano::soundboardMaterial() const noexcept {return impl_->soundboardWood;}
double PhysicalPiano::boardModeFrequency(std::size_t mode) const noexcept {return mode<impl_->board.count?impl_->board.modes[mode].omega/(2*pi):0;}
std::size_t PhysicalPiano::boardModeCount() const noexcept {return impl_->board.count;}
void PhysicalPiano::setReferenceSoundboardEnabled(bool enabled) noexcept {if(impl_->referenceBoard==enabled)return;impl_->referenceBoard=enabled;impl_->build();reset();}
bool PhysicalPiano::referenceSoundboardEnabled() const noexcept {return impl_->referenceBoard;}
void PhysicalPiano::reset() noexcept {auto& p=*impl_;for(auto& key:p.strings)key.clear();p.board.clear();p.hammers={};p.down.fill(false);p.previous.fill(0);p.pedal=0;p.frameOpen=false;for(std::size_t i=0;i<keyCount;++i)p.damping(i);p.bridge.clearMetrics();p.contactLedger={};}
void PhysicalPiano::setKeyDown(int note,bool down) noexcept {if(!validNote(note))return;impl_->down[note-21]=down;impl_->damping(note-21);}
void PhysicalPiano::noteOn(int note,double velocity) noexcept {
  if(!validNote(note)||!std::isfinite(velocity))return;
  if(velocity<=0){noteOff(note);return;}
  setKeyDown(note,true);auto& p=*impl_;auto& bank=p.strings[note-21];
  const double speed=.22+5.6*std::pow(std::clamp(velocity,0.,1.),.8);
  if(p.nonlinearHammer){
    const auto index=std::size_t(note-21);auto& hammer=p.hammers[index];
    p.contactLedger.retiredHammerEnergy+=p.hammerStored(index);
    hammer={};hammer.active=true;hammer.position=bank.displacement()-.00005;hammer.velocity=speed;
    p.contactLedger.launchedEnergy+=.5*p.hammerMass[index]*speed*speed;return;
  }
  const double relative=speed-bank.velocity();
  // Perfectly inelastic instantaneous hammer collision. The hammer's outgoing
  // kinetic energy plus string energy cannot exceed their incoming total.
  if(relative>0)bank.contactImpulse(relative/(1/p.hammerMass[note-21]+bank.inverseMass()));
}
void PhysicalPiano::noteOff(int note) noexcept {setKeyDown(note,false);}
void PhysicalPiano::sustain(double position) noexcept {if(!std::isfinite(position))return;impl_->pedal=std::clamp(position,0.,1.);for(std::size_t i=0;i<keyCount;++i)impl_->damping(i);}
void PhysicalPiano::setResonance(double value) noexcept {if(!std::isfinite(value))return;impl_->resonance=std::clamp(value,0.,1.);impl_->configureBridge();}
void PhysicalPiano::setCouplingEnabled(bool enabled) noexcept {impl_->coupling=enabled;impl_->configureBridge();}
void PhysicalPiano::setNonlinearHammerEnabled(bool enabled) noexcept {impl_->nonlinearHammer=enabled;}
bool PhysicalPiano::setHammerContactLaw(const physics::ContactLaw& law) noexcept {if(!physics::solveContact(0,0,0,impl_->dt,law).valid)return false;impl_->hammerLaw=law;reset();return true;}
void PhysicalPiano::setMechanicalLossEnabled(bool enabled) noexcept {auto& p=*impl_;p.mechanicalLoss=enabled;for(auto& bank:p.strings)for(std::size_t i=0;i<bank.count;++i){auto& m=bank.modes[i];m.lossHalf=enabled?m.configuredLossHalf:1.;m.lossSigma=enabled?-std::log(m.configuredLossHalf)/p.dt:0;}for(std::size_t i=0;i<p.board.count;++i){auto& m=p.board.modes[i];m.lossHalf=enabled?m.configuredLossHalf:1.;m.lossSigma=enabled?-std::log(m.configuredLossHalf)/p.dt:0;}p.buildRadiation();}
void PhysicalPiano::setRadiationEnabled(bool enabled) noexcept {impl_->radiation=enabled;}
void PhysicalPiano::setComplexRadiationEnabled(bool enabled) noexcept {impl_->complexRadiation=enabled;impl_->buildRadiation();}
void PhysicalPiano::beginFrame() noexcept {auto& p=*impl_;if(p.frameOpen)return;p.frameOpen=true;for(std::size_t i=0;i<keyCount;++i){p.previous[i]=p.strings[i].displacement();p.strings[i].freeStep(p.damperHalf[i]);auto& h=p.hammers[i];if(h.active){h.previous=h.position;h.free=h.position+p.dt*h.velocity;h.position=h.free;}}p.board.freeStep();}
void PhysicalPiano::finishFrame() noexcept {auto& p=*impl_;if(!p.frameOpen)return;p.hammerContacts();for(std::size_t i=0;i<keyCount;++i)p.strings[i].finishLoss(p.damperHalf[i]);p.board.finishLoss();p.bridge.step(p.strings,p.board);p.frameOpen=false;}
void PhysicalPiano::observe(float& left,float& right) const noexcept {const auto& p=*impl_;
  if(!p.radiation){left=right=0;return;}const auto stems=observeStems();left=static_cast<float>(stems.primary[0]+stems.secondary[0]+stems.board[0]);right=static_cast<float>(stems.primary[1]+stems.secondary[1]+stems.board[1]);
}
PhysicalPiano::RadiationStems PhysicalPiano::observeStems() const noexcept {const auto& p=*impl_;RadiationStems stems{};if(!p.radiation)return stems;stems.board=p.board.radiation();for(auto& y:stems.board)y*=.5;for(const auto& bank:p.strings)for(std::size_t i=0;i<bank.count;++i){const auto& mode=bank.modes[i];auto& target=mode.polarization?stems.secondary:stems.primary;for(unsigned channel=0;channel<2;++channel)target[channel]+=.5*(mode.observation[channel]*mode.x+mode.velocityObservation[channel]*mode.v);}return stems;}
PhysicalPiano::QuadratureStems PhysicalPiano::observeQuadratureStems() const noexcept {const auto& p=*impl_;QuadratureStems out{};if(!p.radiation)return out;out.displacement.board=p.board.radiation();for(auto& y:out.displacement.board)y*=.5;for(const auto& bank:p.strings)for(std::size_t i=0;i<bank.count;++i){const auto& mode=bank.modes[i];auto& x=mode.polarization?out.displacement.secondary:out.displacement.primary;auto& v=mode.polarization?out.velocity.secondary:out.velocity.primary;for(unsigned channel=0;channel<2;++channel){x[channel]+=.5*mode.targetObservation[channel]*mode.x;v[channel]+=.5*mode.targetObservation[channel]*mode.v;}}return out;}
void PhysicalPiano::endFrame(float& left,float& right) noexcept {if(!impl_->frameOpen)beginFrame();finishFrame();observe(left,right);}
void PhysicalPiano::process(float* left,float* right,uint32_t frames) noexcept {if(!left||!right)return;for(uint32_t i=0;i<frames;++i){beginFrame();endFrame(left[i],right[i]);}}
double PhysicalPiano::keyPreviousDisplacement(int note) const noexcept {return validNote(note)?impl_->previous[note-21]:0;}
double PhysicalPiano::keyDisplacement(int note) const noexcept {return validNote(note)?impl_->strings[note-21].displacement():0;}
double PhysicalPiano::keyVelocity(int note) const noexcept {return validNote(note)?impl_->strings[note-21].velocity():0;}
double PhysicalPiano::keyInverseMass(int note) const noexcept {return validNote(note)?impl_->strings[note-21].inverseMass():0;}
double PhysicalPiano::contactCompliance(int note) const noexcept {return validNote(note)?impl_->strings[note-21].forceCompliance():0;}
double PhysicalPiano::keyImpulse(int note,double impulse) noexcept {return validNote(note)&&std::isfinite(impulse)?impl_->strings[note-21].contactImpulse(impulse):0;}
double PhysicalPiano::applyContactForce(int note,double force) noexcept {return validNote(note)&&std::isfinite(force)?impl_->strings[note-21].contactForce(force):0;}
double PhysicalPiano::boardDisplacement(unsigned port) const noexcept {return impl_->board.portDisplacement(port);}
double PhysicalPiano::boardVelocity(unsigned port) const noexcept {return port<3?impl_->board.portVelocity()[port]:0;}
double PhysicalPiano::boardInverseMass(unsigned port) const noexcept {return port<3?impl_->bridge.gram[port][port]:0;}
double PhysicalPiano::boardImpulse(unsigned port,double impulse) noexcept {if(port>=3||!std::isfinite(impulse))return 0;std::array<double,3> j{};j[port]=impulse;return impl_->board.portImpulse(j);}
double PhysicalPiano::keyEnergy(int note) const noexcept {return validNote(note)?impl_->strings[note-21].energy():0;}
double PhysicalPiano::boardEnergy() const noexcept {return impl_->board.energy();}
double PhysicalPiano::hammerEnergy() const noexcept {double e=0;for(std::size_t i=0;i<keyCount;++i)e+=impl_->hammerStored(i);return e;}
PhysicalPiano::ContactMetrics PhysicalPiano::contactMetrics() const noexcept {return impl_->contactLedger;}
double PhysicalPiano::energy() const noexcept {double e=impl_->board.energy()+hammerEnergy();for(const auto& key:impl_->strings)e+=key.energy();return e;}
PhysicalPiano::Metrics PhysicalPiano::metrics() const noexcept {const auto& b=impl_->bridge;return {b.maximumPositiveEnergyChange,b.maximumBalanceResidual,b.dissipatedEnergy};}
std::size_t PhysicalPiano::modeCount() const noexcept {std::size_t n=impl_->board.count;for(const auto& key:impl_->strings)n+=key.count;return n;}
} // namespace keyra
