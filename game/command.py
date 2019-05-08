from enum import IntEnum
from typing import List
from dataclasses import dataclass
import random

from . import logger
from .status import Side
from .unit import Unit
from .log import TurnLog


class TargetScope(IntEnum):
    """
    対象範囲
    """
    UNIT = 0,
    GROUP = 1,
    TEAM = 2,
    ALL = 3,


@dataclass
class Command:
    @staticmethod
    @property
    def target_scope():
        pass

    def targets(self, source: Unit, units: List[Unit]) -> List[Unit]:
        pass

    def do(self, turn_id: int, order: int, source: Unit, targets: List[Unit],
           logs: List[TurnLog]):
        pass


@dataclass
class AttackCommand(Command):
    """
    たたかう コマンド
    """
    @staticmethod
    @property
    def target_scope() -> TargetScope:
        return TargetScope.UNIT

    @staticmethod
    def estimate_damage(attack: int, defence: int) -> int:
        # 平均ダメージの推定
        return max((attack - defence//2)//2, 0)

    def targets(self, source: Unit, units: List[Unit]) -> List[Unit]:
        return list(filter(lambda u: source.can_attack(u), units))

    def do(self, turn_id: int, order: int, source: Unit, targets: List[Unit],
           logs: List[TurnLog]):
        for target in targets:
            # ダメージを計算する
            base = max((source.attack - target.defence // 2) // 2, 0)
            damage_cumsum = target.life_max - target.life
            damage = random.randint(base * 7 // 8, base * 9 // 8)
            target.life = max(0, target.life - damage)

            logger.debug("%12s %10s -> %10s damage=%d %s" % (
                "Attack", str(source), str(target), damage, "" if target.life > 0 else "defeated"))

            source_observable = source.side == Side.PLAYER
            target_observable = target.side == Side.PLAYER

            logs.append(TurnLog(
                turn_id=turn_id,
                order=order,
                command=self,
                source_id=source.status.id,
                source_side=source.side,
                source_hp=source.life if source_observable else None,
                source_atk=source.attack if source_observable else None,
                source_def=source.defence if source_observable else None,
                source_spd=source.speed if source_observable else None,
                target_id=target.status.id,
                target_side=target.side,
                target_hp=target.life if target_observable else None,
                target_atk=target.attack if target_observable else None,
                target_def=target.defence if target_observable else None,
                target_spd=target.speed if target_observable else None,
                damage=damage,
                damage_cumsum=damage_cumsum+damage,
                defeated=target.life <= 0,
            ))
