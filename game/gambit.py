from typing import List, Tuple
from dataclasses import dataclass, field
import random

import numpy as np

from .status import Side, statuses
from .unit import Unit
from .team import Team
from .command import Command, AttackCommand
from .estimator import Estimator


class Gambit:
    def reset(self, teams: List[Team]):
        pass

    def select_command(self,
                       source: Unit,
                       units: List[Unit],
                       commands: List[Command]
                       ) -> Tuple[Command, List[Unit]]:
        pass


@dataclass
class NaiveGambit(Gambit):
    """
    ランダムに行動する
    """

    def select_command(self,
                       source: Unit,
                       units: List[Unit],
                       commands: List[Command]
                       ) -> Tuple[Command, List[Unit]]:
        command = commands[0]  # 一択のためコマンドは固定
        targets = command.targets(source, units)
        targets[:] = [random.choice(targets)]
        return command, targets


@dataclass
class CunningGambit(Gambit):
    """
    相手ステータス丸見えの状態で、最適な行動を行う
    """

    def estimate_priority(self, source: Unit, target: Unit):
        # 優先度の推定
        damage_taken = AttackCommand.estimate_damage(target.attack, source.defence)
        damage_given = AttackCommand.estimate_damage(source.attack, target.defence)
        return damage_taken / target.status.life * damage_given

    def select_command(self,
                       source: Unit,
                       units: List[Unit],
                       commands: List[Command]
                       ) -> Tuple[Command, List[Unit]]:
        command = commands[0]  # 一択のためコマンドは固定
        targets = command.targets(source, units)
        targets.sort(key=lambda t: self.estimate_priority(source, t))
        return command, targets[-1:]


@dataclass
class MLbasedGambit(Gambit):
    """
    機械学習にもとづいて最適な行動を推測
    """

    is_training: bool = False
    source_side: Side = Side.PLAYER
    target_side: Side = Side.MONSTER
    estimators: List[Estimator] = field(default_factory=list)
    n_class: int = field(init=False)

    def __post_init__(self):
        self.n_class = len(statuses[self.target_side])
        self.estimators = [
            Estimator('TakenDamage', self.n_class),
            Estimator('GivenDamage', self.n_class),
            Estimator('MaxHP', self.n_class),
        ]

        for reg in self.estimators:
            if not self.is_training:
                reg.load_model()
            else:
                reg.build_model()

    def id2vec(self, _id: int):
        return np.eye(self.n_class)[_id]

    def estimate_priority(self, source: Unit, target: Unit):
        # 被ダメージの推定
        Xv = np.array([[source.defence]], dtype=np.float32)
        Xc = np.array([self.id2vec(target.id)], dtype=np.float32)
        damage_taken = self.estimators[0].model.predict([Xv, Xc])

        # 与ダメージの推定
        Xv = np.array([[source.attack]], dtype=np.float32)
        Xc = np.array([self.id2vec(target.id)], dtype=np.float32)
        damage_given = self.estimators[1].model.predict([Xv, Xc])

        # 最大HPの推定
        Xv = np.array([[1]], dtype=np.float32)
        Xc = np.array([self.id2vec(target.id)], dtype=np.float32)
        life_max = self.estimators[2].model.predict([Xv, Xc])

        # 優先度の推定
        return damage_taken / life_max * damage_given

    def select_command(self,
                       source: Unit,
                       units: List[Unit],
                       commands: List[Command]
                       ) -> Tuple[Command, List[Unit]]:
        command = commands[0]  # 一択のためコマンドは固定
        targets = command.targets(source, units)
        targets.sort(key=lambda t: self.estimate_priority(source, t))
        return command, targets[-1:]
