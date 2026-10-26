#include "keyra/physics/WaveguideString.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {
using String=keyra::physics::WaveguideString;
using Complex=std::complex<double>;
constexpr double pi=3.14159265358979323846;
struct Case {std::string name;double f1=0,B=0,Z=0,position=0;String::Config config{};};
bool read(const char* path,Case& c){
  std::ifstream file(path);if(!(file>>c.name>>c.f1>>c.B>>c.Z>>c.position))return false;
  auto pathRead=[&](String::PathConfig& p){
    if(!(file>>p.delaySamples>>p.lossGain>>p.lossMix>>p.allpassCount)||p.allpassCount>String::allpassCapacity)return false;
    for(unsigned j=0;j<p.allpassCount;++j)if(!(file>>p.allpass[j]))return false;
    return true;
  };
  c.config.impedance=c.Z;
  if(!pathRead(c.config.left)||!pathRead(c.config.toBridge))return false;
  c.config.fromBridge=c.config.toBridge;
  String validation;return validation.prepare(c.config)&&c.f1>0&&c.B>=0&&c.position>0&&c.position<1;
}
double frequency(const Case& c,unsigned n){return n*c.f1*std::sqrt((1+c.B*n*n)/(1+c.B));}
double sigma(const Case& c,double f){return .11+.21*std::pow(c.f1/440.,.6)+.000012*std::pow(f,1.30)+.00000000035*f*f;}
Complex loop(const Case& c,Complex z){
  return String::transfer(c.config.left,z)*String::transfer(c.config.toBridge,z)*String::transfer(c.config.fromBridge,z);
}
Complex pole(const Case& c,double target){
  Complex z=std::exp(Complex(-sigma(c,target),2*pi*target)/String::sampleRate);
  for(unsigned i=0;i<80;++i){
    const Complex residual=loop(c,z)-1.;
    if(std::abs(residual)<2.e-12)break;
    const double epsilon=1.e-7;
    const Complex derivative=(loop(c,z+epsilon)-loop(c,z-epsilon))/(2*epsilon);
    if(!std::isfinite(std::abs(derivative))||std::abs(derivative)<1.e-12)return Complex(0,0);
    Complex correction=residual/derivative;
    if(std::abs(correction)>.02)correction*=.02/std::abs(correction);
    z-=correction;
  }
  return z;
}
struct Transfer {Complex contact{},reaction{},bridgeImpedance{};};
Transfer transfer(const Case& c,Complex z){
  const auto p=String::transfer(c.config.left,z),q=String::transfer(c.config.toBridge,z);
  const auto r=String::transfer(c.config.fromBridge,z),P=p*q*r;
  return {(1.-p)*(1.-q*r)/(2*c.Z*(1.-P)),q*(1.-p)/(1.-P),c.Z*(1.+P)/(1.-P)};
}
// Continuous isolated stiff-string point mobility, sine modes and original
// authored intrinsic sigma. Z fixes mu*length = Z*sqrt(1+B)/(2*f1).
Complex modalContact(const Case& c,Complex s){
  Complex y=0;const double inverseMass=4*c.f1/(c.Z*std::sqrt(1+c.B));
  for(unsigned n=1;n<=320;++n){const double f=frequency(c,n);if(f>19000)break;
    const double shape=std::sin(pi*n*c.position);
    y+=inverseMass*shape*shape*s/(s*s+2*sigma(c,f)*s+4*pi*pi*f*f);
  }
  return y;
}
// Dispersion-matched traveling-line endpoint mobility. This comparison shares
// the fitted stiff-string k(omega), but does not impose bending boundary data.
Complex dispersiveBridgeMobility(const Case& c,double omega){
  const double r=omega/(2*pi*c.f1);
  const double n2=c.B>0?2*r*r*(1+c.B)/(1+std::sqrt(1+4*c.B*r*r*(1+c.B))):r*r;
  const double n=std::sqrt(n2),phase=2*pi*n;
  const double roundtripGroupSeconds=std::sqrt((1+c.B)*(1+c.B*n2))/(c.f1*(1+2*c.B*n2));
  const double attenuation=sigma(c,omega/(2*pi))*roundtripGroupSeconds;
  const auto P=std::exp(Complex(-attenuation,-phase));
  return (1.-P)/(c.Z*(1.+P));
}
void report(const Case& c){
  std::cout<<"{\"name\":\""<<c.name<<"\",\"f1_hz\":"<<c.f1<<",\"B\":"<<c.B<<",\"Z_kg_s\":"<<c.Z<<",\"partials\":[";
  bool first=true;double maxCents=0,sumCents=0,maxSigmaRelative=0;unsigned count=0;
  for(unsigned n=1;n<=20;++n){
    const double target=frequency(c,n);if(target>19000)break;
    const auto z=pole(c,target);const double f=std::arg(z)*String::sampleRate/(2*pi);
    const double decay=-String::sampleRate*std::log(std::abs(z));
    const double cents=1200*std::log2(f/target),wanted=sigma(c,target);
    const double residual=std::abs(loop(c,z)-1.);
    maxCents=std::max(maxCents,std::abs(cents));sumCents+=cents*cents;
    maxSigmaRelative=std::max(maxSigmaRelative,std::abs(decay/wanted-1));++count;
    if(!first)std::cout<<',';
    first=false;
    std::cout<<"{\"n\":"<<n<<",\"target_hz\":"<<target<<",\"pole_hz\":"<<f<<",\"cents\":"<<cents
             <<",\"sigma_per_second\":"<<decay<<",\"target_sigma_per_second\":"<<wanted<<",\"pole_residual\":"<<residual<<'}';
  }
  // Several complex-frequency samples validate the real state loop against
  // independently derived two-port transfers, including the bridge sign.
  std::vector<double> probes{c.f1*.77,c.f1*1.13,c.f1*1.37,c.f1*2.61,
                             c.f1*4.31,c.f1*8.37,c.f1*12.2};
  const double epsilon=6.;
  std::vector<Complex> accumContact(probes.size()),accumReaction(probes.size()),accumBridge(probes.size());
  String contact,bridge;contact.prepare(c.config);bridge.prepare(c.config);
  for(unsigned frame=0;frame<3*unsigned(String::sampleRate);++frame){
    const auto a=contact.step(frame==0?1.:0.);
    const auto b=bridge.step(0,frame==0?1.:0.);
    for(unsigned i=0;i<probes.size();++i){
      const auto weight=std::exp(Complex(-epsilon,-2*pi*probes[i])*double(frame)/String::sampleRate);
      accumContact[i]+=a.contactVelocity*weight;accumReaction[i]-=a.bridgeForce*weight;
      accumBridge[i]+=b.bridgeForce*weight;
    }
  }
  double maxTransferResidual=0;
  std::cout<<"],\"max_abs_cents\":"<<maxCents<<",\"rms_cents\":"<<std::sqrt(sumCents/count)
           <<",\"max_relative_sigma_error\":"<<maxSigmaRelative<<",\"admittance\":[";
  for(unsigned i=0;i<probes.size();++i){
    const auto z=std::exp(Complex(epsilon,2*pi*probes[i])/String::sampleRate);
    const auto t=transfer(c,z);
    const auto continuous=modalContact(c,Complex(epsilon,2*pi*probes[i]));
    const double relative=std::abs(t.contact-continuous)/std::abs(continuous);
    const double residual=std::max({std::abs(t.contact-accumContact[i])/std::max(1.e-9,std::abs(t.contact)),
      std::abs(t.reaction-accumReaction[i])/std::max(1.e-9,std::abs(t.reaction)),
      std::abs(t.bridgeImpedance-accumBridge[i])/std::max(1.e-9,std::abs(t.bridgeImpedance))});
    maxTransferResidual=std::max(maxTransferResidual,residual);
    const auto unit=std::exp(Complex(0,2*pi*probes[i])/String::sampleRate);
    const auto modeledBridge=1./transfer(c,unit).bridgeImpedance;
    const auto priorBridge=dispersiveBridgeMobility(c,2*pi*probes[i]);
    if(i)std::cout<<',';
    std::cout<<"{\"frequency_hz\":"<<probes[i]<<",\"contact_modal_relative_error\":"<<relative
             <<",\"contact_modal_magnitude_error_db\":"<<20*std::log10(std::abs(t.contact/continuous))
             <<",\"bridge_traveling_prior_relative_error\":"<<std::abs(modeledBridge-priorBridge)/std::abs(priorBridge)
             <<",\"simulation_transfer_relative_residual\":"<<residual<<'}';
  }
  std::cout<<"],\"max_simulation_transfer_residual\":"<<maxTransferResidual
           <<",\"three_second_contact_balance_residual_J\":"<<contact.balanceResidual()
           <<",\"three_second_bridge_balance_residual_J\":"<<bridge.balanceResidual();
  // Independent voices/uncorrelated state; working set is larger than one rail.
  // No callback deadline or full-piano speed claim follows from this average.
  std::vector<String> bank(230);for(auto& string:bank)string.prepare(c.config);
  constexpr unsigned frames=12000;
  double check=0;
  std::array<double,3> wall{},cpu{};
  for(unsigned trial=0;trial<wall.size();++trial){
    for(auto& string:bank)string.prepare(c.config);
    const auto start=std::chrono::steady_clock::now();
    const auto cpuStart=std::clock();
    for(unsigned frame=0;frame<frames;++frame)
      for(unsigned voice=0;voice<bank.size();++voice){
        const auto result=bank[voice].step(frame==(voice%31)?1.:0.);
        check+=result.bridgeForce;
      }
    wall[trial]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    cpu[trial]=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;
  }
  std::sort(wall.begin(),wall.end());std::sort(cpu.begin(),cpu.end());
  const double seconds=wall[1];
  std::cout<<",\"benchmark_voices\":230,\"benchmark_audio_seconds\":"<<frames/String::sampleRate
           <<",\"benchmark_wall_seconds\":"<<seconds<<",\"benchmark_wall_per_audio_second\":"<<seconds/(frames/String::sampleRate)
           <<",\"benchmark_cpu_per_audio_second\":"<<cpu[1]/(frames/String::sampleRate)
           <<",\"benchmark_wall_min_per_audio_second\":"<<wall.front()/(frames/String::sampleRate)
           <<",\"benchmark_wall_max_per_audio_second\":"<<wall.back()/(frames/String::sampleRate)
           <<",\"benchmark_checksum\":"<<check<<",\"bytes_per_string\":"<<sizeof(String)<<'}';
}
}
int main(int argc,char** argv){
  if(argc<2){std::cerr<<"Usage: keyra_waveguide_probe candidate.cfg [candidate.cfg ...]\n";return 2;}
  std::cout<<std::setprecision(17)<<"{\"sample_rate\":48000,\"cases\":[";
  for(int i=1;i<argc;++i){Case c;if(!read(argv[i],c)){std::cerr<<"Invalid candidate "<<argv[i]<<'\n';return 2;}
    if(i>1)std::cout<<',';
    report(c);}
  std::cout<<"]}\n";
}
