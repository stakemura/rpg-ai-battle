from enum import IntEnum
from typing import List, Tuple, Optional
from dataclasses import dataclass

from . import logger
from .unit import Unit
from .team import Team
from .gambit import Gambit
from .command import Command, AttackCommand
from .log import TurnLog


class TurnResult(IntEnum):
    KEEPING = 0
    FINISHED = 1
    ESCAPED = 2


@dataclass(frozen=True)
class Turn:
    """
    ターン
    """

    id: int

    def __lt__(self, other):
        return other.id > self.id

    def __eq__(self, other):
        return self.id == other.id

    def proceed(self,
                teams: List[Team],
                gambits: List[Gambit],
                logs: List[TurnLog]
                ) -> Tuple[TurnResult, Optional[Team]]:
        """
        ターンを進める
        """

        # 参加ユニットを求める
        units: List[Unit] = [unit for team in teams for unit in team.units]

        # 行動が早い順にユニットソート
        units.sort(key=Unit.calc_action_priority, reverse=True)

        for order, source in enumerate(units):
            # 行動可能かチェック
            if not source.alive:
                continue

            commands: List[Command] = [AttackCommand()]
            gambit = gambits[source.team]
            command, targets = gambit.select_command(source, units, commands)
            command.do(self.id, order, source, targets, logs)

            # 戦闘終了の判定
            if not any(filter(lambda u: source.can_attack(u), units)):
                return TurnResult.FINISHED, teams[source.team]

        return TurnResult.KEEPING, None
