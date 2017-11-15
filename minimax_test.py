import unittest
from agents import MinimaxAgent
from state import State, print_board


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 4):
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
