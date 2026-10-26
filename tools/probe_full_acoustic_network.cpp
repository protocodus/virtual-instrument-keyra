#include "full_acoustic_network_support.h"
#include <ctime>
#include <filesystem>
#include <string_view>

namespace {
namespace probe=keyra::full_acoustic_probe;
namespace body=keyra::mechanism_probe;
constexpr unsigned rate=48000,frames=34560;
constexpr double seconds=double(frames)/rate;
constexpr unsigned stems=4;
constexpr std::array<const char*,stems> stemNames{{"combined","acoustic-reaction-proxy","mechanism-direct-proxy","cavity-pressure-pa"}};
struct Event { unsigned frame; const char* kind; int note; double value; };
constexpr std::array<Event,14> events{{
  {720,"pedal",0,1},{1200,"on",60,75},{5760,"off",60,0},
  {6720,"on",60,75},{12000,"off",60,0},
  {13920,"on",21,70},{13920,"on",48,65},{13920,"on",84,72},{13920,"on",108,60},
  {19200,"off",21,0},{19200,"off",48,0},{19200,"off",84,0},{19200,"off",108,0},
  {24960,"pedal",0,0}}};
struct Stats {
  double sum=0,peak=0;
  void add(double x) { sum+=x*x; peak=std::max(peak,std::abs(x)); }
  double rms(unsigned count) const { return std::sqrt(sum/count); }
};
struct Render {
  std::string name,ablation;
  probe::Config config{};
  std::array<std::vector<float>,stems> audio;
  std::array<Stats,stems> stats{};
  double cpu=0,wall=0,maximumCallback=0;
  double maximumAir=0,maximumBoard=0,maximumStrings=0;
  double suppliedAir=0,airBoardWork=0,couplingLoss=0,radiationLoss=0,playerLoss=0,internalLoss=0;
  double maximumBalance=0,maximumReaction=0;
  uint64_t launches=0;
  keyra::physics::AcousticProperties properties{};
};

Render render(const std::string& name,double lid,double player,double distance,const std::string& ablation="intact") {
  Render out; out.name=name; out.ablation=ablation;
  auto& config=out.config;
  config.acoustic[0].lidPosition=lid;
  config.acoustic[0].player.presence=player; config.acoustic[0].player.distanceM=distance;
  config.mechanicalImpulseLevel=.025;
  config.airEnabled=ablation!="load-off"; config.airCoupling=ablation!="coupling-off";
  config.directAirGain=0;
  probe::Piano piano(config);
  out.properties=piano.acoustic[0].properties();
  for (auto& a:out.audio) a.resize(frames*2);
  std::array<std::array<double,2>,stems> previous{},hp{};
  const double pole=std::exp(-2*grand::pi*24/rate);
  unsigned next=0;
  const auto cpuStart=std::clock(); const auto start=std::chrono::steady_clock::now();
  for (unsigned first=0;first<frames;first+=64) {
    const auto callback=std::chrono::steady_clock::now();
    for (unsigned frame=first;frame<std::min(first+64,frames);++frame) {
      if (frame==240&&ablation!="source-off") out.suppliedAir+=piano.applyPressureImpulse(0,.02);
      while (next<events.size()&&events[next].frame==frame) {
        const auto& e=events[next++];
        if (std::string_view(e.kind)=="on") piano.noteOn(e.note,e.value);
        else if (std::string_view(e.kind)=="off") piano.noteOff(e.note);
        else piano.sustain(e.value);
      }
      const auto result=piano.step(frame);
      if (!result.valid) throw std::runtime_error("Nonfinite full acoustic network render");
      out.maximumBalance=std::max(out.maximumBalance,result.junction.maximumBalanceResidual);
      out.maximumReaction=std::max(out.maximumReaction,result.junction.maximumReactionResidual);
      const auto& load=result.junction.loads[0];
      out.airBoardWork+=load.boardWork; out.couplingLoss+=load.couplingDissipation;
      out.radiationLoss+=load.radiationDissipation; out.playerLoss+=load.playerDissipation;
      out.internalLoss+=load.internalDissipation+load.numericalDissipation;
      const double pa=result.junction.cavityPressurePa;
      const std::array<std::array<double,2>,stems> data{{result.combined,result.acousticReaction,
        result.mechanismDirect,{pa,pa}}};
      for (unsigned stem=0;stem<stems;++stem) for (unsigned ch=0;ch<2;++ch) {
        const double x=data[stem][ch];
        // Match the original renderer's 24-Hz observation filter for proxy
        // stems. Physical cavity pressure stays unfiltered and separate.
        double observed=x;
        if (stem!=3) {
          hp[stem][ch]=pole*(hp[stem][ch]+x-previous[stem][ch]); previous[stem][ch]=x;
          observed=hp[stem][ch];
        }
        out.audio[stem][2*frame+ch]=float(observed); out.stats[stem].add(observed);
      }
      if ((frame&63u)==0) {
        out.maximumAir=std::max(out.maximumAir,piano.acousticEnergy());
        out.maximumBoard=std::max(out.maximumBoard,body::boardEnergy(piano.strike.model));
        out.maximumStrings=std::max(out.maximumStrings,body::stringEnergy(piano.strike.model));
      }
    }
    out.maximumCallback=std::max(out.maximumCallback,
      std::chrono::duration<double>(std::chrono::steady_clock::now()-callback).count());
  }
  out.cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  out.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  out.launches=piano.strike.ledger.launches;
  return out;
}

struct Isolated {
  double wall=0,cpu=0,maximumCallback=0,supplied=0,finalEnergy=0,radiation=0,player=0,maximumBalance=0;
};
Isolated isolated(const keyra::physics::AcousticConfig& configuration) {
  keyra::physics::AcousticLoad load;
  if (!load.prepare(configuration)) throw std::runtime_error("Invalid isolated load");
  load.setCouplingEnabled(false);
  Isolated out;
  const auto cpu=std::clock(); const auto start=std::chrono::steady_clock::now();
  for (unsigned first=0;first<rate;first+=64) {
    const auto block=std::chrono::steady_clock::now();
    for (unsigned frame=first;frame<first+64;++frame) {
      if (frame==240) out.supplied+=load.applyPressureImpulse(.02);
      const auto result=load.step({0,0});
      if (!result.valid) throw std::runtime_error("Invalid isolated acoustic result");
      out.maximumBalance=std::max(out.maximumBalance,std::abs(result.balanceResidual));
      out.radiation+=result.radiationDissipation; out.player+=result.playerDissipation;
    }
    out.maximumCallback=std::max(out.maximumCallback,std::chrono::duration<double>(std::chrono::steady_clock::now()-block).count());
  }
  out.wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  out.cpu=double(std::clock()-cpu)/CLOCKS_PER_SEC; out.finalEnergy=load.energy();
  return out;
}
Stats difference(const std::vector<float>& a,const std::vector<float>& b,std::vector<float>* output=nullptr) {
  Stats stats;
  if (output) output->resize(a.size());
  for (unsigned i=0;i<a.size();++i) {
    const double x=double(a[i])-b[i]; stats.add(x); if(output)(*output)[i]=float(x);
  }
  return stats;
}
}

int main(int argc,char** argv) {
  try {
    if (argc!=2) throw std::runtime_error("Usage: keyra_full_acoustic_probe OUTPUT_DIRECTORY");
    const std::string directory=argv[1];
    if (directory.find_first_of("\"\\\n\r\t")!=std::string::npos)
      throw std::runtime_error("Unsupported output directory characters");
    std::filesystem::create_directories(directory);
    std::vector<Render> versions; versions.reserve(12);
    for (unsigned lid=0;lid<3;++lid) for (unsigned player=0;player<3;++player) {
      const double presence=player==0?0:1,distance=player==1?.2:player==2?2:.6;
      const std::string name="lid-"+std::to_string(lid)+"-player-"+std::to_string(player);
      versions.push_back(render(name,.5*lid,presence,distance));
    }
    for (const char* ablation:{"source-off","coupling-off","load-off"})
      versions.push_back(render(ablation,.5,0,.6,ablation));
    // One export gain for every target, proxy stem, Pa diagnostic and delta.
    // Sharing gain preserves differences but does NOT equate unlike units.
    double maximum=0;
    for (const auto& version:versions) for (const auto& s:version.stats) maximum=std::max(maximum,s.peak);
    double maximumDelta=0;
    for (unsigned i=0;i<versions.size();++i)
      maximumDelta=std::max(maximumDelta,difference(versions[i].audio[0],versions[3].audio[0]).peak);
    const double gain=.8/std::max(maximum,maximumDelta);
    auto write=[&](const std::string& name,const std::vector<float>& raw) {
      std::vector<float> data=raw; for (auto& x:data) x=float(x*gain);
      grand::wav(directory+"/"+name+".wav",data,rate);
    };
    std::ostringstream json; json<<std::setprecision(17);
    json<<"{\n\"schema_version\":1,\"sample_rate\":"<<rate<<",\"seconds\":"<<seconds
      <<",\"room\":\"none\",\"seed\":"<<versions[0].config.seed<<",\"variation\":0.65,"
      <<"\"original_pressure_proxy_gain\":1,\"mechanical_impulse_level\":0.025,\"direct_air_mix_gain\":0,"
      <<"\"shared_export_gain\":"<<gain<<",\"proxy_highpass_hz\":24,\"cavity_pressure_highpass_hz\":0,"
      <<"\"air_source_event\":{\"frame\":240,\"pressure_impulse_pa_seconds\":0.02},"
      <<"\"events\":[";
    for (unsigned i=0;i<events.size();++i) {
      if(i)json<<',';
      const auto& e=events[i];
      json<<"{\"frame\":"<<e.frame<<",\"kind\":\""<<e.kind<<"\",\"note\":"<<e.note<<",\"value\":"<<e.value<<'}';
    }
    json<<"],\n\"timing_scope\":\"Indicative shared-Linux-host throughput; preparation/allocation/export excluded; per-sample metrics and interval full-energy scans included. 64-frame chunks are a probe loop, not a host callback or deadline guarantee.\","
      <<"\"isolated_scope\":\"One uncoupled cavity, no board, strings or mechanisms; one second, pressure source at frame 240; same prepared geometry/player controls as its full network.\","
      <<"\"versions\":[\n";
    for (unsigned i=0;i<versions.size();++i) {
      const auto& v=versions[i]; const auto& c=v.config.acoustic[0]; const auto b=isolated(c);
      if(i)json<<",\n";
      json<<"{\"name\":\""<<v.name<<"\",\"ablation\":\""<<v.ablation<<"\",\"lid\":"<<c.lidPosition
        <<",\"player_presence\":"<<c.player.presence<<",\"player_distance_m\":"<<c.player.distanceM
        <<",\"full_cpu_seconds\":"<<v.cpu<<",\"full_wall_seconds\":"<<v.wall
        <<",\"full_cpu_realtime_factor\":"<<v.cpu/seconds<<",\"maximum_probe_block_seconds\":"<<v.maximumCallback
        <<",\"maximum_cavity_energy_j\":"<<v.maximumAir<<",\"maximum_board_energy_j\":"<<v.maximumBoard
        <<",\"maximum_string_energy_j\":"<<v.maximumStrings<<",\"air_external_work_j\":"<<v.suppliedAir
        <<",\"air_board_work_j\":"<<v.airBoardWork<<",\"air_coupling_dissipation_j\":"<<v.couplingLoss
        <<",\"air_radiation_dissipation_j\":"<<v.radiationLoss<<",\"air_player_dissipation_j\":"<<v.playerLoss
        <<",\"air_internal_and_numerical_dissipation_j\":"<<v.internalLoss
        <<",\"maximum_air_balance_residual_j\":"<<v.maximumBalance<<",\"maximum_actual_board_work_residual_j\":"<<v.maximumReaction
        <<",\"strike_launches\":"<<v.launches<<",\"acoustic_frequency_hz\":"<<v.properties.frequencyHz
        <<",\"aperture_ka\":"<<v.properties.apertureKa<<",\"low_ka_approximation\":"<<(v.properties.lowKaApproximation?"true":"false")
        <<",\"isolated\":{\"cpu_seconds\":"<<b.cpu<<",\"wall_seconds\":"<<b.wall
        <<",\"maximum_probe_block_seconds\":"<<b.maximumCallback<<",\"external_work_j\":"<<b.supplied
        <<",\"final_energy_j\":"<<b.finalEnergy<<",\"radiation_dissipation_j\":"<<b.radiation
        <<",\"player_dissipation_j\":"<<b.player<<",\"maximum_balance_residual_j\":"<<b.maximumBalance<<"},\"stems\":[";
      for (unsigned stem=0;stem<stems;++stem) {
        if(stem)json<<',';
        const std::string name=v.name+"-"+stemNames[stem]; write(name,v.audio[stem]);
        json<<"{\"name\":\""<<stemNames[stem]<<"\",\"file\":\""<<name<<".wav\",\"raw_rms\":"<<v.stats[stem].rms(frames*2)
          <<",\"raw_peak\":"<<v.stats[stem].peak<<",\"unit\":\""<<(stem==3?"Pa in authored cavity geometry":"original pressure proxy; uncalibrated")<<"\"}";
      }
      std::vector<float> delta;
      const auto d=difference(v.audio[0],versions[3].audio[0],&delta);
      const std::string deltaName=v.name+"-minus-lid-1-player-0.wav"; write(deltaName.substr(0,deltaName.size()-4),delta);
      json<<"],\"difference_from_lid_half_player_absent\":{\"file\":\""<<deltaName<<"\",\"raw_rms\":"<<d.rms(frames*2)<<",\"raw_peak\":"<<d.peak<<"}}";
    }
    json<<"],\n\"limits\":[\"Research-only first-order composition after complete original mechanics; no original source, calibration, controller or production API changes.\","
      <<"\"Physical cavity pressure and original proxy pressure units are not calibrated to each other; cavity stem is diagnostic and direct air mix gain is zero. Sharing export gain does not make their levels physically comparable.\","
      <<"\"Source-off removes only the injected cavity pressure event; passive air can still be excited by strings, board and mechanisms. Coupling-off retains cavity source and losses. Load-off removes the entire air module.\","
      <<"\"Mechanism gain, cavity geometry, board moving area, resistance and player proximity/loss budget are authored. No fit to ambiguous library pedal low frequencies or material claims.\","
      <<"\"Lid 0/0.5/1 are separately prepared static aperture geometries; not live lid motion. One cavity/aperture mode is not a three-dimensional air field, lid plate, room or anatomical player.\","
      <<"\"Same notes, pedal events, seed, gains and room-none path across targets; only stated source/coupling/load ablations differ.\","
      <<"\"No recording/listening validation, production quality, SDK or host real-time guarantee. Reserved mechanism corpus remains unopened.\"]\n}\n";
    std::ofstream file(directory+"/report.json"); file<<json.str();
    if(!file)throw std::runtime_error("Cannot write acoustic network report");
    std::cout<<"Wrote "<<versions.size()<<" full-network targets and isolated-air benchmarks to "<<directory<<"/report.json\n";
  } catch (const std::exception& e) { std::cerr<<"full acoustic network probe: "<<e.what()<<'\n'; return 1; }
}
