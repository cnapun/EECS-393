import random
import unittest

from chess.agents import MinimaxAgent
from chess.mcts import RandomMoveAgent, RandomPlayoutAgent

from chess.state import State


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 3):
        super().__init__()
        self._max_depth = max_depth

    @property
    def max_depth(self):
        return self._max_depth

    def heuristic(self, state: 'State'):
        return 0


class MinimaxTest(unittest.TestCase):
    def test_search(self):
        s = State(
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            (0, 0, 0, 0, 0, 1),
            turn='w',
            in_check=False
        )
        agent = SampleMinimaxAgent()
        selected_move = agent.select_move(s)
        self.assertEqual(selected_move, (2 << 16, 2 << 8), 'Checkmate in 1')


class RandomAgentTest(unittest.TestCase):
    def test_select_move_random(self):
        agent = RandomMoveAgent()
        s = State()
        random.seed(124915)
        moves = set()
        for i in range(10):
            moves.add(agent.select_move(s))
        self.assertTrue(len(moves) > 1)

    def test_select_move_playout(self):
        agent = RandomPlayoutAgent(max_time=1, max_depth=2)
        s = State(
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            (0, 0, 0, 0, 0, 1),
            turn='w',
            in_check=False
        )
        random.seed(124915)
        selected_move = agent.select_move(s)
        self.assertEqual(selected_move, (2 << 16, 2 << 8), 'Checkmate in 1')


class LearningAgentTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
