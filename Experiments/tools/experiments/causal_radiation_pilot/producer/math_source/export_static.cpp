#include "PreparedModel.h"
#include <array>
#include <cstdio>
#include <string>
int main(int argc,char**argv){if(argc!=2)return 2;const std::string dir=argv[1];grand::Options o;o.sampleRate=48000;grand::Piano model(o);std::array<double,3> R{};std::array<unsigned,3> count{};
 for(const auto&st:model.strings){R[st.group]+=st.resistance*model.opt.bridge;++count[st.group];}
 FILE*f=std::fopen((dir+"/board.f64le").c_str(),"wb");if(!f)return 3;
 for(size_t i=0;i<model.board.size();++i){const auto&z=model.board[i];const double row[11]={double(i),z.w,z.sigma,z.c,z.s,z.damp,z.port[0],z.port[1],z.port[2],z.mic[0],z.mic[1]};if(std::fwrite(row,sizeof(double),11,f)!=11)return 4;}std::fclose(f);
 f=std::fopen((dir+"/modes.f64le").c_str(),"wb");if(!f)return 5;
 for(size_t si=0;si<model.strings.size();++si){const auto&st=model.strings[si];const auto&m=st.m;grand::Cal cal(st.note);const double r=st.resistance*model.opt.bridge;
  for(size_t j=0;j<m.size();++j){const auto H=model.radiationTransfer(m.omega[j],st.group);const double mag=std::sqrt((std::norm(H[0])+std::norm(H[1]))*.5);
   const double target=std::pow(10.,cal.mode(m.partial[j],m.polarization[j]?&piano_calibration::Anchor::radiationAfterDb:&piano_calibration::Anchor::radiationDb)/20.);
   double ratio=std::clamp(target/std::max(mag,1.e-8),.025,40.);if(m.partial[j]>64)ratio=1+(ratio-1)*std::exp(-(m.partial[j]-64)/24.);
   const double drive=r*double(m.b[j])*double(m.omega[j])*(ratio-1);const auto c0=std::complex<double>(0,drive)*H[0],c1=std::complex<double>(0,drive)*H[1];
   const double row[23]={double(si),double(st.note),double(st.unison),double(st.group),double(m.partial[j]),double(m.polarization[j]),double(m.omega[j]),double(m.b[j]),r,ratio,drive,H[0].real(),H[0].imag(),H[1].real(),H[1].imag(),double(m.radQL[j]),double(m.radPL[j]),double(m.radQR[j]),double(m.radPR[j]),c0.real(),c0.imag(),c1.real(),c1.imag()};
   if(std::fwrite(row,sizeof(double),23,f)!=23)return 6;
  }}std::fclose(f);
 std::printf("{\"rate\":48000,\"dt\":%.17g,\"R\":[%.17g,%.17g,%.17g],\"string_group_counts\":[%u,%u,%u],\"strings\":%zu,\"modes\":%zu,\"board_modes\":%zu}\n",model.dt,R[0],R[1],R[2],count[0],count[1],count[2],model.strings.size(),model.modeCount(),model.board.size());return 0;}
