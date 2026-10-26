#include "local_resonance_support.h"
#include <chrono>
#include <ctime>
#include <filesystem>

namespace {
namespace probe=keyra::local_resonance_probe;
using keyra::physics::LocalResonance;
constexpr unsigned rate=48000,frames=38400;
constexpr double duration=double(frames)/rate;
constexpr std::array<const char*,5> names{{"combined","network","auxiliary-direct","body","strings"}};
struct Render {
  int velocity=0;std::string variant;
  std::array<std::vector<float>,5> audio;
  double keyF1=0,keyB=0,portG=0,weight=0;
  unsigned stringCount=0;
  double cpu=0,wall=0,maximumEnergy=0,maximumWorkResidual=0,maximumBalance=0,maximumField=0;
  double beforeRestrike=0,afterRestrike=0;
  keyra::physics::LocalResonanceLedger ledger{};
};
Render render(int velocity,const char* variant,bool enabled,bool coupling) {
  Render out;out.velocity=velocity;out.variant=variant;
  for(auto& a:out.audio)a.resize(frames*2);
  grand::Piano piano(probe::options(rate));
  probe::SpeakingKeyPort<grand::Piano> key(piano,108);
  LocalResonance auxiliary;auxiliary.setEnabled(enabled);auxiliary.setCouplingEnabled(coupling);
  out.keyF1=piano.keys[87].f0;out.keyB=piano.keys[87].B;out.portG=key.snapshot().inverseMass;
  out.stringCount=key.stringCount();out.weight=key.weight();
  std::array<std::array<double,2>,5> previous{},hp{};
  const double pole=std::exp(-2*grand::pi*24/rate);
  const auto start=std::chrono::steady_clock::now();const auto cpuStart=std::clock();
  for(unsigned frame=0;frame<frames;++frame) {
    if(frame==unsigned(.02*rate))piano.noteOn(108,velocity);
    if(frame==unsigned(.35*rate))piano.noteOff(108);
    if(frame==unsigned(.45*rate)) {
      out.beforeRestrike=auxiliary.energy();piano.noteOn(108,velocity);out.afterRestrike=auxiliary.energy();
    }
    if(frame==unsigned(.65*rate))piano.noteOff(108);
    const auto result=probe::step(piano,key,auxiliary,frame);
    if(!result.valid)throw std::runtime_error("Nonfinite local-resonance frame");
    out.maximumEnergy=std::max(out.maximumEnergy,result.auxiliaryEnergy);
    out.maximumWorkResidual=std::max(out.maximumWorkResidual,std::abs(result.workResidual));
    out.maximumBalance=std::max(out.maximumBalance,std::abs(result.balanceResidual));
    if((frame&255u)==0) {
      const auto recomputed=probe::recomputeObservation(piano);
      for(unsigned ch=0;ch<2;++ch)out.maximumField=std::max(out.maximumField,std::abs(result.network[ch]-recomputed[ch]));
    }
    const std::array<std::array<double,2>,5> fields{{result.combined,result.network,
      result.auxiliaryDirect,result.body,result.strings}};
    for(unsigned stem=0;stem<5;++stem)for(unsigned ch=0;ch<2;++ch) {
      const double x=fields[stem][ch];
      hp[stem][ch]=pole*(hp[stem][ch]+x-previous[stem][ch]);previous[stem][ch]=x;
      out.audio[stem][2*frame+ch]=float(hp[stem][ch]);
    }
  }
  out.cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  out.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  out.ledger=auxiliary.ledger();return out;
}
double rms(const std::vector<float>& data) {
  double p=0;for(float x:data)p+=double(x)*x;return std::sqrt(p/data.size());
}
double peak(const std::vector<float>& data) {
  double p=0;for(float x:data)p=std::max(p,std::abs(double(x)));return p;
}
double relativeDb(double a,double b) {return 20*std::log10(std::max(a,1.e-150)/std::max(b,1.e-150));}
double fixedBandPower(const std::vector<float>& data,double hz) {
  const unsigned first=unsigned(.05*rate),count=unsigned(.2*rate);
  std::array<double,2> real{},imag{};double sum=0;
  for(unsigned i=0;i<count;++i) {
    const double window=.5-.5*std::cos(2*grand::pi*i/(count-1));sum+=window;
    const double phase=2*grand::pi*hz*(first+i)/rate;
    for(unsigned ch=0;ch<2;++ch) {
      const double x=data[2*(first+i)+ch]*window;
      real[ch]+=x*std::cos(phase);imag[ch]+=x*std::sin(phase);
    }
  }
  return (real[0]*real[0]+imag[0]*imag[0]+real[1]*real[1]+imag[1]*imag[1])/(sum*sum);
}
double benchmark() {
  LocalResonance auxiliary;double speakingVelocity=.1;
  const auto start=std::clock();
  for(unsigned i=0;i<144000;++i) {
    if(i%4800==0)speakingVelocity+=.1;
    const auto r=auxiliary.step({speakingVelocity,2});
    speakingVelocity=(speakingVelocity+2*r.speakingImpulse)*.999;
  }
  const double cpu=double(std::clock()-start)/CLOCKS_PER_SEC;
  if(!std::isfinite(speakingVelocity+auxiliary.energy()))throw std::runtime_error("Nonfinite local benchmark");
  return cpu;
}
}
int main(int argc,char** argv) {
  try {
    if(argc!=2)throw std::runtime_error("Usage: keyra_local_resonance_probe OUTPUT_PREFIX");
    const std::string prefix=argv[1];
    if(prefix.find_first_of("\"\\\n\r\t")!=std::string::npos)throw std::runtime_error("Unsupported output-prefix characters");
    if(!std::filesystem::path(prefix).parent_path().empty())
      std::filesystem::create_directories(std::filesystem::path(prefix).parent_path());
    std::array<Render,6> versions{{render(40,"baseline",false,false),render(40,"coupled",true,true),
      render(40,"coupling-off",true,false),render(93,"baseline",false,false),
      render(93,"coupled",true,true),render(93,"coupling-off",true,false)}};
    double maximum=0;
    for(const auto& v:versions)for(const auto& a:v.audio)maximum=std::max(maximum,peak(a));
    const double gain=maximum>0?.8/maximum:1;
    auto write=[&](const std::string& suffix,const std::vector<float>& raw) {
      auto a=raw;for(auto& x:a)x=float(x*gain);grand::wav(prefix+'-'+suffix+".wav",a,rate);
    };
    std::ostringstream report;report<<std::setprecision(15);
    report<<"{\n\"schema_version\":1,\n\"solver_source\":\""<<KEYRA_LOCAL_RESONANCE_SOLVER
      <<"\",\n\"sample_rate\":"<<rate<<",\n\"seconds\":"<<duration<<",\n\"note\":108,"
      <<"\n\"MIDI_velocities\":[40,93],\n\"sample_policy\":\"Authored C8 MIDI40/93 only; no reference audio, A0 or C8v8 opened.\","
      <<"\n\"physical_identity\":\"Effective key-local mode; not identified as measured duplex/string/body/frame.\","
      <<"\n\"mode_frequency_hz\":4433.86,\n\"free_amplitude_loss_db_per_second\":50,"
      <<"\n\"coupling_resistance_authored\":0.5,\n\"direct_observer_gain_authored\":1,"
      <<"\n\"shared_export_gain\":"<<gain<<",\n\"isolated_component_cpu_seconds_per_3_audio_seconds\":"<<benchmark()
      <<",\n\"observer_policy\":\"Direct auxiliary field is optional and distinct from existing board radiation; no second loaded-board transfer is added. Coupled-network is the observer-muted output of the same intact run.\","
      <<"\n\"integration\":\"Original full network step then one passive key-local impulse; changed current-frame string radiation is corrected from actual p deltas. First-order split.\","
      <<"\n\"versions\":[";
    for(unsigned i=0;i<versions.size();++i) {
      const auto& v=versions[i];if(i)report<<',';
      const std::string label="midi"+std::to_string(v.velocity)+'-'+v.variant;
      report<<"{\"label\":\""<<label<<"\",\"cpu_seconds\":"<<v.cpu<<",\"wall_seconds\":"<<v.wall
        <<",\"key_carrier_hz\":"<<v.keyF1<<",\"key_B\":"<<v.keyB<<",\"speaking_strings\":"<<v.stringCount
        <<",\"aggregate_weight\":"<<v.weight<<",\"aggregate_inverse_mass\":"<<v.portG
        <<",\"maximum_auxiliary_energy_j\":"<<v.maximumEnergy
        <<",\"maximum_coupler_balance_residual_j\":"<<v.maximumBalance
        <<",\"maximum_actual_speaking_work_residual_j\":"<<v.maximumWorkResidual
        <<",\"maximum_current_field_recompute_error\":"<<v.maximumField
        <<",\"auxiliary_energy_before_restrike_j\":"<<v.beforeRestrike
        <<",\"auxiliary_energy_after_restrike_j\":"<<v.afterRestrike<<",\"stems\":[";
      for(unsigned stem=0;stem<5;++stem) {
        if(stem)report<<',';write(label+'-'+names[stem],v.audio[stem]);
        report<<"{\"name\":\""<<names[stem]<<"\",\"raw_rms\":"<<rms(v.audio[stem])
          <<",\"raw_peak\":"<<peak(v.audio[stem])<<",\"fixed_4433_86_hz_power_50_250ms\":"<<fixedBandPower(v.audio[stem],4433.86)
          <<",\"key_carrier_power_50_250ms\":"<<fixedBandPower(v.audio[stem],v.keyF1)<<"}";
      }
      report<<"]}";
    }
    report<<"],\n\"comparisons\":[";
    for(unsigned i=0;i<2;++i) {
      if(i)report<<',';const auto& baseline=versions[3*i];const auto& coupled=versions[3*i+1];
      const auto& disconnected=versions[3*i+2];
      if(baseline.audio[0]!=disconnected.audio[0])throw std::runtime_error("Coupling-off changed baseline float output");
      std::vector<float> delta(frames*2),totalDelta(frames*2);
      for(unsigned j=0;j<delta.size();++j) {
        delta[j]=coupled.audio[1][j]-baseline.audio[1][j];
        totalDelta[j]=coupled.audio[0][j]-baseline.audio[0][j];
      }
      const std::string label="midi"+std::to_string(baseline.velocity);
      write(label+"-network-effect",delta);write(label+"-total-effect",totalDelta);
      report<<"{\"MIDI_velocity\":"<<baseline.velocity<<",\"coupling_off_float_output_identical\":true,"
        <<"\"network_effect_relative_rms_db\":"<<relativeDb(rms(delta),rms(baseline.audio[0]))
        <<",\"unit_aux_direct_relative_rms_db\":"<<relativeDb(rms(coupled.audio[2]),rms(baseline.audio[0]))
        <<",\"combined_effect_relative_rms_db\":"<<relativeDb(rms(totalDelta),rms(baseline.audio[0]))<<"}";
    }
    report<<"],\n\"limits\":[\"No fit, model promotion, listening verdict or realtime claim.\","
      <<"\"One frequency/loss prior and authored coupling/unit observation; a strong corpus component is not proof of physical duplex identity.\","
      <<"\"All stems/counterfactuals share one gain across both velocities; no isolated component boost.\","
      <<"\"Fixed-frequency Hann projections are diagnostics, not independent component identification or recording validation.\"]\n}\n";
    std::ofstream file(prefix+".json");file<<report.str();if(!file)throw std::runtime_error("Cannot write local report");
    std::cout<<report.str();
  }catch(const std::exception& e){std::cerr<<"keyra_local_resonance_probe: "<<e.what()<<'\n';return 1;}
}
