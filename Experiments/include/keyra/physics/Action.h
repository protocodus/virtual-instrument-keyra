#pragma once
#include <array>
#include <cstdint>

namespace keyra::physics {

// Compression is positive. Stiffness has units N/m^exponent; dissipation is
// seconds/metre in the nonnegative Hunt-Crossley factor. These are effective
// contact parameters, not an identification of a particular felt specimen.
struct ContactLaw {
  double stiffness=8.e8;
  double exponent=2.5;
  double dissipation=.08;
};
struct ContactPort {
  double oldDisplacement=0;   // metres, before the current free mechanical step
  double freeDisplacement=0;  // metres, after that step and before contact force
  double forceCompliance=0;   // metres/newton for a constant force over the step
};
struct ContactResult {
  double force=0;
  double compression=0;
  double residual=0;
  double dissipatedEnergy=0;
  unsigned iterations=0;
  bool valid=true;
};

double contactPotential(double compression,const ContactLaw&) noexcept;
// Solve F = DG(Phi)(oldCompression, freeCompression-compliance*F) *
// max(0,1+dissipation*(newCompression-oldCompression)/dt). With dissipation=0,
// a compatible exact constant-force mechanical port cancels contact work.
ContactResult solveContact(double oldCompression,double freeCompression,
                           double totalCompliance,double dt,const ContactLaw&) noexcept;

enum class ActionStage : uint8_t { Rest, Driven, Escaped, Contact, Returning, Backchecked };
struct ActionConfig {
  double keyMass=.050;               // kg, effective mass at the key front
  double hammerMass=.008;            // kg, effective translational hammer mass
  double keyTravel=.010;             // m, nominal top-to-bed distance
  double hammerStroke=.045;          // m, rest-to-string distance
  double leverRatio=4.5;             // hammer displacement / key displacement
  double escapementFraction=.80;     // fraction of key travel
  double keyReturnStiffness=35;       // N/m
  double keyDamping=.15;              // N s/m
  double hammerReturnStiffness=1;     // N/m, reduced return potential
  double hammerDamping=.002;          // N s/m
  double fingerStiffness=6000;        // N/m; kinematic driver, not a rigid key reset
  double fingerDamping=8;             // N s/m, non-adhesive contact loss
  double keybedStiffness=200000;      // N/m, effective compressed bed cushion
  double keybedDamping=45;            // N s/m, non-adhesive cushion loss
  double fingerOvertravel=.0005;     // m beyond nominal bed
  double backcheckDistance=.012;     // m behind string plane
  ContactLaw hammerContact{};
  bool fingerEnabled=true;
  bool keybedEnabled=true;
  bool jackEnabled=true;
  bool hammerContactEnabled=true;
  bool backcheckEnabled=true;
};
struct ActionState {
  double fingerPosition=0;
  double keyPosition=0,keyVelocity=0;
  double hammerPosition=0,hammerVelocity=0;
  double fingerForce=0,keybedForce=0,hammerForce=0;
  bool down=false,jackEngaged=true;
  ActionStage stage=ActionStage::Rest;
};
struct ActionEnergy {
  double keyKinetic=0,keyReturn=0,keybed=0,fingerContact=0;
  double hammerKinetic=0,hammerReturn=0;
  double total() const noexcept {
    return keyKinetic+keyReturn+keybed+fingerContact+hammerKinetic+hammerReturn;
  }
};
struct ActionLedger {
  double fingerWork=0;
  double viscousDissipation=0;
  double fingerDissipation=0;
  double keybedDissipation=0;
  double catchDissipation=0;
  double contactDissipation=0;
  double maximumContactResidual=0;
  uint64_t contactSolves=0;
};

// A reduced, independently testable action candidate. All arrays are fixed-size.
// MIDI press/release drives an authored finite-speed finger trajectory; it is
// not measured finger motion. Configuration is offline: it resets all states.
class Action {
public:
  static constexpr unsigned keyCount=88;
  Action() noexcept;
  bool prepare(double sampleRate) noexcept;
  bool configure(const ActionConfig&) noexcept;
  const ActionConfig& configuration() const noexcept { return config_; }
  void reset() noexcept;
  void press(int note,double velocity) noexcept;
  void release(int note) noexcept;
  // Explicit kinematic input for isolated finger/key experiments. The target
  // is bounded to the configured action travel, and speed is metres/second.
  void setFingerTarget(int note,double position,double speed) noexcept;
  void beginFrame() noexcept;
  // Call once per note after the mechanical network's beginFrame(), then apply
  // the returned force once to the network's exact constant-force port.
  ContactResult solveStringContact(int note,const ContactPort&) noexcept;
  void endFrame() noexcept;
  ActionState state(int note) const noexcept;
  ActionEnergy energy(int note) const noexcept;
  double energy() const noexcept;
  const ActionLedger& ledger() const noexcept { return ledger_; }
  bool active(int note) const noexcept;
  bool frameOpen() const noexcept { return frameOpen_; }
private:
  struct Key {
    ActionState state{};
    double fingerTarget=0,fingerSpeed=1;
    double oldHammer=0,freeHammer=0;
    bool live=false,flightStep=false,contactSolved=false;
  };
  ActionConfig config_{};
  std::array<Key,keyCount> keys_{};
  ActionLedger ledger_{};
  double sampleRate_=48000,dt_=1./48000;
  double hammerCos_=1,hammerSin_=0,hammerOmega_=1;
  double hammerCompliance_=0,hammerForceVelocity_=0,hammerHalfDamp_=1;
  bool frameOpen_=false;
  void coefficients() noexcept;
  void advanceKey(Key&) noexcept;
  void catchAndReset(Key&) noexcept;
};
} // namespace keyra::physics
