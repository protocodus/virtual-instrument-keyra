#include "CausalRadiation.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <random>
#include <vector>
using keyra_causal::Observer;using keyra_causal::Vec;
int main(int argc,char**argv){if(argc!=2)return 2;grand::Options options;options.sampleRate=48000;grand::Piano model(options);Observer observer;if(!observer.prepare(model))return 3;
 const std::string dir=argv[1];bool all=true;std::printf("{\"readout\":\"DC_stationary_corrected_endpoint\",\"passivity\":[");bool first=true;
 for(double scale:{0.,1.,1000.}){observer.reset();for(unsigned g=0;g<3;++g)observer.resistance[g]=scale*std::array<double,3>{{32.30000000000002,68.85000000000004,94.34999999999987}}[g];if(!observer.buildInverse())return 4;
  std::mt19937 random(412);std::normal_distribution<double> normal;for(auto& n:observer.nodes){n.x=1.e-4*normal(random);n.v=1.e-4*normal(random);}const double initial=observer.energy();double maximum=1,maxRise=0,maxBalance=0,previous=initial;bool valid=true;
  for(unsigned i=0;i<24000;++i){const auto r=observer.stepDriven({});valid=valid&&r.valid;maximum=std::max(maximum,r.energyAfter/initial);maxRise=std::max(maxRise,(r.energyAfter-previous)/initial);maxBalance=std::max(maxBalance,std::abs(r.balanceResidual)/initial);previous=r.energyAfter;}
  const bool pass=valid&&maximum<=1+1.e-11&&maxRise<=1.e-11&&maxBalance<=1.e-11;all=all&&pass;if(!first)std::printf(",");first=false;
  std::printf("{\"resistance_scale\":%.17g,\"frames\":24000,\"initial_energy_J\":%.17g,\"max_energy_ratio\":%.17g,\"max_step_rise_over_initial\":%.17g,\"max_balance_over_initial\":%.17g,\"final_energy_ratio\":%.17g,\"passed\":%s}",scale,initial,maximum,maxRise,maxBalance,previous/initial,pass?"true":"false");
 }
 for(unsigned g=0;g<3;++g)observer.resistance[g]=std::array<double,3>{{32.30000000000002,68.85000000000004,94.34999999999987}}[g];if(!observer.buildInverse())return 5;
 observer.reset();double dcMax=0,dcLast=0;for(unsigned i=0;i<240000;++i){const auto r=observer.stepDriven({.3,-.1,.2});if(!r.valid)return 6;if(i>=235200)for(double p:r.pressure)dcMax=std::max(dcMax,std::abs(p));dcLast=std::hypot(r.pressure[0],r.pressure[1]);}
 const bool dcPass=dcMax<1.e-7;all=all&&dcPass;
 std::printf("],\"constant_force\":{\"input\":[0.3,-0.1,0.2],\"frames\":240000,\"last100ms_max_pressure\":%.17g,\"last_stereo_norm\":%.17g,\"passed\":%s},\"forced_cases\":[",dcMax,dcLast,dcPass?"true":"false");
 struct Test{double hz;unsigned group;};const std::array<Test,6>tests{{{31.,1},{65.4,0},{784.5,1},{2080.,2},{10000.,1},{19000.,1}}};first=true;
 for(unsigned index=0;index<tests.size();++index){const auto test=tests[index];observer.reset();const double phase=2*grand::pi*test.hz/48000.;FILE*f=std::fopen((dir+"/forced-"+std::to_string(index)+".f64le").c_str(),"wb");if(!f)return 7;
  for(unsigned i=0;i<192000;++i){Vec u{};u[test.group]=std::cos(phase*i);const auto r=observer.stepDriven(u);if(!r.valid)return 8;if(i>=144000){const double row[3]={double(i),r.pressure[0],r.pressure[1]};if(std::fwrite(row,sizeof(double),3,f)!=3)return 9;}}std::fclose(f);
  if(!first)std::printf(",");first=false;std::printf("{\"id\":%u,\"Hz\":%.17g,\"group\":%u,\"settle_frames\":144000,\"fit_frames\":48000}",index,test.hz,test.group);
 }
 // Same deterministic sample sequence after reset, with different outer block
 // partitioning. No note/reset interface exists on the observer itself.
 std::array<std::array<double,2>,4096> a{},b{};const auto play=[&](auto& result,bool fragmented){unsigned cursor=0,part=0;const unsigned sizes[]={1,3,17,64};while(cursor<result.size()){unsigned n=std::min<unsigned>(result.size()-cursor,fragmented?sizes[part++%4]:result.size());for(unsigned j=0;j<n;++j){const unsigned i=cursor+j;const auto r=observer.stepDriven({std::sin(i*.13),std::cos(i*.08),.2*std::sin(i*.21)});result[i]=r.pressure;}cursor+=n;}};
 observer.reset();play(a,false);observer.reset();play(b,true);const bool partition=std::memcmp(a.data(),b.data(),sizeof(a))==0;all=all&&partition;
 std::printf("],\"reset_partition_byte_identical\":%s,\"passed\":%s}\n",partition?"true":"false",all?"true":"false");return all?0:10;}
