#include "mechanism_network_support.h"
#include <chrono>
#include <ctime>
#include <filesystem>

namespace {
namespace probe=keyra::mechanism_probe;
using keyra::physics::MechanismExciter;
constexpr unsigned rate=48000;
constexpr double seconds=1.3;
constexpr unsigned frames=unsigned(rate*seconds);
struct Trigger { double time; unsigned source; double strength; };
constexpr std::array<Trigger,8> triggers{{
  {.05,0,.65},{.065,1,.65},{.35,2,.35},{.48,3,.55},
  {.65,0,.8},{.665,1,.8},{.92,2,.4},{1.02,3,.45}}};
constexpr std::array<const char*,9> stemNames{{
  "combined","direct","network","body","strings",
  "key-press-direct","keybed-direct","key-release-direct","pedal-direct"}};
struct Render {
  std::string name;
  std::array<std::vector<float>,9> audio;
  double wall=0,cpu=0,maximumBoard=0,maximumStrings=0,maximumSource=0;
  double maximumSourceResidual=0,maximumReactionResidual=0,maximumReconstructionError=0;
  std::array<keyra::physics::MechanismLedger,4> ledgers{};
  bool finite=true;
};

Render render(const char* name,bool enabled,bool coupling,bool notes) {
  Render result; result.name=name;
  for (auto& data:result.audio) data.resize(frames*2);
  grand::Piano piano(probe::options(rate)); probe::openDampers(piano);
  std::array<MechanismExciter,4> sources; probe::prepare(sources,rate,enabled,coupling);
  std::array<std::array<double,2>,9> previous{},hp{};
  const double pole=std::exp(-2*grand::pi*24/rate);
  size_t next=0;
  const auto start=std::chrono::steady_clock::now(); const auto cpuStart=std::clock();
  for (unsigned frame=0;frame<frames;++frame) {
    while (next<triggers.size() && unsigned(std::llround(triggers[next].time*rate))<=frame) {
      const auto& t=triggers[next++]; (void)sources[t.source].trigger(t.strength);
    }
    if (notes) {
      if (frame==unsigned(.065*rate)) piano.noteOn(60,61);
      if (frame==unsigned(.3*rate)) piano.noteOff(60);
      if (frame==unsigned(.665*rate)) { piano.noteOn(48,50); piano.noteOn(55,57); piano.noteOn(64,72); }
      if (frame==unsigned(1.0*rate)) { piano.noteOff(48); piano.noteOff(55); piano.noteOff(64); }
    }
    const auto observation=probe::step(piano,sources,frame);
    result.finite=result.finite&&observation.valid;
    if (!observation.valid) throw std::runtime_error("Nonfinite mechanism network");
    result.maximumSourceResidual=std::max(result.maximumSourceResidual,observation.maximumSourceBalanceResidual);
    result.maximumReactionResidual=std::max(result.maximumReactionResidual,observation.maximumReactionWorkResidual);
    std::array<std::array<double,2>,9> data{{observation.combined,observation.direct,
      observation.network,observation.body,observation.strings,{},{},{},{}}};
    for (unsigned i=0;i<4;++i) data[i+5]={observation.individualDirect[i],observation.individualDirect[i]};
    for (unsigned ch=0;ch<2;++ch) {
      result.maximumReconstructionError=std::max(result.maximumReconstructionError,
        std::abs(observation.combined[ch]-observation.direct[ch]-observation.network[ch]));
      result.maximumReconstructionError=std::max(result.maximumReconstructionError,
        std::abs(observation.network[ch]-observation.body[ch]-observation.strings[ch]));
      for (unsigned stem=0;stem<9;++stem) {
        const double sample=data[stem][ch];
        hp[stem][ch]=pole*(hp[stem][ch]+sample-previous[stem][ch]); previous[stem][ch]=sample;
        result.audio[stem][2*frame+ch]=float(hp[stem][ch]);
      }
    }
    if ((frame&63u)==0) {
      result.maximumBoard=std::max(result.maximumBoard,probe::boardEnergy(piano));
      result.maximumStrings=std::max(result.maximumStrings,probe::stringEnergy(piano));
      double energy=0; for (const auto& s:sources) energy+=s.energy();
      result.maximumSource=std::max(result.maximumSource,energy);
    }
  }
  result.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  result.cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  for (unsigned i=0;i<4;++i) result.ledgers[i]=sources[i].ledger();
  return result;
}

double rms(const std::vector<float>& data) {
  double sum=0; for (float x:data) sum+=double(x)*x; return std::sqrt(sum/data.size());
}
double peak(const std::vector<float>& data) {
  double p=0; for (float x:data) p=std::max(p,std::abs(double(x))); return p;
}
struct Benchmark {double cpu=0,wall=0,maximumCallback=0;unsigned callbacks=0;};
Benchmark benchmark() {
  MechanismExciter source; source.trigger(.8);
  double bodyVelocity=0;
  Benchmark b;
  const auto start=std::chrono::steady_clock::now(); const auto cpuStart=std::clock();
  for (unsigned first=0;first<144000;first+=64) {
    const auto callback=std::chrono::steady_clock::now();
    for (unsigned i=first;i<first+64;++i) {
      if (i%4800==0) (void)source.trigger(.5);
      const auto result=source.step({bodyVelocity,1});
      bodyVelocity=(bodyVelocity+result.bodyImpulse)*.9999;
    }
    b.maximumCallback=std::max(b.maximumCallback,std::chrono::duration<double>(std::chrono::steady_clock::now()-callback).count());
    ++b.callbacks;
  }
  b.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  b.cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  // Keep the computed states observable to the optimizer without render I/O.
  if (!std::isfinite(source.energy()+bodyVelocity)) throw std::runtime_error("Invalid mechanism benchmark");
  return b;
}
}

int main(int argc,char** argv) {
  try {
    if (argc<2||argc>3||(argc==3&&std::string(argv[2])!="--notes")) {
      std::cerr<<"Usage: keyra_mechanism_probe OUTPUT_PREFIX [--notes]\n";
      return 1;
    }
    const std::string prefix=argv[1];
    if (prefix.find_first_of("\"\\\n\r\t")!=std::string::npos)
      throw std::runtime_error("Output prefix contains unsupported JSON control characters");
    if (!std::filesystem::path(prefix).parent_path().empty())
      std::filesystem::create_directories(std::filesystem::path(prefix).parent_path());
    const bool notes=argc==3;
    std::array<Render,3> versions{{render("intact",true,true,notes),
      render("coupling-off",true,false,notes),render("source-off",false,false,notes)}};
    std::vector<float> delta(frames*2),couplingDelta(frames*2),reactionDelta(frames*2);
    for (unsigned i=0;i<delta.size();++i) {
      delta[i]=versions[0].audio[0][i]-versions[2].audio[0][i];
      couplingDelta[i]=versions[0].audio[2][i]-versions[1].audio[2][i];
      reactionDelta[i]=versions[0].audio[1][i]-versions[1].audio[1][i];
    }
    double maximumPeak=std::max(peak(delta),peak(couplingDelta));
    for (const auto& version:versions) for (const auto& data:version.audio)
      maximumPeak=std::max(maximumPeak,peak(data));
    const double gain=maximumPeak>0?.8/maximumPeak:1;
    auto write=[&](const std::string& suffix,const std::vector<float>& raw) {
      std::vector<float> audio(raw);
      for (auto& value:audio) value=float(value*gain);
      grand::wav(prefix+"-"+suffix+".wav",audio,rate);
    };
    const auto timing=benchmark();
    std::ostringstream report;
    report<<std::setprecision(15)<<"{\n\"schema_version\":1,\n\"sample_rate\":"<<rate
      <<",\n\"seconds\":"<<seconds<<",\n\"notes_enabled\":"<<(notes?"true":"false")
      <<",\n\"shared_export_gain\":"<<gain
      <<",\n\"body_reaction_direct_difference_raw_rms\":"<<rms(reactionDelta)
      <<",\n\"observer_units\":\"Authored pressure proxies, not calibrated pascals or measured microphone levels.\","
      <<"\n\"scope\":\"All intact stems come from the same complete simulation. Coupling-off and source-off are separate counterfactual renders with the same triggers and MIDI.\","
      <<"\n\"integration\":\"Original network step then sequential passive mechanism impulses; J/dt added once to acceleration observation without overwriting bridge force. First-order composition.\","
      <<"\n\"whole_network_timing_scope\":\"Includes original full solver, port/observation scans and interval energy diagnostics; preparation/export excluded. Not SDK or Reason performance.\","
      <<"\n\"isolated_benchmark\":{\"audio_seconds\":3,\"component\":\"One three-mode mechanism plus finite-mass damped dummy body\",\"cpu_seconds\":"
      <<timing.cpu<<",\"wall_seconds\":"<<timing.wall<<",\"callbacks_64_frames\":"<<timing.callbacks
      <<",\"maximum_callback_seconds\":"<<timing.maximumCallback<<"},\n\"triggers\":[";
    for (unsigned i=0;i<triggers.size();++i) {
      if(i)report<<',';
      report<<"{\"seconds\":"<<triggers[i].time<<",\"component\":\""<<probe::names[triggers[i].source]
        <<"\",\"strength\":"<<triggers[i].strength<<"}";
    }
    report<<"],\n\"versions\":[";
    for (unsigned index=0;index<versions.size();++index) {
      auto& version=versions[index]; if(index)report<<',';
      report<<"{\"name\":\""<<version.name<<"\",\"finite\":"<<(version.finite?"true":"false")
        <<",\"cpu_seconds\":"<<version.cpu<<",\"wall_seconds\":"<<version.wall
        <<",\"maximum_board_energy_j\":"<<version.maximumBoard<<",\"maximum_string_energy_j\":"<<version.maximumStrings
        <<",\"all_strings_unstruck\":"<<(notes?"false":"true")<<",\"maximum_source_energy_j\":"<<version.maximumSource
        <<",\"maximum_source_balance_residual_j\":"<<version.maximumSourceResidual
        <<",\"maximum_body_reaction_residual_j\":"<<version.maximumReactionResidual
        <<",\"maximum_stem_reconstruction_error\":"<<version.maximumReconstructionError<<",\"stems\":[";
      for (unsigned stem=0;stem<stemNames.size();++stem) {
        if(stem)report<<',';
        const std::string suffix=version.name+"-"+stemNames[stem]; write(suffix,version.audio[stem]);
        report<<"{\"name\":\""<<stemNames[stem]<<"\",\"file\":\""<<prefix<<'-'<<suffix
          <<".wav\",\"raw_rms\":"<<rms(version.audio[stem])<<",\"raw_peak\":"<<peak(version.audio[stem])<<"}";
      }
      report<<"],\"mechanism_ledgers\":[";
      for (unsigned i=0;i<4;++i) {
        if(i)report<<',';
        const auto& l=version.ledgers[i];
        report<<"{\"name\":\""<<probe::names[i]<<"\",\"external_work_j\":"<<l.externalWork
          <<",\"internal_dissipation_j\":"<<l.internalDissipation<<",\"coupling_dissipation_j\":"<<l.couplingDissipation
          <<",\"body_work_j\":"<<l.bodyWork<<",\"retired_energy_j\":"<<l.retiredEnergy
          <<",\"frames\":"<<l.frames<<",\"triggers\":"<<l.triggers<<",\"invalid_frames\":"<<l.invalidFrames<<"}";
      }
      report<<"]}";
    }
    write("source-off-delta",delta); write("coupling-off-network-delta",couplingDelta);
    report<<"],\n\"deltas\":[\""<<prefix<<"-source-off-delta.wav\",\""<<prefix
      <<"-coupling-off-network-delta.wav\"],\n\"limits\":[\"Effective masses, frequencies, losses, impulses and direct levels are authored, not measured.\","
      <<"\"No default sound or commercial-quality claim; listenable diagnostics are not perceptual validation.\","
      <<"\"The source-off render removes both direct observation and passive mechanical loading. Observation-only mute remains a separate tested control.\","
      <<"\"All exports share one gain; ablation differences are not independently normalized away.\"]\n}\n";
    std::ofstream file(prefix+".json"); file<<report.str();
    if (!file) throw std::runtime_error("Cannot write mechanism report");
    std::cout<<report.str();
  } catch (const std::exception& e) {
    std::cerr<<"keyra_mechanism_probe: "<<e.what()<<'\n'; return 1;
  }
}
