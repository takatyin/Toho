#include "environment.hpp"
#include <stdexcept>
namespace toho {
Environment::Environment(int max_frames, std::uint32_t seed)
    : max_frames_(max_frames), seed_(seed) {
  if (max_frames <= 0) throw std::invalid_argument("max_frames must be positive");
  reset(seed);
}
State Environment::reset(std::uint32_t seed) {
  seed_ = seed;
  // v0 uses deterministic bullet patterns. Seed is reserved for future patterns.
  state_ = new_game();
  done_ = false;
  return state_;
}
Transition Environment::step(Action action) {
  if (done_) throw std::logic_error("Call reset() after episode end");
  Input input;
  switch (action) {
    case Action::stay: break;
    case Action::up: input.dy = -1; break;
    case Action::down: input.dy = 1; break;
    case Action::left: input.dx = -1; break;
    case Action::right: input.dx = 1; break;
    default: throw std::invalid_argument("Invalid action");
  }
  input.shoot = true;
  const int previous_hp = state_.player.hp;
  const auto status = toho::step(state_, input);
  const bool terminated = status != Status::playing;
  const bool truncated = !terminated && state_.frame >= max_frames_;
  done_ = terminated || truncated;
  // A sparse, documented baseline: no survival reward to avoid stalling incentives.
  float reward = static_cast<float>(state_.player.hp - previous_hp);
  if (status == Status::won) reward += 10.0f;
  if (status == Status::lost) reward -= 10.0f;
  return {state_, reward, terminated, truncated};
}
} // namespace toho
