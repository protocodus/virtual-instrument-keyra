// Independent physical contracts against the actual engine, not an alternate DSP.
#define main grand_cli_main
#include "../src/grand.cpp"
#undef main

using namespace grand;
double stringEnergy(const Piano &p, int midi) {
  double e=0; for(int i:p.keys[midi-21].strings)e+=p.strings[i].m.energy(); return e;
}
double otherEnergy(const Piano &p,int midi) {
  double e=0;for(int n=21;n<=108;++n)if(n!=midi)e+=stringEnergy(p,n);return e;
}
double centroid(const Piano &p,int midi) {
  double num=0,den=0;
  for(int i:p.keys[midi-21].strings){auto &m=p.strings[i].m;
    for(size_t j=0;j<m.size();++j){double e=.5*m.omega[j]*m.omega[j]*(m.q[j]*m.q[j]+m.p[j]*m.p[j]);num+=e*m.omega[j]/(2*pi);den+=e;}}
  return num/den;
}
double energyWithBackcheckedHammer(const Piano &p) {
  double e=p.energy();for(auto &k:p.keys)if(!k.hammerActive)e+=.5*k.mass*k.hammerV*k.hammerV;return e;
}
int main(){
  double energyError=0,dissipativeRise=0,minForce=1e9,maxResidual=0;
  // Contact is tested in isolated, loss-free modal strings at three registers
  // and two dynamics; retain backchecked hammer kinetic energy in the audit.
  for(int n:{21,60,108})for(int v:{32,127})for(double loss:{0.,.12}){
    Options o;o.sampleRate=96000;o.bridge=0;o.loss=0;o.damper=0;o.hammerLoss=loss;
    Piano p(o);p.noteOn(n,v);p.setDamping();double initial=p.energy(),prev=initial;
    auto &k=p.keys[n-21];
    for(int t=0;t<2400;++t){
      p.oscillators();double e=energyWithBackcheckedHammer(p);
      if(loss==0)energyError=std::max(energyError,std::abs(e-initial)/initial);
      else dissipativeRise=std::max(dissipativeRise,(e-prev)/initial);
      prev=e;if(!k.hammerActive)break;
    }
    minForce=std::min(minForce,k.maxForce);maxResidual=std::max(maxResidual,p.maxContactResidual);
  }
  // Actual contact should inject more energy and proportionally more high-mode
  // energy when struck hard. No sample layers or post-filter changes are involved.
  std::array<double,2> velEnergy{},velCentroid{},velForce{},velContact{};
  for(int j=0;j<2;++j){Options o;o.sampleRate=96000;o.bridge=0;o.loss=0;o.damper=0;Piano p(o);p.noteOn(60,j?115:35);p.setDamping();
    for(int t=0;t<1920;++t)p.oscillators();
    velEnergy[j]=stringEnergy(p,60);velCentroid[j]=centroid(p,60);velForce[j]=p.maxForce;velContact[j]=p.contactTime;
  }
  double damped=0,sustained=0,sympathetic=0,source=0;
  for(int sustain=0;sustain<2;++sustain){Options o;o.sampleRate=96000;Piano p(o);p.pedal=p.pedalTarget=sustain;p.noteOn(60,100);
    for(uint64_t t=0;t<57600;++t){if(t==11520)p.noteOff(60);p.step(t);if(t==28800&&sustain){sympathetic=otherEnergy(p,60);source=stringEnergy(p,60);}}
    (sustain?sustained:damped)=stringEnergy(p,60);
  }
  bool pass=energyError<2e-7&&dissipativeRise<2e-7&&maxResidual<1e-7&&minForce>0&&
    velEnergy[1]>4*velEnergy[0]&&velCentroid[1]>1.05*velCentroid[0]&&velContact[1]<velContact[0]&&
    sustained>100*damped&&sympathetic>1e-14&&sympathetic<source;
  std::cout<<std::setprecision(12)<<"{\"passed\":"<<(pass?"true":"false")
    <<",\"contact_cases\":12,\"contact_registers\":[21,60,108],\"contact_velocities\":[32,127]"
    <<",\"conservative_max_relative_energy_error\":"<<energyError
    <<",\"dissipative_max_relative_energy_increase\":"<<dissipativeRise
    <<",\"max_contact_relative_residual\":"<<maxResidual
    <<",\"soft_string_energy_J\":"<<velEnergy[0]<<",\"hard_string_energy_J\":"<<velEnergy[1]
    <<",\"soft_modal_energy_centroid_hz\":"<<velCentroid[0]<<",\"hard_modal_energy_centroid_hz\":"<<velCentroid[1]
    <<",\"soft_contact_seconds\":"<<velContact[0]<<",\"hard_contact_seconds\":"<<velContact[1]
    <<",\"soft_peak_force_N\":"<<velForce[0]<<",\"hard_peak_force_N\":"<<velForce[1]
    <<",\"damped_key_energy_after_release_J\":"<<damped<<",\"sustained_key_energy_after_release_J\":"<<sustained
    <<",\"unstruck_string_energy_J\":"<<sympathetic<<",\"struck_string_energy_J\":"<<source<<"}\n";
  return pass?0:1;
}
