#include "candidate/src/full_instrument/PreparedModel.h"
#include <cstring>
#include <iostream>
#include <random>
struct Samples{std::array<grand::Modes,3> lanes;};
uint64_t mismatches=0,rows=0,fixtures=0,fallbackFixtures=0;
template<int N> void witness(size_t count,unsigned seed){
 std::mt19937 rng(seed);std::uniform_real_distribution<float> random(-1,1);Samples a,b;grand::UnisonGroup original;grand::FreeUnisonGroup fused;original.count=fused.count=N;
 for(int lane=0;lane<N;++lane){auto& m=a.lanes[lane];
  for(size_t j=0;j<count;++j){float angle=random(rng)*3,omega=20+std::abs(random(rng))*120000;
   float q=random(rng)*1e-4f,p=random(rng)*1e-4f;if(j%23==0){q=std::copysign(0.f,q);p=std::copysign(0.f,p);}if(j%17==0){q=std::copysign(1e-38f,q);p=std::copysign(1e-38f,p);}
   m.q.push_back(q);m.p.push_back(p);m.c.push_back(std::cos(angle));m.s.push_back(std::sin(angle));m.damp.push_back(.6f+.4f*std::abs(random(rng)));
   original.omega[lane].push_back(omega);original.inverse[lane].push_back(float(1.0/omega));}
  b.lanes[lane]=m;auto& f=b.lanes[lane];original.velocity[lane]=m.p.data();fused.velocity[lane]=f.p.data();fused.position[lane]=f.q.data();fused.cosine[lane]=f.c.data();fused.sine[lane]=f.s.data();fused.damping[lane]=f.damp.data();fused.omega[lane]=original.omega[lane];fused.inverse[lane]=original.inverse[lane];}
 for(size_t j=0;j<count;++j){const float c=j%5==0?std::copysign(0.f,random(rng)):.3f*std::abs(random(rng));original.coefficient.push_back(c);fused.coefficient.push_back(c);}
 // Exercise live damping storage updates, not cached damping scalar values.
 for(int tick=0;tick<5;++tick){
  for(int lane=0;lane<N;++lane)for(size_t j=0;j<count;++j){float value=.2f+.8f*std::abs(random(rng));a.lanes[lane].damp[j]=b.lanes[lane].damp[j]=value;}
  for(int lane=0;lane<N;++lane)a.lanes[lane].freeDampedStep();original.scalarStep<N>();fused.fusedStep<N>();
  for(int lane=0;lane<N;++lane){const auto& x=a.lanes[lane];const auto& y=b.lanes[lane];mismatches+=std::memcmp(x.q.data(),y.q.data(),count*sizeof(float))!=0;mismatches+=std::memcmp(x.p.data(),y.p.data(),count*sizeof(float))!=0;}
  rows+=count;++fixtures;
 }
 // Uncovered-mode run kernel preserves the same float recurrence across splits.
 for(int lane=0;lane<N;++lane){auto x=a.lanes[lane],y=x;x.freeDampedStep();const size_t middle=count/2;
  for(auto range:{std::pair<size_t,size_t>{0,middle},{middle,count}}){grand::FreeModeRun run;run.count=range.second-range.first;run.q=y.q.data()+range.first;run.p=y.p.data()+range.first;run.c=y.c.data()+range.first;run.s=y.s.data()+range.first;run.damp=y.damp.data()+range.first;run.step();}
  mismatches+=std::memcmp(x.q.data(),y.q.data(),count*sizeof(float))!=0;mismatches+=std::memcmp(x.p.data(),y.p.data(),count*sizeof(float))!=0;++fallbackFixtures;}
}
int main(){
 for(size_t n:{1,2,3,4,5,7,8,15,16,17,31,32,33,129})for(unsigned seed=0;seed<80;++seed){witness<1>(n,seed);witness<2>(n,seed);witness<3>(n,seed);}
 std::cout<<"{\"passed\":"<<(mismatches?"false":"true")<<",\"row_updates\":"<<rows<<",\"paired_state_fixtures\":"<<fixtures<<",\"fallback_fixtures\":"<<fallbackFixtures<<",\"bit_mismatches\":"<<mismatches<<",\"Piano_constructed\":false,\"sizeof_FreeUnisonGroup\":"<<sizeof(grand::FreeUnisonGroup)<<",\"sizeof_UnisonGroup\":"<<sizeof(grand::UnisonGroup)<<",\"sizeof_FreeModeRun\":"<<sizeof(grand::FreeModeRun)<<"}\n";return mismatches?1:0;
}
