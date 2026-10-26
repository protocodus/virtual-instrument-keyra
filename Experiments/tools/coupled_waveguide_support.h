#pragma once
// Offline research setup only. Runtime coupling lives in CoupledWaveguide.h.
#define main keyra_coupled_waveguide_original_main
#include "../src/full_reference/grand.cpp"
#undef main
#include "keyra/physics/CoupledWaveguide.h"
#include <fstream>
#include <stdexcept>
#include <string>

namespace keyra::waveguide_probe {
inline physics::WaveguideString::Config readString(const std::string& path) {
  using String=physics::WaveguideString;
  std::ifstream input(path);std::string name;double f1=0,b=0,z=0,position=0;
  String::Config config;
  if(!(input>>name>>f1>>b>>z>>position)||!std::isfinite(f1)||f1<=0||
     !std::isfinite(b)||b<0||!std::isfinite(position)||position<=0||position>=1)
    throw std::runtime_error("Invalid waveguide configuration header: "+path);
  config.impedance=z;
  const auto read=[&](String::PathConfig& p) {
    if(!(input>>p.delaySamples>>p.lossGain>>p.lossMix>>p.allpassCount)||p.allpassCount>String::allpassCapacity)
      throw std::runtime_error("Invalid waveguide path: "+path);
    for(unsigned i=0;i<p.allpassCount;++i)if(!(input>>p.allpass[i]))
      throw std::runtime_error("Incomplete waveguide path: "+path);
  };
  read(config.left);read(config.toBridge);config.fromBridge=config.toBridge;
  String validation;if(!validation.prepare(config))throw std::runtime_error("Invalid waveguide coefficients: "+path);
  return config;
}

inline physics::CoupledWaveguide::Config pianoConfig(int note,const std::string& path,bool losses=true,bool dcShelf=true) {
  if(note!=36&&note!=60)throw std::runtime_error("Bounded coupled prototype permits only C2 and C4");
  grand::Options options;options.sampleRate=48000;grand::Piano reference(options);
  const auto& key=reference.keys[note-21];
  physics::CoupledWaveguide::Config config;config.note=note;
  config.stringCount=static_cast<unsigned>(key.strings.size());config.bridgeGroup=note<45?0:1;
  config.hammerMass=key.mass;config.hammerStiffness=key.K;config.hammerPower=key.power;
  config.hammerLoss=losses?reference.opt.hammerLoss:0;config.velocityExponent=key.velocityExponent;
  config.humanization=0;
  auto string=readString(path);
  const auto loss=[&](physics::WaveguideString::PathConfig& p) {
    if(!losses){p.lossGain=1;p.lossMix=0;}
    p.dcPreservingLoss=dcShelf;
    p.dcLossPole=std::exp(-2*grand::pi*2/physics::WaveguideString::sampleRate);
  };
  loss(string.left);loss(string.toBridge);string.fromBridge=string.toBridge;
  // Identical choir lines isolate the coupling law. Small real unison detuning
  // and the original frequency-selective common-loss ports are not reproduced.
  for(unsigned i=0;i<config.stringCount;++i)config.strings[i]=string;
  config.boardCount=static_cast<unsigned>(reference.board.size());
  if(config.boardCount>physics::CoupledWaveguide::boardCapacity)throw std::runtime_error("Board capacity exceeded");
  for(unsigned i=0;i<config.boardCount;++i) {
    const auto& source=reference.board[i];auto& target=config.board[i];
    target.frequencyHz=source.w/(2*grand::pi);target.sigma=losses?source.sigma:0;
    target.port=source.port;target.microphone=source.mic;
  }
  return config;
}
} // namespace keyra::waveguide_probe
