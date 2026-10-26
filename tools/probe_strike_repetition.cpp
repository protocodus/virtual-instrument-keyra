#include "strike_repetition_support.h"
#include <chrono>
#include <ctime>
#include <filesystem>

namespace {
namespace probe=keyra::strike_probe;
constexpr unsigned rate=48000,frames=28800;
struct Event {double time;char kind;double value;};
constexpr std::array<Event,16> events{{
  {0,'p',1},{.010,'n',80},{.0105,'n',80},{.011,'o',0},{.015,'n',80},{.016,'o',0},
  {.030,'n',80},{.040,'o',0},{.110,'n',80},{.150,'o',0},
  {.250,'n',80},{.290,'o',0},{.320,'p',.5},{.350,'n',80},
  {.390,'o',0},{.480,'p',0}}};
struct Launch {
  double time=0,velocity=0,hardness=0,recovery=0,keyLift=0;
  double velocityFactor=0,recoveryFactor=0;
  uint64_t request=0;
  bool partial=false;
};
struct Render {
  const char* name=nullptr;
  std::vector<float> audio;
  std::vector<Launch> launches;
  keyra::physics::StrikeStatistics statistics{};
  probe::LaunchLedger ledger{};
  double cpu=0,wall=0,maxCallback=0,finalEnergy=0;
  unsigned legacyActiveResets=0;
};
Render render(const char* name,bool legacy,double variation,bool mechanisms) {
  Render result; result.name=name; result.audio.resize(frames*2); result.launches.reserve(events.size());
  probe::Piano piano(rate,variation,123456); piano.enableMechanisms(mechanisms);
  std::array<double,2> previous{},hp{};
  const double pole=std::exp(-2*grand::pi*24/rate);
  unsigned next=0; uint64_t previousLaunch=0;
  const auto start=std::chrono::steady_clock::now(); const auto cpuStart=std::clock();
  for (unsigned first=0;first<frames;first+=64) {
    const auto callback=std::chrono::steady_clock::now();
    for (unsigned frame=first;frame<std::min(first+64,frames);++frame) {
      while (next<events.size()&&unsigned(std::llround(events[next].time*rate))<=frame) {
        const auto& e=events[next++];
        if (e.kind=='n') {
          if (legacy) {
            if (piano.model.keys[39].hammerActive) ++result.legacyActiveResets;
            piano.model.noteOn(60,e.value);
          } else (void)piano.noteOn(60,e.value);
        } else if (e.kind=='o') {
          if (legacy) piano.model.noteOff(60); else piano.noteOff(60);
        } else {
          if (legacy) piano.model.pedalTarget=e.value; else piano.sustain(e.value);
        }
      }
      const auto value=legacy?piano.model.step(frame):piano.step(frame);
      if (!legacy&&piano.controller.statistics().launches!=previousLaunch) {
        const auto& l=piano.lastLaunch[39]; const auto& k=piano.model.keys[39];
        result.launches.push_back({frame/double(rate),k.hammerV,k.K,l.recovery,l.keyLift,
          l.velocityFactor,l.recoveryVelocityFactor,l.requestId,l.preserveSeparatedPosition});
        previousLaunch=piano.controller.statistics().launches;
      }
      for (unsigned ch=0;ch<2;++ch) {
        if (!std::isfinite(value[ch])) throw std::runtime_error("Nonfinite strike probe");
        hp[ch]=pole*(hp[ch]+value[ch]-previous[ch]); previous[ch]=value[ch];
        result.audio[frame*2+ch]=float(hp[ch]);
      }
    }
    result.maxCallback=std::max(result.maxCallback,
      std::chrono::duration<double>(std::chrono::steady_clock::now()-callback).count());
  }
  result.cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  result.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  result.statistics=piano.controller.statistics(); result.ledger=piano.ledger;
  result.finalEnergy=piano.model.energy(); return result;
}

double controllerBenchmark() {
  keyra::physics::StrikeController controller;
  double witness=0;
  const auto start=std::clock();
  for (unsigned frame=0;frame<144000;++frame) {
    if (frame%4800==0) controller.request(60,.7);
    if (frame%4800==2400) controller.release(60);
    if (controller.requiresTick(60)) {
      const auto launch=controller.poll(60,{false,-.012,0});
      witness+=launch.velocityFactor+controller.state(60).returnDepth;
    }
  }
  const double cpu=double(std::clock()-start)/CLOCKS_PER_SEC;
  if (!std::isfinite(witness)||witness<=0) throw std::runtime_error("Controller benchmark inactive");
  return cpu;
}
}

int main(int argc,char** argv) {
  try {
    if (argc!=2) throw std::runtime_error("Usage: keyra_strike_probe OUTPUT_PREFIX");
    const std::filesystem::path prefix=argv[1];
    if (prefix.has_parent_path()) std::filesystem::create_directories(prefix.parent_path());
    std::array<Render,4> renders{{render("legacy-reset",true,0,false),
      render("recovery-control",false,0,false),render("varied-recovery",false,.65,false),
      render("varied-with-mechanisms",false,.65,true)}};
    double peak=0;
    for (const auto& version:renders) for (float value:version.audio) peak=std::max(peak,std::abs(double(value)));
    const double gain=.8/std::max(peak,1.e-15);
    std::ostringstream out; out<<std::setprecision(15)<<"{\n\"schema_version\":1,\n\"sample_rate\":"<<rate
      <<",\n\"seconds\":"<<frames/double(rate)<<",\n\"seed\":123456,\n\"shared_export_gain\":"<<gain
      <<",\n\"controller_only_benchmark\":{\"audio_seconds\":3,\"cpu_seconds\":"<<controllerBenchmark()
      <<",\"scope\":\"One fixed-array controller, one repeated key, authored inactive-hammer observation; excludes piano and mechanism adapter.\"},\n\"events\":[";
    for (unsigned i=0;i<events.size();++i) {
      if (i) out<<','; const auto& e=events[i];
      out<<"{\"seconds\":"<<e.time<<",\"kind\":\""<<e.kind<<"\",\"value\":"<<e.value<<'}';
    }
    out<<"],\n\"versions\":[";
    for (unsigned i=0;i<renders.size();++i) {
      auto& version=renders[i]; if (i) out<<',';
      for (auto& sample:version.audio) sample=float(sample*gain);
      const std::string path=prefix.string()+"-"+version.name+".wav";
      grand::wav(path,version.audio,rate);
      const auto& s=version.statistics; const auto& l=version.ledger;
      out<<"{\"name\":\""<<version.name<<"\",\"audio\":\""<<path<<"\",\"cpu_seconds\":"<<version.cpu
        <<",\"wall_seconds\":"<<version.wall<<",\"maximum_64frame_callback_seconds\":"<<version.maxCallback
        <<",\"final_network_energy_j\":"<<version.finalEnergy<<",\"legacy_active_resets\":"<<version.legacyActiveResets
        <<",\"requests\":"<<s.requests<<",\"launches\":"<<s.launches<<",\"coalesced\":"<<s.coalesced
        <<",\"cancelled\":"<<s.cancelled<<",\"expired\":"<<s.expired
        <<",\"retired_before_separation\":"<<s.retiredBeforeSeparation<<",\"invalid_observations\":"<<s.invalidObservations
        <<",\"core_launch_work_j\":"<<l.coreLaunchWork<<",\"retired_core_hammer_energy_j\":"<<l.retiredCoreHammerEnergy
        <<",\"replaced_inactive_kinematic_energy_j\":"<<l.replacedInactiveKinematicEnergy
        <<",\"partial_launches\":"<<l.partialLaunches<<",\"launch_events\":[";
      for (unsigned j=0;j<version.launches.size();++j) {
        const auto& event=version.launches[j]; if (j) out<<',';
        out<<"{\"seconds\":"<<event.time<<",\"request_id\":"<<event.request<<",\"hammer_velocity_after_frame\":"<<event.velocity
          <<",\"hardness\":"<<event.hardness<<",\"recovery\":"<<event.recovery<<",\"key_lift\":"<<event.keyLift
          <<",\"velocity_factor\":"<<event.velocityFactor<<",\"recovery_velocity_factor\":"<<event.recoveryFactor
          <<",\"preserved_separated_position\":"<<(event.partial?"true":"false")<<'}';
      }
      out<<"]}";
    }
    out<<"],\n\"limits\":[\"Authored repetition/return and excitation-variation model, not measured action geometry.\","
      "\"Requests keep sample timestamps; physical hammer launches may be deferred, coalesced or cancelled.\","
      "\"Same string/network state persists; original full solver and calibration are unchanged.\","
      "\"Shared gain across all outputs, original24Hz high-pass, no added room.\","
      "\"CPU includes full original solver and launch diagnostics; not actual Reason or realtime qualification.\"]\n}\n";
    std::ofstream report(prefix.string()+".json"); report<<out.str();
    if (!report) throw std::runtime_error("Cannot write strike report");
    std::cout<<out.str();
  } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
