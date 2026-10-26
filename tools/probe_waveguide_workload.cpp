#define main keyra_preserved_renderer_main
#include "../src/full_reference/grand.cpp"
#undef main
#include "keyra/physics/WaveguideString.h"
#include <ctime>

using Wave=keyra::physics::WaveguideString;
bool readWave(const char* path,Wave::Config& c){
  std::ifstream f(path);std::string name;double fundamental,B,Z,position;
  if(!(f>>name>>fundamental>>B>>Z>>position))return false;
  c.impedance=Z;
  auto read=[&](Wave::PathConfig& p){
    if(!(f>>p.delaySamples>>p.lossGain>>p.lossMix>>p.allpassCount)||
       p.allpassCount>Wave::allpassCapacity)return false;
    for(unsigned j=0;j<p.allpassCount;++j)if(!(f>>p.allpass[j]))return false;
    return true;
  };
  if(!read(c.left)||!read(c.toBridge))return false;
  c.fromBridge=c.toBridge;
  Wave validation;return validation.prepare(c);
}
struct Primary {
  grand::Modes mode;
  double step(double force){mode.freeDampedStep();if(force!=0)mode.force(force);return mode.portVelocity();}
};
int main(int argc,char** argv){
  if(argc!=4)return 2;
  std::array<Wave::Config,3> config{};
  for(unsigned i=0;i<config.size();++i)if(!readWave(argv[i+1],config[i]))return 2;
  grand::Options options;options.sampleRate=48000;grand::Piano piano(options);
  std::vector<Primary> modal(piano.strings.size());std::vector<Wave> wave(piano.strings.size());
  std::size_t primaryCount=0,secondaryCount=0,hybridCount=0,hybridWaveCount=0;
  std::ofstream counts("out/waveguide-study/mode-counts.csv");counts<<"string,midi,unison,primary_modes,secondary_modes,f1_hz,B\n";
  for(std::size_t i=0;i<piano.strings.size();++i){
    const auto& string=piano.strings[i];auto& out=modal[i].mode;unsigned primary=0,secondary=0;
    for(std::size_t j=0;j<string.m.size();++j){
      if(string.m.polarization[j]){++secondary;continue;}++primary;
      out.add(string.m.omega[j]/(2*grand::pi),string.m.hammer[j],string.m.b[j],string.m.loss[j],string.m.damper[j],1./48000,string.m.partial[j],0);
    }
    primaryCount+=primary;secondaryCount+=secondary;
    if(string.note>=72)hybridCount+=primary;else ++hybridWaveCount;
    counts<<i<<','<<string.note<<','<<string.unison<<','<<primary<<','<<secondary<<','<<string.m.omega[0]/(2*grand::pi)<<','<<piano.keys[string.note-21].B<<'\n';
    // This is a computational workload, not a fitted full-range instrument.
    // Select existing anchor paths; only integer storage is resized for the
    // actual source frequency where feasible. High treble stays unvalidated.
    auto c=config[string.note<48?0:string.note<72?1:2];
    const double scale=(string.note<48?65.01421446843138:string.note<72?261.6038708567966:1050.3644434995263)/(string.m.omega[0]/(2*grand::pi));
    c.left.delaySamples=std::max(1u,unsigned(std::round(c.left.delaySamples*scale)));
    c.toBridge.delaySamples=std::max(1u,unsigned(std::round(c.toBridge.delaySamples*scale)));
    c.fromBridge=c.toBridge;if(!wave[i].prepare(c))return 3;
  }
  std::cout<<std::setprecision(17)<<"{\"strings\":"<<piano.strings.size()<<",\"primary_modes\":"<<primaryCount<<",\"secondary_modes_excluded\":"<<secondaryCount
    <<",\"board_modes_excluded\":"<<piano.board.size()<<",\"hybrid_modal_midi_min\":72,\"hybrid_waveguide_strings\":"<<hybridWaveCount<<",\"hybrid_modal_primary_modes\":"<<hybridCount<<",\"variants\":[";
  constexpr unsigned frames=24000;double checksum=0;
  for(unsigned variant=0;variant<3;++variant){
    std::array<double,3> cpus{},walls{};
    for(unsigned trial=0;trial<3;++trial){
      const auto start=std::chrono::steady_clock::now();const auto begin=std::clock();
      for(unsigned frame=0;frame<frames;++frame)for(std::size_t i=0;i<wave.size();++i){
        const double force=frame==unsigned(i%31)?1.:0.;
        if(variant==0||(variant==2&&piano.strings[i].note>=72))checksum+=modal[i].step(force);
        else checksum+=wave[i].step(force).bridgeForce;
      }
      cpus[trial]=double(std::clock()-begin)/CLOCKS_PER_SEC/(frames/48000.);
      walls[trial]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()/(frames/48000.);
    }
    std::sort(cpus.begin(),cpus.end());std::sort(walls.begin(),walls.end());
    if(variant)std::cout<<',';
    std::cout<<"{\"name\":\""<<(variant==0?"all_modal_primary":variant==1?"all_waveguide_s16_workload":"hybrid_s16_modal_from_C5")<<"\",\"median_cpu_per_audio_second\":"<<cpus[1]<<",\"median_wall_per_audio_second\":"<<walls[1]<<'}';
  }
  std::cout<<"],\"checksum\":"<<checksum<<"}\n";
}
