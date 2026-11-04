// Numeric-only guard for generate_velocity_interpolation.py. The real engine's
// raw single(... LaneCache ...) overload remains independent of generated masks.
#define KEYRA_GENERATING_VELOCITY_GUARD 1
#include "DSP/KeyraEngine.cpp"
#include <complex>
#include <iomanip>
#include <iostream>
#include <stdexcept>
namespace {
using Z=std::complex<double>;
Z coefficient(const keyra::LaneData& x){return std::pow(10.,x.level/20)*Z(x.phase.re,x.phase.im);}
Z cross(const keyra::PartialData& a,const keyra::PartialData& b,double from,double to,double rise=0){
  Z sum{};double additions[6]={0},weights[6]={1};int terms=1;
  if(rise>0){
    // Closed form of the native 48 kHz discrete smoothing recurrence, from
    // zero at contact. Its square gives six exponential terms in the integral.
    const double aa=std::exp(-1/(rise*48000)),bb=std::exp(-1/(keyra::contactSmoothing*48000));
    const double ca=(1-bb)*aa/(aa-bb),cb=(1-aa)*bb/(aa-bb);
    const double r[6]={0,2/rise,2/keyra::contactSmoothing,1/rise,1/keyra::contactSmoothing,1/rise+1/keyra::contactSmoothing};
    const double w[6]={1,ca*ca,cb*cb,-2*ca,2*cb,-2*ca*cb};terms=6;
    for(int k=0;k<terms;++k){additions[k]=r[k];weights[k]=w[k];}
  }
  for(int j=0;j<keyra::lanes;++j)for(int k=0;k<keyra::lanes;++k){
    const auto& x=a.lane[j];const auto& y=b.lane[k];
    const Z pickup=Z(x.left.re,x.left.im)*std::conj(Z(y.left.re,y.left.im))+Z(x.right.re,x.right.im)*std::conj(Z(y.right.re,y.right.im));
    Z integral{};
    for(int q=0;q<terms;++q){const Z c(std::exp(x.rate)+std::exp(y.rate)+additions[q],2*keyra::pi*(y.offset-x.offset));
      integral+=weights[q]*(std::exp(-c*from)-std::exp(-c*to))/c;}
    sum+=coefficient(x)*std::conj(coefficient(y))*pickup*integral;
  }
  return sum;
}
double riseAt(const keyra::Model& m,const keyra::measured::Anchor& a,const keyra::PartialData& d,double v){
  const double cap=m.contactTime*std::pow(2.,-(a.note-60)/24.);
  return std::max(cap>0?std::min(std::exp(d.rise),cap):std::exp(d.rise),std::exp(keyra::onsetRiseAt(m,a,v)));
}
double excursion(double power,double a,double b){
  if(!(std::isfinite(power)&&power>0&&std::isfinite(a)&&a>0&&std::isfinite(b)&&b>0))
    throw std::runtime_error("velocity guard requires finite, positive window powers");
  return std::max({0.,10*std::log10(std::min(a,b)/power),10*std::log10(power/std::max(a,b))});
}
}
int main(){try{
  const char* names[]={"grand","upright","kawai","hamburg","newyork"};
  const double from[]={.05,.75,1.5},to[]={.75,1.5,3.5};
  std::cout<<"model,note,order,partial,layer,baseline_excursion,early_excursion,pa,pb,rho,q00,q01,q02,q10,q11,q12,q20,q21,q22\n"<<std::setprecision(17);
  for(int piano=0;piano<keyra::pianoCount;++piano){const auto& m=keyra::models[piano];
    for(int n=0;n<m.anchorCount;++n){const auto& anchor=m.anchors[n];
      for(int j=anchor.first;j<anchor.first+anchor.count;++j){const auto& p=m.partials[j];std::array<keyra::LaneCache,keyra::lanes> lanes{};
        for(int k=0;k<keyra::lanes;++k)lanes[k]=keyra::cacheLane(p.lanes[k],m.layers);
        for(int layer=0;layer<m.layers-1;++layer){
          const double lo=m.layerVelocity[layer],hi=m.layerVelocity[layer+1];
          const auto a=keyra::single(m,p,lanes,lo),b=keyra::single(m,p,lanes,hi);
          const double pa=keyra::windowPower(a),pb=keyra::windowPower(b);
          excursion(pa,pa,pb); // validate before logarithms and normalization
          const auto cache=keyra::cacheVelocity(m,p,lanes,layer);
          const double earlyA=cross(a,a,0,.05,riseAt(m,anchor,a,lo)).real(),earlyB=cross(b,b,0,.05,riseAt(m,anchor,b,hi)).real();
          double baseline=0,early=0;
          // A detected baseline violation is sufficient to justify considering
          // an interval. The candidate's variable-rise early window is checked
          // at quarter recording coordinates, including the endpoints.
          for(double v=lo+.25;v<hi;v+=.25){
            const auto raw=keyra::single(m,p,lanes,v),candidate=keyra::interpolateVelocity(raw,cache,(v-lo)/(hi-lo));
            baseline=std::max(baseline,excursion(keyra::windowPower(raw),pa,pb));
            early=std::max(early,excursion(cross(candidate,candidate,0,.05,riseAt(m,anchor,raw,v)).real(),earlyA,earlyB));
          }
          std::cout<<names[piano]<<','<<anchor.note<<','<<p.order<<','<<m.partialFirst+j<<','<<layer<<','<<baseline<<','<<early<<','<<pa<<','<<pb<<','<<cache.overlap;
          const Z align=std::polar(1.,cache.angle);
          for(int w=0;w<3;++w){
            const double x=cross(a,a,from[w],to[w]).real()/pa,y=cross(b,b,from[w],to[w]).real()/pb;
            const double c=(cross(a,b,from[w],to[w])*std::conj(align)).real()/std::sqrt(pa*pb);
            std::cout<<','<<x<<','<<2*(c-x)<<','<<x+y-2*c;
          }
          std::cout<<'\n';
        }
      }
    }
  }
  return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
