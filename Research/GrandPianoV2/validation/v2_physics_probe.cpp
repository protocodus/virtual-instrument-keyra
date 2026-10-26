// Independent numerical contracts for the v2 unison port and observation map.
// No reference recording or held-out tuning measurement is read by this test.
#define main grand_cli_main
#include "../src/grand.cpp"
#undef main
#include <set>
#include <tuple>

using namespace grand;
namespace {
void zeroState(Piano &p){
  for(auto &s:p.strings){std::fill(s.m.q.begin(),s.m.q.end(),0);std::fill(s.m.p.begin(),s.m.p.end(),0);}
  for(auto &b:p.board){b.q=b.p=b.force=0;}
  for(auto &k:p.keys){k.hammerActive=false;k.hammerX=k.hammerV=0;}
}
void velocity(Piano &p,std::pair<int,int> which,double v){
  auto &m=p.strings[which.first].m;m.p[which.second]=v/m.omega[which.second];
}
double maximumStateDifference(const Piano &p,const std::vector<std::vector<double>> &saved){
  double difference=0;for(size_t si=0;si<p.strings.size();++si){auto &m=p.strings[si].m;
    for(size_t j=0;j<m.size();++j)difference=std::max(difference,std::abs(m.p[j]-saved[si][j])*m.omega[j]);}
  return difference;
}
}

int main(){
  try{
    Options options;options.sampleRate=192000;options.calibrated=true;
    Piano p(options);
    bool validTopology=true,finite=true;
    std::vector<std::vector<int>> membership;
    for(auto &st:p.strings)membership.emplace_back(st.m.size(),0);
    double minimumCoefficient=1,maximumNormalizedCoefficient=0;
    for(auto &u:p.unisonPorts){
      validTopology=validTopology&&!u.modes.empty()&&std::isfinite(u.coefficient)&&u.coefficient>=0&&u.coefficient*u.modes.size()<=1;
      minimumCoefficient=std::min(minimumCoefficient,u.coefficient);
      maximumNormalizedCoefficient=std::max(maximumNormalizedCoefficient,u.coefficient*u.modes.size());
      std::set<std::pair<int,int>> seen;
      int note=-1,partial=-1;
      for(auto [si,j]:u.modes){
        validTopology=validTopology&&si>=0&&si<(int)p.strings.size();
        if(si<0||si>=(int)p.strings.size())throw std::runtime_error("bad string index");
        auto &st=p.strings[si];auto &m=st.m;
        if(j<0||j>=(int)m.size())throw std::runtime_error("bad modal index");
        if(note<0){note=st.note;partial=m.partial[j];}
        validTopology=validTopology&&st.note==note&&m.partial[j]==partial&&!m.polarization[j]&&seen.insert({si,j}).second;
        ++membership[si][j];
      }
    }
    for(size_t si=0;si<p.strings.size();++si)for(size_t j=0;j<p.strings[si].m.size();++j)
      validTopology=validTopology&&(membership[si][j]==(p.strings[si].m.polarization[j]?0:1));

    // All modal states are exercised simultaneously. Because the mechanical
    // energy uses v=omega*p, differing unison frequencies do not invalidate the
    // mean-velocity projection's Euclidean kinetic-energy contraction.
    std::mt19937 rng(281105);std::normal_distribution<double> normal;
    double maxRandomRise=0,randomInitial=0,randomFinal=0;
    for(auto &s:p.strings)for(size_t j=0;j<s.m.size();++j){s.m.p[j]=normal(rng)*.001/s.m.omega[j];s.m.q[j]=normal(rng)*.001/s.m.omega[j];}
    for(auto &b:p.board){b.q=normal(rng)*.001/b.w;b.p=normal(rng)*.001/b.w;}
    randomInitial=p.energy();double previous=randomInitial;
    for(int i=0;i<128;++i){p.unisonStep();double now=p.energy();maxRandomRise=std::max(maxRandomRise,(now-previous)/randomInitial);previous=now;}
    randomFinal=previous;

    // Each of the 88 keys supplies a fundamental port. Common initial velocity
    // has the known kinetic-energy ratio (1-N*c)^2, independent of tuning.
    // Equal-and-opposite velocities live in the projector's nullspace.
    int commonCases=0,oppositeCases=0;
    double maxCommonRatioError=0,maxOppositeEnergyError=0,maxOppositeVelocityChange=0;
    for(auto &u:p.unisonPorts){
      auto [firstSi,firstJ]=u.modes.front();if(p.strings[firstSi].m.partial[firstJ]!=1)continue;
      zeroState(p);for(auto address:u.modes)velocity(p,address,.013);
      double before=p.energy();p.unisonStep();double after=p.energy();
      double expected=std::pow(1-u.coefficient*u.modes.size(),2);
      maxCommonRatioError=std::max(maxCommonRatioError,std::abs(after/before-expected));++commonCases;
      if(u.modes.size()<2)continue;
      zeroState(p);velocity(p,u.modes[0],.017);velocity(p,u.modes[1],-.017);
      std::vector<std::vector<double>> saved;for(auto &st:p.strings)saved.push_back(st.m.p);
      before=p.energy();p.unisonStep();after=p.energy();
      maxOppositeEnergyError=std::max(maxOppositeEnergyError,std::abs(after/before-1));
      maxOppositeVelocityChange=std::max(maxOppositeVelocityChange,maximumStateDifference(p,saved));++oppositeCases;
    }

    // Analytic reference independent of the 3x3 elimination: for ONE physical
    // board mode with three spatial ports, its total viscous load is sum Rg*dg².
    // Thus force->acceleration is a single damped second-order response.
    const auto originalBoard=p.board;BoardMode test=originalBoard.front();
    test.port={.23,-.41,.17};test.mic={.73,-.29};test.w=2*pi*313.7;test.sigma=7.3;
    p.board={test};Vec3 R{};for(auto &st:p.strings)R[st.group]+=st.resistance*p.opt.bridge;
    double viscous=2*test.sigma;for(int g=0;g<3;++g)viscous+=R[g]*test.port[g]*test.port[g];
    double maxTransferRelativeError=0,maxPhaseProjectionError=0;
    int analyticCases=0;
    using C=std::complex<double>;
    for(double hz:{28.0,75.0,261.6,313.7,1050.0,6000.0,18000.0})for(int g=0;g<3;++g){
      double w=2*pi*hz;auto result=p.radiationTransfer(w,g);
      for(int ch=0;ch<2;++ch){
        C expected=(-w*w*test.mic[ch]*test.port[g])/C(test.w*test.w-w*w,w*viscous);
        maxTransferRelativeError=std::max(maxTransferRelativeError,std::abs(result[ch]-expected)/std::max(1e-30,std::abs(expected)));
        // A displacement cos(theta) has p=-sin(theta). Compare direct complex
        // response to the q,p observation representation, including velocity's
        // +i*w factor and a signed modal bridge participation.
        C coefficient=C(0,w)*.85*(-.31)*result[ch];
        for(double theta:{0.0,.37,pi*.5,pi,4.9}){
          double direct=std::real(coefficient*std::exp(C(0,theta)));
          double projected=coefficient.real()*std::cos(theta)-coefficient.imag()*std::sin(theta);
          maxPhaseProjectionError=std::max(maxPhaseProjectionError,std::abs(direct-projected)/std::max(1.0,std::abs(coefficient)));
        }
        ++analyticCases;
      }
    }
    p.board=originalBoard;

    // Check the complete 88-key coefficient field. This exercises the actual
    // generated projection when enabled, and verifies the intentional zero
    // projection while mechanics-only calibration is being evaluated.
    double maxStoredCoefficientError=0,maxCandidateCoefficient=0;
    size_t modesChecked=0;std::set<int> keysChecked;
    zeroState(p);
    for(auto &st:p.strings){Cal cal(st.note);auto &m=st.m;keysChecked.insert(st.note);
      for(size_t j=0;j<m.size();++j){
        auto H=p.radiationTransfer(m.omega[j],st.group);
        double mag=std::sqrt((std::norm(H[0])+std::norm(H[1]))*.5);
        auto radiationField=m.polarization[j]?&piano_calibration::Anchor::radiationAfterDb:&piano_calibration::Anchor::radiationDb;
        double target=std::pow(10.0,cal.mode(m.partial[j],radiationField)/20);
        double ratio=std::clamp(target/std::max(mag,1e-8),.025,40.0);
        if(m.partial[j]>64)ratio=1+(ratio-1)*std::exp(-(m.partial[j]-64)/24.0);
        finite=finite&&std::isfinite(mag)&&std::isfinite(target)&&std::isfinite(ratio)&&std::isfinite(m.radiationMagnitude[j]);
        for(int ch=0;ch<2;++ch){
          C coefficient=C(0,m.omega[j])*st.resistance*p.opt.bridge*m.b[j]*H[ch]*(ratio-1);
          const double actualQ=ch?m.radQR[j]:m.radQL[j],actualP=ch?m.radPR[j]:m.radPL[j];
          finite=finite&&std::isfinite(coefficient.real())&&std::isfinite(coefficient.imag())&&std::isfinite(actualQ)&&std::isfinite(actualP);
          maxCandidateCoefficient=std::max(maxCandidateCoefficient,std::abs(coefficient));
          C expected=piano_calibration::radiationEnabled?coefficient:C(0,0);
          maxStoredCoefficientError=std::max(maxStoredCoefficientError,std::abs(C(actualQ,actualP)-expected)/std::max(1.0,std::abs(expected)));
        }
        ++modesChecked;
      }
    }
    // Rebuilding an observation map must leave every mechanical state unchanged.
    for(auto &st:p.strings)for(size_t j=0;j<st.m.size();++j){st.m.q[j]=normal(rng)*1e-5/st.m.omega[j];st.m.p[j]=normal(rng)*1e-5/st.m.omega[j];}
    double observationBefore=p.energy();p.buildRadiation();double observationAfter=p.energy();
    double observationEnergyError=std::abs(observationAfter/observationBefore-1);

    bool passed=validTopology&&finite&&commonCases==88&&oppositeCases==77&&keysChecked.size()==88&&
      maxRandomRise<1e-12&&randomFinal<=randomInitial&&maxCommonRatioError<1e-12&&
      maxOppositeEnergyError<1e-12&&maxOppositeVelocityChange<1e-12&&
      maxTransferRelativeError<1e-10&&maxPhaseProjectionError<1e-12&&maxStoredCoefficientError<1e-12&&observationEnergyError==0;
    std::cout<<std::setprecision(12)<<"{\"passed\":"<<(passed?"true":"false")
      <<",\"radiation_enabled\":"<<(piano_calibration::radiationEnabled?"true":"false")
      <<",\"unison_ports\":"<<p.unisonPorts.size()<<",\"valid_port_topology\":"<<(validTopology?"true":"false")
      <<",\"minimum_port_coefficient\":"<<minimumCoefficient<<",\"maximum_N_times_coefficient\":"<<maximumNormalizedCoefficient
      <<",\"random_state_max_relative_energy_increase\":"<<maxRandomRise<<",\"random_state_energy_ratio_after128_steps\":"<<randomFinal/randomInitial
      <<",\"common_velocity_cases\":"<<commonCases<<",\"maximum_common_energy_ratio_error\":"<<maxCommonRatioError
      <<",\"opposite_velocity_cases\":"<<oppositeCases<<",\"maximum_opposite_relative_energy_error\":"<<maxOppositeEnergyError
      <<",\"maximum_opposite_velocity_change\":"<<maxOppositeVelocityChange
      <<",\"analytic_single_board_mode_transfer_cases\":"<<analyticCases<<",\"maximum_transfer_relative_error\":"<<maxTransferRelativeError
      <<",\"maximum_qp_phase_projection_error\":"<<maxPhaseProjectionError
      <<",\"keys_checked\":"<<keysChecked.size()<<",\"modes_checked\":"<<modesChecked
      <<",\"all_projection_coefficients_finite\":"<<(finite?"true":"false")
      <<",\"maximum_candidate_projection_coefficient\":"<<maxCandidateCoefficient
      <<",\"maximum_stored_projection_coefficient_error\":"<<maxStoredCoefficientError
      <<",\"observation_rebuild_relative_mechanical_energy_change\":"<<observationEnergyError
      <<",\"scope\":\"Numerical mechanics and observation math only; no recording or held-out tuning comparison. Enabled-projection runtime path is covered only when radiation_enabled is true.\"}\n";
    return passed?0:1;
  }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 2;}
}
