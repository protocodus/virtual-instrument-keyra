#pragma once
#include <cstddef>

namespace keyra {
struct AnchorBracket { std::size_t lower,upper; };
// Setup-only lookup into a strictly increasing, immutable calibration table.
// The endpoint pair is retained for bounded tuning/dispersion extrapolation;
// callers clamp the interpolation fraction for quantities that do not extrapolate.
template<class Anchor>
constexpr AnchorBracket anchorBracket(int note,const Anchor* anchors,std::size_t count) noexcept {
  if(count<2)return {0,0};
  std::size_t lower=0;
  while(lower+2<count&&note>=anchors[lower+1].note)++lower;
  return {lower,lower+1};
}
} // namespace keyra
