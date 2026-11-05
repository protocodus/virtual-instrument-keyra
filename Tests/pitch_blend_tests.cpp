// Every key between two recorded pitches, on every piano, at every recorded
// layer, halfway between each two and at both ends of the velocity range, as
// the engine blends the two pitches' fits where the keyboard network's table
// (MeasuredNetworkKeys.h) holds none of the key: each partial both pitches
// have plays, over the 50-750 ms window the layers' levels are measured over,
// its power over both channels at its place between theirs in dB, each
// channel's power between theirs, and its balance, the left channel's power
// over the right's, at its place between theirs in dB unless that would take
// a channel outside both pitches': then that channel stops at the pitch's
// power it would pass. Its right channel lags the left at its place between
// theirs along the shorter arc. Read from the blend, against the two pitches'
// own partials at the same velocity.
// Held as one power over both channels alone, a key could play one channel
// far outside both pitches' while the other made up for it: the Hamburg's E1
// put its twelfth partial's right channel 11.4 dB under both C1's and G1's.
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct PitchBlendTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
double db(double power){return 10*std::log10(power);}
// How far x lies outside the range of a and b, in their unit; 0 inside.
double outside(double x,double a,double b){return std::max({0.,std::min(a,b)-x,x-std::max(a,b)});}
}

int main(){
  keyra::Engine engine(48000);
  auto& impl=keyra::PitchBlendTestObserver::state(engine);
  int keys=0,partials=0,held=0,lags=0;
  double worstTotal=0,worstChannel=0,worstBalance=0,worstHeld=0,worstRadians=0;
  for(int p=0;p<keyra::pianoCount;++p){
    const keyra::Model& m=keyra::models[p];
    std::vector<double> velocities{1.,127.};
    for(int layer=0;layer<m.layers;++layer){
      velocities.push_back(m.layerVelocity[layer]);
      if(layer+1<m.layers)velocities.push_back(.5*(m.layerVelocity[layer]+m.layerVelocity[layer+1]));
    }
    const auto* cache=&impl.partialLanes[m.partialFirst];
    for(int upper=1;upper<m.anchorCount;++upper){
      const auto& a=m.anchors[upper-1];const auto& b=m.anchors[upper];
      for(int note=a.note+1;note<b.note;++note)for(const double velocity:velocities){
        keyra::Side x;x.m=&m;x.a=&a;x.b=&b;x.upper=upper;x.v=velocity;
        x.t=static_cast<double>(note-a.note)/(b.note-a.note);
        const int count=impl.blended(x,p);++keys;
        // The series merges the two pitches' partials by order, as here.
        int i=a.first,j=b.first;
        for(int n=0;n<count;++n){
          const int oa=i<a.first+a.count?m.partials[i].order:1<<30,ob=j<b.first+b.count?m.partials[j].order:1<<30;
          if(oa!=ob){if(oa<ob)++i;else ++j;continue;}
          const keyra::PartialData& played=impl.seriesData[p][n];
          const auto pa=keyra::single(m,m.partials[i],cache[i],velocity),pb=keyra::single(m,m.partials[j],cache[j],velocity);
          ++i;++j;++partials;
          const auto [la,ra]=keyra::windowPowers(pa);
          const auto [lb,rb]=keyra::windowPowers(pb);
          const auto [ld,rd]=keyra::windowPowers(played);
          check(la>0&&lb>0&&ld>0&&ra>0&&rb>0&&rd>0,"a recorded partial sounds in both channels");
          worstTotal=std::max(worstTotal,std::abs(db(ld+rd)-keyra::mix(db(la+ra),db(lb+rb),x.t)));
          worstChannel=std::max({worstChannel,outside(db(ld),db(la),db(lb)),outside(db(rd),db(ra),db(rb))});
          const double balance=std::abs(db(ld/rd)-keyra::mix(db(la/ra),db(lb/rb),x.t));
          if(balance>1e-9){
            // Moved off its place: a channel must sit at one of the pitches'.
            const double edge=std::min({std::abs(db(ld)-db(la)),std::abs(db(ld)-db(lb)),std::abs(db(rd)-db(ra)),std::abs(db(rd)-db(rb))});
            worstHeld=std::max(worstHeld,edge);worstBalance=std::max(worstBalance,balance);++held;
          }
          const keyra::Complex ca=keyra::windowChannels(pa,keyra::windowPairs(pa)),cb=keyra::windowChannels(pb,keyra::windowPairs(pb)),
                               cd=keyra::windowChannels(played,keyra::windowPairs(played));
          if(std::hypot(ca.re,ca.im)>0&&std::hypot(cb.re,cb.im)>0&&std::hypot(cd.re,cd.im)>0){
            const double from=std::atan2(ca.im,ca.re),to=std::atan2(cb.im,cb.re);
            const double place=from+x.t*std::remainder(to-from,2*keyra::pi);
            worstRadians=std::max(worstRadians,std::abs(std::remainder(std::atan2(cd.im,cd.re)-place,2*keyra::pi)));
            ++lags;
          }
        }
      }
    }
  }
  std::cout<<"keys_by_velocity="<<keys<<" shared_partials="<<partials<<" lags="<<lags
           <<" worst_total_power_off_db="<<worstTotal<<" worst_channel_outside_db="<<worstChannel
           <<" balances_held="<<held<<" worst_balance_held_db="<<worstBalance<<" worst_held_channel_off_edge_db="<<worstHeld
           <<" worst_lag_off_rad="<<worstRadians<<'\n';
  check(keys>0&&partials>0&&lags>0,"the keyboard is covered");
  // The blend sets these exactly; the bounds only take its rounding.
  check(worstTotal<1e-9,"a key between two recorded pitches plays each partial's power at its place between theirs");
  check(worstChannel<1e-9,"a key between two recorded pitches plays each partial's channels between theirs");
  check(worstHeld<1e-9,"a partial's balance leaves its place between the pitches' only to hold a channel at one of theirs");
  check(worstRadians<1e-9,"a key between two recorded pitches lags each partial's channels at its place between theirs");
  return failures?1:0;
}
