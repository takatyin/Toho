"""2D弾幕シューティングの最小ゲームロジック (v0, 画面描画なし)。

設計上の決定:
- 座標系: 原点は画面左上、x は右向き、y は下向きが正。画面は WIDTH x HEIGHT。
- 時間刻み: 固定ステップ。step() 1回 = 1フレーム。速度は「1フレームあたりの移動量」。
- 操作入力: step(dx, dy, shoot)。dx, dy は -1/0/1 の方向、shoot は発射するかどうか。
- 当たり判定: 円同士の判定 (中心間距離 <= 半径の和)。
- 自機弾は上向き (-y)、敵弾は下向き (+y) に直進し、画面外に出たら消える。
- 敵は移動せず、一定間隔で真下に弾を1発撃つ。
- 勝敗確定後 (WON / LOST) は step() を呼んでも状態を一切変更しない。
- 同一フレームで両者のHPが尽きた場合は敗北を優先する。
"""

from dataclasses import dataclass, field
from enum import Enum

WIDTH = 200
HEIGHT = 300

PLAYER_HP = 3
PLAYER_SPEED = 4
PLAYER_RADIUS = 3
PLAYER_SHOT_SPEED = 8
PLAYER_SHOT_COOLDOWN = 5

ENEMY_HP = 10
ENEMY_RADIUS = 12
ENEMY_SHOT_SPEED = 4
ENEMY_SHOT_INTERVAL = 30

BULLET_RADIUS = 2
BULLET_DAMAGE = 1


class Status(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class Entity:
    x: float
    y: float
    radius: float
    hp: int


@dataclass
class Bullet:
    x: float
    y: float
    vy: float
    radius: float = BULLET_RADIUS


@dataclass
class GameState:
    player: Entity
    enemy: Entity
    player_bullets: list = field(default_factory=list)
    enemy_bullets: list = field(default_factory=list)
    status: Status = Status.PLAYING
    frame: int = 0
    shot_cooldown: int = 0


def new_game():
    """自機を画面下部中央、敵を画面上部中央に配置した初期状態を返す。"""
    return GameState(
        player=Entity(WIDTH / 2, HEIGHT - 30, PLAYER_RADIUS, PLAYER_HP),
        enemy=Entity(WIDTH / 2, 40, ENEMY_RADIUS, ENEMY_HP),
    )


def _clamp(value, low, high):
    return max(low, min(high, value))


def move_player(state, dx, dy):
    p = state.player
    p.x = _clamp(p.x + _clamp(dx, -1, 1) * PLAYER_SPEED, p.radius, WIDTH - p.radius)
    p.y = _clamp(p.y + _clamp(dy, -1, 1) * PLAYER_SPEED, p.radius, HEIGHT - p.radius)


def player_shoot(state):
    """クールダウン中でなければ自機の真上に弾を発射する。発射したら True。"""
    if state.shot_cooldown > 0:
        return False
    p = state.player
    state.player_bullets.append(Bullet(p.x, p.y - p.radius, -PLAYER_SHOT_SPEED))
    state.shot_cooldown = PLAYER_SHOT_COOLDOWN
    return True


def enemy_shoot(state):
    e = state.enemy
    state.enemy_bullets.append(Bullet(e.x, e.y + e.radius, ENEMY_SHOT_SPEED))


def _in_bounds(b):
    return -b.radius <= b.y <= HEIGHT + b.radius


def update_bullets(state):
    for b in state.player_bullets + state.enemy_bullets:
        b.y += b.vy
    state.player_bullets = [b for b in state.player_bullets if _in_bounds(b)]
    state.enemy_bullets = [b for b in state.enemy_bullets if _in_bounds(b)]


def collides(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    r = a.radius + b.radius
    return dx * dx + dy * dy <= r * r


def resolve_collisions(state):
    """命中した弾を消し、対象のHPを減らす。"""
    remaining = []
    for b in state.player_bullets:
        if collides(b, state.enemy):
            state.enemy.hp = max(0, state.enemy.hp - BULLET_DAMAGE)
        else:
            remaining.append(b)
    state.player_bullets = remaining

    remaining = []
    for b in state.enemy_bullets:
        if collides(b, state.player):
            state.player.hp = max(0, state.player.hp - BULLET_DAMAGE)
        else:
            remaining.append(b)
    state.enemy_bullets = remaining


def check_outcome(state):
    if state.player.hp <= 0:
        state.status = Status.LOST
    elif state.enemy.hp <= 0:
        state.status = Status.WON


def step(state, dx=0, dy=0, shoot=False):
    """1フレーム進める。勝敗確定後は何もしない。現在のステータスを返す。"""
    if state.status is not Status.PLAYING:
        return state.status

    move_player(state, dx, dy)
    if state.shot_cooldown > 0:
        state.shot_cooldown -= 1
    if shoot:
        player_shoot(state)
    if state.frame % ENEMY_SHOT_INTERVAL == 0:
        enemy_shoot(state)
    update_bullets(state)
    resolve_collisions(state)
    check_outcome(state)
    state.frame += 1
    return state.status
