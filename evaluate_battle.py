import argparse
import logging
from typing import List, Tuple, Counter as _Counter
from collections import Counter

import tensorflow as tf

from game import logger
from game.status import Side, Status, statuses
from game.unit import Unit
from game.team import Team
from game.log import TurnLog
from game.battle import Battle
from game.gambit import Gambit, NaiveGambit, CunningGambit, MLbasedGambit


def simulate_battle(teams: List[Team],
                    gambits: List[Gambit],
                    n_battle: int = 1000
                    ) -> Tuple[_Counter[int], List[TurnLog]]:
    win: _Counter[int] = Counter()
    logs: List[TurnLog] = []

    # バトルを複数回シミュレーション
    for n in range(0, n_battle):
        battle = Battle(n)
        result = battle.simulate(teams, gambits, logs)
        win[result] += 1

    return win, logs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='count', default=0)
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('-n', '--n_battle', action='store', default=1000)
    args = parser.parse_args()

    dbg_format = '%(levelname)-8s %(module)-16s %(lineno)4s: %(message)s'
    logging.basicConfig(
        level=logging.WARN + 10 * (args.quiet - args.verbose),
        format=dbg_format if args.debug else None
    )
    tf.logging.set_verbosity(tf.logging.ERROR)

    teams: List[Team] = [
        # プレイヤーチームのユニット構成
        Team(0, [
            Unit(statuses[Side.PLAYER][0]),
            Unit(statuses[Side.PLAYER][1]),
            Unit(statuses[Side.PLAYER][2]),
        ]),
        # モンスターチームのユニット構成
        Team(1, [
            Unit(statuses[Side.MONSTER][0]),
            Unit(statuses[Side.MONSTER][1]),
            Unit(statuses[Side.MONSTER][2]),
        ]),
    ]

    gambits: List[Gambit] = [
        # プレイヤーの戦闘AI
        NaiveGambit(),
        # モンスターの戦闘AI
        NaiveGambit(),
    ]

    # バトルシミュレーション1 （プレイヤーの行動を、ランダムで決める）
    win, logs = simulate_battle(teams, gambits, args.n_battle)
    print("Player(Naive) win rate %7.5f%%" % (100.0 * win[0] / sum(win.values()),))

    # バトルシミュレーション2 （プレイヤーの行動を、チートして決める）
    gambits[Side.PLAYER] = CunningGambit()
    win, logs = simulate_battle(teams, gambits, args.n_battle)
    print("Player(Cunning) win rate %7.5f%%" % (100.0 * win[0] / sum(win.values()),))

    # バトルシミュレーション3 （プレイヤーの行動を、機械学習モデルで決める）
    gambits[Side.PLAYER] = MLbasedGambit()
    win, logs = simulate_battle(teams, gambits, args.n_battle)
    print("Player(MLbased) win rate %7.5f%%" % (100.0 * win[0] / sum(win.values()),))
