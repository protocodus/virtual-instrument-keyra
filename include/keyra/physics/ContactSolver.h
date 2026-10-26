#pragma once
#include <algorithm>
#include <cmath>
#include <limits>

namespace keyra::physics {

// Positive compression, metres/newton compliance, seconds per step, and
// nonnegative Hunt-Crossley loss in seconds/metre. This is the complete grand
// model's scalar contact law, separate from the action research module.
struct FullContactInput {
  double oldCompression=0,freeCompression=0,compliance=0;
  double timeStep=1./48000.,stiffness=0,power=2.5,loss=0;
};
enum class FullContactFailure : unsigned {
  None,InvalidInput,NonfiniteEvaluation,NumericalRange,InvalidBracket,NoConvergence
};
struct FullContactResult {
  // Force is usable only when valid. Every failure returns exactly zero force;
  // no unverified tentative force is exposed to an instrument adapter.
  double force=0;
  // On success these describe the returned force. On failure they describe the
  // best finite residual seen, if any; validity/failure must be checked first.
  double residual=0,normalizedResidual=0;
  unsigned newtonIterations=0,bisectionIterations=0,evaluations=0;
  bool usedBisection=false,converged=false,valid=false;
  FullContactFailure failure=FullContactFailure::None;
};
struct FullContactLimits {
  static constexpr unsigned newtonIterations=10,bisectionIterations=56;
  static constexpr unsigned evaluations=1+newtonIterations+bisectionIterations;
  static constexpr double refinementTolerance=2.e-14;
  static constexpr double acceptanceTolerance=1.e-10;
};

// Solve F=DG(V)(a,b)*max(0,1+loss*(b-a)/dt), b=free-compliance*F,
// V(x)=K*max(x,0)^(power+1)/(power+1). The target is nonincreasing in F,
// so its value at F=0 supplies a finite nonnegative upper bracket.
//
// Adapted from tools/probe_fast_full_contact.py's validated scalar experiment:
// cache V(a), use stable DG/derivative evaluations and safeguarded Newton, then
// bounded bisection. The tighter refinement goal avoids unnecessary iterations;
// convergence requires a separately verified normalized residual <=1e-10.
// No allocation, exceptions, locks, I/O, globals or thread-local state.
inline FullContactResult solveFullContact(const FullContactInput& in) noexcept {
  FullContactResult result;
  const double a=in.oldCompression,free=in.freeCompression,A=in.compliance;
  const double dt=in.timeStep,K=in.stiffness,power=in.power,loss=in.loss;
  const auto fail=[&](FullContactFailure reason) noexcept {
    result.force=0;result.valid=result.converged=false;result.failure=reason;
    result.usedBisection=result.bisectionIterations!=0;
    return result;
  };
  const auto success=[&](double force,double residual) noexcept {
    result.force=force;result.residual=residual;
    result.normalizedResidual=std::abs(residual)/(1+force);
    result.valid=result.converged=true;result.failure=FullContactFailure::None;
    result.usedBisection=result.bisectionIterations!=0;
    return result;
  };
  if(!std::isfinite(a)||!std::isfinite(free)||!std::isfinite(A)||!std::isfinite(dt)||
     !std::isfinite(K)||!std::isfinite(power)||!std::isfinite(loss)||
     A<0||dt<=0||K<0||power<1||power>5||loss<0)
    return fail(FullContactFailure::InvalidInput);
  if(K==0||(a<=0&&free<=0))return success(0,0);
  const double va=a>0?K*std::pow(a,power+1)/(power+1):0;
  const double chi=loss/dt;
  if(!std::isfinite(va)||!std::isfinite(chi))
    return fail(FullContactFailure::NonfiniteEvaluation);
  // A rounded-zero positive potential can conceal a large force when a tiny
  // power underflows before multiplication by a large K. Reject that numerical
  // domain rather than reporting a false successful zero-force solve.
  if(a>0&&va==0)return fail(FullContactFailure::NumericalRange);
  struct Evaluation {
    double residual=0,tangent=1,target=0;bool finite=true;
    FullContactFailure failure=FullContactFailure::NonfiniteEvaluation;
  };
  const auto evaluate=[&](double f) noexcept {
    ++result.evaluations;
    const double b=free-A*f,d=b-a;
    if(!std::isfinite(b)||!std::isfinite(d))return Evaluation{0,1,0,false};
    const double h=std::max(0.0,1+chi*d);
    if(!std::isfinite(h))return Evaluation{0,1,0,false};
    if(h==0||(a<=0&&b<=0))return Evaluation{f,1,0,true};
    double g=0,gb=0;
    if(b<=0){const double distance=a-b;g=va/distance;gb=g/distance;}
    else if(a<=0){
      const double vb=K*std::pow(b,power+1)/(power+1);
      if(vb==0)return Evaluation{0,1,0,false,FullContactFailure::NumericalRange};
      const double prime=(power+1)*vb/b;
      g=vb/d;gb=(prime-g)/d;
    }else{
      const double t=d/a;
      if(std::abs(t)<1e-2){
        // Integral/binomial series for the same DG law; avoids subtracting
        // nearby potentials. Six terms suffice for power in [1,5] and |t|<.01.
        const double base=(power+1)*va/a;
        double coefficient=1,value=1,derivative=0,term=1;
        for(int k=1;k<=6;++k){
          coefficient*=(power-k+1)/(k+1);
          derivative+=k*coefficient*term;term*=t;value+=coefficient*term;
        }
        g=base*value;gb=base*derivative/a;
      }else{
        const double vb=K*std::pow(b,power+1)/(power+1);
        if(vb==0)return Evaluation{0,1,0,false,FullContactFailure::NumericalRange};
        const double prime=(power+1)*vb/b;
        g=(vb-va)/d;gb=(prime-g)/d;
      }
    }
    const double target=g*h,residual=f-target;
    // A nonfinite tangent merely disables Newton: the finite force residual
    // still admits a bracketed bisection. A nonfinite force evaluation does not.
    return Evaluation{residual,1+A*(h*gb+chi*g),target,
      std::isfinite(g)&&g>=0&&std::isfinite(target)&&target>=0&&std::isfinite(residual)};
  };
  const auto zero=evaluate(0);
  if(!zero.finite)return fail(zero.failure);
  if(zero.target==0)return success(0,0);
  if(A==0)return success(zero.target,0);
  double low=0,high=zero.target;
  if(!(high>low))return fail(FullContactFailure::InvalidBracket);
  double f=zero.target/zero.tangent;
  if(!(f>low&&f<high)||!std::isfinite(f))f=.5*(low+high);
  double best=0,bestResidual=std::numeric_limits<double>::infinity();
  const auto remember=[&](double value,const Evaluation& e) noexcept {
    if(std::abs(e.residual)<std::abs(bestResidual)){
      best=value;bestResidual=e.residual;
      result.residual=bestResidual;result.normalizedResidual=std::abs(bestResidual)/(1+best);
    }
  };
  bool refined=false;
  for(unsigned i=0;i<FullContactLimits::newtonIterations;++i){
    const auto e=evaluate(f);++result.newtonIterations;
    if(!e.finite)return fail(e.failure);
    remember(f,e);
    if(std::abs(e.residual)<=FullContactLimits::refinementTolerance*(1+f)){
      refined=true;break;
    }
    if(e.residual>0)high=f;else low=f;
    double next=f-e.residual/e.tangent;
    if(!std::isfinite(e.tangent)||e.tangent<1||!std::isfinite(next)||!(next>low&&next<high))
      next=.5*(low+high);
    f=next;
  }
  if(!refined)for(unsigned i=0;i<FullContactLimits::bisectionIterations;++i){
    f=.5*(low+high);const auto e=evaluate(f);++result.bisectionIterations;
    if(!e.finite)return fail(e.failure);
    remember(f,e);
    if(std::abs(e.residual)<=FullContactLimits::refinementTolerance*(1+f))break;
    if(e.residual>0)high=f;else low=f;
  }
  if(!std::isfinite(best)||best<0||!std::isfinite(bestResidual)||
     std::abs(bestResidual)>FullContactLimits::acceptanceTolerance*(1+best))
    return fail(FullContactFailure::NoConvergence);
  return success(best,bestResidual);
}

} // namespace keyra::physics
