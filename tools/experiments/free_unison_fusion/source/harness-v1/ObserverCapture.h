#pragma once
#include <array>
#include <cstddef>
namespace keyra_fusion_capture {
constexpr std::size_t capacity=65536;
inline std::array<double,2*capacity> pressure{};
inline std::size_t cursor=0;
inline bool overflow=false;
inline void capture(const std::array<double,2>& x) noexcept {
  if(cursor>=capacity){overflow=true;return;}
  pressure[2*cursor]=x[0];pressure[2*cursor+1]=x[1];++cursor;
}
inline void reset() noexcept {cursor=0;overflow=false;}
}
