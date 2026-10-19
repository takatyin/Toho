import copy
import unittest

from toho import game
from toho.game import Bullet, Entity, Status


class InitTest(unittest.TestCase):
    def test_new_game_initial_state(self):
        s = game.new_game()
        self.assertEqual(s.status, Status.PLAYING)
        self.assertEqual(s.player.hp, game.PLAYER_HP)
        self.assertEqual(s.enemy.hp, game.ENEMY_HP)
        self.assertEqual(s.player_bullets, [])
        self.assertEqual(s.enemy_bullets, [])
        self.assertEqual(s.frame, 0)
        self.assertGreater(s.player.y, s.enemy.y)


class MoveTest(unittest.TestCase):
    def test_move_player(self):
        s = game.new_game()
        x, y = s.player.x, s.player.y
        game.move_player(s, 1, -1)
        self.assertEqual((s.player.x, s.player.y), (x + game.PLAYER_SPEED, y - game.PLAYER_SPEED))

    def test_move_is_clamped_to_screen(self):
        s = game.new_game()
        for _ in range(1000):
            game.move_player(s, -1, 1)
        self.assertEqual(s.player.x, s.player.radius)
        self.assertEqual(s.player.y, game.HEIGHT - s.player.radius)


class ShootTest(unittest.TestCase):
    def test_player_shoot_and_cooldown(self):
        s = game.new_game()
        self.assertTrue(game.player_shoot(s))
        self.assertEqual(len(s.player_bullets), 1)
        self.assertLess(s.player_bullets[0].vy, 0)
        self.assertFalse(game.player_shoot(s))
        self.assertEqual(len(s.player_bullets), 1)

    def test_enemy_shoots_on_interval(self):
        s = game.new_game()
        s.player.x = 10  # 敵弾の射線から外す
        game.step(s)
        self.assertEqual(len(s.enemy_bullets), 1)
        self.assertGreater(s.enemy_bullets[0].vy, 0)
        for _ in range(game.ENEMY_SHOT_INTERVAL - 1):
            game.step(s)
        self.assertEqual(len(s.enemy_bullets), 1)
        game.step(s)
        self.assertEqual(len(s.enemy_bullets), 2)


class BulletUpdateTest(unittest.TestCase):
    def test_bullets_move_by_velocity(self):
        s = game.new_game()
        s.player_bullets.append(Bullet(50, 100, -8))
        s.enemy_bullets.append(Bullet(50, 100, 4))
        game.update_bullets(s)
        self.assertEqual(s.player_bullets[0].y, 92)
        self.assertEqual(s.enemy_bullets[0].y, 104)

    def test_offscreen_bullets_removed(self):
        s = game.new_game()
        s.player_bullets.append(Bullet(50, 0, -8))
        s.enemy_bullets.append(Bullet(50, game.HEIGHT, 4))
        game.update_bullets(s)
        self.assertEqual(s.player_bullets, [])
        self.assertEqual(s.enemy_bullets, [])


class CollisionTest(unittest.TestCase):
    def test_collides(self):
        e = Entity(0, 0, 3, 1)
        self.assertTrue(game.collides(Bullet(0, 5, 0, radius=2), e))  # 接触
        self.assertFalse(game.collides(Bullet(0, 5.1, 0, radius=2), e))
        self.assertTrue(game.collides(Bullet(3, 3, 0, radius=2), e))

    def test_player_bullet_hits_enemy(self):
        s = game.new_game()
        s.player_bullets.append(Bullet(s.enemy.x, s.enemy.y, -8))
        game.resolve_collisions(s)
        self.assertEqual(s.enemy.hp, game.ENEMY_HP - game.BULLET_DAMAGE)
        self.assertEqual(s.player_bullets, [])

    def test_enemy_bullet_hits_player(self):
        s = game.new_game()
        s.enemy_bullets.append(Bullet(s.player.x, s.player.y, 4))
        game.resolve_collisions(s)
        self.assertEqual(s.player.hp, game.PLAYER_HP - game.BULLET_DAMAGE)
        self.assertEqual(s.enemy_bullets, [])

    def test_miss_does_not_change_hp(self):
        s = game.new_game()
        s.player_bullets.append(Bullet(s.enemy.x + 50, s.enemy.y, -8))
        s.enemy_bullets.append(Bullet(s.player.x + 50, s.player.y, 4))
        game.resolve_collisions(s)
        self.assertEqual(s.enemy.hp, game.ENEMY_HP)
        self.assertEqual(s.player.hp, game.PLAYER_HP)
        self.assertEqual(len(s.player_bullets), 1)
        self.assertEqual(len(s.enemy_bullets), 1)


class OutcomeTest(unittest.TestCase):
    def test_win_when_enemy_hp_depleted(self):
        s = game.new_game()
        s.enemy.hp = 1
        s.player_bullets.append(Bullet(s.enemy.x, s.enemy.y + 8, -8))
        self.assertEqual(game.step(s), Status.WON)

    def test_lose_when_player_hp_depleted(self):
        s = game.new_game()
        s.player.hp = 1
        s.enemy_bullets.append(Bullet(s.player.x, s.player.y - 4, 4))
        self.assertEqual(game.step(s), Status.LOST)

    def test_lose_takes_priority_on_simultaneous_ko(self):
        s = game.new_game()
        s.player.hp = 0
        s.enemy.hp = 0
        game.check_outcome(s)
        self.assertEqual(s.status, Status.LOST)

    def test_no_progress_after_game_over(self):
        for status in (Status.WON, Status.LOST):
            s = game.new_game()
            s.player_bullets.append(Bullet(100, 150, -8))
            s.enemy_bullets.append(Bullet(10, 150, 4))
            s.status = status
            before = copy.deepcopy(s)
            for _ in range(100):
                self.assertEqual(game.step(s, 1, 1, True), status)
            self.assertEqual(s, before)


class EndToEndTest(unittest.TestCase):
    """画面なしで開始から勝敗決定まで通しで実行する。"""

    MAX_FRAMES = 2000

    def test_e2e_win(self):
        s = game.new_game()
        # 敵弾の射線 (x=敵中心) から外れつつ、自機弾は敵に当たる位置へ移動して撃ち続ける
        game.step(s, dx=1)
        game.step(s, dx=1)
        self.assertEqual(s.player.x - s.enemy.x, 2 * game.PLAYER_SPEED)
        while s.status is Status.PLAYING and s.frame < self.MAX_FRAMES:
            game.step(s, shoot=True)
        self.assertEqual(s.status, Status.WON)
        self.assertEqual(s.enemy.hp, 0)
        self.assertEqual(s.player.hp, game.PLAYER_HP)
        frame = s.frame
        game.step(s, shoot=True)
        self.assertEqual(s.frame, frame)

    def test_e2e_lose(self):
        s = game.new_game()
        # 敵の真下で何もしないと敵弾を受け続けて敗北する
        hp_history = []
        while s.status is Status.PLAYING and s.frame < self.MAX_FRAMES:
            game.step(s)
            hp_history.append(s.player.hp)
        self.assertEqual(s.status, Status.LOST)
        self.assertEqual(s.player.hp, 0)
        self.assertEqual(s.enemy.hp, game.ENEMY_HP)
        self.assertEqual(sorted(set(hp_history), reverse=True), [3, 2, 1, 0])


if __name__ == "__main__":
    unittest.main()
