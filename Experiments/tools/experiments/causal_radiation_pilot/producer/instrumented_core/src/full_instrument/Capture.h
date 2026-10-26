
#pragma once
#include "Trace.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
namespace causal_capture {
inline size_t count=0;inline int note=48;
inline std::vector<std::array<float,2>> candidate;
inline std::array<std::vector<std::array<float,2>>,3> stems;
inline std::vector<std::array<double,3>> driver;
// rawold2,rawboard2,newcorrection2,energy,freeLoss,loadLoss,work,balance,forceNote,bridge3.
inline std::vector<std::array<double,15>> trace;
inline std::vector<std::array<uint64_t,3>> stateProof,forceProof;
inline uint64_t mismatch=0,candidateFaults=0;
inline void begin(size_t n,int midi){count=n;note=midi;candidate.resize(n);driver.resize(n);trace.resize(n);forceProof.resize(n);stateProof.clear();stateProof.reserve(n/256+2);for(auto& stem:stems)stem.resize(n);mismatch=candidateFaults=0;}
inline void reset() noexcept {mismatch=candidateFaults=0;stateProof.clear();}
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
template<class T> bool write(const char* folder,const char* name,const T& data){char path[4096];const int n=std::snprintf(path,sizeof(path),"%s/%s",folder,name);if(n<0||size_t(n)>=sizeof(path))return false;FILE* f=std::fopen(path,"wb");if(!f)return false;const bool ok=std::fwrite(data.data(),sizeof(data[0]),data.size(),f)==data.size();return std::fclose(f)==0&&ok;}
}
