#pragma once
#include <vector>
namespace toho {
constexpr float width = 200.0f;
constexpr float height = 300.0f;
enum class Status { playing, won, lost };
struct Entity { float x, y, radius; int hp; };
struct Bullet { float x, y, vy, radius = 2.0f; };
struct Input { int dx = 0; int dy = 0; bool shoot = false; };
struct State {
  Entity player{100.0f, 270.0f, 3.0f, 3};
  Entity enemy{100.0f, 40.0f, 12.0f, 10};
  std::vector<Bullet> player_bullets, enemy_bullets;
  Status status = Status::playing;
  int frame = 0, shot_cooldown = 0;
};
State new_game();
Status step(State& state, Input input = {});
bool collides(float ax, float ay, float ar, float bx, float by, float br);
} // namespace toho
