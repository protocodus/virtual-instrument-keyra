// Offline, observer-only 88-key scalar workload. No piano mechanics/SDK claim.
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
struct Pole {double a=0,b=0,g=0;};
struct Observer {
 unsigned inputs=0;std::vector<Pole> pole;std::vector<double> weights[2];
 std::vector<std::array<double,2>> state[2];
 explicit Observer(const char* file){
  std::ifstream in(file);unsigned count;
  if(!(in>>inputs>>count)||inputs<1||inputs>2||count>32)throw std::runtime_error("invalid observer header");
  pole.resize(count);for(auto& p:pole)if(!(in>>p.a>>p.b>>p.g)||std::hypot(p.a,p.b)>=1)throw std::runtime_error("invalid pole");
  for(auto& w:weights){w.resize(inputs*(1+2*count));for(auto& x:w)if(!(in>>x)||!std::isfinite(x))throw std::runtime_error("invalid observer weight");}
  for(unsigned i=0;i<inputs;++i)state[i].resize(count);
 }
 void reset(){for(auto& s:state)for(auto& x:s)x={};}
 std::array<double,2> step(double reaction,double contact){
  const double in[]={reaction,contact};std::array<double,2> out{};
  for(unsigned k=0;k<inputs;++k){const auto off=k*(1+2*pole.size());
   for(unsigned ch=0;ch<2;++ch)out[ch]+=weights[ch][off]*in[k];
   for(unsigned i=0;i<pole.size();++i){const auto& p=pole[i];auto& s=state[k][i];
    const double old=s[0];s[0]=p.g*in[k]+p.a*old-p.b*s[1];s[1]=p.b*old+p.a*s[1];
    for(unsigned ch=0;ch<2;++ch)out[ch]+=weights[ch][off+1+2*i]*s[0]+weights[ch][off+2+2*i]*s[1];
   }
  }return out;
 }
};
int main(int argc,char** argv)try {
 if(argc!=3){std::cerr<<"usage: probe_waveguide_radiation_cost C2.cfg C4.cfg\n";return 1;}
 std::vector<Observer> bank;bank.reserve(88);for(unsigned i=0;i<88;++i)bank.emplace_back(argv[1+i%2]);
 std::array<double,3> cpu{};double checksum=0;
 for(unsigned trial=0;trial<3;++trial){for(auto& o:bank)o.reset();uint32_t seed=12345;
  const auto start=std::clock();
  for(unsigned frame=0;frame<24000;++frame)for(auto& o:bank){seed=seed*1664525u+1013904223u;
   const double x=(double(seed)/4294967296.-.5)*.01;
   const auto p=o.step(x,x*.15);checksum+=p[0]+p[1];}
  cpu[trial]=double(std::clock()-start)/CLOCKS_PER_SEC;
 }
 std::cout<<std::setprecision(17)<<"{\"sample_rate\":48000,\"voices\":88,\"audio_seconds\":0.5,\"trials_cpu_seconds\":["<<cpu[0]<<','<<cpu[1]<<','<<cpu[2]<<"],\"checksum\":"<<checksum<<",\"finite\":"<<(std::isfinite(checksum)?"true":"false")<<",\"observer_sections_per_input\":"<<bank[0].pole.size()<<",\"inputs\":"<<bank[0].inputs<<",\"scope\":\"Observer only; C2/C4 mixed88 independent fixed-pole filters, synthesized input, scalar GNU strict FP; no string/board/mechanism/host cost\"}\n";
 return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
