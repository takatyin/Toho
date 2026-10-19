#pragma once
#include "game.hpp"
#include <cstdint>
namespace toho {
// A fixed five-action space. Shooting is automatic to keep control minimal.
enum class Action { stay, up, down, left, right };
struct Transition {
  State observation;
  float reward;
  bool terminated; // Victory or defeat.
  bool truncated;  // Time limit, not a terminal game outcome.
};
class Environment {
 public:
  explicit Environment(int max_frames = 2000, std::uint32_t seed = 0);
  State reset(std::uint32_t seed = 0);
  Transition step(Action action);
  const State& state() const { return state_; }
 private:
  State state_;
  int max_frames_;
  std::uint32_t seed_;
  bool done_ = false;
};
} // namespace toho
