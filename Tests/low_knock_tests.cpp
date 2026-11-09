// The strike's knock under the noise bands (Tools/fit_low_knock.py,
// MeasuredLowKnock.h; the strike and the noise bands in KeyraEngine.cpp). A
// low key, whose recorded pitches on either side lie under every band, plays
// none of it; a higher key's knock lies under 400 Hz, sounds louder from a
// harder blow, and within 0.4 s it has gone. Its bands start from their
// filters' stationary state, which the engine's factor holds exactly at every
// rate, and from the same state after any silence.
#include <cmath>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct LowKnockTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
keyra::Parameters quiet(keyra::Piano piano){
  // At this Output the output stage passes the strikes untouched
  // (Tools/benchmark_recordings.py), and with the room off what the knock
  // adds is the knock alone.
  keyra::Parameters p;p.build=keyra::measuredBuild(piano);p.gain=.07f;p.room=0;return p;
}
std::vector<float> render(keyra::Engine& engine,int frames,int block){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
// Left and right interleaved, half a second of `note` struck from silence.
std::vector<float> strike(keyra::Piano piano,int note,float velocity,bool knock){
  keyra::Engine engine(48000);engine.setParameters(quiet(piano));engine.setSteadyStrikesForMeasurement(true);
  engine.setLowKnockForMeasurement(knock);engine.noteOn(note,velocity);
  return render(engine,24000,64);
}
std::vector<float> minus(const std::vector<float>& a,const std::vector<float>& b){
  std::vector<float> d(a.size());for(std::size_t i=0;i<a.size();++i)d[i]=a[i]-b[i];return d;
}
// Both channels' energy from `from` to `to` seconds, unfiltered or through
// four second-order high-passes at 500 Hz (Butterworth sections, RBJ), 49 dB
// down an octave under, at the bands' top (315 Hz).
double energy(const std::vector<float>& x,double from,double to,bool over500=false){
  const double w=2*keyra::pi*500/48000,alpha=std::sin(w)/std::sqrt(2.);
  const double a0=1+alpha,b0=(1+std::cos(w))/2/a0,b1=-(1+std::cos(w))/a0,a1=-2*std::cos(w)/a0,a2=(1-alpha)/a0;
  double sum=0;
  for(int c=0;c<2;++c){double x1[4]{},x2[4]{},y1[4]{},y2[4]{};
    for(std::size_t i=0;2*i+static_cast<std::size_t>(c)<x.size();++i){
      double y=x[2*i+static_cast<std::size_t>(c)];
      if(over500)for(int s=0;s<4;++s){const double v=y;y=b0*v+b1*x1[s]+b0*x2[s]-a1*y1[s]-a2*y2[s];
        x2[s]=x1[s];x1[s]=v;y2[s]=y1[s];y1[s]=y;}
      const double t=i/48000.;if(t>=from&&t<to)sum+=y*y;}}
  return sum;
}
}

int main(){
  using keyra::Piano;
  const Piano pianos[]{Piano::grand,Piano::upright,Piano::kawai,Piano::hamburg,Piano::newyork};
  for(Piano piano:pianos){
    const int p=static_cast<int>(piano);
    // A1: every piano's recorded pitches either side of it lie under the
    // bands' lowest (125 Hz) by a third of an octave and more, so the fit
    // measured none there.
    check(strike(piano,33,.8f,true)==strike(piano,33,.8f,false),"a low key plays no low knock");
    // F#6 (1480 Hz), under the top notes' trim. With the room off, what the
    // knock adds is the knock alone: its bands' filters hold it under 400 Hz
    // but for what its rise spreads, and on every piano it falls 10 dB and
    // more by 0.3 to 0.4 s.
    const auto on=strike(piano,90,.8f,true),off=strike(piano,90,.8f,false),knock=minus(on,off);
    const double all=energy(knock,0,.5),over=energy(knock,0,.5,true);
    const double fall=10*std::log10(energy(knock,0,.1)/energy(knock,.3,.4));
    const double harder=10*std::log10(energy(knock,0,.1)/energy(minus(strike(piano,90,.4f,true),strike(piano,90,.4f,false)),0,.1));
    std::cout<<"piano "<<p<<": "<<100*over/all<<" % of the knock over 500 Hz, falls "<<fall<<" dB by 0.3 s, "<<harder<<" dB more at velocity 0.8 than 0.4\n";
    check(all>0&&over<=.01*all,"a high key's low knock plays, 99 % of it and more under 500 Hz");
    check(fall>=10,"the low knock falls 10 dB and more by 0.3 s");
    check(harder>=3,"a harder blow knocks louder");
  }
  // The stationary state: the factor's covariance is the filters' own, from
  // their impulse response, of each section's output (its variance and its
  // covariance one sample apart) and of the source's last two samples with
  // the last output, at every rate the engine runs at. The source's
  // variance is 1/3; one second holds every band's impulse response to
  // within e^-40.
  for(double sr:{44100.,48000.,96000.}){
    keyra::Engine engine(sr);auto& impl=keyra::LowKnockTestObserver::state(engine);
    for(int b=keyra::noiseBands;b<keyra::bankBands;++b){
      const auto& band=impl.noise[static_cast<std::size_t>(b)];
      double sigma[keyra::noiseStates][keyra::noiseStates]{};
      for(int i=0;i<keyra::noiseStates;++i)for(int j=0;j<keyra::noiseStates;++j)
        for(int k=0;k<keyra::noiseStates;++k)sigma[i][j]+=band.stationary[i][k]*band.stationary[j][k];
      std::vector<double> h(static_cast<std::size_t>(sr),0.);h[0]=1;
      for(int j=0;j<keyra::noiseSections;++j){
        double x1=0,x2=0,y1=0,y2=0;
        for(double& v:h){const double y=band.b0[j]*(v-x2)-band.a1[j]*y1-band.a2[j]*y2;x2=x1;x1=v;y2=y1;y1=y;v=y;}
        double zero=0,one=0;
        for(std::size_t k=0;k<h.size();++k){zero+=h[k]*h[k];if(k+1<h.size())one+=h[k]*h[k+1];}
        const auto near=[](double got,double want,double scale){return std::abs(got-want)<=1e-6*scale;};
        const double var=zero/3;
        if(!near(sigma[2*j+2][2*j+2],var,var)||!near(sigma[2*j+3][2*j+3],var,var)||!near(sigma[2*j+2][2*j+3],one/3,var)){
          std::cerr<<"rate "<<sr<<" band "<<b<<" section "<<j<<": "<<sigma[2*j+2][2*j+2]<<" "<<sigma[2*j+2][2*j+3]<<", want "<<var<<" "<<one/3<<'\n';
          check(false,"a low knock band's sections hold their outputs' stationary covariance");
        }
        if(j==keyra::noiseSections-1&&(!near(sigma[0][2*j+2],h[0]/3,var)||!near(sigma[1][2*j+2],h[1]/3,var)))
          check(false,"a low knock band's output holds its stationary covariance with the source");
      }
    }
  }
  // Every silence leaves the low knock bands in the same state, and a strike
  // after silence sounds the same however long the silence was. C5 is
  // damped, so the engine falls silent once it is let go, and its knock's
  // bands all lie under it.
  {
    std::vector<float> after[2];std::vector<double> states[2];
    for(int k=0;k<2;++k){
      keyra::Engine e(48000);auto& s=keyra::LowKnockTestObserver::state(e);e.setParameters(quiet(Piano::kawai));
      e.setSteadyStrikesForMeasurement(true);
      const auto snapshot=[&]{std::vector<double> v;
        for(int b=keyra::noiseBands;b<keyra::bankBands;++b){const auto& band=s.noise[static_cast<std::size_t>(b)];
          for(int j=0;j<keyra::noiseSections;++j)for(int c=0;c<2;++c){v.push_back(band.x1[j][c]);v.push_back(band.x2[j][c]);
            v.push_back(band.y1[j][c]);v.push_back(band.y2[j][c]);}}
        return v;};
      const auto fresh=snapshot();
      bool drawn=false;for(double v:fresh)drawn=drawn||v!=0;
      check(drawn,"the low knock bands start from a drawn state, not from rest");
      e.noteOn(72,1.f);render(e,24000,256);e.noteOff(72);
      int waited=0;while(!s.sleeping&&waited<48000*120){render(e,4800,4800);waited+=4800;}
      check(s.sleeping&&snapshot()==fresh,"the engine falls silent with its low knock bands as they started");
      states[k]=snapshot();
      render(e,k==0?48000:480000,4800);
      e.noteOn(72,1.f);after[k]=render(e,24000,256);
      e.reset();check(snapshot()==fresh,"reset() leaves the low knock bands as they started");
    }
    check(after[0]==after[1],"a strike after silence does not depend on how long the silence was");
  }
  if(failures)std::cerr<<failures<<" low knock check(s) failed\n";else std::cout<<"low knock tests passed\n";
  return failures?1:0;
}
