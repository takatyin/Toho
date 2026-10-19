#include "environment.hpp"
#include <cassert>
#include <stdexcept>
using namespace toho;
int main() {
  Environment env(2000, 123);
  auto s = env.reset(123);
  auto t = env.step(Action::right);
  assert(t.observation.player.x == s.player.x + 4);
  assert(!t.terminated && !t.truncated);
  assert(t.reward == 0);
  assert(t.observation.player_bullets.size() == 1);
  // Fixed seed and actions must produce identical trajectories.
  Environment other(2000, 123);
  auto u = other.step(Action::right);
  assert(t.observation.frame == u.observation.frame);
  assert(t.observation.player.x == u.observation.player.x);
  assert(t.observation.enemy_bullets.size() == u.observation.enemy_bullets.size());
  // Truncation is distinct from losing.
  Environment short_env(1);
  auto last = short_env.step(Action::stay);
  assert(!last.terminated && last.truncated);
  bool rejected = false;
  try { short_env.step(Action::stay); }
  catch (const std::logic_error&) { rejected = true; }
  assert(rejected);
  short_env.reset();
  assert(!short_env.step(Action::stay).terminated);
  // The default policy (stay, automatically shoot) must eventually finish.
  Environment episode;
  Transition result{};
  for (int i = 0; i < 2000; ++i) {
    result = episode.step(Action::stay);
    if (result.terminated || result.truncated) break;
  }
  assert(result.terminated);
  assert(!result.truncated);
  assert(result.observation.status == Status::lost || result.observation.status == Status::won);
}
