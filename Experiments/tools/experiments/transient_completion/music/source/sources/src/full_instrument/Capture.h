#pragma once
#include "Trace.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
namespace causal_capture {
inline size_t count=0;inline int note=48;
inline std::vector<std::array<float,2>> candidate,expectedBaseline;
// raw primary LR, raw full pitch-memory LR, raw rho1 control LR.
inline std::vector<std::array<double,6>> pressure;
// All actual primary contact88 and Schur3 forces; companion uses contact88 only.
inline std::vector<std::array<double,91>> forces;
inline std::vector<std::array<unsigned char,88>> branches;
inline std::vector<std::array<uint64_t,3>> stateProof,forceProof;
inline uint64_t mismatch=0,candidateFaults=0;
inline std::string companionReport;
inline std::vector<double> preparedRhos;
inline void reset() noexcept {mismatch=candidateFaults=0;stateProof.clear();companionReport.clear();preparedRhos.clear();}
inline void begin(size_t n,int midi){count=n;note=midi;candidate.resize(n);expectedBaseline.resize(n);pressure.resize(n);forces.resize(n);branches.resize(n);forceProof.resize(n);stateProof.reserve(n/256+2);reset();}
inline void bytes(uint64_t& h,const void* p,size_t size) noexcept {const auto* data=static_cast<const unsigned char*>(p);for(size_t i=0;i<size;++i){h^=data[i];h*=1099511628211ull;}}
template<class T> inline void scalar(uint64_t& h,const T& x) noexcept {bytes(h,&x,sizeof(x));}
inline uint64_t forceHash() noexcept {uint64_t h=14695981039346656037ull;bytes(h,causal_trace::force.data(),sizeof(causal_trace::force));bytes(h,causal_trace::bridge.data(),sizeof(causal_trace::bridge));return h;}
inline uint64_t stateHash(const grand::Piano& p) noexcept {
 uint64_t h=14695981039346656037ull;
 for(const auto& st:p.strings){for(const auto* a:{&st.m.q,&st.m.p,&st.m.damp})bytes(h,a->data(),a->size()*sizeof(float));scalar(h,st.velocity);scalar(h,st.force);}
 for(const auto& z:p.board){scalar(h,z.q);scalar(h,z.p);scalar(h,z.force);}
 for(const auto& k:p.keys){scalar(h,k.hammerX);scalar(h,k.hammerV);scalar(h,k.age);scalar(h,k.K);scalar(h,k.down);scalar(h,k.hammerActive);scalar(h,k.everStruck);scalar(h,k.damperPosition);scalar(h,k.cachedContact);scalar(h,k.cachedLoss);}
 scalar(h,p.pedal);scalar(h,p.pedalTarget);scalar(h,p.maxForce);scalar(h,p.contactTime);scalar(h,p.maxContactResidual);scalar(h,p.forceSolves);scalar(h,p.faultFlags);return h;
}

template<class T> bool write(const char* folder,const char* name,const std::vector<T>& data){
 const std::string path=std::string(folder)+"/"+name;FILE* f=std::fopen(path.c_str(),"wb");if(!f)return false;
 const bool ok=std::fwrite(data.data(),sizeof(T),data.size(),f)==data.size();return std::fclose(f)==0&&ok;
}
inline bool writeOutputs(const char* folder){
 std::ofstream meta(std::string(folder)+"/companion.json");meta<<companionReport<<'\n';meta.close();
 return bool(meta)&&write(folder,"candidate.f32le",candidate)&&write(folder,"filter-baseline.f32le",expectedBaseline)&&
 write(folder,"pressure.f64le",pressure)&&write(folder,"forces-and-bridge.f64le",forces)&&write(folder,"active-branches.u8",branches)&&
 write(folder,"prepared-rhos.f64le",preparedRhos)&&write(folder,"state-proof.u64le",stateProof)&&write(folder,"force-proof.u64le",forceProof);
}
}
