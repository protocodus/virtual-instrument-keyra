#pragma once
#include "keyra/physics/MechanismExciter.h"
#include <array>
#include <cstddef>
#include <vector>

namespace keyra::detail {
// Prepare-time board coefficients; per-frame fresh two-port velocities and
// sequential reciprocal impulses. One float board write intentionally differs
// from the legacy per-source writes. See FULL_MECHANISM_CACHE.md for the work,
// observer and rounding audits. No pointer aliases or render allocations.
struct MechanismBodyCache {
  struct Node {std::array<double,2> impulse{},dampingObserver{};};
  std::vector<Node> nodes;
  std::array<std::array<double,2>,2> gram{},forceObserver{};
  std::array<double,2> velocity{},impulse{};
  template<class Model> void prepare(const Model& model) {
    nodes.resize(model.board.size());gram={};forceObserver={};
    for(unsigned g=0;g<2;++g)for(unsigned h=0;h<2;++h)gram[g][h]=model.boardGram[g][h];
    for(std::size_t i=0;i<nodes.size();++i){const auto& z=model.board[i];auto& n=nodes[i];
      for(unsigned g=0;g<2;++g)n.impulse[g]=z.port[g]/z.w;
      for(unsigned ch=0;ch<2;++ch){n.dampingObserver[ch]=-2*z.sigma*z.w*z.mic[ch];
        for(unsigned g=0;g<2;++g)forceObserver[g][ch]+=z.port[g]*z.mic[ch]/model.dt;}
    }
    reset();
  }
  void reset() noexcept {velocity={};impulse={};}
  template<class Model> void begin(const Model& model) noexcept {
    velocity={};impulse={};
    for(const auto& z:model.board)for(unsigned g=0;g<2;++g)velocity[g]+=z.port[g]*z.w*z.p;
  }
  keyra::physics::MechanismBodyPort port(unsigned group) const noexcept {return {velocity[group],gram[group][group]};}
  void add(unsigned group,double value) noexcept {
    impulse[group]+=value;
    for(unsigned h=0;h<2;++h)velocity[h]+=gram[h][group]*value;
  }
  template<class Model> std::array<double,2> finish(Model& model) noexcept {
    std::array<double,2> out{};
    for(unsigned g=0;g<2;++g)for(unsigned ch=0;ch<2;++ch)out[ch]+=forceObserver[g][ch]*impulse[g];
    for(std::size_t i=0;i<nodes.size();++i){auto& z=model.board[i];const auto& n=nodes[i];
      const double old=z.p;
      z.p=old+n.impulse[0]*impulse[0]+n.impulse[1]*impulse[1];
      const double change=double(z.p)-old;
      for(unsigned ch=0;ch<2;++ch)out[ch]+=n.dampingObserver[ch]*change;
    }
    return out;
  }
};
} // namespace keyra::detail
