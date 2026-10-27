#pragma once
#include <array>
#include <cstdint>

namespace keyra {
// Stable host/state IDs. Append parameters rather than reordering these IDs.
enum class ParamId : uint32_t {
  Instrument=0, Material=1, Mic=2, Tone=3, Dynamics=4, Resonance=5,
  Noise=6, Distance=7, Width=8, Gain=9, Count=10
};
struct ParamInfo {
  ParamId id;
  const char* name;
  double min, max, defaultValue;
  bool stepped;
};
inline constexpr std::array<ParamInfo,10> kParameters {{
  {ParamId::Instrument,"Instrument",0,3,0,true},
  {ParamId::Material,"Material voicing",0,2,0,true},
  {ParamId::Mic,"Microphones",0,5,0,true},
  {ParamId::Tone,"Tone",0,1,.5,false},
  {ParamId::Dynamics,"Dynamics",0,1,.5,false},
  {ParamId::Resonance,"Resonance",0,1,.3,false},
  {ParamId::Noise,"Mechanical noise",0,1,.1,false},
  {ParamId::Distance,"Room / distance",0,1,.15,false},
  {ParamId::Width,"Stereo width",0,1,.7,false},
  {ParamId::Gain,"Output (dB)",-48,6,-6,false}
}};
inline constexpr std::array<const char*,4> kInstruments {{
  "Concert Grand","Studio Grand","Upright","Felt Upright"
}};
inline constexpr std::array<const char*,3> kMaterials {{"Spruce","Cedar","Maple"}};
inline constexpr std::array<const char*,6> kMicrophones {{
  "Close AB","XY","ORTF","Mid Side","Mono","Room AB"
}};
inline constexpr const ParamInfo& paramInfo(ParamId id) noexcept {
  auto i=static_cast<uint32_t>(id);
  return kParameters[i<kParameters.size()?i:0];
}
inline constexpr const char* const* parameterChoices(ParamId id) noexcept {
  return id==ParamId::Instrument?kInstruments.data():
         id==ParamId::Material?kMaterials.data():
         id==ParamId::Mic?kMicrophones.data():nullptr;
}
} // namespace keyra
