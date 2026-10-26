#include "coupled_waveguide_support.h"
#include <cstring>
#include <ctime>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <vector>

namespace {
using Network=keyra::physics::CoupledWaveguide;
struct Case {
  std::string name;int note=60;
  bool coupling=true,observe=true,loss=true,repeat=false,boardTap=false;
  bool damper=false,source=true,release=false,dynamicPedal=false;
  double pedal=0;
};
struct Result {
  Case spec;Network::Ledger ledger;keyra::physics::StrikeStatistics strikes;
  double cpu=0,peak=0,rms=0,maxBalance=0,maxString=0,maxBoard=0,finalEnergy=0;
  double eventStateDelta=0,energyBeforeRepeat=0,finalDisplacement=0;
  double tailEnergyIntegral=0,maximumDamperSolveResidual=0,maximumDamperForceWorkResidual=0;
  double finalDamperClosure=0,finalDamperTarget=0;
  std::vector<std::array<float,2>> pressure;
};
void u16(std::ostream& o,unsigned n){o.put(char(n));o.put(char(n>>8));}
void u32(std::ostream& o,uint32_t n){for(unsigned i=0;i<4;++i)o.put(char(n>>(8*i)));}
void wav(const std::filesystem::path& path,const Result& r) {
  std::ofstream o(path,std::ios::binary);if(!o)throw std::runtime_error("Cannot write WAV");
  const uint32_t bytes=uint32_t(r.pressure.size()*2*sizeof(float));
  o.write("RIFF",4);u32(o,36+bytes);o.write("WAVEfmt ",8);u32(o,16);u16(o,3);u16(o,2);
  u32(o,48000);u32(o,48000*8);u16(o,8);u16(o,32);o.write("data",4);u32(o,bytes);
  for(const auto& frame:r.pressure)for(float value:frame) {
    static_assert(sizeof(float)==4,"32-bit float required");uint32_t bits;std::memcpy(&bits,&value,4);u32(o,bits);
  }
}
Result render(const Case& spec,const std::string& profiles) {
  Result r;r.spec=spec;
  const auto path=profiles+"/C"+(spec.note==36?std::string("2"):std::string("4"))+"-s32.cfg";
  auto c=keyra::waveguide_probe::pianoConfig(spec.note,path,spec.loss,true);
  c.coupling=spec.coupling;c.observation=spec.observe;c.humanization=spec.repeat?.65:0;c.seed=123456;
  c.damperEnabled=spec.damper;
  Network n;if(!n.prepare(c))throw std::runtime_error("Invalid network setup");
  if(!n.setPedal(spec.pedal))throw std::runtime_error("Invalid initial pedal");
  if(spec.source&&!spec.boardTap&&!n.noteOn(.7))throw std::runtime_error("Initial strike rejected");
  const unsigned frames=48000;r.pressure.resize(frames);
  const auto start=std::clock();
  double sum=0;
  unsigned pedalEvent=0;
  for(unsigned i=0;i<frames;++i) {
    if(spec.release&&i==4800){const double before=n.energy();n.noteOff();
      r.eventStateDelta=std::max(r.eventStateDelta,std::abs(n.energy()-before));}
    if(spec.dynamicPedal&&(i==12000||i==19200||i==26400||i==33600)) {
      const double before=n.energy();const double pedals[]={.5,0,1,.25};
      if(!n.setPedal(pedals[pedalEvent++]))throw std::runtime_error("Invalid dynamic pedal");
      r.eventStateDelta=std::max(r.eventStateDelta,std::abs(n.energy()-before));
    }
    if(spec.repeat&&(i==4800||i==9600)) {
      n.noteOff();const double before=n.stringEnergy()+n.boardEnergy();
      if(!n.noteOn(.7))throw std::runtime_error("Repeat request rejected");
      r.eventStateDelta=std::max(r.eventStateDelta,std::abs(n.stringEnergy()+n.boardEnergy()-before));
      r.energyBeforeRepeat=std::max(r.energyBeforeRepeat,before);
    }
    Network::Input input;if(spec.boardTap&&i<100)input.boardForce={{.01,-.004,.003}};
    const auto frame=n.step(input);if(!frame.valid)throw std::runtime_error("Invalid network frame");
    r.maximumDamperSolveResidual=std::max(r.maximumDamperSolveResidual,frame.damperSolveResidual);
    double forceWork=0;for(unsigned s=0;s<c.stringCount;++s)forceWork-=Network::h*frame.damperForce[s]*frame.contactVelocity[s];
    r.maximumDamperForceWorkResidual=std::max(r.maximumDamperForceWorkResidual,std::abs(forceWork-frame.damperLoss));
    for(unsigned ch=0;ch<2;++ch){
      if(!std::isfinite(frame.pressure[ch]))throw std::runtime_error("Nonfinite pressure");
      r.pressure[i][ch]=float(frame.pressure[ch]);r.peak=std::max(r.peak,std::abs(frame.pressure[ch]));sum+=frame.pressure[ch]*frame.pressure[ch];
    }
    if(i%64==0){r.maxBalance=std::max(r.maxBalance,std::abs(n.balanceResidual()));
      r.maxString=std::max(r.maxString,n.stringEnergy());r.maxBoard=std::max(r.maxBoard,n.boardEnergy());
      if(i>=9600)r.tailEnergyIntegral+=n.energy()*64*Network::h;}
  }
  r.cpu=double(std::clock()-start)/CLOCKS_PER_SEC;r.rms=std::sqrt(sum/(2*frames));
  r.ledger=n.ledger();r.strikes=n.strikeStatistics();r.finalEnergy=n.energy();r.finalDisplacement=n.contactDisplacement();
  r.finalDamperClosure=n.damperClosure();r.finalDamperTarget=n.damperTargetClosure();return r;
}
}
int main(int argc,char** argv)try {
  if(argc!=3&&(argc!=4||std::string(argv[3])!="--damper")){
    std::cerr<<"usage: probe_coupled_waveguide OUTPUT_DIR PROFILE_DIR [--damper]\n";return 1;}
  const bool damperMode=argc==4;
  const std::filesystem::path output=argv[1];std::filesystem::create_directories(output);
  std::vector<Result> results;
  for(int note:{36,60})for(unsigned kind=0;kind<(damperMode?9u:6u);++kind) {
    Case c;c.note=note;c.name=(note==36?"C2-":"C4-");
    if(damperMode) {
      c.damper=true;c.release=true;
      switch(kind) {
        case 0:c.name+="damper-pedal0";break;
        case 1:c.name+="damper-pedal-half";c.pedal=.5;break;
        case 2:c.name+="damper-pedal1";c.pedal=1;break;
        case 3:c.name+="damper-load-off";c.damper=false;break;
        case 4:c.name+="damper-coupling-off";c.coupling=false;break;
        case 5:c.name+="damper-observer-off";c.observe=false;break;
        case 6:c.name+="damper-source-off";c.source=false;break;
        case 7:c.name+="damper-dynamic-pedal";c.pedal=1;c.dynamicPedal=true;break;
        default:c.name+="damper-repeat-10hz";c.release=false;c.repeat=true;break;
      }
    } else switch(kind) {
      case 0:c.name+="connected";break;
      case 1:c.name+="lossless";c.loss=false;break;
      case 2:c.name+="coupling-off";c.coupling=false;break;
      case 3:c.name+="observer-off";c.observe=false;break;
      case 4:c.name+="repeat-10hz";c.repeat=true;break;
      default:c.name+="board-source-only";c.boardTap=true;break;
    }
    results.push_back(render(c,argv[2]));wav(output/(c.name+".wav"),results.back());
  }
  std::ofstream j(output/"report.json");j<<std::setprecision(17);
  j<<"{\n  \"schema\": 1,\n  \"sample_rate\": 48000,\n  \"seconds_per_case\": 1,\n"
    <<"  \"scope\": \"One key per case, 1 polarization, identical choir lines, original 475-mode board; raw board-only pressure, no final radiation calibration\",\n"
    <<"  \"realtime_claim\": false,\n  \"damper_mode\": "<<(damperMode?"true":"false")<<",\n  \"cases\": [\n";
  bool first=true;
  for(const auto& r:results){const auto& l=r.ledger;
    if(!first)j<<",\n";first=false;
    j<<"    {\"name\":\""<<r.spec.name<<"\",\"note\":"<<r.spec.note<<",\"cpu_seconds\":"<<r.cpu
      <<",\"pressure_peak\":"<<r.peak<<",\"pressure_rms\":"<<r.rms
      <<",\"max_balance_residual_j\":"<<r.maxBalance<<",\"maximum_interaction_residual_j\":"<<l.maximumInteractionResidual
      <<",\"launches\":"<<l.launches<<",\"partial_launches\":"<<l.partialLaunches<<",\"launch_work_j\":"<<l.launchWork
      <<",\"external_work_j\":"<<l.externalForceWork<<",\"path_loss_j\":"<<l.pathLoss<<",\"board_loss_j\":"<<l.boardLoss
      <<",\"contact_loss_j\":"<<l.contactLoss<<",\"minimum_contact_loss_j\":"<<l.minimumContactLoss
      <<",\"damper_loss_j\":"<<l.damperLoss<<",\"tail_energy_integral_j_s\":"<<r.tailEnergyIntegral
      <<",\"maximum_damper_solve_residual_m_s\":"<<r.maximumDamperSolveResidual
      <<",\"maximum_damper_force_work_residual_j\":"<<r.maximumDamperForceWorkResidual
      <<",\"final_damper_closure\":"<<r.finalDamperClosure<<",\"final_damper_target\":"<<r.finalDamperTarget
      <<",\"retired_energy_j\":"<<l.retiredEnergy<<",\"contact_faults\":"<<l.contactFaults<<",\"bridge_faults\":"<<l.bridgeFaults
      <<",\"maximum_contact_residual\":"<<l.maximumContactResidual<<",\"maximum_string_energy_j\":"<<r.maxString
      <<",\"maximum_board_energy_j\":"<<r.maxBoard<<",\"final_energy_j\":"<<r.finalEnergy
      <<",\"event_state_delta_j\":"<<r.eventStateDelta<<",\"energy_before_repeat_j\":"<<r.energyBeforeRepeat
      <<",\"final_contact_displacement_m\":"<<r.finalDisplacement<<",\"requests\":"<<r.strikes.requests
      <<",\"expired\":"<<r.strikes.expired<<",\"cancelled\":"<<r.strikes.cancelled<<"}";
  }
  j<<"\n  ]\n}\n";
  if(!j)throw std::runtime_error("Cannot write report");
  std::cout<<"Wrote "<<results.size()<<" bounded cases to "<<output<<"\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
