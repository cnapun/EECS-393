import abc
import random
from typing import Tuple, List

import time

from chess.state import State, GameResult


def _popcount(n):
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    return n


class Agent(abc.ABC):
    @abc.abstractmethod
    def select_move(self, state: 'State') -> Tuple[int, int]:
        pass


class MinimaxAgent(Agent):
    def __init__(self):
        self.whose_turn = None

    @abc.abstractmethod
    def heuristic(self, state: 'State') -> float:
        pass

    @property
    @abc.abstractmethod
    def max_depth(self) -> int:
        pass

    def select_move(self, state: 'State') -> Tuple[int, int]:
        self.whose_turn = state.white_turn
        self._alpha_beta(state, self.max_depth, -float('inf'), float('inf'),
                         True)
        return self.optimal_child.prev_move

    def _alpha_beta(self, state: 'State', depth: int, alpha: float, beta: float,
                    maxer: bool) -> float:
        result = state.is_terminal()
        if result == GameResult.P1_WINS:
            # print(state)
            # print()
            if self.whose_turn:
                return 10000 * depth
            else:
                return -10000 * depth
        elif result == GameResult.P2_WINS:
            if self.whose_turn:
                return -10000 * depth
            else:
                return 10000 * depth
        elif result == GameResult.DRAW:
            return -1
        elif depth == 0:
            return self.heuristic(state)
        children = state.get_children()
        if maxer:
            v = -float('inf')
            for child in children:
                y = self._alpha_beta(child, depth - 1, alpha, beta, False)
                if y > v and depth == self.max_depth:
                    # print(child)
                    # print(child.is_terminal())
                    self.optimal_child = child
                v = max(v, y)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = float('inf')
            for child in children:
                y = self._alpha_beta(child, depth - 1, alpha, beta, True)
                v = min(v, y)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v


class SavingAgent(Agent):
    @abc.abstractmethod
    def to_file(self, filename):
        pass

    @staticmethod
    @abc.abstractstaticmethod
    def from_file(filename, **kwargs):
        pass


class LearningAgent(Agent):
    @abc.abstractmethod
    def update(self, states: List['State'], result: GameResult):
        pass

    @property
    @abc.abstractmethod
    def max_iter(self) -> int:
        """
        Maximum number of moves to make in a game
        :return:
        """
        pass

    def setup_iteration(self):
        pass

    def teardown_iteration(self):
        pass

    def setup_train(self):
        pass

    def teardown_train(self):
        pass

    def play_and_update(self):
        self.setup_iteration()
        n_moves = 0
        result = GameResult.NONTERMINAL
        states = []
        state = State()
        while n_moves < self.max_iter and result == GameResult.NONTERMINAL:
            states.append(state)
            move = self.select_move(state)
            state = state.get_child(*move)
            result = state.is_terminal()
            n_moves += 1

        self.update(states, result)
        self.teardown_iteration()

    def train_n_games(self, n_games, save_every=-1, save_filename=None):
        self.setup_train()
        if save_every <= 0:
            save_every = float('inf')
        else:
            if save_filename is None:
                raise ValueError('Please enter a filename to save to')
        for i in range(1, n_games + 1):
            self.play_and_update()
            if i % save_every == 0 or i == n_games:
                print('Saving: iteration %d' % i)
                self.to_file(save_filename)
        self.teardown_train()


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 3):
        super().__init__()
        self._max_depth = int(max_depth)

    @property
    def max_depth(self):
        return self._max_depth

    def piece_value(self, state_tuple):
        return _popcount(state_tuple[0]) + \
               3 * (_popcount(state_tuple[1]) + _popcount(state_tuple[2])) + \
               5 * _popcount(state_tuple[3]) + 12 * _popcount(state_tuple[4])

    def heuristic(self, state: 'State'):
        if state.white_turn:
            me = state.white
            them = state.black
        else:
            me = state.black
            them = state.white
        return self.piece_value(them) - self.piece_value(me)


class CountingMinimaxAgent(SampleMinimaxAgent):
    def __init__(self, max_depth=5):
        super().__init__()
        self._max_depth = max_depth
        self.n_ab = self.n_heuristic = 0

    @property
    def max_depth(self):
        return self._max_depth

    def select_move(self, state: 'State'):
        self.n_ab = self.n_heuristic = 0
        return super(CountingMinimaxAgent, self).select_move(state)

    def _alpha_beta(self, state: 'State', depth: int, alpha: float, beta: float,
                    maxer: bool):
        self.n_ab += 1
        return super(CountingMinimaxAgent, self)._alpha_beta(state, depth,
                                                             alpha, beta, maxer)

    def heuristic(self, state: 'State'):
        self.n_heuristic += 1
        return super(CountingMinimaxAgent, self).heuristic(state)


if __name__ == '__main__':
    a = CountingMinimaxAgent(6)
    s = State()
    start = time.time()
    a.select_move(s)
    end = time.time()
    heuristic_per_second = a.n_heuristic / (end - start)
    ab_per_second = a.n_ab / (end - start)
    print('Heuristic Evaluations per second: %.1f' % heuristic_per_second)
    print('Alpha Beta Evaluations per second: %.1f' % ab_per_second)
