import abc
from typing import Tuple

from chess.state import State, GameResult


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
        self._alpha_beta(state, self.max_depth, -float('inf'), float('inf'), True)
        return self.optimal_child.prev_move

    def _alpha_beta(self, state: 'State', depth: int, alpha: float, beta: float, maxer: bool) -> float:
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


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 3):
        super().__init__()
        self._max_depth = max_depth

    @property
    def max_depth(self):
        return self._max_depth

    def heuristic(self, state: 'State'):
        return 0
