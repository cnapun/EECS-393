import abc
from typing import Tuple

from state import State, GameState


class Agent(abc.ABC):
    @abc.abstractmethod
    def select_move(self, state: 'State') -> Tuple[int, int]:
        pass


class MinimaxAgent(Agent):
    @abc.abstractmethod
    def heuristic(self, state: 'State') -> float:
        pass

    @property
    @abc.abstractmethod
    def max_depth(self) -> int:
        pass

    def select_move(self, state: 'State') -> Tuple[int, int]:
        self._alpha_beta(state, self.max_depth, -float('inf'), float('inf'), True)
        return self.optimal_child.prev_move

    def _alpha_beta(self, state: 'State', depth: int, alpha: float, beta: float, maxer: bool) -> float:
        result = state.is_terminal()
        if result == GameState.P1_WINS:
            return 100.0 if state.white_turn else -100.0
        if result == GameState.P2_WINS:
            return -100.0 if state.white_turn else 100.0
        if result == GameState.DRAW:
            return -1.0
        if depth == self.max_depth:
            return self.heuristic(state)

        if maxer:
            v = -float('inf')
            for child in state.get_children():
                y = self._alpha_beta(child, depth - 1, alpha, beta, False)
                if y > v and depth == self.max_depth:
                    self.optimal_child = child
                v = max(v, y)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = float('inf')
            for child in state.get_children():
                y = self._alpha_beta(child, depth - 1, alpha, beta, True)
                v = min(v, y)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v
