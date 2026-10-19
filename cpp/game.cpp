#include "game.hpp"
#include <algorithm>
namespace toho {
namespace {
constexpr float player_speed = 4.0f;
constexpr float player_shot_speed = 8.0f;
constexpr float enemy_shot_speed = 4.0f;
constexpr int player_shot_cooldown = 5;
constexpr int enemy_shot_interval = 30;
float clamp(float v, float lo, float hi) { return std::clamp(v, lo, hi); }
bool in_bounds(const Bullet& bullet) {
  return bullet.y >= -bullet.radius && bullet.y <= height + bullet.radius;
}
void move_bullets(std::vector<Bullet>& bullets) {
  for (auto& bullet : bullets) bullet.y += bullet.vy;
  bullets.erase(std::remove_if(bullets.begin(), bullets.end(),
                               [](const Bullet& bullet) { return !in_bounds(bullet); }),
                bullets.end());
}
void apply_hits(std::vector<Bullet>& bullets, Entity& target) {
  bullets.erase(std::remove_if(bullets.begin(), bullets.end(), [&](const Bullet& bullet) {
    if (!collides(bullet.x, bullet.y, bullet.radius, target.x, target.y, target.radius))
      return false;
    target.hp = std::max(0, target.hp - 1);
    return true;
  }), bullets.end());
}
} // namespace
State new_game() { return {}; }
bool collides(float ax, float ay, float ar, float bx, float by, float br) {
  const float dx = ax - bx, dy = ay - by, sum = ar + br;
  return dx * dx + dy * dy <= sum * sum;
}
Status step(State& state, Input input) {
  if (state.status != Status::playing) return state.status;
  auto& player = state.player;
  player.x = clamp(player.x + clamp(static_cast<float>(input.dx), -1.0f, 1.0f) * player_speed,
                   player.radius, width - player.radius);
  player.y = clamp(player.y + clamp(static_cast<float>(input.dy), -1.0f, 1.0f) * player_speed,
                   player.radius, height - player.radius);
  if (state.shot_cooldown > 0) --state.shot_cooldown;
  if (input.shoot && state.shot_cooldown == 0) {
    state.player_bullets.push_back({player.x, player.y - player.radius, -player_shot_speed});
    state.shot_cooldown = player_shot_cooldown;
  }
  if (state.frame % enemy_shot_interval == 0) {
    const auto& enemy = state.enemy;
    state.enemy_bullets.push_back({enemy.x, enemy.y + enemy.radius, enemy_shot_speed});
  }
  move_bullets(state.player_bullets);
  move_bullets(state.enemy_bullets);
  apply_hits(state.player_bullets, state.enemy);
  apply_hits(state.enemy_bullets, state.player);
  if (state.player.hp == 0) state.status = Status::lost;
  else if (state.enemy.hp == 0) state.status = Status::won;
  ++state.frame;
  return state.status;
}
} // namespace toho
