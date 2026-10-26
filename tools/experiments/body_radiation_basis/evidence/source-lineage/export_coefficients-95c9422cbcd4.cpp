#include "PreparedModel.h"
#include <cstdio>
#include <string>
int main(int argc,char**argv){if(argc!=2)return 2;grand::Options o;o.sampleRate=48000;grand::Piano p(o);const std::string dir=argv[1];FILE*f=std::fopen((dir+"/board-coefficients.f64le").c_str(),"wb");if(!f)return 3;
 for(size_t i=0;i<p.board.size();++i){const auto&z=p.board[i];const double row[11]={double(i),z.w,z.sigma,z.c,z.s,z.damp,z.port[0],z.port[1],z.port[2],z.mic[0],z.mic[1]};if(std::fwrite(row,sizeof(double),11,f)!=11)return 4;}std::fclose(f);
 f=std::fopen((dir+"/key-coefficients.f64le").c_str(),"wb");if(!f)return 5;
 for(int n:{29,48,56,72,75,77}){const auto&k=p.keys[n-21];const double row[8]={double(n),k.f0,k.B,k.mass,k.K,k.power,k.velocityExponent,k.contactCompliance};if(std::fwrite(row,sizeof(double),8,f)!=8)return 6;}std::fclose(f);return 0;}
