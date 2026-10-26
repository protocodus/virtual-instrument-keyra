#include "keyra/physics/Action.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace keyra::physics {
namespace {
bool finite(double x) noexcept {
#if defined(__GNUC__) || defined(__clang__)
  return __builtin_isfinite(x);
#else
  return std::isfinite(x);
#endif
}
double absValue(double x) noexcept {return x<0?-x:x;}
double positive(double x) noexcept {return x>0?x:0;}
bool validLaw(const ContactLaw& law) noexcept {
  return finite(law.stiffness)&&law.stiffness>=0&&law.stiffness<=1.e18&&
         finite(law.exponent)&&law.exponent>=1&&law.exponent<=5&&
         finite(law.dissipation)&&law.dissipation>=0&&law.dissipation<=10;
}
double power(double x,double exponent) noexcept {
  if(x<=0)return 0;
  if(exponent==1)return x;
  if(exponent==2)return x*x;
  if(exponent==3)return x*x*x;
  return std::pow(x,exponent);
}
double discreteForce(double a,double b,const ContactLaw& law) noexcept {
  if(a<=0&&b<=0)return 0;
  const double difference=b-a;
  // The midpoint limit avoids cancellation of nearly equal contact potentials.
  // Its work defect is third order in this already sub-relative-ulp interval.
  if(absValue(difference)<=1.e-9*std::max(1.e-9,std::max(absValue(a),absValue(b))))
    return law.stiffness*power(positive(.5*(a+b)),law.exponent);
  return (contactPotential(b,law)-contactPotential(a,law))/difference;
}
double linearContactForce(double a,double b,double stiffness) noexcept {
  if(a<=0&&b<=0)return 0;
  if(a>=0&&b>=0)return stiffness*.5*(a+b);
  const double difference=b-a;
  if(difference==0)return stiffness*positive(a);
  return .5*stiffness*(positive(b)*positive(b)-positive(a)*positive(a))/difference;
}
double dampedLinearContact(double a,double b,double stiffness,double damping,double dt) noexcept {
  if(a<=0&&b<=0)return 0;
  return positive(linearContactForce(a,b,stiffness)+damping*(b-a)/dt);
}
double contactTangent(double a,double b,double stiffness,double damping,double dt) noexcept {
  if(a<=0&&b<=0)return 0;
  const double force=linearContactForce(a,b,stiffness)+damping*(b-a)/dt;
  if(force<=0)return 0;
  double slope=.5*stiffness;
  if(a<0&&b>0) {
    const double difference=b-a;
    slope=.5*stiffness*b*(b-2*a)/(difference*difference);
  } else if(a>0&&b<0) {
    const double difference=a-b;
    slope=.5*stiffness*a*a/(difference*difference);
  }
  return slope+damping/dt;
}
bool validNote(int note) noexcept {return note>=21&&note<=108;}
bool inRange(double value,double low,double high) noexcept {
  return finite(value)&&value>=low&&value<=high;
}
}

double contactPotential(double compression,const ContactLaw& law) noexcept {
  return compression<=0?0:law.stiffness*power(compression,law.exponent+1)/(law.exponent+1);
}
ContactResult solveContact(double oldCompression,double freeCompression,
                           double compliance,double dt,const ContactLaw& law) noexcept {
  ContactResult result{};
  result.compression=freeCompression;
  if(!validLaw(law)||!finite(oldCompression)||!finite(freeCompression)||
     absValue(oldCompression)>1||absValue(freeCompression)>1||
     !inRange(compliance,0,1.e6)||!inRange(dt,1.e-8,.02)) {
    result.valid=false;return result;
  }
  if(law.stiffness==0||(oldCompression<=0&&freeCompression<=0))return result;
  const auto elastic=[&](double force) noexcept {
    const double next=freeCompression-compliance*force;
    return discreteForce(oldCompression,next,law)*
      positive(1+law.dissipation*(next-oldCompression)/dt);
  };
  const double initial=elastic(0);
  if(!finite(initial)||initial<0){result.valid=false;return result;}
  double low=0,high=std::max(1.e-12,initial);
  // The elastic target decreases with F for nonnegative compliance. Thus
  // F=target(0) is a bracket, without an unbounded expansion or allocation.
  for(unsigned iteration=0;iteration<56;++iteration) {
    const double mid=.5*(low+high);
    const double residual=mid-elastic(mid);
    if(residual>0)high=mid;else low=mid;
    ++result.iterations;
    if(high-low<=2.e-13*(1+high))break;
  }
  result.force=.5*(low+high);
  result.compression=freeCompression-compliance*result.force;
  result.residual=result.force-elastic(result.force);
  const double potentialChange=contactPotential(result.compression,law)-contactPotential(oldCompression,law);
  result.dissipatedEnergy=result.force*(result.compression-oldCompression)-potentialChange;
  // Roundoff at conservative contact may be a tiny negative value; expose
  // only genuine dissipation here, while tests check the independent work law.
  if(result.dissipatedEnergy<0&&result.dissipatedEnergy> -1.e-12)result.dissipatedEnergy=0;
  result.valid=finite(result.force)&&finite(result.compression)&&finite(result.residual)&&
    finite(result.dissipatedEnergy)&&absValue(result.residual)<=1.e-9*(1+result.force)&&
    result.dissipatedEnergy>= -1.e-10;
  return result;
}

Action::Action() noexcept {coefficients();reset();}
bool Action::prepare(double rate) noexcept {
  if(!inRange(rate,8000,384000))return false;
  sampleRate_=rate;dt_=1/rate;coefficients();reset();return true;
}
bool Action::configure(const ActionConfig& c) noexcept {
  if(!inRange(c.keyMass,.005,1)||!inRange(c.hammerMass,.001,.1)||
     !inRange(c.keyTravel,.003,.025)||!inRange(c.hammerStroke,.015,.1)||
     !inRange(c.leverRatio,1,10)||!inRange(c.escapementFraction,.3,.95)||
     c.leverRatio*c.keyTravel*c.escapementFraction>c.hammerStroke-.001||
     !inRange(c.keyReturnStiffness,1,1000)||!inRange(c.keyDamping,0,10)||
     !inRange(c.hammerReturnStiffness,.01,100)||!inRange(c.hammerDamping,0,1)||
     !inRange(c.fingerStiffness,10,1.e7)||!inRange(c.keybedStiffness,100,1.e9)||
     !inRange(c.fingerDamping,0,1000)||!inRange(c.keybedDamping,0,10000)||
     !inRange(c.fingerOvertravel,0,.005)||!inRange(c.backcheckDistance,.002,.03)||
     c.backcheckDistance>=c.hammerStroke||!validLaw(c.hammerContact))return false;
  config_=c;coefficients();reset();return true;
}
void Action::coefficients() noexcept {
  hammerOmega_=std::sqrt(config_.hammerReturnStiffness/config_.hammerMass);
  const double phase=hammerOmega_*dt_;
  hammerCos_=std::cos(phase);hammerSin_=std::sin(phase);
  // sin(phase/2)^2 is accurate even for a tiny return-spring phase.
  const double halfSine=std::sin(.5*phase);
  hammerCompliance_=2*halfSine*halfSine/config_.hammerReturnStiffness;
  hammerForceVelocity_=hammerSin_/(config_.hammerMass*hammerOmega_);
  hammerHalfDamp_=std::exp(-.5*config_.hammerDamping*dt_/config_.hammerMass);
}
void Action::reset() noexcept {
  for(auto& key:keys_) {
    key=Key{};key.state.hammerPosition=-config_.hammerStroke;
    key.state.jackEngaged=config_.jackEnabled;
    key.oldHammer=key.freeHammer=key.state.hammerPosition;
  }
  ledger_={};frameOpen_=false;
}
void Action::press(int note,double velocity) noexcept {
  if(!validNote(note)||!finite(velocity))return;
  if(velocity<=0){release(note);return;}
  auto& key=keys_[unsigned(note-21)];key.live=true;key.state.down=true;
  key.fingerTarget=config_.keyTravel+config_.fingerOvertravel;
  key.fingerSpeed=.08+.9*std::pow(std::clamp(velocity,0.,1.),1.4);
}
void Action::release(int note) noexcept {
  if(!validNote(note))return;
  auto& key=keys_[unsigned(note-21)];if(!key.live)return;
  key.state.down=false;key.fingerTarget=0;
  key.fingerSpeed=1;key.live=true;
}
void Action::setFingerTarget(int note,double position,double speed) noexcept {
  if(!validNote(note)||!finite(position)||!inRange(speed,.001,10))return;
  auto& key=keys_[unsigned(note-21)];
  key.fingerTarget=std::clamp(position,0.,config_.keyTravel+config_.fingerOvertravel);
  key.fingerSpeed=speed;key.state.down=key.fingerTarget>0;key.live=true;
}
void Action::advanceKey(Key& key) noexcept {
  auto& s=key.state;
  const double fingerOld=s.fingerPosition;
  const double fingerChange=std::clamp(key.fingerTarget-fingerOld,-key.fingerSpeed*dt_,key.fingerSpeed*dt_);
  const double fingerNew=fingerOld+fingerChange;
  const double xOld=s.keyPosition,vOld=s.keyVelocity;
  const bool driven=s.jackEngaged&&config_.jackEnabled;
  const double ratio=driven?config_.leverRatio:0;
  const double mass=config_.keyMass+ratio*ratio*config_.hammerMass;
  const double stiffness=config_.keyReturnStiffness+ratio*ratio*config_.hammerReturnStiffness;
  const double damping=config_.keyDamping+ratio*ratio*config_.hammerDamping;
  const double compliance=.5*dt_*dt_/mass;
  const double fingerK=config_.fingerEnabled?config_.fingerStiffness:0;
  const double bedK=config_.keybedEnabled?config_.keybedStiffness:0;
  const double fingerD=config_.fingerEnabled?config_.fingerDamping:0;
  const double bedD=config_.keybedEnabled?config_.keybedDamping:0;
  const auto force=[&](double next) noexcept {
    const double finger=dampedLinearContact(fingerOld-xOld,fingerNew-next,fingerK,fingerD,dt_);
    const double bed=dampedLinearContact(xOld-config_.keyTravel,next-config_.keyTravel,bedK,bedD,dt_);
    return finger-bed-stiffness*.5*(xOld+next)-damping*(next-xOld)/dt_;
  };
  const double free=xOld+dt_*vOld;
  double low=std::min({xOld,free,fingerNew,0.})-.1;
  double high=std::max({xOld,free,fingerNew,config_.keyTravel})+.1;
  // Almost every step stays in one linear contact region, so one Newton step
  // is exact there. Safeguarding retains the monotone root across unilateral
  // contact transitions, with bounded bisection only for a difficult crossing.
  double next=std::clamp(free,low,high);
  bool solved=false;
  for(unsigned i=0;i<12;++i) {
    const double residual=next-free-compliance*force(next);
    if(absValue(residual)<5.e-17){solved=true;break;}
    if(residual>0)high=next;else low=next;
    const double tangent=1+compliance*(
      contactTangent(fingerOld-xOld,fingerNew-next,fingerK,fingerD,dt_)+
      contactTangent(xOld-config_.keyTravel,next-config_.keyTravel,bedK,bedD,dt_)+
      .5*stiffness+damping/dt_);
    const double candidate=next-residual/tangent;
    next=candidate>low&&candidate<high?candidate:.5*(low+high);
  }
  if(!solved) {
    for(unsigned i=0;i<48;++i) {
      next=.5*(low+high);
      if(next-free-compliance*force(next)>0)high=next;else low=next;
    }
    next=.5*(low+high);
  }
  const double midVelocity=(next-xOld)/dt_;
  s.keyPosition=next;s.keyVelocity=2*midVelocity-vOld;s.fingerPosition=fingerNew;
  const double fingerA=fingerOld-xOld,fingerB=fingerNew-next;
  const double bedA=xOld-config_.keyTravel,bedB=next-config_.keyTravel;
  s.fingerForce=dampedLinearContact(fingerA,fingerB,fingerK,fingerD,dt_);
  s.keybedForce=dampedLinearContact(bedA,bedB,bedK,bedD,dt_);
  ledger_.fingerWork+=s.fingerForce*fingerChange;
  ledger_.viscousDissipation+=damping*midVelocity*midVelocity*dt_;
  ledger_.fingerDissipation+=s.fingerForce*(fingerB-fingerA)-
    .5*fingerK*(positive(fingerB)*positive(fingerB)-positive(fingerA)*positive(fingerA));
  ledger_.keybedDissipation+=s.keybedForce*(bedB-bedA)-
    .5*bedK*(positive(bedB)*positive(bedB)-positive(bedA)*positive(bedA));
  if(driven) {
    s.hammerPosition=-config_.hammerStroke+ratio*next;
    s.hammerVelocity=ratio*s.keyVelocity;
    s.stage=ActionStage::Driven;
    if(s.keyPosition>=config_.keyTravel*config_.escapementFraction&&s.hammerVelocity>0) {
      s.jackEngaged=false;s.stage=ActionStage::Escaped;
    }
  }
}
void Action::beginFrame() noexcept {
  if(frameOpen_)return;
  frameOpen_=true;
  for(auto& key:keys_) {
    if(!key.live)continue;
    auto& s=key.state;
    key.contactSolved=false;s.hammerForce=0;
    key.flightStep=!s.jackEngaged&&s.stage!=ActionStage::Backchecked;
    key.oldHammer=s.hammerPosition;
    advanceKey(key);
    if(key.flightStep) {
      const double oldV=s.hammerVelocity;
      s.hammerVelocity*=hammerHalfDamp_;
      ledger_.viscousDissipation+=.5*config_.hammerMass*(oldV*oldV-s.hammerVelocity*s.hammerVelocity);
      const double q=s.hammerPosition+config_.hammerStroke,v=s.hammerVelocity;
      s.hammerPosition=-config_.hammerStroke+hammerCos_*q+hammerSin_*v/hammerOmega_;
      s.hammerVelocity=hammerCos_*v-hammerSin_*hammerOmega_*q;
      s.stage=s.hammerVelocity<0?ActionStage::Returning:ActionStage::Escaped;
    }
    key.freeHammer=s.hammerPosition;
  }
}
ContactResult Action::solveStringContact(int note,const ContactPort& port) noexcept {
  ContactResult result{};
  if(!validNote(note)||!frameOpen_){result.valid=false;return result;}
  auto& key=keys_[unsigned(note-21)];
  if(!key.live)return result;
  if(key.contactSolved){result.valid=false;return result;}
  key.contactSolved=true;
  if(!key.flightStep||!config_.hammerContactEnabled)return result;
  if(!finite(port.oldDisplacement)||!finite(port.freeDisplacement)||!inRange(port.forceCompliance,0,1.e6)) {
    result.valid=false;return result;
  }
  result=solveContact(key.oldHammer-port.oldDisplacement,
                      key.freeHammer-port.freeDisplacement,
                      hammerCompliance_+port.forceCompliance,dt_,config_.hammerContact);
  if(!result.valid)return result;
  key.state.hammerPosition=key.freeHammer-hammerCompliance_*result.force;
  key.state.hammerVelocity-=hammerForceVelocity_*result.force;
  key.state.hammerForce=result.force;
  if(result.force>0)key.state.stage=ActionStage::Contact;
  ledger_.contactDissipation+=result.dissipatedEnergy;
  ledger_.maximumContactResidual=std::max(ledger_.maximumContactResidual,absValue(result.residual)/(1+result.force));
  ledger_.contactSolves+=result.iterations?1:0;
  return result;
}
void Action::catchAndReset(Key& key) noexcept {
  auto& s=key.state;
  const double rest=-config_.hammerStroke;
  if(!s.jackEngaged&&s.stage==ActionStage::Backchecked&&!s.down)s.stage=ActionStage::Returning;
  if(!s.jackEngaged&&config_.backcheckEnabled&&s.down&&s.hammerVelocity<0&&
     key.oldHammer> -config_.backcheckDistance&&s.hammerPosition<= -config_.backcheckDistance) {
    const double before=.5*config_.hammerMass*s.hammerVelocity*s.hammerVelocity+
      .5*config_.hammerReturnStiffness*(s.hammerPosition-rest)*(s.hammerPosition-rest);
    const double caught=-config_.backcheckDistance;
    const double after=.5*config_.hammerReturnStiffness*(caught-rest)*(caught-rest);
    if(before>=after) {
      ledger_.catchDissipation+=before-after;s.hammerPosition=caught;s.hammerVelocity=0;s.stage=ActionStage::Backchecked;
    }
  }
  if(!s.jackEngaged&&s.hammerPosition<rest) {
    ledger_.catchDissipation+=.5*config_.hammerMass*s.hammerVelocity*s.hammerVelocity+
      .5*config_.hammerReturnStiffness*(s.hammerPosition-rest)*(s.hammerPosition-rest);
    s.hammerPosition=rest;s.hammerVelocity=0;
  }
  if(!s.down&&absValue(s.keyPosition)<1.e-5&&absValue(s.keyVelocity)<.005&&
     absValue(s.hammerPosition-rest)<1.e-5&&absValue(s.hammerVelocity)<.005&&s.fingerPosition==0) {
    const auto before=energy(int(&key-keys_.data())+21).total();
    s=ActionState{};s.hammerPosition=rest;s.jackEngaged=config_.jackEnabled;
    ledger_.catchDissipation+=before;key.live=false;
  }
}
void Action::endFrame() noexcept {
  if(!frameOpen_)return;
  for(auto& key:keys_) {
    if(!key.live)continue;
    auto& s=key.state;
    if(key.flightStep) {
      const double oldV=s.hammerVelocity;s.hammerVelocity*=hammerHalfDamp_;
      ledger_.viscousDissipation+=.5*config_.hammerMass*(oldV*oldV-s.hammerVelocity*s.hammerVelocity);
    }
    catchAndReset(key);
  }
  frameOpen_=false;
}
ActionState Action::state(int note) const noexcept {
  return validNote(note)?keys_[unsigned(note-21)].state:ActionState{};
}
ActionEnergy Action::energy(int note) const noexcept {
  ActionEnergy e{};if(!validNote(note))return e;
  const auto& s=keys_[unsigned(note-21)].state;
  e.keyKinetic=.5*config_.keyMass*s.keyVelocity*s.keyVelocity;
  e.keyReturn=.5*config_.keyReturnStiffness*s.keyPosition*s.keyPosition;
  e.keybed=config_.keybedEnabled?.5*config_.keybedStiffness*power(positive(s.keyPosition-config_.keyTravel),2):0;
  e.fingerContact=config_.fingerEnabled?.5*config_.fingerStiffness*power(positive(s.fingerPosition-s.keyPosition),2):0;
  e.hammerKinetic=.5*config_.hammerMass*s.hammerVelocity*s.hammerVelocity;
  const double hammerOffset=s.hammerPosition+config_.hammerStroke;
  e.hammerReturn=.5*config_.hammerReturnStiffness*hammerOffset*hammerOffset;
  return e;
}
double Action::energy() const noexcept {
  double value=0;for(unsigned i=0;i<keyCount;++i)value+=energy(int(i)+21).total();return value;
}
bool Action::active(int note) const noexcept {return validNote(note)&&keys_[unsigned(note-21)].live;}
} // namespace keyra::physics
