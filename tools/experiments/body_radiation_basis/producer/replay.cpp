#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

// PRIVATE reconstruction only. No string/contact state, recording, fitting or audio export.
constexpr int Modes=475, Bands=6, Channels=2, Columns=14, Rate=48000;
constexpr double dt=1.0/Rate;
constexpr std::array<double,Bands> centers{{55,140,350,900,2400,6500}};
constexpr std::array<double,Bands> testAlpha{{.5,.75,1,1.25,1.5,2}};
using Stereo=std::array<double,2>;
using Row=std::array<double,Columns>;
struct Mode {float q=0,p=0;double w,sigma,c,s,damp;std::array<double,3> port;Stereo mic;std::array<double,Bands> phi{};};
struct Stats {
  uint64_t frames=0,directDifferent=0,nonfinite=0,forceMismatch=0;double directError=0,partitionError=0,partitionScaled=0,weightedError=0,weightedScaled=0,hpError=0,maxAbsSum=0,maxHPAbs=0;
};
double max(double a,double b){return std::max(a,b);}
int main(int argc,char**argv){
  if(argc!=8){std::cerr<<"usage: replay COEFF TRACE OUTPUT STATS CHUNK_MODE FORCE_PROOF MIDI\n";return 2;}
  std::ifstream cf(argv[1],std::ios::binary),in(argv[2],std::ios::binary);std::ofstream out(argv[3],std::ios::binary),js(argv[4]);
  std::ifstream proof(argv[6],std::ios::binary);const int midi=std::atoi(argv[7]);
  if(!cf||!in||!out||!js||!proof||midi<21||midi>108)return 3;
  std::array<Mode,Modes> modes{};double maxPhiSumError=0,minPhi=1,maxPhi=0;std::array<unsigned,Bands> support{};
  for(int i=0;i<Modes;++i){std::array<double,11> r{};cf.read(reinterpret_cast<char*>(r.data()),sizeof(r));if(!cf||r[0]!=i)return 4;
    auto&z=modes[i];z.w=r[1];z.sigma=r[2];z.c=r[3];z.s=r[4];z.damp=r[5];for(int g=0;g<3;++g)z.port[g]=r[6+g];z.mic={{r[9],r[10]}};
    const double f=z.w/(2*std::acos(-1.0));
    if(f<=centers.front())z.phi[0]=1;
    else if(f>=centers.back())z.phi[Bands-1]=1;
    else for(int b=0;b<Bands-1;++b)if(f>=centers[b]&&f<centers[b+1]){
      const double t=(std::log(f)-std::log(centers[b]))/(std::log(centers[b+1])-std::log(centers[b]));
      const double hi=.5-.5*std::cos(std::acos(-1.0)*t);z.phi[b]=1-hi;z.phi[b+1]=hi;break;
    }
    double sum=0;for(int b=0;b<Bands;++b){const auto p=z.phi[b];sum+=p;minPhi=std::min(minPhi,p);maxPhi=max(maxPhi,p);if(p>0)++support[b];}maxPhiSumError=max(maxPhiSumError,std::abs(sum-1));
  }
  char extra;if(cf.read(&extra,1))return 5;
  constexpr std::array<int,6> chunks{{1,3,17,64,129,7}};const bool alternate=std::string(argv[5])=="alternate";size_t ci=0;
  Stats stats;std::array<Stereo,Bands+1> hp{},previous{};const double pole=std::exp(-2*std::acos(-1.0)*24/Rate);
  const double eps=std::numeric_limits<double>::epsilon(),gamma=Modes*eps/(1-Modes*eps);
  while(true){
    const int count=alternate?chunks[ci++%chunks.size()]:64;std::vector<std::array<double,15>> trace(count);in.read(reinterpret_cast<char*>(trace.data()),count*sizeof(trace[0]));const auto bytes=in.gcount();
    if(bytes%sizeof(trace[0]))return 6;const size_t n=bytes/sizeof(trace[0]);if(!n)break;std::vector<Row> buffer(n);
    for(size_t k=0;k<n;++k){
      const auto&t=trace[k];auto&r=buffer[k];Stereo absSum{},weighted{};
      std::array<double,91> allForce{};allForce[midi-21]=t[11];for(int g=0;g<3;++g)allForce[88+g]=t[12+g];
      uint64_t forceHash=14695981039346656037ull;const auto* data=reinterpret_cast<const unsigned char*>(allForce.data());for(size_t j=0;j<sizeof(allForce);++j){forceHash^=data[j];forceHash*=1099511628211ull;}
      std::array<uint64_t,3> forceProof{};proof.read(reinterpret_cast<char*>(forceProof.data()),sizeof(forceProof));if(!proof)return 9;
      if(forceProof[0]!=stats.frames||forceProof[1]!=forceHash||forceProof[2]!=forceHash)++stats.forceMismatch;
      for(auto&z:modes){
        const double v=z.p*z.damp,y=z.q;z.q=z.c*y+z.s*v;z.p=(z.c*v-z.s*y)*z.damp;
        double force=0;for(int g=0;g<3;++g)force-=z.port[g]*t[12+g];z.p+=dt*force/z.w;
        const double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+force;
        double weight=0;for(int b=0;b<Bands;++b)weight+=testAlpha[b]*z.phi[b];
        for(int ch=0;ch<Channels;++ch){const double contribution=acc*z.mic[ch];r[ch]+=contribution;absSum[ch]+=std::abs(contribution);weighted[ch]+=acc*(z.mic[ch]*weight);
          for(int b=0;b<Bands;++b)r[2+2*b+ch]+=contribution*z.phi[b];
        }
      }
      for(int ch=0;ch<Channels;++ch){
        const double error=std::abs(r[ch]-t[2+ch]);stats.directError=max(stats.directError,error);if(std::memcmp(&r[ch],&t[2+ch],sizeof(double)))++stats.directDifferent;
        double sum=0,recombined=0;for(int b=0;b<Bands;++b){sum+=r[2+2*b+ch];recombined+=testAlpha[b]*r[2+2*b+ch];}
        const double pe=std::abs(sum-r[ch]),we=std::abs(recombined-weighted[ch]);stats.partitionError=max(stats.partitionError,pe);stats.weightedError=max(stats.weightedError,we);
        const double bound=8*gamma*absSum[ch]+32*eps*absSum[ch];stats.partitionScaled=max(stats.partitionScaled,bound?pe/bound:pe);stats.weightedScaled=max(stats.weightedScaled,bound?we/(2*bound):we);stats.maxAbsSum=max(stats.maxAbsSum,absSum[ch]);
        for(int b=0;b<Bands+1;++b){const double x=r[2*b+ch];hp[b][ch]=pole*(hp[b][ch]+x-previous[b][ch]);previous[b][ch]=x;stats.maxHPAbs=max(stats.maxHPAbs,std::abs(hp[b][ch]));}
        double hs=0;for(int b=1;b<Bands+1;++b)hs+=hp[b][ch];stats.hpError=max(stats.hpError,std::abs(hs-hp[0][ch]));
        for(double x:{weighted[ch],absSum[ch],hs,recombined,t[2+ch]})if(!std::isfinite(x))++stats.nonfinite;
        for(int b=0;b<Bands+1;++b)if(!std::isfinite(hp[b][ch]))++stats.nonfinite;
      }
      for(double x:r)if(!std::isfinite(x))++stats.nonfinite;++stats.frames;
    }
    out.write(reinterpret_cast<const char*>(buffer.data()),n*sizeof(Row));if(!out)return 7;if(n<size_t(count))break;
  }
  if(proof.read(&extra,1))return 10;
  js<<std::setprecision(17)<<"{\n\"frames\":"<<stats.frames<<",\n\"force_proof_mismatches\":"<<stats.forceMismatch<<",\n\"direct_max_error\":"<<stats.directError<<",\n\"direct_nonidentical_samples\":"<<stats.directDifferent<<",\n\"partition_max_error\":"<<stats.partitionError<<",\n\"partition_error_over_bound\":"<<stats.partitionScaled<<",\n\"positive_weight_recombination_max_error\":"<<stats.weightedError<<",\n\"positive_weight_error_over_bound\":"<<stats.weightedScaled<<",\n\"hp24_partition_max_error\":"<<stats.hpError<<",\n\"hp24_partition_bound\":"<<(32*gamma*stats.maxAbsSum+128*eps*stats.maxHPAbs)<<",\n\"max_abs_modal_sum\":"<<stats.maxAbsSum<<",\n\"nonfinite\":"<<stats.nonfinite<<",\n\"basis_min\":"<<minPhi<<",\n\"basis_max\":"<<maxPhi<<",\n\"basis_partition_max_error\":"<<maxPhiSumError<<",\n\"basis_support_modes\":[";
  for(int b=0;b<Bands;++b){if(b)js<<',';js<<support[b];}js<<"],\n\"final_qp\":[";for(int i=0;i<Modes;++i){if(i)js<<',';js<<'['<<modes[i].q<<','<<modes[i].p<<']';}js<<"],\n\"final_hp_previous\":[";for(int b=0;b<Bands+1;++b){if(b)js<<',';js<<'['<<hp[b][0]<<','<<hp[b][1]<<','<<previous[b][0]<<','<<previous[b][1]<<']';}js<<"]\n}\n";
  return stats.nonfinite?8:0;
}
