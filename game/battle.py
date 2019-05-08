from typing import List, Optional
from dataclasses import dataclass

from game import logger
from game.team import Team
from game.turn import Turn, TurnResult
from game.log import TurnLog
from game.gambit import Gambit


@dataclass(frozen=True)
class Battle:
    """
    バトル
    """

    id: int

    def simulate(self,
                 teams: List[Team],
                 gambits: List[Gambit],
                 logs: List[TurnLog],
                 max_turn: int = 1000,
                 ) -> int:
        logger.debug("## Battle No.%d" % self.id)

        # バトルのシミュレーション
        for team in teams:
            team.reset()

        for gambit in gambits:
            gambit.reset(teams)

        # 上限までターンを進める
        for turn_id in range(1, max_turn):
            logger.debug("### Turn No.%d" % turn_id)

            turn = Turn(turn_id)
            result, win_team = turn.proceed(teams, gambits, logs)
            if win_team:
                return win_team.id

        return -1
