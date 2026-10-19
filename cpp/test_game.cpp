#include "game.hpp"
#include <cassert>
#include <iostream>
using namespace toho;
int main() {
  {
    auto game = new_game();
    assert(game.status == Status::playing && game.player.hp == 3);
    step(game, {1, -1, true});
    assert(game.player.x == 104.0f && game.player.y == 266.0f);
    assert(game.player_bullets.size() == 1);
    assert(game.enemy_bullets.size() == 1);
  }
  {
    auto game = new_game();
    game.player.x = 108.0f;
    while (game.status == Status::playing && game.frame < 2000)
      step(game, {0, 0, true});
    assert(game.status == Status::won && game.enemy.hp == 0);
    const auto frame = game.frame;
    step(game, {1, 1, true});
    assert(game.frame == frame);
  }
  {
    auto game = new_game();
    while (game.status == Status::playing && game.frame < 2000) step(game);
    assert(game.status == Status::lost && game.player.hp == 0);
  }
  assert(collides(0, 0, 3, 0, 5, 2));
  assert(!collides(0, 0, 3, 0, 6, 2));
  std::cout << "All C++ gameplay tests passed\n";
}
