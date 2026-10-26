// Grand piano research POC. No samples, impulse-response recordings, or SDK.
// Mass-normalized modal coordinates; exact free rotations; discrete-gradient
// hammer contact; reciprocal dissipative string/board ports. See README.md.
#include <algorithm>
#include <array>
#include <chrono>
#include <complex>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <limits>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "calibration.h"

namespace grand {
constexpr double pi=3.14159265358979323846;
double lerp(double a,double b,double t){return a+(b-a)*t;}
double loglerp(double a,double b,double t){return std::exp(lerp(std::log(a),std::log(b),t));}
double anchor(int note,double a,double b,double c){
  return note<=60?loglerp(a,b,(note-36)/24.0):loglerp(b,c,(note-60)/36.0);
}
double sinc(double x){return std::abs(x)<1e-8?1.0:std::sin(x)/x;}
struct Cal {
  int lo,hi;double t;
  explicit Cal(int note){lo=std::clamp((note-36)/12,0,3);hi=lo+1;t=(note-piano_calibration::anchors[lo].note)/12.0;}
  double scalar(double piano_calibration::Anchor::*field,bool logarithmic=false,bool extrapolate=false)const{
    double u=extrapolate?t:std::clamp(t,0.0,1.0);
    return logarithmic?loglerp(piano_calibration::anchors[lo].*field,piano_calibration::anchors[hi].*field,u):lerp(piano_calibration::anchors[lo].*field,piano_calibration::anchors[hi].*field,u);
  }
  double mode(int n,std::array<double,64> piano_calibration::Anchor::*field,bool logarithmic=false)const{
    int j=std::clamp(n-1,0,63);double u=std::clamp(t,0.0,1.0);
    double a=(piano_calibration::anchors[lo].*field)[j],b=(piano_calibration::anchors[hi].*field)[j];
    return logarithmic?loglerp(a,b,u):lerp(a,b,u);
  }
};
using Vec3=std::array<double,3>;
using Mat3=std::array<Vec3,3>;
Vec3 solve3(Mat3 a,Vec3 b){
  for(int k=0;k<3;++k){
    int pivot=k; for(int j=k+1;j<3;++j)if(std::abs(a[j][k])>std::abs(a[pivot][k]))pivot=j;
    if(std::abs(a[pivot][k])<1e-20)throw std::runtime_error("singular bridge");
    std::swap(a[k],a[pivot]);std::swap(b[k],b[pivot]);
    for(int j=k+1;j<3;++j){double r=a[j][k]/a[k][k];for(int l=k;l<3;++l)a[j][l]-=r*a[k][l];b[j]-=r*b[k];}
  }
  Vec3 x{};for(int k=2;k>=0;--k){double y=b[k];for(int j=k+1;j<3;++j)y-=a[k][j]*x[j];x[k]=y/a[k][k];}return x;
}

struct Modes {
  std::vector<double> q,p,c,s,omega,hammer,b,forceQ,forceP,loss,damper,damp;
  std::vector<int> partial,polarization;
  std::vector<double> radQL,radPL,radQR,radPR,radiationMagnitude;
  std::vector<double> baseQL,basePL,baseQR,basePR;
  std::vector<double> portOmega,portInverse;
  void add(double hz,double h,double port,double sigma,double ds,double dt,int order,int pol){
    double w=2*pi*hz,phase=w*dt;
    q.push_back(0);p.push_back(0);c.push_back(std::cos(phase));s.push_back(std::sin(phase));omega.push_back(w);
    hammer.push_back(h);b.push_back(port);forceQ.push_back(h*(1-std::cos(phase))/(w*w));forceP.push_back(h*std::sin(phase)/(w*w));
    loss.push_back(sigma);damper.push_back(ds);damp.push_back(std::exp(-sigma*dt));
    partial.push_back(order);polarization.push_back(pol);
    radQL.push_back(0);radPL.push_back(0);radQR.push_back(0);radPR.push_back(0);radiationMagnitude.push_back(0);
    baseQL.push_back(0);basePL.push_back(0);baseQR.push_back(0);basePR.push_back(0);
    portOmega.push_back(port*w);portInverse.push_back(port/w);
  }
  size_t size()const{return q.size();}
  double energy()const{double e=0;for(size_t i=0;i<size();++i)e+=.5*omega[i]*omega[i]*(q[i]*q[i]+p[i]*p[i]);return e;}
  double displacement()const{
#pragma clang fp reassociate(on)
    double y=0;for(size_t i=0;i<size();++i)y+=hammer[i]*q[i];return y;
  }
  double portVelocity()const{
#pragma clang fp reassociate(on)
    double v=0;for(size_t i=0;i<size();++i)v+=portOmega[i]*p[i];return v;
  }
  void freeStep(){
    double *__restrict yq=q.data(),*__restrict yp=p.data();
    const double *__restrict yc=c.data(),*__restrict ys=s.data(),*__restrict yd=damp.data();
    for(size_t i=0;i<size();++i){
      double v=yp[i]*yd[i],y=yq[i];yq[i]=yc[i]*y+ys[i]*v;yp[i]=yc[i]*v-ys[i]*y;
    }
  }
  void finishDamping(){
    double *__restrict yp=p.data();const double *__restrict yd=damp.data();
    for(size_t i=0;i<size();++i)yp[i]*=yd[i];
  }
  void force(double f){
    double *__restrict yq=q.data(),*__restrict yp=p.data();
    const double *__restrict fq=forceQ.data(),*__restrict fp=forceP.data();
    for(size_t i=0;i<size();++i){yq[i]+=fq[i]*f;yp[i]+=fp[i]*f;}
  }
  void portImpulse(double impulse){
    double *__restrict yp=p.data();const double *__restrict bi=portInverse.data();
    for(size_t i=0;i<size();++i)yp[i]+=bi[i]*impulse;
  }
  std::array<double,2> radiation()const{
#pragma clang fp reassociate(on)
    double l=0,r=0;
    for(size_t i=0;i<size();++i){l+=radQL[i]*q[i]+radPL[i]*p[i];r+=radQR[i]*q[i]+radPR[i]*p[i];}
    return {l,r};
  }

};

struct String {
  Modes m;
  int note=60,unison=0,group=0;
  double resistance=.85,compliance=0,velocity=0,force=0;
};
struct Key {
  std::vector<int> strings;
  double f0=0,B=0,length=0,mu=0,mass=.008,K=1e9,power=2.5;
  double hammerX=0,hammerV=0,age=0,maxForce=0,contactSeconds=0,contactCompliance=0,velocityExponent=1.55;
  bool down=false,hammerActive=false,everStruck=false;
  double damperPosition=1;
  double cachedContact=std::numeric_limits<double>::quiet_NaN(),cachedLoss=std::numeric_limits<double>::quiet_NaN();
};
struct BoardMode {
  double q=0,p=0,w=0,c=0,s=0,damp=1,sigma=0,force=0;
  Vec3 port{};
  std::array<double,2> mic{};
};
struct Options {
  int sampleRate=192000;
  double bridge=1,hammerLoss=.12,loss=1,damper=1;
  bool sympathetic=true,calibrated=true,captureStems=false;
};
struct UnisonPort {
  std::vector<std::pair<int,int>> modes;
  double coefficient=0;
  std::array<double*,3> velocityState{};
  std::array<double,3> omega{},inverseOmega{};
  int count=0;
};

class Piano {
public:
  Options opt;double dt,pedal=0,pedalTarget=0;
  std::array<Key,88> keys;
  std::vector<String> strings;
  std::vector<BoardMode> board;
  std::vector<UnisonPort> unisonPorts;
  Mat3 boardGram{};
  double maxForce=0,contactTime=0,maxContactResidual=0;
  uint64_t forceSolves=0;
  double maxEnergy=0;
  std::array<std::array<double,2>,3> lastStems{};
  explicit Piano(Options o):opt(o),dt(1.0/o.sampleRate){build();}
  // Unison ports cache addresses into mode storage, so instances cannot be copied.
  Piano(const Piano&)=delete;
  Piano& operator=(const Piano&)=delete;
  Piano(Piano&&)=delete;
  Piano& operator=(Piano&&)=delete;
  void build(){
    // Example string/hammer anchors after van Walstijn et al., DAFx 2023.
    // Wound bass extrapolation, loss curves, mistuning and port mobility are
    // authored virtual-instrument parameters, not measurements of a named piano.
    for(int n=21;n<=108;++n){
      auto &k=keys[n-21];
      Cal cal(n);
      double stretch=(n<48?-1.8*std::pow((48-n)/27.0,2):n>72?3.0*std::pow((n-72)/36.0,2):0);
      k.f0=440*std::pow(2.0,(n-69+stretch/100)/12.0);
      k.B=std::clamp(anchor(n,7.4e-5,3.77e-4,8.6e-3),3e-5,.022);
      if(opt.calibrated){
        const auto &a=piano_calibration::anchors[cal.lo],&b=piano_calibration::anchors[cal.hi];
        double centsA=1200*std::log2(a.f1/(440*std::pow(2.0,(a.note-69)/12.0)));
        double centsB=1200*std::log2(b.f1/(440*std::pow(2.0,(b.note-69)/12.0)));
        double cents=std::clamp(lerp(centsA,centsB,cal.t),-25.0,30.0);
        k.f0=440*std::pow(2.0,(n-69+cents/100)/12.0);
        k.B=std::clamp(cal.scalar(&piano_calibration::Anchor::B,true,true),2e-5,.025);
        if(n<36)k.B=piano_calibration::anchors[0].B*std::pow(2.0,(36-n)/18.0);
        k.velocityExponent=cal.scalar(&piano_calibration::Anchor::velocityExponent);
      }
      k.length=std::min(2.03,anchor(n,1.90,.62,.09));
      k.mu=std::clamp(anchor(n,.0184,.0063,.0052),.004,.075);
      if(n<36)k.mu*=std::pow(2.0,(36-n)/19.0);
      k.mass=std::clamp(k.mu*k.length*anchor(n,.14,.75,4.71),.0028,.012);
      k.power=n<=60?lerp(2.3,2.5,(n-36)/24.0):lerp(2.5,3.0,(n-60)/36.0);
      // At 1mm compression: approximately 8N bass to 16N treble.
      double forceAt1mm=lerp(8,16,(n-21)/87.0);
      k.K=forceAt1mm/std::pow(.001,k.power);
      if(opt.calibrated)k.K*=cal.scalar(&piano_calibration::Anchor::hardness,true);
      double strike=std::clamp(anchor(n,.12,.12,.0625),.05,.13);
      int count=n<=31?1:n<=43?2:3;
      const double detunes[3]={-.60,.12,.73};
      for(int u=0;u<count;++u){
        String st;st.note=n;st.unison=u;st.group=n<45?0:n<72?1:2;
        double cents=count==1?0:count==2?(u==0?-.38:.43):detunes[u];
        cents*=.7+.45*(n-21)/87.0;
        if(opt.calibrated)cents*=cal.scalar(&piano_calibration::Anchor::detuneScale);
        double fundamental=k.f0*std::pow(2.0,cents/1200);
        double invSqrtMass=std::sqrt(2.0/(k.mu*k.length));
        double intrinsic=.11+.21*std::pow(fundamental/440.0,.6);
        double bridgeLoss=.20+.48*std::pow(fundamental/440.0,.45);
        for(int pol=0;pol<2;++pol){
          int cap=pol==0?320:48;
          for(int j=1;j<=cap;++j){
            double f=j*fundamental*std::sqrt((1+k.B*j*j)/(1+k.B));
            f*=pol==0?1.0:1.00023+.00002*std::sin(n*.7);
            if(f>(pol==0?19000.0:9000.0))break;
            double sigma=intrinsic+.000012*std::pow(f,1.30)+.00000000035*f*f;
            if(pol)sigma*=.72;
            double ds=n>=89?0:24+1.4*std::sqrt(f)+.001*f;
            // Finite felt footprint: smooth Gaussian spatial contact, 5-10mm.
            double footprint=lerp(.010,.005,(n-21)/87.0)/k.length;
            double h=std::sin(pi*j*strike)*std::exp(-.5*std::pow(pi*j*footprint*.34,2))*invSqrtMass/count;
            if(pol)h*=.035;
            double lossAtPort=bridgeLoss*(1+.11*std::pow((double)j,.8));
            if(opt.calibrated){
              // Intrinsic aftersound and radiative loss stay positive. The
              // extra prompt loss is shared by the choir, not applied to each
              // string independently: out-of-phase unison states can survive.
              double late=cal.mode(j,&piano_calibration::Anchor::late,true);
              if(j>64)late*=std::pow(j/64.0,1.3);
              if(n>84)late*=std::pow(2.0,(n-84)/24.0);
              sigma=late*(pol?.60:.82);
              lossAtPort=late*.18;
            }
            double b=(j%2?-1:1)*std::sqrt(2*lossAtPort/.85)*(pol?.17:1.0);
            st.m.add(f,h,b,sigma,ds,dt,j,pol);
          }
        }
        for(size_t j=0;j<st.m.size();++j){st.compliance+=st.m.b[j]*st.m.b[j];k.contactCompliance+=st.m.hammer[j]*st.m.forceQ[j];}
        k.strings.push_back((int)strings.size());strings.push_back(std::move(st));
      }
      k.contactCompliance+=dt*dt/(2*k.mass);
      if(opt.calibrated){
        int countModes=(int)strings[k.strings.front()].m.size();
        for(int j=0;j<countModes;++j){
          if(strings[k.strings.front()].m.polarization[j])continue;
          int order=strings[k.strings.front()].m.partial[j];
          UnisonPort port;
          for(int si:k.strings){auto &m=strings[si].m;
            if(j<(int)m.size()&&m.partial[j]==order&&!m.polarization[j])port.modes.push_back({si,j});}
          double late=cal.mode(order,&piano_calibration::Anchor::late,true);
          double fast=cal.mode(order,&piano_calibration::Anchor::prompt,true);
          if(n>84){late*=std::pow(2.0,(n-84)/24.0);fast*=std::pow(2.0,(n-84)/24.0);}
          double rate=std::max(0.0,fast-late)*opt.loss;
          port.coefficient=-std::expm1(-2*rate*dt)/port.modes.size();
          port.count=(int)port.modes.size();
          for(int i=0;i<port.count;++i){auto [si,mi]=port.modes[i];auto &m=strings[si].m;
            port.velocityState[i]=&m.p[mi];port.omega[i]=m.omega[mi];port.inverseOmega[i]=1.0/m.omega[mi];}
          unisonPorts.push_back(std::move(port));
        }
      }
    }
    // Reduced orthotropic plate, with rib/boundary corrections and three
    // spatial bridge ports. Modes are analytic and intentionally not a 3-D FE fit.
    struct Plate{double f;int m,n;};std::vector<Plate> plate;
    for(int a=1;a<=60;++a)for(int b=1;b<=48;++b){
      double x=(a+.55)/2.02,y=(b+.55)/1.32;
      double f=pi*.5*std::sqrt((1800*std::pow(x,4)+2*300*x*x*y*y+180*std::pow(y,4))/3.65);
      f=std::sqrt(f*f+70*70);
      f*=1+.018*std::sin(a*3.17+b*1.37);
      if(f<13000)plate.push_back({f,a,b});
    }
    std::sort(plate.begin(),plate.end(),[](const Plate&a,const Plate&b){return a.f<b.f;});
    // Preserve the resolved low modes; retain representative modes in 32-Hz
    // bands above 1.2kHz, where structural damping overlaps neighboring modes.
    std::vector<Plate> reduced;double lastBand=-1;
    for(auto z:plate){double band=std::floor((z.f-1200)/32);if(z.f<1200||band!=lastBand){reduced.push_back(z);lastBand=band;}}
    plate=std::move(reduced);
    for(auto v:plate){
      BoardMode z;z.w=2*pi*v.f;z.c=std::cos(z.w*dt);z.s=std::sin(z.w*dt);
      double eta=.018+.010*std::sqrt(v.f/5000.0);
      z.sigma=eta*z.w*.5;z.damp=std::exp(-z.sigma*dt);
      const double xp[3]={.28,.51,.72},yp[3]={.42,.49,.56};
      for(int g=0;g<3;++g)z.port[g]=.55*std::sin(pi*v.m*xp[g])*std::sin(pi*v.n*yp[g]);
      // Two observation points and mode-dependent radiative cancellation.
      double radiation=std::pow(v.f/(v.f+140),.7)/std::sqrt(1+std::pow(v.f/8500.0,4));
      for(int ch=0;ch<2;++ch){
        double x=ch?.63:.37,y=ch?.60:.39;
        z.mic[ch]=radiation*(.58*std::sin(pi*v.m*x)*std::sin(pi*v.n*y)+.42*(v.m%2&&v.n%2?1.0:0.0));
      }
      board.push_back(z);
    }
    for(auto &z:board)for(int a=0;a<3;++a)for(int b=0;b<3;++b)boardGram[a][b]+=z.port[a]*z.port[b];
    setDamping();
    if(opt.calibrated)buildRadiation();
  }
  // Frequency-domain Schur complement of the same loaded soundboard. It
  // supplies phase for an empirical, smooth modal radiation observation map.
  // Changes affect observation only; no radiation gain enters the mechanics.
  std::array<std::complex<double>,2> radiationTransfer(double w,int group)const{
    using C=std::complex<double>;using CV=std::array<C,3>;using CM=std::array<CV,3>;
    CM Y{},A{};std::array<CV,2>T{};Vec3 R{};
    for(auto &st:strings)R[st.group]+=st.resistance*opt.bridge;
    C iw(0,w);
    for(auto &z:board){C inv=1.0/C(z.w*z.w-w*w,2*z.sigma*w);
      for(int g=0;g<3;++g){for(int h=0;h<3;++h)Y[g][h]+=iw*z.port[g]*z.port[h]*inv;
        for(int ch=0;ch<2;++ch)T[ch][g]+=-w*w*z.mic[ch]*z.port[g]*inv;}}
    for(int g=0;g<3;++g)for(int h=0;h<3;++h)A[g][h]=(g==h?1.0:0.0)+R[g]*Y[g][h];
    CV rhs{};rhs[group]=1;
    for(int k=0;k<3;++k){int pivot=k;for(int j=k+1;j<3;++j)if(std::abs(A[j][k])>std::abs(A[pivot][k]))pivot=j;
      std::swap(A[k],A[pivot]);std::swap(rhs[k],rhs[pivot]);
      for(int j=k+1;j<3;++j){C r=A[j][k]/A[k][k];for(int h=k;h<3;++h)A[j][h]-=r*A[k][h];rhs[j]-=r*rhs[k];}}
    CV v{};for(int k=2;k>=0;--k){C s=rhs[k];for(int h=k+1;h<3;++h)s-=A[k][h]*v[h];v[k]=s/A[k][k];}
    std::array<C,2> out{};for(int ch=0;ch<2;++ch)for(int g=0;g<3;++g)out[ch]+=T[ch][g]*v[g];return out;
  }
  void buildRadiation(){
    using C=std::complex<double>;
    for(auto &st:strings){Cal cal(st.note);auto &m=st.m;
      for(size_t j=0;j<m.size();++j){auto H=radiationTransfer(m.omega[j],st.group);
        double mag=std::sqrt((std::norm(H[0])+std::norm(H[1]))*.5);m.radiationMagnitude[j]=mag;
        for(int ch=0;ch<2;++ch){C coeff=C(0,m.omega[j])*st.resistance*opt.bridge*m.b[j]*H[ch];
          (ch?m.baseQR:m.baseQL)[j]=coeff.real();(ch?m.basePR:m.basePL)[j]=coeff.imag();}
        if(!piano_calibration::radiationEnabled)continue;
        double target=std::pow(10.0,cal.mode(m.partial[j],m.polarization[j]?&piano_calibration::Anchor::radiationAfterDb:&piano_calibration::Anchor::radiationDb)/20);
        double ratio=target/std::max(mag,1e-8);
        ratio=std::clamp(ratio,.025,40.0);
        // Return toward the analytic model above the measured harmonic range.
        if(m.partial[j]>64)ratio=1+(ratio-1)*std::exp(-(m.partial[j]-64)/24.0);
        for(int ch=0;ch<2;++ch){C coeff=C(0,m.omega[j])*st.resistance*opt.bridge*m.b[j]*H[ch]*(ratio-1);
          (ch?m.radQR:m.radQL)[j]=coeff.real();(ch?m.radPR:m.radPL)[j]=coeff.imag();}
      }
    }
  }
  void unisonStep(){
    for(auto &u:unisonPorts){
      double sum=u.omega[0]* *u.velocityState[0];
      if(u.count>1)sum+=u.omega[1]* *u.velocityState[1];
      if(u.count>2)sum+=u.omega[2]* *u.velocityState[2];
      double impulse=u.coefficient*sum;
      *u.velocityState[0]-=impulse*u.inverseOmega[0];
      if(u.count>1)*u.velocityState[1]-=impulse*u.inverseOmega[1];
      if(u.count>2)*u.velocityState[2]-=impulse*u.inverseOmega[2];
    }
  }

  void noteOn(int n,double vel){
    if(n<21||n>108)return;
    auto &k=keys[n-21];k.down=true;k.damperPosition=0;k.hammerActive=true;k.everStruck=true;k.age=0;k.maxForce=0;k.contactSeconds=0;
    for(int i:k.strings){auto &m=strings[i].m;for(size_t j=0;j<m.size();++j)m.damp[j]=std::exp(-opt.loss*m.loss[j]*dt);}
    k.cachedContact=0;k.cachedLoss=opt.loss;
    double y=0;for(int i:k.strings)y+=strings[i].m.displacement();
    k.hammerX=y-.000015;
    k.hammerV=.22+5.6*std::pow(std::clamp(vel/127.0,0.0,1.0),k.velocityExponent);
  }
  void noteOff(int n){if(n>=21&&n<=108)keys[n-21].down=false;}
  void setDamping(){
    for(auto &k:keys){
      double target=k.down?0:1-pedal;
      k.damperPosition+=(1-std::exp(-64*dt/.022))*(target-k.damperPosition);
      double contact=std::pow(std::max(0.0,(k.damperPosition-.08)/.92),2.5)*opt.damper;
      if(contact==k.cachedContact&&opt.loss==k.cachedLoss)continue;
      k.cachedContact=contact;k.cachedLoss=opt.loss;
      for(int i:k.strings){auto &m=strings[i].m;for(size_t j=0;j<m.size();++j)m.damp[j]=std::exp(-(opt.loss*m.loss[j]+contact*m.damper[j])*dt);}
    }
  }
  static double potential(double x,double K,double p){return x<=0?0:K*std::pow(x,p+1)/(p+1);}
  static double discreteForce(double a,double b,double K,double p){
    if(std::max(a,b)<=0)return 0;
    if(std::abs(a-b)<1e-10*std::max(1e-5,std::max(std::abs(a),std::abs(b))))return K*std::pow(std::max(0.0,.5*(a+b)),p);
    return (potential(b,K,p)-potential(a,K,p))/(b-a);
  }
  double contact(Key &k,double delta0,double freeDelta){
    const double A=k.contactCompliance;
    auto residual=[&](double f){double delta=freeDelta-A*f;double elastic=discreteForce(delta0,delta,k.K,k.power);
      // Dissipative Hunt-Crossley law. This is not Stulov's memory model.
      double hc=std::max(0.0,1+opt.hammerLoss*(delta-delta0)/dt);
      return f-elastic*hc;};
    if(delta0<=0&&freeDelta<=0)return 0;
    double lo=0,hi=std::max(1.0,2*k.K*std::pow(std::max({0.0,delta0,freeDelta}),k.power)*(1+opt.hammerLoss*std::abs(k.hammerV)));
    for(int j=0;j<32&&residual(hi)<0;++j)hi*=2;
    if(residual(hi)<0)throw std::runtime_error("contact bracket failed");
    for(int j=0;j<42;++j){double mid=.5*(lo+hi);if(residual(mid)>0)hi=mid;else lo=mid;}
    double f=.5*(lo+hi);maxContactResidual=std::max(maxContactResidual,std::abs(residual(f))/(1+f));++forceSolves;
    return f;
  }
  void oscillators(){
    for(auto &k:keys){
      double y0=0;
      if(k.hammerActive)for(int i:k.strings)y0+=strings[i].m.displacement();
      for(int i:k.strings)strings[i].m.freeStep();
      if(k.hammerActive){
        double yf=0;for(int i:k.strings)yf+=strings[i].m.displacement();
        double d0=k.hammerX-y0,xf=k.hammerX+dt*k.hammerV;
        double F=contact(k,d0,xf-yf);
        for(int i:k.strings)strings[i].m.force(F);
        k.hammerX=xf-dt*dt*F/(2*k.mass);k.hammerV-=dt*F/k.mass;k.age+=dt;
        k.maxForce=std::max(k.maxForce,F);maxForce=std::max(maxForce,F);
        if(F>1e-4){k.contactSeconds+=dt;contactTime+=dt;}
        if((k.hammerV<0&&k.hammerX<yf-.002)||k.age>.040)k.hammerActive=false;
      }
      for(int i:k.strings)strings[i].m.finishDamping();
    }
    for(auto &z:board){double v=z.p*z.damp,y=z.q;z.q=z.c*y+z.s*v;z.p=(z.c*v-z.s*y)*z.damp;}
  }
  // Implicit midpoint on the complete reciprocal viscous port network.
  // All string ports couple to the same board; the three-dimensional Schur
  // complement solves the full junction simultaneously. For R>=0 it cannot
  // add mechanical energy. All 88 keys remain present, including unstruck ones.
  void bridgeStep(double step){
    if(opt.bridge<=0){for(auto &z:board)z.force=0;return;}
    Vec3 boardV{},sum{},beta{};
    for(auto &z:board)for(int g=0;g<3;++g)boardV[g]+=z.port[g]*z.w*z.p;
    for(auto &st:strings){
      auto &k=keys[st.note-21];
      if(!opt.sympathetic&&!k.everStruck){st.velocity=0;st.force=0;continue;}
      double r=st.resistance*opt.bridge,den=1+.5*step*r*st.compliance;
      st.velocity=st.m.portVelocity();
      st.force=-r*(st.velocity-boardV[st.group])/den;
      sum[st.group]+=st.force;beta[st.group]+=r/den;
    }
    Mat3 mat{};for(int g=0;g<3;++g)for(int h=0;h<3;++h)mat[g][h]=(g==h?1:0)+.5*step*beta[g]*boardGram[g][h];
    Vec3 total=solve3(mat,sum),correction{};
    for(int g=0;g<3;++g)for(int h=0;h<3;++h)correction[g]+=.5*step*boardGram[g][h]*total[h];
    for(auto &st:strings){
      auto &k=keys[st.note-21];if(!opt.sympathetic&&!k.everStruck)continue;
      double r=st.resistance*opt.bridge,den=1+.5*step*r*st.compliance;
      st.force-=r*correction[st.group]/den;st.m.portImpulse(step*st.force);
    }
    for(auto &z:board){double force=0;for(int g=0;g<3;++g)force-=z.port[g]*total[g];z.force=force;z.p+=step*force/z.w;}
  }
  std::array<double,2> step(uint64_t frame){
    if(frame%64==0){pedal+=(1-std::exp(-64*dt/.012))*(pedalTarget-pedal);setDamping();}
    // The adjacent bridge half steps coalesce into one full step between
    // oscillator steps (zero initial velocity makes the first half a no-op).
    oscillators();unisonStep();bridgeStep(dt);
    std::array<double,2> out{};
    // Radiated pressure proxy: soundboard acceleration observed at two points.
    for(auto &z:board){double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+z.force;for(int ch=0;ch<2;++ch)out[ch]+=acc*z.mic[ch];}
    if(opt.captureStems){lastStems={};std::array<double,2> baseTotal{};
      for(auto &st:strings){auto &m=st.m;for(size_t j=0;j<m.size();++j){int pol=m.polarization[j];
        double l=m.baseQL[j]*m.q[j]+m.basePL[j]*m.p[j],r=m.baseQR[j]*m.q[j]+m.basePR[j]*m.p[j];
        baseTotal[0]+=l;baseTotal[1]+=r;
        lastStems[pol][0]+=l+m.radQL[j]*m.q[j]+m.radPL[j]*m.p[j];lastStems[pol][1]+=r+m.radQR[j]*m.q[j]+m.radPR[j]*m.p[j];}}
      for(int ch=0;ch<2;++ch)lastStems[2][ch]=out[ch]-baseTotal[ch];}
    if(opt.calibrated&&piano_calibration::radiationEnabled)for(auto &st:strings){auto r=st.m.radiation();out[0]+=r[0];out[1]+=r[1];}
    return out;
  }
  double energy()const{
    double e=0;for(auto &s:strings)e+=s.m.energy();
    for(auto &z:board)e+=.5*z.w*z.w*(z.q*z.q+z.p*z.p);
    for(auto &k:keys)if(k.hammerActive){double y=0;for(int i:k.strings)y+=strings[i].m.displacement();e+=.5*k.mass*k.hammerV*k.hammerV+potential(k.hammerX-y,k.K,k.power);}
    return e;
  }
  size_t modeCount()const{size_t n=0;for(auto &s:strings)n+=s.m.size();return n;}
  void dump(const std::string &path)const{
    std::ofstream f(path);f<<std::setprecision(12)<<"{\"sample_rate\":"<<opt.sampleRate<<",\"string_count\":"<<strings.size()<<",\"string_modes\":"<<modeCount()<<",\"soundboard_modes\":"<<board.size()<<",\"keys\":[";
    for(size_t j=0;j<keys.size();++j){auto &k=keys[j];if(j)f<<',';f<<"{\"midi\":"<<j+21<<",\"fundamental_hz\":"<<k.f0<<",\"B\":"<<k.B<<",\"length_m\":"<<k.length<<",\"linear_density_kg_m\":"<<k.mu<<",\"hammer_mass_kg\":"<<k.mass<<",\"hammer_exponent\":"<<k.power<<",\"hammer_stiffness\":"<<k.K<<",\"unisons\":"<<k.strings.size()<<"}";}f<<"]}\n";
  }
  void dumpRadiation(const std::string &path)const{
    std::ofstream f(path);f<<std::setprecision(12)<<"[";bool first=true;
    for(auto &st:strings)if(st.unison==0){auto &m=st.m;
      for(size_t j=0;j<m.size();++j){if(!first)f<<',';first=false;f<<"{\"midi\":"<<st.note<<",\"n\":"<<m.partial[j]<<",\"polarization\":"<<m.polarization[j]<<",\"frequency_hz\":"<<m.omega[j]/(2*pi)<<",\"H_magnitude\":"<<m.radiationMagnitude[j]<<"}";}}
    f<<"]\n";
  }
};

struct Event{double time;std::string kind;int note;double value;};
std::vector<Event> readEvents(const std::string &path){
  std::ifstream f(path);if(!f)throw std::runtime_error("cannot read events: "+path);
  std::vector<Event> events;std::string line;
  while(std::getline(f,line)){
    if(line.empty()||line[0]=='#')continue;Event e;std::istringstream s(line);
    if(!(s>>e.time>>e.kind>>e.note>>e.value)||!std::isfinite(e.time)||e.time<0||!std::isfinite(e.value))throw std::runtime_error("invalid event: "+line);
    if(e.kind!="on"&&e.kind!="off"&&e.kind!="pedal")throw std::runtime_error("unknown event: "+line);
    if(e.kind=="pedal"?(e.value<0||e.value>1):(e.note<21||e.note>108||e.value<0||e.value>127))throw std::runtime_error("event out of range: "+line);
    events.push_back(e);
  }
  std::stable_sort(events.begin(),events.end(),[](auto &a,auto &b){return a.time<b.time;});return events;
}
void u16(std::ofstream &f,uint16_t v){char b[2]={(char)v,(char)(v>>8)};f.write(b,2);}
void u32(std::ofstream &f,uint32_t v){char b[4]={(char)v,(char)(v>>8),(char)(v>>16),(char)(v>>24)};f.write(b,4);}
void wav(const std::string &path,const std::vector<float>&audio,int rate){
  if(audio.size()>((uint64_t(1)<<32)-44)/4)throw std::runtime_error("WAV too large");
  std::ofstream f(path,std::ios::binary);if(!f)throw std::runtime_error("cannot write WAV");
  f.write("RIFF",4);u32(f,36+(uint32_t)audio.size()*4);f.write("WAVEfmt ",8);u32(f,16);u16(f,3);u16(f,2);u32(f,rate);u32(f,rate*8);u16(f,8);u16(f,32);f.write("data",4);u32(f,(uint32_t)audio.size()*4);
  f.write(reinterpret_cast<const char*>(audio.data()),audio.size()*sizeof(float));if(!f)throw std::runtime_error("WAV write failed");
}

int selfTest(){
  Options o;o.sampleRate=192000;o.bridge=0;o.hammerLoss=0;o.loss=0;o.damper=0;
  Piano p(o);p.noteOn(60,100);p.setDamping();
  double initial=p.energy(),maxerr=0,minE=initial;
  // Do not remove the hammer from the energy audit; it remains in the accounting
  // after separation, while the production engine models backcheck removal.
  auto &k=p.keys[60-21];
  for(int i=0;i<2400;++i){p.oscillators();bool active=k.hammerActive;k.hammerActive=true;double e=p.energy();maxerr=std::max(maxerr,std::abs(e-initial)/initial);minE=std::min(minE,e);k.hammerActive=active;if(!active)break;}
  Options b;b.sampleRate=96000;b.loss=0;b.damper=0;b.hammerLoss=0;
  Piano network(b);std::mt19937 rng(812);std::normal_distribution<double> norm;
  for(auto &s:network.strings)for(size_t j=0;j<s.m.size();++j)s.m.p[j]=norm(rng)*1e-5/s.m.omega[j];
  for(auto &m:network.board)m.p=norm(rng)*1e-5/m.w;
  double e0=network.energy(),previous=e0,maxRise=0;
  for(int i=0;i<200;++i){network.bridgeStep(network.dt);double e=network.energy();maxRise=std::max(maxRise,(e-previous)/e0);previous=e;}
  bool ok=maxerr<2e-7&&maxRise<1e-12&&previous<=e0&&p.maxContactResidual<1e-8;
  std::cout<<std::setprecision(12)<<"{\"passed\":"<<(ok?"true":"false")<<",\"conservative_contact_relative_energy_error\":"<<maxerr<<",\"bridge_max_relative_energy_increase\":"<<maxRise<<",\"bridge_energy_remaining_ratio\":"<<previous/e0<<",\"contact_max_relative_residual\":"<<p.maxContactResidual<<"}\n";
  return ok?0:1;
}
} // namespace grand

int main(int argc,char **argv){
 try{
  using namespace grand;Options opt;std::string input,output,metrics,dump,radiationDump,stemPrefix;double tail=7,duration=0;
  for(int j=1;j<argc;++j){std::string a=argv[j];
    if(a=="--self-test")return selfTest();
    if(a=="--no-sympathetic"){opt.sympathetic=false;continue;}
    if(a=="--uncalibrated"){opt.calibrated=false;continue;}
    if(a=="--help"){std::cout<<"grand --events score.events --output raw.wav [--sample-rate 192000] [--tail 7] [--duration seconds] [--metrics file.json] [--dump-model file.json] [--bridge 1] [--hammer-loss .12] [--loss 1] [--damper 1] [--no-sympathetic]\nFloat32 stereo raw output; tools/render.py produces 48kHz/24bit deliverables.\n";return 0;}
    if(j+1>=argc)throw std::runtime_error("missing argument: "+a);std::string v=argv[++j];
    if(a=="--events")input=v;else if(a=="--output")output=v;else if(a=="--sample-rate")opt.sampleRate=std::stoi(v);
    else if(a=="--tail")tail=std::stod(v);else if(a=="--duration")duration=std::stod(v);else if(a=="--metrics")metrics=v;else if(a=="--dump-model")dump=v;
    else if(a=="--dump-radiation")radiationDump=v;
    else if(a=="--stem-prefix"){stemPrefix=v;opt.captureStems=true;}
    else if(a=="--bridge")opt.bridge=std::stod(v);else if(a=="--hammer-loss")opt.hammerLoss=std::stod(v);else if(a=="--loss")opt.loss=std::stod(v);else if(a=="--damper")opt.damper=std::stod(v);else throw std::runtime_error("unknown option: "+a);
  }
  if(input.empty()||output.empty())throw std::runtime_error("--events and --output required; see --help");
  if(opt.sampleRate<48000||opt.sampleRate>384000||!std::isfinite(tail)||tail<0||tail>60||!std::isfinite(duration)||duration<0||duration>600||!std::isfinite(opt.bridge)||opt.bridge<0||opt.bridge>10||!std::isfinite(opt.loss)||opt.loss<0||opt.loss>10||!std::isfinite(opt.damper)||opt.damper<0||opt.damper>10||!std::isfinite(opt.hammerLoss)||opt.hammerLoss<0||opt.hammerLoss>10)throw std::runtime_error("invalid render configuration");
  auto events=readEvents(input);if(duration<=0)duration=(events.empty()?0:events.back().time)+tail;
  Piano p(opt);if(!dump.empty())p.dump(dump);if(!radiationDump.empty())p.dumpRadiation(radiationDump);
  size_t frames=(size_t)std::ceil(duration*opt.sampleRate);std::vector<float> audio(frames*2);
  std::array<std::vector<float>,3> stems;if(opt.captureStems)for(auto &s:stems)s.resize(frames*2);
  std::array<std::array<double,2>,3> stemPrevious{},stemHp{};
  std::cerr<<p.strings.size()<<" strings / "<<p.modeCount()<<" string modes / "<<p.board.size()<<" board modes; "<<duration<<" seconds @ "<<opt.sampleRate<<" Hz\n";
  auto start=std::chrono::steady_clock::now();size_t next=0;double peak=0,sumSquare=0;uint64_t nonfinite=0;std::array<double,2> previous{},hp{};
  const double pole=std::exp(-2*pi*24/opt.sampleRate);
  for(size_t frame=0;frame<frames;++frame){
    while(next<events.size()&&(uint64_t)std::llround(events[next].time*opt.sampleRate)<=frame){auto &e=events[next++];if(e.kind=="on"&&e.value>0)p.noteOn(e.note,e.value);else if(e.kind=="off"||e.kind=="on")p.noteOff(e.note);else p.pedalTarget=e.value;}
    auto x=p.step(frame);
    if(opt.captureStems)for(int s=0;s<3;++s)for(int ch=0;ch<2;++ch){double v=p.lastStems[s][ch];stemHp[s][ch]=pole*(stemHp[s][ch]+v-stemPrevious[s][ch]);stemPrevious[s][ch]=v;stems[s][frame*2+ch]=(float)stemHp[s][ch];}
    for(int ch=0;ch<2;++ch){hp[ch]=pole*(hp[ch]+x[ch]-previous[ch]);previous[ch]=x[ch];double v=hp[ch];if(!std::isfinite(v)){++nonfinite;throw std::runtime_error("non-finite audio");}audio[frame*2+ch]=(float)v;peak=std::max(peak,std::abs(v));sumSquare+=v*v;}
  }
  wav(output,audio,opt.sampleRate);double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  if(opt.captureStems){const char *names[]={"-primary.wav","-secondary.wav","-transient.wav"};for(int s=0;s<3;++s)wav(stemPrefix+names[s],stems[s],opt.sampleRate);}
  std::ostringstream report;report<<std::setprecision(12)<<"{\"sample_rate\":"<<opt.sampleRate<<",\"duration_seconds\":"<<duration<<",\"wall_seconds\":"<<wall<<",\"realtime_factor\":"<<wall/duration<<",\"string_count\":"<<p.strings.size()<<",\"string_modes\":"<<p.modeCount()<<",\"board_modes\":"<<p.board.size()<<",\"raw_peak\":"<<peak<<",\"raw_rms\":"<<std::sqrt(sumSquare/(frames*2))<<",\"nonfinite_samples\":"<<nonfinite<<",\"max_hammer_force_N\":"<<p.maxForce<<",\"accumulated_contact_seconds\":"<<p.contactTime<<",\"contact_solves\":"<<p.forceSolves<<",\"contact_max_relative_residual\":"<<p.maxContactResidual<<",\"final_mechanical_energy_J\":"<<p.energy()<<"}";
  if(!metrics.empty()){std::ofstream f(metrics);f<<report.str()<<'\n';}std::cout<<report.str()<<'\n';return 0;
 }catch(const std::exception &e){std::cerr<<"grand: "<<e.what()<<'\n';return 1;}
}
