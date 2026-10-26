#include "keyra/physics/ContactSolver.h"
#include "../src/full_instrument/PreparedModel.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>
#include <random>

namespace {
using Input=keyra::physics::FullContactInput;
using Result=keyra::physics::FullContactResult;
using Failure=keyra::physics::FullContactFailure;
using Limits=keyra::physics::FullContactLimits;
using LD=long double;
bool trackAllocations=false;
uint64_t allocations=0;
void* allocate(std::size_t size) {
  if(trackAllocations)++allocations;
  if(void* p=std::malloc(size?size:1))return p;
  std::abort();
}
void require(bool value,const char* reason) {
  if(!value){std::fprintf(stderr,"FAIL full contact: %s\n",reason);std::exit(1);}
}
LD potential(LD x,LD K,LD power) {
  return x<=0?0:K*std::pow(x,power+1)/(power+1);
}
// Independent symmetric evaluation. The production polynomial derivative is
// not reused by the reference force, bisection, or scalar work checks.
LD dg(LD a,LD b,LD K,LD power) {
  if(K==0||(a<=0&&b<=0))return 0;
  if(a<=0)return K*std::pow(b,power)*b/((power+1)*(b-a));
  if(b<=0)return K*std::pow(a,power)*a/((power+1)*(a-b));
  const LD hi=std::max(a,b),lo=std::min(a,b);
  if(hi==lo)return K*std::pow(hi,power);
  const LD t=(lo-hi)/hi;
  const LD divided=t<=-1?1/(power+1):
    std::expm1((power+1)*std::log1p(t))/((power+1)*t);
  return K*std::pow(hi,power)*divided;
}
LD target(const Input& c,LD force) {
  const LD a=c.oldCompression,b=LD(c.freeCompression)-LD(c.compliance)*force;
  const LD h=std::max(LD(0),1+LD(c.loss)*(b-a)/LD(c.timeStep));
  return dg(a,b,c.stiffness,c.power)*h;
}
LD reference(const Input& c) {
  const LD high=target(c,0);
  if(high==0||c.compliance==0)return high;
  LD lo=0,hi=high;
  for(unsigned i=0;i<110;++i){
    const LD mid=.5L*(lo+hi);
    if(mid==lo||mid==hi)break;
    if(mid-target(c,mid)>0)hi=mid;else lo=mid;
  }
  return .5L*(lo+hi);
}
struct Statistics {
  uint64_t cases=0,validBisectionCases=0;
  unsigned maxNewton=0,maxBisection=0,maxEvaluations=0;
  double maximumForceError=0,maximumPureRelativeForceError=0;
  double maximumReferenceResidual=0,maximumNormalizedWorkDefect=0;
  double maximumNegativeDissipation=0,maximumAbsoluteWorkDefect=0;
};
void bounded(const Result& r) {
  require(r.newtonIterations<=Limits::newtonIterations&&
          r.bisectionIterations<=Limits::bisectionIterations&&
          r.evaluations<=Limits::evaluations,"iteration/evaluation bound exceeded");
  require(r.usedBisection==(r.bisectionIterations!=0),"fallback diagnostic mismatch");
}
void check(const Input& c,Statistics& stats) {
  const auto r=keyra::physics::solveFullContact(c);bounded(r);
  if(!r.valid){
    std::fprintf(stderr,"unexpected failure %u: a=%.17g free=%.17g A=%.17g dt=%.17g K=%.17g p=%.17g loss=%.17g residual=%.17g\n",
      unsigned(r.failure),c.oldCompression,c.freeCompression,c.compliance,c.timeStep,
      c.stiffness,c.power,c.loss,r.residual);
    require(false,"supported physical contact failed");
  }
  require(r.converged&&r.failure==Failure::None&&std::isfinite(r.force)&&r.force>=0&&
          std::isfinite(r.residual)&&std::isfinite(r.normalizedResidual)&&
          r.normalizedResidual<=Limits::acceptanceTolerance,"successful result not verified");
  const LD ref=reference(c),force=r.force;
  const LD normalizedError=std::abs(force-ref)/(1+std::abs(ref));
  const LD pureError=ref>1.e-3L?std::abs(force-ref)/ref:0;
  const LD refResidual=std::abs(force-target(c,force))/(1+force);
  const LD a=c.oldCompression,b=LD(c.freeCompression)-LD(c.compliance)*force,d=b-a;
  const LD va=potential(a,c.stiffness,c.power),vb=potential(b,c.stiffness,c.power);
  const LD elastic=dg(a,b,c.stiffness,c.power);
  const LD h=std::max(LD(0),1+LD(c.loss)*d/LD(c.timeStep));
  const LD dissipation=force*d-(vb-va);
  const LD expected=h>0?elastic*LD(c.loss)*d*d/LD(c.timeStep):-(vb-va);
  const LD scale=1+std::abs(force*d)+std::abs(va)+std::abs(vb);
  const LD workDefect=std::abs(dissipation-expected);
  const LD normalizedWork=workDefect/scale;
  const LD negative=std::max(LD(0),-dissipation)/scale;
  require(std::isfinite(ref)&&std::isfinite(dissipation)&&std::isfinite(normalizedWork),
          "independent reference/work not finite");
  if(normalizedError>1.e-10L||pureError>1.e-10L||refResidual>1.e-10L||
     normalizedWork>1.e-10L||negative>1.e-10L){
    std::fprintf(stderr,"accuracy/work a=%.17g free=%.17g A=%.17g dt=%.17g K=%.17g p=%.17g loss=%.17g F=%.17g ref=%.21Lg error=%.21Lg refResidual=%.21Lg work=%.21Lg negative=%.21Lg\n",
      c.oldCompression,c.freeCompression,c.compliance,c.timeStep,c.stiffness,c.power,c.loss,
      r.force,ref,normalizedError,refResidual,normalizedWork,negative);
    require(false,"independent long-double force/work gate failed");
  }
  ++stats.cases;if(r.usedBisection)++stats.validBisectionCases;
  stats.maxNewton=std::max(stats.maxNewton,r.newtonIterations);
  stats.maxBisection=std::max(stats.maxBisection,r.bisectionIterations);
  stats.maxEvaluations=std::max(stats.maxEvaluations,r.evaluations);
  stats.maximumForceError=std::max(stats.maximumForceError,double(normalizedError));
  stats.maximumPureRelativeForceError=std::max(stats.maximumPureRelativeForceError,double(pureError));
  stats.maximumReferenceResidual=std::max(stats.maximumReferenceResidual,double(refResidual));
  stats.maximumNormalizedWorkDefect=std::max(stats.maximumNormalizedWorkDefect,double(normalizedWork));
  stats.maximumNegativeDissipation=std::max(stats.maximumNegativeDissipation,double(negative));
  stats.maximumAbsoluteWorkDefect=std::max(stats.maximumAbsoluteWorkDefect,double(workDefect));
}
struct KeyFixture {double stiffness=0,power=0,compliance=0,mass=0,velocityExponent=0;};
using KeyTable=std::array<KeyFixture,88>;
constexpr std::array<int,4> rates{{44100,48000,88200,96000}};
std::array<KeyTable,4> fixtures() {
  std::array<KeyTable,4> all{};
  for(unsigned rate=0;rate<rates.size();++rate){
    grand::Options options;options.sampleRate=rates[rate];grand::Piano model(options);
    for(unsigned note=0;note<88;++note){
      const auto& k=model.keys[note];
      require(k.mass>0&&k.K>0&&k.power>=1&&k.power<=5&&
              k.contactCompliance>=model.dt*model.dt/(2*k.mass),"actual prepared key fixture invalid");
      all[rate][note]={k.K,k.power,k.contactCompliance,k.mass,k.velocityExponent};
    }
  }
  return all;
}
Input input(const KeyFixture& k,int rate,double a,double free,double loss) {
  return {a,free,k.compliance,1./rate,k.stiffness,k.power,loss};
}
void physicalCases(const std::array<KeyTable,4>& all,Statistics& stats) {
  for(unsigned ri=0;ri<rates.size();++ri)for(const auto& k:all[ri])
    for(double normalizedVelocity:{.05,.5,1.})for(double direction:{-1.,1.})
      for(double a:{-1.e-6,0.,.001})for(double loss:{0.,.12}){
        const double velocity=direction*(.22+5.6*std::pow(normalizedVelocity,k.velocityExponent));
        check(input(k,rates[ri],a,a+velocity/rates[ri],loss),stats);
      }
  std::mt19937_64 random(0x4b657972614347ULL);
  std::uniform_real_distribution<double> unit(0,1);
  for(unsigned i=0;i<2000;++i){
    const unsigned ri=unsigned(random()%4),note=unsigned(random()%88);
    const double a=(2*unit(random)-1)*.002,velocity=(2*unit(random)-1)*8;
    const double loss=std::array<double,4>{{0,.12,1,10}}[random()%4];
    auto c=input(all[ri][note],rates[ri],a,a+velocity/rates[ri],loss);
    // The controller's full bounded hardness variation changes K by at most
    // 2.5%; include both authored endpoints in the random physical contacts.
    c.stiffness*=i%2?.975:1.025;
    check(c,stats);
  }
}
void endpoints(const std::array<KeyTable,4>& all,Statistics& stats) {
  const auto endpoint=[&](const KeyFixture& key,int rate,double a,double b,double loss){
    auto c=input(key,rate,a,b,loss);
    const LD h=std::max(LD(0),1+LD(loss)*(LD(b)-LD(a))/LD(c.timeStep));
    const LD f=dg(a,b,c.stiffness,c.power)*h;
    c.freeCompression=double(LD(b)+LD(c.compliance)*f);check(c,stats);
  };
  for(unsigned ri=0;ri<rates.size();++ri)for(unsigned note:{0u,39u,87u}){
    const auto& key=all[ri][note];
    for(double a:{1.e-8,1.e-6,1.e-4,.001})for(double loss:{0.,.12}){
      const double cutoff=1.e-10*std::max(1.e-5,std::abs(a));
      for(double factor:{-1000.,-2.,-1.01,-1.,-.99,0.,.99,1.,1.01,2.,1000.})
        endpoint(key,rates[ri],a,a+factor*cutoff,loss);
      for(double ratio:{-.010001,-.01,-.009999,-.001,-1.e-8,1.e-8,.001,.009999,.01,.010001})
        endpoint(key,rates[ri],a,a*(1+ratio),loss);
    }
    for(double loss:{0.,.12,1.,10.}){
      endpoint(key,rates[ri],-1.e-6,1.e-6,loss);
      endpoint(key,rates[ri],1.e-6,-1.e-6,loss);
      endpoint(key,rates[ri],0,1.e-6,loss);
      endpoint(key,rates[ri],1.e-6,0,loss);
      check(input(key,rates[ri],-.001,-.002,loss),stats);
      check(input(key,rates[ri],0,0,loss),stats);
      if(loss>0){
        const double a=.001,clamp=a-1./(rates[ri]*loss);
        endpoint(key,rates[ri],a,std::nextafter(clamp,-INFINITY),loss);
        endpoint(key,rates[ri],a,clamp,loss);
        endpoint(key,rates[ri],a,std::nextafter(clamp,INFINITY),loss);
      }
    }
    auto zeroA=input(key,rates[ri],.001,.00101,.12);zeroA.compliance=0;check(zeroA,stats);
    auto zeroK=zeroA;zeroK.stiffness=0;check(zeroK,stats);
  }
}
void failureCases() {
  const Input good{.001,.0011,1.e-8,1./48000.,8.e8,2.5,.12};
  for(unsigned field=0;field<7;++field)for(double bad:{
      std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),
      -std::numeric_limits<double>::infinity()}){
    auto c=good;
    switch(field){case 0:c.oldCompression=bad;break;case 1:c.freeCompression=bad;break;
      case 2:c.compliance=bad;break;case 3:c.timeStep=bad;break;case 4:c.stiffness=bad;break;
      case 5:c.power=bad;break;default:c.loss=bad;break;}
    const auto r=keyra::physics::solveFullContact(c);bounded(r);
    require(!r.valid&&!r.converged&&r.force==0&&r.failure==Failure::InvalidInput&&
            r.evaluations==0,"nonfinite input was not rejected with zero force");
  }
  for(unsigned field=0;field<7;++field){
    auto c=good;
    switch(field){case 0:c.compliance=-1;break;case 1:c.timeStep=0;break;
      case 2:c.timeStep=-1;break;case 3:c.stiffness=-1;break;case 4:c.power=.99;break;
      case 5:c.power=5.01;break;default:c.loss=-1;break;}
    const auto r=keyra::physics::solveFullContact(c);bounded(r);
    require(!r.valid&&r.force==0&&r.failure==Failure::InvalidInput,"unsupported parameter accepted");
  }
  auto overflow=good;overflow.oldCompression=overflow.freeCompression=1.e200;
  const auto over=keyra::physics::solveFullContact(overflow);bounded(over);
  require(!over.valid&&over.force==0&&over.failure==Failure::NonfiniteEvaluation,
          "overflow evaluation applied a tentative force");
  overflow=good;overflow.timeStep=std::numeric_limits<double>::denorm_min();
  const auto ratioOverflow=keyra::physics::solveFullContact(overflow);bounded(ratioOverflow);
  require(!ratioOverflow.valid&&ratioOverflow.force==0&&
          ratioOverflow.failure==Failure::NonfiniteEvaluation,
          "loss/time-step overflow did not reject the solve");
  auto underflow=good;underflow.oldCompression=underflow.freeCompression=1.e-180;
  underflow.compliance=0;underflow.stiffness=1.e308;underflow.power=1;underflow.loss=0;
  const auto under=keyra::physics::solveFullContact(underflow);bounded(under);
  require(!under.valid&&under.force==0&&under.failure==Failure::NumericalRange,
          "positive potential underflow reported a false zero-force success");
  underflow.oldCompression=0;
  const auto underNew=keyra::physics::solveFullContact(underflow);bounded(underNew);
  require(!underNew.valid&&underNew.force==0&&underNew.failure==Failure::NumericalRange,
          "new positive potential underflow reported success");
  // Frozen known nonconvergent stiff case from the original bounded study.
  const Input stiff{.001,.0011,1.e-6,1./48000.,1.e12,1,10};
  const auto failed=keyra::physics::solveFullContact(stiff);bounded(failed);
  require(!failed.valid&&!failed.converged&&failed.force==0&&
          failed.failure==Failure::NoConvergence&&failed.usedBisection&&
          failed.evaluations==Limits::evaluations&&
          failed.newtonIterations==Limits::newtonIterations&&
          failed.bisectionIterations==Limits::bisectionIterations,
          "bounded nonconvergence did not reject its tentative force");
}
void supportedPowerEndpoints(Statistics& stats) {
  for(int rate:rates)for(double power:{1.,2.,5.})for(double loss:{0.,.12,1.,10.})
    for(double A:{0.,1.e-8})for(double relative:{-1.e-8,0.,1.e-8})
      check({1.e-8,1.e-8*(1+relative),A,1./rate,8.e8,power,loss},stats);
}
} // namespace

void* operator new(std::size_t n){return allocate(n);}
void* operator new[](std::size_t n){return allocate(n);}
void* operator new(std::size_t n,const std::nothrow_t&) noexcept{return allocate(n);}
void* operator new[](std::size_t n,const std::nothrow_t&) noexcept{return allocate(n);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
void operator delete[](void* p,std::size_t) noexcept{std::free(p);}
void operator delete(void* p,const std::nothrow_t&) noexcept{std::free(p);}
void operator delete[](void* p,const std::nothrow_t&) noexcept{std::free(p);}

int main(){
  const auto actual=fixtures();Statistics stats;
  trackAllocations=true;
  physicalCases(actual,stats);endpoints(actual,stats);supportedPowerEndpoints(stats);failureCases();
  trackAllocations=false;require(allocations==0,"solver/reference loop allocated");
  require(stats.validBisectionCases>0,"no successfully verified bisection fallback was exercised");
  std::printf("{\"passed\":true,\"physical_and_endpoint_cases\":%llu,\"keys_per_rate\":88,\"rates\":[44100,48000,88200,96000],\"actual_model_rebuilt_at_each_rate\":true,\"maximum_normalized_force_error\":%.17g,\"maximum_pure_relative_force_error_above_1e_3_N\":%.17g,\"maximum_reference_residual\":%.17g,\"maximum_normalized_work_defect\":%.17g,\"maximum_normalized_negative_dissipation\":%.17g,\"maximum_absolute_work_defect_J\":%.17g,\"maximum_newton\":%u,\"maximum_bisection\":%u,\"maximum_evaluations\":%u,\"valid_bisection_cases\":%llu,\"forced_failure_evaluations\":67,\"failure_force_zero\":true,\"solver_allocations\":0,\"physical_valid_failures\":0,\"expected_failure_cases\":33,\"long_double_digits\":%d}\n",
    static_cast<unsigned long long>(stats.cases),stats.maximumForceError,
    stats.maximumPureRelativeForceError,stats.maximumReferenceResidual,
    stats.maximumNormalizedWorkDefect,stats.maximumNegativeDissipation,
    stats.maximumAbsoluteWorkDefect,stats.maxNewton,stats.maxBisection,stats.maxEvaluations,
    static_cast<unsigned long long>(stats.validBisectionCases),std::numeric_limits<LD>::digits);
}
