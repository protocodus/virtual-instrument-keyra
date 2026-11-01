#pragma once
#include <cmath>

namespace keyra {
inline constexpr float defaultMechanicsGain=.175f;
inline constexpr float legacyMechanicsGain=1.f;
inline constexpr float maximumMechanicsGain=2.f;
inline constexpr float defaultMechanicsPosition=.4f;

namespace mechanicsControlDetail {
inline double exponent() noexcept {
  return std::log(static_cast<double>(defaultMechanicsGain)/maximumMechanicsGain)
       / std::log(static_cast<double>(defaultMechanicsPosition));
}
}

// The owner chose the .175-amplitude listening candidate B and asked for it
// at 40% knob travel (2026-11-01). This power taper is a UI scale derived
// from those anchors, not an acoustic parameter. Native/saved Mechanics
// remains a linear amplitude gain from 0 to 2; render callbacks do not use
// this conversion. Float inputs match the native and host parameter domain,
// so both .4 and .4f select the exact .175f default without a rounding drift.
// Out-of-range inputs clamp to the endpoints; NaN maps to zero.
inline float mechanicsGainFromPosition(float position) noexcept {
  if(!(position>0))return 0;
  if(position>=1)return maximumMechanicsGain;
  if(position==defaultMechanicsPosition)return defaultMechanicsGain;
  return static_cast<float>(maximumMechanicsGain
    *std::pow(static_cast<double>(position),mechanicsControlDetail::exponent()));
}
inline float mechanicsPositionFromGain(float gain) noexcept {
  if(!(gain>0))return 0;
  if(gain>=maximumMechanicsGain)return 1;
  if(gain==defaultMechanicsGain)return defaultMechanicsPosition;
  return static_cast<float>(std::pow(static_cast<double>(gain)/maximumMechanicsGain,
    1/mechanicsControlDetail::exponent()));
}
}
