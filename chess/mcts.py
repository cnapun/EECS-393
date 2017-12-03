from typing import Tuple

import numpy as np
import random
from collections import Counter

import time

from chess.state import GameResult, State
from chess.agents import Agent


class RandomMoveAgent(Agent):
    def random_child(self, state: 'State') -> 'State':
        return next(state.get_children(shuffle=True))

    def select_move(self, state: 'State') -> Tuple[int, int]:
        return self.random_child(state).prev_move


class RandomPlayoutAgent(Agent):
    def __init__(self, max_time=3, max_depth=100):
        self.max_time = max_time
        self.max_depth = max_depth

    def select_move(self, state: 'State'):
        best_child = self.playout_many(state)
        return best_child.prev_move

    def playout(self, state: 'State', start_depth: int = 0):
        depth = start_depth
        result = GameResult.NONTERMINAL
        while depth < self.max_depth and result == GameResult.NONTERMINAL:
            state = self.random_child(state)
            result = state.is_terminal()
            depth += 1
        return result

    def playout_many(self, state: 'State') -> 'State':
        white_turn = state.white_turn
        counter = Counter()
        start = time.time()
        end = start
        while end - start < self.max_time:
            child = self.random_child(state)
            result = self.playout(child, 1)
            if result in (GameResult.NONTERMINAL, GameResult.DRAW):
                reward = 0
            elif (result == GameResult.P1_WINS and white_turn) or \
                    (result == GameResult.P2_WINS and not white_turn):
                reward = 1
            else:
                reward = -1
            counter[child] += reward
            end = time.time()

        best_child, total_reward = counter.most_common(1)[0]

        return best_child

    def random_child(self, state):
        return next(state.get_children(shuffle=True))
