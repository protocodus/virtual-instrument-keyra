#pragma once
#include "ContactSolver.h"
#include "StrikeController.h"
#include "WaveguideString.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

namespace keyra::physics {

// Bounded, single-key 48 kHz coupling experiment. This is not the complete
// piano backend: secondary polarization, physical damper geometry and
// frequency-selective common-unison loss remain outside this interface proof.
class CoupledWaveguide {
public:
  static constexpr unsigned stringCapacity=3,boardCapacity=475;
  static constexpr double sampleRate=WaveguideString::sampleRate;
  static constexpr double h=WaveguideString::stepSeconds;
  using Vec3=std::array<double,3>;
  using Matrix3=std::array<Vec3,3>;
  struct BoardMode {
    double frequencyHz=100,sigma=0;
    Vec3 port{};
    std::array<double,2> microphone{};
  };
  struct Config {
    int note=60;
    unsigned stringCount=3,boardCount=0,bridgeGroup=1;
    std::array<WaveguideString::Config,stringCapacity> strings{};
    std::array<BoardMode,boardCapacity> board{};
    double hammerMass=.003,hammerStiffness=3.e8,hammerPower=2.5;
    double hammerLoss=.12,velocityExponent=1.55;
    double humanization=.65;
    uint32_t seed=0x4b657972u;
    bool coupling=true,observation=true,retireSeparatedHammer=true;
    // Authored shunt resistance at the existing hammer contact port. This is
    // not the geometry or body reaction of a real felt damper. Disabled keeps
    // the original coupled experiment's force arithmetic and output path.
    bool damperEnabled=false;
    double damperStrength=1,damperLiftSeconds=.001,damperReturnSeconds=.010;
  };
  struct Input {
    // Physical external forces, N; their work is recorded independently of
    // hammer-launch work. Default zero gives an unforced network after a strike.
    std::array<double,stringCapacity> stringForce{};
    Vec3 boardForce{};
  };
  struct Hammer {
    double position=-.012,velocity=0,stiffness=0,age=0;
    bool active=false;
  };
  struct Frame {
    bool valid=false;
    std::array<double,2> pressure{};
    double contactForce=0,contactResidual=0,contactLoss=0;
    double pathLoss=0,boardLoss=0,boardWork=0;
    double stringPortWork=0,externalWork=0,interactionResidual=0;
    double damperLoss=0,damperSolveResidual=0;
    std::array<double,stringCapacity> damperResistance{},damperForce{},contactVelocity{};
  };
  struct Ledger {
    uint64_t frames=0,launches=0,partialLaunches=0,retirements=0;
    uint64_t rejectedInputs=0,contactFaults=0,bridgeFaults=0;
    double launchWork=0,externalForceWork=0,retiredEnergy=0;
    double pathLoss=0,boardLoss=0,contactLoss=0,damperLoss=0;
    double maximumInteractionResidual=0,maximumContactResidual=0;
    double minimumContactLoss=0;
  };

  bool prepare(const Config& c) noexcept {
    if(c.note<21||c.note>108||c.stringCount<1||c.stringCount>stringCapacity||
       c.boardCount>boardCapacity||c.bridgeGroup>2||
       !range(c.hammerMass,1.e-6,1)||!range(c.hammerStiffness,0,1.e18)||
       !range(c.hammerPower,1,5)||!range(c.hammerLoss,0,100)||
       !range(c.velocityExponent,.1,8)||!range(c.humanization,0,1)||
       !range(c.damperStrength,0,100)||!range(c.damperLiftSeconds,1.e-5,10)||
       !range(c.damperReturnSeconds,1.e-5,10))return false;
    WaveguideString validation;
    for(unsigned i=0;i<c.stringCount;++i)if(!validation.prepare(c.strings[i]))return false;
    for(unsigned i=0;i<c.boardCount;++i) {
      const auto& b=c.board[i];
      if(!range(b.frequencyHz,1,.44*sampleRate)||!range(b.sigma,0,1.e5))return false;
      for(double p:b.port)if(!range(p,-100,100))return false;
      for(double p:b.microphone)if(!range(p,-1.e6,1.e6))return false;
    }
    StrikeConfig strike;strike.sampleRate=sampleRate;strike.variation=c.humanization;strike.seed=c.seed;
    // These bounded values are valid before committing any instance state.
    config_=c;(void)controller_.prepare(strike);gram_={};
    damperLiftRate_=1-std::exp(-h/c.damperLiftSeconds);
    damperReturnRate_=1-std::exp(-h/c.damperReturnSeconds);
    for(unsigned i=0;i<c.stringCount;++i)(void)strings_[i].prepare(c.strings[i]);
    for(unsigned i=0;i<c.boardCount;++i) {
      auto& b=board_[i];b.config=c.board[i];b.w=2*pi*b.config.frequencyHz;
      b.c=std::cos(b.w*h);b.s=std::sin(b.w*h);b.damp=std::exp(-b.config.sigma*h);
      for(unsigned a=0;a<3;++a)for(unsigned d=0;d<3;++d)
        gram_[a][d]+=b.config.port[a]*b.config.port[d];
    }
    prepared_=true;reset();return true;
  }
  void reset() noexcept {
    if(!prepared_)return;
    for(unsigned i=0;i<config_.stringCount;++i)(void)strings_[i].prepare(config_.strings[i]);
    for(unsigned i=0;i<config_.boardCount;++i)board_[i].q=board_[i].p=board_[i].force=0;
    controller_.reset();hammer_={};hammer_.position=-controller_.config().restDepth;
    hammer_.stiffness=config_.hammerStiffness;ledger_={};faulted_=false;
    keyDown_=false;pedal_=0;damperClosure_=1;
  }
  bool prepared() const noexcept {return prepared_;}
  bool noteOn(double velocity) noexcept {
    if(!prepared_||!range(velocity,0,1)){++ledger_.rejectedInputs;return false;}
    if(velocity==0){noteOff();return true;}
    if(!controller_.request(config_.note,velocity))return false;
    keyDown_=true;
    const auto launch=controller_.poll(config_.note,observation(),false);
    if(launch.valid)launchHammer(launch);
    return true;
  }
  void noteOff() noexcept {if(prepared_){controller_.release(config_.note);keyDown_=false;}}
  // Normalized pedal 1 means sustain pedal depressed, dampers lifted. Neither
  // control nor bypass resets any rail, board, displacement or loss ledger.
  bool setPedal(double pedal) noexcept {
    if(!prepared_||!range(pedal,0,1)){++ledger_.rejectedInputs;return false;}
    pedal_=pedal;return true;
  }
  void setDamperEnabled(bool enabled) noexcept {config_.damperEnabled=enabled;}
  double pedal() const noexcept {return pedal_;}
  double damperClosure() const noexcept {return damperClosure_;}
  double damperTargetClosure() const noexcept {return keyDown_?0:1-pedal_;}
  void setCouplingEnabled(bool enabled) noexcept {config_.coupling=enabled;}
  void setObservationEnabled(bool enabled) noexcept {config_.observation=enabled;}
  const Config& config() const noexcept {return config_;}
  const Hammer& hammer() const noexcept {return hammer_;}
  const Ledger& ledger() const noexcept {return ledger_;}
  const StrikeStatistics& strikeStatistics() const noexcept {return controller_.statistics();}
  const StrikeState& strikeState() const noexcept {return controller_.state(config_.note);}
  const WaveguideString& string(unsigned i) const noexcept {return strings_[i<stringCapacity?i:0];}
  double contactDisplacement() const noexcept {
    double y=0;for(unsigned i=0;i<config_.stringCount;++i)y+=strings_[i].contactDisplacement();
    return y/config_.stringCount;
  }
  double boardEnergy() const noexcept {
    double e=0;for(unsigned i=0;i<config_.boardCount;++i){const auto& b=board_[i];e+=.5*b.w*b.w*(b.q*b.q+b.p*b.p);}return e;
  }
  double stringEnergy() const noexcept {
    double e=0;for(unsigned i=0;i<config_.stringCount;++i)e+=strings_[i].energy();return e;
  }
  double energy() const noexcept {
    double e=stringEnergy()+boardEnergy();
    if(hammer_.active)e+=.5*config_.hammerMass*hammer_.velocity*hammer_.velocity+
      potential(hammer_.position-contactDisplacement(),hammer_.stiffness,config_.hammerPower);
    return e;
  }
  double balanceResidual() const noexcept {
    return energy()+ledger_.pathLoss+ledger_.boardLoss+ledger_.contactLoss+ledger_.damperLoss+ledger_.retiredEnergy-
      ledger_.launchWork-ledger_.externalForceWork;
  }
  Vec3 boardVelocity() const noexcept {
    Vec3 v{};for(unsigned i=0;i<config_.boardCount;++i){const auto& b=board_[i];for(unsigned g=0;g<3;++g)v[g]+=b.config.port[g]*b.w*b.p;}return v;
  }
  const Matrix3& boardGram() const noexcept {return gram_;}
  Frame step() noexcept {return step(Input{});}
  Frame step(const Input& input) noexcept {
    Frame result;
    if(!prepared_||faulted_)return result;
    for(double f:input.stringForce)if(!range(f,-1.e6,1.e6)){++ledger_.rejectedInputs;return result;}
    for(double f:input.boardForce)if(!range(f,-1.e6,1.e6)){++ledger_.rejectedInputs;return result;}

    if(config_.damperEnabled) {
      const double target=damperTargetClosure();
      damperClosure_+=(target<damperClosure_?damperLiftRate_:damperReturnRate_)*(target-damperClosure_);
      if(std::abs(target-damperClosure_)<1.e-10)damperClosure_=target;
    }

    if(controller_.requiresTick(config_.note)) {
      const auto launch=controller_.poll(config_.note,observation());
      if(launch.valid)launchHammer(launch);
      else if(!hammer_.active&&controller_.state(config_.note).hasLaunched) {
        const auto& s=controller_.state(config_.note);
        hammer_.position=contactDisplacement()-s.returnDepth;hammer_.velocity=-s.returnVelocity;
      }
    }
    const double weight=1./config_.stringCount;
    std::array<WaveguideString::Ports,stringCapacity> ports{};
    std::array<double,stringCapacity> freeContactVelocity{},contactMobility{};
    double yFree=0,contactCompliance=h*h/(2*config_.hammerMass);
    Vec3 source=input.boardForce,impedance{};
    for(unsigned i=0;i<config_.stringCount;++i) {
      ports[i]=strings_[i].ports();
      freeContactVelocity[i]=ports[i].contactVelocityFree+ports[i].contactForceMobility*input.stringForce[i];
      contactMobility[i]=ports[i].contactForceMobility;
      const double z=config_.strings[i].impedance;
      if(config_.damperEnabled)result.damperResistance[i]=2*z*config_.damperStrength*damperClosure_*damperClosure_;
      if(result.damperResistance[i]>0) {
        contactMobility[i]=1/(2*z+result.damperResistance[i]);
        freeContactVelocity[i]=(2*z*ports[i].contactVelocityFree+input.stringForce[i])*contactMobility[i];
      }
      yFree+=weight*(strings_[i].contactDisplacement()+h*freeContactVelocity[i]);
      contactCompliance+=h*weight*weight*contactMobility[i];
      if(config_.coupling) {
        impedance[config_.bridgeGroup]+=z;
        source[config_.bridgeGroup]+=2*z*ports[i].bridgeIncomingVelocity;
      }
    }
    const double oldCompression=hammer_.position-contactDisplacement();
    const double oldHammerEnergy=hammer_.active?.5*config_.hammerMass*hammer_.velocity*hammer_.velocity:0;
    const double oldPotential=hammer_.active?potential(oldCompression,hammer_.stiffness,config_.hammerPower):0;
    if(hammer_.active) {
      FullContactInput contact;contact.oldCompression=oldCompression;
      contact.freeCompression=hammer_.position+h*hammer_.velocity-yFree;
      contact.compliance=contactCompliance;contact.timeStep=h;contact.stiffness=hammer_.stiffness;
      contact.power=config_.hammerPower;contact.loss=config_.hammerLoss;
      const auto solved=solveFullContact(contact);
      if(!solved.valid){++ledger_.contactFaults;faulted_=true;return result;}
      result.contactForce=solved.force;result.contactResidual=solved.normalizedResidual;
      ledger_.maximumContactResidual=std::max(ledger_.maximumContactResidual,result.contactResidual);
      hammer_.position+=h*hammer_.velocity-h*h*solved.force/(2*config_.hammerMass);
      hammer_.velocity-=h*solved.force/config_.hammerMass;hammer_.age+=h;
    }

    for(unsigned i=0;i<config_.boardCount;++i) {
      auto& b=board_[i];const double old=b.p,v=old*b.damp,q=b.q;
      result.boardLoss+=.5*b.w*b.w*(old*old-v*v);
      b.q=b.c*q+b.s*v;const double rotated=b.c*v-b.s*q;b.p=rotated*b.damp;
      result.boardLoss+=.5*b.w*b.w*(rotated*rotated-b.p*b.p);
    }
    const Vec3 before=boardVelocity();Vec3 rhs=before,midpoint{};Matrix3 matrix{};
    for(unsigned g=0;g<3;++g)for(unsigned j=0;j<3;++j) {
      rhs[g]+=.5*h*gram_[g][j]*source[j];
      matrix[g][j]=(g==j?1.:0.)+.5*h*gram_[g][j]*impedance[j];
    }
    if(!solve(matrix,rhs,midpoint)){++ledger_.bridgeFaults;faulted_=true;return result;}
    Vec3 force{};for(unsigned g=0;g<3;++g) {
      force[g]=source[g]-impedance[g]*midpoint[g];
      result.boardWork+=h*force[g]*midpoint[g];
      result.externalWork+=h*input.boardForce[g]*midpoint[g];
    }
    for(unsigned i=0;i<config_.boardCount;++i) {
      auto& b=board_[i];b.force=0;for(unsigned g=0;g<3;++g)b.force+=b.config.port[g]*force[g];
      b.p+=h*b.force/b.w;
      if(config_.observation) {
        const double acceleration=-b.w*b.w*b.q-2*b.config.sigma*b.w*b.p+b.force;
        for(unsigned ch=0;ch<2;++ch)result.pressure[ch]+=acceleration*b.config.microphone[ch];
      }
    }
    for(unsigned i=0;i<config_.stringCount;++i) {
      double f=weight*result.contactForce+input.stringForce[i];
      const double predictedVelocity=freeContactVelocity[i]+weight*result.contactForce*contactMobility[i];
      if(result.damperResistance[i]>0) {
        result.damperForce[i]=-result.damperResistance[i]*predictedVelocity;
        f+=result.damperForce[i];
      }
      const auto response=strings_[i].step(f,config_.coupling?midpoint[config_.bridgeGroup]:0);
      if(!response.valid){faulted_=true;return result;}
      result.pathLoss+=response.dissipated;result.stringPortWork+=response.portWork;
      result.externalWork+=h*input.stringForce[i]*response.contactVelocity;
      result.contactVelocity[i]=response.contactVelocity;
      result.damperLoss+=h*result.damperResistance[i]*response.contactVelocity*response.contactVelocity;
      result.damperSolveResidual=std::max(result.damperSolveResidual,std::abs(response.contactVelocity-predictedVelocity));
    }
    if(hammer_.active) {
      const double newCompression=hammer_.position-contactDisplacement();
      const double delta=newCompression-oldCompression;
      const double newPotential=potential(newCompression,hammer_.stiffness,config_.hammerPower);
      const double g=gradient(oldCompression,newCompression,hammer_.stiffness,config_.hammerPower);
      const double factor=std::max(0.,1+config_.hammerLoss*delta/h);
      result.contactLoss=factor>0?g*config_.hammerLoss*delta*delta/h:-(newPotential-oldPotential);
      ledger_.minimumContactLoss=std::min(ledger_.minimumContactLoss,result.contactLoss);
      const double newHammerEnergy=.5*config_.hammerMass*hammer_.velocity*hammer_.velocity;
      result.interactionResidual=result.stringPortWork+result.boardWork+newHammerEnergy-oldHammerEnergy+
        newPotential-oldPotential+result.contactLoss+result.damperLoss-result.externalWork;
      if(config_.retireSeparatedHammer&&hammer_.velocity<0&&newCompression<-.002) {
        ledger_.retiredEnergy+=newHammerEnergy+newPotential;hammer_.active=false;++ledger_.retirements;
      }
    } else result.interactionResidual=result.stringPortWork+result.boardWork+result.damperLoss-result.externalWork;
    ledger_.pathLoss+=result.pathLoss;ledger_.boardLoss+=result.boardLoss;
    ledger_.contactLoss+=result.contactLoss;ledger_.externalForceWork+=result.externalWork;
    ledger_.damperLoss+=result.damperLoss;
    ledger_.maximumInteractionResidual=std::max(ledger_.maximumInteractionResidual,std::abs(result.interactionResidual));
    ++ledger_.frames;result.valid=true;return result;
  }

private:
  static constexpr double pi=3.14159265358979323846;
  struct BoardState {BoardMode config{};double q=0,p=0,force=0,w=0,c=1,s=0,damp=1;};
  Config config_{};std::array<WaveguideString,stringCapacity> strings_{};
  std::array<BoardState,boardCapacity> board_{};Matrix3 gram_{};
  StrikeController controller_{};Hammer hammer_{};Ledger ledger_{};
  bool prepared_=false,faulted_=false;
  bool keyDown_=false;
  double pedal_=0,damperClosure_=1,damperLiftRate_=0,damperReturnRate_=0;
  static bool range(double x,double low,double high) noexcept {return std::isfinite(x)&&x>=low&&x<=high;}
  static double potential(double x,double k,double p) noexcept {return x>0?k*std::pow(x,p+1)/(p+1):0;}
  static double gradient(double a,double b,double k,double p) noexcept {
    if(a<=0&&b<=0)return 0;
    if(a<=0)return potential(b,k,p)/(b-a);
    if(b<=0)return potential(a,k,p)/(a-b);
    if(a==b)return k*std::pow(a,p);
    const double hi=std::max(a,b),lo=std::min(a,b),t=(lo-hi)/hi;
    if(t<=-1)return k*std::pow(hi,p)/(p+1);
    return k*std::pow(hi,p)*std::expm1((p+1)*std::log1p(t))/((p+1)*t);
  }
  HammerObservation observation() const noexcept {return {hammer_.active,hammer_.position-contactDisplacement(),hammer_.velocity};}
  void launchHammer(const StrikeLaunch& launch) noexcept {
    // Controller admission never modifies a contacting/in-flight hammer.
    if(hammer_.active)return;
    if(!launch.preserveSeparatedPosition)hammer_.position=contactDisplacement()-.000015;
    hammer_.stiffness=config_.hammerStiffness*launch.hardnessFactor;
    hammer_.velocity=(.22+5.6*std::pow(launch.velocity,config_.velocityExponent))*
      launch.velocityFactor*launch.recoveryVelocityFactor;
    hammer_.age=0;hammer_.active=true;
    ledger_.launchWork+=.5*config_.hammerMass*hammer_.velocity*hammer_.velocity;
    ++ledger_.launches;if(launch.preserveSeparatedPosition)++ledger_.partialLaunches;
  }
  static bool solve(Matrix3 a,Vec3 b,Vec3& x) noexcept {
    for(unsigned k=0;k<3;++k) {
      unsigned pivot=k;for(unsigned j=k+1;j<3;++j)if(std::abs(a[j][k])>std::abs(a[pivot][k]))pivot=j;
      if(!std::isfinite(a[pivot][k])||std::abs(a[pivot][k])<1.e-24)return false;
      if(pivot!=k){const auto row=a[pivot];a[pivot]=a[k];a[k]=row;const double value=b[pivot];b[pivot]=b[k];b[k]=value;}
      for(unsigned j=k+1;j<3;++j){const double scale=a[j][k]/a[k][k];for(unsigned c=k;c<3;++c)a[j][c]-=scale*a[k][c];b[j]-=scale*b[k];}
    }
    for(int i=2;i>=0;--i){double sum=b[unsigned(i)];for(unsigned j=unsigned(i)+1;j<3;++j)sum-=a[unsigned(i)][j]*x[j];x[unsigned(i)]=sum/a[unsigned(i)][unsigned(i)];if(!std::isfinite(x[unsigned(i)]))return false;}
    return true;
  }
};
} // namespace keyra::physics
