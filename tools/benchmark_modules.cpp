#include "keyra/PhysicalInstrument.h"
#include "keyra/physics/ModalBank.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
constexpr double pi=3.14159265358979323846;
constexpr unsigned block=64;
struct Settings { double rate=48000; unsigned frames=12032; };
struct Timing {
  double meanMs=0,p95Ms=0,maxMs=0,finalEnergy=0;
  unsigned callbacks=0,deadlineMisses=0;
  bool finite=true;
};
struct Row {
  std::string name,implementation,scope,fixture;
  Timing timing{};
  std::vector<std::pair<std::string,double>> witnesses;
  bool activated=false;
  Row(std::string n,std::string i,std::string s,std::string f)
    :name(std::move(n)),implementation(std::move(i)),scope(std::move(s)),fixture(std::move(f)) {}
};
bool isFinite(double value) { return std::isfinite(value); }
void require(bool good,const char* message) { if(!good)throw std::runtime_error(message); }
void maximum(double& target,double value) { target=std::max(target,std::abs(value)); }

// Setup and the activation-witness pass are excluded from callback timing. The
// second pass repeats the same input, so diagnostic energy scans do not inflate
// a module's timing. The final timed energy remains observable to prevent DCE.
template<class Initialize,class Advance,class Energy,class Inspect>
Timing measure(const Settings& settings,Initialize initialize,Advance advance,
               Energy energy,Inspect inspect) {
  initialize();
  std::vector<double> times;
  times.reserve((settings.frames+block-1)/block);
  using Clock=std::chrono::steady_clock;
  for(unsigned first=0;first<settings.frames;first+=block) {
    const unsigned last=std::min(first+block,settings.frames);
    const auto start=Clock::now();
    for(unsigned frame=first;frame<last;++frame)advance(frame);
    times.push_back(std::chrono::duration<double,std::milli>(Clock::now()-start).count());
  }
  Timing result;
  result.finalEnergy=energy();
  result.finite=isFinite(result.finalEnergy);
  result.callbacks=static_cast<unsigned>(times.size());
  const double deadline=1000*block/settings.rate;
  for(double time:times) {
    result.meanMs+=time/times.size();
    if(time>deadline)++result.deadlineMisses;
  }
  std::sort(times.begin(),times.end());
  result.maxMs=times.back();
  result.p95Ms=times[std::min(times.size()-1,static_cast<std::size_t>(.95*times.size()))];
  initialize();
  for(unsigned frame=0;frame<settings.frames;++frame) {
    advance(frame);
    result.finite=inspect(frame)&&result.finite;
  }
  return result;
}

Row action(const Settings& settings,const std::string& name,bool bed,bool jack,bool release) {
  keyra::physics::Action module;
  keyra::physics::ActionConfig config;
  config.keybedEnabled=bed;config.jackEnabled=jack;
  config.hammerContactEnabled=false;config.backcheckEnabled=jack;
  require(module.configure(config)&&module.prepare(settings.rate),"Action setup failed");
  double travel=0,fingerForce=0,bedForce=0,hammerSpeed=0,energy=0;
  bool escaped=false;
  const unsigned releaseFrame=settings.frames/2;
  const auto initialize=[&] { module.reset();module.press(60,.85); };
  const auto advance=[&](unsigned frame) {
    if(release&&frame==releaseFrame)module.release(60);
    module.beginFrame();module.endFrame();
  };
  const auto inspect=[&](unsigned) {
    const auto state=module.state(60);
    maximum(travel,state.keyPosition);maximum(fingerForce,state.fingerForce);
    maximum(bedForce,state.keybedForce);maximum(hammerSpeed,state.hammerVelocity);
    maximum(energy,module.energy());escaped=escaped||!state.jackEngaged;
    return isFinite(state.keyPosition)&&isFinite(state.keyVelocity)&&isFinite(state.hammerPosition)
      &&isFinite(state.hammerVelocity)&&isFinite(state.fingerForce)&&isFinite(state.keybedForce)
      &&isFinite(module.energy());
  };
  Row row{name,"physics::Action","Physical ablation in the shared reduced action solver",
          "One prescribed MIDI-to-finger trajectory; no strings/contact solver or acoustics. Key/bed/hammer coefficients are effective authored action inputs."};
  row.timing=measure(settings,initialize,advance,[&]{return module.energy();},inspect);
  const auto ledger=module.ledger();const auto last=module.state(60);
  row.witnesses={{"maximum_key_travel_m",travel},{"maximum_finger_force_n",fingerForce},
    {"maximum_keybed_force_n",bedForce},{"maximum_hammer_speed_m_per_s",hammerSpeed},
    {"maximum_stored_energy_j",energy},{"finger_work_j",ledger.fingerWork},
    {"viscous_dissipation_j",ledger.viscousDissipation},
    {"keybed_dissipation_j",ledger.keybedDissipation},{"release_return_travel_m",travel-last.keyPosition},
    {"jack_escaped",escaped?1.:0.},{"hammer_contact_enabled",0.}};
  row.activated=travel>1e-4&&fingerForce>0;
  if(bed)row.activated=row.activated&&bedForce>0;
  if(jack)row.activated=row.activated&&escaped&&hammerSpeed>0;
  if(release)row.activated=row.activated&&(travel-last.keyPosition)>1e-4;
  return row;
}

Row contact(const Settings& settings) {
  const keyra::physics::ContactLaw law{};
  keyra::physics::ContactResult result;
  double force=0,residual=0,dissipation=0,iterations=0;
  const auto advance=[&](unsigned frame) {
    // Deliberately imposed compression, not a fabricated piano performance.
    const double compression=.00015+.00002*double(frame%64)/63.;
    result=keyra::physics::solveContact(compression,compression+.5/settings.rate,
                                      1e-8,1/settings.rate,law);
  };
  Row row{"hammer_felt_contact_kernel","physics::solveContact",
          "Scalar nonlinear contact kernel in isolation",
          "Prescribed positive compression and finite constant-force compliance. Contact-law inputs are effective felt proxies, not measured wool bulk properties."};
  row.timing=measure(settings,[]{},advance,[&]{return result.dissipatedEnergy;},[&](unsigned) {
    maximum(force,result.force);maximum(residual,result.residual);
    dissipation+=result.dissipatedEnergy;iterations+=result.iterations;
    return result.valid&&isFinite(result.force)&&isFinite(result.residual)&&isFinite(result.dissipatedEnergy);
  });
  row.witnesses={{"maximum_contact_force_n",force},{"maximum_force_residual_n",residual},
    {"mean_solver_iterations",iterations/settings.frames},{"reported_contact_dissipation_j",dissipation}};
  row.activated=force>0&&iterations>0;
  return row;
}

Row modalKernel(const Settings& settings) {
  keyra::physics::ModalBank<32> bank;
  bank.count=32;
  for(unsigned i=0;i<bank.count;++i) {
    auto& mode=bank.modes[i];const double order=i+1.;
    mode.omega=2*pi*110*order*std::sqrt((1+.0003*order*order)/1.0003);
    mode.c=std::cos(mode.omega/settings.rate);mode.s=std::sin(mode.omega/settings.rate);
    mode.lossHalf=std::exp(-(.2+.01*order)/settings.rate);
    mode.contact=std::sin(pi*.12*order);mode.contactQ=mode.contact/mode.omega;
  }
  double peak=0,initial=0;
  const auto initialize=[&]{bank.clear();bank.contactImpulse(.001);initial=bank.energy();};
  Row row{"isolated_string_modal_kernel","physics::ModalBank<32>",
          "Computational kernel isolation: one 32-mode bank, no other modules",
          "Synthetic 110 Hz stiff-string fixture with unit-normalized modal masses; not a calibrated complete piano or a copy of its constructor."};
  row.timing=measure(settings,initialize,[&](unsigned){bank.freeStep();bank.finishLoss();},
    [&]{return bank.energy();},[&](unsigned){maximum(peak,bank.energy());return isFinite(bank.energy());});
  row.witnesses={{"modes",32},{"external_impulse_n_s",.001},{"initial_energy_j",initial},
    {"maximum_stored_energy_j",peak},{"final_energy_j",bank.energy()}};
  row.activated=initial>0&&peak>0;
  return row;
}

Row mechanics(const Settings& settings,bool coupled,int wood,bool boardInput) {
  keyra::PhysicalPiano module;
  require(module.prepare(settings.rate)&&module.setSoundboardMaterial(wood),"Mechanical setup failed");
  module.setResonance(1);module.setCouplingEnabled(coupled);
  float left=0,right=0;
  double initial=0,board=0,source=0,unstruck=0,peak=0;
  const auto initialize=[&] {
    module.reset();module.sustain(1);
    if(boardInput)module.boardImpulse(0,.001);else module.keyImpulse(60,.001);
    initial=module.energy();
  };
  const std::string name=boardInput?(wood?"wood_board_norway_spruce":"wood_board_sitka_spruce"):
    coupled?"coupled_strings_and_board":"uncoupled_strings_container";
  Row row{name,"keyra::PhysicalPiano",
          "Physical isolation/ablation in the full mechanical container; timing still includes unexcited banks and observation",
          boardInput?"Board-port impulse, all strings initially unexcited, bridge coupling disabled.":
          coupled?"C4 string-port impulse, bridge enabled, all dampers open; board and unstruck keys begin at zero.":
          "C4 string-port impulse, bridge disabled, all dampers open; board and unstruck keys remain isolated."};
  row.timing=measure(settings,initialize,[&](unsigned){module.process(&left,&right,1);},
    [&]{return module.energy();},[&](unsigned frame) {
      maximum(peak,std::max(std::abs(left),std::abs(right)));
      if((frame&63)==0) { maximum(board,module.boardEnergy());maximum(source,module.keyEnergy(60));maximum(unstruck,module.keyEnergy(64)); }
      return isFinite(left)&&isFinite(right)&&isFinite(module.keyEnergy(60))&&isFinite(module.boardEnergy());
    });
  const auto ledger=module.metrics();
  row.witnesses={{"modes",double(module.modeCount())},{"coupling_enabled",coupled?1.:0.},
    {"initial_energy_j",initial},{"maximum_board_energy_j",board},{"maximum_c4_energy_j",source},
    {"maximum_unstruck_e4_energy_j",unstruck},{"bridge_dissipation_j",ledger.bridgeDissipatedEnergy},
    {"maximum_bridge_balance_residual_j",ledger.maximumBridgeBalanceResidual},
    {"first_board_mode_hz",module.boardModeFrequency(0)},{"peak_observation",peak}};
  row.activated=initial>0&&(boardInput?board>0:source>0);
  if(coupled)row.activated=row.activated&&board>0&&unstruck>0;
  else row.activated=row.activated&&(boardInput?source==0:board==0&&unstruck==0);
  return row;
}

Row acoustic(const Settings& settings,const std::string& name,double temperature,
             double lid,double presence,double distance) {
  keyra::physics::AcousticLoad module;
  keyra::physics::AcousticConfig config;config.sampleRate=settings.rate;
  config.air.temperatureC=temperature;config.lidPosition=lid;
  config.player.presence=presence;config.player.distanceM=distance;
  require(module.prepare(config),"Acoustic setup failed");
  module.setCouplingEnabled(false);
  keyra::physics::AcousticStep last;
  double input=0,stored=0,radiated=0,player=0,internal=0,numerical=0,residual=0,pressure=0;
  const auto initialize=[&]{module.reset();input=module.applyPressureImpulse(.02);};
  Row row{name,"physics::AcousticLoad",
          "One shared reduced air/cavity/aperture/player-load implementation; not separate full-field solvers",
          "External pressure impulse; mechanical coupling disabled. Air changes ideal-gas properties, lid changes aperture geometry, player adds authored positive loss."};
  row.timing=measure(settings,initialize,[&](unsigned){last=module.step({0,0});},
    [&]{return module.energy();},[&](unsigned) {
      maximum(stored,module.energy());maximum(pressure,last.cavityPressure);
      maximum(residual,last.balanceResidual);radiated+=last.radiationDissipation;
      player+=last.playerDissipation;internal+=last.internalDissipation;numerical+=last.numericalDissipation;
      return last.valid&&isFinite(module.energy())&&isFinite(last.cavityPressure)&&isFinite(last.balanceResidual);
    });
  const auto properties=module.properties();
  row.witnesses={{"temperature_c",temperature},{"lid_position",lid},{"player_presence",presence},
    {"player_distance_m",distance},{"external_pressure_work_j",input},{"maximum_stored_energy_j",stored},
    {"radiated_energy_j",radiated},{"player_dissipation_j",player},{"internal_dissipation_j",internal},
    {"numerical_dissipation_j",numerical},{"maximum_balance_residual_j",residual},
    {"maximum_cavity_pressure_pa",pressure},{"density_kg_per_m3",properties.densityKgPerM3},
    {"speed_of_sound_m_per_s",properties.speedOfSoundMps},{"cavity_frequency_hz",properties.frequencyHz},
    {"aperture_ka",properties.apertureKa},{"low_ka_approximation_valid",properties.lowKaApproximation?1.:0.}};
  row.activated=input>0&&stored>0&&radiated>0;
  if(presence>0)row.activated=row.activated&&player>0;
  else row.activated=row.activated&&player==0;
  return row;
}

Row integrated(const Settings& settings) {
  keyra::PhysicalInstrument module;
  keyra::PhysicalInstrumentConfig config;config.sampleRate=settings.rate;config.resonance=1;
  config.acoustic.player.presence=1;
  require(module.prepare(config),"Integrated instrument setup failed");
  float left=0,right=0;
  double travel=0,force=0,strings=0,board=0,air=0,peak=0;
  const auto initialize=[&]{module.reset();module.noteOn(60,.85);module.sustain(1);};
  const auto advance=[&](unsigned frame){if(frame==settings.frames/2)module.noteOff(60);module.process(&left,&right,1);};
  Row row{"connected_physical_instrument","keyra::PhysicalInstrument",
          "Integrated research chain; not the calibrated live preview or a released Rack Extension",
          "Prescribed finger -> key/jack/hammer -> nonlinear contact -> strings/bridge/wood board -> reciprocal acoustic load. One C4 note; pedal held."};
  row.timing=measure(settings,initialize,advance,[&]{return module.energy();},[&](unsigned frame) {
    const auto state=module.action().state(60);
    maximum(travel,state.keyPosition);maximum(force,state.hammerForce);
    maximum(peak,std::max(std::abs(left),std::abs(right)));
    if((frame&63)==0) { maximum(strings,module.mechanics().keyEnergy(60));maximum(board,module.mechanics().boardEnergy());maximum(air,module.acoustics().energy()); }
    return isFinite(left)&&isFinite(right)&&isFinite(state.keyPosition)&&isFinite(state.hammerForce)&&isFinite(module.energy());
  });
  const auto ledger=module.metrics();
  row.witnesses={{"maximum_key_travel_m",travel},{"maximum_hammer_contact_force_n",force},
    {"maximum_c4_string_energy_j",strings},{"maximum_board_energy_j",board},
    {"maximum_cavity_energy_j",air},{"peak_observation",peak},{"contact_frames",double(ledger.contactFrames)},
    {"invalid_contacts",double(ledger.invalidContacts)},{"contact_dissipation_j",ledger.contactDissipation},
    {"acoustic_dissipation_j",ledger.acousticDissipation},
    {"maximum_contact_energy_residual_j",ledger.maximumContactEnergyResidual},
    {"maximum_acoustic_balance_residual_j",ledger.maximumAcousticBalanceResidual}};
  row.activated=travel>0&&force>0&&strings>0&&board>0&&air>0&&ledger.contactFrames>0&&ledger.invalidContacts==0;
  return row;
}

void quoted(const std::string& value) {
  std::cout<<'"';for(char c:value) { if(c=='"'||c=='\\')std::cout<<'\\';std::cout<<c; }std::cout<<'"';
}
void number(double value) { if(isFinite(value))std::cout<<value;else std::cout<<"null"; }
void write(const Row& row,const Settings& settings) {
  std::cout<<"{\"name\":";quoted(row.name);std::cout<<",\"implementation\":";quoted(row.implementation);
  std::cout<<",\"scope\":";quoted(row.scope);std::cout<<",\"fixture\":";quoted(row.fixture);
  std::cout<<",\"frames\":"<<settings.frames<<",\"audio_seconds\":"<<settings.frames/settings.rate;
  std::cout<<",\"callbacks\":"<<row.timing.callbacks<<",\"callback_mean_ms\":";number(row.timing.meanMs);
  std::cout<<",\"callback_p95_ms\":";number(row.timing.p95Ms);std::cout<<",\"callback_max_ms\":";number(row.timing.maxMs);
  std::cout<<",\"callback_deadline_exceedances\":"<<row.timing.deadlineMisses;
  std::cout<<",\"timed_final_energy_or_contact_dissipation_j\":";number(row.timing.finalEnergy);
  std::cout<<",\"all_observed_values_finite\":"<<(row.timing.finite?"true":"false");
  std::cout<<",\"activation_witness_passed\":"<<(row.activated?"true":"false")<<",\"witnesses\":{";
  for(std::size_t i=0;i<row.witnesses.size();++i) {if(i)std::cout<<',';quoted(row.witnesses[i].first);std::cout<<':';number(row.witnesses[i].second);}
  std::cout<<"}}";
}
}

int main(int argc,char** argv) {
  try {
    Settings settings;
    if(argc>2)throw std::runtime_error("Usage: keyra_benchmark_modules [audio-seconds, 0.25..10]");
    if(argc==2) {char* end=nullptr;const double seconds=std::strtod(argv[1],&end);require(end&&*end==0&&isFinite(seconds)&&seconds>=.25&&seconds<=10,"Invalid duration");settings.frames=unsigned(std::ceil(seconds*settings.rate/block))*block;}
    std::vector<Row> rows;
    rows.push_back(action(settings,"finger_and_key",false,false,false));
    rows.push_back(action(settings,"keybed_contact",true,false,false));
    rows.push_back(action(settings,"hammer_action_and_escapement",true,true,false));
    rows.push_back(action(settings,"key_release_and_return",true,false,true));
    rows.push_back(contact(settings));rows.push_back(modalKernel(settings));
    rows.push_back(mechanics(settings,false,0,false));rows.push_back(mechanics(settings,true,0,false));
    rows.push_back(mechanics(settings,false,0,true));rows.push_back(mechanics(settings,false,1,true));
    rows.push_back(acoustic(settings,"air_cold",0,.5,0,.6));
    rows.push_back(acoustic(settings,"air_warm",35,.5,0,.6));
    rows.push_back(acoustic(settings,"lid_closed",20,0,0,.6));
    rows.push_back(acoustic(settings,"lid_open",20,1,0,.6));
    rows.push_back(acoustic(settings,"player_body_absent",20,.5,0,.6));
    rows.push_back(acoustic(settings,"player_body_near",20,.5,1,.3));
    rows.push_back(acoustic(settings,"player_body_far",20,.5,1,2.));
    rows.push_back(integrated(settings));
    for(auto& row:rows)for(const auto& witness:row.witnesses)row.timing.finite=row.timing.finite&&isFinite(witness.second);
    std::cout<<std::setprecision(12)<<"{\n\"schema_version\":1,\"sample_rate\":"<<settings.rate<<",\"frames_per_callback\":64,";
    std::cout<<"\"callback_deadline_ms\":"<<1000*block/settings.rate<<",\"timing_is_diagnostic_not_a_test_gate\":true,";
    std::cout<<"\"timing_scope\":\"Host C++ wall-clock timing. Preparation and identical untimed activation-witness pass excluded; callbacks include harness dispatch. Not SDK-native or Reason-host CPU. Rows are not an additive CPU decomposition.\",";
    std::cout<<"\"shared_modules\":\"Finger/keybed/hammer/release use one reduced Action solver; air/lid/player cases use one reduced AcousticLoad. Wood/string PhysicalPiano ablations retain full-container overhead.\",\n\"modules\":[\n";
    bool good=true;
    for(std::size_t i=0;i<rows.size();++i) {if(i)std::cout<<",\n";write(rows[i],settings);good=good&&rows[i].timing.finite&&rows[i].activated;}
    std::cout<<"\n],\"all_modules_activated_and_finite\":"<<(good?"true":"false")<<"}\n";
    return good?0:1;
  } catch(const std::exception& error) {std::cerr<<"module benchmark: "<<error.what()<<'\n';return 1;}
}
