#pragma once
#include <array>
#include <cstdint>

namespace keyra::physics::materials {
// Source IDs resolve in References/Materials/sources.json. These are bulk
// literature inputs, not an identification of a complete piano or a contact law.
struct OrthotropicWood {
  const char* name;
  double densityKgM3;
  double longitudinalPa;
  double radialPa;
  double shearLRPa;
  double poissonLR;
  const char* sourceId;
};
enum class SoundboardWood : uint8_t { SitkaSpruce=0, NorwaySpruce=1 };
inline constexpr std::array<OrthotropicWood,2> soundboardWoods {{
  {"Sitka spruce",392.,11.5e9,.47e9,.5e9,.3,"BE2013_T1"},
  {"Norway spruce",440.,15.8e9,.85e9,.84e9,.3,"BE2013_T1"}
}};
inline constexpr OrthotropicWood mapleBridge {
  "Maple bridge (literature)",660.,10.e9,2.2e9,2.e9,.3,"BE2013_T1"
};
inline constexpr const OrthotropicWood& soundboard(SoundboardWood id) noexcept {
  const auto index=static_cast<unsigned>(id);
  return soundboardWoods[index<soundboardWoods.size()?index:0];
}
inline constexpr bool validWood(const OrthotropicWood& wood) noexcept {
  return wood.densityKgM3>0 && wood.densityKgM3<3000 &&
         wood.longitudinalPa>0 && wood.longitudinalPa<1.e12 &&
         wood.radialPa>0 && wood.radialPa<1.e12 &&
         wood.shearLRPa>0 && wood.shearLRPa<1.e12 &&
         wood.poissonLR>=0 && wood.poissonLR<1 &&
         wood.poissonLR*wood.poissonLR*wood.radialPa<wood.longitudinalPa;
}
struct PlateStiffness {
  double d11=0,d22=0,d12=0,d66=0; // N m; local material axes L,R
  double massPerArea=0;          // kg/m^2
  bool valid=false;
};
// Thin orthotropic plane-stress plate, not a complete crowned/ribbed board.
// Cross reciprocity is enforced: nu_RL=nu_LR E_R/E_L. Geometry is supplied
// independently; source data never implies a piano's thickness or dimensions.
inline constexpr PlateStiffness plateStiffness(const OrthotropicWood& wood,
                                               double thicknessM) noexcept {
  if(!validWood(wood)||!(thicknessM>0&&thicknessM<.1))return {};
  const double nuRL=wood.poissonLR*wood.radialPa/wood.longitudinalPa;
  const double scale=thicknessM*thicknessM*thicknessM/12.;
  const double denominator=1.-wood.poissonLR*nuRL;
  return {wood.longitudinalPa*scale/denominator,
          wood.radialPa*scale/denominator,
          wood.poissonLR*wood.radialPa*scale/denominator,
          wood.shearLRPa*scale,wood.densityKgM3*thicknessM,true};
}

enum class SolidEvidence : uint8_t { PublishedModel, ManufacturerTypical, DerivedHandbook };
struct BulkSolid {
  const char* name;
  double densityKgM3;
  double youngPa;
  double poisson;
  const char* sourceId;
  SolidEvidence evidence;
};
// AST44_2023_T1 is a published piano-string model's input, not a wire specimen
// measured for Keyra. Wound bass strings need separate core/wrap geometry and
// slip/contact behavior; do not use copper's modulus as the bass string modulus.
inline constexpr BulkSolid musicWire {
  "High-carbon music-wire steel",7850.,200.e9,.3,"AST44_2023_T1",SolidEvidence::PublishedModel
};
inline constexpr BulkSolid copperWinding {
  "C11000 copper winding proxy",8910.,117.210873984e9,.328125,"CDA_C11000",SolidEvidence::ManufacturerTypical
};
inline constexpr BulkSolid acrylicKeyTop {
  "Acrylic PMMA keytop proxy",1190.,3.3e9,.37,"ROHM_PMMA_GS",SolidEvidence::ManufacturerTypical
};
inline constexpr bool validSolid(const BulkSolid& solid) noexcept {
  return solid.densityKgM3>0&&solid.densityKgM3<30000&&
         solid.youngPa>0&&solid.youngPa<2.e12&&solid.poisson> -1&&solid.poisson<.5;
}

// USDA specific gravity is oven-dry mass divided by specimen volume at the
// specified moisture content. rho_MC = SG_MC * rho_water * (1+MC), not SG*1000.
struct KeyWood {
  const char* name;
  double specificGravityAt12Percent;
  double moistureMassFraction;
  double bendingModulusPa;
  const char* sourceId;
  constexpr double densityKgM3() const noexcept {
    return specificGravityAt12Percent*1000.*(1.+moistureMassFraction);
  }
};
enum class KeyWoodChoice : uint8_t { SitkaSpruce=0, AmericanBasswood=1 };
inline constexpr std::array<KeyWood,2> keyWoods {{
  {"Sitka spruce key stick",.40,.12,10.8e9,"USDA2010_T5_3"},
  {"American basswood key stick",.37,.12,10.1e9,"USDA2010_T5_3"}
}};
inline constexpr const KeyWood& keyWood(KeyWoodChoice id) noexcept {
  const auto index=static_cast<unsigned>(id);
  return keyWoods[index<keyWoods.size()?index:0];
}

struct CompositionOnly {
  const char* name;
  const char* sourceId;
  const char* missingProperties;
};
// Do not convert a fiber's tensile modulus into a packed felt force law.
// Felt density, geometry, compression exponent, hysteresis and voicing must be
// measured together. Missing values are intentionally not numeric defaults.
inline constexpr CompositionOnly hammerFelt {
  "Wool hammer felt","YAMAHA_ACTION",
  "Compressed felt density, contact law, relaxation/hysteresis and local voicing"
};
inline constexpr CompositionOnly keybedFelt {
  "Felt bushing; keybed pad unidentified","YAMAHA_ACTION",
  "Keybed composition, fiber blend, pad geometry, compression/contact law and friction"
};
inline constexpr CompositionOnly mapleRim {
  "Laminated maple rim","YAMAHA_WOODS",
  "Laminate layup, glue, thickness, boundary mobility and modal damping"
};
inline constexpr CompositionOnly beechRim {
  "Laminated beech rim","YAMAHA_WOODS",
  "Species/specimen constants, laminate layup, glue, boundary mobility and damping"
};
inline constexpr std::array<CompositionOnly,2> rimMaterials {{mapleRim,beechRim}};
inline constexpr CompositionOnly lidConstruction {
  "Lid construction awaiting measurement","UNIDENTIFIED_LID",
  "Species/layup/geometry and measured reflection/mobility; no fictitious solid-wood modulus"
};

enum class StringConstruction : uint8_t { PlainSteel=0, CopperWoundSteel=1 };
struct StringSection {
  double linearDensityKgM=0;
  double coreBendingRigidityNm2=0;
  bool valid=false;
};
// A wound string is a construction, not a homogeneous copper string. This
// section model accounts for wrap mass and steel-core bending stiffness only.
// Packing fraction, helix/slip losses and dimensions require independent data.
inline constexpr StringSection stringSection(StringConstruction construction,
                                              double coreDiameterM,
                                              double outerDiameterM,
                                              double wrapPackingFraction=1.) noexcept {
  if(static_cast<unsigned>(construction)>1||!(coreDiameterM>0&&coreDiameterM<.02)||
     !(outerDiameterM>=coreDiameterM&&outerDiameterM<.03)||
     !(wrapPackingFraction>=0&&wrapPackingFraction<=1))return {};
  constexpr double pi=3.14159265358979323846;
  const double d2=coreDiameterM*coreDiameterM;
  const double coreArea=pi*d2/4.;
  const double wrapArea=construction==StringConstruction::CopperWoundSteel?
    pi*(outerDiameterM*outerDiameterM-d2)*wrapPackingFraction/4.:0.;
  return {musicWire.densityKgM3*coreArea+copperWinding.densityKgM3*wrapArea,
          musicWire.youngPa*pi*d2*d2/64.,true};
}
inline constexpr CompositionOnly playerBoundary {
  "Clothed player acoustic boundary","UNIDENTIFIED_PLAYER",
  "Position-dependent complex acoustic impedance/absorption and clothing geometry"
};

inline constexpr double dryAirGasConstant=287.05; // J/(kg K), ideal dry-air approximation
inline constexpr double dryAirGamma=1.4;
inline constexpr const char* dryAirSourceId="NPL_DRY_AIR";
// Temperature/humidity corrections are not hidden in species damping numbers.
// The NPL dry-air approximation does not validate humid-air attenuation.

static_assert(validWood(soundboardWoods[0])&&validWood(soundboardWoods[1])&&validWood(mapleBridge),
              "Material stiffness must define a positive elastic energy");
static_assert(validSolid(musicWire)&&validSolid(copperWinding)&&validSolid(acrylicKeyTop),
              "Known solid material entries require physical units and bounds");
static_assert(plateStiffness(soundboardWoods[0],.008).valid,
              "Soundboard plate inputs must be finite and positive");
} // namespace keyra::physics::materials
