from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass, field
import random

from .status import Side, Status


@dataclass
class Unit:
    """
    ユニット
    """

    status: Status
    no: int = field(init=False, default=0)
    team: int = field(init=False, default=0)
    life: int = field(init=False, default=0)
    life_max: int = field(init=False, default=0)

    def __post_init__(self):
        self.reset()

    def __str__(self):
        return "%s:%d" % (self.status.name, self.team)

    def __eq__(self, other):
        return (other.team, other.no) == (self.team, self.no)

    @property
    def id(self) -> int:
        return self.status.id

    @property
    def side(self) -> Side:
        return self.status.side

    @property
    def attack(self) -> int:
        return self.status.attack

    @property
    def defence(self) -> int:
        return self.status.defence

    @property
    def speed(self) -> int:
        return self.status.speed

    def reset(self):
        if self.side == Side.MONSTER:
            self.life_max = int(random.uniform(0.85, 1.0) * self.status.life)
        else:
            self.life_max = self.status.life
        self.life = self.life_max

    @property
    def alive(self) -> bool:
        # 行動可能か判定
        return self.life > 0

    def is_alive(self) -> bool:
        # 行動可能か判定
        return self.life > 0

    def is_adversarial(self, target) -> bool:
        # 敵かどうか判定
        return self.team != target.team

    def can_attack(self, target) -> bool:
        # 攻撃対象か判定
        return target.alive and self.is_adversarial(target)

    def calc_action_priority(self) -> float:
        # 行動の優先順位を求める
        var = random.uniform(0.5, 1.0)
        return self.speed * var
