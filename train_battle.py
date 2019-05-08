import argparse
import logging
from typing import List, Tuple, Counter as _Counter
from collections import Counter

import numpy as np
import tensorflow as tf
from fastprogress import master_bar, progress_bar
from sklearn.model_selection import train_test_split

from game import logger
from game.status import Side, Status, statuses
from game.unit import Unit
from game.team import Team
from game.log import TurnLog
from game.battle import Battle
from game.gambit import Gambit, NaiveGambit, MLbasedGambit


def simulate_battle(teams: List[Team],
                    gambits: List[Gambit],
                    n_battle: int = 1000
                    ) -> Tuple[_Counter[int], List[TurnLog]]:
    win: _Counter[int] = Counter()
    logs: List[TurnLog] = []

    # バトルをシミュレーションする
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
    np.set_printoptions(precision=2)

    logs: List[TurnLog] = []

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

    # 1000回バトルをシミュレーションする
    logger.info("# Simulation")
    win, logs = simulate_battle(teams, gambits, args.n_battle)

    # 学習を始める
    logger.info("# Training")

    EPOCHS = 50
    BATCH_SIZE = 128

    ai = MLbasedGambit(is_training=True)
    mb = master_bar(range(len(ai.estimators)))
    n_class = len(statuses[Side.MONSTER])
    for i, reg in enumerate(ai.estimators):
        logger.info('## Train %s %s' % (reg.name, reg.get_tag()))

        if i == 0:
            _logs = list(filter(lambda l: l.target_side == Side.PLAYER, logs))
            y = np.array([[log.damage] for log in _logs], dtype=np.float32)
            Xv = np.array([[log.target_def] for log in _logs], dtype=np.float32)
            Xc = np.array([ai.id2vec(log.source_id) for log in _logs], dtype=np.float32)
        elif i == 1:
            _logs = list(filter(lambda l: l.source_side == Side.PLAYER, logs))
            y = np.array([[log.damage] for log in _logs], dtype=np.float32)
            Xv = np.array([[log.source_atk] for log in _logs], dtype=np.float32)
            Xc = np.array([ai.id2vec(log.target_id) for log in _logs], dtype=np.float32)
        elif i == 2:
            _logs = list(filter(lambda l: l.source_side == Side.PLAYER, logs))
            y = np.array([[log.damage_cumsum] for log in _logs], dtype=np.float32)
            Xv = np.array([[log.defeated] for log in _logs], dtype=np.float32)
            Xc = np.array([ai.id2vec(log.target_id) for log in _logs], dtype=np.float32)

        Xv_train, Xv_test, Xc_train, Xc_test, y_train, y_test = train_test_split(
            Xv, Xc, y, test_size=0.125, random_state=2)

        losses = list()
        epochs = list()
        for epoch in progress_bar(range(EPOCHS), parent=mb):
            result = reg.model.fit([Xv_train, Xc_train], y_train,
                                   batch_size=BATCH_SIZE,
                                   epochs=1, verbose=0)
            losses.append(result.history['loss'][0])
            epochs.append(epoch+1)
            graphs = [[epochs, losses]]
            x_bounds = [1, EPOCHS]
            y_bounds = [0, None]
            mb.update_graph(graphs, x_bounds, y_bounds)
            if epoch % 5 == 0:
                logger.info('Epoch %i: %.5f MSE' % (epoch + 1, losses[-1]))

        average_loss = reg.model.evaluate([Xv_test, Xc_test], y_test,
                                          batch_size=BATCH_SIZE,
                                          verbose=0)
        logger.info('Average loss %f' % (average_loss,))

        # result0 = reg.model.predict([Xv_test[:1], Xc_test[:1]])

        reg.save_model()
